# -*- coding: utf-8 -*-
"""
"""

from mcrconpy import RconPy

import sys

import argparse


def clear_console() -> None:
    """
    """
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")


def main() -> None:
    """
    """
    main_parser = argparse.ArgumentParser(
        prog="mcrconpy",
        description="RCON protocol client for minecraft servers.",
        epilog="Connect remotely to the server and perform administrative tasks."
    )


    main_parser.add_argument(
        "-a",
        "--address",
        required=True,
        help="Minecraft Server TCP address.",
    )
    main_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=25575,
        help="Minecraft Server RCON Port. Default is 25575.",
    )
    main_parser.add_argument(
        "-P",
        "--password",
        required=True,
        help="User password.",
    )
    main_parser.add_argument(
        "-A",
        "--audit",
        default=False,
        action="store_true",
        help="Saves all commands executed by the user in a JSONL file. Default is disabled.",
    )

    args = main_parser.parse_args()

    address_ = args.address
    port_ = args.port
    password_ = args.password
    audit_ = args.audit


    with RconPy(
            address=address_,
            port=port_,
            password=password_,
            audit=audit_,
    ) as rcon:

        rcon.connect()

        if rcon.check_connection():
            rcon.login()

            if rcon.is_login():

                print("Connected and login to the server.\n")

                try:
                    while True:
                        cmd = input(">> Enter a command: ")
                        if cmd.strip().lower() in ["q", "quit", "exit", ""]:
                            print("Exit\n")
                            break

                        res = rcon.command(command=cmd)
                        print(res + "\n")

                        if cmd.strip() == "stop":
                            break

                except KeyboardInterrupt as e:
                    print("\nExit\n")

            else:
                print("The password is incorrect.")

        else:
            print("Error on address of the server.")


if __name__ == '__main__':
    main()
