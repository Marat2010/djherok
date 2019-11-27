# from django.shortcuts import render
# from django.core.files import File # from pprint import pprint # from proxy_requests import ProxyRequests
# from weatherBot.const import token_telegram, token_pyowm
from django.http import HttpResponse
import requests
import json
import pyowm
import django.views.decorators.csrf
import os

token_telegram = os.environ['token_telegram']
token_pyowm = os.environ['token_pyowm']
file_answer = './weatherBot/answer.json'
# city_message = '--'
# city_message = 'Казань, RU'

URL = 'https://api.telegram.org/bot' + token_telegram + '/'    # print(URL)
owm = pyowm.OWM(token_pyowm, language='ru')
proxies = {'https': 'https://165.22.101.123:3128',
           'http': 'https://180.183.9.124:8213',
           'ftp': 'https://ua-139-170-1.fri-gate0.biz:443'}


def get_wind_direction(deg):
    direction = ['С ', 'СВ', ' В', 'ЮВ', 'Ю ', 'ЮЗ', ' З', 'СЗ']
    for i in range(0, 8):
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


def send_message(chat_id, text='--Привет, привет!-- )'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    # r = requests.post(url, json=answer, proxies=proxies)  # add proxies on local
    r = requests.post(url, json=answer)  # remove proxies on hosting
    return r


def answer_weather(message):
    # global city_message
    print("-Ind-1ans_weat-message:", message, "-Ind-1ans_weat-city_message:", city_message)

    try:
        owm.weather_at_place(message)
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer_w = 'Такого города или места не знаю. Иностранные или некоторые города вводите на английском, ' \
                    'например Сочи-Sochi, Киев-Kiev.'
    else:
        city_message = message  # write city
        d = read_json()
        d['city_message'] = message
        write_json(d)
        print("-Ind-2ans_weat-message:", message, "-Ind-2ans_weat-city_message:", city_message)

        observation = owm.weather_at_place(message)
        w = observation.get_weather()
        date_w = w.get_reference_time(timeformat='date')
        temp = w.get_temperature('celsius')["temp"]
        answer_w = 'В городе {}, темп-ра: {:4.1f} C°\n'.format(w.get_detailed_status(), temp)
        answer_w += 'Ветер: {:3.1f} м/c ({}°-{})\n'.format(
            w.get_wind()["speed"],
            w.get_wind()["deg"],
            get_wind_direction(w.get_wind()["deg"]))
        answer_w += 'Влажн: {} %, Давл: {} мм.рт.ст.\n'.format(
            w.get_humidity(),
            int(w.get_pressure()["press"]/1.333224))
        answer_w += 'Время(GMT+00): {}\n'.format(date_w.strftime("%H:%M %d.%m.%Y"))
        answer_w += 'Где интересует погода или прогноз? : '
    return answer_w


def forecast(message, days_fc=5):
    # global city_message

    try:
        fc = owm.three_hours_forecast(message)
        f = fc.get_forecast()
        lst = f.get_weathers()
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer_fc = 'Введите сначала город.'
    except pyowm.exceptions.api_call_error.APICallError:
        answer_fc = '-Введите сначала город. Возможно проблема с сетью-'
    else:
        # print("-Fc-message:", message, "-Fc-city_message:", city_message)

        answer_fc = '{} (время по GMT+00):\n'.format(message)
        i = 0
        for w in lst:
            date_fc = w.get_reference_time(timeformat='date')
            answer_fc += '{}ч.: {:4.1f} C°, {:3.1f}м/с({:3}°-{:2})\n'.format(
                date_fc.strftime("%d.%m %H"),
                w.get_temperature('celsius')["temp"],
                w.get_wind()["speed"],
                w.get_wind()["deg"],
                get_wind_direction(w.get_wind()["deg"]))
            if days_fc == 5:
                answer_fc = answer_fc.rstrip('\n')
                answer_fc += ', Вл:{:3}%, Давл:{:3}мм. {}\n'.format(
                    w.get_humidity(),
                    int(w.get_pressure()["press"]/1.333224),
                    w.get_detailed_status())
            i += 1
            if i > (days_fc*8):
                break
    return answer_fc


@django.views.decorators.csrf.csrf_exempt
def index(request):
    # global city_message

    if request.method == 'POST':        # if request.content_type == 'application/json':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        # city_message = r['city_message']
        r['city_message'] = city_message
        write_json(r)

        print("-Ind-POST-message:", message, "-Ind-POST-city_message:", city_message)

        if '/start' in message:
            answer = 'Привет, {}.\n/help для помощи'.format(r['message']['chat']['first_name'])
        elif '/help' in message:
            answer = ' Показывет погоду в городе.\
                    \nИностранные или некоторые города вводите на английском, '\
                     'например Сочи-Sochi, Киев-Kiev, можно добавить код ' \
                     'страны через запятую (New York,US).\n' \
                     'По нажатию "/..." - выбор Полного(5 дней) или Короткого(2 дня) прогноза с интервалом 3 часа.\n' \
                     'И не забываем, время по Гринвичу (GMT+00).'
        elif message in ['/fc_small', 'короче']:
            print("-Ind-fc_sm-message:", message, "-Ind-fc_sm-city_message:", city_message)

            days_fc = 2
            answer = forecast(city_message, days_fc)
        elif message in ['/fc_full', 'полный']:
            print("-Ind-fc_full-message:", message, "-Ind-fc_full-city_message:", city_message)

            answer = forecast(city_message)
        else:
            answer = answer_weather(message)
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json()
        city_message = d['city_message']
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)
        return HttpResponse("Последнее сообщение:\n" + d + "\nПосл. город: " + city_message,
                            content_type="application/json")


