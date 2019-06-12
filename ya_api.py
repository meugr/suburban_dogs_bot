import config
import requests


class YaAPI:
    def __init__(self, token):
        pass

    def send_request(data, time):
        '''Посылаем яндексу запрос с нужными станциями и датой'''
        time = time.strftime('%Y-%m-%d')
        info = [data[0], data[1], time]
        url = config.LINK.format(*info, config.YA_TOKEN)
        ya_response = requests.get(url)
        return ya_response.json()
