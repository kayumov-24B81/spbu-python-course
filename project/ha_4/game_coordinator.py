from player import *


class GameCoordinator:
    def __init__(self):
        self.betting_interface = BettingInterface()
        self.roulette = Roulette()
        self.players = []
        self.controllers = {}

    def _add_player(self, player, controller):
        self.players.append(player)
        self.controllers[player] = controller

    def setup_game(self):
        print("=== STARTING ROULETTE GAME ===")

        name = input("Player name: ")
        balance = 1000

        player = Player(name, balance)
        controller = HumanPlayerController(player, self.betting_interface)
        self._add_player(player, controller)
