# -*- coding: utf-8 -*-
"""
"""

from mcrconpy.utils import (
    get_timestamp,
    from_timestamp,
    difference_times,
)


class Command:
    """
    Represents the command executed by the user with the timestamp at which it
    was executed.
    """

    def __init__(
        self,
        command: str,
    ) -> None:
        """
        Constructor.

        Args
            command: str, command used by the user.
        """
        self.command = command
        self.timestamp = get_timestamp()

    def to_dict(self) -> dict:
        """
        Returns the instance on dict format.
        """
        return {
            "command": self.command,
            "timestamp": self.timestamp
        }

    def __str__(self) -> str:
        """
        """
        return "%s, %s" % (
            from_timestamp(self.timestamp),
            self.command[:10]
        )

    def __repr__(self) -> str:
        """
        """
        return "<[ CMD: %s ]>" % self.__str__()




class User:
    """
    Represents the user, storing data such as the password, whether they are
    logged in, and commands.
    """

    def __init__(
        self,
        password: str = None,
    ) -> None:
        """
        Constructor.

        Args
            password: str, current password of the user.
        """
        self.id = 1
        self.__password = password
        self.commands = []
        self.is_login = False
        self.start_session = None
        self.end_session = None
        self.seconds_session = None

    def active_session(self) -> None:
        """
        """
        self.is_login = True
        self.start_session = get_timestamp()

    def close_session(self) -> None:
        """
        """
        self.is_login = False
        self.end_session = get_timestamp()
        self.time_session()

    def time_session(self) -> str:
        """
        """
        delta = difference_times(
                    start=self.start_session,
                    end=self.end_session,
                )
        if delta is None:
            self.seconds_session = None
        else:
            self.seconds_session = delta.total_seconds()

    def set_password(
        self,
        passwd: str,
    ) -> bool:
        """
        Sets a new password for the user.

        Args
            passwd: str, new password.

        Returns
            bool: `True` if the new password is set correctly, otherwise `False.
        """
        if passwd != "" and passwd != self.__password:
            self.__password = passwd
            return True
        return False

    def get_password(
        self,
    ) -> str:
        """
        Returns the current password of the current user.
        """
        return self.__password

    def register_command(
        self,
        cmd: str,
    ) -> None:
        """
        Record the command used by the user.

        Args
            cmd: str, command used by the user.
        """
        self.commands.append(Command(command=cmd))

    def to_dict(self) -> dict:
        """
        """
        start = self.start_session
        if self.start_session is not None:
            start = int(self.start_session * 1000000)

        return {
            "start_session": start,
            "commands": [cmd.to_dict() for cmd in self.commands],
            "is_login": self.is_login,
            "end_session": self.end_session,
            "seconds_session": self.seconds_session
        }

    def __str__(self) -> str:
        """
        """
        return "User: is_login: %s, Session: %s" % (
            self.is_login,
            from_timestamp(self.start_session)
        )

    def __repr__(self) -> str:
        """
        """
        return "<[ %s ]>" % self.__str__()
