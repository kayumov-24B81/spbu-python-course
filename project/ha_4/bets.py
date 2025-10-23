from abc import ABC, abstractmethod
from typing import List, Union, Literal


class Bet(ABC):
    """Abstract base class representing a roulette bet."""

    def __init__(self, amount: float, payout: int) -> None:
        """
        Initialize a bet.

        Args:
            amount: The amount of money wagered
            payout: The payout multiplier if the bet wins
        """
        self.amount = amount
        self.payout = payout

    def get_payout(self) -> int:
        """
        Get the payout multiplier for this bet.

        Returns:
            The payout multiplier as an integer
        """
        return self.payout

    def get_amount(self) -> float:
        """
        Get the amount wagered on this bet.

        Returns:
            The bet amount
        """
        return self.amount

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate if the bet parameters are correct.

        Returns:
            True if the bet is valid, False otherwise
        """
        pass

    @abstractmethod
    def is_winning(self, winning_number) -> bool:
        """
        Check if this bet wins given the winning number.

        Args:
            winning_number: The winning roulette number (0-36)

        Returns:
            True if the bet wins, False otherwise
        """
        pass

    @abstractmethod
    def get_type(self) -> str:
        """
        Get a string description of the bet type.

        Returns:
            String describing the bet type
        """
        pass


class StraightBet(Bet):
    """Bet on a single number."""

    def __init__(self, amount: float, number: int) -> None:
        """
        Initialize a straight bet.

        Args:
            amount: The amount wagered
            number: The number to bet on (0-36)
        """
        super().__init__(amount, 35)
        self.number = number

    def validate(self) -> bool:
        """
        Validate that the bet number is within 0-36 range.

        Returns:
            True if number is between 0 and 36 inclusive
        """
        return self.number in list(range(0, 37))

    def is_winning(self, winning_number: int) -> bool:
        """
        Check if the bet wins (exact match with winning number).

        Args:
            winning_number: The winning roulette number

        Returns:
            True if the bet number matches winning number
        """
        return self.number == winning_number

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the straight bet
        """
        return f"straight: {self.number}"


class SplitBet(Bet):
    """Bet on two adjacent numbers."""

    def __init__(self, amount: float, numbers: List[int]) -> None:
        """
        Initialize a split bet.

        Args:
            amount: The amount wagered
            numbers: List of two adjacent numbers to bet on
        """
        super().__init__(amount, 17)
        self.numbers = numbers

    def validate(self) -> bool:
        """
        Validate that the numbers are adjacent on the roulette table.

        Returns:
            True if numbers are valid adjacent numbers (difference of 1 or 3)
        """
        if len(self.numbers) != 2:
            return False

        for number in self.numbers:
            if number > 36 or number < 0:
                return False

        difference = abs(self.numbers[0] - self.numbers[1])
        return difference == 1 or difference == 3

    def is_winning(self, winning_number) -> bool:
        """
        Check if either of the two numbers wins.

        Args:
            winning_number: The winning roulette number

        Returns:
            True if winning number matches either of the two bet numbers
        """
        return winning_number in self.numbers

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the split bet
        """
        return f"split: {self.numbers[0]}, {self.numbers[1]}"


class StreetBet(Bet):
    """Bet on three numbers in a horizontal line (street)."""

    def __init__(self, amount: float, street_number: int) -> None:
        """
        Initialize a street bet.

        Args:
            amount: The amount wagered
            street_number: The first number of the street (1, 4, 7, etc.)
        """
        super().__init__(amount, 11)
        self.street_number = street_number

    def validate(self) -> bool:
        """
        Validate that the street number is valid.

        Returns:
            True if street number is valid (1-34 and divisible by 3 with remainder 1)
        """
        is_on_board = self.street_number < 35 and self.street_number > 0
        return self.street_number % 3 == 1 and is_on_board

    def is_winning(self, winning_number) -> bool:
        """
        Check if the winning number is in this street.

        Args:
            winning_number: The winning roulette number

        Returns:
            True if winning number is in the street range
        """
        numbers_in_street = range(self.street_number, self.street_number + 3)
        return winning_number in numbers_in_street

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the street bet
        """
        return f"street: street number - {self.street_number}"


class CornerBet(Bet):
    """Bet on four numbers that form a square on the roulette table."""

    def __init__(self, amount: float, numbers: List[int]) -> None:
        """
        Initialize a corner bet.

        Args:
            amount: The amount wagered
            numbers: List of four numbers forming a square
        """
        super().__init__(amount, 8)
        self.numbers = numbers

    def validate(self) -> bool:
        """
        Validate that the numbers form a valid corner.

        Returns:
            True if numbers form a valid corner/square pattern
        """
        for number in self.numbers:
            if number > 36 or number < 1:
                return False

        if len(self.numbers) == 4:
            is_corner = True
            sorted_numbers = sorted(self.numbers)
            is_corner = is_corner and (sorted_numbers[1] - sorted_numbers[0] == 1)
            is_corner = is_corner and (sorted_numbers[2] - sorted_numbers[0] == 3)
            is_corner = is_corner and (sorted_numbers[3] - sorted_numbers[2] == 1)
            return is_corner

        return False

    def is_winning(self, winning_number: int) -> bool:
        """
        Check if the winning number is in the corner.

        Args:
            winning_number: The winning roulette number

        Returns:
            True if winning number matches any of the four corner numbers
        """
        return winning_number in self.numbers

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the corner bet
        """
        return f"corner: {self.numbers[0]}, {self.numbers[1]}, {self.numbers[2]}, {self.numbers[3]}"


class LineBet(Bet):
    """Bet on six numbers in two adjacent streets."""

    def __init__(self, amount: float, line_number: int):
        """
        Initialize a line bet.

        Args:
            amount: The amount wagered
            line_number: The first number of the line (1, 4, 7, etc. up to 31)
        """
        super().__init__(amount, 5)
        self.line_number = line_number

    def validate(self) -> bool:
        """
        Validate that the line number is valid.

        Returns:
            True if line number is valid (1-31 and divisible by 3 with remainder 1)
        """
        is_on_board = self.line_number <= 31 and self.line_number > 0
        return self.line_number % 3 == 1 and is_on_board

    def is_winning(self, winning_number: int) -> bool:
        """
        Check if the winning number is in this line.

        Args:
            winning_number: The winning roulette number

        Returns:
            True if winning number is in the line range
        """
        numbers_in_line = list(range(self.line_number, self.line_number + 6))
        return winning_number in numbers_in_line

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the line bet
        """
        return f"line: line number - {self.line_number}"


