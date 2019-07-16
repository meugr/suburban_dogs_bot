import pymongo
import json
from collections import deque


class UserData:
    """
    Класс для работы с пользовательскими данными из mongoDB
    """

    def __init__(self):
        self.db = pymongo.MongoClient().suburban_dogs.user_data

    def create_new_user(self, chat_id):
        """Создаем нового юзера в mongoDB"""
        self.db.insert_one({
            'id': chat_id,
            'state': 'home',  # (home, search, settings, history)
            'search': {},
            'settings': {},
            'history': ()})

    def get_branch(self, chat_id, branch):
        """Получаем ветку из БД юзеров"""
        return self.db.find_one({'id': chat_id})[branch]

    def set_branch(self, chat_id, branch, changes):
        """Отправляет изменения ветки в mongoDB"""
        self.db.update_one(
            {'id': chat_id},
            {'$set': {branch: changes}})

    def update_last_five(self, chat_id, trains):
        """Обновляет список последних 5 запросов юзера"""
        last = self.get_branch(chat_id, 'history')
        last = deque(last, maxlen=5)
        if list(trains) not in last:
            last.appendleft(trains)
            self.set_branch(chat_id, 'history', tuple(last))


class StationInfo:
    """
    Класс для работы с json базой электричек
    """

    def __init__(self, path_to_db):
        with open(path_to_db) as f:
            self.db = json.load(f)

    def get_info_with_db(self, data):
        '''Возвращает списки подходящих станций отправления и прибытия
        в формате (station_id, region_name, threads)'''
        departure = []
        arrival = []
        res_d = set()
        res_a = set()
        for r in self.db:
            for s in self.db[r]:
                if (data['departure'].lower() in self.db[r][s]['name'].lower()
                    and self.db[r][s]['threads'] != [None]):
                    departure.append((s, r, self.db[r][s]['threads']))
                if (data['arrival'].lower() in self.db[r][s]['name'].lower()
                    and self.db[r][s]['threads'] != [None]):
                    arrival.append((s, r, self.db[r][s]['threads']))
        print(arrival, departure, sep='\n++++++\n')
        for d in departure:
            for a in arrival:
                if len(set(d[2]) & set(a[2])):  # если есть общие нитки
                    res_d.add(d[0])
                    res_a.add(a[0])
        return list(res_d), list(res_a)

    def get_stations_name(self, departure_id, arrival_id):
        """Возвращает строку станция отправления — станция прибытия и 
        коды станции отправления и прибытия"""
        departure = ''
        arrival = ''
        for r in self.db:
            tmp = self.db[r].get(departure_id, {}).get('name')
            if tmp:
                departure = tmp
            tmp = self.db[r].get(arrival_id, {}).get('name')
            if tmp:
                arrival = tmp
        return f'{departure} — {arrival}', departure_id, arrival_id

    def search_engine():
        '''С помощью модуля ищем расстояние Левенштейна'''
        pass
