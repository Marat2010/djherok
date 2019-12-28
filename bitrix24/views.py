from django.shortcuts import render

from django.http import HttpResponse
import requests
import json
import django.views.decorators.csrf
import os
import datetime

local_launch = True    # True - если локально с прокси и ngrok.
# local_launch = False    # True - если локально с прокси и ngrok.
if local_launch:
    token_telegram = os.environ['token_telegram2']
else:
    token_telegram = os.environ['token_telegram2']

Code_app_b24 = 'local.5e04004ad5e626.19578281'
Key_app_b24 = '0mIMVUBB7hfhWwQBLD8cIIEiVPzKjS7Mlkww7VCAyTnlyU3kne'

token_in_b24 = 'jwi2dohttz51o1pk'
url_b24 = 'https://telebot.bitrix24.ru/rest/1/' + token_in_b24 + '/profile/'
file_b24 = './bitrix24/b24.json'
file_answ = './bitrix24/answer.json'
file_data_bot = './bitrix24/data_bot.json'
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


def send_b24():     # отправка запроса в битрикс24
    r = requests.post(url_b24)
    return r


def write_json(data, filename=file_answ, wa='w'):
    with open(filename, wa) as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


def read_json(filename=file_answ):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


def read_ans():    # Чтение данных чата бота из файла answer.json
    data_answer = read_json(file_answ)
    data = {}
    try:
        date_msg = data_answer["message"]['date']
        date_msg = datetime.datetime.fromtimestamp(int(date_msg)).strftime('%H:%M:%S %d-%m-%Y')
        ch_id = data_answer['message']['chat']['id']
        try:
            lang = data_answer['message']['from']['language_code']
        except KeyError:
            lang = 'en'
        f_name = data_answer['message']['chat']['first_name']
        try:
            username = data_answer['message']['chat']['username']
        except Exception:
            username = data_answer['message']['chat']['first_name']
        # username = data_answer['message']['chat']['username']
        msg = data_answer['message']['text']
        data.update({"chat_id": ch_id, "lang_code": lang, "message": msg,
                     "date_msg": date_msg, "first_name": f_name, "username": username})
    except KeyError:
        print("---*** KeyError в 'read_ans()' , не считались данные из 'answer.json' ***---")
    return data


def up_data_chat(**kwargs):  # update данных чата бота (запись нового, обновление существующего, чтение)
    data_l = {}  # Cловарь в логе, если найдется
    number = 0   # Номер в списке, если найдется, или последний при добавлении
    ch_id = read_json(file_answ)['message']['chat']['id']
    try:
        ld = read_json(file_data_bot)   # чтение списка словарей чата
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        ld = []
    for i, l in enumerate(ld):      # Поиск записи
        try:
            number = i                  # запоминаем номер в списке, чтобы потом можно обновить
            if l["chat_id"] == ch_id:
                data_l = l.copy()       # нашли запись в логе
                break
        except KeyError:
            data_l = {}
    if kwargs:              # При аргументах - обновление данных
        if not data_l:      # Первая запись в "лог"
            data_l = read_ans()  # вытаскиваем из answer.json
            num_req = 1             # счетчик обращений к записи
            data_l["num_req"] = num_req
            if 'message' in kwargs:     # создаем список запросов
                data_l['requests'] = [kwargs['message']]
            data_l.update(kwargs)
            ld.append(data_l)   # добавляем запись в лог
            print("--Добав.нов.данн, № в списке: {}, Кол.запросов: {}, Данные: {}".format(len(ld), num_req, kwargs))
        else:                              # изменение словаря для записи в лог-список
            num_req = data_l["num_req"]
            num_req += 1 if ('message' in kwargs) else 0   # если новое сообщение 'message' - увел. счетчика
            data_l["num_req"] = num_req
            date_msg = read_ans()['date_msg']
            data_l.update({'date_msg': date_msg})   # Обновление времени запроса
            if 'message' in kwargs:
                try:
                    req = data_l['requests']
                except (AttributeError, KeyError):
                    req = []
                msg = kwargs['message']
                if len(req) >= 7:
                    req.pop(0)              # удаляем старые запросы
                req.append(msg)             # дополняем список запросов
                data_l['requests'] = req
            data_l.update(kwargs)     # добавление новых данных в случаях 'message', 'location' 'lang'...
            ld[number] = data_l     # запись в список словарей чата
            print("--Измен.дан. № в списке: {}, Кол.запросов: {}, Данные: {}".format(number+1, num_req, kwargs))
        write_json(ld, file_data_bot)  # запись в файл
    return data_l


def answ_b24():     # обработчик запроса от битрих24
    pass


@django.views.decorators.csrf.csrf_exempt
def index(request):
    if request.method == 'POST':        # if request.content_type == 'application/json':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        write_json(r)   # Запсиь данных чата в файла answer.json.
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        up_data_chat(chat_id=chat_id, message=message)  # обновление данных в списке словарей чата.

        # answer = 'Привет, твое сообщение: {}'.format(message)

        r_b24 = send_b24()      # отправка запроса в битрикс24
        print(r_b24, type(r_b24))
        r_b24 = r_b24.json()        # преобразование RESPONSE в json
        write_json(r_b24, file_b24)     # запись в свой файл b24.json для дальнейшего анализа

        # answer = answ_b24()

        answer = read_json(file_b24)
        print(answer, type(answer))
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json(file_b24)
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)

        data_bot = read_json(file_data_bot)
        # data_bot = json.dumps(data_bot, ensure_ascii=False, sort_keys=True)
        ans_d_bot = ""
        for i in data_bot:
            ans_d_bot += 'ID: {:>9}. Вр: {}. Польз: {:>10}. Запросов: {:>4}. Посл: {} - ({}). Яз:{}\n' \
                         ' ---/ Запросы: {} \---\n'.\
                format(i['chat_id'], i['date_msg'], i['username'], i['num_req'],
                       i['location'][0], i['location'][1], i['lang_code'], i['requests'])

        return HttpResponse("Ответ Bitrix24:\n{}\n Данные чата:\n{}".format
                            (d, ans_d_bot), content_type="application/json")


# https://djherok.herokuapp.com/bitrix24/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://djherok.herokuapp.com/bitrix24/

# https://4721dee3.ngrok.io/bitrix24/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://4721dee3.ngrok.io/bitrix24/
#  https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/getWebhookInfo
# deleteWebhook     getWebhookInfo  setWebhook

