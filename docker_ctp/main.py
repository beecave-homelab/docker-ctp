"""Entry point wrapper for docker-ctp."""

from docker_ctp.cli import main as cli_main


def main() -> None:
    """Run the CLI."""
    cli_main()


if __name__ == "__main__":  # pragma: no cover
    main()
