import requests
from bs4 import BeautifulSoup as bs
import json
import dateutil.parser
import datetime as dt
import pytz


def create_link():
    """Создаем ссылку на яндекс.расписания из пользовательского ввода"""
    from_name = input('Откуда: ')
    to_name = input('Куда: ')
    when = 'сегодня'
    data = (from_name, to_name, when)
    link = 'https://rasp.yandex.ru/search/suburban/?fromName={}&toName={}\
    &when={}'.format(*data)
    return link


def parse_main_json(link):
    """Получаем с сайта яндекс.расписаний json, обрабатываем его
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


def print_info_about_train(trains):
    """Распечатывает блок с информацией о рейсе"""
    current_time = pytz.utc.localize(dt.datetime.utcnow())
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
            print('========\n{}\nОтправление {}\nПрибытие {}\nЧерез {}\
 минут\nОстановки - {}\nЦена билета {} руб'.format(
                train['route'],
                departure,
                arrival,
                departure_in,
                train['stops'],
                train['price']))


def test_main():
    trains = []
    link = create_link()
    try:
        data_list = parse_main_json(link)
    except IndexError:
        print('Введите корректное название станций.')
        exit()
    for train in data_list:
        trains.append(get_data(train))
    print_info_about_train(trains)


test_main()
