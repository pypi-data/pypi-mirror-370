# -*- coding: utf-8 -*-
"""
"""

from mcrconpy.packet import Packet

from mcrconpy.connection import Connection
from mcrconpy.authn import AuthN
from mcrconpy.audit import Audit

from mcrconpy.models import User


from mcrconpy.exceptions import (
    ServerTimeOut,
    ServerError,
    ServerAuthError,
    SocketConnectionError,

)

from typing import (
    Union
)


class RconPy:

    def __init__(
        self,
        address: str,
        port: int,
        password: str = None,
        audit: bool = False,
    ) -> None:
        """
        """
        self.address = address
        self.port = port
        self.audit = audit

        self.user = User(password)
        self.conn = Connection()
        self.auth = AuthN(socket=self.conn)

    def set_password(
        self,
        password: str,
    ) -> bool:
        """
        Sets the password for the rcon user.

        Args
            password: str, password of rcon.

        Returns
            bool: whether the password has been set correctly or not.
        """
        return self.user.set_password(password)

    def get_password(self) -> Union[str, None]:
        """
        Gets the password of the rcon user.

        Returns
            str: current password.
            None: if no password is set.
        """
        return self.user.get_password()

    def is_login(self) -> bool:
        """
        If the current user is connected to the server or not.

        Returns
            bool: `True` if log in, otherwise, `False`.
        """
        return self.user.is_login

    def connect(self) -> None:
        """
        Connect to rcon server.
        """
        try:
            self.conn.connect(address=self.address, port=self.port)
        except (ServerTimeOut, ServerError) as e:
            print(">XXXX", e)
            return

    def login(
        self,
        password: str = None
    ) -> bool:
        """
        User login with your password.

        Args
            password: str, password of rcon user.

        Returns
            bool: whether the login was successful or not.
        """
        if self.conn.is_connected() is False:
            return False

        try:
            if password is None and self.user.get_password() is None:
                    return False

            if password is not None:
                self.user.set_password(password)

            if self.auth.login(user=self.user):
                self.user.active_session()
                return True

        except (ServerAuthError, SocketConnectionError) as e:
            print(">", e)
            self.user.is_login = False
            return False

    def command(
        self,
        command: str
    ) -> Union[str, None]:
        """
        Args
            command: str, command to be executed on the server.

        Returns
            str: response of command executed.
            None: if the user is not logged in to the server.
        """
        if self.user.is_login is False:
            return None

        self.user.register_command(cmd=command)

        # print(self.user.commands)

        packet = Packet.build(
                            req_id=self.user.id,
                            packet_type=Packet.SERVERDATA_EXECCOMMAND,
                            data=command,
                        )

        self.send(data=packet)

        data = self.read()
        return data[-1]

    def send(
        self,
        data: bytes
    ) -> bytes:
        """
        Sends data to the server.

        Args
            data: bytes, data to be sent.

        Returns
            bytes: response in bytes from the server.
        """
        if self.conn.is_connected():
            res = self.conn.send(data)
            # print(res, data)
            return res
        return b''

    def read(self) -> tuple:
        """
        Reads the response data from the server.

        Args
            length: int, size of the buffer to read.

        Returns
            bytes: data from the server.
        """
        data = self.conn.read()
        length, id, packet_type, body = Packet.decode(data)
        return (length, id, packet_type, body)

    def check_connection(self) -> bool:
        """
        Checks if current connection is alive.

        Returns
            bool: `True` if connection is alive, otherwise, `False`.
        """
        return self.conn.is_connected()

    def to_audit(self) -> None:
        """
        Records user activity in a JSONL file.
        """
        if self.user.is_login:
            Audit.to_save(
                        data=self.user.to_dict()
                    )

    def disconnect(self) -> None:
        """
        Closes the current connection to the server.
        """
        self.conn.close()
        self.user.close_session()
        if self.audit:
            self.to_audit()

    def __enter__(self) -> None:
        """
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        """
        self.disconnect()

    def __str__(self) -> str:
        """
        """
        return "%s:%s" % (self.address, self.port)

    def __repr__(self) -> str:
        """
        """
        return "<[ RconPy: %s ]>" % self.__str__()
