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
from typing import List


class GameCoordinator:
    def __init__(self, max_rounds=10, winning_balance=5000):
        self.betting_interface = BettingInterface()
        self.roulette = Roulette()
        self.players: List[Player] = []
        self.controllers = {}
        self.round_history = []
        self.current_round = 0
        self.max_rounds = max_rounds
        self.winning_balance = winning_balance

    def _add_player(self, player, controller):
        self.players.append(player)
        self.controllers[player] = controller

    def _check_win_condition(self):
        for player in self.players:
            if player.get_balance() >= self.winning_balance:
                return player
        return None

    def _declare_winner(self):
        print("\n=== FINAL RESULTS ===")
        players_sorted = sorted(
            self.players, key=lambda p: p.get_balance(), reverse=True
        )
        winner = players_sorted[0]
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

    def _check_game_over(self):
        active_players = [p for p in self.players if p.get_balance() > 0]
        if self.current_round >= self.max_rounds:
            print(f"\nMAXIMUM ROUNDS REACHED ({self.max_rounds})!")
            return True

        if len(active_players) == 0:
            print(f"\nALL PLAYERS ARE BROKE")
            self._declare_winner()
            return False

    def _get_human_player(self):
        for player in self.players:
            controller = self.controllers[player]
            if hasattr(controller, "betting_interface"):
                return player
        return None

    def _setup_game(self):
        print("=== STARTING ROULETTE GAME ===")
        print(f"First player to reach ${self.winning_balance} wins!")
        print(f"Or game ends after {self.max_rounds} rounds.")

        name = input("Player name: ")
        balance = 1000
        player = Player(name, balance)
        controller = HumanPlayerController(player, self.betting_interface)
        self._add_player(player, controller)

        bots_config = [
            ("Safe player", ConservativeBotController, 1500),
            ("Risky player", AggressiveBotController, 1500),
            ("Smart player", PatternBotController, 1500),
        ]

        for bot_name, controller_type, bot_balance in bots_config:
            bot = Player(bot_name, bot_balance)
            bot_controller = controller_type(bot)

            self._add_player(bot, bot_controller)

    def _play_turn(self):
        self.current_round += 1
        print(f"=== ROUND {self.current_round}/{self.max_rounds}===")

        if self._check_game_over():
            return False

        for player in self.players:
            controller = self.controllers[player]
            if hasattr(controller, "update_history") and self.round_history:
                controller.update_history(self.round_history[-1])

        print("\n--- PLACE YOUR BETS ---")

        active_players = 0
        for player in self.players:
            if player.get_balance() > 0:
                controller = self.controllers[player]
                bet: Bet = controller.make_bet_decision()
                if bet:
                    if player.place_bet(bet):
                        active_players += 1
                        print(
                            f"{player.get_name()} bets ${bet.get_amount()} on {bet.get_type()}"
                        )
                    else:
                        print(f"{player.get_name()} skips this round.")

        if active_players == 0:
            print("No one placed bets this round. Spinning anyway...")
            winning_number, winning_color = self.roulette.spin()
            self.round_history.append(winning_number)
            if len(self.round_history) > 10:
                self.round_history.pop(0)
            print(f"Winning number: {winning_number}, {winning_color}")
            print("No winners this round.")
            return not self._check_game_over()

        winning_number, winning_color = self.roulette.spin()
        print(f"Winning number: {winning_number}, {winning_color}")

        print("\n--- ROUND RESULTS ---")
        has_winners = False
        for player in self.players:
            player_won = False
            winnings = 0
            for bet in player.get_current_bets():
                if bet.is_winning(winning_number):
                    payout = (bet.get_payout() + 1) * bet.get_amount()
                    winnings += payout
                    player_won = True
                    has_winners = True

            if player_won:
                player.add_balance(winnings)
                print(f"{player.get_name()} won ${winnings}!")

        controller = self.controllers[player]
        if hasattr(controller, "update_stats"):
            won = any(bet.is_winning(winning_number) for bet in player.current_bets)
            controller.update_stats(won)

        if not has_winners:
            print("No winners this round!")

        print(f"\n--- PLAYERS BALANCES (Goal: ${self.winning_balance})")
        for player in self.players:
            balance = player.get_balance()
            if balance == 0:
                status = "LOST TO CASINO"
            else:
                status = balance
            print(f"{player.get_name()}: {status}")

        winner: Player = self._check_win_condition()
        if winner:
            print(f"\n{winner.get_name()} reached ${self.winning_balance}!")
            self._declare_winner()
            return False

        human_player: Player = self._get_human_player()

        if human_player and human_player.get_balance() > 0:
            while True:
                next_round = (
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

    def game_loop(self):
        self._setup_game()
        while self._play_turn():
            pass
        print("\n Thanks for playing!")


Game = GameCoordinator(5, 5000)
Game.game_loop()
