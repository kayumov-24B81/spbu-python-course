import pytest
from unittest.mock import patch, MagicMock
from project.ha_4.betting_interface import BettingInterface
from project.ha_4.bets import StraightBet, SplitBet, ColorBet


class TestBettingInterface:
    @pytest.fixture
    def betting_interface(self):
        return BettingInterface()

    def test_initialization(self, betting_interface):
        assert betting_interface.bet_factory is not None
        assert hasattr(betting_interface, "BET_CONFIG")
        assert "straight" in betting_interface.BET_CONFIG
        assert "color" in betting_interface.BET_CONFIG

    def test_show_betting_options_displays_all_types(self, betting_interface, capsys):
        betting_interface._show_betting_options()
        captured = capsys.readouterr()
        output = captured.out

        for bet_type in betting_interface.BET_CONFIG:
            assert bet_type in output
            assert betting_interface.BET_CONFIG[bet_type]["description"] in output

    @pytest.mark.parametrize(
        "user_input, expected_result",
        [
            ("straight", "straight"),
            ("split", "split"),
            ("color", "color"),
            ("quit", None),
        ],
    )
    def test_receive_bet_type_valid_input(
        self, betting_interface, user_input, expected_result
    ):
        with patch("builtins.input", return_value=user_input):
            result = betting_interface._receive_bet_type()
            assert result == expected_result

    @pytest.mark.parametrize(
        "user_inputs, expected_result",
        [
            (["invalid", "straight"], "straight"),
            (["wrong", "quit"], None),
            (["", "split"], "split"),
        ],
    )
    def test_receive_bet_type_with_retry(
        self, betting_interface, user_inputs, expected_result
    ):
        with patch("builtins.input", side_effect=user_inputs):
            result = betting_interface._receive_bet_type()
            assert result == expected_result

    @pytest.mark.parametrize(
        "bet_type, user_input, expected_result",
        [
            ("straight", "17", 17),
            ("color", "red", "red"),
            ("split", "1 2", [1, 2]),
            ("street", "4", 4),
            ("corner", "1 2 4 5", [1, 2, 4, 5]),
        ],
    )
    def test_receive_bet_choice_valid_input(
        self, betting_interface, bet_type, user_input, expected_result
    ):
        with patch("builtins.input", return_value=user_input):
            result = betting_interface._receive_bet_choice(bet_type)
            assert result == expected_result

    def test_receive_bet_choice_back_command(self, betting_interface):
        with patch("builtins.input", return_value="back"):
            result = betting_interface._receive_bet_choice("straight")
            assert result is None

    @pytest.mark.parametrize(
        "user_input, expected_result",
        [
            ("100", 100),
            ("50", 50),
            ("0", None),
        ],
    )
    def test_receive_bet_amount_valid_input(
        self, betting_interface, user_input, expected_result
    ):
        with patch("builtins.input", return_value=user_input):
            result = betting_interface._receive_bet_amount(1000)
            assert result == expected_result

    @pytest.mark.parametrize(
        "user_inputs, max_bet, expected_result",
        [
            (["-100", "100"], 1000, 100),
            (["1500", "100"], 1000, 100),
            (["invalid", "100"], 1000, 100),
        ],
    )
    def test_receive_bet_amount_with_retry(
        self, betting_interface, user_inputs, max_bet, expected_result
    ):
        with patch("builtins.input", side_effect=user_inputs):
            result = betting_interface._receive_bet_amount(max_bet)
            assert result == expected_result

    def test_get_validated_bet_successful_flow(self, betting_interface):
        with patch.object(betting_interface, "_show_betting_options"), patch.object(
            betting_interface, "_receive_bet_type", return_value="straight"
        ), patch.object(
            betting_interface, "_receive_bet_amount", return_value=100
        ), patch.object(
            betting_interface, "_receive_bet_choice", return_value=17
        ):

            bet = betting_interface.get_validated_bet(1000)

            assert bet is not None
            assert isinstance(bet, StraightBet)
            assert bet.get_amount() == 100
            assert bet.number == 17
            assert bet.validate() == True

    def test_get_validated_bet_cancel_at_type_selection(self, betting_interface):
        with patch.object(betting_interface, "_show_betting_options"), patch.object(
            betting_interface, "_receive_bet_type", return_value=None
        ):

            bet = betting_interface.get_validated_bet(1000)
            assert bet is None

    def test_get_validated_bet_cancel_at_amount_selection(self, betting_interface):
        with patch.object(betting_interface, "_show_betting_options"), patch.object(
            betting_interface, "_receive_bet_type", return_value="straight"
        ), patch.object(betting_interface, "_receive_bet_amount", return_value=None):

            bet = betting_interface.get_validated_bet(1000)
            assert bet is None

    def test_get_validated_bet_cancel_at_choice_selection(self, betting_interface):
        with patch.object(betting_interface, "_show_betting_options"), patch.object(
            betting_interface, "_receive_bet_type", return_value="straight"
        ), patch.object(
            betting_interface, "_receive_bet_amount", return_value=100
        ), patch.object(
            betting_interface, "_receive_bet_choice", return_value=None
        ):

            bet = betting_interface.get_validated_bet(1000)
            assert bet is None

    def test_get_validated_bet_validation_failure(self, betting_interface):
        with patch.object(betting_interface, "_show_betting_options"), patch.object(
            betting_interface, "_receive_bet_type", return_value="straight"
        ), patch.object(
            betting_interface, "_receive_bet_amount", return_value=100
        ), patch.object(
            betting_interface, "_receive_bet_choice", side_effect=[37, 17]
        ):

            bet = betting_interface.get_validated_bet(1000)

            assert bet is not None
            assert bet.number == 17
            assert bet.validate() == True

    def test_get_validated_bet_too_many_validation_attempts(self, betting_interface):
        with patch.object(betting_interface, "_show_betting_options"), patch.object(
            betting_interface, "_receive_bet_type", return_value="straight"
        ), patch.object(
            betting_interface, "_receive_bet_amount", return_value=100
        ), patch.object(
            betting_interface, "_receive_bet_choice", return_value=37
        ):
            bet = betting_interface.get_validated_bet(1000)

            assert bet is None

    @pytest.mark.parametrize(
        "max_bet, user_inputs, expected_results",
        [
            (500, ["600", "400"], 400),
            (1000, ["-100", "200"], 200),
        ],
    )
    def test_bet_amount_validation_scenarios(
        self, betting_interface, max_bet, user_inputs, expected_results
    ):
        with patch("builtins.input", side_effect=user_inputs):
            result = betting_interface._receive_bet_amount(max_bet)
            assert result == expected_results

    def test_bet_config_completeness(self, betting_interface):
        required_keys = ["description", "message", "converter"]

        for bet_type, config in betting_interface.BET_CONFIG.items():
            for key in required_keys:
                assert key in config, f"Missing {key} in {bet_type} config"
            assert callable(
                config["converter"]
            ), f"Converter for {bet_type} should be callable"

    def test_converter_functions_handle_errors(self, betting_interface):
        straight_converter = betting_interface.BET_CONFIG["straight"]["converter"]
        with pytest.raises(ValueError):
            straight_converter("not_a_number")

        split_converter = betting_interface.BET_CONFIG["split"]["converter"]
        result = split_converter("1")
        assert len(result) == 1


class TestBettingInterfaceIntegration:
    def test_complete_happy_path_flow(self):
        betting_interface = BettingInterface()

        user_inputs = [
            "straight",
            "100",
            "17",
        ]

        with patch("builtins.input", side_effect=user_inputs):
            bet = betting_interface.get_validated_bet(1000)

        assert bet is not None
        assert isinstance(bet, StraightBet)
        assert bet.get_amount() == 100
        assert bet.number == 17
        assert bet.validate() == True

    def test_interface_maintains_state_consistency(self):
        betting_interface = BettingInterface()

        for i in range(3):
            with patch.object(betting_interface, "_show_betting_options"), patch.object(
                betting_interface, "_receive_bet_type", return_value="color"
            ), patch.object(
                betting_interface, "_receive_bet_amount", return_value=50 + i * 10
            ), patch.object(
                betting_interface, "_receive_bet_choice", return_value="red"
            ):

                bet = betting_interface.get_validated_bet(1000)
                assert bet is not None
                assert bet.validate() == True
