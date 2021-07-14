import sqlalchemy
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from Conditions_user import conditions
from Search_users import func
from Photos import VkUserPhotos
import time


engine = sqlalchemy.create_engine('postgresql://postgres:1234@localhost:5432/Vkinder_db')
connection = engine.connect()

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
    return token_vk


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


def send_photo(user_id, lst_iduser_idphoto):
    vk_session.method('messages.send', {'user_id': user_id,
                                        'random_id': randrange(10 ** 7), 'attachment': ','.join(lst_iduser_idphoto)})


def delete_repeats(lst_id):
    for i in repeat_users:
        try:
            lst_id.remove(i)
        except ValueError:
            continue
    return lst_id


def send_photos_in_chat(owner_id):
    global id_found_user
    lst_iduser_idphoto = []
    lst_id = func(token_group, owner_id, token_vk)

    try:
        for id in top3_user_photos(lst_id):
            id_found_user = id[0]
            lst_iduser_idphoto.append(f'photo{id_found_user}_{id[1]}')
        send_photo(event.user_id, lst_iduser_idphoto)
    except IndexError:
        lst_id = [owner_id]
        for id in top3_user_photos(lst_id):
            id_found_user = id[0]
            lst_iduser_idphoto.append(f'photo{id_found_user}_{id[1]}')
        send_photo(event.user_id, lst_iduser_idphoto)
        write_msg(event.user_id, f'Пользователей не найденно')


def Add_user_to_table(user):
    ins = connection.execute(f"""INSERT INTO uservk(user_vk) VALUES({user}) ON CONFLICT (user_vk) DO NOTHING;""")
    #return ins


def Add_founduser_to_table(found_user):
    ins = connection.execute(f"""INSERT INTO found_usersvk(found_user)
            VALUES({found_user})  ON CONFLICT (found_user) DO NOTHING;""")
    #return ins


def Add_user_and_founduser_to_table(user, found_user):
    ins = connection.execute(f"""INSERT INTO id_user_id_found_users(user_id, found_user_id)
            VALUES({user}, {found_user});""")
    #return ins


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                write_msg(event.user_id, f"Привет, {event.user_id}. \nВведите ID пользователя VK")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                if request != '0' and request.isdigit() and conditions(token_group, request)[0] != 0 \
                        and conditions(token_group, request)[1] != 0 and conditions(token_group, request)[2] != 0:
                    repeat_users.append(int(request))

                    write_msg(event.user_id, "Подождите..")

                    send_photos_in_chat(request)

                    write_msg(event.user_id, f"https://vk.com/id{id_found_user}")
                    if request not in db_users:
                        db_users[request] = [id_found_user]
                    else:
                        db_users[request].append(id_found_user)

                    Add_user_to_table(request)
                    Add_founduser_to_table(id_found_user)
                    Add_user_and_founduser_to_table(request, id_found_user)
                else:
                    write_msg(event.user_id, "Не хватает данных. \nВведите ID пользователя VK,"
                                             " с указнымми данными: \nВозраст, Пол, Город, Семейное положение")
        user_id = event.user_id

