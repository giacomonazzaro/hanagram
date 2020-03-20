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
        server.games[chat_id]['playermap'][user_id] = name
        print(name, 'joined')

    if text == '/create_game':
        server.games[chat_id] = {'game': None, 'playermap': {} }
        # global_bot.sendMessage(chat_id, answer)

    if text == '/start':
        players = []
        for key, value in server.games[chat_id]['playermap'].items():
            players.append(key)    
        server.games[chat_id]['game'] = hanabi.Game(players)
    

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
