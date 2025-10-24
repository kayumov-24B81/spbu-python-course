import pytest
from unittest.mock import patch
from project.ha_4.game_coordinator import GameCoordinator
from project.ha_4.player import Player
from project.ha_4.controllers import (
    HumanPlayerController,
    ConservativeBotController,
    AggressiveBotController,
    PatternBotController,
)
from project.ha_4.bets import StraightBet, ColorBet


class TestGameCoordinator:
    """
    Unit tests for GameCoordinator class

    Tests initialization, player management, and win condition checking.
    """

    @pytest.fixture
    def game_coordinator(self):
        """Fixture providing a GameCoordinator instance with max_rounds=5, winning_balance=2000"""
        return GameCoordinator(max_rounds=5, winning_balance=2000)

    @pytest.fixture
    def sample_player(self):
        """Fixture providing a sample Player instance with 1000 balance"""
        return Player("TestPlayer", 1000)

    def test_initialization(self, game_coordinator):
        """Tests that GameCoordinator initializes with correct default values"""
        assert game_coordinator.current_round == 0
        assert game_coordinator.max_rounds == 5
        assert game_coordinator.winning_balance == 2000
        assert game_coordinator.players == []
        assert game_coordinator.controllers == {}
        assert game_coordinator.round_history == []
        assert game_coordinator.betting_interface is not None
        assert game_coordinator.roulette is not None

    def test_add_player(self, game_coordinator, sample_player):
        """Tests adding a player with controller to the game"""
        controller = ConservativeBotController(sample_player)

        game_coordinator._add_player(sample_player, controller)

        assert len(game_coordinator.players) == 1
        assert sample_player in game_coordinator.players
        assert game_coordinator.controllers[sample_player] == controller

    @pytest.mark.parametrize(
        "balances, expected_winner_index",
        [
            ([1500, 2500, 1800], 1),
            ([3000, 1500, 2000], 0),
            ([1500, 1800, 1900], None),
        ],
    )
    def test_check_win_condition(
        self, game_coordinator, balances, expected_winner_index
    ):
        """Tests win condition checking with various player balances"""
        players = []
        for i, balance in enumerate(balances):
            player = Player(f"Player{i}", balance)
            controller = ConservativeBotController(player)
            game_coordinator._add_player(player, controller)
            players.append(player)

        winner = game_coordinator._check_win_condition()

        if expected_winner_index is not None:
            expected_winner_player = players[expected_winner_index]
            assert winner == expected_winner_player
        else:
            assert winner is None

    def test_get_human_player(self, game_coordinator):
        """Tests finding human player among mixed player types"""
        bot1 = Player("Bot1", 1000)
        game_coordinator._add_player(bot1, ConservativeBotController(bot1))

        human_player = Player("Human", 1000)
        human_controller = HumanPlayerController(
            human_player, game_coordinator.betting_interface
        )
        game_coordinator._add_player(human_player, human_controller)

        bot2 = Player("Bot2", 1000)
        game_coordinator._add_player(bot2, ConservativeBotController(bot2))

        found_human = game_coordinator._get_human_player()
        assert found_human == human_player

    def test_get_human_player_no_human(self, game_coordinator):
        """Tests human player search when no human players exist"""
        bot1 = Player("Bot1", 1000)
        game_coordinator._add_player(bot1, ConservativeBotController(bot1))

        bot2 = Player("Bot2", 1000)
        game_coordinator._add_player(bot2, ConservativeBotController(bot2))

        found_human = game_coordinator._get_human_player()
        assert found_human is None

    @pytest.mark.parametrize(
        "current_round, max_rounds, player_balances, expected_result",
        [
            (6, 5, [1000, 1500], True),
            (3, 5, [0, 0], True),
            (2, 5, [1000, 0], True),
            (2, 5, [1000, 500], False),
        ],
    )
    def test_check_game_over(
        self, current_round, max_rounds, player_balances, expected_result
    ):
        """Tests game over conditions including round limit and bankrupt players"""
        game = GameCoordinator(max_rounds=max_rounds, winning_balance=2000)
        game.current_round = current_round

        for i, balance in enumerate(player_balances):
            player = Player(f"Player{i}", balance)
            game._add_player(player, ConservativeBotController(player))

        with patch("builtins.print"):
            result = game._check_game_over()
            assert result == expected_result

    def test_setup_game_creates_players(self, game_coordinator):
        """Tests game setup creates correct number of players with proper controllers"""
        with patch("builtins.input", return_value="TestHuman"), patch("builtins.print"):
            game_coordinator._setup_game()

            assert len(game_coordinator.players) == 4

            human_found = any(
                hasattr(game_coordinator.controllers[p], "betting_interface")
                for p in game_coordinator.players
            )
            assert human_found == True

            bot_names = ["Safe player", "Risky player", "Smart player"]
            created_bot_names = [
                p.get_name()
                for p in game_coordinator.players
                if p.get_name() != "TestHuman"
            ]
            assert all(bot_name in created_bot_names for bot_name in bot_names)


