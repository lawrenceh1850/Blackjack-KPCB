from players.player import Player


class HumanPlayer(Player):
    def __init__(self, starting_chips: int):
        self._chips = starting_chips
        self.hand = []
        self._name = None

    def static_hand_to_str(hand):
        """Static version of string to hand"""
        str_rep = ""
        for card in hand:
            str_rep += "\t- " + str(card) + "\n"
        return str_rep[:-1]

    @property
    def name(self):
        return self._name

    @property
    def chips(self):
        return self._chips

    @chips.setter
    def chips(self, chips):
        self._chips = chips
        self._chips = max(0, self._chips)

    @name.setter
    def name(self, name):
        if name is None or len(name) < 0:
            raise ValueError("Name must be non-empty")
        self._name = name

    def hand_to_str(self):
        # in case of multiple hands
        if any(isinstance(subhand, list) for subhand in self.hand):
            str_rep = ""
            for (i, subhand) in enumerate(hand):
                str_rep += f"Subhand {i+1}\n" + \
                    HumanPlayer.static_hand_to_str(subhand) + "\n"
            return str_rep[:-1]
        else:
            return HumanPlayer.static_hand_to_str(self.hand)

    def clear_hand(self):
        self.hand = []

    def __str__(self):
        string_rep = f"Name: \"{self._name}\""
        # TODO: remove
        # \nHand: "
        # if len(self.hand) > 0:
        #     for card in self.hand:
        #         string_rep += str(card)
        # else:
        #     string_rep += "(empty)"
        string_rep += f"\nChips: ${self.chips}"
        return string_rep
