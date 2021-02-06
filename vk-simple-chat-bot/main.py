# -*- coding: utf-8 -*-
import random
from pathlib import Path

import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import yaml


with open("config.yaml") as ymlFile:
    config = yaml.load(ymlFile.read(), Loader=yaml.Loader)


class Bot():
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.IMG_DIR = self.BASE_DIR.joinpath("img")
        self.VIDEO_DIR = self.BASE_DIR.joinpath("video")
        self.MUSIC_DIR = self.BASE_DIR.joinpath("music")
        self.DOC_DIR = self.BASE_DIR.joinpath("documents")

    def write_message(self, message="", attachment=""):
        """Отправляем в беседу сообщение."""
        self.authorize.method("messages.send", {
            "chat_id": self.chat_id,
            "message": message,
            "attachment": attachment,
            "random_id": get_random_id()
        })

    def say_hello(self):
        user_info = self.vk.users.get(user_id=self.user_id)[0]
        username = user_info["first_name"]
        self.write_message(message=f"Привет {username}!")

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
        response = self.vk_upload.document(doc=file)["doc"]
        attachment = "doc{}_{}".format(response["owner_id"], response["id"])
        self.write_message(attachment=attachment)

    def auth_handler(self, remember_device=None):
        code = input("Введите код подтверждения\n> ")
        if remember_device is None:
            remember_device = True
        return code, remember_device

    def auth(self):
        # Авторизация бота
        self.authorize = vk_api.VkApi(token=config["group"]["group_key"])
        self.longpoll = VkBotLongPoll(self.authorize, group_id=config["group"]["group_id"])
        self.upload = vk_api.VkUpload(self.authorize)

        # Авторизация в vk session
        vk_session = vk_api.VkApi(
            login=config["user"]["login"],
            token=config["access_token"]["token"],
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

    def check_message(self, received_message):
        if received_message == "привет":
            self.say_hello()
        elif received_message == "картинка":
            photo = random.choice(tuple((self.IMG_DIR).iterdir()))
            self.send_photo(str(photo))
        elif received_message == "видео":
            video = random.choice(tuple((self.VIDEO_DIR).iterdir()))
            self.send_video(str(video))
        elif received_message == "аудио":
            song = random.choice(tuple((self.MUSIC_DIR).iterdir()))
            self.send_audio(song)
        elif received_message == "документ":
            document = random.choice(tuple((self.DOC_DIR).iterdir()))
            self.send_doc(str(document))

    def watch(self):
        """Отслеживаем каждое событие в беседе."""
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get("text") != "":
                        received_message = event.message.get("text").lower()
                        self.chat_id = event.chat_id
                        self.user_id = event.message.get("from_id")
                        self.check_message(received_message)
            except Exception as e:
                print(e)

    def start_watch(self):
        self.auth()

        self.watch()


if __name__ == "__main__":
    VkBot = Bot()
    VkBot.start_watch()