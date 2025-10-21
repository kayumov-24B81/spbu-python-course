from bets import *
from typing import List


class Player:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.current_bets: List[Bet] = []

    def place_bet(self, bet: Bet):
        self.balance -= bet.amount
        self.current_bets.append(bet)
        return True

    def get_balance(self):
        return self.balance

    def get_current_bets(self):
        return self.current_bets

    def get_name(self):
        return self.name

    def add_balance(self, amount):
        self.balance += amount
