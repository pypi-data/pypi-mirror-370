import socket
import typer
from typing import Optional

from e2c_client import E2CClient
from e2c_client.lib.utils.e2c_errors import E2C_ERRORS_DICT
from e2c_client.lib.utils.hosts import ALL_E2C_APE
from rich.table import Table
from rich.console import Console

tools_app = typer.Typer(short_help="E2C utility commands")


@tools_app.callback()
def tools_app_callback():
    """
    General-purpose functions for E2C-controlled devices.

    Usage:

    \b
    e2c-client tools --help
    e2c-client tools temperature --host <host> --channel <channel> --node <node> # perform AMB monitor request for temperature
    e2c-client tools revision --host <host>
    e2c-client tools revision --all


    """


@tools_app.command(
    "temperature", short_help="Perform AMB monitor request for AMBSI temperature"
)
def temperature(
    host: Optional[str] = typer.Option(None, help="E2C hostname or IP address"),
    port: Optional[int] = typer.Option(2000, help="E2C socket server port"),
    channel: Optional[str] = typer.Option(None, help="LRU channel number"),
    node: Optional[str] = typer.Option(None, help="LRU node address"),
    verbose: Optional[bool] = typer.Option(False, help="Enable verbose output"),
):
    try:
        with E2CClient(host, port, verbose=verbose) as client:
            temp = client.get_temperature_c(
                E2CClient.converter(channel), E2CClient.converter(node)
            )
            print(f"Temperature: {temp} [C]")
    except Exception as e:
        print(f"Error: {str(e)}")


@tools_app.command("revision", short_help="Obtain E2C revision information")
def revision(
    host: Optional[str] = typer.Option(None, help="E2C hostname or IP address"),
    port: Optional[int] = typer.Option(2000, help="E2C socket server port"),
    verbose: Optional[bool] = typer.Option(False, help="Enable verbose output"),
    all: Optional[bool] = typer.Option(
        False, help="Obtain information for all E2Cs in APE"
    ),
):
    rcas = [
        0x30000,
        0x30004,
        0x30005,
    ]  # GET_PROTOCOL_REV_LEVEL, GET_SW_REV_LEVEL, GET_UBOOT_REV_LEVEL

    if not all:
        try:

            with E2CClient(host, port, verbose=verbose) as client:
                for rca in rcas:
                    error, data = client.send_request(
                        resource_id=0,
                        bus_id=client.E2C_INTERNAL_CHANNEL,
                        node_id=client.E2C_INTERNAL_NODE,
                        can_addr=rca,
                        mode=0,
                        data=b"",
                    )
                    if error == 0:
                        rev = ".".join(str(b) for b in data)
                        if rca == 0x30000:
                            print(f"Protocol revision: {rev}")
                        elif rca == 0x30004:
                            print(f"Software revision: {rev}")
                        elif rca == 0x30005:
                            print(f"U-Boot revision: {rev}")
                    else:
                        print(
                            f"Error retrieving revision for RCA {hex(rca)}: {error} "
                            f"({E2C_ERRORS_DICT.get(error, {}).get('description', '')})"
                        )

        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        console = Console()
        console.print("[yellow]Please, wait...[/yellow]")
        table = Table(title="E2C Revision Information")
        table.add_column("Host", style="bold")
        table.add_column("Protocol Revision")
        table.add_column("Software Revision")
        table.add_column("U-Boot Revision")
        table.add_column("Errors")

        try:
            for e2c_host in ALL_E2C_APE:
                protocol_rev = software_rev = uboot_rev = ""
                errors = []
                try:
                    with E2CClient(
                        e2c_host, port, timeout=1, verbose=verbose
                    ) as client:
                        for rca in rcas:
                            error, data = client.send_request(
                                resource_id=0,
                                bus_id=client.E2C_INTERNAL_CHANNEL,
                                node_id=client.E2C_INTERNAL_NODE,
                                can_addr=rca,
                                mode=0,
                                data=b"",
                            )
                            rev = ".".join(str(b) for b in data) if error == 0 else ""
                            if rca == 0x30000:
                                protocol_rev = rev
                            elif rca == 0x30004:
                                software_rev = rev
                            elif rca == 0x30005:
                                uboot_rev = rev
                            if error != 0:
                                errors.append(
                                    f"RCA {hex(rca)}: {error} ({E2C_ERRORS_DICT.get(error, {}).get('description', '')})"
                                )
                except TimeoutError:
                    errors.append("Timeout connecting")
                except socket.gaierror:
                    errors.append("Host not found")
                except Exception as e:
                    errors.append(str(e))

                table.add_row(
                    e2c_host,
                    protocol_rev,
                    software_rev,
                    uboot_rev,
                    "\n".join(errors) if errors else "-",
                )
            console.print(table)
        except Exception as e:
            print(f"Error: {str(e)}")
