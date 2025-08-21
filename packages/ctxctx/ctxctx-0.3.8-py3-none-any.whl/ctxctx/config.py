# ctxctx/config.py
import copy
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Set, Tuple, cast

import yaml  # type: ignore

from .exceptions import ConfigurationError

# === CONFIGURATION ===
# Define the immutable default values structure
_DEFAULT_CONFIG_TEMPLATE: Dict[str, Any] = {
    "ROOT": ".",
    "OUTPUT_FILE_BASE_NAME": "prompt_input_files",
    "OUTPUT_FORMATS": ("md", "json"),
    "TREE_MAX_DEPTH": 3,
    "TREE_EXCLUDE_EMPTY_DIRS": False,
    "SEARCH_MAX_DEPTH": 5,
    "MAX_MATCHES_PER_QUERY": 5,
    "EXPLICIT_IGNORE_NAMES": frozenset(
        {
            ".git",
            ".gitignore",
            "node_modules",
            "__pycache__",
            ".venv",
            ".idea",
            ".DS_Store",
            ".vscode",
            "dist",
            "build",
            "coverage",
            "logs",
            "temp",
            "tmp",
        }
    ),
    "SUBSTRING_IGNORE_PATTERNS": (
        "package-lock.json",
        "playwright-report",
        "yarn.lock",
        "npm-debug.log",
        ".env",
        "__snapshots__",
        ".next",
    ),
    "ADDITIONAL_IGNORE_FILENAMES": (
        ".dockerignore",
        ".npmignore",
        ".eslintignore",
    ),
    "SCRIPT_DEFAULT_IGNORE_FILE": "prompt_builder_ignore.txt",
    "PROFILE_CONFIG_FILE": "prompt_profiles.yaml",
    "DEFAULT_CONFIG_FILENAME": ".ctxctx.yaml",  # NEW
    "VERSION": "0.1.0",
    "USE_GITIGNORE": True,
    "GITIGNORE_PATH": ".gitignore",
    "USE_CACHE": True,
}

# NEW: Keys from the default config that should not be written to the user-facing file.
_INTERNAL_CONFIG_KEYS = {
    "VERSION",
    "SCRIPT_DEFAULT_IGNORE_FILE",
    "PROFILE_CONFIG_FILE",
    "DEFAULT_CONFIG_FILENAME",
}


