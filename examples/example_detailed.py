"""
Detailed game session with mechanical state output each round
"""
import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project.ha_4.game_coordinator import GameCoordinator


def run_detailed_example():
    print("GAME STATE TRACKING")
    print("=" * 50)

    random.seed(12)

    game = GameCoordinator(max_rounds=4, winning_balance=2000)

    previous_state = None
    game_ended = False

    original_play_turn = game._play_turn

    def logged_play_turn():
        nonlocal game_ended
        nonlocal previous_state

        if game._check_game_over():
            print(f"\nGAME ENDED AT ROUND {game.current_round}")
            return False

        current_state = {
            "round": game.current_round,
            "players": {},
            "history": game.round_history.copy(),
            "winning_number": None,
        }

        for player in game.players:
            current_state["players"][player.get_name()] = {
                "balance": player.get_balance(),
                "current_bet": player.get_current_bet(),
                "bet_type": player.get_current_bet().get_type()
                if player.get_current_bet()
                else None,
                "is_active": player.get_balance() > 0,
            }

        result = original_play_turn()

        if not result:
            game_ended = True

        if game_ended:
            return result

        if game.round_history:
            current_state["winning_number"] = game.round_history[-1]

        print(f"\nSTATE - ROUND {game.current_round}:")

        if previous_state:
            print("PARAMETER CHANGES:")

            if current_state["history"] != previous_state["history"]:
                print(
                    f"round_history: {previous_state['history']} -> {current_state['history']}"
                )

            for player_name in current_state["players"]:
                current_player = current_state["players"][player_name]
                previous_player = previous_state["players"][player_name]

                changes = []

                if current_player["balance"] != previous_player["balance"]:
                    changes.append(
                        f"balance: {previous_player['balance']} -> {current_player['balance']}"
                    )

                if current_player["bet_type"] != previous_player["bet_type"]:
                    changes.append(
                        f"bet: {previous_player['bet_type'] or 'None'} -> {current_player['bet_type'] or 'None'}"
                    )

                if current_player["is_active"] != previous_player["is_active"]:
                    old_status = (
                        "active" if previous_player["is_active"] else "inactive"
                    )
                    new_status = "active" if current_player["is_active"] else "inactive"
                    changes.append(f"status: {old_status} -> {new_status}")

                if changes:
                    print(f"{player_name}: {', '.join(changes)}")
                else:
                    print(f"{player_name}: no changes")
        else:
            print("INITIAL STATE:")
            for player_name, player_state in current_state["players"].items():
                print(
                    f"{player_name}: balance={player_state['balance']}, bet={player_state['bet_type'] or 'None'}, status={'active' if player_state['is_active'] else 'inactive'}"
                )
            print(f"round_history: {current_state['history']}")

        previous_state = current_state

        return result

    game._play_turn = logged_play_turn

    game.game_loop()


if __name__ == "__main__":
    run_detailed_example()
