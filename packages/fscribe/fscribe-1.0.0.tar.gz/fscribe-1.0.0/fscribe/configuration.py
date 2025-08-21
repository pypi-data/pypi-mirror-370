try:
    import tomllib  # type: ignore
except ImportError:
    import tomli as tomllib  # type: ignore
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import ConfigurationError
from .interfaces import IConfigurationProvider


class ConfigurationManager(IConfigurationProvider):
    def __init__(
        self, config_path: Optional[Path] = None, cli_args: Optional[Dict[str, Any]] = None
    ):
        self._config_data: Dict[str, Any] = {}
        self._cli_args = cli_args or {}

        if config_path and config_path.exists():
            self._load_config_file(config_path)

        self._apply_defaults()

    def _load_config_file(self, config_path: Path) -> None:
        try:
            with open(config_path, "rb") as f:
                self._config_data = tomllib.load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {config_path}: {e}")

    def _apply_defaults(self) -> None:
        defaults = {
            "include_patterns": [
                "*.md",
                "*.py",
                "*.js",
                "*.jsx",
                "*.ts",
                "*.tsx",
                "*.html",
                "*.css",
                "*.cs",
                "*.csproj",
                "*.sln",
                "*.json",
                "*.yml",
                "*.yaml",
                "*.xml",
                "*.cpp",
                "*.c",
                "*.h",
                "*.hpp",
                "*.java",
                "*.go",
                "*.rs",
                "*.php",
                "*.rb",
                "*.sh",
                "*.sql",
                "*.toml",
                "*.ini",
                "Dockerfile",
            ],
            "exclude_patterns": [
                "*.dll",
                "*.exe",
                "*.png",
                "*.jpg",
                "*.jpeg",
                "*.gif",
                "*.bmp",
                "*.zip",
                "*.tar",
                "*.gz",
                "*.rar",
                "*.7z",
                "*.obj",
                "*.bin",
                "*.so",
                "*.dylib",
                "*.class",
                "*.jar",
                "*.war",
                "*.pyc",
                "node_modules/*",
                ".git/*",
                "__pycache__/*",
                "*.log",
                ".vscode/*",
                ".idea/*",
                "dist/*",
                "build/*",
                "target/*",
            ],
            "max_file_size_kb": 500,
            "output_formats": ["text"],
            "output_directory": None,
        }

        for key, default_value in defaults.items():
            if key not in self._config_data:
                self._config_data[key] = default_value

    def get_include_patterns(self) -> List[str]:
        value = self._cli_args.get(
            "include_patterns", self._config_data.get("include_patterns", [])
        )
        return list(value) if isinstance(value, list) else []

    def get_exclude_patterns(self) -> List[str]:
        value = self._cli_args.get(
            "exclude_patterns", self._config_data.get("exclude_patterns", [])
        )
        return list(value) if isinstance(value, list) else []

    def get_max_file_size_kb(self) -> int:
        value = self._cli_args.get(
            "max_file_size_kb", self._config_data.get("max_file_size_kb", 500)
        )
        return (
            int(value)
            if isinstance(value, int) or (isinstance(value, str) and value.isdigit())
            else 500
        )

    def get_output_formats(self) -> List[str]:
        value = self._cli_args.get(
            "output_formats", self._config_data.get("output_formats", ["text"])
        )
        return list(value) if isinstance(value, list) else ["text"]

    def get_output_directory(self) -> Path:
        output_dir = self._cli_args.get("output_directory") or self._config_data.get(
            "output_directory"
        )
        if output_dir:
            return Path(output_dir)
        return self._get_default_output_directory()

    def _get_default_output_directory(self) -> Path:
        try:
            if Path.home().exists():
                documents_path = Path.home() / "Documents"
                if documents_path.exists():
                    return documents_path
                return Path.home()
            return Path.cwd()
        except Exception:
            return Path.cwd()

    def validate_configuration(self) -> None:
        required_keys = [
            "include_patterns",
            "exclude_patterns",
            "max_file_size_kb",
            "output_formats",
        ]

        for key in required_keys:
            if key not in self._config_data:
                raise ConfigurationError(f"Missing required configuration key: {key}")

        if not isinstance(self._config_data["include_patterns"], list):
            raise ConfigurationError("include_patterns must be a list")

        if not isinstance(self._config_data["exclude_patterns"], list):
            raise ConfigurationError("exclude_patterns must be a list")

        if (
            not isinstance(self._config_data["max_file_size_kb"], int)
            or self._config_data["max_file_size_kb"] <= 0
        ):
            raise ConfigurationError("max_file_size_kb must be a positive integer")

        valid_formats = ["text", "json", "md"]
        for fmt in self._config_data["output_formats"]:
            if fmt not in valid_formats:
                raise ConfigurationError(
                    f"Invalid output format: {fmt}. Valid formats: {valid_formats}"
                )

    def get_config_value(self, key: str, default: Any = None) -> Any:
        return self._cli_args.get(key, self._config_data.get(key, default))

    def set_exclude_patterns(self, patterns: List[str]) -> None:
        if not isinstance(patterns, list):
            raise ConfigurationError("exclude_patterns must be a list")
        self._config_data["exclude_patterns"] = list(patterns)
