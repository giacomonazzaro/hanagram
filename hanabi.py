from random import shuffle
from collections import namedtuple  

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


class HandCard(object):
    def __init__(self, color, value):
        self.color = color    
        self.value = value 
        self.is_color_known = False
        self.is_value_known = False
        self.not_colors = []
        self.not_values = []

def to_string(card, show_value, show_info):
    info = []
    result = ''
    if show_value:
        result += card.color + ' ' + str(card.value)

    if show_info: 
        if card.is_color_known: info.append(card.color)
        if card.is_value_known: info.append(str(card.value))
        
        for color in card.not_colors:
            info.append('not ' + color)
        for value in card.not_values:
            info.append('not ' + str(value))

    if len(info) > 0:
        if show_value:
            result += ', '
        result += '{'
        for i in range(len(info) - 1):
            result += info[i]
            result += ', '
        result += info[-1]
        result += '}' 
    
    return result


def draw_card(hand, deck):
    if len(deck) == 0: 
        return

    card = deck.pop()
    hand_card = HandCard(card.color, card.value)
    hand.append(hand_card)


def new_hand(deck):
    hand = []
    for _ in range(5):
        draw_card(hand, deck)
    return hand


def print_hand(game, player, show_value, show_info):
    print(player + "'s hand:")
    for i, card in enumerate(game.hands[player]):
        s = to_string(card, show_value, show_info)
        print('[' + str(i + 1) + ']:', s)


class Game(object):
    def __init__(self, player_names):
        self.players = player_names
        self.deck = new_deck()
        self.discarded = {}
        self.errors = 0
        self.hints = 8
        self.hands = {}
        self.piles = {}
        self.final_moves = 0
        self.active_player = 0
        
        for color in colors:
            self.discarded[color] = []
            self.piles[color] = 0

        for player in player_names:
            self.hands[player] = new_hand(self.deck)


def discard_card(game, player, index):
    if index < 1 or index > 5:
        return False

    print('discarding', index)

    hand = game.hands[player]
    card = hand.pop(index - 1)
    game.discarded[card.color].append(card.value)
    game.hints = min(game.hints+1, 8)

    if len(game.deck) == 0:
        game.final_moves += 1

    draw_card(hand, game.deck)
    return True

def play_card(game, player, index):
    if index < 1 or index > 5:
        return False

    hand = game.hands[player]
    card = hand.pop(index - 1)

    success = False
    pile = game.piles[card.color]
    if card.value == pile + 1:
        success = True
        if card.value == 5:
            game.hints = min(game.hints+1, 8)
    
    if success:
        game.piles[card.color] += 1
    else:
        game.errors += 1
        game.discarded[card.color].append(card.value)
    
    if len(game.deck) == 0:
        game.final_moves += 1

    draw_card(hand, game.deck)

    return True


def check_state(game):
    if game.errors == 3:
        return -1
    
    win = True
    for pile in game.piles:
        if pile != 5:
            win = False
            break

    if win: return 1

    if len(game.deck) == 0 and game.final_moves == len(game.players):
        return -1
    
    return 0


def give_color_hint(hand, color):
    for card in hand:
        if card.color == color:
            card.is_color_known = True
            card.not_colors = []
        else:
            if color not in card.not_colors:
                card.not_colors.append(color)

def give_value_hint(hand, value):
    for card in hand:
        if card.value == value:
            card.is_value_known = True
            card.not_values = []
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
        return False

    game.hints -= 1
    if len(game.deck) == 0:
        game.final_moves += 1
    return True

def concatenate(result, l, f, c):
    for i in range(len(l) - 1):
        f(result, l[i])
        c(result)
    f(result, l[-1])

def perform_action(game, player, action):
    name, value = action.strip().split(' ', 1)
    ok = False
    if name == 'discard':
        ok = discard_card(game, player, int(value.strip()))
    
    elif name == 'play':
        ok = play_card(game, player, int(value.strip()))
    
    elif name == 'hint':
        other_player, hint = value.split(' ')
        if other_player not in game.hands.keys():
            return False
        if not hint in colors:
            ok = give_hint(game, other_player, int(hint))
        else:
            ok = give_hint(game, other_player, hint)

    if not ok:
        print('Invalid action. Please repeat.')
    
    return ok

def print_board_state(game, seen_from=None):
    for player in game.players:
        print()
        print_hand(game, player, player != seen_from, True)
        print()
    
    for color in colors:
        print(color + ': ' + str(game.piles[color]) + '  ' + str(game.discarded[color]))
    print()
    
    score = 0
    for color, value in game.piles.items():
        score += value

    print('hints: ' + str(game.hints) + ', errors: ' + str(game.errors))
    print('score: ' + str(score) + ', deck: ' + str(len(game.deck)))
    print()


def main():
    players = ['A', 'B']
    game = Game(players)

    while True:
        print_board_state(game, game.players[game.active_player])

        result = check_state(game)
        if result > 0:
            print('*** You win! ***')
        elif result < 0:
            print('*** You lost! ***')
            break

        ok = False
        while not ok:
            action = input(players[game.active_player] + ': ')
            ok = perform_action(game, players[game.active_player], action)
            if ok:
                game.active_player += 1
                if game.active_player == len(players): game.active_player = 0
                print()
                print('    *****************')
                print()


if __name__ == '__main__':
    main()