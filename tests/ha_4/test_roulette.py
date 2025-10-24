import pytest
from unittest.mock import patch
from project.ha_4.roulette import Roulette
from project.ha_4.bets import StraightBet


class TestRoulette:
    """
    Unit tests for Roulette class

    Tests roulette wheel functionality, number generation, and color mapping.
    """

    @pytest.fixture
    def roulette(self):
        """Fixture providing a Roulette instance"""
        return Roulette()

    def test_initialization(self, roulette):
        """Tests that Roulette initializes successfully"""
        assert roulette is not None

    def test_spin_returns_tuple(self, roulette):
        """Tests that spin returns a tuple of (number, color)"""
        result = roulette.spin()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_spin_returns_valid_number_range(self, roulette):
        """Tests that spin returns numbers in valid roulette range (0-36)"""
        number, color = roulette.spin()
        assert 0 <= number <= 36

    def test_spin_returns_valid_color(self, roulette):
        """Tests that spin returns valid roulette colors"""
        number, color = roulette.spin()
        assert color in ["red", "black", "green"]

    @pytest.mark.parametrize(
        "mock_number, expected_color",
        [
            (0, "green"),
            (1, "red"),
            (2, "black"),
            (3, "red"),
            (36, "red"),
            (35, "black"),
        ],
    )
    def test_color_mapping(self, roulette, mock_number, expected_color):
        """Tests that numbers map to correct colors according to roulette rules"""
        with patch("random.choice", return_value=mock_number):
            number, color = roulette.spin()
            assert number == mock_number
            assert color == expected_color

    def test_spin_distribution(self, roulette):
        """Tests that multiple spins produce varied results within expected ranges"""
        results = []
        colors = []

        for _ in range(1000):
            number, color = roulette.spin()
            results.append(number)
            colors.append(color)

        assert all(0 <= num <= 36 for num in results)

        assert all(color in ["red", "black", "green"] for color in colors)

        unique_numbers = set(results)
        assert len(unique_numbers) > 1

        unique_colors = set(colors)
        assert len(unique_colors) >= 2

    def test_zero_is_green(self, roulette):
        """Tests that number 0 always returns green color"""
        with patch("random.choice", return_value=0):
            number, color = roulette.spin()
            assert number == 0
            assert color == "green"

    def test_red_numbers_correct(self, roulette):
        """Tests all standard red numbers return correct color"""
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

        for number in red_numbers:
            with patch("random.choice", return_value=number):
                _, color = roulette.spin()
                assert color == "red"

    def test_black_numbers_correct(self, roulette):
        """Tests all standard black numbers return correct color"""
        black_numbers = [
            2,
            4,
            6,
            8,
            10,
            11,
            13,
            15,
            17,
            20,
            22,
            24,
            26,
            28,
            29,
            31,
            33,
            35,
        ]

        for number in black_numbers:
            with patch("random.choice", return_value=number):
                _, color = roulette.spin()
                assert color == "black"


class TestRouletteGameIntegration:
    """
    Integration tests for Roulette with betting system

    Tests how roulette results interact with bet outcomes.
    """

    def test_roulette_results_affect_bets(self):
        """Tests that roulette spin results correctly determine bet wins/losses"""
        roulette = Roulette()

        bet = StraightBet(100, 17)

        with patch("random.choice", return_value=17):
            winning_number, _ = roulette.spin()
            assert bet.is_winning(winning_number) == True

        with patch("random.choice", return_value=18):
            losing_number, _ = roulette.spin()
            assert bet.is_winning(losing_number) == False

    def test_multiple_spins_produce_different_results(self):
        """Tests that consecutive spins produce varied outcomes"""
        roulette = Roulette()
        results = set()

        for _ in range(50):
            number, color = roulette.spin()
            results.add((number, color))

        assert len(results) > 1

    def test_roulette_state_independence(self):
        """Tests that multiple roulette instances operate independently"""
        roulette1 = Roulette()
        roulette2 = Roulette()

        results1 = [roulette1.spin() for _ in range(10)]
        results2 = [roulette2.spin() for _ in range(10)]

        for number, color in results1 + results2:
            assert 0 <= number <= 36
            assert color in ["red", "black", "green"]


class TestRouletteEdgeCases:
    """
    Tests for edge cases and statistical properties

    Tests comprehensive number coverage and color distribution.
    """

    def test_all_possible_numbers_generated(self):
        """Tests that all roulette numbers (0-36) can be generated"""
        roulette = Roulette()
        generated_numbers = set()

        for _ in range(1000):
            number, _ = roulette.spin()
            generated_numbers.add(number)

        assert generated_numbers == set(range(0, 37))

    def test_color_distribution_approximately_correct(self):
        """
        Tests that color distribution follows expected roulette probabilities:
        - ~48.6% red (18/37)
        - ~48.6% black (18/37)
        - ~2.7% green (1/37)
        """
        roulette = Roulette()

        red_count = 0
        black_count = 0
        green_count = 0
        total_spins = 10000

        for _ in range(total_spins):
            _, color = roulette.spin()
            if color == "red":
                red_count += 1
            elif color == "black":
                black_count += 1
            elif color == "green":
                green_count += 1

        red_ratio = red_count / total_spins
        black_ratio = black_count / total_spins
        green_ratio = green_count / total_spins

        assert 0.45 < red_ratio < 0.55
        assert 0.45 < black_ratio < 0.55
        assert 0.01 < green_ratio < 0.05
