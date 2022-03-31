import time
import telepot
from telepot.loop import MessageLoop
import itertools
import sys
import hanabi
import draw
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

BACKGROUND_COLORS_RGB = itertools.cycle((
    (20, 20, 20),  # black
    (100, 20, 20),  # red
    (10, 50, 10),  # green
    (15, 30, 74),  # blue
    (75, 0, 70),  # purple
))

class ChatGame:
    def __init__(self, chat_id, admin):
        self.game = None
        self.admin = admin
        self.player_to_user = {}
        self.user_to_message = {}
        self.current_action = ''
        self.chat_id = chat_id
        self.background_color = next(BACKGROUND_COLORS_RGB)

class BotServer(object):
    def __init__(self, token):
        self.bot = telepot.Bot(token)
        self.token = token
        self.games = {}

server = None


def add_player(server, chat_id, user_id, name, allow_repeated_players=False):
    if chat_id not in server.games:
        server.bot.sendMessage(chat_id, "No game created for this chat")
        return

    player_to_user = server.games[chat_id].player_to_user
    user_to_message = server.games[chat_id].user_to_message
    if not allow_repeated_players and user_id in player_to_user.values():
        return

    # if user_id in server.user_to_chat_id.keys():
        # server.bot.sendMessage(chat_id, "You already joined the game")
        # return

    if len(player_to_user) >= 4:
        server.bot.sendMessage(chat_id, "There are already 4 players in the game.")
        return
    
    if name in player_to_user:
        name += '_' + str(len(player_to_user))
        
    server.bot.sendMessage(chat_id, name + " joined")
    player_to_user[name] = user_id
    user_to_message[user_id] = None
    # server.user_to_chat_id[user_id] = chat_id


def send_game_views(bot, chat_game, last_player=''):
    for name, user_id in chat_game.player_to_user.items():
        # TODO: Send directly generated image, without write to disk.
        filename = str(user_id) + '.png'
        draw.draw_board_state(chat_game.game, name, filename, background=chat_game.background_color)
        try:
            with open(filename, 'rb') as image:
                bot.sendPhoto(user_id, image)
        except Exception as ex:
            print(ex)
            pass



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
    server.bot.sendMessage(chat_id, "Game started!")
    return


def edit_message(chat_game, bot, chat_id, message="", keyboard=None, delete=False):
    edited = telepot.message_identifier(chat_game.user_to_message[chat_id])
    if delete:
        bot.deleteMessage(edited)
    else:
        bot.editMessageText(edited, message, reply_markup=keyboard)


def send_keyboard(bot, chat_id, keyboard_type):
    chat_game = server.games[chat_id]
    player = hanabi.get_active_player_name(chat_game.game)
    user_id = chat_game.player_to_user[player]
    if keyboard_type == "action":
        keyboard = [[
            InlineKeyboardButton(text='Discard', callback_data='discard|' + str(chat_id)),
            InlineKeyboardButton(text='Play', callback_data='play|' + str(chat_id)),
        ]]
        if chat_game.game.hints > 0:
            keyboard[0].append(InlineKeyboardButton(text='Hint', callback_data='hint|' + str(chat_id)))
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        if chat_game.user_to_message[user_id] is not None:
            # quick fix for unkown crash when user try to /refresh
            try:
                edit_message(chat_game, bot, user_id, player + ", choose an action", keyboard)
            except telepot.exception.TelegramError:
                chat_game.user_to_message[user_id] = bot.sendMessage(user_id, player + ", it's your turn", reply_markup=keyboard)
        else:
            chat_game.user_to_message[user_id] = bot.sendMessage(user_id, player + ", it's your turn", reply_markup=keyboard)
    
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
            options.append(InlineKeyboardButton(text=info, callback_data=str(i+1)+ '|' + str(chat_id)))

        back = [InlineKeyboardButton(text='Back', callback_data='back|' + str(chat_id))]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[options, back])
        edit_message(chat_game, bot, user_id, "Choose card to " + keyboard_type, keyboard)

    elif keyboard_type == "player":
        players = chat_game.game.players
        options = []
        for p in players:
            if p != player:
                options.append(InlineKeyboardButton(text=p, callback_data=p + '|' + str(chat_id)))
        back = [InlineKeyboardButton(text='Back', callback_data='back|' + str(chat_id))]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[options, back])
        edit_message(chat_game, bot, user_id, "Choose a player to hint", keyboard=keyboard)

    elif keyboard_type == "info":
        # TODO: ugly keyboard on desktop
        colors = []
        values = []
        for c in hanabi.colors:
            colors.append(InlineKeyboardButton(text=c, callback_data=c + '|' + str(chat_id)))
        for i in range(1, 6):
            values.append(InlineKeyboardButton(text=str(i), callback_data=str(i) + '|' + str(chat_id)))

        back = [InlineKeyboardButton(text='Back', callback_data='back|' + str(chat_id))]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[colors, values, back])
        edit_message(chat_game, bot, user_id, "Choose information to hint", keyboard=keyboard)      


