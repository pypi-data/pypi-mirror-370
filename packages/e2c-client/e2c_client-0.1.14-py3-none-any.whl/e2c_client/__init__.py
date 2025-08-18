__version__ = "0.1.14"

import socket
import struct
from e2c_client.lib.utils.map_nodes import map_node


class E2CClient:
    """
    Class for communicating with the E2C socket server over TCP to send monitor
    and control requests.

    Example usage:
    client = E2CClient("cob-dmc-01-e2c.ape-hil.ape")

    * LORR on bus 1, node 0x22, relative CAN address 0x30003 (GET_AMBIENT_TEMPERATURE), mode 0 (monitor):
    error, data = client.send_request(resource_id=0, bus_id=1, node_id=0x22, can_addr=0x30003, mode=0, data=b"")

    * LORR on bus 1, node 0x22, relative CAN address 0x00082 (SET_CLEAR_FLAGS), mode 1 (control):
    error, data = client.send_request(resource_id=0, bus_id=1, node_id=0x22, can_addr=0x00082, mode=1, data=b"\x01")

    * Utility to get the temperature in degrees Celsius from an AMBSI:
    temperature = client.get_temperature_c(channel=0, node=0x22)

    * Get E2C internal monitor point (GET_SERIAL_NUMBER, i.e., MAC address):
    error, data = client.send_request(resource_id=0, bus_id=client.E2C_INTERNAL_CHANNEL,
        node_id=client.E2C_INTERNAL_NODE, can_addr=0x0000, mode=0, data=b"")


    """

    # Maximum number of CAN channels supported by the E2C module
    E2C_NUM_CHANNELS = 5

    # Resource IDs for internal E2C requests
    E2C_INTERNAL_CHANNEL = 5
    E2C_INTERNAL_NODE = 0x16

    # Helper function to convert hex or int strings to integers
    converter = lambda foo: (
        int(foo[2:], base=16) if foo.lower().strip().startswith("0x") else int(foo)
    )

    def __init__(self, host, port=2000, timeout=5, verbose=True):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose

    def __del__(self):
        if hasattr(self, "sock"):
            try:
                self.sock.close()
            except:
                pass

    def _connect(self):
        if hasattr(self, "sock"):
            return self.sock
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))
        if self.verbose:
            print(f"Opened socket connection to E2C {self.host} socket server")
        return self.sock

    def __enter__(self):
        self.sock = self._connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if hasattr(self, "sock"):
            if self.verbose:
                print("Socket closed successfully")
            self.sock.close()
        if exc_type is not None:
            print(f"Exception occurred: {exc_value}")
        return False

    def _build_request(self, resource_id, bus_id, node_id, can_addr, mode, data=b""):
        """See the E2C protocol specification (ALMA-70.35.10.14-00.00.00.00-A-ICD) for details."""

        # Compose CAN identifier: top 11 bits node_id, lower 18 bits can_addr
        can_id = (((node_id + 1) & 0x7FF) << 18) | (can_addr & 0x3FFFF)
        req = bytearray(18)
        struct.pack_into(">H", req, 0, resource_id)
        struct.pack_into(">H", req, 2, bus_id)
        struct.pack_into(">I", req, 4, can_id)
        req[8] = mode
        req[9] = len(data) if mode == 1 else 0
        req[10 : 10 + len(data)] = data[:8] if mode == 1 else b""
        return req

    def _parse_response(self, resp):
        error_code = struct.unpack(">I", resp[:4])[0]
        data_len = resp[4]
        data = resp[5 : 5 + 8]
        return error_code, data_len, data

    def send_request(self, resource_id, bus_id, node_id, can_addr, mode, data=b""):
        req = self._build_request(resource_id, bus_id, node_id, can_addr, mode, data)
        s = self._connect()
        s.sendall(req)
        resp = s.recv(13)
        error_code, data_len, data = self._parse_response(resp)

        if mode == 2 and error_code == 0:
            # getNodes: read node list
            nodes = []
            for _ in range(data_len):
                node_info = s.recv(12)
                node_id = struct.unpack(">I", node_info[:4])[0]
                serial = node_info[4:12]
                nodes.append({"node_id": node_id, "serial": serial})
            return error_code, nodes
        return error_code, data[:data_len]

    def get_temperature_c(self, channel, node):
        """
        Method to monitor the temperature returned by an AMBSI.  This method
        takes care of any byte ordering issues which needs to be resolved.  The
        full range of the DS18S20 is used to provide maximum resolution.

        Ref.:
          https://bitbucket.alma.cl/projects/ALMA/repos/almasw/browse/CONTROL/Common/AMBManager/src/CCL/AmbManager.py#563
        """

        try:
            error, data = self.send_request(
                resource_id=0,
                bus_id=channel,
                node_id=node,
                can_addr=0x30003,
                mode=0,
                data=b"",
            )
        except Exception as e:
            # Error getting the temperature from node
            print(f"Error getting temperature: {e}")
            raise e

        byte = struct.unpack("BBBB", data)
        if byte[0] == 0xFF or byte[0] == 0x00:
            # Byte Major Order
            (temp, count_remain, count_per_c) = struct.unpack(">hBB", data)
        else:
            # Byte Minor Order or degenerate case
            (temp, count_remain, count_per_c) = struct.unpack("<hBB", data)
        # Temperature calculation as detailed in DS18S20 datasheet, page 4.
        resp = (temp >> 1) - 0.25 + ((count_per_c - count_remain) / float(count_per_c))
        return resp

    def get_nodes(self, channel):
        """
        List all nodes found in a specific channel.
        """

        try:
            error, data = self.send_request(
                resource_id=0,
                bus_id=channel,
                node_id=0,
                can_addr=0,
                mode=2,
                data=b"",
            )
        except Exception as e:
            print(f"Error getting nodes: {e}")
            raise e

        if len(data):
            for node in data:
                print(
                    f"Channel: {channel}, Node id: {hex(node['node_id']).upper():>5s}, ESN: 0x{node['serial'].hex().upper()}, {map_node(node['node_id'])}"
                )

        return data

    def get_all_nodes(self):
        """
        List all nodes found in all channels.
        """
        data_all = []
        for channel in range(self.E2C_NUM_CHANNELS):
            data = self.get_nodes(channel)
            if data:
                data_all.append([channel, data])

        return data_all