class ColumnBet(Bet):
    """Bet on one of the three vertical columns."""

    def __init__(self, amount: float, column_number: int) -> None:
        """
        Initialize a column bet.

        Args:
            amount: The amount wagered
            column_number: The column number (1, 2, or 3)
        """
        super().__init__(amount, 2)
        self.column_number = column_number

    def validate(self) -> bool:
        """
        Validate that the column number is valid.

        Returns:
            True if column number is 1, 2, or 3
        """
        return self.column_number in range(1, 4)

    def is_winning(self, winning_number) -> bool:
        """
        Check if the winning number is in the chosen column.

        Args:
            winning_number: The winning roulette number

        Returns:
            True if winning number is in the chosen column
        """
        return winning_number % 3 == self.column_number % 3

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the column bet
        """
        return f"column: column number - {self.column_number}"


class ColorBet(Bet):
    """Bet on red or black color."""

    def __init__(self, amount: float, color: str) -> None:
        """
        Initialize a color bet.

        Args:
            amount: The amount wagered
            color: The color to bet on ("red" or "black")
        """
        super().__init__(amount, 1)
        self.color = color

    def validate(self) -> bool:
        """
        Validate that the color is valid.

        Returns:
            True if color is "red" or "black"
        """
        return self.color in ["red", "black"]

    def is_winning(self, winning_number) -> bool:
        """
        Check if the winning number matches the chosen color.

        Args:
            winning_number: The winning roulette number

        Returns:
            True if winning number matches the chosen color (0 always loses)
        """
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
        if winning_number == 0:
            return False
        if self.color == "red":
            return winning_number in red_numbers
        elif self.color == "black":
            return winning_number < 37 and not winning_number in red_numbers

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the color bet
        """
        return "color: " + self.color


class EvenOddBet(Bet):
    """Bet on even or odd numbers."""

    def __init__(self, amount: float, even_odd: str) -> None:
        """
        Initialize an even/odd bet.

        Args:
            amount: The amount wagered
            even_odd: "even" or "odd"
        """
        super().__init__(amount, 1)
        self.even_odd = even_odd

    def validate(self) -> bool:
        """
        Validate that the even_odd parameter is valid.

        Returns:
            True if even_odd is "even" or "odd"
        """
        return self.even_odd in ["even", "odd"]

    def is_winning(self, winning_number) -> bool:
        """
        Check if the winning number matches the even/odd choice.

        Args:
            winning_number: The winning roulette number

        Returns:
            True if winning number matches the even/odd choice (0 always loses)
        """
        if self.even_odd == "even":
            return winning_number % 2 == 0 and winning_number != 0
        elif self.even_odd == "odd":
            return winning_number % 2 == 1

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the even/odd bet
        """
        return "even or odd: " + self.even_odd


class HighLowBet(Bet):
    """Bet on high (19-36) or low (1-18) numbers."""

    def __init__(self, amount: float, high_low: str) -> None:
        """
        Initialize a high/low bet.

        Args:
            amount: The amount wagered
            high_low: "high" or "low"
        """
        super().__init__(amount, 1)
        self.high_low = high_low

    def validate(self) -> bool:
        """
        Validate that the high_low parameter is valid.

        Returns:
            True if high_low is "high" or "low"
        """
        return self.high_low in ["high", "low"]

    def is_winning(self, winning_number) -> bool:
        """
        Check if the winning number is in the high/low range.

        Args:
            winning_number: The winning roulette number

        Returns:
            True if winning number is in the chosen range (0 always loses)
        """
        if self.high_low == "high":
            return winning_number in list(range(19, 37))
        elif self.high_low == "low":
            return winning_number in list(range(1, 19))

    def get_type(self) -> str:
        """
        Get bet type description.

        Returns:
            String describing the high/low bet
        """
        return "high or low: " + self.high_low


class BetFactory:
    """Factory class for creating different types of roulette bets."""

    @staticmethod
    def create_bet(bet_type, amount, **kwargs):
        """
        Create a bet instance based on the bet type.

        Args:
            bet_type: Type of bet to create
            amount: The amount to wager
            **kwargs: Additional parameters required for specific bet types:
                - straight: choice (int)
                - split: choice (List[int])
                - street: choice (int)
                - corner: choice (List[int])
                - line: choice (int)
                - column: choice (int)
                - color: choice (str)
                - even_odd: choice (str)
                - high_low: choice (str)

        Returns:
            A Bet instance of the specified type

        Raises:
            ValueError: If bet_type is unknown or missing required parameters
        """
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