def restart_turn(chat_id):
    chat_game = server.games[chat_id]
    chat_game.current_action = ''
    send_keyboard(server.bot, chat_id, "action")


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


def complete_processed_action(bot, chat_id, last_player):
    # check game ending
    chat_game = server.games[chat_id]
    if hanabi.check_state(chat_game.game) != 0:
        handle_game_ending(bot, chat_game)
        return

    send_game_views(bot, chat_game)
    chat_game.current_action = ''
    next_player = hanabi.get_active_player_name(chat_game.game)
    send_keyboard(server.bot, chat_id, "action")


def handle_keyboard_response(msg):
    try:
        query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    except:
        print("[ERROR]", msg)
        return

    user_id = int(msg['from']['id'])
    chat_id = int(msg['message']['chat']['id'])

    if data == 'join':
        add_player(server, chat_id, user_id, msg['from']['first_name'])
        return

    data, chat_id = data.split('|')
    chat_id = int(chat_id)

    chat_game = server.games.get(chat_id, None)
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
            edit_message(chat_game, server.bot, user_id, delete=True)
            chat_game.user_to_message[active_user_id] = None
            complete_processed_action(server.bot, chat_id, active_player)
        else:
            restart_turn(chat_id)

    if chat_game.current_action == 'hint':
        chat_game.current_action += ' ' + data
        send_keyboard(server.bot, chat_id, "info")

    if data == 'back':
        send_keyboard(server.bot, chat_id, "action")

    if data == 'discard':
        if chat_game.current_action != '': return False
        chat_game.current_action = "discard"
        send_keyboard(server.bot, chat_id, "discard")
        return True

    if data == 'play':
        if chat_game.current_action != '': return False
        chat_game.current_action = "play"
        send_keyboard(server.bot, chat_id, "play")
        return True

    if data == 'hint':
        if chat_game.current_action != '': return False
        chat_game.current_action = "hint"
        if len(chat_game.player_to_user) == 2:
            i = 1 - game.active_player
            chat_game.current_action += ' ' + game.players[i]
            send_keyboard(server.bot, chat_id, "info")
        else:
            send_keyboard(server.bot, chat_id, "player")
        return True


def handle_message(message_object):
    content_type, chat_type, chat_id = telepot.glance(message_object)
    
    user_id = int(message_object['from']['id'])

    if content_type != 'text':
        return
    
    text = message_object['text'].split('@')[0].strip()
    data = message_object.get('callback_data', None)
    chat_id = int(chat_id)
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

    elif text == '/end_game':
        edit_message(server.games[chat_id], server.bot, user_id, "The game ended.")
        del server.games[chat_id]
        return

    elif text in ['/start', '/restart']:
        start_game(server, chat_id, user_id)    
    
    elif text.startswith("/test"):
        try:
            _, n = text.split(' ')
        except ValueError:
            n = 4
        server.games[chat_id] = ChatGame(chat_id, admin=user_id)
        server.bot.sendMessage(chat_id, "A new game has been created.")
        test_players = ['gabriele', 'giacomo', 'fabrizio', 'caio']
        for name in test_players[:int(n)]:
            add_player(server, chat_id, user_id, name, allow_repeated_players=True)
        start_game(server, chat_id, user_id)
    elif text == '/refresh':
        pass
    else:
        return

    chat_game = server.games[chat_id]
    game = chat_game.game

    if not game: 
        return

    active_player = hanabi.get_active_player_name(chat_game.game)
    active_user_id = chat_game.player_to_user[active_player]
    if user_id == active_user_id:
        restart_turn(chat_id)
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
