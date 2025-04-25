
from config import WEBSOCKET_SSL_ENABLED, WEBSOCKET_SSL_CERTFILE, WEBSOCKET_SSL_KEYFILE
from txwebsocket.txws import WebSocketFactory, WebSocketProtocol
from app.protocols.metaplace import MetaplaceWorldServer
from twisted.internet import reactor, ssl

class WebSocketWrapper(WebSocketFactory):
    def __init__(self, world: MetaplaceWorldServer):
        super().__init__(world)
        self.world_id = world.world_id
        self.world_name = world.world_name
        self.world_owner = world.world_owner
        self.build_type = world.build_type
        self.server_type = world.server_type
        self.stylesheet_id = world.stylesheet_id

        self.logger = world.logger
        self.places = world.places
        self.sound_assets = world.sound_assets
        self.assets = world.assets
        self.players = world.players
        self.policy_file = world.policy_file

    def get_place(self, place_id: int):
        return self.wrappedFactory.get_place(place_id)
    
    def register_place(self, place):
        self.wrappedFactory.register_place(place)

    def listen(self, port: int) -> None:
        self.logger.info(f'Starting websocket world server "{self.world_name}" ({port})')

        if not WEBSOCKET_SSL_ENABLED:
            reactor.listenTCP(port, self)
            return

        ssl_context = ssl.DefaultOpenSSLContextFactory(
            WEBSOCKET_SSL_KEYFILE,
            WEBSOCKET_SSL_CERTFILE
        )
        reactor.listenSSL(port, self, ssl_context)

    def buildProtocol(self, addr):
        protocol: WebSocketProtocol = super().buildProtocol(addr)
        protocol.setBinaryMode(True)
        return protocol
