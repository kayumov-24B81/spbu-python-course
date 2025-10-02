from typing import Iterable
import math


class Vector:
    values: Iterable[int | float] = []

    def __init__(self, *values: int | float):
        self.values = values

    def __mul__(self, vector) -> int | float:
        product = 0
        for x, y in zip(self.values, vector.values):
            product += x * y
        return product

    def length(self):
        sq_sum = 0
        for x in self.values:
            sq_sum += x**2
        return math.sqrt(sq_sum)

    def angle(self, vector):
        numerator = self * vector
        denominator = self.length() * vector.length()
        return math.acos(numerator / denominator) * 180 / math.pi
