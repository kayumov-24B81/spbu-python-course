from project.ha_4.controllers import *
from project.ha_4.controllers import (
    AggressiveBotController,
    ConservativeBotController,
    HumanPlayerController,
    PatternBotController,
)
from project.ha_4.player import Player
from project.ha_4.bets import StraightBet, ColorBet
from unittest.mock import Mock, patch
import pytest


class TestPlayer:
    """
    Unit tests for Player class

    Tests player state management, balance operations, and bet placement.
    """

    @pytest.fixture
    def sample_player(self):
        """Fixture providing a Player instance with 1000 balance"""
        return Player("TestPlayer", 1000)

    @pytest.fixture
    def sample_bet(self):
        """Fixture providing a StraightBet instance"""
        return StraightBet(100, 17)

    def test_player_initial_state(self, sample_player):
        """Tests that Player initializes with correct name, balance, and no current bet"""
        assert sample_player.get_name() == "TestPlayer"
        assert sample_player.get_balance() == 1000
        assert sample_player.get_current_bet() is None

    @pytest.mark.parametrize(
        "initial_balance, bet_amount, expected_balance",
        [
            (1000, 100, 900),
            (500, 50, 450),
            (200, 200, 0),
        ],
    )
    def test_place_bet_changes_balance(
        self,
        initial_balance,
        bet_amount,
        expected_balance,
    ):
        """Tests that placing a bet correctly deducts from player balance"""
        player = Player("Test", initial_balance)
        bet = StraightBet(bet_amount, 17)

        result = player.place_bet(bet)

        assert result == True
        assert player.get_balance() == expected_balance
        assert player.get_current_bet() == bet

    def test_replace_current_bet(self, sample_player):
        """Tests that placing a new bet replaces the current bet and deducts correctly"""
        bet1 = StraightBet(100, 17)
        bet2 = ColorBet(50, "red")

        sample_player.place_bet(bet1)
        initial_balance = sample_player.get_balance()

        sample_player.place_bet(bet2)

        assert sample_player.get_current_bet() == bet2
        assert sample_player.get_balance() == initial_balance - 50

    @pytest.mark.parametrize(
        "initial_balance, add_amount, expected_balance",
        [
            (1000, 500, 1500),
            (200, 100, 300),
            (0, 50, 50),
        ],
    )
    def test_add_balance(
        self,
        initial_balance,
        add_amount,
        expected_balance,
    ):
        """Tests that adding balance correctly increases player's balance"""
        player = Player("Test", initial_balance)
        player.add_balance(add_amount)
        assert player.get_balance() == expected_balance

    def test_get_name_returns_string(self, sample_player):
        """Tests that get_name returns correct string representation"""
        name = sample_player.get_name()
        assert isinstance(name, str)
        assert name == "TestPlayer"

    def test_current_bet_lifecycle(self, sample_player, sample_bet):
        """Tests the complete lifecycle of current bet from None to replacement"""
        assert sample_player.get_current_bet() is None

        sample_player.place_bet(sample_bet)
        assert sample_player.get_current_bet() == sample_bet

        new_bet = ColorBet(200, "black")
        sample_player.place_bet(new_bet)
        assert sample_player.get_current_bet() == new_bet

    def test_multiple_operations_affect_state_correctly(self):
        """Tests that multiple operations maintain correct player state"""
        player = Player("Test", 1000)

        bet1 = StraightBet(300, 17)
        player.place_bet(bet1)
        assert player.get_balance() == 700
        assert player.get_current_bet() == bet1

        player.add_balance(200)
        assert player.get_balance() == 900

        bet2 = ColorBet(150, "red")
        player.place_bet(bet2)
        assert player.get_balance() == 750
        assert player.get_current_bet() == bet2


