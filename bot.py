import telebot
import time
from configparser import ConfigParser

file = 'config.ini'
config = ConfigParser()
config.read(file)


TOKEN = config['botdata']['token']
bot = telebot.TeleBot(TOKEN)

status_for_reply = True
last_found_synonym = None


@bot.message_handler(commands=['saufi_start'])  # start message handler
def send_start(message):
    global status_for_reply
    status_for_reply = True
    bot.reply_to(message, 'Saufi Bot has started. 🙃🍾')


@bot.message_handler(commands=['saufi_stop'])  # stop message handler
def send_stop(message):
    global status_for_reply
    status_for_reply = False
    bot.reply_to(message, 'Saufi Bot has stopped. 🥺')


@bot.message_handler(commands=['saufi_status'])  # status message handler
def send_status(message):
    bot.reply_to(message, status())


@bot.message_handler(commands=['saufi_synonyms'])  # synonym message handler
def send_synonyms(message):
    synonym_list = config['synonyms_for_drinking']['synonyms']
    bot.reply_to(message, "A list of drinking synonyms:\n" + synonym_list)


def status():
    global status_for_reply
    if status_for_reply is True:
        return "Saufi Bot is currently running. 🍻"
    else:
        return "Saufi Bot is drinking alone. 🥺😢"


@bot.message_handler(commands=['saufi', 'saufi_help'])  # help message handler
def send_help(message):
    bot.reply_to(message, 'This is the Help-Page: 🍺🍻\n '
                          '/saufi: Displays this Page 🤷‍♂️.\n '
                          '/saufi_start: Starts answering.\n '
                          '/saufi_stop: Stops answering.\n '
                          '/saufi_status: Show bot-status.\n '
                          '/saufi_synonyms: A list of all drinking synonyms.')


@bot.message_handler(func=lambda msg: msg.text is not None and lower_message_contains_word(msg, 'sauf') is True
                                      and status_for_reply)
# lambda function checks if the message is not null and if 'sauf' is contained.
# in case msg.text doesn't exist, the handler doesn't process it
def replymessage_to_sauf(message):
    bot.reply_to(message, "Did I hear SAUFI ❤️")


def lower_message_contains_word(msg, word):
    # check if a word in lowercase is contained in the message.
    text = msg.text.lower()
    if word in text:
        return True
    else:
        return False


@bot.message_handler(func=lambda msg: msg.text is not None and lower_message_contains_word_in_list(msg) is True
                                      and status_for_reply)
# lambda function checks if the message is not null and if a synonym for drinking is in the list of synonyms contained
# in the message
# in case msg.text doesn't exist, the handler doesn't process it
def replymessage_to_synonym(message):
    global last_found_synonym
    if last_found_synonym is not None:
        bot.reply_to(message, last_found_synonym + "? \nThat sounds like a synonym for drinking! 🤔😏🍻")


def lower_message_contains_word_in_list(msg):
    # check if a word in lowercase is contained in the message.
    text = msg.text.lower()
    synonym_list = config['synonyms_for_drinking']['synonyms']
    synonym_list = synonym_list.lower()
    synonym_list = synonym_list.split('\n')
    global last_found_synonym
    for i in synonym_list:
        if i in text:
            last_found_synonym = i
            return True
    last_found_synonym = None
    return False


while True:
    try:
        bot.polling(True)
        time.sleep(1)
        # ConnectionError and ReadTimeout because of possible timout of the requests library
        # maybe there are others, therefore Exception
    except Exception:
        time.sleep(15)
