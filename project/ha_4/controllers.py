from player import Player
from betting_interface import BettingInterface, BetFactory
import random


class HumanPlayerController:
    def __init__(self, player: Player, betting_interface: BettingInterface):
        self.player = player
        self.betting_interface = betting_interface

    def make_bet_decision(self):
        bet = self.betting_interface.get_validated_bet(self.player.get_balance())

        if bet:
            return bet

        return None


class ConservativeBotController:
    def __init__(self, player):
        self.player = player
        self.bet_factory = BetFactory()
        self.weights_dict = {
            "high_low": 0.2,
            "even_odd": 0.2,
            "color": 0.3,
            "column": 0.2,
            "line": 0.1,
        }

    def _weighted_type(self):
        choices = list(self.weights_dict.keys())
        weights = list(self.weights_dict.values())
        return random.choices(choices, weights=weights, k=1)[0]

    def _conservative_choice(self, bet_type):
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

    def make_bet_decision(self):
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
    def __init__(self, player):
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

    def _weighted_type(self):
        choices = list(self.weights_dict.keys())
        weights = list(self.weights_dict.values())
        return random.choices(choices, weights=weights, k=1)[0]

    def _aggressive_choice(self, bet_type):
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
        balance = self.player.get_balance()
        base_amount = max(50, balance // 8)

        if self.consecutive_losses > 0:
            multiplier = min(3, 1 + self.consecutive_losses * 0.5)
            base_amount = int(base_amount * multiplier)

        return min(base_amount, balance)

    def make_bet_decision(self):
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
    def __init__(self, player):
        self.player = player
        self.bet_factory = BetFactory()
        self.last_5_numbers = []
        self.weights_dict = {"color": 0.4, "even_odd": 0.4, "high_low": 0.2}

    def _weighted_type(self):
        choices = list(self.weights_dict.keys())
        weights = list(self.weights_dict.values())
        return random.choices(choices, weights=weights, k=1)[0]

    def _pattern_choice(self, bet_type):
        if len(self.last_5_numbers) < 2:
            return self._basic_choice(bet_type)

        last_two = self.last_5_numbers[-2:]

        if bet_type == "color":
            colors = [self._is_red(n) for n in last_two if n != 0 and n != "00"]
            if len(colors) == 2 and all(colors):
                return "black"
            elif len(colors) == 2 and not any(colors):
                return "red"
            else:
                return self._basic_choice(bet_type)

        elif bet_type == "even_odd":
            parities = [n % 2 == 0 for n in last_two if n != 0 and n != "00"]
            if len(parities) == 2 and all(parities):
                return "odd"
            elif len(parities) == 2 and not any(parities):
                return "even"
            else:
                return self._basic_choice(bet_type)

        else:
            return self._basic_choice(bet_type)

    def _basic_choice(self, bet_type):
        if bet_type == "color":
            return random.choice(["red", "black"])
        elif bet_type == "even_odd":
            return random.choice(["even", "odd"])
        elif bet_type == "high_low":
            return random.choice(["high", "low"])
        else:
            return None

    def _is_red(self, number):
        reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        return number in reds

    def make_bet_decision(self):
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

    def update_history(self, winning_number):
        self.last_5_numbers.append(winning_number)
        if len(self.last_5_numbers) > 5:
            self.last_5_numbers.pop(0)
