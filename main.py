import time
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.loop import MessageLoop
import sys
import hanabi
import draw

class ChatGame:
    def __init__(self):
        self.game = None
        self.playermap = {} 
        self.active_move = None
        self.hint_player = None

class BotServer(object):
    def __init__(self, token):
        self.token = token
        self.games = {}
        self.bot = telepot.Bot(token)

server = None


def add_player(server, chat_id, user_id, name):
    if chat_id not in server.games:
        server.bot.sendMessage(chat_id, "No game created for this chat")
        return
    playermap = server.games[chat_id].playermap
    if len(playermap) >= 4:
        server.bot.sendMessage(chat_id, "Too many players")
        return
    server.bot.sendMessage(chat_id, name + " joined")

    playermap[name] = user_id
    print(server.games)




def send_game_views(bot, chat_game):
    for name, user_id in chat_game.playermap.items():
        # TODO: Send directly generated image, without write to disk.
        filename = str(user_id) + '.png'
        draw.draw_board_state(chat_game.game, name, filename)
        try:
            with open(filename, 'rb') as image:
                bot.sendPhoto(user_id, image)
        except Exception as ex:
            print(ex)


def send_action_message(bot, chat_game, active_player, action):
    for name, user_id in chat_game.playermap.items():
        if name != active_player:
            bot.sendMessage(user_id, active_player + "'s action\n" + action)


def send_keyboard(server, player, chat_id, user_id, keyboard_type):
    if keyboard_type == "action":
        keyboard = ReplyKeyboardMarkup(keyboard=[['Discard'], ['Play'], ['Hint']])
        server.bot.sendMessage(user_id, player + ", it's your turn", reply_markup=keyboard)
    
    elif keyboard_type == "index":
        game = server.games[chat_id].game
        active_player = game.players[game.active_player]
        player_hand = server.games[chat_id].game.hands[active_player]
        options = [[str(i) for i in range(1, len(player_hand)+1)]]

        keyboard = ReplyKeyboardMarkup(keyboard=options)
        server.bot.sendMessage(user_id, "Choose a card index", reply_markup=keyboard)

    elif keyboard_type == "player":
        players = server.games[chat_id].game.players
        options = []
        for p in players:
            if p != player: options.append([p])
        keyboard = ReplyKeyboardMarkup(keyboard=options)
        server.bot.sendMessage(user_id, "Choose a player", reply_markup=keyboard)

    elif keyboard_type == "hint":
        values = [str(i) for i in range(1, 6)]
        colors = ['red', 'blue', 'green', 'white', 'yellow']
        keyboard = ReplyKeyboardMarkup(keyboard=[values, colors])
        server.bot.sendMessage(user_id, "Choose information to hint", reply_markup=keyboard)




def perform_action(server, chat_id, text):
    chat_game = server.games[chat_id]
    game = chat_game.game
    active_player = game.players[game.active_player]
    playermap = chat_game.playermap

    if text.startswith('Discard'):
        chat_game.active_move = "discard"
        send_keyboard(server, active_player, chat_id, playermap[active_player], "index")
        return

    if text.startswith('Play'):
        chat_game.active_move = "play"
        send_keyboard(server, active_player, chat_id, playermap[active_player], "index")
        return

    if text.startswith('Hint'):
        chat_game.active_move = "hint"
        if len(playermap) == 2:
            i = (game.active_player+1) % 2
            chat_game.hint_player = game.players[i]
            send_keyboard(server, active_player, chat_id, playermap[active_player], "hint")
            return
             
        else:
            send_keyboard(server, active_player, chat_id, playermap[active_player], "player")
            return


    # perform discard action
    if chat_game.active_move == "discard" or chat_game.active_move == "play":
        action = chat_game.active_move + " " + text
        hanabi.perform_action(game, active_player, action)
        send_game_views(server.bot, chat_game)
        send_action_message(server.bot, chat_game, active_player, action)

        chat_game.active_move = None
        next_player = game.players[game.active_player]
        send_keyboard(server, next_player, chat_id, playermap[next_player], "action")

    
    if chat_game.active_move == "hint":
        if chat_game.hint_player == None:
            chat_game.hint_player = text
            send_keyboard(server, active_player, chat_id, playermap[active_player], "hint")

        # perform hint action
        else:
            action = "hint " + chat_game.hint_player + " " + text
            hanabi.perform_action(game, active_player, action)
            send_game_views(server.bot, chat_game)
            send_action_message(server.bot, chat_game, active_player, action)
            chat_game.active_move = None
            chat_game.hint_player = None
            next_player = game.players[game.active_player] # recompute the active player
            send_keyboard(server, next_player, chat_id, playermap[next_player], "action")








def handle_message(message_object):
    print(message_object)
    print()
    content_type, chat_type, chat_id = telepot.glance(message_object)
    
    user_id = int(message_object['from']['id'])

    if content_type != 'text':
        return
    
    text = message_object['text']

    if text == '/create_game':
        server.games[chat_id] = ChatGame()
        server.bot.sendMessage(chat_id, "A new game has been created")
        return

    if text.startswith('/join'):
        name = text[len('/join'):].strip()
        add_player(server, chat_id, user_id, name)
        return


    if text == '/start' or text == '/START':
        if text == '/START':
            server.games[chat_id] = ChatGame()
            server.bot.sendMessage(chat_id, "A new game has been created")
            for name in ['gabriele', 'giacomo']:
                add_player(server, chat_id, user_id, name)

        players = []
        playermap = server.games[chat_id].playermap
        for name in playermap.keys():
            players.append(name)

        server.games[chat_id].game = hanabi.Game(players)
        server.bot.sendMessage(chat_id, "Game started with players " + str(players))

        # send a view to all the players
        chat_game = server.games[chat_id]
        send_game_views(server.bot, chat_game)
        server.bot.sendMessage(chat_id, "Game sarted!")
        
        game = server.games[chat_id].game
        active_player = game.players[game.active_player]

        send_keyboard(server, active_player, chat_id, playermap[active_player], "action")
        return

    
    # game started
    for chat, game in server.games.items():
        if not game: continue
        for uname, uid in game.playermap.items():
            if uid == user_id:
                perform_action(server, chat, text)

    






def main(token):
    global server
    server = BotServer(token)
    
    print ('*** Telegram bot started ***')
    print ('    Now listening...')
    MessageLoop(server.bot, handle_message).run_as_thread()
    while 1:
        time.sleep(10)


if __name__ == '__main__':
    main(sys.argv[1])
