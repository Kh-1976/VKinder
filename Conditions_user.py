import requests
from datetime import datetime

url_users = 'https://api.vk.com/method/users.get'
current_year = datetime.now().year
result = []


def conditions(token_group, user_id):
    result = []
    params = {'user_id': user_id, 'access_token': token_group, 'v': '5.52', 'fields':'sex,city,bdate,relation'}
    res = requests.get(url_users, params=params)
    if res.json()['response'][0]['first_name'] != 'DELETED' and 'deactivated' not in res.json()['response'][0] \
            and 'city' in res.json()['response'][0] and 'bdate' in res.json()['response'][0] and 'relation' in res.json()['response'][0]:
        try:
            age = current_year - int(res.json()['response'][0]['bdate'][-4:])
        except ValueError:
            age = 0
        sex = res.json()['response'][0]['sex']
        city = res.json()['response'][0]['city']['id']
        relation = res.json()['response'][0]['relation']
        result = [age, sex, city, relation]
    else:
        result = [0, 0, 0, 0]
    return result