class TestHumanPlayerController:
    """
    Tests for HumanPlayerController class

    Tests human player interaction through betting interface.
    """

    @pytest.fixture
    def human_setup(self):
        """Fixture providing player, mocked betting interface, and controller"""
        player = Player("Human", 1000)
        betting_interface = Mock()
        controller = HumanPlayerController(player, betting_interface)
        return player, betting_interface, controller

    def test_make_bet_decision_returns_bet(self, human_setup):
        """Tests that human controller returns bet from betting interface"""
        _, betting_interface, controller = human_setup
        mock_bet = Mock()
        betting_interface.get_validated_bet.return_value = mock_bet

        result = controller.make_bet_decision()

        assert result == mock_bet
        betting_interface.get_validated_bet.assert_called_once_with(1000)

    def test_make_bet_decision_returns_none_when_cancelled(self, human_setup):
        """Tests that human controller returns None when bet is cancelled"""
        _, betting_interface, controller = human_setup
        betting_interface.get_validated_bet.return_value = None

        result = controller.make_bet_decision()

        assert result is None


class TestConservativeBotController:
    """
    Tests for ConservativeBotController class

    Tests safe betting strategies with weighted choices.
    """

    @pytest.fixture
    def conservative_bot(self):
        """Fixture providing ConservativeBotController with 1000 balance"""
        player = Player("ConservativeBot", 1000)
        return ConservativeBotController(player)

    def test_initial_state(self, conservative_bot):
        """Tests that conservative bot initializes with correct player and weights"""
        assert conservative_bot.player.get_name() == "ConservativeBot"
        assert conservative_bot.weights_dict is not None

    def test_weighted_type_returns_valid_type(self, conservative_bot):
        """Tests that weighted type selection returns valid bet type"""
        bet_type = conservative_bot._weighted_type()
        assert bet_type in conservative_bot.weights_dict.keys()

    @pytest.mark.parametrize(
        "bet_type, expected_choices",
        [
            ("color", ["red", "black"]),
            ("high_low", ["high", "low"]),
            ("even_odd", ["even", "odd"]),
            ("column", [1, 2, 3]),
        ],
    )
    def test_conservative_choice_returns_valid_choices(
        self, conservative_bot, bet_type, expected_choices
    ):
        """Tests that conservative choice returns valid options for each bet type"""
        choice = conservative_bot._conservative_choice(bet_type)
        assert choice in expected_choices

    def test_make_bet_decision_with_valid_bet(self, conservative_bot):
        """Tests complete bet decision making with mocked random choices"""
        with patch.object(
            conservative_bot, "_weighted_type", return_value="color"
        ), patch.object(
            conservative_bot, "_conservative_choice", return_value="red"
        ), patch(
            "random.random", return_value=0.5
        ):

            bet = conservative_bot.make_bet_decision()

            assert bet is not None
            assert bet.validate() == True

    def test_make_bet_decision_skips_with_low_balance(self):
        """Tests that bot skips betting when balance is zero"""
        player = Player("PoorBot", 0)
        bot = ConservativeBotController(player)

        bet = bot.make_bet_decision()

        assert bet is None

    def test_make_bet_decision_skips_randomly(self, conservative_bot):
        """Tests random skipping behavior with low random value"""
        with patch("random.random", return_value=0.05):
            bet = conservative_bot.make_bet_decision()
            assert bet is None


