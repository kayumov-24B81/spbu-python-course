import random
from bets import *


class Roulette:
    def __init__(self):
        self.numbers = range(0, 37)
        self.colors = self._assign_colors()

    def _assign_colors(self):
        colors = {}
        red_numbers = [
            1,
            3,
            5,
            7,
            9,
            12,
            14,
            16,
            18,
            19,
            21,
            23,
            25,
            27,
            30,
            32,
            34,
            36,
        ]
        for number in self.numbers:
            if number == 0:
                colors[number] = "green"
            elif number in red_numbers:
                colors[number] = "red"
            else:
                colors[number] == "black"

    def spin(self):
        number = random.choice(self.numbers)
        return (number, self.colors[number])


class BettingInterface:
    BET_CONFIG = {
        "straight": {
            "description": "Bet on a single number",
            "message": "Enter one number (0-36): ",
            "converter": lambda x: int(x.strip()),
        },
        "split": {
            "description": "Bet on two adjacent numbers",
            "message": 'Enter two adjacent numbers separated by space (e.g., "1 2" or "1 4"): ',
            "converter": lambda x: [int(num.strip()) for num in x.split()[:2]],
        },
        "street": {
            "description": "Bet on three numbers in a row (e.g., 1-2-3, 4-5-6)",
            "message": "Enter the first number of the street (1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34): ",
            "converter": lambda x: int(x.strip()),
        },
        "corner": {
            "description": "Bet on four numbers forming a square (e.g., 1-2-4-5)",
            "message": 'Enter the four numbers of the corner separated by spaces (e.g., "1 2 4 5"): ',
            "converter": lambda x: [int(num.strip()) for num in x.split()[:4]],
        },
        "line": {
            "description": "Bet on six numbers from two adjacent rows (e.g., 1-2-3-4-5-6)",
            "message": "Enter the first number of the line (1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31): ",
            "converter": lambda x: int(x.strip()),
        },
        "column": {
            "description": "Bet on one of the three vertical columns",
            "message": "Enter the column number (1, 2, or 3): ",
            "converter": lambda x: int(x.strip()),
        },
        "color": {
            "description": "Bet on red or black color",
            "message": "Enter color (red or black): ",
            "converter": lambda x: x.strip().lower(),
        },
        "even_odd": {
            "description": "Bet on even or odd numbers",
            "message": "Enter choice (even or odd): ",
            "converter": lambda x: x.strip().lower(),
        },
        "high_low": {
            "description": "Bet on low (1-18) or high (19-36) numbers",
            "message": "Enter choice (low or high): ",
            "converter": lambda x: x.strip().lower(),
        },
    }

    def __init__(self):
        self.bet_factory = BetFactory()

    def _show_betting_options(self):
        print("AVAILABLE BETS: ")
        for name in self.BET_CONFIG:
            print(f" {name}: {self.BET_CONFIG[name]['description']}")

    def _recieve_bet(self):
        while True:
            bet_type = input("\nChoose the bet:\n")
            if bet_type in self.BET_CONFIG.keys():
                break
            print(f"{bet_type} is invalid bet!")

        bet_choice = self.BET_CONFIG[bet_type]["converter"](
            input(self.BET_CONFIG[bet_type]["message"])
        )
        return bet_type, bet_choice

    def place_bet_flow(self):
        self._show_betting_options()
        bet_type, bet_choice = self._recieve_bet()

        bet = self.bet_factory.create_bet(bet_type, 100, choice=bet_choice)
        print(type(bet).__name__)
