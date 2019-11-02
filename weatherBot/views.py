# from django.shortcuts import render

__author__ * @begyy
from rest_framework.response import Response
from rest_framework.views import APIView

# import constants
import telebot
bot = telebot.TeleBot('856048822:AAG2vyULOMJ_xflmyAxU5KL-W-z5DyhJ9Gg')
# bot = telebot.TeleBot(constants.token_telegram2)


class UpdateBot(APIView):
    def post(self, request):
        json_string = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])

        return Response({'code': 200})

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет')

@bot.message_handler(content_types='text')
def send_Message(message):
    bot.send_message(message.chat.id, 'Как дела?')



