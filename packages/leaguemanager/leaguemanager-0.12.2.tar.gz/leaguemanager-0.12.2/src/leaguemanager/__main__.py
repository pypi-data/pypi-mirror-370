"""Entry point for CLI application."""

from leaguemanager import __app_name__, cli


def main() -> None:
    """Entrypoint for CLI application."""
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    main()
