# Blackjack - by Lawrence Huang for the KPCB Engineering Fellows Program 2020

### Rules
Based off of the rules found here: https://bicyclecards.com/how-to-play/blackjack/

### Game modes
Single-player vs. AI dealer

## Design

---

Classes

- Game
  - Constructor()
  - Fields
    - players: List[Player]
    - input_manager: InputManager
  - Methods
    - play() -> None

- BlackjackGame (Game)
  - Constructor(num_decks: int, min_bet: int, max_bet: int, num_players: int, starting_chips: Chips)
  - Fields
    - num_decks: int
    - human_players: List[HumanPlayer]
    - dealer: Dealer
  - Methods
    - get_card_value(card: Card) -> int

- InputManager
  - Constructor()
  - Fields
  - Methods
    - getInput(prompt: str, is_valid: Callable[[Any], bool]) -> str

- Shoe
  - Constructor(num_decks: int)
  - Fields
    - cards: List[Card]
  - Methods
    - get_num_cards() -> int
    - shuffle() -> None
    - deal(num_cards: int) -> None
    - reset() -> None

- Deck
  - Constructor()
  - Fields
    - cards: List[Card]
  - Methods
    - shuffle() -> None
    - get_num_cards() -> int
    - deal(num_cards: int) -> None

- Card
  - Constructor(rank: str, suit: str)
  - Fields
    - rank: str
    - suit: int
  - Methods
    - \_\_str\_\_() -> str

- Player
  - Constructor()
  - Fields
  - Methods
    - take_action(actions: List[str]) -> int

- HumanPlayer (Player)
  - Constructor(starting_chips: Chips)
  - Fields
    - chips: Chips
    - hand: List[Card]
  - Methods
    - place_bet() -> Chips

- Dealer (Player)
  - Constructor()
  - Fields
  - Methods


# DECIDED NOT TO HAVE
- Chips
  - Constructor(chip_dict: Dict[int, int])
  - Fields
    - chip_dict: Dict[int, int]
  - Methods
    - get_cur_value() -> int
    - take_chips(chip_amount: int, number: int) -> Chips
      - throws Exceptions if not enough chips or invalid chip_amount