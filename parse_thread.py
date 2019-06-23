import json
import config
import requests
import copy


def threads(key):
    """ Получаем список всех ниток на станции"""
    res = set()
    url = 'https://api.rasp.yandex.net/v3.0/schedule/?apikey={}&station={}&limit=1000&transport_types=suburban'.format(config.YA_TOKEN, key)
    try:
        schedules = requests.get(url).json()['schedule']
    except KeyError:
        return [None]
    for train in schedules:
        d = train['thread']['uid'].split('_')[2]
        res.add(d)
    return list(res)


def update_db():
    """Перезаписываем базу данных
    добавляя актуальные нитки для каждой станции"""
    with open('stations_db.json') as f:
        db = json.load(f)
    db_copy = copy.deepcopy(db)
    for reg in db:
        for key in db[reg]:
            print(key)
            db_copy[reg]['thread'] = threads(key)
            print(db_copy[reg]['thread'])
            print('++++++++++++++++')
    with open('stations_db.json', 'w') as f:
        json.dump(db_copy, f)


def create_db():
    try:
        with open('stations_db.json') as f:
            db = json.load(f)
        res = {}
        for reg in db:
            res[reg] = {}
            for key in db[reg]:
                res[reg][key] = {'name': db[reg][key], 'threads': []}
                print(key)
                res[reg][key]['threads'].extend(threads(key))
                print(res[reg][key]['threads'])
                print('++++++++++++++++')

    finally:
        with open('stations_db_new.json', 'w') as f:
            json.dump(res, f)


create_db()
