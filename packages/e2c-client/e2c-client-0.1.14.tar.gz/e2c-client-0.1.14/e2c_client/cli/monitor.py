import typer
from typing import Optional

from e2c_client import E2CClient
from e2c_client.lib.utils.e2c_errors import E2C_ERRORS_DICT

monitor_app = typer.Typer(short_help="E2C monitoring related commands")


@monitor_app.callback()
def monitor_app_callback():
    """
    Perform monitoring requests for E2C-controlled devices.

    Usage:

    \b
    e2c-client monitor --help
    e2c-client monitor request --host <host> --channel <channel> --node <node> --rca <RCA>

    Example:
    Get attenuators on IFP0 of DA63. Returns: A:12 dB, B:12.5 dB, C:9 dB, D:8.5 dB

    $ e2c-client monitor request --host da63-e2c --channel 0 --node 0x29 --rca 0x0101
    Error: 0  (No error)
    Data:
    0x60, 0x64, 0x48, 0x44

    Optionally, you can interpret the response data as a struct format string using the `--interpret` option.
    See https://docs.python.org/3/library/struct.html#format-characters for available format characters.

    Get E2C processor temperature in degrees Celsius (response data is a 4 bytes float, according to ICD):
    $ e2c-client monitor request --host dv10-e2c --channel 5 --node 0x16 --rca 0x0E --interpret ">f"
    Error: 0  (No error)
    Data:
    0x42, 0x28, 0x74, 0x92
    Interpreted data:
    42.11383819580078

    """


@monitor_app.command("request", short_help="Perform AMB monitor request")
def request(
    host: Optional[str] = typer.Option(None, help="E2C hostname or IP address"),
    port: Optional[int] = typer.Option(2000, help="E2C socket server port"),
    channel: Optional[str] = typer.Option(None, help="LRU channel number"),
    node: Optional[str] = typer.Option(None, help="LRU node address"),
    rca: Optional[str] = typer.Option(None, help="Monitor request RCA"),
    interpret: Optional[str] = typer.Option(
        None, help="Interpret response data as given struct format string"
    ),
    verbose: Optional[bool] = typer.Option(False, help="Enable verbose output"),
):
    try:
        with E2CClient(host, port, verbose=verbose) as client:
            error, data = client.send_request(
                resource_id=0,  # ignored, kept in the API for backwards compatibility
                bus_id=E2CClient.converter(channel),
                node_id=E2CClient.converter(node),
                can_addr=E2CClient.converter(rca),
                mode=0,
                data=b"",
            )
            print(
                f"Error: {error} ",
                f"({E2C_ERRORS_DICT.get(error, {}).get('description', '')})",
            )
            print("Data: ")
            print(", ".join(hex(b) for b in data))
            if interpret:
                import struct

                try:
                    fmt = interpret.strip()
                    unpacked_data = struct.unpack(fmt, data)
                    print("Interpreted data:\n", unpacked_data[0])
                except struct.error as e:
                    print(f"Error interpreting data with format '{fmt}': {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")


@monitor_app.command("nodes", short_help="List all CAN nodes reported by E2C host")
def nodes(
    host: Optional[str] = typer.Option(None, help="E2C hostname or IP address"),
    port: Optional[int] = typer.Option(2000, help="E2C socket server port"),
    verbose: Optional[bool] = typer.Option(False, help="Enable verbose output"),
):
    try:
        with E2CClient(host, port, verbose=verbose) as client:
            client.get_all_nodes()
    except Exception as e:
        print(f"Error: {str(e)}")
