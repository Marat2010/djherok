# Setting up Webhook
# https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/setWebhook?url=https://mysite.com/cbbf15d8-0421-4512-84d9-5e5d977e3aef/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://edcd2e43.ngrok.io/bot/
from django.shortcuts import render

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
# import pyTelegramBotAPI
import telebot

TOKEN = '919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE'
# tbot = telebot.TeleBot(TOKEN)
tbot = telebot.TeleBot(TOKEN)


# For free PythonAnywhere accounts
# tbot = telebot.TeleBot(TOKEN, threaded=False)


@csrf_exempt
def bot(request):
    if request.META['CONTENT_TYPE'] == 'application/json':

        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        tbot.process_new_updates([update])

        return HttpResponse("qwqw1")

    else:
        raise PermissionDenied


@tbot.message_handler(content_types=["text"])
def get_okn(message):
    tbot.send_message(message.chat.id, "Hello, bot!")

