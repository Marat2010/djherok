from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # bot.polling(none_stop=True)
    return HttpResponse("<h1>Скрипт бота 'Test'</h1>")





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
