"""Entry point wrapper for docker-ctp."""

from .cli import main as cli_main


def main() -> None:
    """Run the CLI."""
    cli_main()


if __name__ == "__main__":  # pragma: no cover
    main()
