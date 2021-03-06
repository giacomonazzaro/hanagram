import time
import telepot
from telepot.loop import MessageLoop
import sys
import hanabi
import draw
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


class ChatGame:
    def __init__(self, chat_id, admin):
        self.game = None
        self.admin = admin
        self.player_to_user = {} 
        self.current_action = ''
        self.chat_id = chat_id

class BotServer(object):
    def __init__(self, token):
        self.bot = telepot.Bot(token)
        self.token = token
        self.games = {}
        self.user_to_chat = {}

server = None


def add_player(server, chat_id, user_id, name):
    if chat_id not in server.games:
        server.bot.sendMessage(chat_id, "No game created for this chat")
        return

    if user_id in server.user_to_chat.keys():
        # server.bot.sendMessage(chat_id, "You already joined the game")
        return

    player_to_user = server.games[chat_id].player_to_user
    if len(player_to_user) >= 4:
        server.bot.sendMessage(chat_id, "Too many players")
        return
    
    if name in player_to_user:
        name += '_' + str(len(player_to_user))
        
    server.bot.sendMessage(chat_id, name + " joined")
    player_to_user[name] = user_id
    server.user_to_chat[user_id] = chat_id


def send_game_views(bot, chat_game, last_player=''):
    for name, user_id in chat_game.player_to_user.items():
        # TODO: Send directly generated image, without write to disk.
        filename = str(user_id) + '.png'
        draw.draw_board_state(chat_game.game, name, filename)
        try:
            with open(filename, 'rb') as image:
                bot.sendPhoto(user_id, image)
        except Exception as ex:
            print(ex)



def start_game(server, chat_id, user_id):
    if chat_id not in server.games:
        server.bot.sendMessage(chat_id, "No game created for this chat")
        return
    
    if user_id != server.games[chat_id].admin:
        server.bot.sendMessage(chat_id, "You cannot start this game")

    player_to_user = server.games[chat_id].player_to_user
    if len(server.games[chat_id].player_to_user) < 2:
        server.bot.sendMessage(chat_id, "Too few players")
        return

    players = []
    for name in player_to_user.keys():
        players.append(name)

    server.games[chat_id].game = hanabi.Game(players)
    server.bot.sendMessage(chat_id, "Game started with players " + str(players))

    # send a view to all the players
    chat_game = server.games[chat_id]
    send_game_views(server.bot, chat_game)
    server.bot.sendMessage(chat_id, "Game sarted!")
    return


def send_keyboard(bot, chat_game, keyboard_type, its_your_turn=True):
    player = hanabi.get_active_player_name(chat_game.game)
    user_id = chat_game.player_to_user[player]
    if keyboard_type == "action":
        keyboard = [[
            InlineKeyboardButton(text='Discard', callback_data='discard'),
            InlineKeyboardButton(text='Play', callback_data='play'),
        ]]
        if chat_game.game.hints > 0:
            keyboard[0].append(InlineKeyboardButton(text='Hint', callback_data='hint'))
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        if its_your_turn:
            bot.sendMessage(user_id, player + ", it's your turn", reply_markup=keyboard)
    
    elif keyboard_type in ['play', 'discard']:
        game = chat_game.game
        active_player = game.players[game.active_player]
        player_hand = chat_game.game.hands[active_player]
        options = []
        for i, card in enumerate(player_hand):
            info = ''
            if card.is_color_known:
                info += card.color + ' '
            if card.is_value_known:
                info += str(card.value) + ' '
            info = info.strip()
            if info == '':
                info = ' '
            options.append(InlineKeyboardButton(text=info, callback_data=str(i+1)))

        keyboard = InlineKeyboardMarkup(inline_keyboard=[options])
        bot.sendMessage(user_id, "Choose card to " + keyboard_type, reply_markup=keyboard)

    elif keyboard_type == "player":
        players = chat_game.game.players
        options = []
        for p in players:
            if p != player:
                options.append(InlineKeyboardButton(text=p, callback_data=p))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[options])
        bot.sendMessage(user_id, "Choose a player to hint", reply_markup=keyboard)

    elif keyboard_type == "info":
        # TODO: ugly keyboard on desktop
        colors = []
        values = []
        for c in hanabi.colors:
            colors.append(InlineKeyboardButton(text=c, callback_data=c))
        for i in range(1, 6):
            values.append(InlineKeyboardButton(text=str(i), callback_data=str(i)))

        keyboard = InlineKeyboardMarkup(inline_keyboard=[colors, values])
        bot.sendMessage(user_id, "Choose information to hint", reply_markup=keyboard)        


def restart_turn(bot, chat_game):
    chat_game.current_action = ''
    send_keyboard(server.bot, chat_game, "action")


