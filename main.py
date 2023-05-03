import telebot
import requests
import logging
import datetime
import threading
import sqlite3
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
