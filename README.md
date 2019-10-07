# Blackjack - by Lawrence Huang for the KPCB Engineering Fellows Program 2020

### Rules
Based off of the rules found here: https://bicyclecards.com/how-to-play/blackjack/

### Game modes
Single or multi player vs. AI dealer

### How to run game/tests
- clone repository to directory of choice
```
git clone git@github.com:lawrenceh1850/Blackjack-KPCB.git
```
- navigate to cloned repository
```
cd Blackjack-KPCB
```
- change permissions on run scripts
```
chmod 700 run_blackjack.sh
chmod 700 run_blackjack_tests.sh
```
- to run game
```
./run_blackjack.sh
```
- to run tests
```
./run_blackjack_tests.sh
```

### System tests
- player tries to split, can't if they don't have enough chips to match original bet
- player gets one blackjack out of two split hands
- set a player's chips to 0
    - when there was 1 player: game ended
    - when there were multiple players: game continued with other players
- set dealer hand to a blackjack
    - insurance situations:
        - set ace face up
            - buy insurance with half of original bet
            - try to buy insurance when no chips remaining
- set deck to be empty
    - before dealing
    - after dealing
            
### Points of improvement:
- when offering insurance, tell player how much they can buy maximum right away instead of in a tooltip