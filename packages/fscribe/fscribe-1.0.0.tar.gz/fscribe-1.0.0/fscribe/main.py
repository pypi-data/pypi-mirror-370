import asyncio

from .cli import CommandLineInterface


def main() -> None:
    cli = CommandLineInterface()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()