class TestGameCoordinatorRoundFlow:
    """
    Integration tests for game round flow and betting mechanics

    Tests complete turn execution with various betting scenarios.
    """

    @pytest.fixture
    def game_with_players(self):
        """Fixture providing game with mixed player types (human, conservative, aggressive)"""
        game = GameCoordinator(max_rounds=10, winning_balance=3000)

        human_player = Player("Human", 1000)
        bot1 = Player("Conservative", 1000)
        bot2 = Player("Aggressive", 1000)

        human_controller = HumanPlayerController(human_player, game.betting_interface)
        bot1_controller = ConservativeBotController(bot1)
        bot2_controller = AggressiveBotController(bot2)

        game._add_player(human_player, human_controller)
        game._add_player(bot1, bot1_controller)
        game._add_player(bot2, bot2_controller)

        return game, human_player, bot1, bot2

    def test_play_turn_increments_round(self, game_with_players):
        """Tests that playing a turn increments the round counter"""
        game, _, _, _ = game_with_players
        initial_round = game.current_round

        with patch.object(game, "_check_game_over", return_value=False), patch.object(
            game.betting_interface, "get_validated_bet", return_value=None
        ), patch.object(
            ConservativeBotController, "make_bet_decision", return_value=None
        ), patch.object(
            AggressiveBotController, "make_bet_decision", return_value=None
        ), patch.object(
            game.roulette, "spin", return_value=(17, "red")
        ), patch.object(
            game, "_check_win_condition", return_value=None
        ), patch(
            "builtins.input", return_value="yes"
        ), patch(
            "builtins.print"
        ):

            result = game._play_turn()

            assert game.current_round == initial_round + 1
            assert result == True

    def test_play_turn_with_bets_and_winners(self, game_with_players):
        """Tests complete betting round with win/loss calculations"""
        game, human_player, bot1, bot2 = game_with_players

        human_bet = StraightBet(100, 16)  # Payout 35:1
        bot1_bet = ColorBet(50, "red")  # Payout 1:1
        bot2_bet = StraightBet(200, 18)  # Bet on the other number (should lose)

        with patch.object(game, "_check_game_over", return_value=False), patch.object(
            game.betting_interface, "get_validated_bet", return_value=human_bet
        ), patch.object(
            ConservativeBotController, "make_bet_decision", return_value=bot1_bet
        ), patch.object(
            AggressiveBotController, "make_bet_decision", return_value=bot2_bet
        ), patch.object(
            game.roulette, "spin", return_value=(16, "red")
        ), patch.object(
            game, "_check_win_condition", return_value=None
        ), patch(
            "builtins.input", return_value="yes"
        ), patch(
            "builtins.print"
        ):

            result = game._play_turn()

            assert human_player.get_current_bet() == human_bet
            assert bot1.get_current_bet() == bot1_bet
            assert bot2.get_current_bet() == bot2_bet

            # Check balances (initial = 1000):
            # human: 1000 - 100 + (100 * 36) = 1000 - 100 + 3600 = 4500
            # bot1: 1000 - 50 + (50 * 2) = 1000 - 50 + 100 = 1050 (red won)
            # bot2: 1000 - 200 + 0 = 800 (18 didn't win)
            assert human_player.get_balance() == 4500
            assert bot1.get_balance() == 1050
            assert bot2.get_balance() == 800

            assert result == True

    def test_play_turn_game_over_condition(self, game_with_players):
        """Tests early termination when game over condition is met"""
        game, _, _, _ = game_with_players

        with patch.object(game, "_check_game_over", return_value=True):
            result = game._play_turn()
            assert result == False

    def test_play_turn_win_condition_met(self, game_with_players):
        """Tests game termination when a player reaches winning balance"""
        game, human_player, bot1, bot2 = game_with_players

        human_bet = StraightBet(100, 17)
        bot1_bet = ColorBet(50, "red")

        with patch.object(game, "_check_game_over", return_value=False), patch.object(
            game.betting_interface, "get_validated_bet", return_value=human_bet
        ), patch.object(
            ConservativeBotController, "make_bet_decision", return_value=bot1_bet
        ), patch.object(
            AggressiveBotController, "make_bet_decision", return_value=None
        ), patch.object(
            game.roulette, "spin", return_value=(17, "red")
        ), patch.object(
            game, "_check_win_condition", return_value=human_player
        ), patch.object(
            game, "_declare_winner"
        ), patch(
            "builtins.input"
        ), patch(
            "builtins.print"
        ):

            result = game._play_turn()
            assert result == False

    def test_play_turn_no_bets_placed(self, game_with_players):
        """Tests turn execution when no players place bets"""
        game, _, _, _ = game_with_players

        with patch.object(game, "_check_game_over", return_value=False), patch.object(
            game.betting_interface, "get_validated_bet", return_value=None
        ), patch.object(
            ConservativeBotController, "make_bet_decision", return_value=None
        ), patch.object(
            AggressiveBotController, "make_bet_decision", return_value=None
        ), patch.object(
            game.roulette, "spin", return_value=(17, "red")
        ), patch.object(
            game, "_check_win_condition", return_value=None
        ), patch(
            "builtins.input", return_value="yes"
        ), patch(
            "builtins.print"
        ):

            result = game._play_turn()
            assert result == True


