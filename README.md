### Простой бот для беседы Вконтакте
<b>Бот умеет здороваться, отправлять картинки, видео и аудиозаписи</b>

### Как использовать:

Скачиваем зависимости:
```bash
pip3 install -r requirements.txt
```
В файл config.yaml вписываем данные свои данные. <br>
**Внимание**, токен от Standalone-приложения, не прошедшого модерацию, не подойдёт.
Нужен [ключ доступа пользователя](https://vk.com/dev/implicit_flow_user) или выше

```bash
group:
  group_id: ""  # id группы
  group_key: ""  # Ключ cообщества
access_token:
  token: ""  # Токен
```
[Гайд по настройке группы и бота](https://www.youtube.com/watch?v=DJV_Y1yNWRE&ab_channel=RPT-RussianPythonTutor)