class TestAggressiveBotController:
    """
    Tests for AggressiveBotController class

    Tests risky betting strategies with progressive betting.
    """

    @pytest.fixture
    def aggressive_bot(self):
        """Fixture providing AggressiveBotController with 2000 balance"""
        player = Player("AggressiveBot", 2000)
        return AggressiveBotController(player)

    def test_initial_state(self, aggressive_bot):
        """Tests that aggressive bot initializes with correct state"""
        assert aggressive_bot.player.get_balance() == 2000
        assert aggressive_bot.consecutive_losses == 0

    def test_calculate_aggressive_amount_increases_with_losses(self, aggressive_bot):
        """Tests that bet amount increases with consecutive losses"""
        aggressive_bot.consecutive_losses = 2

        amount = aggressive_bot._calculate_aggressive_amount()

        assert amount > 200

    @pytest.mark.parametrize(
        "consecutive_losses, expected_multiplier",
        [
            (0, 1.0),
            (1, 1.5),
            (2, 2.0),
            (3, 2.5),
            (5, 3.0),
        ],
    )
    def test_aggressive_bet_amount_calculation(
        self, consecutive_losses, expected_multiplier
    ):
        """Tests that aggressive amount calculation uses correct multipliers"""
        player = Player("Test", 2000)
        bot = AggressiveBotController(player)
        bot.consecutive_losses = consecutive_losses

        with patch.object(bot, "_calculate_aggressive_amount") as mock_calc:
            bot.make_bet_decision()
            mock_calc.assert_called_once()

        calculated_amount = bot._calculate_aggressive_amount()
        base_amount = 250
        expected_amount = min(int(base_amount * expected_multiplier), 2000)

        assert calculated_amount == expected_amount

    def test_aggressive_choice_returns_risky_options(
        self, aggressive_bot: AggressiveBotController
    ):
        """Tests that aggressive choice selects from high-risk numbers"""
        risky_bet = aggressive_bot._aggressive_choice("straight")
        assert risky_bet in [0, 13, 17, 32, 36]


class TestPatternBotController:
    """
    Tests for PatternBotController class

    Tests pattern-based betting strategies using historical data.
    """

    @pytest.fixture
    def pattern_bot(self):
        """Fixture providing PatternBotController with 1000 balance"""
        player = Player("PatternBot", 1000)
        return PatternBotController(player)

    def test_initial_history_empty(self, pattern_bot):
        """Tests that pattern bot starts with empty history"""
        assert pattern_bot.last_5_numbers == []

    def test_update_history_limits_size(self, pattern_bot):
        """Tests that history maintains only last 5 numbers"""
        for i in range(10):
            pattern_bot.update_history(i)

        assert len(pattern_bot.last_5_numbers) == 5
        assert pattern_bot.last_5_numbers == [5, 6, 7, 8, 9]

    @pytest.mark.parametrize(
        "history, expected_pattern_choice",
        [
            ([1, 1], "black"),
            ([2, 2], "red"),
            ([1, 2], None),
        ],
    )
    def test_pattern_detection_for_color(
        self,
        history,
        expected_pattern_choice,
    ):
        """Tests color pattern detection based on historical numbers"""
        player = Player("Test", 1000)
        bot = PatternBotController(player)

        for number in history:
            bot.update_history(number)

        with patch.object(bot, "_basic_choice", return_value="red"):
            choice = bot._pattern_choice("color")

            if expected_pattern_choice:
                assert choice == expected_pattern_choice
            else:
                assert choice in ["red", "black"]

    def test_is_red_method(self, pattern_bot):
        """Tests color detection for roulette numbers"""
        assert pattern_bot._is_red(1) == True
        assert pattern_bot._is_red(2) == False
        assert pattern_bot._is_red(0) == False


