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
        
class BotServer(object):
    def __init__(self, token):
        self.token = token
        self.games = {}
        self.bot = telepot.Bot(token)

server = None


def add_player(server, chat_id, user_id, name):
    if chat_id not in server.games:
        server.bot.sendMessage(chat_id, "No game created")
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
        filename = str(chat_id) +  name + 'image.png'
        draw.draw_board_state(game, name, filename)
        try:
            server.bot.sendPhoto(user_id, open(filename, 'rb'))
        except Exception as ex:
            print(ex)


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
        for name in server.games[chat_id].playermap.keys():
            players.append(name)
        print(players)
        server.games[chat_id].game = hanabi.Game(players)

        # send a view to all the players
        send_game_views(server, chat_id)
        server.bot.sendMessage(chat_id, "Game sarted!")

    
    if text.startswith('/discard') or text.startswith('/play') or text.startswith('/hint'):
        game = server.games[chat_id].game
        player = game.players[game.active_player]

        hanabi.perform_action(game, player, text[1:].strip())

        game.active_player += 1 
        if game.active_player == len(game.players): 
            game.active_player = 0
        
        send_game_views(server, chat_id)
        

    



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
