import json
import requests
import configparser
from tqdm import tqdm
from vk import Vk
from yd import YaDisk

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


if __name__ == '__main__':
    print(main())
   