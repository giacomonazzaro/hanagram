import time
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.loop import MessageLoop
import sys
import hanabi

class BotServer(object):
    def __init__(self, token):
        self.token = token
        self.games = {}
        self.bot = telepot.Bot(token)


server = None

def add_player(server, chat_id, user_id, name):
    server.games[chat_id]['playermap'][user_id] = name
    print(name, 'joined')

def handle_message(message_object):
    print(message_object)
    print()
    content_type, chat_type, chat_id = telepot.glance(message_object)
    
    user_id = int(message_object['from']['id'])
    user_name = int(message_object['from']['id'])
    
    if content_type != 'text':
        return
    
    text = message_object['text']

    if text.startswith('/join'):
        name = text[len('/join'):]
        add_player(server, chat_id, user_id, name)

    if text == '/create_game':
        server.games[chat_id] = {'game': None, 'playermap': {} }

    if text == '/start' or text == '/START':
        if text == '/START':
            server.games[chat_id] = {'game': None, 'playermap': {} }
            for i, name in enumerate(['A', 'B', 'C']):
                add_player(server, chat_id, i, name)

        players = []
        for key, value in server.games[chat_id]['playermap'].items():
            players.append(value)
        print(players)
        server.games[chat_id]['game'] = hanabi.Game(players)
        server.bot.sendMessage(chat_id, "Game sarted!")

        original = sys.stdout
        sys.stdout = open(str(chat_id) + '.txt', 'a')
        hanabi.print_board_state(server.games[chat_id]['game'])
        sys.stdout = original

    

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
