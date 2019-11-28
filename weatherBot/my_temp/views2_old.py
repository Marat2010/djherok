from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
import telebot

TOKEN = '919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE'
tbot = telebot.TeleBot(TOKEN)


# For free PythonAnywhere accounts
# tbot = telebot.TeleBot(TOKEN, threaded=False)

@csrf_exempt
def index(request):
    if request.META['CONTENT_TYPE'] == 'application/json':

        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        tbot.process_new_updates([update])

        return HttpResponse("")

    else:
        raise PermissionDenied


@bot.message_handler(content_types=["text"])
def get_okn(message):
    tbot.send_message(message.chat.id, "Hello, bot!")


# from django.shortcuts import render
# from django.http import HttpResponse
# import requests
# import json
#
# import urllib
# from urllib.request import urlopen
#
# URL = 'https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/'
# URL = URL + 'getMe'
#
#
# def write_json(data, filename='answer.json'):
#     with open(filename, 'w') as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)
#
#
# def index(request):
#     # bot.polling(none_stop=True)
#
#     # r = requests.get(URL + 'getMe')
#     r = requests.get(URL)
#
#     write_json(r.json())
#
#     return HttpResponse("<h1>Скрипт бота 'Test1' </h1>" + str(r.json()))
#
#
#
#
# # https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://7687a4b2.ngrok.io/
# # https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://marat2010.pythonanywhere.com/
# # https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/getWebhookInfo
# # https://7687a4b2.ngrok.io
# # deleteWebhook     getWebhookInfo  setWebhook
# # -------------------------------------------
#
# # __author__ = '@begyy'
# # from rest_framework.response import Response
# # from rest_framework.views import APIView
# # from .models import User
# #
# # import telebot
# # bot = telebot.TeleBot('919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE')
# #
# #
# # class UpdateBot(APIView):
# #     def post(self, request):
# #         json_string = request.body.decode("UTF-8")
# #         update = telebot.types.Update.de_json(json_string)
# #         bot.process_new_updates([update])
# #
# #         return Response({'code': 200})
# #
# #
# # @bot.send_message(commands=['start'])
# # def start(message):
# #     bot.send_message(message.chat.id, 'Привет')
# #
# # @bot.send_message(content_types='text')
# # def send_Message(message):
# #     bot.send_message(message.chat.id, 'Как дела?')
# #
# #
# #
