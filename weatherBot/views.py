# from django.shortcuts import render
# from django.core.files import File # from pprint import pprint # from proxy_requests import ProxyRequests
from django.http import HttpResponse
import requests
import json
import pyowm
import django.views.decorators.csrf
# from weatherBot.const import token_telegram, token_pyowm
import os


token_telegram = os.environ['token_telegram']
token_pyowm = os.environ['token_pyowm']

URL = 'https://api.telegram.org/bot' + token_telegram + '/'    # print(URL)
owm = pyowm.OWM(token_pyowm, language='ru')
proxies = {'https': 'https://165.22.101.123:3128',
           'http': 'https://180.183.9.124:8213',
           'ftp': 'https://ua-139-170-1.fri-gate0.biz:443'}
file_answer = './weatherBot/answer.json'


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
    r = requests.post(url, json=answer, proxies=proxies)  # add proxies on local
    # r = requests.post(url, json=answer)  # remove proxies on hosting
    return r


def answer_weather(message):
    try:
        owm.weather_at_place(message)
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer = 'Такого города или места не знаю. Иностранные или некоторые города вводите на английском, ' \
                    'например Сочи-Sochi, Киев-Kiev.'
    else:
        observation = owm.weather_at_place(message)
        w = observation.get_weather()
        temp = w.get_temperature('celsius')["temp"]
        answer = 'В городе {}, температура: {} \n'.format(w.get_detailed_status(), temp)
        answer += 'Скорость ветра: {} м/c. \n'.format(w.get_wind()["speed"])
        answer += 'Где интересует погода? : '
    return answer


def forecast(message):
    try:
        fc = owm.three_hours_forecast(message)
        f = fc.get_forecast()
        lst = f.get_weathers()
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer_fc = 'Введите сначала город.'
    except pyowm.exceptions.api_call_error.APICallError:
        answer_fc = '-Введите сначала город.-'
    else:
        # print(f)
        # print(lst)
        answer_fc = 'Время по Гринвичу (GMT+00:00):\n'
        for w in lst:
            answer_fc += '{} {} {} \n'.format(w.get_reference_time('iso'), w.get_detailed_status(), w.get_temperature('celsius')["temp"])
        # print(answer_fc)
    return answer_fc


@django.views.decorators.csrf.csrf_exempt
def index(request):
    previous_message = 'Paris'
    if request.method == 'POST':        # if request.content_type == 'application/json':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        print(r)            # pprint(r)
        write_json(r)
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        if '/start' in message:
            answer = 'Привет, {}.\n/help для помощи'.format(r['message']['chat']['first_name'])
        elif '/help' in message:
            answer = 'Введите название города, где интересует погода.\
                    \nИностранные или некоторые города вводите на английском, '\
                     'например Сочи-Sochi, Киев-Kiev.'
        elif '/forecast' in message:
            answer = forecast(previous_message)
        else:
            answer = answer_weather(message)
            previous_message = message
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json()
        print('чтение ---- {}'.format(d['message']['text']))
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)
        # print("Вывод:\n" + d)
        return HttpResponse("Последнее сообщение:\n" + d, content_type="application/json")


if __name__ == '__main__':
    pass

# https://api.telegram.org/bot814337205:AAHB61wNXswK4UH6TTd_UA1l5TijT13nWZ0/setWebhook?url=https://djherok.herokuapp.com/weatherBot/

# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://0ae2a05d.ngrok.io/weatherBot/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://marat2010.pythonanywhere.com/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/getWebhookInfo
# deleteWebhook     getWebhookInfo  setWebhook

# -------------------------------------------

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