def handle_game_ending(bot, chat_game):
    send_game_views(bot, chat_game)
    chat_id = chat_game.chat_id
    game = chat_game.game
    filename = str(chat_id) + '.png'
    draw.draw_board_state(chat_game.game, '', filename)
    try:
        with open(filename, 'rb') as image:
            bot.sendPhoto(chat_id, image)
    except Exception as ex:
        print(ex)

    score = hanabi.get_score(game)
    for name, user_id in chat_game.player_to_user.items():
        bot.sendMessage(user_id, "The game ended with score " + str(score))
    
    bot.sendMessage(chat_id, "The game ended with score " + str(score))
    bot.sendMessage(chat_id, "Send /restart to play again")
    chat_game.game = None
    return


def complete_processed_action(bot, chat_game, last_player):
    # check game ending
    if hanabi.check_state(chat_game.game) != 0:
        handle_game_ending(bot, chat_game)
        return

    send_game_views(bot, chat_game)
    chat_game.current_action = ''
    next_player = hanabi.get_active_player_name(chat_game.game)
    send_keyboard(server.bot, chat_game, "action")


def handle_keyboard_response(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print(msg)
    user_id = int(msg['from']['id'])
    chat_id = int(msg['message']['chat']['id'])

    if data == 'join':
        add_player(server, chat_id, user_id, msg['from']['first_name'])
        return

    # TODO: refactor this block into a function
    chat = server.user_to_chat.get(user_id, None)
    if not chat: return

    chat_game = server.games.get(chat, None)
    if not chat_game: return

    game = chat_game.game
    if not game: return

    active_player = hanabi.get_active_player_name(game)
    active_user_id = chat_game.player_to_user[active_player]
    if user_id != active_user_id: return

    # perform action
    if chat_game.current_action in ["discard", "play"] or chat_game.current_action.strip().startswith('hint '):
        chat_game.current_action += ' ' + data
        success = hanabi.perform_action(game, active_player, chat_game.current_action)

        if success:
            complete_processed_action(server.bot, chat_game, active_player)
        else:
            restart_turn(server.bot, chat_game)

    if chat_game.current_action == 'hint':
        chat_game.current_action += ' ' + data
        send_keyboard(server.bot, chat_game, "info")


    if data == 'discard':
        if chat_game.current_action != '': return False
        chat_game.current_action = "discard"
        send_keyboard(server.bot, chat_game, "discard")
        return True

    if data == 'play':
        if chat_game.current_action != '': return False
        chat_game.current_action = "play"
        send_keyboard(server.bot, chat_game, "play")
        return True

    if data == 'hint':
        if chat_game.current_action != '': return False
        chat_game.current_action = "hint"
        if len(chat_game.player_to_user) == 2:
            i = 1 - game.active_player
            chat_game.current_action += ' ' + game.players[i]
            send_keyboard(server.bot, chat_game, "info")
        else:
            send_keyboard(server.bot, chat_game, "player")
        return True


def handle_message(message_object):
    print(message_object, '\n')
    content_type, chat_type, chat_id = telepot.glance(message_object)
    
    user_id = int(message_object['from']['id'])

    if content_type != 'text':
        return
    
    text = message_object['text'].split('@')[0].strip()
    data = message_object.get('callback_data', None)
    if data:
        print('DATA', data)

    if text == '/new_game':
        server.games[chat_id] = ChatGame(chat_id, admin=user_id)
        keyboard = [[
            InlineKeyboardButton(text='Join', callback_data='join'),
        ]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        server.bot.sendMessage(chat_id, "A new game has been created", reply_markup=keyboard)
        return

    if text == '/end_game':
        del server.games[chat_id]
        server.bot.sendMessage(chat_id, "The game ended.")
        return

    if text in ['/start', '/restart']:
        start_game(server, chat_id, user_id)    
    
    if text == "/S":
        server.games[chat_id] = ChatGame(chat_id, admin=user_id)
        server.bot.sendMessage(chat_id, "A new game has been created.")
        for name in ['gabriele', 'giacomo', 'fabrizio']:
            add_player(server, chat_id, user_id, name)
        start_game(server, chat_id, user_id)  



    # Cancel an action with any text
    chat = server.user_to_chat.get(user_id, None)
    if not chat: return

    chat_game = server.games[chat]
    game = chat_game.game

    if not game: return

    active_player = hanabi.get_active_player_name(chat_game.game)
    active_user_id = chat_game.player_to_user[active_player]
    if user_id == active_user_id:
        restart_turn(server.bot, chat_game)
    else:
        server.bot.sendMessage(chat_id, "Wait for your turn.")





def main(token):
    global server
    server = BotServer(token)
    
    print ('*** Telegram bot started ***')
    print ('    Now listening...')
    MessageLoop(server.bot, {'chat': handle_message, 'callback_query': handle_keyboard_response}).run_as_thread()
    while 1:
        time.sleep(10)


if __name__ == '__main__':
    main(sys.argv[1])
