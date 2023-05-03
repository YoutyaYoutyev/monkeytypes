import telebot
import requests
import logging
import datetime
import threading
import sqlite3
import io
lock = threading.Lock()

date_obj = datetime.datetime.now()
date = date_obj.strftime('%m-%d-%y-%H-%M-%S ')

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logging.basicConfig(
    level=logging.INFO,
    filename=('logs/' + date + '.log'),
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

with open('token.txt', 'r') as token:
    token = token.read()
with open('monkey_token.txt', 'r') as monkey_token:
    monkey_token = monkey_token.read()

bot = telebot.TeleBot(token)
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()


def log(message):
    logging.info(str(message.chat.id) + " " + "@" + str(message.from_user.username
                                                        if message.from_user.username
                                                        else "None") + " " + str(message.text))


@bot.message_handler(commands=['start'])
def start(message):
    log(message)
    try:
        with lock:
            id_listing = c.execute("SELECT id FROM users WHERE id = ?", (message.from_user.id, )).fetchone()
            username_listing = c.execute("SELECT username FROM users WHERE id = ?", (message.from_user.id, )).fetchone()
        if id_listing is None:
            with lock:
                c.execute("INSERT INTO users VALUES (?, ?)", (message.from_user.id, str(message.from_user.username)))
                conn.commit()
        elif str(message.from_user.username) not in username_listing:
            with lock:
                c.execute('UPDATE users SET username = ? WHERE id = ?', (str(message.from_user.username),
                                                                         message.from_user.id))
                conn.commit()
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, f'''Listing DB error occurred.''', parse_mode='HTML')
    bot.send_message(message.chat.id, f'''👋 <b>Hi there, {message.from_user.full_name}! I'm here to help you 
with your monkeytype.com stats ^^</b>

🐵 <i>Send me any username from Monkeytype and I'll send you it's stats!</i>

🛠 <u><b>Made using Monkeytype's API. By @Youtya_Youtyev. If you have any troubles - message me</b></u>

😺 <b><i>Source code: github.com/YoutyaYoutyev/monkeytypes</i></b>''', parse_mode='HTML')


@bot.message_handler(commands=['send'])
def spam(message):
    log(message)
    try:

        user_id = str(message.from_user.id)

        with open("admins.txt", "r") as adminl:
            adminl = adminl.read()
            adminl = adminl.split("\n")

        if user_id in adminl:

            sendlist = c.execute('SELECT id FROM users').fetchall()

            try:
                for i in sendlist:
                    bot.send_message(i[0], message.text[5:], parse_mode='HTML')

            except Exception:
                pass

        else:
            bot.send_message(message.chat.id, 'Not enough rights to execute :)')

    except Exception as e:

        bot.send_message(message.chat.id, 'Что-то пошло не так.')

        logging.error("error > " + str(e))


@bot.message_handler(commands=['botstop'])
def bot_stop(message):
    log(message)
    user_id = str(message.from_user.id)

    try:

        with open("admins.txt", "r") as adminl:
            adminl = adminl.read()
            adminl = adminl.split("\n")

    finally:

        if user_id in adminl:
            raise Exception("Stopped by Admin.")

        else:
            bot.send_message(message.chat.id, 'Not enough rights to execute :)')


@bot.message_handler(commands=['logs'])
def logs(message):
    log(message)
    user_id = str(message.from_user.id)

    try:

        with open("admins.txt", "r") as adminl:
            adminl = adminl.read()
            adminl = adminl.split("\n")

    finally:

        if user_id in adminl:
            file = open('logs/' + date + '.log', 'rb')
            bot.send_document(message.chat.id, file)

        else:
            bot.send_message(message.chat.id, 'Not enough rights to execute :)')


@bot.message_handler(commands=['db'])
def database(message):
    log(message)
    user_id = str(message.from_user.id)

    try:

        with open("admins.txt", "r") as adminl:
            adminl = adminl.read()
            adminl = adminl.split("\n")

    finally:

        if user_id in adminl:
            file = open('anek.db', 'rb')
            bot.send_document(message.chat.id, file)

        else:
            bot.send_message(message.chat.id, 'Not enough rights to execute :)')


@bot.message_handler(commands=['file'])
def download(message):
    log(message)
    user_id = str(message.from_user.id)

    try:

        with open("admins.txt", "r") as adminl:
            adminl = adminl.read()
            adminl = adminl.split("\n")

    finally:

        if user_id in adminl:
            file = open(message.text[6:], 'rb')
            bot.send_document(message.chat.id, file)

        else:
            bot.send_message(message.chat.id, 'Not enough rights to execute :)')


@bot.message_handler(commands=['get_stats'])
def search_c(message):
    log(message)
    try:
        got = requests.get('https://api.monkeytype.com/users/' + message.text[11:] + '/profile',
                           headers={'Authorization': f'ApeKey {monkey_token}'})
        bot.send_message(message.chat.id, got.text[:3000], parse_mode='HTML')
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, 'User not found or an error occurred :(', parse_mode='HTML')


@bot.message_handler(commands=['get_json_stats'])
def search_json(message):
    log(message)
    try:
        got = requests.get('https://api.monkeytype.com/users/' + message.text[16:] + '/profile',
                           headers={'Authorization': f'ApeKey {monkey_token}'})
        temp = io.BytesIO(got.content)
        bot.send_document(message.chat.id, temp, visible_file_name=(message.text[16:] + '.json'))
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, 'User not found or an error occurred :(', parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def search(message):
    log(message)
    try:
        got = requests.get('https://api.monkeytype.com/users/' + message.text + '/profile',
                           headers={'Authorization': f'ApeKey {monkey_token}'})
        bot.send_message(message.chat.id, got.text[:3000], parse_mode='HTML')
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, 'User not found or an error occurred :(', parse_mode='HTML')


bot.infinity_polling()
