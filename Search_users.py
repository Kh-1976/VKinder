from Conditions_user import conditions
import vk_api
from vk_api import VkTools

lst_find_users, lst_user_conditions = [], []


def func(token_group, user_id, token_vk):
    vk = vk_api.VkApi(token=token_vk)
    api = vk.get_api()
    lst_user_conditions = conditions(token_group, user_id)

    rs = VkTools(api).get_all(
        method='users.search',
        max_count=1000,
        values={
            'age_from': int(lst_user_conditions[0])-3,
            'age_to': int(lst_user_conditions[0])+3,
            'sex': int(lst_user_conditions[1]),
            'city': int(lst_user_conditions[2]),
            'fields': 'relation, sex, city, bdate',
        },
    )
    for i in rs['items']:
        try:
            if i['city']['id'] == int(lst_user_conditions[2]) \
                    and i['relation'] == int(lst_user_conditions[3]):
                lst_find_users.append(i['id'])
        except KeyError:
            continue

    return lst_find_users