class TestGameCoordinatorIntegration:
    """
    Integration tests for complete game flow and state management

    Tests multi-round gameplay and winner declaration.
    """

    def test_complete_game_flow_with_mocks(self):
        """Tests complete game loop with mocked dependencies"""
        game = GameCoordinator(max_rounds=3, winning_balance=1500)

        with patch.object(game, "_setup_game") as mock_setup, patch.object(
            game, "_play_turn", side_effect=[True, True, False]
        ) as mock_play_turn, patch("builtins.print"):

            game.game_loop()

            mock_setup.assert_called_once()
            assert mock_play_turn.call_count == 3

    def test_game_state_changes_over_rounds(self):
        """Tests that game state updates correctly across multiple rounds"""
        game = GameCoordinator(max_rounds=3, winning_balance=2000)

        player1 = Player("Player1", 1000)
        player2 = Player("Player2", 1000)

        game._add_player(player1, ConservativeBotController(player1))
        game._add_player(player2, AggressiveBotController(player2))

        initial_round = game.current_round
        initial_history_len = len(game.round_history)

        with patch.object(game, "_check_game_over", return_value=False), patch.object(
            game.betting_interface, "get_validated_bet", return_value=None
        ), patch.object(
            ConservativeBotController, "make_bet_decision", return_value=None
        ), patch.object(
            AggressiveBotController, "make_bet_decision", return_value=None
        ), patch.object(
            game.roulette, "spin", side_effect=[(17, "red"), (5, "black"), (0, "green")]
        ), patch.object(
            game, "_check_win_condition", return_value=None
        ), patch(
            "builtins.input", return_value="yes"
        ):

            result1 = game._play_turn()
            assert result1 == True
            assert game.current_round == initial_round + 1
            assert len(game.round_history) == initial_history_len + 1
            assert game.round_history[-1] == 17

            result2 = game._play_turn()
            assert result2 == True
            assert game.current_round == initial_round + 2
            assert len(game.round_history) == initial_history_len + 2
            assert game.round_history[-1] == 5

    def test_winner_declaration(self, capsys):
        """Tests that winner declaration displays correct information"""
        game = GameCoordinator(max_rounds=5, winning_balance=2000)

        players = [
            Player("Loser1", 500),
            Player("Winner", 2500),
            Player("Loser2", 800),
        ]

        for player in players:
            game._add_player(player, ConservativeBotController(player))

        game._declare_winner()
        captured = capsys.readouterr()
        output = captured.out

        assert "Winner" in output
        assert "2500" in output
        assert "FINAL RESULTS" in output

    def test_pattern_bot_history_update(self):
        """Tests that PatternBotController correctly updates its number history"""
        game = GameCoordinator(max_rounds=5, winning_balance=2000)

        pattern_player = Player("PatternBot", 1000)
        pattern_controller = PatternBotController(pattern_player)

        bet = ColorBet(50, "red")

        game._add_player(pattern_player, pattern_controller)

        assert len(pattern_controller.last_5_numbers) == 0

        with patch.object(game, "_check_game_over", return_value=False), patch.object(
            game.betting_interface, "get_validated_bet", return_value=None
        ), patch.object(
            PatternBotController, "make_bet_decision", return_value=bet
        ), patch.object(
            game.roulette, "spin", return_value=(17, "red")
        ), patch.object(
            game, "_check_win_condition", return_value=None
        ), patch(
            "builtins.input", return_value="yes"
        ):

            result = game._play_turn()
            assert result == True

            assert len(pattern_controller.last_5_numbers) == 1
            assert pattern_controller.last_5_numbers[0] == 17


