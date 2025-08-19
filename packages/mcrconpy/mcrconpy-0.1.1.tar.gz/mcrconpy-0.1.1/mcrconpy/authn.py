# -*- coding: utf-8 -*-
"""
"""

from mcrconpy.packet import Packet

from mcrconpy.exceptions import (
    ServerAuthError,
    AddressError,
    PasswordError
)


from typing import TypeVar


SOCKET = TypeVar("SOCKET")
USER = TypeVar("User")


class AuthN:
    """
    Responsible for sending data to log in to the server.
    """

    def __init__(
        self,
        socket: SOCKET
    ) -> None:
        """
        Constructor.

        Args
            socket: instance of `socket.socket()`.
        """
        self.socket = socket

    def login(
        self,
        user: USER
    ) -> bool:
        """
        Sends data to log in to the server.

        Args
            passwd: str, password of the user.

        Returns
            bool: `True` if the login is successful, otherwise, `False`.

        Raises
            ServerAuthError: if the user's password is incorrect.
        """
        packet = Packet.build(
                            req_id=user.id,
                            packet_type=Packet.SERVERDATA_AUTH,
                            data=user.get_password(),
                        )

        self.socket.send(data=packet)


        # res = self.socket.read(4)
        # x = self.socket.read(int.from_bytes(res, byteorder="little"))
        # print(Packet.decode(data=x))

        res = self.socket.read()

        auth_response = Packet.decode(data=res)
        length, id, packet_type, body = auth_response

        # print("X", res, length, id, packet_type, body)

        if id == -1:
            raise ServerAuthError()

        return True
