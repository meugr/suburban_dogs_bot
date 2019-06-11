import config
import redis
import json


class UserState():
    '''
    Функции для работы с redis и управлением состоянием пользователя (FSM)
    '''

    def __init__(self):
        self.conn = redis.Redis(db=1, charset='utf-8', decode_responses=True)

    def start_search(self, chat_id):
        '''Создает в redis запись, тем самым начиная опрос юзера'''
        self.conn.delete(chat_id)
        self.conn.hmset(chat_id, {'search': 'True'})

    def reset_info(self, chat_id):
        '''Отмена опроса юзера и удаление записи о начале поиска из redis'''
        self.conn.delete(chat_id)

    def append_info(self, chat_id, step, user_input):
        '''Добавление в redis пользовательского ввода'''
        return self.conn.hset(chat_id, step, user_input)

    def get_info(self, chat_id):
        '''Получаем весь юзерввод из redis'''
        return self.conn.hgetall(chat_id)


class StationInfo:
    def __init__(self, path_to_db):
        with open(path_to_db) as f:
            self.db = json.load(f)

    def create_new_user(chat_id):
        pass

    def get_info_with_db(self, data):
        '''Возвращает списки подходящих станций отправления и прибытия
        в формате (station_id, region_name)'''
        departure = []
        arrival = []
        for r in self.db:
            for s in self.db[r]:
                if self.db[r][s].lower() == data['departure'].lower():
                    departure.append((s, r))
        for r in self.db:
            for s in self.db[r]:
                if self.db[r][s].lower() == data['arrival'].lower():
                    arrival.append((s, r))
        return departure, arrival





    def search_engine():
        '''С помощью модуля ищем расстояние Левенштейна'''
        pass
