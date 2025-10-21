from bets import BetFactory
from typing import Optional, Dict, Any, Callable, Union, List


class BettingInterface:
    """
    A user interface for placing various types of roulette bets.

    Provides interactive prompts for bet type selection, parameter input,
    and amount specification with validation.
    """

    BET_CONFIG = {
        "straight": {
            "description": "Bet on a single number",
            "message": "Enter one number (0-36): ",
            "converter": lambda x: int(x.strip()),
        },
        "split": {
            "description": "Bet on two adjacent numbers",
            "message": 'Enter two adjacent numbers separated by space (e.g., "1 2" or "1 4"): ',
            "converter": lambda x: [int(num.strip()) for num in x.split()[:2]],
        },
        "street": {
            "description": "Bet on three numbers in a row (e.g., 1-2-3, 4-5-6)",
            "message": "Enter the first number of the street (1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34): ",
            "converter": lambda x: int(x.strip()),
        },
        "corner": {
            "description": "Bet on four numbers forming a square (e.g., 1-2-4-5)",
            "message": 'Enter the four numbers of the corner separated by spaces (e.g., "1 2 4 5"): ',
            "converter": lambda x: [int(num.strip()) for num in x.split()[:4]],
        },
        "line": {
            "description": "Bet on six numbers from two adjacent rows (e.g., 1-2-3-4-5-6)",
            "message": "Enter the first number of the line (1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31): ",
            "converter": lambda x: int(x.strip()),
        },
        "column": {
            "description": "Bet on one of the three vertical columns",
            "message": "Enter the column number (1, 2, or 3): ",
            "converter": lambda x: int(x.strip()),
        },
        "color": {
            "description": "Bet on red or black color",
            "message": "Enter color (red or black): ",
            "converter": lambda x: x.strip().lower(),
        },
        "even_odd": {
            "description": "Bet on even or odd numbers",
            "message": "Enter choice (even or odd): ",
            "converter": lambda x: x.strip().lower(),
        },
        "high_low": {
            "description": "Bet on low (1-18) or high (19-36) numbers",
            "message": "Enter choice (low or high): ",
            "converter": lambda x: x.strip().lower(),
        },
    }

    def __init__(self) -> None:
        """Initialize the betting interface with a bet factory."""

        self.bet_factory = BetFactory()

    def _show_betting_options(self) -> None:
        """
        Display all available betting options to the user.

        Shows each bet type with its description in a formatted list.
        """
        print("AVAILABLE BETS: ")
        for name in self.BET_CONFIG:
            print(f" {name}: {self.BET_CONFIG[name]['description']}")

    def _receive_bet_type(self) -> Optional[str]:
        """
        Prompt user to select a bet type.

        Returns:
            The selected bet type as string, or None if user cancels

        Note:
            User can type 'quit' to cancel the betting process
        """
        while True:
            bet_type = (
                input("\nChoose bet type (or 'quit' to cancel): ").strip().lower()
            )

            if bet_type == "quit":
                return None
            elif bet_type in self.BET_CONFIG:
                return bet_type
            else:
                print(f"'{bet_type}' is not a valid bet type!")

    def _receive_bet_choice(
        self, bet_type: str
    ) -> Optional[Union[int, str, List[int]]]:
        """
        Prompt user for bet-specific parameters based on bet type.

        Args:
            bet_type: The type of bet being placed

        Returns:
            The converted user input for the bet parameters, or None if user goes back

        Raises:
            Handles conversion errors and prompts user again
        """
        config = self.BET_CONFIG[bet_type]

        while True:
            try:
                user_input = input(
                    config["message"] + " (or 'back' to change bet type): "
                ).strip()

                if user_input.lower() == "back":
                    return None

                bet_choice = config["converter"](user_input)
                return bet_choice
            except (ValueError, Exception) as e:
                print(f"Invalid input: {e}")

    def _receive_bet_amount(self, max_bet: float) -> Optional[float]:
        """
        Prompt user for bet amount with validation.

        Args:
            max_bet: The maximum allowed bet amount (usually player's balance)

        Returns:
            The validated bet amount, or None if user cancels

        Note:
            Validates that amount is positive and doesn't exceed max_bet
        """
        while True:
            try:
                user_input = input(
                    f"Enter bet amount (1-{max_bet}, or '0' to cancel): "
                ).strip()

                if user_input == "0":
                    return None

                bet_amount = int(user_input)

                if bet_amount <= 0:
                    print("Bet amount must be positive!")
                elif bet_amount > max_bet:
                    print(
                        f"Bet amount (${bet_amount}) exceeds your balance (${max_bet})!"
                    )
                else:
                    return bet_amount

            except ValueError:
                print("Please enter a valid number!")

    def get_validated_bet(self, max_bet: float) -> Optional[Any]:
        """
        Guide user through the complete bet placement process with validation.

        Args:
            max_bet: The maximum amount the user can bet

        Returns:
            A validated Bet object if successful, None if user cancels or validation fails

        Process:
            1. Show available bet types
            2. Get bet type selection
            3. Get bet amount
            4. Get bet-specific parameters
            5. Validate the complete bet
            6. Allow up to 3 attempts for valid parameters
        """
        self._show_betting_options()

        # Step 1: Get bet type
        bet_type = self._receive_bet_type()
        if bet_type is None:
            return None

        # Step 2: Get bet amount
        bet_amount = self._receive_bet_amount(max_bet)
        if bet_amount is None:
            return None

        # Step 3: Get bet parameters with validation
        for attempt in range(3):
            bet_choice = self._receive_bet_choice(bet_type)
            if bet_choice is None:
                return None

            # Create and validate bet
            bet = self.bet_factory.create_bet(bet_type, bet_amount, choice=bet_choice)

            if bet.validate():
                return bet
            else:
                remaining_attempts = 2 - attempt
                if remaining_attempts > 0:
                    print(f"Invalid parameters. {remaining_attempts} attempts left.")
                else:
                    print("Too many failed attempts. Bet cancelled.")
                    return None

        return None
