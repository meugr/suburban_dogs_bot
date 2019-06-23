import config
import requests
import datetime as dt


class YaAPI:
    def __init__(self, token):
        pass

    def send_request(data, date, time):
        '''Посылаем яндексу запрос с нужными станциями и датой'''
        if date == 'Завтра':
            time += dt.timedelta(days=1)
        time = time.strftime('%Y-%m-%d')
        info = [data[0], data[1], time]
        url = config.LINK.format(*info, config.YA_TOKEN)
        ya_response = requests.get(url)
        return ya_response.json()
