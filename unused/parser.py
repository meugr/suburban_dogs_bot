import requests
from bs4 import BeautifulSoup as bs
import json
import dateutil.parser
import datetime as dt
import pytz
import config


def create_link(data):
    """Создаем ссылку на сайт с расписаниями из пользовательского ввода"""
    link = config.LINK.format(*data)
    return link


def parse_main_json(link):
    """Получаем с сайта с расписаниями json, обрабатываем его
    и возвращаем список словарей с данными о сегодняшних рейсах"""
    p = requests.get(link)
    soup = bs(p.text, "html.parser")
    data = soup.find_all('script')[3]  # парсим нужный тег
    data = str(data).split('window.INITIAL_STATE = ')[1]  # отрезаем 1 часть
    data = data.split(';\n')
    data = data[0]
    data = json.loads(data)
    data_list = data['search']['segments']  # пофиксить на get()
    return data_list  # вернули список словарей с данными о рейсах


def get_data(train):
    """Принимаем на вход словарь, с данными о конкретном рейсе -- возвращаем
    словарь нужных данных для отображения"""
    data = {}

    data['route'] = train.get('title')
    data['stops'] = train.get('stops')

    departure = train.get('departure')
    data['departure'] = dateutil.parser.parse(departure)  # UTC

    arrival = train.get('arrival')
    data['arrival'] = dateutil.parser.parse(arrival)  # UTC

    data['is_express'] = train.get('thread', {}).get('isExpress')
    data['price'] = (
        train.get('tariffs', {}).
        get('suburbanCategories', {}).
        get('usual', [None])[0].
        get('price', {}).
        get('value'))
    return data


def info_about_trains(trains):
    """Распечатывает блок с информацией о рейсе"""
    current_time = pytz.utc.localize(dt.datetime.utcnow())
    res = []
    timez = pytz.timezone('Europe/Moscow')
    for train in trains:
        delta = train['departure'] - current_time
        if delta.days >= 0:
            departure = train['departure'].astimezone(timez).strftime('%H:%M')
            arrival = train['arrival'].astimezone(timez).strftime('%H:%M')
            departure_in = delta.seconds // 60
            if departure_in > 59:
                departure_in = '{} часов {}'.format(
                    departure_in // 60,
                    departure_in % 60)
            res.append('========\n{}\nОтправление {}\nПрибытие {}\nЧерез {}\
 минут\nОстановки - {}\nЦена билета {} руб'.format(
                train['route'],
                departure,
                arrival,
                departure_in,
                train['stops'],
                train['price']))
    return res


def test_main(user_input):
    trains = []
    res = []
    link = create_link(user_input)
    try:
        data_list = parse_main_json(link)
    except IndexError:
        return ['Введите корректное название станций.']
        exit()
    for train in data_list:
        trains.append(get_data(train))
    res = [*info_about_trains(trains)][:3]
    return res
