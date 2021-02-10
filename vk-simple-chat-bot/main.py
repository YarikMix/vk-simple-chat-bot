# -*- coding: utf-8 -*-
import random
from pathlib import Path

import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import yaml

from functions import get_random_file


with open("config.yaml") as ymlFile:
    config = yaml.load(ymlFile.read(), Loader=yaml.Loader)


class Bot():
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.IMG_DIR = self.BASE_DIR.joinpath("img")
        self.VIDEO_DIR = self.BASE_DIR.joinpath("video")
        self.MUSIC_DIR = self.BASE_DIR.joinpath("music")
        self.DOC_DIR = self.BASE_DIR.joinpath("documents")

        # Авторизация бота
        authorize = vk_api.VkApi(token=config["group"]["group_token"])

        self.longpoll = VkBotLongPoll(authorize, group_id=config["group"]["group_id"])
        self.upload = vk_api.VkUpload(authorize)
        self.bot = authorize.get_api()

        # Авторизация в vk session
        vk_session = vk_api.VkApi(token=config["user"]["user_token"])

        self.vk = vk_session.get_api()
        self.vk_upload = vk_api.VkUpload(vk_session)

    def write_message(self, message="", attachment=""):
        """Отправляем в беседу сообщение."""
        self.bot.messages.send(
            chat_id=self.chat_id,
            message=message,
            attachment=attachment,
            random_id=get_random_id()
        )

    def say_hello(self):
        user_info = self.vk.users.get(user_id=self.user_id)[0]
        username = user_info["first_name"]
        self.write_message(message=f"Привет {username}!")

    def send_file(self, file, file_type):
        if file_type == "photo":
            """Загружаем фото на сервер Вконтакте."""
            response = self.upload.photo_messages(photos=file)[0]
            attachment = "photo{}_{}".format(response["owner_id"], response["id"])
        elif file_type == "video":
            """Загружаем видео на сервер Вконтакте."""
            response = self.vk_upload.video(video_file=file, name='test')
            attachment = "video{}_{}".format(response["owner_id"], response["video_id"])
        elif file_type == "audio":
            """Загружаем аудиозапись на сервер Вконтакте."""
            song_data = str(file.name)[:-3].split(" - ")
            response = self.vk_upload.audio(
                audio = str(file),
                artist = song_data[0],
                title = song_data[1]
            )
            attachment = "audio{}_{}".format(response["owner_id"], response["id"])
        elif file_type == "doc":
            response = self.upload.document_message(
                doc=file,
                title="doc",
                peer_id=2000000000 + self.chat_id
            )["doc"]
            attachment = "doc{}_{}".format(response["owner_id"], response["id"])
        self.write_message(attachment=attachment)

    # # Не работает
    # def send_doc(self, file):
    #     response = self.vk_upload.document(doc=file)["doc"]
    #     attachment = "doc{}_{}".format(response["owner_id"], response["id"])
    #     self.write_message(attachment=attachment)

    def check_message(self, received_message):
        if received_message == "привет":
            self.say_hello()
        elif received_message == "картинка":
            photo = get_random_file(self.IMG_DIR)
            self.send_file(str(photo), "photo")
        elif received_message == "видео":
            video = get_random_file(self.VIDEO_DIR)
            self.send_file(str(video), "video")
        elif received_message == "аудио":
            audio = get_random_file(self.MUSIC_DIR)
            self.send_file(audio, "audio")
        elif received_message == "документ":
            document = get_random_file(self.DOC_DIR)
            self.send_file(str(document), "doc")

    def run(self):
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


if __name__ == "__main__":
    VkBot = Bot()
    VkBot.run()