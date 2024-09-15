import requests


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