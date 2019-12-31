from django.shortcuts import render

from django.http import HttpResponse
import requests
import json
import django.views.decorators.csrf
import os
import datetime
# from bitrix24 import Bitrix24

# local_launch = True    # True - если локально с прокси и ngrok (для Телеграмм).
local_launch = False    # False - если хостинг, без прокси (для Телеграмм).
if local_launch:
    token_telegram = os.environ['token_telegram2']
else:
    token_telegram = os.environ['token_telegram2']

# Используем пока веб хук(входящий). Код и ключ (Серверное локальное приложение
# без интерфейса в Битрикс24) будем использовать позже (REST по протоколу авторизации OAuth 2.0)
# Code_app_b24 = 'local.5e04004ad5e626.19578281'
# Key_app_b24 = '0mIMVUBB7hfhWwQBLD8cIIEiVPzKjS7Mlkww7VCAyTnlyU3kne'
# Используем пока веб хук(входящий) - всё от одного пользователя admin (используем token_in_b24)
token_in_b24 = 'jwi2dohttz51o1pk'
# token_in_b24 = '70a32986f1bf204dec4567147ca6a2af'

URL_b24 = 'https://telebot.bitrix24.ru/rest/1/' + token_in_b24 + '/'
file_b24 = './bitrix24/b24.json'

file_answ = './bitrix24/answer.json'
file_data_bot = './bitrix24/data_bot.json'
URL = 'https://api.telegram.org/bot' + token_telegram + '/'
# token_trans_ya = os.environ['token_trans_ya']
# url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
proxies = {'https': 'https://70.89.113.137:443/'}

# bx24 = Bitrix24('https://e340ea95.ngrok.io/bitrix24/', token_in_b24)
# bx24 = Bitrix24('', token_in_b24)


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


def callMethod(method):
    pass
#     'tasks.task.list',
#     {filter:{'>STATUS':2, REPLICATE:'N', '::SUBFILTER-PARAMS':{FAVORITE:'Y'}}},
#     function(res){console.log(res.answer.result);}
# );


def send_b24(method='', **kwargs):     # отправка запроса в битрикс24
    url = URL_b24 + method
    print(url)
    r = requests.post(url, json=kwargs)
    r = r.json()  # преобразование ответа в json
    return r


def answ_b24(msg):     # обработчик запроса от битрих24
    msg = ''
    answer = read_json(file_b24)
    return answer


@django.views.decorators.csrf.csrf_exempt
def index(request):
    if request.method == 'POST':        # if request.content_type == 'application/json':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        write_json(r)   # Запсиь данных чата в файла answer.json.
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        up_data_chat(chat_id=chat_id, message=message)  # обновление данных в списке словарей чата.

        if message in ['/profile', 'P']:
            r_b24 = send_b24('profile')  # отправка запроса в битрикс24, получение словаря
            answer = 'Вы: {} {}, Админ: {}'.format(r_b24['result']['NAME'], r_b24['result']['LAST_NAME'],
                                                   r_b24['result']['ADMIN'])
        elif message in ['/help', '/start', 'H']:
            r_b24 = send_b24('profile')
            answer = 'Добро пожаловать в Bitrix24, {}.\n Команды:\n/task или "T" - просмотр задач и их дедлайн\n' \
                     '/profile или "P" - просмотр своего профиля\n' \
                     '/L "текст" - сообщение которое разместиться в живой ленте'.format(r_b24['result']['NAME'])
        elif message == 'Лиды':
            r_b24 = send_b24('crm.lead.get', id=1)
            # tasks = r_b24['result']['tasks']
            answer = 'Лиды получены'
        elif message in ['/task', 'T']:
            r_b24 = send_b24('tasks.task.list')
            tasks = r_b24['result']['tasks']
            answer = ''
            for i in tasks:
                answer = answer + i['title'] + '\n'
                try:
                    date = str(i['deadline'])
                    date = date.replace('T', ' ')[:16]
                except Exception:
                    date = "не установлен"
                print("---Время: {}, тип: {} ---".format(date, type(date)))
                answer = answer + "-Дата Дедлайна:" + str(date) + '\n'
            answer = '-** Кол-во задач: {} **-\n {}'.format(r_b24['total'], answer)
        elif '/L ' in message:
            # params = {'POST_TITLE': '-*** От БОССА ***-', 'POST_MESSAGE': message}
            msg = message[3:]
            send_b24('log.blogpost.add', POST_TITLE='-*** От БОССА ***-', POST_MESSAGE=msg)
            r_b24 = send_b24('log.blogpost.get')
            msgs = ''
            for i, val in enumerate(r_b24['result']):
                if i > 7:
                    print('-Номер: {}, Знач: {}'.format(i, val))
                    break
                # msgs = msgs + i + val['DETAIL_TEXT'] + '\n'
                msgs = msgs + "Сообщ.{}: {}\n".format(i, val['DETAIL_TEXT'])
            print(msgs)
            answer = '-** Последние сообщения: **-\n-' + msgs
        else:
            r_b24 = send_b24('profile')
            answer = 'Что именно хотели, {} {}?'.format(r_b24['result']['NAME'], r_b24['result']['LAST_NAME'])
        write_json(r_b24, file_b24)  # запись в свой файл - b24.json для дальнейшего анализа

        # answer = answ_b24(message)
        print(answer)
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json(file_b24)
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)

        data_bot = read_json(file_data_bot)
        ans_d_bot = ""
        for i in data_bot:
            ans_d_bot += 'ID: {:>9}. Вр: {}. Польз: {:>10}. Запросов: {:>4}. Посл: {} - ({}). Яз:{}\n' \
                         ' ---/ Запросы: {} \---\n'.\
                format(i['chat_id'], i['date_msg'], i['username'], i['num_req'],
                       i['location'][0], i['location'][1], i['lang_code'], i['requests'])

        return HttpResponse("Ответ Bitrix24:\n{}\n Данные чата:\n{}".format
                            (d, ans_d_bot), content_type="application/json")