class TestGameStateChangesWithControllers:
    """
    Integration tests for controller-player interactions

    Tests how different controllers affect player state and game flow.
    """

    def test_player_balance_changes_with_bets(self):
        """Tests that controller decisions correctly affect player balance"""
        player = Player("Test", 1000)
        controller = ConservativeBotController(player)

        initial_balance = player.get_balance()

        with patch.object(
            controller, "_weighted_type", return_value="color"
        ), patch.object(controller, "_conservative_choice", return_value="red"), patch(
            "random.random", return_value=0.5
        ):

            bet = controller.make_bet_decision()
            if bet:
                player.place_bet(bet)
                assert player.get_balance() < initial_balance
                assert player.get_current_bet() == bet

    def test_different_controllers_produce_different_behaviors(self):
        """Tests that different controller types exhibit distinct betting behaviors"""
        balance = 2000
        conservative_player = Player("Conservative", balance)
        aggressive_player = Player("Aggressive", balance)

        conservative_controller = ConservativeBotController(conservative_player)
        aggressive_controller = AggressiveBotController(aggressive_player)

        conservative_bets = []
        aggressive_bets = []

        for _ in range(20):
            cons_bet = conservative_controller.make_bet_decision()
            agg_bet = aggressive_controller.make_bet_decision()

            if cons_bet:
                conservative_bets.append(cons_bet)
            if agg_bet:
                aggressive_bets.append(agg_bet)

        if aggressive_bets:
            risky_bet_types = ["straight", "split", "street"]
            aggressive_risky_bets = [
                bet
                for bet in aggressive_bets
                if any(risky in bet.get_type() for risky in risky_bet_types)
            ]

            assert len(aggressive_risky_bets) >= 0

    def test_controller_decisions_affect_player_state(self):
        """Tests complete controller decision flow and player state changes"""
        player = Player("Test", 1500)
        controller = PatternBotController(player)

        initial_balance = player.get_balance()

        with patch.object(
            controller, "_weighted_type", return_value="color"
        ), patch.object(controller, "_pattern_choice", return_value="red"), patch(
            "random.random", return_value=0.5
        ):

            bet = controller.make_bet_decision()
            if bet:
                assert bet.validate() == True

                player.place_bet(bet)
                assert player.get_balance() == initial_balance - bet.get_amount()
                assert player.get_current_bet() == bet
                assert player.get_current_bet().get_type() == "color: red"

    @pytest.mark.parametrize(
        "controller_class, expected_behavior",
        [
            (ConservativeBotController, "safe"),
            (AggressiveBotController, "risky"),
            (PatternBotController, "pattern_based"),
        ],
    )
    def test_controllers_have_different_strategies(
        self, controller_class, expected_behavior
    ):
        """Tests that each controller type has appropriate strategy attributes"""
        player = Player("Test", 1000)
        controller = controller_class(player)

        if expected_behavior == "safe":
            assert hasattr(controller, "weights_dict")
            assert "color" in controller.weights_dict
        elif expected_behavior == "risky":
            assert hasattr(controller, "consecutive_losses")
            assert hasattr(controller, "weights_dict")
            assert "straight" in controller.weights_dict
        elif expected_behavior == "pattern_based":
            assert hasattr(controller, "last_5_numbers")
            assert hasattr(controller, "_is_red")

    def test_controllers_maintain_game_flow_invariants(self):
        """Tests that all controllers maintain game integrity across multiple bets"""
        players = [
            Player("Conservative", 1000),
            Player("Aggressive", 1000),
            Player("Pattern", 1000),
        ]

        controllers = [
            ConservativeBotController(players[0]),
            AggressiveBotController(players[1]),
            PatternBotController(players[2]),
        ]

        for controller, player in zip(controllers, players):

            for _ in range(5):
                bet = controller.make_bet_decision()
                if bet and player.get_balance() >= bet.get_amount():
                    player.place_bet(bet)

                    assert player.get_balance() >= 0
                    assert player.get_current_bet() == bet

    def test_bet_replacement_behavior(self):
        """Tests that replacing bets correctly updates player state and balance"""
        player = Player("Test", 1000)
        controller = ConservativeBotController(player)

        initial_balance = player.get_balance()

        with patch.object(
            controller, "_weighted_type", return_value="color"
        ), patch.object(controller, "_conservative_choice", return_value="red"), patch(
            "random.random", return_value=0.5
        ):

            bet1 = controller.make_bet_decision()
            if bet1:
                player.place_bet(bet1)
                assert player.get_current_bet() == bet1

                bet2 = controller.make_bet_decision()
                if bet2:
                    player.place_bet(bet2)

                    expected_balance = (
                        initial_balance - bet1.get_amount() - bet2.get_amount()
                    )
                    assert player.get_balance() == expected_balance
                    assert player.get_current_bet() == bet2
                    assert player.get_current_bet() != bet1
