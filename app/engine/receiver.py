
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.error import ConnectionDone
from twisted.python.failure import Failure
from typing import List, Any

from app.data import POLICY_FILE
from app import engine

import logging
import shlex
import json
import ast

class Receiver(LineOnlyReceiver):
    def __init__(self, server: engine.SnowflakeEngine, address: IPv4Address | IPv6Address):
        self.address = address
        self.server = server
        self.logger = logging.getLogger(address.host)

    def dataReceived(self, data: bytes):
        if data.startswith(b'<policy-file-request/>'):
            self.logger.debug(f'-> "{data}"')
            self.sendLine(POLICY_FILE.encode())
            self.close_connection()
            return

        return super().dataReceived(data)

    def lineReceived(self, line: bytes):
        try:
            data = line.decode("utf-8")
        except UnicodeDecodeError:
            self.logger.warning(f'Invalid request: "{line}"')
            self.close_connection()
            return

        try:
            parsed = shlex.split(data)
            command, args = parsed[0], parsed[1:]
        except (ValueError, UnicodeDecodeError):
            self.logger.warning(f'Invalid request: "{data}"')
            self.close_connection()
            return

        for index, argument in enumerate(args):
            if argument.startswith('{'):
                # Try to convert the argument to a JSON object
                # TODO: Refactor this mess
                try:
                    args = [json.loads(' '.join(data.split(' ')[1:]))]
                    break
                except json.JSONDecodeError:
                    pass

            try:
                # Try to convert the argument to a Python object
                args[index] = ast.literal_eval(argument)
            except (ValueError, SyntaxError):
                pass

        self.logger.debug(f'-> "{command}": {args}')
        self.command_received(command, args)

    def connectionLost(self, reason: Failure | None = None) -> None:
        if (reason is not None) and (reason.type != ConnectionDone):
            self.logger.warning(f"Connection lost: {reason.getErrorMessage()}")

        self.server.players.remove(self)
        # TODO: Handle Matchmaking

    def close_connection(self):
        self.transport.loseConnection()
        self.connectionLost()

    def send_tag(self, tag: str, *args):
        self.logger.debug(f'<- "{tag}": {args}')
        self.sendLine(
            (f'[{tag}]|' + '|'.join(str(a) for a in args) + '|').encode()
        )

    def command_received(self, command: str, args: List[Any]):
        ...
