from players.player import Player


class Dealer(Player):
    def __init__(self):
        self.hand = []

    def clear_hand(self):
        self.hand = []

    def reveal_hand(self, reveal_number=1):
        """Reveals first x cards from hand, as specified by reveal_number."""
        reveal = []

        for i in range(reveal_number):
            if i < len(self.hand):
                reveal.append(self.hand[i])

        return reveal

    def hand_to_str(self, reveal_all=False, reveal_number=1):
        """Follows same reveal scheme as reveal_hand."""
        str_rep = ""
        if reveal_all:
            for card in self.hand:
                str_rep += "\t- " + str(card) + "\n"
        else:
            for i in range(reveal_number):
                if i < len(self.hand):
                    str_rep += "\t- " + str(self.hand[i]) + "\n"
        return str_rep[:-1]
