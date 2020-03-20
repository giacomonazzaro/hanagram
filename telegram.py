import sys
import time
import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from telepot.loop import MessageLoop

# user_id = 413404680

def get_bot(token):
    bot = telepot.Bot(token)
    # me = tg.bot.getMe()
    return bot


def start_running(bot, handle_message_function):
    print ('*** Telegram bot started ***')
    print ('    Now listening...')
    MessageLoop(bot, handle_message_function).run_as_thread()

    while 1:
        time.sleep(10)

    exit('EXIT time spleep')


def main():
    bot = get_bot(token)
    start_running(bot)


#     global babel_domains, KB, bot, me, dtree_classifier, dtree_classifier_binary
#     dtree_classifier = qu.classifier()
#     dtree_classifier_binary = qu.classifier()

#     babel_domains = babel_domains_load()
#     KB = load.load_database_dictionary('DB_dict.txt')

#     bot = telepot.Bot(token)
#     me = bot.getMe()
#     MessageLoop(bot, handle).run_as_thread()

#     while 1:
#         time.sleep(10)
#     exit('EXIT time spleep')


# if __name__ == '__main__':
    # while 1:
    #     bnid = babelnet.babelfy(input())[0]
    #     print("bnid", bnid)
    #     print("word", babelnet.word_from_babelnetId(bnid))

    # main()