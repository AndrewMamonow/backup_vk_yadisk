import requests
import time

class Vk:
# Класс подключения к ВК и получения списка файлов
    def __init__(self, access_token: str, user_id: str, version=5.199):
        self.base_address = 'https://api.vk.com/method'
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {
                    'access_token': self.token,
                    'v': self.version
                    }
        
    def users_info(self):
    # Получение информации о статусе пользователя ВК
        url = f'{self.base_address}/users.get'
        params = {
                'user_ids': self.id
                }
        response = requests.get(url, params={**self.params, **params})
        return response.json()    

    def get_profile_photos(self, album_id, count=''):
    # Получение фотографий пользователя ВК из альбома
        url = f'{self.base_address}/photos.get'
        params = {
                'owner_id' : self.id,
                'album_id' : album_id,
                'count' : count,
                'extended' : '1'
                }
        response = requests.get(url, params = {**self.params, **params})
        return response.json()
        
    def get_file_album(self, album_id: str):
    # Выбор и получение фотографий из альбома пользователя ВК
        photos_list = []
        photos_album = self.get_profile_photos(album_id)
        if  not 'error' in photos_album:
            photos_count = photos_album['response']['count']
            if photos_count == 0:
                print(f'В альбоме {album_id} нет файлов. Выберите другой альбом')
            else:
                photos_get = input(f'В альбоме {photos_count} файлов. Сколько сохранить на диск? (по умолчанию 5)')
                if photos_get == '':
                    photos_get = 5
                if int(photos_get) > int(photos_count):
                    print(f'Введенное количество {photos_get} больше, чем файлов в альбоме.')
                    if input(f'Сохранить все {photos_count} файлов? Y/N').lower() == 'y':
                        photos_get = photos_count 
                    else:
                        photos_get = 5
                print(f'Будет сохранено {photos_get} файлов.')
                photos_album = self.get_profile_photos(album_id, photos_get)
                photos_list = self._photo_sort(photos_album)
        return photos_list

    def _photo_sort(self, photos_album: dict):
    # Выбор файлов с максимальным разрешением    
        photos_list = []
        for photos in photos_album['response']['items']:
            photos_dict = {
                        'date_photo' : time.strftime('%d%m%Y', time.gmtime(photos['date'])),
                        'likes' : photos['likes']['count'],
                        'filename' : f'{photos['likes']['count']}.jpg'
                        }
            size_max = 0
            for photo in photos['sizes']:
                if photo['height'] * photo['width'] > size_max:
                    photos_dict['url'] = photo['url']
                    photos_dict['sizes'] = photo['type']
            photos_list.append(photos_dict)
            likes_count=[]
            for photo in photos_list:
                if photo['likes'] in likes_count:
                    photo['filename'] = f'{photo['likes']}_{photo['date_photo']}.jpg'
                else:
                    likes_count.append(photo['likes'])
        return photos_list

