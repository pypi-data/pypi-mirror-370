# -*- coding: utf-8 -*-
"""
Exceptions
"""

class ErrorParameter(Exception):
    def __init__(
        self,
        msg: str
    ) -> None:
        """
        """
        super().__init__(f"Parameter Error: {msg}")

class SocketConnectionError(Exception):
    def __init__(
        self,
        msg: str
    ) -> None:
        """
        """
        super().__init__(f"Socket Connection Error: {msg}.")


class ServerTimeOut(Exception):
    def __init__(self) -> None:
        """
        """
        super().__init__("Connection timed out.")


class ServerError(Exception):
    def __init__(
        self,
        error
    ) -> None:
        """
        """
        super().__init__(f"Server Socket Error: {error}")


class ServerAuthError(Exception):
    def __init__(self) -> None:
        super().__init__("Server Auth Error, check the password.")


class AddressError(Exception):
    def __init__(self) -> None:
        super().__init__("IP address and PORT is incorrect.")


class PasswordError(Exception):
    def __init__(self) -> None:
        super().__init__("Password has not been provided or is incorrect.")
