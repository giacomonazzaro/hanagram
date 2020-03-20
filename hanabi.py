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

def main():
    players = {'Giacomo': [], 'Gabriele': []}
    deck = new_deck()
    # print_deck(deck)

    for player, hand in players.items():
        hand = new_hand(deck)
        print(hand)

if __name__ == '__main__':
    main()