class Config:
    """
    Holds and manages the application's configuration.
    Provides attribute-like access to configuration values.
    """

    def __init__(self, initial_data: Dict[str, Any]):
        # Store a mutable dictionary internally for flexible merging and updates
        self._data = initial_data

        # Explicitly define attributes for type hinting and clear access.
        # These attributes are synced with the internal _data dictionary.
        self.root: Path = Path()  # Will be set via _sync_attributes
        self.output_file_base_name: str = ""
        self.output_formats: List[str] = []
        self.tree_max_depth: int = 0
        self.tree_exclude_empty_dirs: bool = False
        self.search_max_depth: int = 0
        self.max_matches_per_query: int = 0
        self.explicit_ignore_names: Set[str] = set()
        self.substring_ignore_patterns: List[str] = []
        self.additional_ignore_filenames: List[str] = []
        self.script_default_ignore_file: str = ""
        self.profile_config_file: str = ""
        self.default_config_filename: str = ""  # NEW
        self.version: str = ""
        self.use_gitignore: bool = False
        self.gitignore_path: str = ""
        self.use_cache: bool = True

        self._sync_attributes()  # Initialize attributes from initial_data

    def _sync_attributes(self):
        """Syncs public attributes with the current state of the internal _data dictionary."""
        # Ensure ROOT is always an absolute Path for consistency
        self.root = Path(self._data.get("ROOT", ".")).resolve()
        self.output_file_base_name = self._data.get("OUTPUT_FILE_BASE_NAME", "prompt_input_files")
        self.output_formats = list(self._data.get("OUTPUT_FORMATS", []))
        self.tree_max_depth = self._data.get("TREE_MAX_DEPTH", 3)
        self.tree_exclude_empty_dirs = self._data.get("TREE_EXCLUDE_EMPTY_DIRS", False)
        self.search_max_depth = self._data.get("SEARCH_MAX_DEPTH", 5)
        self.max_matches_per_query = self._data.get("MAX_MATCHES_PER_QUERY", 5)
        self.explicit_ignore_names = set(self._data.get("EXPLICIT_IGNORE_NAMES", set()))
        self.substring_ignore_patterns = list(self._data.get("SUBSTRING_IGNORE_PATTERNS", []))
        self.additional_ignore_filenames = list(self._data.get("ADDITIONAL_IGNORE_FILENAMES", []))
        self.script_default_ignore_file = self._data.get(
            "SCRIPT_DEFAULT_IGNORE_FILE", "prompt_builder_ignore.txt"
        )
        self.profile_config_file = self._data.get("PROFILE_CONFIG_FILE", "prompt_profiles.yaml")
        self.default_config_filename = self._data.get(
            "DEFAULT_CONFIG_FILENAME", ".ctxctx.yaml"
        )  # NEW
        self.version = self._data.get("VERSION", "0.1.0")
        self.use_gitignore = self._data.get("USE_GITIGNORE", True)
        self.gitignore_path = self._data.get("GITIGNORE_PATH", ".gitignore")
        self.use_cache = self._data.get("USE_CACHE", True)

    # Optional: Allow dictionary-like access for generic keys if needed, though attribute
    # access is preferred
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._sync_attributes()  # Re-sync attributes when internal data is directly modified

    def merge(self, data: Dict[str, Any]) -> None:
        """
        Merges new data into the current configuration's internal state.
        After merging, public attributes are re-synchronized.
        """
        _merge_dicts(self._data, data)
        self._sync_attributes()

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return f"Config({self._data})"


def create_default_config_dict() -> Dict[str, Any]:
    """
    Returns a deep copy of the default configuration dictionary template.
    This intermediate step converts immutable types (frozenset, tuple)
    to mutable ones (set, list) for runtime manipulation.
    """
    default_copy = copy.deepcopy(_DEFAULT_CONFIG_TEMPLATE)
    default_copy["OUTPUT_FORMATS"] = list(cast(Tuple[str, ...], default_copy["OUTPUT_FORMATS"]))
    default_copy["EXPLICIT_IGNORE_NAMES"] = set(
        cast(FrozenSet[str], default_copy["EXPLICIT_IGNORE_NAMES"])
    )
    default_copy["SUBSTRING_IGNORE_PATTERNS"] = list(
        cast(Tuple[str, ...], default_copy["SUBSTRING_IGNORE_PATTERNS"])
    )
    default_copy["ADDITIONAL_IGNORE_FILENAMES"] = list(
        cast(Tuple[str, ...], default_copy["ADDITIONAL_IGNORE_FILENAMES"])
    )
    return default_copy


def get_default_config() -> Config:
    """
    Returns a new Config object initialized with default values.
    """
    return Config(create_default_config_dict())


def _merge_dicts(d1: Dict[str, Any], d2: Dict[str, Any]) -> None:
    """
    Recursively merges d2 into d1. d2 overrides d1 for scalar values,
    merges for collections.
    """
    for k, v in d2.items():
        if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
            _merge_dicts(d1[k], v)
        elif k in d1 and isinstance(d1[k], list) and isinstance(v, list):
            d1[k].extend(v)
            # Deduplicate for specific list-based config keys
            if k in [
                "OUTPUT_FORMATS",
                "SUBSTRING_IGNORE_PATTERNS",
                "ADDITIONAL_IGNORE_FILENAMES",
            ]:
                d1[k] = list(set(d1[k]))
        elif k in d1 and isinstance(d1[k], set) and isinstance(v, set):
            d1[k].update(v)
        else:
            d1[k] = v


