from player import Player
from betting_interface import BettingInterface, BetFactory
import random
from typing import Optional, Dict, List, Tuple, Any


class HumanPlayerController:
    """
    Controller for human players that uses a betting interface for input.

    Delegates bet decision making to the interactive betting interface.
    """

    def __init__(self, player: Player, betting_interface: BettingInterface) -> None:
        """
        Initialize human player controller.

        Args:
            player: The player instance to control
            betting_interface: The interface for receiving bet inputs
        """
        self.player = player
        self.betting_interface = betting_interface

    def make_bet_decision(self) -> Optional[Any]:
        """
        Get bet decision from human player via betting interface.

        Returns:
            A Bet object if player places a bet, None if player cancels
        """
        bet = self.betting_interface.get_validated_bet(self.player.get_balance())

        if bet:
            return bet

        return None


class ConservativeBotController:
    """
    AI controller that makes safe, conservative betting decisions.

    Prefers low-risk bets with higher probability of winning but lower payouts.
    Uses weighted random selection for bet types and safe betting choices.
    """

    def __init__(self, player) -> None:
        """
        Initialize conservative bot controller.

        Args:
            player: The player instance to control
        """
        self.player = player
        self.bet_factory = BetFactory()
        self.weights_dict = {
            "high_low": 0.2,
            "even_odd": 0.2,
            "color": 0.3,
            "column": 0.2,
            "line": 0.1,
        }

    def _weighted_type(self) -> str:
        """
        Select bet type based on weighted probabilities.

        Returns:
            Selected bet type string
        """
        choices = list(self.weights_dict.keys())
        weights = list(self.weights_dict.values())
        return random.choices(choices, weights=weights, k=1)[0]

    def _conservative_choice(self, bet_type: str) -> Optional[Any]:
        """
        Get conservative choice for the given bet type.

        Args:
            bet_type: Type of bet to make choice for

        Returns:
            Appropriate choice for the bet type, None for unsupported types
        """
        if bet_type == "color":
            return random.choice(["red", "black"])
        elif bet_type == "high_low":
            return random.choice(["high", "low"])
        elif bet_type == "even_odd":
            return random.choice(["even", "odd"])
        elif bet_type == "column":
            return random.choice([1, 2, 3])
        elif bet_type == "line":
            safe_lines = [4, 7, 10, 13, 16, 19, 22, 25, 28]
            return random.choice(safe_lines)
        else:
            return None

    def make_bet_decision(self) -> Optional[Any]:
        """
        Make conservative betting decision.

        Returns:
            A Bet object if decision is made, None if skipping turn or invalid

        Strategy:
            - 10% chance to skip betting
            - Uses small bet amounts (5% of balance, minimum 10)
            - Prefers safe bet types with higher win probability
        """
        if self.player.get_balance() <= 0:
            return None

        if random.random() < 0.1:
            return None

        bet_type = self._weighted_type()
        bet_amount = max(10, self.player.get_balance() // 20)
        bet_choice = self._conservative_choice(bet_type)

        if not bet_choice:
            return None

        bet = self.bet_factory.create_bet(bet_type, bet_amount, choice=bet_choice)

        if bet and bet.validate():
            return bet

        return None


class AggressiveBotController:
    """
    AI controller that makes high-risk, high-reward betting decisions.

    Prefers low-probability bets with high payouts. Implements martingale-like
    strategy by increasing bets after consecutive losses.
    """

    def __init__(self, player: Player) -> None:
        """
        Initialize aggressive bot controller.

        Args:
            player: The player instance to control
        """

        self.player = player
        self.bet_factory = BetFactory()
        self.consecutive_losses = 0
        self.weights_dict = {
            "straight": 0.35,
            "split": 0.25,
            "street": 0.15,
            "corner": 0.10,
            "line": 0.08,
            "dozen": 0.05,
            "column": 0.02,
        }

    def _weighted_type(self) -> str:
        """
        Select bet type based on weighted probabilities favoring risky bets.

        Returns:
            Selected bet type string
        """
        choices = list(self.weights_dict.keys())
        weights = list(self.weights_dict.values())
        return random.choices(choices, weights=weights, k=1)[0]

    def _aggressive_choice(self, bet_type: str) -> Optional[Any]:
        """
        Get aggressive/high-risk choice for the given bet type.

        Args:
            bet_type: Type of bet to make choice for

        Returns:
            Appropriate high-risk choice for the bet type
        """
        if bet_type == "straight":
            risky_numbers = [0, 13, 17, 32, 36]
            return random.choice(risky_numbers)

        elif bet_type == "split":
            risky_splits = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (34, 35), (35, 36)]
            return random.choice(risky_splits)

        elif bet_type == "street":
            risky_streets = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
            return random.choice(risky_streets)

        elif bet_type == "corner":
            risky_corners = [
                (0, 1, 2, 3),
                (1, 2, 4, 5),
                (2, 3, 5, 6),
                (31, 32, 34, 35),
                (32, 33, 35, 36),
            ]
            return random.choice(risky_corners)

        elif bet_type == "line":
            return random.choice([1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31])

        elif bet_type == "dozen":
            return random.choice([1, 2, 3])

        elif bet_type == "column":
            return random.choice([1, 2, 3])

        else:
            return None

    def _calculate_aggressive_amount(self):
        """
        Calculate bet amount using aggressive strategy.

        Returns:
            Bet amount, increased after consecutive losses

        Strategy:
            - Base amount: 12.5% of balance (minimum 50)
            - Increases with consecutive losses (up to 3x multiplier)
        """
        balance = self.player.get_balance()
        base_amount = max(50, balance // 8)

        if self.consecutive_losses > 0:
            multiplier = min(3, 1 + self.consecutive_losses * 0.5)
            base_amount = int(base_amount * multiplier)

        return min(base_amount, balance)

    def make_bet_decision(self) -> Optional[Any]:
        """
        Make aggressive betting decision.

        Returns:
            A Bet object if decision is made, None if skipping turn or invalid

        Strategy:
            - 5% chance to skip betting
            - Uses large bet amounts (12.5% of balance, minimum 50)
            - Increases bets after losses
            - Prefers high-risk, high-reward bet types
        """
        if self.player.get_balance() <= 0:
            return None

        if random.random() < 0.05:
            return None

        bet_type = self._weighted_type()
        bet_amount = self._calculate_aggressive_amount()
        bet_choice = self._aggressive_choice(bet_type)

        if not bet_choice:
            return None

        bet = self.bet_factory.create_bet(bet_type, bet_amount, choice=bet_choice)

        if bet and bet.validate():
            return bet

        return None


class PatternBotController:
    """
    AI controller that uses pattern recognition for betting decisions.

    Analyzes recent winning numbers to detect patterns and bet against them
    (assuming patterns will break - gambler's fallacy strategy).
    """

    def __init__(self, player: Player) -> None:
        """
        Initialize pattern-based bot controller.

        Args:
            player: The player instance to control
        """
        self.player = player
        self.bet_factory = BetFactory()
        self.last_5_numbers = []
        self.weights_dict = {"color": 0.4, "even_odd": 0.4, "high_low": 0.2}

    def _weighted_type(self) -> str:
        """
        Select bet type based on weighted probabilities.

        Returns:
            Selected bet type string
        """
        choices = list(self.weights_dict.keys())
        weights = list(self.weights_dict.values())
        return random.choices(choices, weights=weights, k=1)[0]

    def _pattern_choice(self, bet_type: str) -> Optional[Any]:
        """
        Get choice based on detected patterns in recent numbers.

        Args:
            bet_type: Type of bet to make choice for

        Returns:
            Choice that bets against recent patterns, or basic choice if no clear pattern
        """
        if len(self.last_5_numbers) < 2:
            return self._basic_choice(bet_type)

        last_two = self.last_5_numbers[-2:]

        if bet_type == "color":
            colors = [self._is_red(n) for n in last_two if n != 0]
            if len(colors) == 2 and all(colors):
                return "black"
            elif len(colors) == 2 and not any(colors):
                return "red"
            else:
                return self._basic_choice(bet_type)

        elif bet_type == "even_odd":
            parities = [n % 2 == 0 for n in last_two if n != 0]
            if len(parities) == 2 and all(parities):
                return "odd"
            elif len(parities) == 2 and not any(parities):
                return "even"
            else:
                return self._basic_choice(bet_type)

        else:
            return self._basic_choice(bet_type)

    def _basic_choice(self, bet_type: str) -> Optional[Any]:
        """
        Get basic random choice when no clear pattern is detected.

        Args:
            bet_type: Type of bet to make choice for

        Returns:
            Random choice for the bet type
        """
        if bet_type == "color":
            return random.choice(["red", "black"])
        elif bet_type == "even_odd":
            return random.choice(["even", "odd"])
        elif bet_type == "high_low":
            return random.choice(["high", "low"])
        else:
            return None

    def _is_red(self, number: int) -> bool:
        """
        Check if a number is red on roulette wheel.

        Args:
            number: The number to check

        Returns:
            True if number is red, False if black
        """
        reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        return number in reds

    def make_bet_decision(self) -> Optional[Any]:
        """
        Make pattern-based betting decision.

        Returns:
            A Bet object if decision is made, None if invalid

        Strategy:
            - Uses medium bet amounts (10% of balance, minimum 20)
            - Bets against detected patterns in recent numbers
            - Focuses on color, even/odd, and high/low bets
        """
        if self.player.get_balance() <= 0:
            return None

        bet_type = self._weighted_type()
        bet_amount = max(20, self.player.get_balance() // 10)

        bet_choice = self._pattern_choice(bet_type)
        if not bet_choice:
            return None

        bet = self.bet_factory.create_bet(bet_type, bet_amount, choice=bet_choice)

        if bet and bet.validate():
            return bet

        return None

    def update_history(self, winning_number) -> None:
        """
        Update history with latest winning number for pattern analysis.

        Args:
            winning_number: The latest winning number to add to history
        """
        self.last_5_numbers.append(winning_number)
        if len(self.last_5_numbers) > 5:
            self.last_5_numbers.pop(0)