class TestFullGameSimulation:
    """
    End-to-end tests for complete game simulations

    Tests game invariants and complete gameplay scenarios.
    """

    def test_minimal_game_simulation(self):
        """Tests minimal game simulation with limited rounds"""
        game = GameCoordinator(max_rounds=2, winning_balance=1000)

        player = Player("TestPlayer", 800)
        game._add_player(player, ConservativeBotController(player))

        with patch.object(game, "_setup_game"), patch.object(
            game, "_play_turn", side_effect=[True, False]
        ), patch("builtins.print"):

            game.game_loop()

            assert game.current_round <= 2

    def test_game_coordinator_maintains_invariants(self):
        """Tests that game invariants are maintained throughout gameplay"""
        game = GameCoordinator(max_rounds=10, winning_balance=1500)

        players = [
            Player("Player1", 1000),
            Player("Player2", 1000),
            Player("Player3", 1000),
        ]

        for player in players:
            game._add_player(player, ConservativeBotController(player))

        assert game.current_round >= 0
        assert len(game.players) == 3
        assert len(game.controllers) == 3
        assert all(player in game.controllers for player in game.players)

        with patch.object(game, "_check_game_over", return_value=False), patch.object(
            game.betting_interface, "get_validated_bet", return_value=None
        ), patch.object(
            ConservativeBotController, "make_bet_decision", return_value=None
        ), patch.object(
            game.roulette, "spin", return_value=(10, "black")
        ), patch.object(
            game, "_check_win_condition", return_value=None
        ), patch(
            "builtins.input", return_value="yes"
        ):

            game._play_turn()

            assert game.current_round == 1
            assert len(game.players) == 3
            assert len(game.round_history) == 1
            assert game.round_history[0] == 10
