import argparse
from copy import deepcopy
import random
import time

from typing import List, Set

from game import Game
from players.human_player import HumanPlayer
from players.dealer import Dealer
from gamepieces.shoe import Shoe
from gamepieces.card import Card
from gamepieces.deck import NoMoreCardsError
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
        # keep track of blackjacks for players
        self.bj_players = {}

        self.round = 1

        # set up deck
        self.shoe = Shoe(num_decks)

        self.min_bet = min_bet
        self.max_bet = max_bet
        self.starting_chips = starting_chips

        self.dealer = Dealer()

    def _print_players(self, bet: bool = False, hand: bool = False):
        title = "=== PLAYER SUMMARY ==="
        print(title, end="")
        for (index, player) in enumerate(self.human_players):
            print()
            print(f"Player {index+1}")
            print(player)
            if bet:
                print(f"Bet amount: {self.player_main_bets[player]}")
            if hand:
                print(f"Hand:\n{player.hand_to_str()}")
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

            side_bet = self.player_side_bets[player]
            if side_bet > 0:
                print(
                    f"Player \"{player.name}\" side bet: {side_bet}")
            print()
        print()

    def _print_game_state(self):
        title = f"===== Round {self.round} ====="
        print(title)
        self._print_players()

    def _select_player_names(self, num_players):
        print("=== NOW SELECTING NAMES ===")
        picked_names = set()
        for i in range(num_players):
            name = self.i_manager.get_input(
                f"Select name for player {i + 1}: ",
                unique_strs(picked_names),
                "Please enter a non-empty, unique name.",
                quit_callback=lambda: self.quit_game(
                    "=== Exiting name selection... ===")
            )
            self.human_players[i].name = name
        print("=== DONE SELECTING NAMES ===")
        self.i_manager.enter_to_cont()

    def _init_betting(self):
        for player in self.human_players:
            self.player_main_bets[player] = 0
            self.player_side_bets[player] = 0

    def _check_player_status(self, player_index):
        """Returns True if player can still play, else False."""
        player = self.human_players[player_index]
        # player no longer has enough to play
        if player.chips < self.min_bet:
            print(
                f"Player \"{player.name}\" no longer has enough chips to play.")

            player = self.human_players[player_index]
            if player in self.player_main_bets:
                del self.player_main_bets[player]
            if player in self.player_side_bets:
                del self.player_side_bets[player]
            if player in self.split_players:
                self.split_players.remove(player)
            if player in self.bj_players:
                del self.bj_players[player]
            del self.human_players[player_index]

            if len(self.human_players) < 1:
                self.quit_game("No players remaining...Quitting game")
            return False
        return True

    def _collect_bets(self):
        for (index, player) in enumerate(self.human_players):
            if not self._check_player_status(index):
                continue

            max_possible = min(self.max_bet, player.chips)

            max_message = "the maximum bet"
            if max_possible < self.max_bet:
                max_message = "the chips you have remaining"

            bet = int(self.i_manager.get_input(
                f"Enter bet for player \"{player.name}\": ",
                is_num_within_bounds(self.min_bet, max_possible),
                f"Please enter a bet between the minimum bet (${self.min_bet}) and {max_message} (${max_possible})",
                quit_callback=lambda:
                self.quit_game("=== Quitting game... ===")))

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
        """Raises NoMoreCardsError if run out cards."""

        # Deal to players
        for i in range(2):
            print(f"=== Dealing card #{i+1} ===")
            for index in range(len(self.human_players)):
                player = self.human_players[index]
                title = f"=== Now dealing to player \"{player.name}\" ==="
                print(title)
                try:
                    self._deal_to_player(player)
                except NoMoreCardsError:
                    raise

                print(f"=== \"{player.name}\" now has: ===\n" +
                      player.hand_to_str(), end="\n\n")
                if 21 in self._calc_hand_value(player.hand):
                    print(f"=== Player \"{player.name}\" has a blackjack! ===")
                    self.bj_players[player] = True
            self.i_manager.enter_to_cont()
            print()

        # Deal to dealer
        title = f"=== Now dealing to Dealer ==="
        print(title)
        for i in range(2):
            try:
                self._deal_to_player(self.dealer)
            except NoMoreCardsError:
                raise
        print(f"=== Dealer's hand so far: ===\n{self.dealer.hand_to_str()}")
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
                max_allowed = min(
                    self.player_main_bets[player] // 2, player.chips)

                condition_str = "half of your original bet"
                if max_allowed == player.chips:
                    condition_str = "your remaining chips"

                side_bet = int(self.i_manager.get_input(
                    f"How much insurance do you want to buy? ",
                    is_num_within_bounds(0, max_allowed),
                    f"Please enter a positive amount no more than ${max_allowed} ({condition_str})", quit_callback=lambda:
                    self.quit_game("Quitting game...")).lower())

                player.chips -= side_bet
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
            if len(player.hand) != 2:
                return False
            else:
                player.chips -= current_bet
                self.player_main_bets[player] += current_bet

                print(
                    f"=== Player \"{player.name}\" has added an additional, equal bet for their second hand ===")
                self._print_bets()

                self.split_players.add(player)
                player.hand = [[player.hand[0]], [player.hand[1]]]

                for i in range(2):
                    print(
                        f"=== Player \"{player.name}\" now playing split hand #{i+1} ===")
                    player.hand[i] = self._handle_normal_play(
                        player.name, player.hand[i])
                    # check for player blackjack
                    if len(player.hand[i]) == 2 and (21 in self._calc_hand_value(player.hand[i])):
                        if player in self.bj_players:
                            self.bj_players[player][i] = True
                        else:
                            self.bj_players[player] = [False, False]
                            self.bj_players[player][i] = True

                return True

    def _handle_double(self, player):
        self.player_main_bets[player] *= 2
        print(
            f"=== Player \"{player.name}\" has doubled their bet to {self.player_main_bets[player]} ===")

        try:
            self._deal_to_player(player)
        except NoMoreCardsError:
            raise

        print(
            f"=== Player \"{player.name}\" has been dealt another card face down and their turn is over ===")

    def _handle_normal_play(self, player_name, player_hand):
        """Returns hand after round of play."""

        print(
            f"=== Current hand: ===\n {HumanPlayer.static_hand_to_str(player_hand)}")
        while True:
            hand_vals = self._calc_hand_value(player_hand)

            # bust
            if len(hand_vals) == 0:
                print(
                    f"=== Player \"{player_name}\" has bust! ===")
                self.i_manager.enter_to_cont()
                break

            print("=== Current hand value: " +
                  "/".join([str(i) for i in list(hand_vals)]) + " ===")
            choice = int(self.i_manager.get_input(
                "Do you wish to:\n1.) hit\n2.) stand\n-> ",
                is_num_within_bounds(1, 2),
                "Please enter 1 or 2",
                quit_callback=lambda:
                self.quit_game("=== Quitting game... ===")))

            if choice == 1:
                # hit
                card_dealt = self._deal_a_card()
                player_hand.append(card_dealt)
                print(
                    f"=== Player \"{player_name}\" was dealt a {card_dealt} ===", end="\n\n")
                print(f"=== \"{player_name}\" now has: === \n" +
                      HumanPlayer.static_hand_to_str(player_hand), end="\n\n")
            else:
                self.i_manager.enter_to_cont()
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
                self.bj_players[player] = True
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

        return False

    def _dealer_actions(self):
        # reveal dealer's other hand
        print("=== Dealer's hand is fully revealed ===")
        print("=== Dealer has: ===\n" + self.dealer.hand_to_str(reveal_all=True))

        while True:
            self.i_manager.enter_to_cont()
            dealer_hand_vals = self._calc_hand_value(self.dealer.hand)

            # bust
            if len(dealer_hand_vals) == 0:
                print(
                    "=== Dealer has bust! ===")
                break
            else:
                max_val = max(dealer_hand_vals)
                print(
                    f"=== Dealer's hand has a value of {max_val}")
                if max_val < 17:
                    print(
                        "=== Dealer has less than 17, dealer hits ===")
                    dealt_card = self._deal_to_player(self.dealer)
                    print(
                        f"=== Dealer was dealt a {str(dealt_card)} ===")
                    print("=== Dealer now has ===\n" +
                          self.dealer.hand_to_str(reveal_all=True))
                else:
                    print(
                        "=== Dealer has 17 or more, dealer stands ===")
                    break
        self.i_manager.enter_to_cont()

    def _settle_payments(self, dealer_blackjack: bool):
        print("\n=== Round completed, now settling payments ===")
        self._print_players(bet=True, hand=True)

        self.i_manager.enter_to_cont()

        dealer_hand_vals = self._calc_hand_value(self.dealer.hand)

        for player in self.human_players:
            # handle side bets for insurance
            if player in self.player_side_bets:
                if dealer_blackjack:
                    side_bet_amount = self.player_side_bets[player]
                    payout = side_bet_amount * 2
                    player.chips += payout
                    print(
                        f"=== Dealer had blackjack and Player \"{player.name}\" collects ${payout} from insurance ===")

            if player in self.split_players:
                for (i, split_hand) in enumerate(player.hand):
                    bet_amount = self.player_main_bets[player] / 2
                    print(
                        f"=== Settling split hand #{i+1} for Player \"{player.name}\" ===")

                    player_hand_vals = self._calc_hand_value(split_hand)

                    # player blackjack stored as array of booleans for split hands
                    player_blackjack = False
                    if player in self.bj_players.keys():
                        player_blackjack = self.bj_players[player][i]

                    original_bet_amount = self.player_main_bets[player] / 2

                    self._check_hand_winner(
                        dealer_blackjack, dealer_hand_vals, player, player_blackjack, player_hand_vals, original_bet_amount)
            else:
                original_bet_amount = self.player_main_bets[player]
                player_blackjack = False
                if player in self.bj_players.keys():
                    player_blackjack = True
                player_hand_vals = self._calc_hand_value(player.hand)

                print(
                    f"=== Settling hand for Player \"{player.name}\" ===")
                self._check_hand_winner(
                    dealer_blackjack, dealer_hand_vals, player, player_blackjack, player_hand_vals, original_bet_amount)
            self.i_manager.enter_to_cont()

    def _check_hand_winner(self,
                           dealer_blackjack, dealer_hand_vals, player, player_blackjack, player_hand_vals, original_bet_amount):
        player_payback_multiple = 0

        # dealer had blackjack
        if dealer_blackjack:
            if player_blackjack:
                print(
                    f"=== Both dealer and player \"{player.name}\" had blackjacks! ===")
                player_payback_multiple = 1
            else:
                print(
                    f"=== Dealer had blackjack and won! ===")
                player_payback_multiple = 0
        elif player_blackjack:  # if player had blackjack, automatically wins
            print(
                f"=== Player had blackjack and won! ===")
            player_payback_multiple = 2.5
        else:  # neither dealer nor player had BJ
            dealer_bust = False
            player_bust = False
            dealer_hand_val = 0
            player_hand_val = 0

            # check dealer bust
            if len(dealer_hand_vals) == 0:
                dealer_bust = True
            else:
                dealer_hand_val = max(dealer_hand_vals)

            # check player bust
            if len(player_hand_vals) == 0:
                player_bust = True
            else:
                player_hand_val = max(player_hand_vals)

            # player bust, automatically loses
            if player_bust:
                print(f"=== Player \"{player.name}\" busted on this hand ===")
                player_payback_multiple = 0
            else:  # player did not bust
                if dealer_bust:  # dealer bust, player wins
                    print("=== Dealer busted ===")
                    player_payback_multiple = 2
                else:  # compare numbers
                    if dealer_hand_val > player_hand_val:
                        # dealer won
                        print("=== Dealer had the higher hand and won ===")
                        player_payback_multiple = 0
                    elif dealer_hand_val == player_hand_val:
                        # push
                        print(
                            f"=== Dealer and player \"{player.name}\" had equal hands, push ===")
                        player_payback_multiple = 1
                    else:
                        # player won
                        print(
                            f"=== Player \"{player.name}\" had the higher hand and won ===")
                        player_payback_multiple = 2

        if player_payback_multiple == 0:
            print(
                f"=== Player \"{player.name}\" lost their bet of ${original_bet_amount} ===")
        elif player_payback_multiple == 1:
            print(
                f"=== Player \"{player.name}\" was refunded their bet of ${original_bet_amount} ===")
        elif player_payback_multiple == 2:
            print(
                f"=== Player \"{player.name}\" was refunded their bet of ${original_bet_amount} and won an additional ${original_bet_amount} ===")
        elif player_payback_multiple == 2.5:
            print(
                f"=== Player \"{player.name}\" refunded their bet of ${original_bet_amount} and won an additional ${original_bet_amount * 1.5} ===")

        player.chips += original_bet_amount * player_payback_multiple
        print()

    def _reset_round(self):
        for player in self.human_players:
            player.clear_hand()
        self.dealer.clear_hand()
        self.split_players = set()
        self.bj_players = {}
        self._init_betting()
        self.round += 1

    def _reset_shoe(self):
        # seed random num generator
        random.seed(time.time())

        print("=== Resetting shoe and reshuffling ===")
        num_decks = self.shoe.num_decks
        self.shoe = Shoe(num_decks)
        self.shoe.shuffle()

    def _refund_bets(self):
        for player in self.player_main_bets:
            player.chips += self.player_main_bets[player]
        for player in self.player_side_bets:
            player.chips += self.player_side_bets[player]

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

            # also checks if players are still in the game
            self._collect_bets()

            self.i_manager.clear_screen()
            self._print_bets()
            self.i_manager.enter_to_cont()

            try:
                self._deal_hands()

                dealer_blackjack = self._player_actions()
                if not dealer_blackjack:
                    self._dealer_actions()
            except NoMoreCardsError:
                print("=== Run out of cards ===")
                print("=== Refunding bets ===")
                self._refund_bets()
                self._reset_shoe()
                print("=== Starting new round ===")
                self._reset_round()
                continue

            self._settle_payments(dealer_blackjack)
            self._reset_round()

    def quit_game(self, quit_message):
        print(quit_message)
        exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-np", "--num_players", type=int, default=1,
                        help="Number of human players")
    parser.add_argument("-nd", "--num_decks", type=int, default=4,
                        help="Number of decks in shoe")
    parser.add_argument("-min", "--min_bet", type=int, default=2,
                        help="Minimum bet amount")
    parser.add_argument("-max", "--max_bet", type=int, default=500,
                        help="Maximum bet amount")
    parser.add_argument("-start", "--starting_chips", type=int, default=500,
                        help="Starting chips amount")

    args = vars(parser.parse_args())
    print(args)
    np = max(1, args["num_players"])
    nd = max(1, args["num_decks"])
    min_bet = max(0, args["min_bet"])
    max_bet = max(1, args["max_bet"])
    sc = max(1, args["starting_chips"])

    bj_game = BlackjackGame(np, nd, min_bet, max_bet, sc)
    bj_game.play()
