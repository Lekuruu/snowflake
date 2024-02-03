
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.error import ConnectionDone
from twisted.python.failure import Failure
from typing import List, Any

from app.data import POLICY_FILE
from app import engine

import logging
import time
import json
import ast

class Receiver(LineOnlyReceiver):
    def __init__(self, server: engine.SnowflakeEngine, address: IPv4Address | IPv6Address):
        self.address = address
        self.server = server
        self.logger = logging.getLogger(address.host)
        self.last_action = time.time()
        self.disconnected = False

    def dataReceived(self, data: bytes):
        if data.startswith(b'<policy-file-request/>'):
            self.logger.debug(f'-> "{data}"')
            self.sendLine(POLICY_FILE.encode())
            self.close_connection()
            return

        self.last_action = time.time()
        return super().dataReceived(data)

    def lineReceived(self, line: bytes):
        try:
            data = line.decode("utf-8")
        except UnicodeDecodeError:
            self.logger.warning(f'Invalid request: "{line}"')
            self.close_connection()
            return

        try:
            parsed = data.split(' ')
            command, args = parsed[0], parsed[1:]
        except (ValueError, UnicodeDecodeError):
            self.logger.warning(f'Invalid request: "{data}"')
            self.close_connection()
            return

        for index, argument in enumerate(args):
            try:
                if argument.startswith('{'):
                    # We received a json string
                    args = [json.loads(' '.join(args))]
                    break

                # Try to convert the argument to a Python object
                args[index] = ast.literal_eval(argument)
            except (ValueError, SyntaxError, json.JSONDecodeError):
                pass

        self.command_received(command, args)

    def connectionLost(self, reason: Failure | None = None) -> None:
        if reason is not None and not self.disconnected:
            self.logger.warning(f"Connection lost: {reason.getErrorMessage()}")

        self.server.players.remove(self)
        self.server.matchmaking.remove(self)
        self.disconnected = True

    def close_connection(self):
        if not self.transport:
            return

        self.transport.loseConnection()
        self.connectionLost()

    def send_tag(self, tag: str, *args):
        if not self.transport:
            return

        self.logger.debug(f'<- "{tag}": {args}')
        self.sendLine(
            (f'[{tag}]|' + '|'.join(str(a) for a in args) + '|').encode()
        )

    def command_received(self, command: str, args: List[Any]):
        ...
