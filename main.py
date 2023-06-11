import json


def load_authorized_users(file_path):
    try:
        with open(file_path, 'r') as file:
            authorized_users = json.load(file)
    except FileNotFoundError:
        authorized_users = {}
    return authorized_users

chat_id = 988966234

authorized_users = load_authorized_users('GeOnline/authorized_users.json')
if authorized_users[chat_id] == 1:
    print("Yes")