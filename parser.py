import pytz
import datetime as dt
import dateutil.parser


def get_current_time(user_tz):
    return pytz.utc.localize(dt.datetime.utcnow()).astimezone(user_tz)


def hourse_minutes(delta):
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
    if train['thread']['express_type']:
        res['is_express'] = chr(128648)
    else:
        res['is_express'] = chr(128642)

    res['departure'] = dateutil.parser.parse(train['departure']).strftime(
        '%H:%M')
    res['arrival'] = dateutil.parser.parse(train['arrival']).strftime(
        '%H:%M')
    res['in_way'] = hourse_minutes(dateutil.parser.parse(
        train['arrival']) - dateutil.parser.parse(train['departure']))
    res['departure_in'] = hourse_minutes(delta)

    res['stops'] = train['stops']
    res['price'] = train['tickets_info']['places'][0]['price']['whole']
    return res


def message_template(data):
    msg = '''
*Через {departure_in} мин.*
{is_express} {thread}
Отправление {departure}
Прибытие {arrival}
В пути {in_way} мин.
Остановки - {stops}
Цена билета {price} руб'''.format(**data)
    return msg
