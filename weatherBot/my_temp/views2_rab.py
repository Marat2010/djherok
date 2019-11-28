from django.shortcuts import render
from django.http import HttpResponse
import requests
import json

import urllib
from urllib.request import urlopen

URL = 'https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/'


def write_json(data, filename='./weatherBot/answer.json'):
    print(data)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_updates():
    url = URL + 'getUpdates'
    r = requests.get(url)
    print(r)
    write_json(r.json())
    return r.json()


def send_message(chat_id, text='Привет, привет! )'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()


def index():
    r = get_updates()
    chat_id = r['result'][-1]['message']['chat']['id']
    print(chat_id)
    send_message(chat_id)
    # r = requests.get(URL + 'getMe')
    # r = requests.get(URL)
    # write_json(r.json())
    # return HttpResponse("<h1>---Скрипт бота 'Test1'---- </h1>" + str(r.json()))


# URL = URL_Base + 'getWebhookInfo'
if __name__ == '__main__':
    index()


# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://7687a4b2.ngrok.io/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://marat2010.pythonanywhere.com/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/getWebhookInfo
# https://7687a4b2.ngrok.io
# deleteWebhook     getWebhookInfo  setWebhook
# -------------------------------------------

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
