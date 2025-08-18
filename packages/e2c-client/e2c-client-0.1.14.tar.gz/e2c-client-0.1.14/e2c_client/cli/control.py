import typer
import struct
from typing import Optional

from e2c_client import E2CClient

control_app = typer.Typer(short_help="E2C control related commands")


@control_app.callback()
def monitor_app_callback():
    """
    Perform control requests for E2C-controlled devices.

    Usage:

    \b
    e2c-client control --help
    e2c-client control request --host <host> --channel <channel> --node <node> --rca <RCA> --data <data>

    Example:
    Set attenuators on IFP0 of DA63 to A:12 dB, B:12.5 dB, C:9 dB, D:8.5 dB

    e2c-client control request --host da63-e2c --channel 0 --node 0x29 --rca 0x0181 --data "0x60 0x64 0x48 0x44"

    """


@control_app.command("request", short_help="Perform AMB control request")
def request(
    host: Optional[str] = typer.Option(None, help="E2C hostname or IP address"),
    port: Optional[int] = typer.Option(2000, help="E2C socket server port"),
    channel: Optional[str] = typer.Option(None, help="LRU channel number"),
    node: Optional[str] = typer.Option(None, help="LRU node address"),
    rca: Optional[str] = typer.Option(None, help="Control request RCA"),
    data: Optional[str] = typer.Option(
        None, help="Data to send in control request (space-separated int or hex values)"
    ),
    verbose: Optional[bool] = typer.Option(False, help="Enable verbose output"),
):
    try:
        with E2CClient(host, port, verbose=verbose) as client:
            error, data = client.send_request(
                resource_id=0,
                bus_id=E2CClient.converter(channel),
                node_id=E2CClient.converter(node),
                can_addr=E2CClient.converter(rca),
                mode=1,  # control mode
                data=struct.pack(
                    f"{len(data.split(' '))}B",
                    *[E2CClient.converter(item) for item in data.split(" ")],
                ),
            )
            print(f"Error: {error}")
            print("Data: ")
            print(", ".join(hex(b) for b in data))
    except Exception as e:
        print(f"Error: {str(e)}")
