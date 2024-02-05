
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import Factory
from twisted.python.failure import Failure
from twisted.internet import reactor
from typing import List, Any

from app.engine.windows import WindowManager
from app.data import ServerType, BuildType
from app.objects import Players

import logging
import time
import json
import ast

class MetaplaceProtocol(LineOnlyReceiver):
    def __init__(self, server: "MetaplaceWorldServer", address: IPv4Address | IPv6Address):
        self.address = address
        self.server = server
        self.disconnected = False
        self.window_manager = WindowManager(self)

        self.last_action = time.time()
        self.logger = logging.getLogger(address.host)

    def lineReceived(self, line: bytes):
        self.last_action = time.time()

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

        encoded_arguments = '|'.join(str(a) for a in args)
        self.sendLine((f'[{tag}]|{encoded_arguments}|').encode())

    def command_received(self, command: str, args: List[Any]):
        """This method should be overridden by the protocol implementation."""
        ...

class MetaplaceWorldServer(Factory):
    protocol = MetaplaceProtocol

    def __init__(
        self,
        world_id: int,
        world_name: str,
        stylesheet_id: str,
        server_type: ServerType = ServerType.LIVE,
        build_type: BuildType = BuildType.RELEASE
    ) -> None:
        self.world_id = world_id
        self.world_name = world_name
        self.build_type = build_type
        self.server_type = server_type
        self.stylesheet_id = stylesheet_id

        self.players = Players()
        self.logger = logging.getLogger(f"{world_name} ({world_id})")

    def buildProtocol(self, address: IPv4Address | IPv6Address):
        self.logger.debug(f'-> "{address.host}:{address.port}"')
        self.players.add(player := self.protocol(self, address))
        return player

    def listen(self, port: int):
        self.logger.info(f"Starting engine: {self} ({port})")
        reactor.listenTCP(port, self)
