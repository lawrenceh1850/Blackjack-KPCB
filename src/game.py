from players.player import Player
from inputmanager import InputManager


class Game:
    def __init__(self, players):
        self.players = players
        self.i_manager = InputManager()