if __name__ == '__main__':
    pass

# https://api.telegram.org/bot814337205:AAHB61wNXswK4UH6TTd_UA1l5TijT13nWZ0/setWebhook?url=https://djherok.herokuapp.com/weatherBot/

# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://0ae2a05d.ngrok.io/weatherBot/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://marat2010.pythonanywhere.com/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/getWebhookInfo
# deleteWebhook     getWebhookInfo  setWebhook

# -------------------------------------------
# answer_fc += '{}: {:4.2f} C°, {:4.2f} м/с({:3}°-{:2}), {}, Вл:{}%, Давл:{}мм.\n'.format(
#     date_fc.strftime("%d.%m %H:%M"),
#     w.get_temperature('celsius')["temp"],
#     w.get_wind()["speed"],
#     w.get_wind()["deg"],
#     get_wind_direction(w.get_wind()["deg"]),
#     w.get_detailed_status(),
#     w.get_humidity(),
#     int(w.get_pressure()["press"] / 1.333224))
# ------------------------------------

# date_fc = w.get_reference_time(timeformat='date')
# answer_fc += '{}ч: {:4.1f} C°, {:3.1f} м/с ({:3}°-{:2}), {}\n'.format(
#     date_fc.strftime("%d.%m %H"),
#     w.get_temperature('celsius')["temp"],
#     w.get_wind()["speed"],
#     w.get_wind()["deg"],
#     get_wind_direction(w.get_wind()["deg"]),
#     w.get_detailed_status())
# ----------------------------------

# return HttpResponse(json.dumps(d, indent=2, ensure_ascii=False), content_type="application/json; encoding=utf-8")
# return HttpResponse("<h1>---Скрипт бота 'Test1'---- </h1>" + str(d))
# return JsonResponse(d, content_type="application/json; encoding=utf-8")
# d = serializers.deserialize('json', d)

# r = get_updates()
# chat_id = r['result'][-1]['message']['chat']['id']
# send_message(chat_id)
# -------------------------
# https://ua-139-170-1.fri-gate0.biz:443 [UA]
# https://fr-54-189-1.friproxy.eu:443 [FR]
# https://uk-167-116-1.friproxy0.eu:443 [UK]

# ---------------------
# __author__ = '@begyy'
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .models import User
#
# import telebot
# bot = telebot.TeleBot('919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE')
#
#
# class UpdateBot(APIView):
#     def post(self, request):
#         json_string = request.body.decode("UTF-8")
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#
#         return Response({'code': 200})
#
# def get_updates():
#     url = URL + 'getUpdates'
#     r = requests.get(url)
#     # r = requests.get(url, proxies=proxies)
#     write_json(r.json())
#     return r.json()
#
# @bot.send_message(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, 'Привет')
#
# @bot.send_message(content_types='text')
# def send_Message(message):
#     bot.send_message(message.chat.id, 'Как дела?')
#
#
#
