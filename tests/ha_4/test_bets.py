from project.ha_4.bets import *
import pytest


class TestStraightBet:
    """
    Tests for Straight Bet (single number bet)

    Bet on a single number from 0 to 36. Payout 35:1.
    """

    @pytest.mark.parametrize(
        "number, is_valid",
        [(0, True), (17, True), (36, True), (-1, False), (37, False), (100, False)],
    )
    def test_straight_bet_validation(self, number, is_valid):
        """Tests number validation for straight bets"""
        bet = StraightBet(100, number)
        assert bet.validate() == is_valid

    @pytest.mark.parametrize(
        "bet_number, winning_number, should_win",
        [
            (17, 17, True),
            (17, 18, False),
            (0, 0, True),
            (0, 1, False),
        ],
    )
    def test_straight_bet_winning_conditions(
        self, bet_number, winning_number, should_win
    ):
        """Tests winning conditions for straight bets"""
        bet = StraightBet(100, bet_number)
        assert bet.is_winning(winning_number) == should_win


class TestSplitBet:
    """
    Tests for Split Bet (two adjacent numbers)

    Bet on two adjacent numbers. Payout 17:1.
    Numbers must be vertically or horizontally adjacent on roulette layout.
    """

    @pytest.mark.parametrize(
        "numbers, is_valid",
        [
            ([1, 2], True),
            ([1, 4], True),
            ([2, 3], True),
            ([35, 36], True),
            ([1, 5], False),
            ([1, 37], False),
            ([1], False),
            ([1, 2, 3], False),
        ],
    )
    def test_split_bet_validation(self, numbers, is_valid):
        """Tests number pair validation for split bets"""
        bet = SplitBet(100, numbers)
        assert bet.validate() == is_valid

    @pytest.mark.parametrize(
        "numbers, winning_number, should_win",
        [
            ([1, 2], 1, True),
            ([1, 2], 2, True),
            ([1, 2], 3, False),
            ([1, 2], 0, False),
        ],
    )
    def test_split_bet_winning_conditions(self, numbers, winning_number, should_win):
        """Tests winning conditions for split bets"""
        bet = SplitBet(100, numbers)
        assert bet.is_winning(winning_number) == should_win


class TestStreetBet:
    """
    Tests for Street Bet (three numbers in a row)

    Bet on three consecutive numbers in a horizontal line. Payout 11:1.
    Street numbers: 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34
    """

    @pytest.mark.parametrize(
        "street_number, is_valid",
        [
            (1, True),
            (4, True),
            (7, True),
            (34, True),
            (0, False),
            (2, False),
            (35, False),
            (37, False),
        ],
    )
    def test_street_bet_validation(self, street_number, is_valid):
        """Tests street number validation"""
        bet = StreetBet(100, street_number)
        assert bet.validate() == is_valid

    @pytest.mark.parametrize(
        "street_number, winning_numbers",
        [
            (1, [1, 2, 3]),
            (4, [4, 5, 6]),
            (34, [34, 35, 36]),
        ],
    )
    def test_street_bet_winning_conditions(self, street_number, winning_numbers):
        """Tests winning conditions for street bets"""
        bet = StreetBet(100, street_number)

        for number in winning_numbers:
            assert bet.is_winning(number) == True

        assert bet.is_winning(0) == False
        assert bet.is_winning(winning_numbers[0] - 1) == False
        assert bet.is_winning(winning_numbers[-1] + 1) == False


