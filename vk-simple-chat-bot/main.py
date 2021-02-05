# -*- coding: utf-8 -*-
import random
from pathlib import Path

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from config import *


class Bot():
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.IMG_DIR = self.BASE_DIR.joinpath("img")
        self.VIDEO_DIR = self.BASE_DIR.joinpath("video")
        self.MUSIC_DIR = self.BASE_DIR.joinpath("music")
        self.DOC_DIR = self.BASE_DIR.joinpath("documents")

    def write_message(self, message="", attachment=""):
        """Отправляем в беседу сообщение."""
        self.authorize.method("messages.send", {"chat_id": self.sender, "message": message, "attachment": attachment, "random_id": get_random_id()})

    def send_photo(self, file):
        """Загружаем фото на сервер Вконтакте."""
        response = self.upload.photo_messages(photos=file)[0]
        attachment = "photo{}_{}".format(response["owner_id"], response["id"])
        self.write_message(attachment=attachment)

    def send_video(self, file):
        """Загружаем видео на сервер Вконтакте."""
        response = self.vk_upload.video(video_file=file, name='test')
        attachment = "video{}_{}".format(response["owner_id"], response["video_id"])
        self.write_message(attachment=attachment)

    def send_audio(self, file):
        """Загружаем аудиозапись на сервер Вконтакте."""
        song_data = str(file.name)[:-3].split(" - ")
        response = self.vk_upload.audio(
            audio = str(file),
            artist = song_data[0],
            title = song_data[1]
        )
        attachment = "audio{}_{}".format(response["owner_id"], response["id"])
        self.write_message(attachment=attachment)

    # Не работает
    def send_doc(self, file):
        response = self.vk_upload.document(doc=file, title="Test")["doc"]
        attachment = "doc{}_{}".format(response["owner_id"], response["id"])
        self.write_message(attachment=attachment)

    def auth_handler(self, remember_device=None):
        code = input("Введите код подтверждения\n> ")
        if remember_device is None:
            remember_device = True
        return code, remember_device

    def auth(self):
        # Авторизация бота
        self.authorize = vk_api.VkApi(token=longpoll_token)
        self.longpoll = VkBotLongPoll(self.authorize, group_id=group_id)
        self.upload = vk_api.VkUpload(self.authorize)

        # Авторизация в vk session
        vk_session = vk_api.VkApi(
            login=login,
            password=password,
            auth_handler=self.auth_handler
        )
        try:
            vk_session.auth()
        except Exception as e:
            print("Не получилось авторизоваться, попробуйте снова.")
            print(e)
        finally:
            print('Вы успешно авторизовались.')
            self.vk = vk_session.get_api()
            self.vk_upload = vk_api.VkUpload(vk_session)

    def watch(self):
        """Отслеживаем каждое событие в беседе."""
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get("text") != "":
                        self.reseived_message = event.message.get("text").lower()
                        self.sender = event.chat_id
                        self.user_id = event.message.get("from_id")
                        self.user_info = self.vk.users.get(user_id=self.user_id)[0]
                        if self.reseived_message == "привет":
                            self.write_message(f"Привет {self.user_info['first_name']}")
                        elif self.reseived_message == "картинка":
                            photo = random.choice(tuple((self.IMG_DIR).iterdir()))
                            self.send_photo(str(photo))
                        elif self.reseived_message == "видео":
                            video = random.choice(tuple((self.VIDEO_DIR).iterdir()))
                            self.send_video(str(video))
                        elif self.reseived_message == "аудио":
                            song = random.choice(tuple((self.MUSIC_DIR).iterdir()))
                            self.send_audio(song)
                        elif self.reseived_message == "документ":
                            document = random.choice(tuple((self.DOC_DIR).iterdir()))
                            self.send_doc(document)
            except Exception as e:
                print(e)

    def start_watch(self):
        self.auth()

        self.start_watch()


if __name__ == "__main__":
    VkBot = Bot()
    VkBot.start_watch()