import telebot
from telebot import types

from little_db import UserData
from little_db import StationInfo
from machine_parts import Engine
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


def choise_one_station(message, stations, point):
    """Выбор юзером одной станции из списка"""
    print(f'###DEBUG### bot.py НЕСКОЛЬКО СТАНЦИЙ {point}')
    word_point = 'отправления' if point == 'd' else 'прибытия'
    kbd_list_sts = types.InlineKeyboardMarkup()
    for code in stations:
        for r in s.db:
            name = s.db[r].get(code, {}).get('name', None)
            if name:
                break
        kbd_list_sts.add(
            types.InlineKeyboardButton(text=str(name),
                                       callback_data=point + code))
    bot.send_message(
        message.chat.id, f'Уточните станцию {word_point}',
        reply_markup=kbd_list_sts)


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
    kbd_last_five = types.InlineKeyboardMarkup()
    for b in last:
        kbd_last_five.add(
            types.InlineKeyboardButton(text=str(b[0]),
                                       callback_data=' '.join(b[1:])))
    bot.send_message(message.chat.id, 'Открываем архивы...',
                     reply_markup=kbd_cancel)
    bot.send_message(
        message.chat.id, 'Выберите недавний маршрут или нажмите отмена',
        reply_markup=kbd_last_five)


@bot.callback_query_handler(func=lambda message:
                            db.get_branch(message.message.chat.id, 'state') ==
                            'history')
def search_from_last(message):
    print('###DEBUG### bot.py', message.data)
    d, a = message.data.split()
    date = 'Сегодня'
    Engine.search(message.message, db, d, a, date, bot, kbd_start)
    db.set_branch(message.message.chat.id, 'state', 'home')


@bot.callback_query_handler(func=lambda message:
                            db.get_branch(message.message.chat.id, 'state') ==
                            'search')
def set_chosen_station(message):
    update_branch = db.get_branch(message.message.chat.id, 'search')
    if message.data[0] == 'd':
        update_branch['codes_found'][0] = [message.data[1:]]
    elif message.data[0] == 'a':
        update_branch['codes_found'][1] = [message.data[1:]]
    db.set_branch(message.message.chat.id, 'search', update_branch)
    search(message.message)


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
    Engine.cancel_search(message, db)
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
        # отправление и прибытие с регионом и нитью
        d, a = s.get_info_with_db(update_search)
        if d == [] or a == []:
            bot.send_message(
                message.chat.id, 'Введите корректное название станций',
                reply_markup=kbd_start)
            Engine.cancel_search(message, db)
            return
        update_search['codes_found'] = (d, a)
        db.set_branch(message.chat.id, 'search', update_search)

    if len(db.get_branch(message.chat.id, 'search')) == 4:
        d, a = db.get_branch(message.chat.id, 'search')['codes_found']

        if len(d) > 1:
            choise_one_station(message, d, point='d')
            return

        elif len(a) > 1:
            choise_one_station(message, a, point='a')
            return

        bot.send_message(
            message.chat.id, 'Загружаю расписание...',
            reply_markup=remove_markup)
        date = db.get_branch(message.chat.id, 'search')['date']
        search_result = Engine.search(
            message, db, d[0], a[0], date, bot, kbd_start)

        # Сброс состояния
        db.set_branch(message.chat.id, 'search', {})
        db.set_branch(message.chat.id, 'state', 'home')
        # обновление 5 последних запросов
        print()
        if search_result:
            d, a = search_result  # инфа об отправлении и прибытии
            last_response = s.get_stations_name(d, a)
            db.update_last_five(message.chat.id, last_response)


if __name__ == '__main__':
    bot.polling(none_stop=True)
