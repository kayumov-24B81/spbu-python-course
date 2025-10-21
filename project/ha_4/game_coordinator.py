from bets import *
from controllers import (
    BettingInterface,
    ConservativeBotController,
    PatternBotController,
    HumanPlayerController,
    AggressiveBotController,
    Player,
)
from roulette import Roulette
from typing import List, Optional, Dict, Type, Any, Tuple


class GameCoordinator:
    """
    Main game coordinator that manages the roulette game flow.

    Handles player setup, round management, betting, and win conditions.
    Coordinates between players, controllers, and the roulette wheel.
    """

    def __init__(self, max_rounds: int = 10, winning_balance: int = 5000) -> None:
        """
        Initialize the game coordinator.

        Args:
            max_rounds: Maximum number of rounds before game ends
            winning_balance: Target balance for automatic victory
        """
        self.betting_interface = BettingInterface()
        self.roulette = Roulette()
        self.players: List[Player] = []
        self.controllers: Dict[Player, Any] = {}
        self.round_history: List[int] = []
        self.current_round: int = 0
        self.max_rounds = max_rounds
        self.winning_balance = winning_balance

    def _add_player(self, player: Player, controller: Any) -> None:
        """
        Add a player and their controller to the game.

        Args:
            player: The player instance
            controller: The controller that manages player's decisions
        """
        self.players.append(player)
        self.controllers[player] = controller

    def _check_win_condition(self) -> Optional[Player]:
        """
        Check if any player has reached the winning balance.

        Returns:
            Player who reached winning balance, or None if no winner yet
        """
        for player in self.players:
            if player.get_balance() >= self.winning_balance:
                return player
        return None

    def _declare_winner(self) -> None:
        """Display final results and declare the winner."""
        print("\n=== FINAL RESULTS ===")
        players_sorted: List[Player] = sorted(
            self.players, key=lambda p: p.get_balance(), reverse=True
        )
        winner: Player = players_sorted[0]
        if winner.get_balance() > self.winning_balance:
            print(f"VICTORY: {winner.get_name()} reached ${winner.get_balance()}")
        else:
            print(
                f"WINNER (by highest balance): {winner.get_name()} with ${winner.get_balance()}"
            )

        print(f"\nTotal rounds played: {self.current_round}")
        print("\nFinal standings:")
        for i, player in enumerate(players_sorted, 1):
            print(f"{i}.: {player.get_name()}")

    def _check_game_over(self) -> bool:
        """
        Check if game should end due to round limit or all players being broke.

        Returns:
            True if game should end, False otherwise
        """
        active_players: List[Player] = [p for p in self.players if p.get_balance() > 0]
        if self.current_round >= self.max_rounds:
            print(f"\nMAXIMUM ROUNDS REACHED ({self.max_rounds})!")
            return True

        if len(active_players) == 0:
            print(f"\nALL PLAYERS ARE BROKE")
            self._declare_winner()
            return False

    def _get_human_player(self) -> Optional[Player]:
        """
        Find the human player among all players.

        Returns:
            Human player instance, or None if not found
        """
        for player in self.players:
            controller: Any = self.controllers[player]
            if hasattr(controller, "betting_interface"):
                return player
        return None

    def _setup_game(self) -> None:
        """
        Set up the game with human player and AI bots.

        Creates one human player and three AI bots with different strategies.
        """
        print("=== STARTING ROULETTE GAME ===")
        print(f"First player to reach ${self.winning_balance} wins!")
        print(f"Or game ends after {self.max_rounds} rounds.")

        name: str = input("Player name: ")
        balance: int = 1000
        player: Player = Player(name, balance)
        controller: HumanPlayerController = HumanPlayerController(
            player, self.betting_interface
        )
        self._add_player(player, controller)

        bots_config: List[Tuple[str, Type, int]] = [
            ("Safe player", ConservativeBotController, 1500),
            ("Risky player", AggressiveBotController, 1500),
            ("Smart player", PatternBotController, 1500),
        ]

        for bot_name, controller_type, bot_balance in bots_config:
            bot: Player = Player(bot_name, bot_balance)
            bot_controller: Any = controller_type(bot)

            self._add_player(bot, bot_controller)

    def _play_turn(self) -> bool:
        """
        Execute one complete round of the game.

        Returns:
            True if game should continue, False if game should end

        Process:
            1. Increment round counter
            2. Check game over conditions
            3. Update bot history
            4. Collect bets from all players
            5. Spin roulette wheel
            6. Calculate winnings
            7. Display results
            8. Check win conditions
            9. Prompt for next round (if human player active)
        """
        self.current_round += 1
        print(f"=== ROUND {self.current_round}/{self.max_rounds}===")

        # Check if game should end
        if self._check_game_over():
            return False

        # Update pattern bots with previous winning numbers
        for player in self.players:
            controller: Any = self.controllers[player]
            if hasattr(controller, "update_history") and self.round_history:
                controller.update_history(self.round_history[-1])

        print("\n--- PLACE YOUR BETS ---")

        # Collect bets from all players
        active_players: int = 0
        for player in self.players:
            if player.get_balance() > 0:
                controller: Any = self.controllers[player]
                bet: Bet = controller.make_bet_decision()
                if bet:
                    if player.place_bet(bet):
                        active_players += 1
                        print(
                            f"{player.get_name()} bets ${bet.get_amount()} on {bet.get_type()}"
                        )
                    else:
                        print(f"{player.get_name()} skips this round.")

        # Spin the wheel even if no bets were placed
        if active_players == 0:
            print("No one placed bets this round. Spinning anyway...")
            winning_number, winning_color = self.roulette.spin()
            self.round_history.append(winning_number)
            if len(self.round_history) > 10:
                self.round_history.pop(0)
            print(f"Winning number: {winning_number}, {winning_color}")
            print("No winners this round.")
            return not self._check_game_over()

        # Spin roulette wheel
        winning_number: int
        winning_color: str
        winning_number, winning_color = self.roulette.spin()
        print(f"Winning number: {winning_number}, {winning_color}")

        # Calculate and distribute winnings
        print("\n--- ROUND RESULTS ---")
        has_winners: bool = False
        for player in self.players:
            player_won: bool = False
            winnings: int = 0
            bet: Bet = player.get_current_bet()
            if bet.is_winning(winning_number):
                payout: float = (bet.get_payout() + 1) * bet.get_amount()
                winnings += payout
                player_won = True
                has_winners = True

            if player_won:
                player.add_balance(winnings)
                print(f"{player.get_name()} won ${winnings}!")

        # Update bot statistics
        controller = self.controllers[player]
        if hasattr(controller, "update_stats"):
            won: bool = any(
                bet.is_winning(winning_number) for bet in player.current_bets
            )
            controller.update_stats(won)

        if not has_winners:
            print("No winners this round!")

        # Display player balances
        print(f"\n--- PLAYERS BALANCES (Goal: ${self.winning_balance})")
        for player in self.players:
            balance: float = player.get_balance()
            if balance == 0:
                status: str = "LOST TO CASINO"
            else:
                status = balance
            print(f"{player.get_name()}: {status}")

        # Check for winner
        winner: Optional[Player] = self._check_win_condition()
        if winner:
            print(f"\n{winner.get_name()} reached ${self.winning_balance}!")
            self._declare_winner()
            return False

        human_player: Optional[Player] = self._get_human_player()

        # Prompt for next round (if human player is active)
        if human_player and human_player.get_balance() > 0:
            while True:
                next_round: str = (
                    input(f"\nContinue to the nex round? (yes/no):").strip().lower()
                )
                if next_round == "yes":
                    return True
                elif next_round == "no":
                    return False
                else:
                    print("Invalid input. Please enter 'yes' or 'no'")
        else:
            print("\nContinuing to the next round...")
            return True

    def game_loop(self) -> None:
        """
        Main game loop that runs the entire game.

        Process:
            1. Set up game
            2. Play turns until game ends
            3. Display farewell message
        """
        self._setup_game()
        while self._play_turn():
            pass
        print("\n Thanks for playing!")
