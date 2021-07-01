import requests
from operator import itemgetter


class VkUserPhotos:
    url = 'https://api.vk.com/method/photos.get'

    def __init__(self, owner_id_vk, token_vk):
        self.params = {
            'owner_id': owner_id_vk,
            'access_token': token_vk,
            'v': '5.52',
            'album_id': 'profile',
            'extended': 1
        }
        self.lst_top_photos = []
        self.lst_user_photos = []

    def photos(self):
        res = requests.get(self.url, params=self.params)
        return res.json()['response']['items']

    def user_top3_photos(self, lst_photos):
        for i in lst_photos:
            try:
                self.lst_user_photos.append([i['owner_id'], i['id'], i['comments']['count'] + i['likes']['count']])
            except KeyError:
                continue
        self.lst_user_photos.sort(key=itemgetter(2), reverse=True)
        return self.lst_user_photos[:3]


