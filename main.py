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




def send_game_views(server, chat_id):
    game = server.games[chat_id].game
    playermap = server.games[chat_id].playermap

    for name, user_id in playermap.items():
        # TODO: Send directly generated image, without write to disk.
        filename = str(chat_id) + '_' + str(user_id) + '.png'
        draw.draw_board_state(game, name, filename)
        try:
            with open(filename, 'rb') as image:
                server.bot.sendPhoto(user_id, image)
        except Exception as ex:
            print(ex)




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




def perform_action(srever, chat_id, text):
    chat_game = server.games[chat_id]
    game = chat_game.game
    active_player = game.players[game.active_player]
    playermap = chat_game.playermap


    text = text.lower()
    if text.startswith('discard'):
        chat_game.active_move = "discard"
        send_keyboard(server, active_player, chat_id, playermap[active_player], "index")
        return

    if text.startswith('play'):
        chat_game.active_move = "play"
        send_keyboard(server, active_player, chat_id, playermap[active_player], "index")
        return

    if text.startswith('hint'):
        chat_game.active_move = "hint"
        send_keyboard(server, active_player, chat_id, playermap[active_player], "player")
        return


    # perform action discard
    if chat_game.active_move == "discard":
        hanabi.perform_action(game, active_player, "discard " + text)
        
        game.active_player += 1
        if game.active_player == len(game.players):
            game.active_player = 0

        active_player = game.players[game.active_player]       
        send_game_views(server, chat_id)
        chat_game.active_move = None
        send_keyboard(server, active_player, chat_id, playermap[active_player], "action")

    # perform action play
    if chat_game.active_move == "play":
        hanabi.perform_action(game, active_player, "play " + text)
        
        game.active_player += 1 
        if game.active_player == len(game.players): 
            game.active_player = 0
        
        active_player = game.players[game.active_player]
        send_game_views(server, chat_id)
        chat_game.active_move = None
        send_keyboard(server, active_player, chat_id, playermap[active_player], "action")

    
    
    if chat_game.active_move == "hint":
        if chat_game.hint_player == None:
            chat_game.hint_player = text
            send_keyboard(server, active_player, chat_id, playermap[active_player], "hint")

        # perform hint action
        else:
            hanabi.perform_action(game, active_player, "hint " + chat_game.hint_player + " " + text)
            game.active_player += 1 
            if game.active_player == len(game.players):
                game.active_player = 0
        
            active_player = game.players[game.active_player]
            send_game_views(server, chat_id)
            chat_game.active_move = None
            chat_game.hint_player = None
            send_keyboard(server, active_player, chat_id, playermap[active_player], "action")








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

    if text.startswith('/join'):
        name = text[len('/join'):].strip()
        add_player(server, chat_id, user_id, name)


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
        print(players)
        server.games[chat_id].game = hanabi.Game(players)

        # send a view to all the players
        send_game_views(server, chat_id)
        server.bot.sendMessage(chat_id, "Game sarted!")
        
        game = server.games[chat_id].game
        active_player = game.players[game.active_player]

        send_keyboard(server, active_player, chat_id, playermap[active_player], "action")
    

    if chat_id not in server.games:
        server.bot.sendMessage(chat_id, "No game created")
        return

    if server.games[chat_id].game == None:
        server.bot.sendMessage(chat_id, "Join and start the game")
        return

    
    # game started
    perform_action(server, chat_id, text)

    






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
