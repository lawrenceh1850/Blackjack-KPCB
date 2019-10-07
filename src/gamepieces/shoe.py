from gamepieces.deck import Deck, NoMoreCardsError
import random


class Shoe:
    def __init__(self, num_decks: int, shuffle=True):
        self._num_decks = num_decks
        self._cards = []
        for i in range(num_decks):
            self._cards += Deck().cards
        if shuffle:
            self.shuffle()

    @property
    def num_decks(self):
        return self._num_decks

    @property
    def num_cards(self):
        return len(self._cards)

    def shuffle(self):
        num_shuffles = random.randint(3, 10)
        for _ in range(num_shuffles):
            random.shuffle(self._cards)

    def deal(self):
        if len(self._cards) == 0:
            raise NoMoreCardsError()
        return(self._cards.pop())

    def __str__(self):
        str_rep = ""
        for card in self._cards:
            str_rep += str(card) + "\n"
        return str_rep
