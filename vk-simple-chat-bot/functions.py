import random

import requests
from bs4 import BeautifulSoup


def get_random_file(path):
    return random.choice(tuple((path).iterdir()))

def get_weather(city):
    url = f"https://sinoptik.com.ru/погода-{city}"
    response = requests.get(url)
    write_html(response.content)
    print(response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        temp = soup.find("div", class_="weather__article_main_temp").text.strip()
        sunrise = soup.find("div", class_="ss_wrap ru").findAll("span")[0].text
        sunset = soup.find("div", class_="ss_wrap ru").findAll("span")[1].text
        pressure = soup.find("div", class_="table__col current").find("div", class_="table__pressure").text
        humidity = soup.find("div", class_="table__col current").find("div", class_="table__humidity").text
        wind = soup.find("div", class_="table__col current").findAll("label", class_="show-tooltip")[1].text
        weather_data = {
            "temp": temp,
            "sunrise": sunrise,
            "sunset": sunset,
            "pressure": pressure,
            "humidity": humidity,
            "wind": wind
        }
        return weather_data