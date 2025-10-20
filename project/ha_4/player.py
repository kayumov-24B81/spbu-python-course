from bets import *
from table import *


class Player:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.current_bets = []

    def can_afford(self, amount):
        return self.balance >= amount

    def place_bet(self, bet: Bet):
        if self.can_afford(bet.amount):
            self.balance -= bet.amount
            self.current_bets.append(bet)
            return True
        return False

    def get_balance(self):
        return self.balance


class HumanPlayerController:
    def __init__(self, player: Player, betting_interface: BettingInterface):
        self.player = player
        self.betting_interface = betting_interface

    def make_bet_decision(self):
        bet = self.betting_interface.get_validated_bet(self.player.get_balance())

        if bet:
            return bet

        return None