class TestCornerBet:
    """
    Tests for Corner Bet (four adjacent numbers)

    Bet on four numbers that form a square. Payout 8:1.
    Example: [1, 2, 4, 5] forms a valid corner bet.
    """

    @pytest.mark.parametrize(
        "numbers, is_valid",
        [
            ([1, 2, 4, 5], True),
            ([2, 3, 5, 6], True),
            ([32, 33, 35, 36], True),
            ([1, 2, 3, 4], False),
            ([1, 2, 4], False),
            ([0, 1, 3, 4], False),
        ],
    )
    def test_corner_bet_validation(self, numbers, is_valid):
        """Tests corner number validation"""
        bet = CornerBet(100, numbers)
        assert bet.validate() == is_valid

    @pytest.mark.parametrize(
        "numbers, winning_number, should_win",
        [
            ([1, 2, 4, 5], 1, True),
            ([1, 2, 4, 5], 2, True),
            ([1, 2, 4, 5], 4, True),
            ([1, 2, 4, 5], 5, True),
            ([1, 2, 4, 5], 0, False),
            ([1, 2, 4, 5], 3, False),
            ([1, 2, 4, 5], 6, False),
            ([1, 2, 4, 5], 7, False),
            ([1, 2, 4, 5], 36, False),
            ([32, 33, 35, 36], 32, True),
            ([32, 33, 35, 36], 33, True),
            ([32, 33, 35, 36], 35, True),
            ([32, 33, 35, 36], 36, True),
            ([32, 33, 35, 36], 31, False),
            ([32, 33, 35, 36], 34, False),
            ([17, 18, 20, 21], 17, True),
            ([17, 18, 20, 21], 18, True),
            ([17, 18, 20, 21], 20, True),
            ([17, 18, 20, 21], 21, True),
            ([17, 18, 20, 21], 16, False),
            ([17, 18, 20, 21], 19, False),
            ([17, 18, 20, 21], 22, False),
        ],
    )
    def test_corner_bet_winning_conditions(self, numbers, winning_number, should_win):
        """Tests winning conditions for corner bets"""
        bet = CornerBet(100, numbers)
        assert bet.is_winning(winning_number) == should_win


class TestColorBet:
    """
    Tests for Color Bet (red or black)

    Bet on all red or all black numbers. Payout 1:1.
    Zero (0) is not included in either color (is green).
    """

    @pytest.mark.parametrize(
        "color, is_valid",
        [
            ("red", True),
            ("black", True),
            ("green", False),
            ("blue", False),
            ("", False),
        ],
    )
    def test_color_bet_validation(self, color, is_valid):
        """Tests color validation"""
        bet = ColorBet(100, color)
        assert bet.validate() == is_valid

    @pytest.mark.parametrize(
        "color, winning_number, should_win",
        [
            ("red", 1, True),
            ("red", 3, True),
            ("red", 2, False),
            ("red", 0, False),
            ("black", 2, True),
            ("black", 4, True),
            ("black", 1, False),
            ("black", 0, False),
        ],
    )
    def test_color_bet_winning_conditions(self, color, winning_number, should_win):
        """Tests winning conditions for color bets"""
        bet = ColorBet(100, color)
        assert bet.is_winning(winning_number) == should_win


class TestEvenOddBet:
    """
    Tests for Even/Odd Bet

    Bet on all even or all odd numbers. Payout 1:1.
    Zero (0) is not included in either category.
    """

    @pytest.mark.parametrize(
        "choice, is_valid",
        [("even", True), ("odd", True), ("both", False), ("", False)],
    )
    def test_even_odd_bet_validation(self, choice, is_valid):
        """Tests even/odd choice validation"""
        bet = EvenOddBet(100, choice)
        assert bet.validate() == is_valid

    @pytest.mark.parametrize(
        "choice, winning_number, should_win",
        [
            ("even", 2, True),
            ("even", 4, True),
            ("even", 1, False),
            ("even", 0, False),
            ("odd", 1, True),
            ("odd", 3, True),
            ("odd", 2, False),
            ("odd", 0, False),
        ],
    )
    def test_even_odd_bet_winning_conditions(self, choice, winning_number, should_win):
        """Tests winning conditions for even/odd bets"""
        bet = EvenOddBet(100, choice)
        assert bet.is_winning(winning_number) == should_win


