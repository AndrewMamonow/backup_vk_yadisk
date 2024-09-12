
import json
import time
import requests
import configparser
from tqdm import tqdm
from pprint import pprint


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


class YaDisk:
    # Класс подключения к диску для сохранения файлов
    def __init__(self, token: str, user_id: str):
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.token = token
        self.id = user_id
        self.headers = {
                        'Authorization': self.token
                        }

    def disk_info(self):
    # Получение информации о диске    
        params = {
                'path': '/'
                }
        response = requests.get(self.url,
                        params = params,
                        headers = self.headers)         
        return response.json()

    def _create_folder(self, folder_path: str):
    # Проверка наличия папки и создание папки на диске
        params = {
                'path': folder_path
                }
        response = requests.get(self.url,
                            params = params,
                            headers = self.headers)
        if response.status_code != 200:
            response = requests.put(self.url,
                                params = params,
                                headers = self.headers)
            if response.status_code != 201:
                folder_path = ''
        return folder_path

    def backup_yd(self, photos_list_upload: dict):
    # Загрузка файлов на диск в папку Backup_{user_id}
        photos_list = []
        folder_path = self._create_folder(f'Backup_{self.id}')
        if folder_path == '':
            print('Не создана папка на диске.')
        else:
            for photos in tqdm(photos_list_upload):
                filename = photos['filename']
                file_path = f'{folder_path}/{filename}'
                params = {
                        'path' : file_path
                        }
                response = requests.get(self.url,
                            params = params,
                            headers = self.headers)
                if response.status_code == 200:
                    file_replace = input(f' Файл {filename} на диске уже есть. Заменить? Y/N')
                    if file_replace.lower() == 'y':
                        response = requests.delete(self.url,
                                    params = {'path' : file_path},
                                    headers = self.headers)
                    else:
                        continue
                params = {
                        'path' : file_path,
                        'url': photos['url']
                        }
                response = requests.post(url = f'{self.url}/upload',
                                    params = params,
                                    headers = self.headers)
                if response.status_code != 202:
                    print(f'Ошибка сохранения файла {filename} на диск.')
                else:    
                    photos_dict = {
                            'file_name' : filename,
                            'size' : photos['sizes']
                            }
                    photos_list.append(photos_dict)
                    time.sleep(1)
            photos_dict = {folder_path : photos_list}
            result_save(photos_dict, 'result.json')
        return len(photos_list)   


def result_save(photos_dict: dict, filename: str):
    # Сохранение результата в файл {filename} в формате json
    json_str = json.dumps(photos_dict, ensure_ascii=False, indent=2)
    with open(filename, 'w') as f:
        f.write(json_str)
   

def config_parametr(parametr: str):
# Параметры из файла setting.ini
    config = configparser.ConfigParser()
    config_file = 'settings.ini'
    config.read(config_file)
    parametr_config = config['Settings'][parametr]
    if parametr_config == '':
        parametr_config = str(input(f'Введите параметр {parametr}:'))
        if input(f' Сохранить параметр {parametr} в {config_file}? Y/N').lower() == 'y':
            config.set('Settings', parametr, parametr_config)
            with open(config_file, 'w') as f:
                config.write(f) 
    return parametr_config

def main():
# Чтение файлов из альбома ВК и сохранение их на Яндекс диск.    
    access_token_vk = config_parametr('access_token_vk')
    user_id_vk = config_parametr('user_id_vk')
    vk = Vk(access_token_vk, user_id_vk)
    vk_user = vk.users_info()
    if 'error' in vk_user:
        result = f'Нет авторизации ВК: {vk_user['error']['error_msg']}'
    else:
        album_id = input(f'Введите album_id альбома пользователя ВК (по умолчанию "profile"):')
        if album_id == '':
            album_id = 'profile'
        photos_album = vk.get_file_album(album_id)
        if len(photos_album) == 0:
             result = f'Нет доступа к альбому {album_id} ВК или альбома нет.'
        else:    
            token = config_parametr('oauth_token_yd')
            yd = YaDisk(token, vk.id)
            yd_info = yd.disk_info()
            if 'error' in yd_info:
                result = f'Нет доступа к диску: {yd_info['message']}'
            else:
                photo_upload = yd.backup_yd(photos_album)
                if photo_upload > 0:
                    result = f'Сохранено \033[34m{photo_upload}\033[0m файлов. Информация в файле \033[34mresult.json\033[0m'
                else:
                    result = 'Ничего не сохранено на диск.'
    return result

if __name__ == '__main__':
    print(main())
   