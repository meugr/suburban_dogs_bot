import telebot
from telebot import types

import pytz
# import datetime as dt
import dateutil.parser

from little_db import UserState
from little_db import StationInfo
from ya_api import YaAPI
import parser

import config

r = UserState()
s = StationInfo(config.DB_PATH)

bot = telebot.TeleBot(config.TG_TOKEN)
remove_markup = types.ReplyKeyboardRemove()  # настройка кастомной клавиатуры
markup = types.ReplyKeyboardMarkup()
markup.row('Сегодня', 'Завтра')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать.')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Узнай актуальное расписание \
электричек!\nВыберите свой часовой пояс для корректной работы.')


@bot.message_handler(commands=['cancel'])
def cancel_search(message):
    print(r.get_info(message.chat.id))
    r.reset_info(message.chat.id)
    bot.send_message(message.chat.id, 'Вы отменили выбор станции.',
                     reply_markup=remove_markup)


@bot.message_handler(commands=['search'],
                     func=lambda message: r.get_info(
                     message.chat.id) == {})
def get_departure(message):
    r.start_search(message.chat.id)
    bot.send_message(message.chat.id, 'Введите станцию отправления')


# старт FSM
@bot.message_handler(func=lambda message:
                     len(r.get_info(message.chat.id)) == 1)
def get_arrival(message):
    r.append_info(message.chat.id, 'departure', message.text)
    bot.send_message(message.chat.id, 'Введите станцию прибытия')
    print(r.get_info(message.chat.id))


@bot.message_handler(func=lambda message:
                     len(r.get_info(message.chat.id)) == 2)
def get_date(message):
    r.append_info(message.chat.id, 'arrival', message.text)
    bot.send_message(message.chat.id, 'Выберете дату', reply_markup=markup)
    print(r.get_info(message.chat.id))


@bot.message_handler(func=lambda message:
                     len(r.get_info(message.chat.id)) == 3)
def return_result(message):
    bot.send_message(
        message.chat.id, 'Загружаю расписание...', reply_markup=remove_markup)
    r.append_info(message.chat.id, 'date', message.text)

    data = r.get_info(message.chat.id)
    print(data)
    d, a = s.get_info_with_db(data)  # отправление и прибытие с регионом и нитью
    print(d, a, sep='\n\n')
    if len(d) > 1:
        print('search_engine d!')  # кастом клава, если станций несколько
    if len(a) > 1:
        print('search_engine a!')
    tzone = pytz.timezone('Europe/Moscow')  # брать tz из настроек юзера
    t_now = parser.get_current_time(tzone)

# Временная мера, написать обработчик некорректного ввода и обработчик
# при нахождении нескольких станций в БД
    try:
        # Получаю инфу о рейсах
        trains = YaAPI.send_request((d[0][0], a[0][0]), t_now)['segments']
    except IndexError:
        bot.send_message(
            message.chat.id, 'Введите корректное название станций')
        r.reset_info(message.chat.id)
        return
    except KeyError:
        bot.send_message(
            message.chat.id,
            '''Извините, для этой станции расписание пока недоступно.
Попробуйте ввести ТОЧНОЕ название станций.''')
        r.reset_info(message.chat.id)
        return

    counter = config.HOW_MUCH
    for train in trains:  # пропускаем только неушедшие рейсы
        delta = dateutil.parser.parse(
            train['departure']).astimezone(tzone) - t_now
        if delta.days >= 0 and counter:  # по дефолту вывод 5 рейсов
            counter -= 1
            msg_dict = parser.info_about_train(train, t_now, delta)
            bot.send_message(
                message.chat.id, parser.message_template(msg_dict),
                parse_mode='markdown')





    r.reset_info(message.chat.id)  # Сброс состояния


if __name__ == '__main__':
    bot.polling(none_stop=True)
