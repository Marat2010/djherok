# from django.shortcuts import render
# from django.core.files import File # from pprint import pprint # from proxy_requests import ProxyRequests
# from weatherBot.const import token_telegram, token_pyowm
from django.http import HttpResponse
import requests
import json
import pyowm
import django.views.decorators.csrf
import os

local_launch = False    # True - если локально с прокси и ngrok.
if local_launch:
    token_telegram = os.environ['token_telegram2']
else:
    token_telegram = os.environ['token_telegram']
token_pyowm = os.environ['token_pyowm']
file_answer = './weatherBot/answer.json'
file_answer_city = './weatherBot/city.txt'
URL = 'https://api.telegram.org/bot' + token_telegram + '/'    # print(URL)
owm = pyowm.OWM(token_pyowm, language='ru')
# proxies = {'https': 'https://178.32.55.52:443/', 'http': 'https://103.101.253.18:443/'}
# proxies = {'https': 'https://ua-139-170-1.fri-gate0.biz:443/'}
# Искать прокси с портом 443 ( https://awmproxy.com/freeproxy.php )
proxies = {'https': 'https://70.89.113.137:443/'}

icon_url = 'http://openweathermap.org/img/w/04n.png'


def get_wind_direction(deg):
    direction = ['С ', 'СВ', ' В', 'ЮВ', 'Ю ', 'ЮЗ', ' З', 'СЗ']
    for i in range(0, 8):
        if not int(deg):
            res = "\U00002753"
            break
        step = 45.
        min_c = i*step - 45/2.
        max_c = i*step + 45/2.
        if i == 0 and deg > 360-45/2.:
            deg = deg - 360
        if (deg >= min_c) and (deg <= max_c):
            res = direction[i]
            break
    return res


def write_json(data, filename=file_answer):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_json(filename=file_answer):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


def get_icon(status='Неизвестно', weather_code=''):
    dict_status = {'Clear': "\U00002600", 'Snow': "\U00002744",
                   'Clouds': "\U00002601", 'Few clouds': "\U000026C5",
                   'Rain': "\U0001F327", 'Light rain': "\U00002602", 'Moderate rain': "\U00002614",
                   'Thunderstorm': "\U000026C8", 'Mist': "\U0001F301"}
    # Туман Mist: мост-1F301, 1F32B, Снег:- U+1F328,  2744
    if status == 'Clouds':
        if weather_code in [801, 802]:
            status = 'Few clouds'
    if status == 'Rain':
        if weather_code == 500:
            status = 'Light rain'
        elif weather_code == 501:
            status = 'Moderate rain'
    try:
        r = dict_status[status]
    except KeyError:
        r = '-"\U00002753"-'
    return r


def decrease_record(record=''):
    ll = record.split()
    if len(ll) > 1:
        for i, val in enumerate(ll):
            ll[i] = ll[i][0:5]
        rec = '.'.join(ll)
    else:
        rec = record
    return rec


def send_message(chat_id, text='--Привет, привет!-- )'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    # print("---УРЛ и Словарьв send_message перед отправкой: ", url, answer)
    if local_launch:
        r = requests.post(url, json=answer, proxies=proxies)  # add proxies on local
    else:
        r = requests.post(url, json=answer)  # remove proxies on hosting
    return r


def answer_weather(message):
    try:
        owm.weather_at_place(message)
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer_w = 'Такого города или места не знаю. Иностранные или некоторые города вводите на английском, ' \
                    'например Сочи-Sochi, Киев-Kiev.'
    else:
        with open(file_answer_city, 'w') as f:   # write str city to file
            f.write(message)
        observation = owm.weather_at_place(message)
        w = observation.get_weather()
        date_w = w.get_reference_time(timeformat='date')
        temp = w.get_temperature('celsius')["temp"]
        try:
            deg_wind = w.get_wind()['deg']
        except KeyError:
            deg_wind = "?"
        answer_w = 'В городе {} {}, темп-ра: {:4.1f} C°\n'.format(w.get_detailed_status(),
                                    get_icon(w.get_status(), w.get_weather_code()), temp)
        answer_w += 'Ветер: {:3.1f} м/c ({}°-{})\n'.format(w.get_wind()["speed"],
                                                           deg_wind,
                                                           get_wind_direction(deg_wind))
        answer_w += 'Влажн: {} %, Давл: {} мм.рт.ст.\n'.format(
            w.get_humidity(),
            int(w.get_pressure()["press"]/1.333224))
        answer_w += 'Время(GMT+00): {}\n'.format(date_w.strftime("%H:%M %d.%m.%Y"))
        answer_w += ' Где интересует погода или прогноз?:'
    return answer_w


def forecast(message, days_fc=5):
    try:
        fc = owm.three_hours_forecast(message)
        f = fc.get_forecast()
        lst = f.get_weathers()
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer_fc = 'Введите сначала город.'
    except pyowm.exceptions.api_call_error.APICallError:
        answer_fc = '-Введите сначала город. Возможно проблема с сетью-'
    else:
        answer_fc = '{} (время по GMT+00):\n'.format(message)
        i = 0
        for w in lst:
            date_fc = w.get_reference_time(timeformat='date')
            try:
                deg_wind = w.get_wind()['deg']
            except KeyError:
                deg_wind = "?"
            answer_fc += '{}ч:{:2}{:5.1f}C°,{:4.1f}м/с({:3}°-{:>2})\n'.format(
                date_fc.strftime("%d.%m %H"),
                get_icon(w.get_status(), w.get_weather_code()),
                w.get_temperature('celsius')["temp"],
                w.get_wind()["speed"],
                deg_wind,
                get_wind_direction(deg_wind))
            if days_fc == 5:
                answer_fc = answer_fc.rstrip('\n')
                answer_fc += ', Вл:{:3}%, Давл:{:3}мм. {}\n'.format(
                    w.get_humidity(),
                    int(w.get_pressure()["press"]/1.333224),
                    decrease_record(w.get_detailed_status()))
            i += 1
            if i > (days_fc*8):
                break
    return answer_fc


@django.views.decorators.csrf.csrf_exempt
def index(request):
    if request.method == 'POST':        # if request.content_type == 'application/json':
        with open(file_answer_city, 'r') as f:
            city_message = f.readline()
        print("---Пред.сообш (Город):", city_message, type(city_message))
        r = request.body.decode('utf-8')
        r = json.loads(r)
        write_json(r)
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        print("---Чат ID и тек сообщ:", chat_id, type(chat_id), message, type(message))
        if '/start' in message:
            answer = 'Привет, {}.\n/help для помощи'.format(r['message']['chat']['first_name'])
        elif message in ['/help', 'H']:
            answer = 'Показывет погоду в городе.\
                    \nИностранные или некоторые города вводите на английском, '\
                     'например Сочи-Sochi, Киев-Kiev, можно добавить код ' \
                     'страны через запятую (New York,US).\n' \
                     'По нажатию "/..." или "F","S" - выбор Полного(5 дней)' \
                     ' или Короткого(2 дня) прогноза с интервалом 3 часа.\n' \
                     'И не забываем, время по Гринвичу (GMT+00).'
        elif message in ['/fc_short', 'S']:
            days_fc = 2
            answer = forecast(city_message, days_fc)
        elif message in ['/fc_full', 'F']:
            answer = forecast(city_message)
        else:
            answer = answer_weather(message)
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json()
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)
        with open(file_answer_city, 'r') as f:
            city_message = f.readline()
        return HttpResponse("Последнее сообщение:\n" + d + "\nПосл. город: " + city_message,
                            content_type="application/json")


if __name__ == '__main__':
    pass


# ------------
