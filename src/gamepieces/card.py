class Card:
    RANKS_TO_NAMES = {1: "Ace", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
                      6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
                      11: "Jack", 12: "Queen", 13: "King"}

    SUITS_TO_NAMES = {0: "Clubs", 1: "Diamonds", 2: "Hearts", 3: "Spades"}

    def __init__(self, rank: int, suit: int):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{Card.RANKS_TO_NAMES[self.rank]} of {Card.SUITS_TO_NAMES[self.suit]}"
