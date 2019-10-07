from gamepieces.card import Card


class NoMoreCardsError(Exception):
    """Error raised when shoe is out of cards"""
    pass


class Deck:
    def __init__(self):
        self._cards = []
        for rank in Card.RANKS_TO_NAMES.keys():
            for suit in Card.SUITS_TO_NAMES.keys():
                self._cards.append(Card(rank, suit))

    @property
    def cards(self):
        return self._cards

    def get_num_cards(self) -> int:
        return len(self.cards)

    def __str__(self):
        str_rep = ""
        for card in self._cards:
            str_rep += str(card) + "\n"
        return str_rep