class TestHighLowBet:
    """
    Tests for High/Low Bet

    Bet on high (19-36) or low (1-18) numbers. Payout 1:1.
    Zero (0) is not included in either category.
    """

    @pytest.mark.parametrize(
        "choice, is_valid",
        [
            ("high", True),
            ("low", True),
            ("middle", False),
            ("", False),
        ],
    )
    def test_high_low_bet_validation(self, choice, is_valid):
        """Tests high/low choice validation"""
        bet = HighLowBet(100, choice)
        assert bet.validate() == is_valid

    @pytest.mark.parametrize(
        "choice, winning_number, should_win",
        [
            ("low", 1, True),
            ("low", 18, True),
            ("low", 19, False),
            ("low", 0, False),
            ("high", 19, True),
            ("high", 36, True),
            ("high", 18, False),
            ("high", 0, False),
        ],
    )
    def test_high_low_bet_winning_conditions(self, choice, winning_number, should_win):
        """Tests winning conditions for high/low bets"""
        bet = HighLowBet(100, choice)
        assert bet.is_winning(winning_number) == should_win


class TestBasicValues:
    """
    Tests for basic bet properties across all bet types

    Verifies payout ratios and type strings are consistent.
    """

    @pytest.mark.parametrize(
        "bet_class, bet_args, expected_payout",
        [
            (StraightBet, (100, 17), 35),
            (SplitBet, (100, [1, 2]), 17),
            (StreetBet, (100, 1), 11),
            (CornerBet, (100, [1, 2, 4, 5]), 8),
            (LineBet, (100, 1), 5),
            (ColumnBet, (100, 1), 2),
            (ColorBet, (100, "red"), 1),
            (EvenOddBet, (100, "even"), 1),
            (HighLowBet, (100, "high"), 1),
        ],
    )
    def test_all_bet_types_have_correct_payouts(
        self, bet_class, bet_args, expected_payout
    ):
        """Tests that all bet types have correct payout ratios"""
        bet = bet_class(*bet_args)
        assert bet.get_payout() == expected_payout

    @pytest.mark.parametrize(
        "bet_class, bet_args, expected_type",
        [
            (StraightBet, (100, 17), "straight: 17"),
            (SplitBet, (100, [1, 2]), "split: 1, 2"),
            (StreetBet, (100, 1), "street: street number - 1"),
            (CornerBet, (100, [1, 2, 4, 5]), "corner: 1, 2, 4, 5"),
            (LineBet, (100, 1), "line: line number - 1"),
            (ColumnBet, (100, 1), "column: column number - 1"),
            (ColorBet, (100, "red"), "color: red"),
            (EvenOddBet, (100, "even"), "even or odd: even"),
            (HighLowBet, (100, "high"), "high or low: high"),
        ],
    )
    def test_all_bet_types_have_correct_type_strings(
        self, bet_class, bet_args, expected_type
    ):
        """Tests that all bet types have correct type string representations"""
        bet = bet_class(*bet_args)
        assert bet.get_type() == expected_type


class TestFactory:
    """
    Tests for BetFactory class

    Verifies that factory correctly creates all bet types and handles errors.
    """

    @pytest.mark.parametrize(
        "bet_type, kwargs, expected_class",
        [
            ("straight", {"choice": 17}, StraightBet),
            ("split", {"choice": [1, 2]}, SplitBet),
            ("street", {"choice": 1}, StreetBet),
            ("corner", {"choice": [1, 2, 4, 5]}, CornerBet),
            ("line", {"choice": 1}, LineBet),
            ("column", {"choice": 1}, ColumnBet),
            ("color", {"choice": "red"}, ColorBet),
            ("even_odd", {"choice": "even"}, EvenOddBet),
            ("high_low", {"choice": "high"}, HighLowBet),
        ],
    )
    def test_bet_factory_creates_all_types(self, bet_type, kwargs, expected_class):
        """Tests that factory creates correct bet types"""
        factory = BetFactory()
        bet = factory.create_bet(bet_type, 100, **kwargs)
        assert isinstance(bet, expected_class)

    @pytest.mark.parametrize(
        "invalid_bet_type", ["unknown_type", "invalid", "random", "test"]
    )
    def test_bet_factory_invalid_types(self, invalid_bet_type):
        """Tests that factory raises errors for invalid bet types"""
        factory = BetFactory()
        with pytest.raises(ValueError, match="Unknown bet type"):
            factory.create_bet(invalid_bet_type, 100, choice=1)
