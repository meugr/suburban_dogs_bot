import json


def create_new_user(chat_id):
    with open('info.json', 'r') as f:
        db = json.load(f)
    with open('info.json', 'w') as f:
        db[str(chat_id)] = {'settings': [], 'current_state': [None]}
        json.dump(db, f)


def reset_info(chat_id):
    with open('info.json', 'r') as f:
        db = json.load(f)
    with open('info.json', 'w') as f:
        db[str(chat_id)]['current_state'] = [None]
        json.dump(db, f)


def set_empty_info(chat_id):
    with open('info.json', 'r') as f:
        db = json.load(f)
    with open('info.json', 'w') as f:
        db[str(chat_id)]['current_state'] = []
        json.dump(db, f)


def append_info(chat_id, user_input):
    with open('info.json', 'r') as f:
        db = json.load(f)
    with open('info.json', 'w') as f:
        db[str(chat_id)]['current_state'].append(user_input)
        json.dump(db, f)


def get_info(chat_id):
    with open('info.json', 'r') as f:
        db = json.load(f)
    try:
        return db[str(chat_id)]['current_state']
    except KeyError:
        create_new_user(chat_id)
        return db[str(chat_id)]['current_state']
