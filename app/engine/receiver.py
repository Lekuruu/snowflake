
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import Factory
from typing import List

from app.data import POLICY_FILE

import logging
import shlex
import json
import ast

class Receiver(LineOnlyReceiver):
    def __init__(self, server: Factory, address: IPv4Address | IPv6Address):
        self.address = address
        self.server = server
        self.logger = logging.getLogger(address.host)

    def lineReceived(self, line: bytes):
        data = line.decode("utf-8")

        if data.startswith('<policy-file-request/>'):
            self.logger.debug(f'-> "{data}"')
            self.sendLine(POLICY_FILE.encode())
            self.close_connection()
            return

        if data.startswith('/'):
            command, args = shlex.split(data)

            for index, argument in enumerate(args):
                try:
                    # Try to load json
                    args[index] = json.loads(argument)
                    continue
                except json.JSONDecodeError:
                    pass

                try:
                    # Try to convert the argument to a Python object
                    args[index] = ast.literal_eval(argument)
                except ValueError:
                    pass

            self.logger.debug(f'-> "{command}": {args}')
            self.command_received(command, args)
            return

        self.logger.warning(f'Unknown request: "{data}"')

    def close_connection(self):
        self.transport.loseConnection()
        self.logger.info("Connection closed.")

    def send_tag(self, tag: str, *args):
        self.logger.debug(f'<- "{tag}": {args}')
        self.sendLine(f'[{tag.name}]|' + '|'.join(str(a) for a in args))

    def command_received(self, command: str, args: List[str]):
        ...
