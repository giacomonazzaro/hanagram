from collections import namedtuple
from sys import getsizeof
from random import shuffle

        
colors = ['white', 'red', 'blue', 'green', 'yellow']

def new_deck():
    deck = [];        
    for color in colors:
        for i in range(1, 6):
            count = 2
            if i == 1: count = 3
            if i == 5: count = 1
            for _ in range(count):
                deck.append(namedtuple('Card', 'color value')(color, i))

    shuffle(deck)
    return deck

def print_deck(deck):
    for card in deck:
        print(str(card.value) + " " + card.color)

def draw_card(hand, deck):
    # assert(len(hand) != 0)
    card = deck.pop();
    hand_card = namedtuple('HandCard', 'color value is_color_known is_value_known not_colors not_values')(card.color, card.value, False, False, [], [])
    hand.append(hand_card)

def discard_card(hand, index, discarded, clues):
    discarded.append(hand.pop(index))
    clues += 1

def play_card(hand, index, discarded, piles, errors):
    card = hand.pop(index)
    pile = piles[card.color]
    success = False
    if len(pile) == 0:
        if card.value == 1:
            success = True
    else:
        if card.value == pile[-1] + 1:
            success == True
    
    if success:
        pile.append(card)
    else:
        errors += 1
        discarded.append(card)

def check_state(errors, players, piles):
    if errors == 3:
        return -1
    
    win = True
    for pile in piles:
        if pile[-1].value != 5:
            win = False
            break

    if win: return -1

    lost = True
    for player, hand in player.items():
        if len(hand) != 0:
            lost = False
            break

    if lost: return -1 
    
    return 0


def new_hand(deck):
    hand = []
    for _ in range(5):
        draw_card(hand, deck)
    return hand

def print_hand(hand):
    for card in hand:
        print(str(card.value) + " " + card.color + " " + str(card.not_colors) + " " + str(card.not_values))


def give_color_clue(hand, color):
    for card in hand:
        if card.color == color:
            card.is_color_known = True
        else:
            if color not in card.not_colors:
                card.not_colors.append(color)

def give_value_clue(hand, value):
    for card in hand:
        if card.value == value:
            card.is_value_known = True
        else:
            if value not in card.not_values:
                card.not_values.append(value)


def give_clue(hand, clue, is_color_clue, clues):
    assert(clues > 0)
    if is_color_clue:
        give_color_clue(hand, clue)
    else:
        give_value_clue(hand, clue)
    clues -= 1


def main():
    players = {'Giacomo': [], 'Gabriele': []}
    deck = new_deck()
    discarded = []
    errors = 0
    clues = 8
    # print_deck(deck)

    for player, hand in players.items():
        hand = new_hand(deck)
        print(hand)

if __name__ == '__main__':
    main()