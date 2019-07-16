import pytz
import datetime as dt
import dateutil.parser
from ya_api import YaAPI
import config




class Parser:
    def get_current_time(user_tz):
        return pytz.utc.localize(dt.datetime.utcnow()).astimezone(user_tz)

    def hours_minutes(delta):
        departure_in = delta.seconds // 60
        if departure_in > 59:
            departure_in = '{} ч. {}'.format(
                departure_in // 60,
                departure_in % 60)
        return departure_in

    def info_about_train(train, t_now, delta):
        '''Принимаем словарь c конкретным рейсом и текущее время юзера'''
        res = {}
        res['thread'] = train['thread']['title']
        if train['thread']['express_type']:  # выбор смайлика типа поезда
            res['is_express'] = '\U0001F688'
        else:
            res['is_express'] = '\U0001F682'

        res['departure'] = dateutil.parser.parse(train['departure']).strftime(
            '%H:%M')
        res['arrival'] = dateutil.parser.parse(train['arrival']).strftime(
            '%H:%M')
        res['in_way'] = Parser.hours_minutes(dateutil.parser.parse(
            train['arrival']) - dateutil.parser.parse(train['departure']))
        res['departure_in'] = Parser.hours_minutes(delta)

        res['stops'] = train['stops']
        res['price'] = train['tickets_info']['places'][0]['price']['whole']
        return res

    def message_template(data):
        """Заполняет шаблон сообщения с информацией о рейсе"""
        msg = '''
*Через {departure_in} мин.*
{is_express} {thread}
Отправление {departure}
Прибытие {arrival}
В пути {in_way} мин.
Остановки - {stops}
Цена билета {price} руб'''.format(**data)
        return msg


class SearchEngine:
    def cancel_search(message, db):
        """Отмена ввода и возврат состояния на домашний экран"""
        print(db.get_branch(message.chat.id, 'search'))
        db.set_branch(message.chat.id, 'search', {})
        db.set_branch(message.chat.id, 'state', 'home')

    def search(message, db, d, a, date, bot, kbd_start):
        """Обработка информации введенной юзером
        db - обьект little_db.UserData, d - код станции отправления,
        a - код станции прибытия, date - дата, bot - объект бота,
        kbd_start - клавиатура стартового экрана"""
        tzone = pytz.timezone('Europe/Moscow')  # брать tz из настроек
        t_now = Parser.get_current_time(tzone)  # юзера
    # Временная мера, написать обработчик некорректного ввода и обработчик
    # при нахождении нескольких станций в БД
            # Получаю инфу о рейсах
            # Добавить интерфейс выбора конкретной станции из d, a
        try:
            trains = YaAPI.send_request(
                (d[0], a[0]), date, t_now)['segments']
        except KeyError:
            bot.send_message(
                message.chat.id,
                '''Извините, для этой станции расписание пока недоступно.
Попробуйте ввести ТОЧНОЕ название станций.''', reply_markup=kbd_start)
            SearchEngine.cancel_search(message, db)
            return
        counter = config.HOW_MUCH
        for train in trains:  # пропускаем только неушедшие рейсы
            delta = dateutil.parser.parse(
                train['departure']).astimezone(tzone) - t_now
            if delta.days >= 0 and counter:  # по дефолту вывод 5 рейсов
                counter -= 1
                msg_dict = Parser.info_about_train(train, t_now, delta)
                bot.send_message(
                    message.chat.id, Parser.message_template(msg_dict),
                    parse_mode='markdown', reply_markup=kbd_start)
        if counter == config.HOW_MUCH:  # счетчик сообщений не поменялся
            bot.send_message(
                message.chat.id, 'На сегодня электричек нет',
                reply_markup=kbd_start)
        print('###DEBUG### parser.py', d, a, sep='\n')
        return d[0], a[0]
