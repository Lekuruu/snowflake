
from app.protocols.metaplace import MetaplaceWorldServer
from txwebsocket.txws import WebSocketFactory
from twisted.internet import reactor

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
        reactor.listenTCP(port, self)
