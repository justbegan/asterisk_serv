import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import jwt
import time
from django.http import FileResponse
import io

load_dotenv()


def create_voice(text: str) -> FileResponse:
    s = Syntes_sound()
    audio_data = b''.join(s.synthesize(text))
    audio_filename = f'file_{datetime.now()}.mp3'
    file_stream = io.BytesIO(audio_data)
    response = FileResponse(file_stream, content_type='audio/mpeg')
    response.headers['Content-Disposition'] = f'attachment; filename="{audio_filename}"'
    return response


class Syntes_sound():
    def __init__(self):
        self.open_token()

    def open_token(self):
        with open('token/token.json', 'r') as json_file:
            self.data = json.load(json_file)

    def synthesize(self, text: str) -> requests:
        url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        token = self.get_old_token() if self.validate_token() else self.get_new_token()
        headers = {
            'Authorization': 'Bearer ' + token
        }

        data = {
            'text': text,
            'lang': 'ru-RU',
            'voice': 'oksana',
            'folderId': os.getenv('folder_id'),
            'format': 'mp3',
            'sampleRateHertz': 48000,
        }

        with requests.post(url, headers=headers, data=data, stream=True) as resp:
            if resp.status_code != 200:
                raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

            for chunk in resp.iter_content(chunk_size=None):
                yield chunk

    def validate_token(self):
        date_str = self.data['expiresAt']
        rounded_date_str = date_str[:23] + date_str[26:29] + date_str[-1]
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        date_obj = datetime.strptime(rounded_date_str, date_format)
        if datetime.now() < date_obj:
            return True
        return False

    def get_old_token(self):
        print("Старый токен")
        return self.data['iamToken']

    def get_new_token(self):
        print("Новый токен")
        self.create_iam()
        self.open_token()
        return self.data['iamToken']

    def create_iam(self):
        """
        Создает json файл из jwt Токена iam токен
        """
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        headers = {
            'Content-Type': 'application/json',
        }

        data = {
            'jwt': self.get_jwt()
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response_data = json.loads(response.text)

            with open('token/token.json', "w") as json_file:
                json.dump(response_data, json_file, indent=4)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")

    def get_jwt(self) -> str:
        """
        Получает по статичным токенам и закрытому ключу JWT Токен
        """
        with open("token/priv.pem", 'r') as private:
            private_key = private.read()  # Чтение закрытого ключа из файла.
        now = int(time.time())
        payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': os.getenv('service_account_id'),
            'iat': now,
            'exp': now + 360
        }
        encoded_token = jwt.encode(
            payload,
            private_key,
            algorithm='PS256',
            headers={'kid': os.getenv('key_id')})
        return encoded_token
