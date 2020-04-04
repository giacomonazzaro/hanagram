import time
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.loop import MessageLoop
import sys
import hanabi
import draw
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


class ChatGame:
    def __init__(self):
        self.game = None
        self.player_to_user = {} 
        self.current_action = ''

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
    player_to_user = server.games[chat_id].player_to_user
    if len(player_to_user) >= 4:
        server.bot.sendMessage(chat_id, "Too many players")
        return
    server.bot.sendMessage(chat_id, name + " joined")

    player_to_user[name] = user_id
    server.user_to_chat[user_id] = chat_id




def send_game_views(bot, chat_game, last_player=''):
    for name, user_id in chat_game.player_to_user.items():
        # TODO: Send directly generated image, without write to disk.
        # TODO: Write last performed action on the game view
        # action = chat_game.current_action
        filename = str(user_id) + '.png'
        draw.draw_board_state(chat_game.game, name, filename)
        try:
            with open(filename, 'rb') as image:
                bot.sendPhoto(user_id, image)
        except Exception as ex:
            print(ex)


def notify_players_about_last_action(bot, chat_game, active_player):
    for name, user_id in chat_game.player_to_user.items():
        if name != active_player:
            bot.sendMessage(user_id, active_player + " performed: " + chat_game.current_action)


def send_keyboard(bot, chat_game, keyboard_type, its_your_turn=True):
    player = hanabi.get_active_player_name(chat_game.game)
    user_id = chat_game.player_to_user[player]
    if keyboard_type == "action":
        keyboard = [[
            InlineKeyboardButton(text='Discard', callback_data='discard'),
            InlineKeyboardButton(text='Play', callback_data='play'),
            InlineKeyboardButton(text='Hint', callback_data='hint')
        ]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        if its_your_turn:
            bot.sendMessage(user_id, player + ", it's your turn", reply_markup=keyboard)
    
    elif keyboard_type in ['play', 'discard']:
        game = chat_game.game
        active_player = game.players[game.active_player]
        player_hand = chat_game.game.hands[active_player]
        options = []
        # options = [[str(i) for i in range(1, len(player_hand)+1)]]
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


def complete_processed_action(bot, chat_game, last_player):
    send_game_views(bot, chat_game)
    # active_player_name = chat_game.game.playeres[chat_game.game[active_player]]
    notify_players_about_last_action(server.bot, chat_game, last_player)
    chat_game.current_action = ''
    next_player = hanabi.get_active_player_name(chat_game.game)
    send_keyboard(server.bot, chat_game, "action")


def test(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    user_id = int(msg['from']['id'])
    chat = server.user_to_chat[user_id]
    chat_game = server.games[chat]
    game = chat_game.game
    active_player = hanabi.get_active_player_name(game)

    # perform discard action
    if chat_game.current_action == "discard" or chat_game.current_action == "play":
        chat_game.current_action += ' ' + data
        success = hanabi.perform_action(game, active_player, chat_game.current_action)
        if success:
            complete_processed_action(server.bot, chat_game, active_player)
        else:
            restart_turn(server.bot, chat_game)


    if chat_game.current_action.strip().startswith('hint '):
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
    
    text = message_object['text']
    data = message_object.get('callback_data', None)
    if data:
        print('DATA', data)

    if text == '/create_game':
        server.games[chat_id] = ChatGame()
        server.bot.sendMessage(chat_id, "A new game has been created")
        return

    if text.startswith('/join'):
        name = text[len('/join'):].strip()
        add_player(server, chat_id, user_id, name)
        return


    if text == '/start' or text == '/S':
        if text == '/S':
            server.games[chat_id] = ChatGame()
            server.bot.sendMessage(chat_id, "A new game has been created")
            for name in ['gabriele', 'giacomo', 'fabrizio']:
                add_player(server, chat_id, user_id, name)

        players = []
        player_to_user = server.games[chat_id].player_to_user
        for name in player_to_user.keys():
            players.append(name)

        server.games[chat_id].game = hanabi.Game(players)
        server.bot.sendMessage(chat_id, "Game started with players " + str(players))

        # send a view to all the players
        chat_game = server.games[chat_id]
        send_game_views(server.bot, chat_game)
        server.bot.sendMessage(chat_id, "Game sarted!")
        
        game = server.games[chat_id].game
        active_player = game.players[game.active_player]

        send_keyboard(server.bot, chat_game, "action")
        return


    # Cancel an action with any text
    chat = server.user_to_chat[user_id]
    chat_game = server.games[chat]
    active_player = hanabi.get_active_player_name(chat_game.game)
    active_user_id = chat_game.player_to_user[active_player]
    if user_id == active_user_id:
        restart_turn(server.bot, chat_game)




def main(token):
    global server
    server = BotServer(token)
    
    print ('*** Telegram bot started ***')
    print ('    Now listening...')
    MessageLoop(server.bot, {'chat': handle_message, 'callback_query': test}).run_as_thread()
    while 1:
        time.sleep(10)


if __name__ == '__main__':
    main(sys.argv[1])
