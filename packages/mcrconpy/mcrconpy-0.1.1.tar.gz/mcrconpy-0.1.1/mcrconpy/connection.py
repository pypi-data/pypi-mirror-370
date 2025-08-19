# -*- coding: utf-8 -*-
"""
"""

from mcrconpy.packet import Packet

from mcrconpy.exceptions import (
    ServerTimeOut,
    ServerError,
    SocketConnectionError,
)

import socket


class Connection:

    def __init__(
        self,
    ) -> None:
        """
        Set up the socket for connection.
        """
        self.socket = None

    def is_connected(
        self,
    ) -> bool:
        """
        Check if the connection to the server is active.
        """
        try:
            self.send(b'')
            return True
        except Exception as e:
            return False

    def connect(
        self,
        address: str,
        port: int
    ) -> None:
        """
        Connect to the server with the specified address and port.

        Args
            address: str, address of the server.
            port: int, port used by the server.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((address, port))
        except socket.timeout as e:
            raise ServerTimeOut()
        except socket.error as e:
            raise ServerError(e)

    def send(
        self,
        data: bytes
    ) -> int:
        """
        Sends data to the server.

        Args
            data: bytes, data to send to the server.

        Returns
            bytes: response from the server.
        """
        if self.socket is not None:
            try:
                bytes_sent = self.socket.send(data)
                return bytes_sent
            except Exception as e:
                raise SocketConnectionError(e)
        else:
            raise SocketConnectionError("Socket is not connected.")


    def read(
        self,
        length: int = 4
    ) -> bytes:
        """
        Reads data from the server.

        Args
            length: int, size of buffer to read.

        Returns
            bytes: data from the server.
        """
        def _read(length: int) -> bytes:
            """
            """
            data_ = b''
            while len(data_) < length:
                res = self.socket.recv(length - len(data_))
                if not res:
                    break
                data_ += res
            return data_

        try:
            full_packet = b''
            # recv bytes packet length
            length_packet = _read(length=4)
            full_packet += length_packet

            # recv rest of packet using packet length
            data = _read(Packet.decode(data=length_packet)[0])
            full_packet += data

            return full_packet
        except Exception as e:
            # print(e)
            raise SocketConnectionError(e)

    def close(
        self,
    ) -> None:
        """
        Closes the current socket, whether connected to the server or not.
        """
        if self.socket is not None:
            self.socket.close()
            self.socket = None