# Елочка нарядная,
# Красавица стоит,
# Огоньки сияют,
# Новый год спешит!
# #
# Будет много счастья,
# Радости, добра,
# Будет год волшебным,
# Будут чудеса!
#
# Будут и подарки,
# Праздничный салют,
# Дед Мороза дети,
# Очень, очень ждут!
# © http://pozdravok.ru/pozdravleniya/prazdniki/noviy-god/detskie/2.htm



# help - Описание
# task - просмотр задач
# profile - просмотр своего профиля

# https://telebot.bitrix24.ru/rest/1/jwi2dohttz51o1pk/log.blogpost.add
# https://telebot.bitrix24.ru/rest/1/jwi2dohttz51o1pk/log.blogpost.add?POST_TITLE=-** Заголовок **-&POST_MESSAGE=---Тело ообщения ---
# https://telebot.bitrix24.ru/rest/1/jwi2dohttz51o1pk/log.blogpost.add?POST_TITLE=%22---11%D0%B7%D0%B0%D0%B3%D0%BE%D0%BB%D0%BE%D0%B2%D0%BE%D0%BA2%22&POST_MESSAGE=%22--fdf---%22
# https://telebot.bitrix24.ru/rest/1/jwi2dohttz51o1pk/tasks.task.list
# https: // telebot.bitrix24.ru / rest / 1 / jwi2dohttz51o1pk / tasks.task.list

        # data_bot = json.dumps(data_bot, ensure_ascii=False, sort_keys=True)

# https://djherok.herokuapp.com/bitrix24/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://djherok.herokuapp.com/bitrix24/


# https://3f63a3f1.ngrok.io/bitrix24/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://3f63a3f1.ngrok.io/bitrix24/
#  https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/getWebhookInfo
# deleteWebhook     getWebhookInfo  setWebhook

# Вместе с кодом будет представлен образец URL, который нужно использовать при отправке данных из сторонней системы
#  в Битрикс24:
# https://********.bitrix24.ru/rest/1/83te1pjdphsa9u15/profile/
# где:
# ******** - имя вашего портала;
# /rest/ - указание системе на то, что данный адрес относится в вебхукам;
# /1/ - идентификатор пользователя, создавшего вебхук. Под правами этого пользователя будет работать этот вебхук.
# /83te1pjdphsa9u15/ - секретный код;
# /profile/ - метод REST, который вы хотите выполнить, обращаясь к вебхуку. Разработчик должен сам подобрать метод
#  из REST API в зависимости от целей создания вебхука.
