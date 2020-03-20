import telegram
import telepot
import os

# global_token = '413404680:AAGWMfh2d-5fUiwMlvfgSftFXaOdF2B7QuY'
global_token =   '584734213:AAH1DviSNaZQXQ7CWfiPLpIQ8a_RRtPGmZs'
global_bot = None

def handle_message(message_object):
    print(message_object)
    content_type, chat_type, chat_id = telepot.glance(message_object)
    # state = chat_states.get(chat_id, ChatState())

    if content_type != 'text':
        return

    text = message_object['text']
    print(global_token + ':', text)

    if text.startswith('/show'):
        type = text.split(' ')
        if len(type) < 2: return
        type = type[1]
        answer = open('data/'+type+'.txt').read()
        global_bot.sendMessage(chat_id, answer)
        return
    
    if text.startswith('/'):
        text = text[1:]
        # type = text.splitlines()[0][1:]
        type = './data/'+text.split(' ')[0]+'.txt'
        add_new_item(global_databases, type, text)
        global_bot.sendMessage(chat_id, 'ok, salvato')
        write_database()
        print_global_database()


def main():
    global global_bot

    global_bot = telegram.get_bot(global_token)
    telegram.start_running(global_bot, handle_message)



if __name__ == '__main__':
    main()
