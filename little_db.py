import config
from rejson import Client, Path
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
        return self.db.find_one({'id': chat_id})[branch]

    def set_branch(self, chat_id, branch, changes):
        """Отправляет изменения ветки в mongoDB"""
        self.db.update_one(
            {'id': chat_id},
            {'$set': {branch: changes}})

    def change_current_branch(self, chat_id, branch):
        """Задаем текущую ветку в mongoDB
        maybe unused"""
        self.db.update_one({'id': chat_id}, {'$set': {'state': branch}})

    def reset_search_info(self, chat_id):
        '''Отмена опроса юзера и удаление записи о начале поиска из redis'''
        self.conn.jsonset(chat_id, Path(f'.{chat_id}.search'), {})
        self.change_current_branch(chat_id, 'home')

    def get_search_info(self, chat_id):
        '''Получаем весь юзерввод из redis'''
        return self.conn.jsonget(chat_id, Path(f'.{chat_id}.search'))









    # def start_search(self, chat_id):
    #     '''Создает в redis запись, тем самым начиная опрос юзера'''
    #     self.conn.delete(chat_id)
    #     # self.conn.hmset(chat_id, {'search': 'True'})


    def append_info(self, chat_id, step, user_input):
        '''Добавление в redis пользовательского ввода'''
        return self.conn.hset(chat_id, step, user_input)


class UserSettings(UserData):
    pass


class UserHistory(UserData):
    pass


class StationInfo:
    """
    Класс для работы с json базой электричек
    """
    def __init__(self, path_to_db):
        with open(path_to_db) as f:
            self.db = json.load(f)

    def create_new_user(chat_id):
        pass

    def get_info_with_db(self, data):
        '''Возвращает списки подходящих станций отправления и прибытия
        в формате (station_id, region_name, threads)'''
        departure = []
        arrival = []
        for r in self.db:
            for s in self.db[r]:
                if self.db[r][s]['name'].lower() in data['departure'].lower():
                    departure.append((s, r, self.db[r][s]['threads']))
        for r in self.db:
            for s in self.db[r]:
                if self.db[r][s]['name'].lower() in data['arrival'].lower():
                    arrival.append((s, r, self.db[r][s]['threads']))
        # ДОБАВИТЬ ТУТ СТАВНЕНИЕ СТАНЦИЙ ПО НИТКАМ, ВЕРНУТЬ ТОЛЬКО 
        # СТАНЦИИ ГДЕ ПЕРЕСЕКАЕТСЯ ХОТЯ БЫ 1 НИТКА
        # set(a) & set(b)
        for d in departure:
            for a in arrival:
                if len(set(d[2]) & set(a[2])):
                    return departure[0][:-1], arrival[0][:-1]






    def search_engine():
        '''С помощью модуля ищем расстояние Левенштейна'''
        pass
