import config
import requests

class YaAPI:
    def __init__(self, token):
        pass

    def send_request(data):
        '''Посылаем яндексу запрос с нужными станциями и датой'''
        info = [data[0], data[1]]
        url = config.LINK.format(*info, config.YA_TOKEN)
        ya_response = requests.get(url)
        return ya_response.json()
