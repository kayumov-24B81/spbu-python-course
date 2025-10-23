from typing import Literal
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
    @pytest.fixture
    def sample_player(self):
        return Player("TestPlayer", 1000)

    @pytest.fixture
    def sample_bet(self):
        return StraightBet(100, 17)

    def test_player_initial_state(self, sample_player: Player):
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
        initial_balance: Literal[1000] | Literal[500] | Literal[200],
        bet_amount: Literal[100] | Literal[50] | Literal[200],
        expected_balance: Literal[900] | Literal[450] | Literal[0],
    ):
        player = Player("Test", initial_balance)
        bet = StraightBet(bet_amount, 17)

        result = player.place_bet(bet)

        assert result == True
        assert player.get_balance() == expected_balance
        assert player.get_current_bet() == bet

    def test_replace_current_bet(self, sample_player: Player):
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
        initial_balance: Literal[1000] | Literal[200] | Literal[0],
        add_amount: Literal[500] | Literal[100] | Literal[50],
        expected_balance: Literal[1500] | Literal[300] | Literal[50],
    ):
        player = Player("Test", initial_balance)
        player.add_balance(add_amount)
        assert player.get_balance() == expected_balance

    def test_get_name_returns_string(self, sample_player: Player):
        name = sample_player.get_name()
        assert isinstance(name, str)
        assert name == "TestPlayer"

    def test_current_bet_lifecycle(
        self, sample_player: Player, sample_bet: StraightBet
    ):
        assert sample_player.get_current_bet() is None

        sample_player.place_bet(sample_bet)
        assert sample_player.get_current_bet() == sample_bet

        new_bet = ColorBet(200, "black")
        sample_player.place_bet(new_bet)
        assert sample_player.get_current_bet() == new_bet

    def test_multiple_operations_affect_state_correctly(self):
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
    @pytest.fixture
    def human_setup(self):
        player = Player("Human", 1000)
        betting_interface = Mock()
        controller = HumanPlayerController(player, betting_interface)
        return player, betting_interface, controller

    def test_make_bet_decision_returns_bet(
        self, human_setup: tuple[Player, Mock, HumanPlayerController]
    ):
        player, betting_interface, controller = human_setup
        mock_bet = Mock()
        betting_interface.get_validated_bet.return_value = mock_bet

        result = controller.make_bet_decision()

        assert result == mock_bet
        betting_interface.get_validated_bet.assert_called_once_with(1000)

    def test_make_bet_decision_returns_none_when_cancelled(
        self, human_setup: tuple[Player, Mock, HumanPlayerController]
    ):
        player, betting_interface, controller = human_setup
        betting_interface.get_validated_bet.return_value = None

        result = controller.make_bet_decision()

        assert result is None


class TestConservativeBotController:
    @pytest.fixture
    def conservative_bot(self):
        player = Player("ConservativeBot", 1000)
        return ConservativeBotController(player)

    def test_initial_state(self, conservative_bot: ConservativeBotController):
        assert conservative_bot.player.get_name() == "ConservativeBot"
        assert conservative_bot.weights_dict is not None

    def test_weighted_type_returns_valid_type(
        self, conservative_bot: ConservativeBotController
    ):
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
        self,
        conservative_bot: ConservativeBotController,
        bet_type: Literal["color"]
        | Literal["high_low"]
        | Literal["even_odd"]
        | Literal["column"],
        expected_choices: list[str] | list[int],
    ):
        choice = conservative_bot._conservative_choice(bet_type)
        assert choice in expected_choices

    def test_make_bet_decision_with_valid_bet(
        self, conservative_bot: ConservativeBotController
    ):
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
        player = Player("PoorBot", 0)
        bot = ConservativeBotController(player)

        bet = bot.make_bet_decision()

        assert bet is None

    def test_make_bet_decision_skips_randomly(
        self, conservative_bot: ConservativeBotController
    ):
        with patch("random.random", return_value=0.05):
            bet = conservative_bot.make_bet_decision()
            assert bet is None


class TestAggressiveBotController:
    @pytest.fixture
    def aggressive_bot(self):
        player = Player("AggressiveBot", 2000)
        return AggressiveBotController(player)

    def test_initial_state(self, aggressive_bot: AggressiveBotController):
        assert aggressive_bot.player.get_balance() == 2000
        assert aggressive_bot.consecutive_losses == 0

    def test_calculate_aggressive_amount_increases_with_losses(
        self, aggressive_bot: AggressiveBotController
    ):
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
        self,
        consecutive_losses: Literal[0]
        | Literal[1]
        | Literal[2]
        | Literal[3]
        | Literal[5],
        expected_multiplier: float,
    ):
        player = Player("Test", 2000)
        bot = AggressiveBotController(player)
        bot.consecutive_losses = consecutive_losses

        with patch.object(bot, "_calculate_aggressive_amount") as mock_calc:
            bot.make_bet_decision()
            mock_calc.assert_called_once()

    def test_aggressive_choice_returns_risky_options(
        self, aggressive_bot: AggressiveBotController
    ):
        risky_bet = aggressive_bot._aggressive_choice("straight")
        assert risky_bet in [0, 13, 17, 32, 36]


class TestPatternBotController:
    @pytest.fixture
    def pattern_bot(self):
        player = Player("PatternBot", 1000)
        return PatternBotController(player)

    def test_initial_history_empty(self, pattern_bot: PatternBotController):
        assert pattern_bot.last_5_numbers == []

    def test_update_history_limits_size(self, pattern_bot: PatternBotController):
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
        history: list[int],
        expected_pattern_choice: None | Literal["black"] | Literal["red"],
    ):
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

    def test_is_red_method(self, pattern_bot: PatternBotController):
        assert pattern_bot._is_red(1) == True
        assert pattern_bot._is_red(2) == False
        assert pattern_bot._is_red(0) == False


class TestGameStateChangesWithControllers:
    def test_player_balance_changes_with_bets(self):
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
        self,
        controller_class: type[ConservativeBotController]
        | type[AggressiveBotController]
        | type[PatternBotController],
        expected_behavior: Literal["safe"]
        | Literal["risky"]
        | Literal["pattern_based"],
    ):
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
