import argparse
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from .configuration import ConfigurationManager
from .core import ProjectAnalysisService
from .exceptions import ConfigurationError, FscribeException
from .interfaces import IConfigurationProvider


class CommandLineInterface:
    def __init__(self) -> None:
        self._parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Summarize project files into text, JSON, and Markdown.",
            epilog="Example usage:\n  fscribe /path/to/project -o /output/path -s 500 -f text json md",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        parser.add_argument("directory", type=str, help="Path to the project directory")
        parser.add_argument("-o", "--output", type=str, help="Output directory")
        parser.add_argument(
            "-s", "--size", type=int, default=500, help="Max file size in KB (default: 500)"
        )
        parser.add_argument(
            "-f",
            "--format",
            nargs="+",
            choices=["text", "json", "md"],
            default=["text"],
            help="Output format(s): text, json, md (default: text)",
        )
        parser.add_argument(
            "-c", "--config", type=str, help="Path to configuration file (.fscribe.toml)"
        )
        parser.add_argument("--include", nargs="+", help="Include patterns (overrides config)")
        parser.add_argument("--exclude", nargs="+", help="Exclude patterns (overrides config)")
        parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")

        return parser

    def parse_arguments(self) -> Dict[str, Any]:
        args = self._parser.parse_args()

        cli_config = {
            "directory": Path(args.directory),
            "max_file_size_kb": args.size,
            "output_formats": args.format,
        }

        if args.output:
            cli_config["output_directory"] = Path(args.output)

        if args.include:
            cli_config["include_patterns"] = args.include

        if args.exclude:
            cli_config["exclude_patterns"] = args.exclude

        config_path = None
        if args.config:
            config_path = Path(args.config)
        elif Path(".fscribe.toml").exists():
            config_path = Path(".fscribe.toml")

        cli_config["config_path"] = config_path
        cli_config["interactive_mode"] = args.interactive

        return cli_config

    async def run(self) -> None:
        try:
            cli_args = self.parse_arguments()
            config_path = cli_args.pop("config_path")
            directory = cli_args.pop("directory")
            interactive_mode = cli_args.pop("interactive_mode")

            config_manager = ConfigurationManager(config_path, cli_args)
            config_manager.validate_configuration()

            service = ProjectAnalysisService()

            if interactive_mode:
                await self._run_interactive_mode(service, directory, config_manager)
            else:
                await service.analyze_and_save(directory, config_manager)

        except ConfigurationError as e:
            print(f"Configuration error: {e}")
            exit(1)
        except FscribeException as e:
            print(f"Error: {e}")
            exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            exit(1)

    async def _run_interactive_mode(
        self, service: ProjectAnalysisService, directory: Path, config: IConfigurationProvider
    ) -> None:
        print(
            "Interactive mode - Enter additional exclude patterns (one per line, empty line to finish):"
        )

        additional_excludes: List[str] = []
        while True:
            pattern = input("> ").strip()
            if not pattern:
                break
            additional_excludes.append(pattern)

        if additional_excludes:
            current_excludes = config.get_exclude_patterns()
            # Prefer public setter if available
            if hasattr(config, "set_exclude_patterns"):
                config.set_exclude_patterns(current_excludes + additional_excludes)  # type: ignore[attr-defined]
            else:
                # Fallback: best-effort update (not ideal, but allows runtime behavior)
                # mypy will still flag direct attribute access on interfaces, so silence it here
                try:
                    config._config_data["exclude_patterns"] = current_excludes + additional_excludes  # type: ignore[attr-defined]
                except Exception:
                    pass

        await service.analyze_and_save(directory, config)


def get_user_input() -> Dict[str, Any]:
    return CommandLineInterface().parse_arguments()
