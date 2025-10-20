from abc import ABC, abstractmethod


class Bet(ABC):
    def __init__(self, amount, payout):
        self.amount = amount
        self.payout = payout

    def get_payout(self):
        return self.payout

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def is_winning(self, winning_number):
        pass


class StraightBet(Bet):
    def __init__(self, amount, number):
        super().__init__(amount, 35)
        self.number = number

    def validate(self):
        return self.number in list(range(0, 36))

    def is_winning(self, winning_number):
        return self.number == winning_number


class SplitBet(Bet):
    def __init__(self, amount, numbers):
        super().__init__(amount, 17)
        self.numbers = numbers

    def validate(self):
        for number in self.numbers:
            if number > 36 or number < 0:
                return False

        difference = abs(self.numbers[0] - self.numbers[1])
        return difference == 1 or difference == 3

    def is_winning(self, winning_number):
        return winning_number in self.numbers


class StreetBet(Bet):
    def __init__(self, amount, street_number):
        super().__init__(amount, 11)
        self.street_number = street_number

    def validate(self, street_number):
        is_on_board = street_number < 34 and street_number > 0
        return street_number % 3 == 0 and is_on_board

    def is_winning(self, winning_number):
        numbers_in_street = range(self.street_number, self.street_number + 3)
        return winning_number in numbers_in_street


class CornerBet(Bet):
    def __init__(self, amount, numbers):
        super().__init__(amount, 8)
        self.numbers = numbers

    def validate(self):
        for number in self.numbers:
            if number > 36 and number < 0:
                return False

        if len(self.numbers) == 4:
            is_corner = True
            sorted_numbers = sorted(self.numbers)
            is_corner = is_corner and (sorted_numbers[1] - sorted_numbers[0] == 1)
            is_corner = is_corner and (sorted_numbers[2] - sorted_numbers[0] == 3)
            is_corner = is_corner and (sorted_numbers[3] - sorted_numbers[2] == 1)
            return is_corner

        return False

    def is_winning(self, winning_number):
        return winning_number in self.numbers


class LineBet(Bet):
    def __init__(self, amount, line_number):
        super().__init__(amount, 5)
        self.line_number = line_number

    def validate(self):
        is_on_board = self.line_number < 31 and self.line_number > 0
        return self.line_number % 3 == 0 and is_on_board

    def is_winning(self, winning_number):
        numbers_in_line = list(range(self.line_number, self.line_number + 6))
        return winning_number in numbers_in_line


class ColumnBet(Bet):
    def __init__(self, amount, column_number):
        super().__init__(amount, 2)
        self.column_number = column_number

    def validate(self):
        return self.column_number in range(1, 4)

    def is_winning(self, winning_number):
        return winning_number % 3 == self.column_number % 3


class ColorBet(Bet):
    def __init__(self, amount, color):
        super().__init__(amount, 1)
        self.color = color

    def validate(self):
        return self.color in ["red", "black"]

    def is_winning(self, winning_number):
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
        if self.color == "red":
            return winning_number in red_numbers
        elif self.color == "black":
            return winning_number < 37 and not winning_number in red_numbers


class EvenOddBet(Bet):
    def __init__(self, amount, even_odd):
        super().__init__(amount, 1)
        self.even_odd = even_odd

    def validate(self):
        return self.even_odd in [0, 1]

    def is_winning(self, winning_number):
        return winning_number % 2 == self.even_odd


class HighLowBet(Bet):
    def __init__(self, amount, high_low):
        super().__init__(amount, 1)
        self.high_low = high_low

    def validate(self):
        return self.high_low in ["high", "low"]

    def is_winning(self, winning_number):
        if self.high_low == "high":
            return winning_number in list(range(19, 37))
        elif self.high_low == "low":
            return winning_number in list(range(1, 19))


class BetFactory:
    @staticmethod
    def create_bet(bet_type, amount, **kwargs):
        if bet_type == "straight":
            return StraightBet(amount, kwargs["choice"])
        elif bet_type == "split":
            return SplitBet(amount, kwargs["choice"])
        elif bet_type == "street":
            return StreetBet(amount, kwargs["choice"])
        elif bet_type == "corner":
            return CornerBet(amount, kwargs["choice"])
        elif bet_type == "line":
            return LineBet(amount, kwargs["choice"])
        elif bet_type == "column":
            return ColumnBet(amount, kwargs["choice"])
        elif bet_type == "color":
            return ColorBet(amount, kwargs["choice"])
        elif bet_type == "even_odd":
            return EvenOddBet(amount, kwargs["choice"])
        elif bet_type == "high_low":
            return HighLowBet(amount, kwargs["choice"])
        else:
            raise ValueError(f"Unknown bet type: {bet_type}")
