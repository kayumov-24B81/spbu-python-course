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
                colors[number] = "black"
        return colors

    def spin(self):
        number = random.choice(self.numbers)
        return (number, self.colors[number])
