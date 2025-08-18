import typer
from typing import Optional

from e2c_client import __version__

# Commands and subcommands import
from e2c_client.cli import monitor
from e2c_client.cli import control
from e2c_client.cli import tools

# Command-line application based on Typer
app = typer.Typer(add_completion=False)

# Commands and subcommands definition divided by subsystem or functionality set
app.add_typer(monitor.monitor_app, name="monitor")
app.add_typer(control.control_app, name="control")
app.add_typer(tools.tools_app, name="tools")


@app.callback()
def callback():
    """
    E2C client commands

    Usage example (not all commands shown. Use --help for complete list):

    \b
    e2c-client --help
    e2c-client version
    e2c-client monitor --help
    e2c-client monitor request --host <host> --channel <channel> --node <node> --rca <RCA>
    e2c-client monitor --help
    e2c-client control request --host <host> --channel <channel> --node <node> --rca <RCA> --data <data>

    """


@app.command(short_help="Show current version")
def version():
    print(__version__)


def main():
    app()


if __name__ == "__main__":
    main()
