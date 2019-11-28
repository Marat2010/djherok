from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint
from proxy_requests import ProxyRequests

token_telegram2 = '919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE'
# proxy_https = 'https://ua-139-170-1.fri-gate0.biz:443/'
proxies = {'https': 'https://165.22.101.123:3128',
           'http': 'https://180.183.9.124:8213',
           'ftp': 'https://ua-139-170-1.fri-gate0.biz:443'}
# URL = 'https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/'
URL = 'https://api.telegram.org/bot' + token_telegram2 + '/'
print(URL)
file_answer = './weatherBot/answer.json'


def write_json(data, filename=file_answer):
    with open(filename, 'w') as f:
        # f = File(f)
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_json(filename=file_answer):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


def get_updates():
    url = URL + 'getUpdates'
    r = requests.get(url)
    # r = requests.get(url, proxies=proxies)
    write_json(r.json())
    return r.json()


def send_message(chat_id, text='--Привет, привет!-- )'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    # r = ProxyRequests(url)
    # r = r.post(answer)

    r = requests.post(url, json=answer, proxies=proxies)
    # r = requests.post(url, json=answer)
    return r
    # return r.json()


@csrf_exempt
def index(request):
    # if request.content_type == 'application/json':
    if request.method == 'POST':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        print(r)        # pprint(r)
        write_json(r)
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        if 'Казань' in message:
            send_message(chat_id, text='Угадал, Казань!')
        else:
            send_message(chat_id)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json()
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)
        print("Вывод:\n" + d)
        return HttpResponse("Последнее сообщение:\n" + d, content_type="application/json")


if __name__ == '__main__':
    # index()
    pass

# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://1ab27b25.ngrok.io/weatherBot/
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
