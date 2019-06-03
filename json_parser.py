import json

res = []

with open('res.json') as f:
    data = json.load(f)

def first(data):
    res = []
    for r in data['regions']:
        ST = {}
        for n in r['settlements']:
            for s in n['stations']:
                if s['transport_type'] == 'train':
                    ST[s['codes']['yandex_code']] = s['title']
        temp = {'reg': r['title'], 'stations': ST}
        res.append(temp)
    return res


def second(data):
    res = {}
    for r in data['regions']:
        ST = {}
        for n in r['settlements']:
            for s in n['stations']:
                if s['transport_type'] == 'train':
                    try:
                        print(ST[s['title']], s['title'])
                    except:
                        ST[s['title']] = s['codes']['yandex_code']
        res[r['title']] = ST
    return res




print(second(data)['Брянская область'])
