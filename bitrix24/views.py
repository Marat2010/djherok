from django.shortcuts import render

from django.http import HttpResponse
import requests
import json
import django.views.decorators.csrf
import os
import datetime

# local_launch = True    # True - если локально с прокси и ngrok.
local_launch = False    # True - если локально с прокси и ngrok.
if local_launch:
    token_telegram = os.environ['token_telegram2']
else:
    token_telegram = os.environ['token_telegram2']
file_answ = './bitrix24/answer.json'              # Для heroku и pythonanywhere
file_data_bot = './bitrix24/data_bot.json'             # Для heroku и pythonanywhere
URL = 'https://api.telegram.org/bot' + token_telegram + '/'
# token_trans_ya = os.environ['token_trans_ya']
# url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
proxies = {'https': 'https://70.89.113.137:443/'}


def send_message(chat_id, text='--Привет, привет!-- )'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    if local_launch:
        r = requests.post(url, json=answer, proxies=proxies)  # add proxies on local
    else:
        r = requests.post(url, json=answer)  # remove proxies on hosting
    return r


def write_json(data, filename=file_answ, wa='w'):
    with open(filename, wa) as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


def read_json(filename=file_answ):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


@django.views.decorators.csrf.csrf_exempt
def index(request):
    if request.method == 'POST':        # if request.content_type == 'application/json':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        write_json(r)   # Запсиь данных чата в файла answer.json.
        chat_id = r['message']['chat']['id']
        message = r['message']['text']

        answer = message
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        # d = read_json()
        # d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)

        data_bot = read_json(file_data_bot)
        # data_bot = json.dumps(data_bot, ensure_ascii=False, sort_keys=True)
        ans_d_bot = ""
        for i in data_bot:
            ans_d_bot += 'ID: {:>9}. Вр: {}. Польз: {:>10}. Запросов: {:>4}. Посл: {} - ({}). Яз:{}\n' \
                         ' ---/ Запросы: {} \---\n'.\
                format(i['chat_id'], i['date_msg'], i['username'], i['num_req'],
                       i['location'][0], i['location'][1], i['lang_code'], i['requests'])

        return HttpResponse("\n Данные чата:\n{}".format
                            (ans_d_bot), content_type="application/json")

