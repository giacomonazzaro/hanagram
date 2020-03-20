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
    if len(deck) == 0: 
        return

    card = deck.pop();
    hand_card = HandCard(card.color, card.value)
    hand.append(hand_card)


def new_hand(deck):
    hand = []
    for _ in range(5):
        draw_card(hand, deck)
    return hand


def print_hand(game, player):
    print(player + " hand information:")
    for i, card in enumerate(game.hands[player]):
            print(str(i + 1) + ':', card)

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
    if index < 1 or index > 5:
        return False

    print('discarding', index)

    hand = game.hands[player]
    card = hand.pop(index - 1)
    game.discarded[card.color].append(card.value)
    game.hints += 1
    draw_card(hand, game.deck)
    return True

def play_card(game, player, index):
    if index < 1 or index > 5:
        return False

    hand = game.hands[player]
    card = hand.pop(index - 1)
    success = False
    pile = game.piles[card.color]
    if pile == 0:
        if card.value == 1:
            success = True
    else:
        if card.value == pile + 1:
            success == True
        if pile == 5:
            game.hints += 1
    
    if success:
        game.piles[card.color] += 1
    else:
        game.errors += 1
        game.discarded[card.color].append(card.value)
    
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

    lost = True
    for player, hand in game.hands.items():
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
        return False

    game.hints -= 1
    return True


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


def main():
    players = ['Giacomo', 'Gabriele']
    game = Game(players)

    active = 0
    ok = True
    while True:
        if ok:
            for player in players:
                print_public_hand(game, player)
                print()
                print_hand(game, player)
                print()
            
            for color in colors:
                print(color + ': ' + str(game.piles[color]) + '  ' + str(game.discarded[color]))
            print()
            
            score = 0
            for color, value in game.piles.items():
                score += value

            print('hints:', game.hints, 'errors:', game.errors, 'score:', score)
            print()

            result = check_state(game)
            if result > 0:
                print('*** You win! ***')
            elif result < 0:
                print('*** You lost! ***')
                break

        action = input(players[active] + ': ')
        ok = perform_action(game, players[active], action)
        if ok:
            active += 1
            if active == len(players):
                active = 0
            print()
            print('*****************')
            print()





if __name__ == '__main__':
    main()