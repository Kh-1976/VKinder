import json
import os
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from Conditions_user import conditions
from Search_users import func
from Photos import VkUserPhotos
import time


token_group = 'token_group'
token_vk = ''
user_id = ''
vk_session = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk_session)

id_found_user = ''
repeat_users = []
db_users = {}


def check_token(token):
    vk_photo = VkUserPhotos(owner_id_vk='552934290', token_vk=token)
    try:
        vk_photo.photos()
        result = token
    except KeyError:
        result = 'Токен невалидный'
    return result


def input_token():
    global token_vk
    result = input('Введите валидный Token VK: ')
    if check_token(result) == 'Токен невалидный':
        input_token()
    else:
        token_vk = result
    return  token_vk


input_token()
print('Чат-бот включен')


def top3_user_photos(lst_id):
    lst_top_photos = []
    cnt = 0
    for i in lst_id:
        cnt += 1
        if cnt == 500:
            time.sleep(0.5)
            cnt = 0
        if i not in repeat_users:
            vk_photo = VkUserPhotos(owner_id_vk=str(i), token_vk=token_vk)
            try:
                lst_top_photos.append(vk_photo.user_top3_photos(vk_photo.photos()))
            except KeyError:
                continue

    max_, lst_result = 0, []
    for i in lst_top_photos:
        try:
            if i[0][2] > max_:
                max_ = i[0][2]
                lst_result = i
        except IndexError:
            continue

    repeat_users.append(lst_result[0][0])
    return lst_result


def write_msg(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message,
                                        'random_id': randrange(10 ** 7)})


def send_photo(user_id, url):
    vk_session.method('messages.send', {'user_id': user_id, 'attachment': url,
                                        'random_id': randrange(10 ** 7)})


def delete_repeats(lst_id):
    for i in repeat_users:
        try:
            lst_id.remove(i)
        except ValueError:
            continue
    return lst_id


def send_photos_in_chat(owner_id):
    global id_found_user
    cnt = 0
    lst_id = func(token_group, owner_id, token_vk)
    for id in top3_user_photos(lst_id):
        cnt += 1
        id_found_user = id[0]
        send_photo(event.user_id, f'photo{id[0]}_{id[1]}')
        write_msg(event.user_id, f'Топ-{cnt} фото пользователя  {id[0]}, лайков и комментов {id[2]}')


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                write_msg(event.user_id, f"Привет, {event.user_id}. \nВведите ID пользователя VK")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                id = request
                if request.isdigit() and conditions(token_group, id)[0] != 0 \
                        and conditions(token_group, id)[1] != 0 and conditions(token_group, id)[2] != 0:
                    repeat_users.append(int(id))
                    write_msg(event.user_id, "Подождите..")
                    send_photos_in_chat(f'{id}')

                    write_msg(event.user_id, f"https://vk.com/id{id_found_user}")
                    if id not in db_users:
                        db_users[id] = [id_found_user]
                    else:
                        db_users[id].append(id_found_user)
                    with open(os.path.join(os.getcwd(), 'log.json'), 'a', encoding="utf-8") as f:
                        json.dump(db_users, f)
                else:
                    write_msg(event.user_id, "Не хватает данных. \nВведите ID пользователя VK,"
                                             " с указнымми данными: \nВозраст, Пол, Город, Семейное положение")
        user_id = event.user_id

