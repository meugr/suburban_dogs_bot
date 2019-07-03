import telebot
from telebot import types

import pytz
import dateutil.parser

from little_db import UserData
from little_db import StationInfo
from ya_api import YaAPI
import parser
import config


db = UserData()
s = StationInfo(config.DB_PATH)

bot = telebot.TeleBot(config.TG_TOKEN)
remove_markup = types.ReplyKeyboardRemove()  # настройка кастомной клавиатуры
kbd_choose_date = types.ReplyKeyboardMarkup()
kbd_choose_date.row('Сегодня', 'Завтра')
kbd_choose_date.row('\U0001F519 Отмена')
kbd_start = types.ReplyKeyboardMarkup()
kbd_start.row('\U0001F50D Поиск расписаний')
kbd_start.row('\U0001F551 5 последних запросов')
kbd_start.row('\U0001F6E0 Настройки', '\U0001F198 Помощь')
kbd_cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
kbd_cancel.row('\U0001F519 Отмена')


def on_development_stage(message):
    bot.send_message(message.chat.id, 'Раздел в процессе разработки')


@bot.message_handler(commands=['start'])
def start_message(message):
    db.create_new_user(message.chat.id)
    bot.send_message(
        message.chat.id, 'Добро пожаловать.', reply_markup=kbd_start)



@bot.message_handler(func=lambda message:
                     message.text == '\U0001F551 5 последних запросов')
def last_five(message):
    db.set_branch(message.chat.id, 'state', 'history')
    last = db.get_branch(message.chat.id, 'history')
    kbd_test = types.InlineKeyboardMarkup()
    for b in last:
        kbd_test.add(types.InlineKeyboardButton(text=str(b[0]),
                                                callback_data=' '.join(b[1:])))
    bot.send_message(message.chat.id, 'Открываем архивы...',
        reply_markup=kbd_cancel)
    bot.send_message(
        message.chat.id, 'Выберите недавний маршрут или нажмите отмена', reply_markup=kbd_test)



@bot.callback_query_handler(func=lambda message:
                            db.get_branch(message.message.chat.id, 'state') ==
                            'history')
def repeat(message):
    bot.send_message(message.message.chat.id, message.data,
        reply_markup=kbd_start)
    db.set_branch(message.message.chat.id, 'state', 'home')





@bot.message_handler(func=lambda message:
                     message.text == '\U0001F6E0 Настройки')
def settings(message):
    on_development_stage(message)


@bot.message_handler(func=lambda message:
                     message.text == '\U0001F198 Помощь')
def help_message(message):
    bot.send_message(message.chat.id, '''Узнай актуальное расписание \
электричек!
Время указано в часовом поясе Москвы
Исходный код бота: https://github.com/meugr/suburban_dogs_bot
''')


@bot.message_handler(func=lambda message:
                     message.text == '\U0001F519 Отмена' or
                     message.text == '/cancel')
def cancel_search(message):
    print(db.get_branch(message.chat.id, 'search'))
    db.set_branch(message.chat.id, 'search', {})
    db.set_branch(message.chat.id, 'state', 'home')
    bot.send_message(message.chat.id, 'Выбор станции отменен',
                     reply_markup=kbd_start)


@bot.message_handler(func=lambda message:
                     message.text == '\U0001F50D Поиск расписаний' and
                     db.get_branch(message.chat.id, 'state') == 'home')
def get_departure(message):
    db.set_branch(message.chat.id, 'state', 'search')
    bot.send_message(message.chat.id,
                     'Введите станцию отправления\nДля отмены нажмите /cancel',
                     reply_markup=remove_markup)


# старт FSM
@bot.message_handler(func=lambda message:
                     db.get_branch(message.chat.id, 'state') == 'search')
def search(message):
    if len(db.get_branch(message.chat.id, 'search')) == 0:
        db.set_branch(message.chat.id, 'search',
                      {'departure': message.text})
        bot.send_message(message.chat.id,
                         'Введите станцию прибытия\nДля отмены нажмите \
/cancel')
        print(db.get_branch(message.chat.id, 'search'))

    elif len(db.get_branch(message.chat.id, 'search')) == 1:
        update_search = db.get_branch(message.chat.id, 'search')
        update_search['arrival'] = message.text
        db.set_branch(message.chat.id, 'search', update_search)
        bot.send_message(
            message.chat.id, 'Выберите дату', reply_markup=kbd_choose_date)
        print(db.get_branch(message.chat.id, 'search'))

    elif len(db.get_branch(message.chat.id, 'search')) == 2:
        update_search = db.get_branch(message.chat.id, 'search')
        update_search['date'] = message.text
        db.set_branch(message.chat.id, 'search', update_search)
        bot.send_message(
            message.chat.id, 'Загружаю расписание...',
            reply_markup=remove_markup)

        data = db.get_branch(message.chat.id, 'search')
        try:
            # отправление и прибытие с регионом и нитью
            d, a = s.get_info_with_db(data)
            tzone = pytz.timezone('Europe/Moscow')  # брать tz из настроек
            t_now = parser.get_current_time(tzone)  # юзера
    # Временная мера, написать обработчик некорректного ввода и обработчик
    # при нахождении нескольких станций в БД
            # Получаю инфу о рейсах
            trains = YaAPI.send_request(
                (d[0], a[0]), data['date'], t_now)['segments']

        except (IndexError, TypeError):
            bot.send_message(
                message.chat.id, 'Введите корректное название станций',
                reply_markup=kbd_start)
            cancel_search(message)
            return
        except KeyError:
            bot.send_message(
                message.chat.id,
                '''Извините, для этой станции расписание пока недоступно.
Попробуйте ввести ТОЧНОЕ название станций.''', reply_markup=kbd_start)
            cancel_search(message)
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
                    parse_mode='markdown', reply_markup=kbd_start)
        if counter == config.HOW_MUCH:  # счетчик сообщений не поменялся
            bot.send_message(
                message.chat.id, 'На сегодня электричек нет',
                reply_markup=kbd_start)

        # Сброс состояния
        db.set_branch(message.chat.id, 'search', {})
        db.set_branch(message.chat.id, 'state', 'home')
        # обновление 5 последних запросов
        print()
        last_response = s.get_stations_name(d[0], a[0])
        db.update_last_five(message.chat.id, last_response)


if __name__ == '__main__':
    bot.polling(none_stop=True)
