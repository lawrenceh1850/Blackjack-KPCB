import os
import time
from typing import Any, Callable, Optional


class InputManager:
    def __init__(self):
        self.TIME_DELAY = 0.7

    def time_delay(self, multiple=1.0):
        """Pause game for user to read developments"""

        time.sleep(self.TIME_DELAY * multiple)

    def get_input(self, prompt: str,
                  is_valid: Callable[[Any], bool],
                  error_message: str,
                  quit_callback: Callable = None) -> Optional[str]:
        """
        Read user input from terminal. 

        Returns None on interrupt unless options specified.
        """

        try:
            user_input = input(prompt)
            while is_valid and not is_valid(user_input):
                print(error_message)
                user_input = input(prompt)
            return user_input
        except (EOFError, KeyboardInterrupt):
            if quit_callback:
                quit_callback()
            else:
                return None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def enter_to_cont(self, message="Press enter to continue..."):
        self.get_input(message, is_valid=lambda x: True,
                       error_message="", quit_callback=lambda: exit(1))
