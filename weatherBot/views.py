# from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
import re
#--------------


# https://api.telegram.org/bot856048822:AAG2vyULOMJ_xflmyAxU5KL-W-z5DyhJ9Gg/setWebhook?url=https://7687a4b2.ngrok.io/
# https://api.telegram.org/bot856048822:AAG2vyULOMJ_xflmyAxU5KL-W-z5DyhJ9Gg/setWebhook?url=https://marat2010.pythonanywhere.com/
# https://api.telegram.org/bot856048822:AAG2vyULOMJ_xflmyAxU5KL-W-z5DyhJ9Gg/getWebhookInfo
# https://7687a4b2.ngrok.io
# deleteWebhook     getWebhookInfo  setWebhook
# -------------------------------------------

URL = 'https://api.telegram.org/bot814337205:AAHB61wNXswK4UH6TTd_UA1l5TijT13nWZ0/'


def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_updates():
    # https://api/telegram.org/bot856048822:AAG2vyULOMJ_xflmyAxU5KL-W-z5DyhJ9Gg/getUpdates
    url = URL + 'getUpdates'
    r = requests.get(url)
    write_json(r.json())
    return r.json()


def send_message(chat_id, text='bla-bla-bla'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()


def parse_text(text):
    pattern = r'/\w+'
    crypto = re.search(pattern, text).group()
    return crypto[1:]


def get_price(crypto):
    url = 'https://api.coinmarketcap.com/v1/ticker/{}'.format(crypto)
    r = requests.get(url).json()
    price = r[-1]['price_usd']
    # write_json(r.json(), filename='price.json')
    return price

# --------------------------
def index_hook(request):
    if request.method == 'POST':
        r = request.get_json()
        chat_id = r['message']['chat']['id']
        message = r['message']['text']

        pattern = r'/\w+'

        if re.search(pattern, message):
            price = get_price(parse_text(message))
            send_message(chat_id, text=price)

        write_json(r)
        # return jsonify(r)
        return r

    return HttpResponse("<h1>Скрипт бота 'Погода'</h1>")


def botmain():
    # r = requests.get(URL + 'getMe')
    # print(r.json())
    # get_updates()
    pass

# ----------
import telebot
import pyowm
import constants


bot = telebot.TeleBot(constants.token_telegram2)
owm = pyowm.OWM(constants.token_pyowm, language='ru')


@bot.message_handler(commands=['start'])
def handle_start(message):
    answer = 'Привет, {}. \n/help для помощи'.format(message.chat.first_name)
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['help'])
def handle_help(message):
    answer = 'Введите название города. \n Иностранные или некоторые города вводите на английском, ' \
                'например Сочи-Sochi, Киев-Kiev.'
    bot.send_message(message.chat.id, answer)


@bot.message_handler(content_types=['text'])
def send_echo(message):
    answer = ''
    try:
        owm.weather_at_place(message.text)
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer1 = 'Такого города или места не знаю. Иностранные или некоторые города вводите на английском, ' \
                    'например Сочи-Sochi, Киев-Kiev.'
        bot.send_message(message.chat.id, answer1)
    else:
        observation = owm.weather_at_place(message.text)
        w = observation.get_weather()
        temp = w.get_temperature('celsius')["temp"]

        answer = 'В городе {}, температура: {} \n'.format(w.get_detailed_status(), temp)
        answer += 'Скорость ветра: {} м/c. \n'.format(w.get_wind()["speed"])
        answer += 'Где интересует погода? : '
    bot.send_message(message.chat.id, answer)


def index(request):
    bot.polling(none_stop=True)
    return HttpResponse("<h1>Скрипт бота 'Погода'</h1>")



# if __name__ == '__main__':
#     bot.polling(none_stop=True)





