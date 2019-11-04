# Setting up Webhook
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://djherok.herokuapp.com/bot/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/getWebhookInfo
# deleteWebhook     getWebhookInfo  setWebhook

from django.shortcuts import render

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
# import pyTelegramBotAPI
import telebot
import requests

TOKEN = '919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE'
tbot = telebot.TeleBot(TOKEN)


# For free PythonAnywhere accounts  - # tbot = telebot.TeleBot(TOKEN, threaded=False)


@csrf_exempt
def bot(request):
    URL = 'https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/'
    URL = URL + 'getMe'
    r = requests.get(URL)

    # if request.META['CONTENT_TYPE'] == 'application/json':
    if request.content_type == 'application/json':
        json_data = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_data)
        tbot.process_new_updates([update])
        return HttpResponse("qwqw1" + str(r))
    else:
        raise PermissionDenied


@tbot.message_handler(content_types=["text"])
def get_okn(message):
    tbot.send_message(message.chat.id, "--Hello--, bot!")
    tbot.send_message(message.chat.id, 'r')
    return HttpResponse("--qwqw1---")


