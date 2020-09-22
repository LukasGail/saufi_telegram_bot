import codecs

import telebot
import time
from configparser import ConfigParser
import pathlib
import random

file = 'config.ini'
config = ConfigParser()
config.read(file)

TOKEN = config['botdata']['token']

bot = telebot.TeleBot(TOKEN)
list_of_chatids_not_replying_to = []

last_found_synonym = None


def get_synonyms_string():
    synonyms_file = codecs.open("synonyms.txt", "r", "utf-8")
    synonyms_list = synonyms_file.read()
    synonyms_file.close()
    return synonyms_list


def status_for_reply(msg):
    global list_of_chatids_not_replying_to
    if str(msg.chat.id) in list_of_chatids_not_replying_to:
        return False
    else:
        return True


def is_synonym_present_in_list(synonym):
    syn_string = get_synonyms_string()
    syn_list = syn_string.split('\n')
    syn_list_lower = syn_string.lower().split('\n')
    counter = 0
    for i in syn_list_lower:
        list_element_trimed = i.strip()
        if list_element_trimed in synonym.lower() and i != '' and i != ' ':
            return syn_list[counter].strip()
        counter = counter + 1
    return None


def add_synonym_to_list(synonym_to_add):
    synonyms_file = codecs.open("synonyms.txt", "a", "utf-8")
    synonyms_file.write("\n"+synonym_to_add)
    synonyms_file.close()


def del_synonym_from_list(synonym_to_delete):
    with open("synonyms.txt", "r") as f:
        lines = f.readlines()
    with open("synonyms.txt", "w") as f:
        for line in lines:
            if line.strip("\n") != synonym_to_delete and line.strip("\n").strip() != '':
                f.write(line)


@bot.message_handler(commands=['saufi_start'])  # start message handler
def send_start(message):
    global list_of_chatids_not_replying_to
    if str(message.chat.id) in list_of_chatids_not_replying_to:
        list_of_chatids_not_replying_to.remove(str(message.chat.id))
    bot.reply_to(message, 'Saufi Bot has started. 🙃🍾')


@bot.message_handler(commands=['saufi_stop'])  # stop message handler
def send_stop(message):
    global list_of_chatids_not_replying_to
    if str(message.chat.id) not in list_of_chatids_not_replying_to:
        list_of_chatids_not_replying_to.append(str(message.chat.id))
    bot.reply_to(message, 'Saufi Bot has stopped. 🥺')


@bot.message_handler(commands=['saufi_status'])  # status message handler
def send_status(message):
    bot.reply_to(message, status_msg(message))


@bot.message_handler(commands=['saufi_add'])  # add synonym message handler
def add_synonym(message):
    synonym_to_add = message.text
    synonym_to_add = \
        synonym_to_add.replace('\n', ' ').replace('\r', '').replace('@did_i_hear_saufi_bot', '')[11:].strip()
    synonym_to_add = synonym_to_add.replace('/', '')
    if len(synonym_to_add) > 60:
        bot.reply_to(message, "Please use a synonym that is not longer than 60 characters")
        return
    if len(synonym_to_add) < 4:
        bot.reply_to(message, "Please write a word behind /saufi_add <that is longer than 3 characters>")
    else:
        found_syn_in_list = is_synonym_present_in_list(synonym_to_add)
        if found_syn_in_list is not None:
            bot.reply_to(message, "\"" + found_syn_in_list + "\" was found in List as part of "
                         + "\"" + synonym_to_add + "\".")
        else:
            add_synonym_to_list(synonym_to_add)
            bot.reply_to(message, "\"" + synonym_to_add + "\" was added as synonym for drinking.")


@bot.message_handler(commands=['saufi_del'])  # remove synonym message handler
def remove_synonym(message):
    synonym_to_del = message.text
    synonym_to_del = \
        synonym_to_del.replace('\n', ' ').replace('\r', '').replace('@did_i_hear_saufi_bot', '')[11:].strip()
    if len(synonym_to_del) < 1:
        bot.reply_to(message, "Please write a synonym (/saufi_synonyms) behind /saufi_del <synonym>")
    else:
        found_syn_in_list = is_synonym_present_in_list(synonym_to_del)
        if found_syn_in_list is not None:
            del_synonym_from_list(found_syn_in_list)
            bot.reply_to(message, "\"" + found_syn_in_list + "\" was found and deleted. ")
        else:
            bot.reply_to(message, "\"" + synonym_to_del + "\" was not found as synonym for drinking.\n"
                                                          "Try /saufi_synonyms for a list of synonyms")


@bot.message_handler(commands=['saufi_synonyms'])  # synonym message handler
def send_synonyms(message):
    synonyms_string = get_synonyms_string()
    bot.reply_to(message, "A list of drinking synonyms:\n" + synonyms_string)


def status_msg(message):
    if status_for_reply(message) is True:
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
                          '/saufi_add <syn>: Add synonym to list.\n '
                          '/saufi_del <syn>: Del synonym from list.\n '
                          '/saufi_synonyms: A list of all drinking synonyms.')


@bot.message_handler(func=lambda msg: msg.text is not None and status_for_reply(msg)
                                      and lower_message_contains_word_for_saufi(msg))
# lambda function checks if the message is not null and if 'sauf' is contained.
# in case msg.text doesn't exist, the handler doesn't process it
def replymessage_to_sauf(message):
    bot.reply_to(message, "Did I hear SAUFI? 🍻❤️")
    path = str(pathlib.Path().absolute())
    path = path+'/sticker/sticker{}.webp'.replace('\\', '/').format(random.randint(1, 6))
    sticker = open(path, 'rb')
    bot.send_sticker(message.chat.id, sticker)


def lower_message_contains_word_for_saufi(msg):
    # check if a word in lowercase is contained in the message.
    list_of_saufi_words = config['saufi_words']['synonyms_for_saufi']
    list_of_saufi_words = list_of_saufi_words.lower().split('\n')
    text = msg.text.lower()
    for i in list_of_saufi_words:
        if i in text and i != '' and i != ' ':
            return True
    return False


@bot.message_handler(func=lambda msg: msg.text is not None and lower_message_contains_word_in_list(msg) is True
                                      and status_for_reply(msg) is True)
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
    synonyms_string = get_synonyms_string()
    synonyms_list = synonyms_string.split('\n')
    synonyms_string_lower = synonyms_string.lower()
    synonyms_list_lower = synonyms_string_lower.split('\n')
    counter = 0
    for i in synonyms_list_lower:
        synonyms_list_lower[counter] = i.strip()
        counter = counter + 1

    global last_found_synonym
    last_found_synonym = None
    counter = 0
    for i in synonyms_list_lower:
        if i in text and i != '' and i != ' ':
            last_found_synonym = synonyms_list[int(counter)]
            return True
        counter = counter + 1
    return False


while True:
    try:
        bot.polling(True)
        # time.sleep(1.5)
        # ConnectionError and ReadTimeout because of possible timout of the requests library
        # maybe there are others, therefore Exception
    except Exception:
        time.sleep(10)
