import os
from abc import ABC, abstractmethod
from collections import deque
from typing import Optional

from behave.model import Feature
from behave.configuration import Configuration
from behave.runner_util import parse_features, collect_feature_locations, PathManager
from behave.runner import path_getrootdir, Runner
from behave.exception import ConfigError


class FeatureFinder:
    _config: Configuration

    def __init__(self, config: Configuration):
        self._config = config

    def _setup_paths(self, path_manager: PathManager):
        # pylint: disable=too-many-branches, too-many-statements
        if self._config.paths:
            if self._config.verbose:
                print(
                    "Supplied path:",
                    ", ".join('"%s"' % path for path in self._config.paths),
                )
            first_path = self._config.paths[0]
            if hasattr(first_path, "filename"):
                # -- BETTER: isinstance(first_path, FileLocation):
                first_path = first_path.filename
            base_dir = first_path
            if base_dir.startswith("@"):
                # -- USE: behave @features.txt
                base_dir = base_dir[1:]
                file_locations = self.feature_locations()
                if file_locations:
                    base_dir = os.path.dirname(file_locations[0].filename)
            base_dir = os.path.abspath(base_dir)

            # supplied path might be to a feature file
            if os.path.isfile(base_dir):
                if self._config.verbose:
                    print("Primary path is to a file so using its directory")
                base_dir = os.path.dirname(base_dir)
        else:
            if self._config.verbose:
                print('Using default path "{}"'.format(Runner.DEFAULT_DIRECTORY))
            base_dir = os.path.abspath(Runner.DEFAULT_DIRECTORY)

        # Get the root. This is not guaranteed to be "/" because Windows.
        root_dir = path_getrootdir(base_dir)
        new_base_dir = base_dir
        steps_dir = self._config.steps_dir
        environment_file = self._config.environment_file

        while True:
            if self._config.verbose:
                print("Trying base directory:", new_base_dir)

            if os.path.isdir(os.path.join(new_base_dir, steps_dir)):
                break
            if os.path.isfile(os.path.join(new_base_dir, environment_file)):
                break
            if new_base_dir == root_dir:
                break

            new_base_dir = os.path.dirname(new_base_dir)

        if new_base_dir == root_dir:
            if self._config.verbose:
                if not self._config.paths:
                    print(
                        'ERROR: Could not find "%s" directory. '
                        "Please specify where to find your features." % steps_dir
                    )
                else:
                    print(
                        'ERROR: Could not find "%s" directory in your '
                        'specified path "%s"' % (steps_dir, base_dir)
                    )

            message = "No %s directory in %r" % (steps_dir, base_dir)
            raise ConfigError(message)

        base_dir = new_base_dir
        self._config.base_dir = base_dir

        for dirpath, dirnames, filenames in os.walk(base_dir, followlinks=True):
            if [fn for fn in filenames if fn.endswith(".feature")]:
                break
        else:
            if self._config.verbose:
                if not self._config.paths:
                    print(
                        'ERROR: Could not find any "<name>.feature" files. '
                        "Please specify where to find your features."
                    )
                else:
                    print(
                        'ERROR: Could not find any "<name>.feature" files '
                        'in your specified path "%s"' % base_dir
                    )
            raise ConfigError("No feature files in %r" % base_dir)

        self.base_dir = base_dir
        path_manager.add(base_dir)
        if not self._config.paths:
            self._config.paths = [base_dir]

        if base_dir != os.getcwd():
            path_manager.add(os.getcwd())

    def _find_feature_location(self) -> list[str]:
        return [
            filename
            for filename in collect_feature_locations(self._config.paths)
            if not self._config.exclude(filename)
        ]

    def get_all_features(self) -> list[Feature]:
        path_manager = PathManager()
        with path_manager:
            self._setup_paths(path_manager)
            return parse_features(
                self._find_feature_location(), language=self._config.lang
            )


class TaskAllocator(ABC):

    _config: Configuration
    _feature_finder: FeatureFinder

    def __init__(self, config: Configuration):
        self._config = config
        self._feature_finder = FeatureFinder(config)

    @abstractmethod
    def allocate(self, job_number: int) -> Optional[Feature]:
        pass

    @abstractmethod
    def empty(self) -> bool:
        pass


class FeatureTaskAllocator(TaskAllocator):

    _features: deque[Feature]

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._features = deque(self._feature_finder.get_all_features())

    def allocate(self, _: int) -> Optional[Feature]:
        if not self.empty():
            return self._features.popleft()

    def empty(self) -> bool:
        return len(self._features) == 0
