from telebot import TeleBot, types
import time
from threading import Thread
import requests
import phonenumbers

#venv
API_TOKEN = ''
bot = TeleBot(API_TOKEN)
manager_id = 
site = "https://redro.ru"

#variables
monitoring_active = True
number_valid = True
text = 'Напишите пожалуйста номер телефона для связи(+7хххххххххх).'
user_problems = {}
button_labels = [
    'Не загружается сайт.',
    'Не могу зайти в профиль.',
    'Белый экран в профиле',
    'Нет торговой точки',
    'Неправильные цены',
    'Не прогружаются товары',
    'Нет нужной позиции',
    'Неправильная картинка у товара',
    'Назад'
]

def contacts(message):
    try:
        parsed_number = phonenumbers.parse(message.text)
        global number_valid
        if phonenumbers.is_valid_number(parsed_number):
            bot.reply_to(message, "Спасибо! В ближайшее время с Вами свяжется оператор!")
            number_valid = True
        else: 
            bot.reply_to(message, "Пожалуйста, введите корректный номер телефона (в формате +7хххххххххх).")
            number_valid = False
    except phonenumbers.NumberParseException:
        bot.reply_to(message, "Пожалуйста, введите корректный номер телефона(в формате +7хххххххххх).")
        number_valid = False

#send_message_to_manager
def reaction(message):
    user_id =  message.from_user.id
    if user_id in user_problems:
        problem = user_problems[user_id]
        contacts(message)
        username = message.from_user.first_name
        global number_valid
        if number_valid:
            bot.send_message(manager_id, f"{username} - {problem}")
            bot.forward_message(manager_id, message.chat.id, message.message_id)
            close(message)
            del problem
        else: print(number_valid)

#open_bot
@bot.message_handler(regexp='^(start|назад|/start)$')
def open(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton('Есть проблема!'))
    keyboard.add(types.KeyboardButton('Нет проблем!'))
    bot.send_message(message.chat.id, 'Добрый день! Что у Вас случилось?', reply_markup=keyboard)

#close_bot
def close(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(types.KeyboardButton('Есть проблема!'))
    keyboard.add(types.KeyboardButton('Нет проблем!'))
    bot.send_message(message.chat.id, 'До связи!', reply_markup=keyboard)

#if_not_problems
@bot.message_handler(regexp='Нет проблем!')
def no_problem(message):
    bot.send_message(message.chat.id, 'Ну и славно')

#if_promlems
@bot.message_handler(regexp='Есть проблема!')
def command_help(message):
    keyboard = types.ReplyKeyboardMarkup()
    for label in button_labels:
        keyboard.add(types.KeyboardButton(label))
    bot.send_message(message.chat.id, 'Уточните c какой проблемой вы столкнулись?', reply_markup=keyboard)

    def problem(message):
        user_problems[message.from_user.id] = message.text
        bot.send_message(message.chat.id,'Напишите пожалуйста номер телефона для связи(в формате +7хххххххххх', reply_markup=keyboard)
        @bot.message_handler(func=lambda message: True)
        def go_profile(message):
            reaction(message)

    @bot.message_handler(regexp='|'.join(button_labels))
    def handle_problem(message):
        problem(message)

#cheking_website
def check_website(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def work_it(message):
    global monitoring_active
    while monitoring_active:
        if not check_website(site):
            bot.send_message(manager_id, "Сайт redro.ru недоступен!")
            time.sleep(60)
        else: bot.send_message(manager_id, "Сайт работает")
        time.sleep(3600)

Thread(target=work_it, args=(bot,), daemon=True).start()
bot.infinity_polling()