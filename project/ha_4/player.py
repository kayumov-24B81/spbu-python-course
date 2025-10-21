from bets import *
from typing import List


class Player:
    """Represents a player in the roulette game with balance and bets."""

    def __init__(self, name: str, balance: float) -> None:
        """
        Initialize a player.

        Args:
            name: The player's name
            balance: The player's starting balance
        """
        self.name = name
        self.balance = balance
        self.current_bet: Bet = None

    def place_bet(self, bet: Bet) -> bool:
        """
        Place a bet by deducting the amount from balance and adding to current bets.

        Args:
            bet: The bet object to place

        Returns:
            True if bet was successfully placed
        """
        self.balance -= bet.amount
        self.current_bet = bet
        return True

    def get_balance(self) -> float:
        """
        Get the player's current balance.

        Returns:
            The current balance amount
        """
        return self.balance

    def get_current_bet(self) -> Bet:
        """
        Get current active bet.

        Returns:
            Bet object that is currently active
        """
        return self.current_bet

    def get_name(self) -> set:
        """
        Get the player's name.

        Returns:
            The player's name
        """
        return self.name

    def add_balance(self, amount: float) -> None:
        """
        Add funds to the player's balance.

        Args:
            amount: The amount to add to the balance
        """
        self.balance += amount
