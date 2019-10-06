from copy import deepcopy
import random
import time

from typing import List, Set

from game import Game
from players.human_player import HumanPlayer
from players.dealer import Dealer
from gamepieces.shoe import Shoe
from gamepieces.card import Card
from validate_funcs import is_num, unique_strs, is_num_within_bounds, y_or_n


class BlackjackGame(Game):
    """Class for Blackjack game."""

    def __init__(self, num_players: int, num_decks: int, min_bet: int,
                 max_bet: int, starting_chips: int) -> None:
        super().__init__([HumanPlayer(starting_chips)
                          for _ in range(num_players)])

        # alias for blackjack
        self.human_players = self.players

        # bets for main betting
        self.player_main_bets = {}
        # bets for insurance
        self.player_side_bets = {}

        # keep track of players who split
        self.split_players = set()

        self.round = 1

        # set up deck
        self.shoe = Shoe(num_decks)

        self.min_bet = min_bet
        self.max_bet = max_bet
        self.starting_chips = starting_chips

        self.dealer = Dealer()

    def _print_players(self, bet: bool = False):
        title = "=== PLAYER SUMMARY ==="
        print(title, end="")
        for (index, player) in enumerate(self.human_players):
            print()
            print(f"Player {index+1}")
            print(player)
            if bet:
                print(f"Bet amount: {self.player_main_bets[player]}")
        print("=" * len(title))

    def _print_rules(self):
        title = "=== RULES ==="
        print(title)
        print(f"Minimum bet: {self.min_bet}")
        print(f"Maximum bet: {self.max_bet}")
        print("=" * len(title))

    def _print_bets(self):
        for player in self.player_main_bets:
            print(
                f"Player \"{player.name}\" main bet: {self.player_main_bets[player]}")
            print(
                f"Player \"{player.name}\" side bet: {self.player_side_bets[player]}")
            print()
        print()

    def _print_game_state(self):
        title = f"===== Round {self.round} ====="
        print(title)
        self._print_players()

        # TODO: remove
        print(self.player_main_bets)
        print(self.player_side_bets)

    def _select_player_names(self, num_players):
        print("=== NOW SELECTING NAMES ===")
        picked_names = set()
        for i in range(num_players):
            name = self.i_manager.get_input(
                f"Select name for player {i + 1}: ",
                unique_strs(picked_names),
                "Please enter a non-empty, unique name.",
                quit_callback=lambda: self.quit_game(
                    "Exiting name selection...")
            )
            self.human_players[i].name = name
        print("=== DONE SELECTING NAMES ===")
        self.i_manager.enter_to_cont()

    def _init_betting(self):
        for player in self.human_players:
            self.player_main_bets[player] = 0
            self.player_side_bets[player] = 0

    def _check_player_status(self, player_index):
        player = self.human_players[player_index]
        # player no longer has enough to play
        if player.chips < self.min_bet:
            print(
                f"Player \"{player.name}\" no longer has enough chips to play.")

            del self.human_players[player_index]

            if len(self.human_players) < 1:
                self.quit_game("No players remaining...Quitting game")

    def _collect_bets(self):
        for (index, player) in enumerate(self.human_players):
            self._check_player_status(index)

            max_possible = min(self.max_bet, player.chips)

            max_message = "the maximum bet"
            if max_possible < self.max_bet:
                max_message = "the chips you have remaining"

            bet = int(self.i_manager.get_input(
                f"Enter bet for player \"{player.name}\": ",
                is_num_within_bounds(self.min_bet, max_possible),
                f"Please enter a bet between the minimum bet (${self.min_bet}) and {max_message} (${max_possible})",
                quit_callback=lambda:
                self.quit_game("Quitting game...")))

            self.player_main_bets[player] = bet
            # subtract bet from player chips
            player.chips -= bet

        self.i_manager.enter_to_cont()
        print()

    def _calc_hand_value(self, hand: List[Card]) -> Set[int]:
        """Calculates all possible hand values for a hand"""
        values = set()
        values.add(0)
        for card in hand:
            new_values = set()
            for val in values:
                if card.rank == 1:
                    if val + 1 <= 21:
                        new_values.add(val + 1)
                    if val + 11 <= 21:
                        new_values.add(val + 11)
                else:
                    card_val = min(10, card.rank)
                    if val + card_val <= 21:
                        new_values.add(val + card_val)
            values = new_values
        return values

    def _deal_to_player(self, player) -> Card:
        # TODO: handle if the deck needs to be reshuffled
        card_dealt = self.shoe.deal()
        player.hand.append(card_dealt)
        return card_dealt

    def _deal_a_card(self) -> Card:
        # TODO: handle if the deck needs to be reshuffled
        return self.shoe.deal()

    def _deal_hands(self):
        # Deal to players
        for i in range(2):
            print(f"=== Dealing card #{i+1} ===")
            for index in range(len(self.human_players)):
                player = self.human_players[index]
                title = f"=== Now dealing to player \"{player.name}\" ==="
                print(title)
                self._deal_to_player(player)
                print(f"\"{player.name}\" now has: \n" +
                      player.hand_to_str(), end="\n\n")
            self.i_manager.enter_to_cont()
            print()

        # Deal to dealer
        title = f"=== Now dealing to Dealer ==="
        print(title)
        for i in range(2):
            self._deal_to_player(self.dealer)
        print(f"Dealer's hand so far:\n{self.dealer.hand_to_str()}")
        self.i_manager.enter_to_cont()

        print()

    def _handle_insurance(self):
        print("=== Dealer has an ace face-up! ===")
        print("=== Players have option to buy insurance ===")
        for player in self.human_players:
            player_choice = self.i_manager.get_input(
                f"Does player \"{player.name}\" want to buy insurance (y/n): ", y_or_n, "Please enter \"y\" or \"n\"", quit_callback=lambda:
                self.quit_game("Quitting game...")).lower()

            if player_choice == "y":
                    # only allowed to buy up to half of original bet
                max_allowed = self.player_main_bets[player] // 2
                side_bet = int(self.i_manager.get_input(
                    f"How much insurance do you want to buy? ",
                    is_num_within_bounds(0, max_allowed),
                    f"Please enter a positive amount no more than ${max_allowed} (half of your original bet)", quit_callback=lambda:
                    self.quit_game("Quitting game...")).lower())

                self.player_side_bets[player] = side_bet

    def _is_split_hand(self, player) -> bool:
        if len(player.hand) != 2:
            return False
        else:
            return player.hand[0].rank == player.hand[1].rank

    def _is_double_hand(self, player) -> bool:
        if len(player.hand) != 2:
            return False
        else:
            x = self._calc_hand_value(player.hand)
            return 9 in x or 10 in x or 11 in x

    def _handle_split(self, player):
        """Return True if split hands successfully played."""
        current_bet = self.player_main_bets[player]

        if player.chips < current_bet:
            print(
                "=== Player \"{player.name}\" does not have enough chips remaining to split ===")
            return False
        else:
            player.chips -= current_bet
            self.player_main_bets[player] += current_bet
            self.split_players.add(player)

            if len(player.hand) != 2:
                return False
            else:
                player.hand = [[player.hand[0]], [player.hand[1]]]

                for i in range(2):
                    print(
                        f"=== Player \"{player.name}\" now playing split hand {i+1} ===")
                    player.hand[i] = self._handle_normal_play(
                        player.name, player.hand[i])
                return True

    def _handle_double(self, player):
        self.player_main_bets[player] *= 2
        print(
            f"=== Player \"{player.name}\" has doubled their bet to {self.player_main_bets[player]} ===")

        self._deal_to_player(player)
        print(
            f"=== Player \"{player.name}\" has been dealt another card face down and their turn is over ===")

    def _handle_normal_play(self, player_name, player_hand):
        """Returns hand after round of play."""

        print(f"Current hand:\n {HumanPlayer.static_hand_to_str(player_hand)}")
        while True:
            # TODO: remove
            self._print_game_state()
            hand_vals = self._calc_hand_value(player_hand)

            # bust
            if len(hand_vals) == 0:
                print(
                    f"=== Player \"{player_name}\" has bust! ===")
                break

            print("Current hand value: " +
                  "/".join([str(i) for i in list(hand_vals)]))
            choice = int(self.i_manager.get_input(
                "Do you wish to:\n1.) hit\n2.) stand\n-> ",
                is_num_within_bounds(1, 2),
                "Please enter 1 or 2",
                quit_callback=lambda:
                self.quit_game("Quitting game...")))

            if choice == 1:
                # hit
                card_dealt = self._deal_a_card()
                player_hand.append(card_dealt)
                print(
                    f"Player \"{player_name}\" was dealt a {card_dealt}", end="\n\n")
                print(f"\"{player_name}\" now has: \n" +
                      HumanPlayer.static_hand_to_str(player_hand), end="\n\n")
            else:
                break
        return player_hand

    def _player_actions(self) -> bool:
        "Returns True if dealer had blackjack"

        # check dealer second card if first card is ace or ten-card
        revealed_card = self.dealer.reveal_hand()[0]
        # handle insurance
        if revealed_card.rank == 1:
            self._handle_insurance()

        if revealed_card.rank == 1 or revealed_card.rank >= 10:
            print("=== Now checking for dealer blackjack! ===")
            if 21 in self._calc_hand_value(self.dealer.hand):
                print("=== Dealer has blackjack! ===")
                return True
            else:
                print("=== Dealer does not have blackjack! ===")
            print()

        for player in self.human_players:
            print(f"=== Player \"{player.name}\" to play ===")

            if 21 in self._calc_hand_value(player.hand):
                print(f"=== Player \"{player.name}\" has a blackjack! ===")
                continue
            else:
                split_option = self._is_split_hand(player)
                double_option = self._is_double_hand(player)

                if split_option and double_option:
                    # can choose to either split or choose
                    print(
                        f"=== Player \"{player.name}\" has additional options! ===")
                    player_choice = int(self.i_manager.get_input(
                        "Do you wish to:\n1.) split\n2.) double\n-> ",
                        is_num_within_bounds(1, 2),
                        "Please enter 1 or 2",
                        quit_callback=lambda:
                        self.quit_game("Quitting game...")))

                    if player_choice == 1:
                        if self._handle_split(player):
                            continue
                    else:
                        self._handle_double(player)
                        continue
                elif split_option or double_option:
                    print(
                        f"=== Player \"{player.name}\" has additional options! ===")
                    if split_option:
                        # only choice to split
                        player_choice = self.i_manager.get_input(
                            "Do you wish to split (y/n): ",
                            y_or_n,
                            "Please enter \"y\" or \"n\"",
                            quit_callback=lambda:
                            self.quit_game("Quitting game...")).lower()

                        if player_choice == "y":
                            if self._handle_split(player):
                                continue
                    else:
                        # only choice to double
                        player_choice = self.i_manager.get_input(
                            "Do you wish to double (y/n): ",
                            y_or_n,
                            "Please enter \"y\" or \"n\"",
                            quit_callback=lambda:
                            self.quit_game("Quitting game...")).lower()

                        if player_choice == "y":
                            self._handle_double(player)
                            continue

                # normal player action
                self._handle_normal_play(player.name, player.hand)
                self.i_manager.enter_to_cont()

        return False

    def _dealer_actions(self):
        pass

    def _settle_payments(self):
        pass

    def _reset_round(self):
        for player in self.human_players:
            player.clear_hand()
        self.dealer.clear_hand()
        self.split_players = set()
        self._init_betting()

    def game_setup(self) -> None:
        # clear screen
        self.i_manager.clear_screen()

        # seed random num generator
        random.seed(time.time())

        # select player names
        self.player_main_bets = {}
        self._select_player_names(len(self.human_players))

        # betting infrastructure
        self._init_betting()

        # print rules
        print()
        self._print_rules()
        self.i_manager.enter_to_cont()
        print()

        # shuffle shoe
        title = f"=== Now shuffling shoe of {self.shoe.num_decks} decks ==="
        print(title)
        self.shoe.shuffle()
        self.i_manager.enter_to_cont()
        print()

    def play(self) -> None:
        """Main game loop for Blackjack."""

        self.game_setup()

        # main_game_loop
        while True:
            # Print current game state
            self._print_game_state()
            self._collect_bets()

            self.i_manager.clear_screen()
            self._print_bets()
            self.i_manager.enter_to_cont()

            self._deal_hands()
            # TODO: remove
            self.dealer.hand = [Card(4, 1), Card(10, 1)]
            self.human_players[0].hand = [Card(4, 1), Card(4, 1)]

            self._player_actions()
            self._dealer_actions()

            self._settle_payments()
            self._reset_round()

            self.round += 1

    def quit_game(self, quit_message):
        print(quit_message)
        exit(0)


if __name__ == "__main__":
    # TODO: add an argparse that allows user to pick their values
    bj_game = BlackjackGame(1, 4, 2, 500, 100)
    # bj_game = BlackjackGame(2, 4, 2, 500, 100)
    bj_game.play()
