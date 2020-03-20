from random import shuffle
        
colors = ['white', 'red', 'blue', 'green', 'yellow']

class Card(object):
    def __init__(self, color, value):
        self.color = color        
        self.value = value 

    def __str__(self):
        return self.color + ' ' + str(self.value)
    
    def __repr__(self):
        return self.__str__()


def new_deck():
    deck = [];        
    for color in colors:
        for i in range(1, 6):
            count = 2
            if i == 1: count = 3
            if i == 5: count = 1
            for _ in range(count):
                deck.append(Card(color, i))

    shuffle(deck)
    return deck


class HandCard(Card):
    def __init__(self, color, value):
        self.color = color        
        self.value = value 
        self.is_color_known = False
        self.is_value_known = False
        self.not_colors = []
        self.not_values = []

    def __str__(self):
        result = ''
        
        if self.is_color_known or self.is_value_known:
            result = 'is: '
            if self.is_color_known: result += self.color + ' '
            if self.is_value_known: result += str(self.value) + ' '
        
        if len(self.not_colors) > 0 or len(self.not_values) > 0:
            result += 'not: '
            if len(self.not_colors) > 0 :
                result += str(self.not_colors)
            if len(self.not_values) > 0 :
                result += str(self.not_values)

        return result
    
    def __repr__(self):
        return self.__str__()


def draw_card(hand, deck):
    # assert(len(hand) != 0)
    card = deck.pop();
    hand_card = HandCard(card.color, card.value)
    hand.append(hand_card)


def new_hand(deck):
    hand = []
    for _ in range(5):
        draw_card(hand, deck)
    return hand


def print_hand(game, player):
    print(player + "'s hand:")
    for card in game.hands[player]:
        print(card)

def print_public_hand(game, player):
    print(player + "'s hand:")
    for card in game.hands[player]:
        print(card.color + ' ' + str(card.value))


class Game(object):
    def __init__(self, player_names):
        self.deck = new_deck()
        self.discarded = {}
        self.errors = 0
        self.hints = 8
        self.hands = {}
        self.piles = {}
        
        for color in colors:
            self.discarded[color] = []
            self.piles[color] = 0

        for player in player_names:
            self.hands[player] = new_hand(self.deck)


def discard_card(game, player, index):
    hand = game.hands[player]
    card = hand.pop(index)
    game.discarded[card.color].append(card.value)
    game.hints += 1

def play_card(game, player, index):
    hand = game.hands[player]
    card = hand.pop(index)
    pile = game.piles[card.color]
    success = False
    if pile == 0:
        if card.value == 1:
            success = True
    else:
        if card.value == pile + 1:
            success == True
        if pile == 5:
            game.hints += 1
    
    if success:
        pile += 1
    else:
        errors += 1
        discarded.append(card)

def check_state(game):
    if game.errors == 3:
        return -1
    
    win = True
    for pile in game.piles:
        if pile != 5:
            win = False
            break

    if win: return -1

    lost = True
    for player, hand in game.hands:
        if len(hand) != 0:
            lost = False
            break

    if lost: return -1 
    
    return 0


def give_color_hint(hand, color):
    for card in hand:
        if card.color == color:
            card.is_color_known = True
        else:
            if color not in card.not_colors:
                card.not_colors.append(color)

def give_value_hint(hand, value):
    for card in hand:
        if card.value == value:
            card.is_value_known = True
        else:
            if value not in card.not_values:
                card.not_values.append(value)


def give_hint(game, player, hint):
    assert(game.hints > 0)
    hand = game.hands[player]
    if type(hint) is str:
        give_color_hint(hand, hint)
    elif type(hint) is int:
        give_value_hint(hand, hint)
    else:
        assert(0)

    game.hints -= 1


def main():
    game = Game(['Giacomo', 'Gabriele'])
    # print(game.deck)
    print_public_hand(game, 'Giacomo')
    print()

    give_hint(game, 'Giacomo', 'red')
    print_hand(game, 'Giacomo')
    print()

    discard_card(game, 'Giacomo', 3)
    print_hand(game, 'Giacomo')



if __name__ == '__main__':
    main()