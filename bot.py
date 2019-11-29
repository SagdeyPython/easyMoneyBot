# encoding: utf - 8
import os
import pickle
import traceback
from datetime import datetime
from functools import wraps
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

flag_textbook_mode_from_text = {}
path_env = "env\.env"
load_dotenv(dotenv_path=path_env)
token = '909657915:AAFg_R2Ib0hw1xQ8sYFHDD5pSVBoFiwpwnk'
global_domashka_keyboard = {}
ex_table = {}


PROXY_HOST = '193.233.78.155'
PROXY_PORT = 65233
PROXY_USER = 'bbildroid228'
PROXY_PASS = 'S3n1ZiQ'

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}
chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)



def catch_error(f):
    @wraps(f)
    def wrap(update, context):
        try:
            return f(update, context)
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id, text="Error occured: " + traceback.format_exc())

    return wrap


def change_number(num, string):
    string = string.split('/')
    number = string[-2]
    last = number[number.index('-'):]
    read = ''
    string[-2] = str(num) + str(last)
    for i in range(len(string)):
        read += string[i] if string[i] != str(num) + str(last) else ''
        if i == 0:
            read += '/'
        elif i == 2:
            read += '/'
        elif i == 3:
            read += '/'
        elif i == 4:
            read += '/'
        elif string[i] == '':
            read += '/'
    read += str(num) + str(last) + '/'
    return read

current_site = '1'

@catch_error
def get_number(update, context):
    text = update.message.text
    # https://gdz.ru/class-9/algebra/makarichev-14/123-nom/
    if 'Отмена' in text:
        default_test(update, global_domashka_keyboard[f'{update.message.chat_id}'], 'Возвращение в меню выбора предмета')
        dispatcher.remove_handler(number_handler)
        dispatcher.add_handler(text_handler)
    elif text.isdigit():
        site = change_number(int(text), current_site)
        get_solution(update=update, context=context, site=site)
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text='Введен некорректный номер')

def get_solution(update, context, site):
    if 'Нейросеть не может распознать домашнее задание' in site or '/-nom/' in site:
        global current_site
        default_test(update, [['Отмена']],'Нейросеть не может распознать домашнее задание\n'
                                                                      'Сейчас вы можете ввести необходимый вам номер:')
        current_site = site
        dispatcher.remove_handler(text_handler)
        dispatcher.add_handler(number_handler)
        return
        # context.bot.send_message(chat_id=update.message.chat_id, text='Введите упр.номер.параграф.№.')
    elif "'Нейросеть не может распознать домашнее задание', ''" in site:
        a = 1
    else:
        s = requests.Session()
        res = s.get(site)
        html = res.text
        soup = bs(html, features="html.parser")
        temp = soup.find_all('div', class_="with-overtask")
        for i in range(len(temp)):
            element = temp[i].find('img')['src']
            bot.send_photo(chat_id=update.message.chat_id, photo=f'https:{element}')

class_people = {}

bot = telegram.Bot(token=token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
chats_file = 'chats.txt'
data_file = 'data.txt'
domashka = {}
ex_table = {}
if os.path.getsize(chats_file) > 0:
    chats = pickle.load(open(chats_file, 'rb')) if os.path.exists(chats_file) else {}
else:
    chats = set()
f = open(data_file, 'r')
if os.path.getsize(data_file) > 0:
    data = pickle.load(open(data_file, 'rb')) if os.path.exists(chats_file) else {}
else:
    data = {'12': '12'}
f.close()
print(bot.get_me())
print(data)
glavnoe_menu_keyboard = [['💻Личный кабинет💻'], ['💵Заработок на подписках💵', '👨‍💼Заработок на рефералах👨‍💼'],
                         ['📞Помощь📞', '📊Вывод📊']]
textbook_menu_keyboard = [['Алгебра', 'Геометрия'], ['Русский'], ['Назад в главное меню']]
algebra_textbooks = [['Ю.Н. Макарычев, Н.Г. Миндюк', 'А.Г. Мерзляк, В.Б. Полонский'], ['Ш.А. Алимов, Ю.М. Колягин'],
                     ['Назад в главное меню', 'Назад в меню выбора учебников']]
russki_textbooks = [['Тростенцова Л.А., Ладыженская Т.А.', 'С.Г. Бархударов, С.Е. Крючков'],
                    ['М.М. Разумовская, С.И. Львова'], ['Назад в главное меню', 'Назад в меню выбора учебников']]
geometriya_textbooks = [['Л.С. Атанасян, В.Ф. Бутузов', 'А.В. Погорелов'], ['Ершова A.П., Голобородько B.В.'],
                        ['Назад в главное меню', 'Назад в меню выбора учебников']]

current_day = datetime.now()
import requests

next_day = int(datetime(2019, 11, current_day.day + 1, 0, 0).timestamp())
next_day_url = f'https://edu.tatar.ru/user/diary/day?for={next_day}'
day_url = 'https://edu.tatar.ru/user/diary/day'


def login_with_requests(session, login, password):
    payload = {'main_login': login, 'main_password': password}
    url = 'https://edu.tatar.ru/logon'
    headers = {'Referer': url}
    responce = session.post(url,
                            data=payload,
                            headers=headers)


proxies = {
    'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
    'https': f'https://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
}


def send_everyone(text, silent=False):
    for chat_id in chats:
        bot.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True,
                         disable_notification=silent)


@catch_error
def start(update, context):
    chats.add(update.message.chat_id)
    with open(chats_file, 'wb') as file:
        pickle.dump(chats, file)
    default_test(update, glavnoe_menu_keyboard, f"Я бот ГДЗ")


def default_test(update, custom_keyboard, text):
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=text,
                     reply_markup=reply_markup)





@catch_error
def text(update, context):
    text = update.message.text
    subject_day = []
    if 'ичный кабинет' in text:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"""
        💻Личный кабинет💻
        👨‍💼Пользователь: -👨‍💼
        💰Средства на выводе: 💰
        💵Количество рефералов:💵
        💳Количество активных рефералов:💳
        Ваша реферальная ссылка - 
    """)
        print(update.message.from_user.first_name)
    else:
        default_test(update, glavnoe_menu_keyboard, 'Комманда "' + text + '" отсутствует')


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

text_handler = MessageHandler(Filters.text, text)
dispatcher.add_handler(text_handler)
updater.start_polling()