def generate_default_config_file(config_filepath: Path) -> None:
    """
    Generates a default .ctxctx.yaml file using PyYAML.
    """
    header = (
        "# ctxctx Configuration File\n"
        "# This file allows you to customize the behavior of ctxctx for your project.\n"
        "# For more details, see the project's documentation.\n\n"
    )

    # Prepare a dictionary of user-facing default settings, preserving order
    config_to_write: Dict[str, Any] = {}
    defaults = create_default_config_dict()  # Get a mutable version
    for key in _DEFAULT_CONFIG_TEMPLATE:  # Iterate in defined order
        if key in _INTERNAL_CONFIG_KEYS:
            continue

        value = defaults[key]
        # Convert sets to sorted lists for stable and readable YAML output
        if isinstance(value, set):
            config_to_write[key] = sorted(list(value))
        else:
            config_to_write[key] = value

    try:
        with open(config_filepath, "w", encoding="utf-8") as f:
            f.write(header)
            # Use yaml.dump for robust and correct YAML generation.
            # sort_keys=False maintains the insertion order from the defaults dict.
            yaml.dump(config_to_write, f, sort_keys=False, indent=2, default_flow_style=False)
    except IOError as e:
        raise ConfigurationError(
            f"Failed to write default config file to '{config_filepath}': {e}"
        ) from e
    except Exception as e:
        # Catch potential yaml errors, though they are unlikely here
        raise ConfigurationError(
            f"An unexpected error occurred while generating the default config file: {e}"
        ) from e


def load_base_config_file(config_filepath: Path) -> Dict[str, Any]:
    """
    Loads configuration from a base YAML file (e.g., .ctxctx.yaml).
    Returns an empty dictionary if the file is not found,
    or raises ConfigurationError if parsing fails.
    """
    if not config_filepath.is_file():
        return {}  # Not found, return empty dict as it's an optional file

    try:
        with open(config_filepath, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            if config_data is None:  # An empty file parses to None
                return {}
            if not isinstance(config_data, dict):
                raise ConfigurationError(
                    f"Invalid base configuration file '{config_filepath}'. "
                    "Expected a dictionary at root."
                )
            return config_data
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Error loading YAML config from '{config_filepath}': {e}") from e
    except Exception as e:
        raise ConfigurationError(f"Error reading config file '{config_filepath}': {e}") from e


def load_profile_config(
    profile_name: str, root_path: Path, profile_config_filename: str
) -> Dict[str, Any]:
    """
    Loads configuration from a YAML profile file and returns the selected
    profile data as a dictionary.
    Raises ConfigurationError if file not found or profile not found.
    """
    profile_config_path = root_path / profile_config_filename

    if not profile_config_path.is_file():
        raise ConfigurationError(f"Profile configuration file not found: '{profile_config_path}'.")

    try:
        # open() accepts Path objects directly
        with open(profile_config_path, "r", encoding="utf-8") as f:
            all_profiles_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(
            f"Error loading YAML config from '{profile_config_path}': {e}"
        ) from e
    except Exception as e:
        raise ConfigurationError(
            f"Error reading YAML config file '{profile_config_path}': {e}"
        ) from e

    if (
        not all_profiles_data
        or not isinstance(all_profiles_data, dict)
        or "profiles" not in all_profiles_data
    ):
        raise ConfigurationError(
            f"Invalid profile configuration file '{profile_config_path}'. "
            "Expected 'profiles' key at root."
        )

    if profile_name not in all_profiles_data["profiles"]:
        raise ConfigurationError(f"Profile '{profile_name}' not found in '{profile_config_path}'.")

    return all_profiles_data["profiles"][profile_name]


def apply_profile_config(config_obj: Config, profile_data: Dict[str, Any]) -> None:
    """
    Applies profile data (dictionary) to the Config object's internal state.
    This merges values from profile_data into config_obj._data and then syncs
    the public attributes of the Config object.
    """
    config_obj.merge(profile_data)
