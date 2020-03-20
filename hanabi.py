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

def main():
    deck = new_deck()
    for card in deck:
        print(str(card.value) + " " + card.color)

if __name__ == '__main__':
    main()