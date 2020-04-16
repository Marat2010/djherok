# from django.http import HttpResponse
# from .views import *
# from django.views.decorators.csrf import csrf_exempt
# import time
# from pytz import timezone

import json
from datetime import datetime, timedelta
from django.utils import timezone
import requests
import os
from bitrix24.bitrix24 import Bitrix24
from .models import Bitr, Chat, Messages
from django.core.exceptions import ObjectDoesNotExist

file_answ = './bitr24/answer.json'  # Файл для временного хранения словаря от Телеграмм
# file_data_bot = './bitr24/data_bot.json'  # Файл для хранения данных всех чатов (без БД)

# local_launch = True    # True - если локально с прокси и ngrok (для Телеграмм).
local_launch = False    # False - если хостинг, без прокси (для Телеграмм).
if local_launch:
    token_telegram = os.environ['token_telegram3']
else:
    token_telegram = os.environ['token_telegram2']
URL = 'https://api.telegram.org/bot' + token_telegram + '/'
# proxies = {'https': 'https://70.89.113.137:443/'}     # proxy_url = 'https://telegg.ru/orig/bot'
proxies = {'https': 'https://94.135.230.163:443/'}

# Использовали веб хук(входящий) - всё от одного пользователя admin (bx24_webhook_in)
# Теперь "Серверное локальное приложение без интерфейса в Битрикс24". Код(client_id) и ключ(client_secret) - REST
#  по протоколу авторизации OAuth 2.0.
bx24_webhook_in = os.environ['bx24_webhook_in']
URL_bx24 = 'https://telebot.bitrix24.ru/rest/1/' + bx24_webhook_in + '/'
# Bitrix24 server app without UI
client_id = os.environ['bx24_code_app']     # Битрикс24 код приложения
client_secret = os.environ['bx24_key_app']  # Битрикс24 ключ приложения
file_b24 = './bitr24/bx24.json'             # Файл для временного хранения словаря от Битрикс24
file_bx24_tok = './bitr24/bx24_tok_file.json'  # Файл для временного хранения словаря токенов от Битрикс24
file_last_bindings = './bitr24/last_bindings.json'  # Файл последней связки chat_id и bx24_id

# Использование библиотеки bitrix24-python3-client
# bx24 = Bitrix24('telebot.bitrix24.ru', client_id, client_secret)  # Создание экземпляра Bitrix24.


def write_json(data, filename=file_answ, wa='w'):
    with open(filename, wa) as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


def read_json(filename=file_answ):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


def rw_chat(post=False):
    data = read_ans()  # print('--* Словарь из answer.json: ', data)
    data.pop('date_msg')
    message = data.pop('message')    # print('=== data in "rw_chat":', data)
    chat = Chat.objects.get_or_create(chat_id=data['chat_id'], defaults=data)[0]
    if post:
        try:
            chat = Chat.objects.update_or_create(chat_id=data['chat_id'], defaults=data)[0]
            chat.messages.create(message=message)
        except Exception as e:
            print('== Что то непонятное в "rw_chat": {}'.format(e))
    chat.last_message = message     # добавим чтобы не искать в связанной базе в будущем
    return chat


def send_msg_authorization(bx24):
    url_tok = bx24.resolve_authorize_endpoint()  # Поучение ссылки для авторизации
    url_tok = '<a href="{}">Bitrix24</a>'.format(url_tok)
    answer = "Авторизуйтесь пож-та в: {} ".format(url_tok)
    return answer


def convert_time(expires):    # преобразует время из 1584146509 в datetime.datetime(2020, ..) + TimeZone
    fmt = '%Y-%m-%d %H:%M:%S'
    if isinstance(expires, str):     # Преобразуем строку '2020-03-14 03:41:49' в формат "datetime".
        expires = datetime.strptime(expires[0:19], fmt)
    elif isinstance(expires, int):  # преобразует время из 1584146509 в datetime.datetime(2020, ..) + TimeZone
        expires_no_tz = datetime.fromtimestamp(expires)  # datetime.datetime(2020, 3, 14, 1, 48, 29)
        current_tz = timezone.get_current_timezone()  # <DstTzInfo 'Europe/Moscow' LMT+2:30:00 STD>
        expires = current_tz.localize(expires_no_tz)  # datetime.datetime(2020, 3, 14, 1, 48, 29, tzinfo=<DstTzInfo
                                                      #  'Europe/Moscow' MSK+3:00:00 STD>)
    else:                     # Значит дата в формате "datetime"
        expires = expires.strftime(fmt)  # Преобразует из "datetime" в строку '2020-03-14 03:41:49'
    return expires


class Bx24(Bitrix24):
    try:
        last_bindings = read_json(file_last_bindings)
    except json.decoder.JSONDecodeError:
        last_bindings = {}
    # print('== Загруженные привязки: {}'.format(last_bindings))

    def __init__(self, chat_id=None, message=None):
        super().__init__(domain='telebot.bitrix24.ru', client_id=client_id, client_secret=client_secret)
        self.chat_id = chat_id      # Добавляем в экземпляр "chat_id" и "message" для удобства оперирования.
        self.message = message
        self.bx24_id = self.user_id  # Дублирование (в родительском классе - user_id, а в базе Bitr - bx24_id)
        self.expires = None

    def get_last_binding(self):
        self.user_id = __class__.last_bindings.get(str(self.chat_id)).get('bx24_id')
        self.bx24_id = __class__.last_bindings.get(str(self.chat_id)).get('bx24_id')
        self.access_token = __class__.last_bindings.get(str(self.chat_id)).get('access_token')
        self.refresh_token = __class__.last_bindings.get(str(self.chat_id)).get('refresh_token')
        self.expires = __class__.last_bindings.get(str(self.chat_id)).get('expires')

    def update_last_binding(self):
        __class__.last_bindings.update({str(self.chat_id): {'bx24_id': self.bx24_id, 'expires': self.expires,
                                                            'access_token': self.access_token,
                                                            'refresh_token': self.refresh_token}})
        write_json(__class__.last_bindings, file_last_bindings)   # Запись в  файл и в базу:
        Bitr.objects.update_or_create(bx24_id=self.user_id, defaults={'access_token': self.access_token,
                                                                      'refresh_token': self.refresh_token,
                                                                      'expires': self.expires})

    def get_tokens_from_db(self, bitr):  # Получение токенов с базы и привязка таблиц "Bitr", "Chat"
        self.user_id = bitr.bx24_id  # передаем id,токены, expires экземпляру bx24, для вызова 'call_method'-а
        self.bx24_id = bitr.bx24_id  # Дублирование (в родительском классе - user_id, а в базе Bitr - bx24_id)
        self.expires = bitr.expires
        self.access_token = bitr.access_token
        self.refresh_token = bitr.refresh_token

        chat = Chat.objects.get(chat_id=self.chat_id)
        chat.bitrs.add(bitr)  # Привязываем записи в двух таблицах. Или так: bitr.chats.add(chat)


def check_msg_auth_code(bx24):           # Проверка в сообщения нашего кода авторизации ('/AUTH-3d29')
    if len(bx24.message.split('-')) == 1:
        print('-------------- Точка 3(check_msg_auth_code). В сообщении /AUTH НЕТ кода')
        answer = send_msg_authorization(bx24)   # Отправить ответ сообщение на авторизацию
    else:                                       # Есть какой то код авторизации ('/AUTH-3d29')
        print('-------------- Точка 3(check_msg_auth_code). В сообщении /AUTH ЕСТЬ код')
        bind_code = bx24.message.split('-')[1]  # Код '3d29'
        acc_tok3_code = bind_code[:3]       # Первые три символа - должны быть первыми 3-мя знаками access tokena (3d2).
        bx24_id_code = bind_code[3:]        # Остальные цифры - это ID пользователя в системе Б24 (9).
        try:                        # Проверка существования Б24 ID в базе Bitr.
            bitr = Bitr.objects.get(bx24_id=bx24_id_code)
        except ObjectDoesNotExist:
            print('-------------- Точка 4(check_msg_auth_code). Bx24_id НЕ найден.')
            answer = 'Битрикс24 id НЕ совпадают. '
        else:
            print('-------------- Точка 4(check_msg_auth_code). Bx24_id найден.')
            answer = 'Битрикс24 id найден. '
            if acc_tok3_code == bitr.access_token[:3]:  # Проверка access токена в code и в словаре (базе Bitr).
                print('-------------- Точка 5(check_msg_auth_code). Токены совпадают')
                answer += 'Токены совпадают. Авторизация прошла удачно!!!'
                bx24.get_tokens_from_db(bitr)  # Получение токенов с базы и привязка таблиц "Bitr", "Chat"
                print('===== Значения (bx24.expires):{}, Тип: {}'.format(bx24.expires, type(bx24.expires)))
                bx24.expires = convert_time(bx24.expires)  # Преобразуем из формата "datetime" в строку
                bx24.update_last_binding()
            else:
                print('-------------- Точка 5(check_msg_auth_code). Токены НЕ совпадают')
                answer += 'Токены НЕ совпадают!!!'
    return answer


def portal(chat):
    message = chat.messages.first().message  # находим посл.сообщение польз. телеграмм
    bx24 = Bx24(chat_id=chat.chat_id, message=message)
    print('---------- Точка 0. Last Bind: {}'.format(bx24.last_bindings))
    if str(bx24.chat_id) in Bx24.last_bindings.keys() and '/AUTH' not in bx24.message:   # Есть запись и не авторизация.
        print('-------------- Точка 1(portal). Есть запись')
        bx24.get_last_binding()                     # Берем данные с последних привязок (chat_id, bx24_id, токены).
        answer, bx24 = check_tokens(bx24)           # Cделать проверку на срок токенов и обновления их.
        if answer is None:         # Если answer пустой, значит все хорошо (иначе в answer будет ссылка на авторизацию),
            answer = bitrix_command_handler(bx24)   # идем на обработку комманд Б24.
    else:                                           # Записи НЕТ, новый пользователь.
        print('-------------- Точка 1(portal). Нет записи или запрос авторизации')
        if '/AUTH' in bx24.message:                 # В сообщение запрос на авторизацию или ответ от авторизации.
            print('-------------- Точка 2(portal). В сообщении /AUTH')
            answer = check_msg_auth_code(bx24)      # Проверка кода.
        else:                                       # Нет ни кода, ни запроса на авторизацию,
            answer = send_msg_authorization(bx24)   # отправим сами его на авторизацию.
            print('-------------- Точка 2(portal). В сообщении нет /AUTH')
    return answer


def check_tokens(bx24):
    answer = None
    date_now = datetime.now()
    expires = convert_time(bx24.expires)    # Преобразуем из строки в формат "datetime"
    print('== NOW: {}   == EXP: {}'.format(date_now.strftime('%Y-%m-%d %H:%M:%S'), expires))
    if date_now > expires + timedelta(days=30):  # Устарел refresh токен
        print('-------------- Точка 3.1(check_tokens). Refresh Токен устарел (30 дней), Отпр. на авторизацию')
        answer = send_msg_authorization(bx24)    # Отправим на авторизацию
    else:
        if date_now > expires:              # токен (access) устарел ?
            print('-------------- Точка 3.1(check_tokens). Токен устарел, Обновляем')
            bx24.refresh_tokens()           # обновляем токены
            expires = date_now + timedelta(seconds=3600)  # Добавления дельты, expires 60 минут.
            bx24.expires = convert_time(expires)  # обновляем время токена, и в формат строки
            bx24.update_last_binding()      # обновляем токены в последних привязках и в базе Bitr
        else:
            print('-------------- Точка 3.1(check_tokens). Токен Не устарел')
    return answer, bx24


def bitrix_command_handler(bx24):  # Обработчик команд Битрикс24
    message = bx24.message
    if message in ['/profile', 'P']:
        r_bx24 = bx24.call_method('user.current')  # (r_ -запрос) получение словаря
        answer = 'Ваш ID: {},\nИмя: {}, {}'.format(r_bx24['result']['ID'],
                                                   r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
    elif message in ['/help', '/start', 'H']:
        # r_b24 = send_bx24_webhook('profile')
        r_bx24 = bx24.call_method('profile')
        answer = 'Добро пожаловать в Bitrix24, {}.\n Команды:\n/task или "T" - просмотр задач и их дедлайн\n' \
                 '/profile или "P" - просмотр своего профиля\n/Leads или "Лиды" - просмотр Лидов\n' \
                 '/L "текст" - сообщение которое разместиться в живой ленте'.format(r_bx24['result']['NAME'])
    elif message in ['/Leads', 'Лиды']:
        # r_b24 = send_bx24_webhook('crm.lead.get', id=1)   # r_b24 = send_bx24_webhook('crm.lead.list')
        r_bx24 = bx24.call_method('crm.lead.list')
        leads = r_bx24['result']
        answer = ''
        for i in leads:
            date = str(i['BIRTHDATE'])
            date = date.replace('T', ' ')[:16]
            answer = answer + '* {}\n ->ДР: {}\n'.format(i['TITLE'], date)
        answer = 'Лиды получены:\n {}'.format(answer)
    elif message in ['/task', 'T']:
        r_bx24 = bx24.call_method('tasks.task.list')
        tasks = r_bx24['result']['tasks']
        answer = ''
        for i in tasks:
            answer = answer + '*' + i['title'] + '\n'
            try:
                date = str(i['deadline'])
                date = date.replace('T', ' ')[:16]
            except Exception as ex:
                print("---Исключение: {}".format(ex))
                date = "не установлен"
            answer = answer + " --> Дедлайн: {}\n".format(str(date))
        answer = '*** Кол-во задач: {} ***\n{}'.format(r_bx24['total'], answer)
    elif '/L' in message:
        ll = message.split()
        if len(ll) > 1:
            msg = message[3:]
            bx24.call_method('log.blogpost.add',
                             {'POST_TITLE': "-*** С телеграм бота @Bitr24_bot ***-", 'POST_MESSAGE': msg})
        r_bx24 = bx24.call_method('log.blogpost.get')
        r_bx24['result'] = r_bx24['result'][:7]  # уменьшение кол-ва сообщ до 7
        msgs = ''
        for i in r_bx24['result']:
            msgs += "{}: {}\n".format(i['DATE_PUBLISH'][11:16], i['DETAIL_TEXT'])
        print(msgs)
        answer = '-** Последние сообщения: **-\n*' + msgs
    # elif '/AUTH' in message:      # Убрать, условие проверяется в portal с last_bindings
    #     answer = check_msg_auth_code(bx24)  # проверка кода
    #     r_bx24 = {"result": message}
    #     print('-------------- Точка 5(bitrix_command_handler). Смена авторизации')
    else:
        r_bx24 = bx24.call_method('user.current')  # r_bx24 = send_bx24_webhook('profile') # через webhook, убрать
        answer = 'Что именно хотели, {} {}?'.format(r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
    write_json(r_bx24, file_b24)  # запись в свой файл - b24.json для дальнейшего анализа
    return answer


def send_message(chat_id, text='--Привет, привет!-- )', parse_mode=''):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
    if local_launch:
        r = requests.post(url, json=answer, proxies=proxies)  # add proxies on local
    else:
        r = requests.post(url, json=answer)  # remove proxies on hosting
    return r


def read_ans():    # Чтение данных чата бота из файла answer.json
    data_answer = read_json(file_answ)
    data = {}
    try:
        date_msg = data_answer["message"]['date']
        date_msg = datetime.fromtimestamp(int(date_msg)).strftime('%H:%M:%S %d-%m-%Y')
        ch_id = data_answer['message']['chat']['id']
        try:
            lang = data_answer['message']['from']['language_code']
        except KeyError:
            lang = 'en'
        f_name = data_answer['message']['chat']['first_name']
        last_name = data_answer['message']['chat']['last_name']
        try:
            username = data_answer['message']['chat']['username']
        except Exception:
            username = data_answer['message']['chat']['first_name']
        # username = data_answer['message']['chat']['username']
        msg = data_answer['message']['text']
        data.update({"chat_id": ch_id, "lang_code": lang, "message": msg,
                     "date_msg": date_msg, "first_name": f_name, "last_name": last_name, "username": username})
    except KeyError:
        print("---*** KeyError в 'read_ans()' , не считались данные из 'answer.json' ***---")
    return data


# Не используется!!! :
def send_bx24_webhook(method='', **kwargs):     # отправка запроса в битрикс24 (через WebHook)
    url = URL_bx24 + method             # print(url)
    r = requests.post(url, json=kwargs)
    r = r.json()                        # преобразование ответа в json
    return r

    #     self.message = message
    #     self.bx24_id = self.user_id
    #     self.access_token = self.access_token
    #     self.refresh_token = self.refresh_token
    #     self.bx24_name = bx24_name

# https://djherok.herokuapp.com/bitr24/tg/

# def portal_old(chat):
#     # message = chat.messages.first().message  # находим посл.сообщение польз. телеграмм
#     message = chat.last_message  # находим посл.сообщение польз. телеграмм
#     print('== Последнее сообщение chat.last_message: {} {}'.format(chat.last_message, type(chat.last_message)))
#     bx24 = Bx24(chat_id=chat.chat_id, message=message)
#
#     if '/AUTH' in message:
#         answer = check_msg_auth(bx24)
#     try:
#         # bitr = chat.bitrs.first()   # находим посл.запись польз.Б24 под кем заходил из телеграмм
#         bitr = find_last_record_bitr(chat)   # находим посл.запись польз.Б24 под кем заходил из телеграмм
#         print('===== bitr from find_last_record_bitr(chat) ', bitr)
#         bx24.get_tokens_from_db(bitr)  # может перенести в 'else' ?
#
#     except Exception:  # Значит новый пользователь, или только что авторизовался и нет связки двух таблиц
#         bitr = Bitr.objects.first()  # Находим посл.запись поль. Б24 не привязынную к таблице польз. телеграмм.
#         if bitr:                     # Если есть, значит была авторизацция, и надо связать польз-ей в таблицах
#             bitr.chats.add(chat)         # Привязываем записи в двух таблицах. Или так: chat.bitrs.add(bitr)
#             bitr.expires = "{}".format(bitr.expires)  # обновляем, добавляем чат ID в expires "chat_id, 'время'"
#             bitr.save()
#             print('== Поль. Б24 связали с польз. телеграмм в базах')
#             answer = 'Вы авторизовались!!!(Ваше имя в Битрикс: {})'.format(bitr.bx24_name)
#         else:   # Значит нет записи в табл. польз. Б24, отправить приглашение на авторизацию
#             print('== Новый польз. Б24, отправить приглашение на авторизацию')    # нет записей польз.Б24, первый вход
#             answer = send_msg_authorization(bx24)
#
#     else:               # Значит польз. с телеграм связан с польз.Б24
#         # bx24 = find_new_auth(bx24)
#         r_bx24 = bx24.call_method('user.current')  # (r_ -запрос) получение словаря
#         try:                # ... если Токены есть в базе, но access токен истек (1час),или refresh (1 месяц) ...
#             r_bx24['result']    # Проверка на то что токены не проходят
#         except KeyError:        # r_bx24['error']
#             if r_bx24['error_description'] == 'The access token provided has expired.':
#                 print('==Токен access устарел (1час). словарь bx24.call_method: {}'.format(r_bx24))
#                 bx24.refresh_tokens()  # Токены есть в базе, но access токен истек (1час), обновить через токен refresh
#                 expires = (datetime.now() + timedelta(seconds=3600)).strftime('%H:%M:%S %d-%m-%Y')
#                 # bitr.expires = "{}, {}".format(chat.chat_id, bitr.expires)
#                 # expires = [chat.chat_id, expires]                 # обновляем новые токены в базе:
#                 expires = "{}, {}".format(chat.chat_id, expires)                 # обновляем новые токены в базе:
#                 bitr = Bitr.objects.update_or_create(bx24_id=bx24.user_id, defaults=bx24.get_tokens())[0]
#                 bitr.expires = expires
#                 bitr.save()
#                 print('== Б24 токены обновлены и в базе тоже')
#                 print(bx24.__dict__)
#                 answer = bitrix_command_handler(bx24, message)  # дальше обрабатываем команду с чата
#             elif r_bx24['error_description'] == 'The refresh token provided has expired.':
#                 print('==Возможно токены refresh, надо обновить, дописать код, отправить  на авторизацию')
#                 answer = '== Возможно токены refresh, надо обновить'
#             elif r_bx24['error'] == 'invalid_token':
#                 print('==Возможно токены поломали, надо заново авторизоваться ')
#                 answer = '==Возможно токены поломали, надо заново авторизоваться'
#             elif r_bx24['error'] == 'NO_AUTH_FOUND':
#                 print('==Ошибка NO_AUTH_FOUND ==: ', r_bx24)
#                 # bitr.chats.remove(chat)  # Удаляем привязку записи в двух таблицах. Надо подругому!!!
#                 bitr.expires = chat.chat_id  # делаем пометку для того чтобы след.раз привязать
#                 bitr.access_token = ''
#                 bitr.refresh_token = ''
#                 bitr.save()
#                 answer = send_msg_authorization(bx24)
#                 # url_tok = bx24.resolve_authorize_endpoint()  # Поучение ссылки для авторизации
#                 # url_tok = '<a href="{}">Bitrix24</a>'.format(url_tok)
#                 # answer = "Авторизуйтесь пож-та в: {} ".format(url_tok)
#             else:
#                 print('==При всех остальных непонятных случаях "error" отправлять на авторизацию')
#                 answer = '==При всех остальных непонятных случаях "error" отправлять на авторизацию'
#         else:
#             if message in ['/AUTH']:  # Если польз. телеграмм решил переавторизоваться в Б24
#                 print('== Польз. решил переавторизоваться в Б24')  # нет записей польз.Б24, первый вход
#                 # bitr.expires = '/AUTH {}'.format(chat.chat_id)  # делаем пометку для того чтобы след.раз привязать
#                 bitr.expires = chat.chat_id  # делаем пометку для того чтобы след.раз привязать
#                 bitr.access_token = ''
#                 bitr.refresh_token = ''
#                 bitr.save()
#                 answer = send_msg_authorization(bx24)
#             else:
#                 answer = bitrix_command_handler(bx24, message)  # Обработчик команд-сообщений от телеграм в Битрикс24
#     return answer

# def find_new_auth(bx24):
#     bitr_all = Bitr.objects.all()
#     for b in bitr_all:
#         spisok = b.expires.split(',')
#         if len(spisok) == 1:
#             if len(spisok[0]) > 15:     # Значит время
#                 b.expires = '{}, {}'.format(bx24.chat_id, b.expires)
#                 b.save()
#                 bx24.get_tokens_from_db(b)
#             else:       # Значит чат ID
#                 chat_id = int(b.expires)
#                 print('== 1-B.ACCESS: {}, TYPE: {}'.format(b.access_token, type(b.access_token)))
#
#                 # if chat_id == bx24.chat_id and not bx24.access_token == '':
#                 if chat_id == bx24.chat_id and (not b.access_token == ''):
#                     print('== 2 -B.ACCESS: '.format(b.access_token))
#                     b.expires = '{}, {}'.format(chat_id, b.expires)
#                     b.save()
#                     # bx24.get_tokens_from_db(b)
#                 else:
#                     pass
#                     # b.expires = ''
#                     # b.save()
#         elif len(spisok) == 2:      # значит стоит и чат ID и время
#             print('==11 РАВНО: {} = {}'.format(spisok[0], bx24.chat_id))
#             if int(spisok[0]) == bx24.chat_id:
#                 bx24.get_tokens_from_db(b)
#                 print('==22 РАВНО: {} = {}'.format(spisok[0], bx24.chat_id))
#         else:
#             pass
#         print('== EXPIRES: {}'.format(b.expires))
#     print('==BX24:== {}'.format(bx24.__dict__))
#     return bx24


# def split_expires(expires):     # Разделение на чат ID и время в сек., чтобы найти последнию запись польз.Б24
#     # bitr[0].expires     # '1080498053, 01:36:56 02-03-2020'
#     # expires = '1080498053, 01:36:56 02-03-2020'
#     l = expires.split(',')      # ['1080498053', ' 01:36:56 02-03-2020']
#     l[1] = l[1][1:]             # ['1080498053', '01:36:56 02-03-2020'] убираем пробел
#     time_sec = time.strptime(l[1], '%H:%M:%S %d-%m-%Y')  # time.struct_time(tm_year=2020,tm_mon=3,tm_mday=2 tm_hour=1,.
#     time_sec = time.mktime(time_sec)        # = > 1583102215.0
#     return (l[0], time_sec)  # кортеж: chat_id, time at seconds


# def find_last_record_bitr(chat):
#     bitr = chat.bitrs.all()   # Все записи польз.Б24 под кем заходил из телеграмм
#     print('---chat_id: {} -----bitr_all: {}'.format(chat.chat_id, bitr))
#     last_bitr = None
#     time_max = 0
#     for b in bitr:
#         chat_id, time_sec = split_expires(b.expires)
#         if time_max < time_sec:
#             time_max = time_sec
#             last_bitr = b
#     return last_bitr
#         # bitr = chat.bitrs.all()
#         # bitr   --  <QuerySet [<Bitr:   9:Mara2017>, <Bitr:  15:Bi_Linux>]>
#         # bitr[0]  --   <Bitr:   9:Mara2017>
#         # bitr[1].expires  --    '1080498053, 01:07:40 02-03-2020'


# def check_msg_auth(bx24):           # Проверка в сообщения нашего кода авторизации (au = '/AUTH-0739')
#     print('== Сообщение bx24.message: {} = type: {}'.format(bx24.message, type(bx24.message)))
#     ll = bx24.message.split('-')
#     if len(ll) == 1:
#         answer = send_msg_authorization(bx24)
#     elif len(ll) == 2:
#         bind_code = ll[1]
#         acc_tok3 = bind_code[:3]
#         bx24_id = int(bind_code[3:])
#         bitr = Bitr.objects.get(bx24_id=bx24_id)  # вытаскиваем запись
#         if bitr.access_token[:3] == acc_tok3:
#             answer = 'Код подтвержден'
#             chat = Chat.objects.get(chat_id=bx24.chat_id)
#             chat.bitrs.add(bitr)  # Привязываем записи в двух таблицах. Или так: bitr.chats.add(chat)
#             bx24.get_tokens_from_db(bitr)
#             Bx24.last_bindings.update({bx24.chat_id: {'bx24_id': bx24_id,
#                                                       'access_token': bx24.access_token,
#                                                       'refresh_token': bx24.refresh_token,
#                                                       'expires': str(bitr.expires)}})
#             print('== Bx24.last_bindings : {} ==type: {}'.format(Bx24.last_bindings, type(Bx24.last_bindings)))
#             write_json(Bx24.last_bindings, file_last_bindings)
#         else:
#             answer = 'Код  НЕ подтвержден!'
#     else:
#         answer = 'Не верный код!'
#     return answer


# def record_search2(bx24):
#     bx24.get_last_binding()
#     expires = bx24.expires[:19]
#     fmt = '%Y-%m-%d %H:%M:%S'
#     expires = datetime.strptime(expires, fmt)
#     print('== expireSS: ', expires)
#     if bx24.expires:
#         if expires < datetime.now():
#             bx24.refresh_tokens()
#             print('== токены обновлены---')
#             expires = (datetime.now() + timedelta(seconds=3600))
#             print(expires)
#             Bx24.last_bindings.update({str(bx24.chat_id): {'bx24_id': bx24.bx24_id,
#                                                       'access_token': bx24.access_token,
#                                                       'refresh_token': bx24.refresh_token,
#                                                       'expires': str(expires)}})
#             print('== токены обновлены--  Bx24.last_bindings-', Bx24.last_bindings)
#
#             write_json(Bx24.last_bindings, file_last_bindings)
#         is_available = True
#     else:
#         is_available = False
#     return (bx24, is_available)
# --------------------------------------------
# def portal(chat):
#     message = chat.messages.first().message  # находим посл.сообщение польз. телеграмм
#     bx24 = Bx24(chat_id=chat.chat_id, message=message)
#     print('~~~ Точка 0. bx24.__dict__ : {}'.format(bx24.__dict__))
#     bx24, is_available = record_search2(bx24)  # Поиск по чат ID информации: (bx24_id, токены, expires)
#     print('~~~ Точка 1. is_available: {}, bx24.__dict__ : {}'.format(is_available, bx24.__dict__))
#     if is_available:
#         print('~~~ Точка 2(Да). Продолжаем.')
#         if '/AUTH' in message:
#             print('~~~ Точка 3(Да). Продолжаем. Проверка на код')
#             answer = 'Разбор кода'
#         else:
#             print('~~~ Точка 3(Нет). Все хорошо. Можно отправить на обработку сообщений для Б24')
#             answer = bitrix_command_handler(bx24)
#             print('~~~ Точка 5(Би24). Все хорошо. После обработки сообщений для Б24')
#     else:
#         print('~~~ Точка 2(Нет). Отправка на авторизацию')
#         answer = send_msg_authorization(bx24)
#         print('~~~ Точка 5(AUTH). answer : {}'.format(answer))
#     return answer

# try:                # Проверка что там только ID пользователя телеграмм.
#     int(b.expires)
# except ValueError:
#     chat_id = int(b.expires.split(',')[0][1:])
# else:
#     chat_id = int(b.expires.split(',')[0][1:])

# -----------
# try:
#     session = request.session['OAuth']
# except Exception:
#     print('== Сессии: NO')
# else:
#     print('== Сессии: ', session)
# ------------
# ./manage.py runserver 0.0.0.0:8000
# Starting development server at http://0.0.0.0:8000/
# sudo ufw enable
# sudo ufw enable
# netstat -ano | grep 8000
# tcp        0      0 0.0.0.0:8000            0.0.0.0:*               LISTEN      off (0.00/0/0)
# ---------------------------------------------
# # elif message in ['/AUTH']:  # Если польз. телеграмм решил переавторизоваться в Б24
# #     print('== Польз. решил переавторизоваться в Б24')  # нет записей польз.Б24, первый вход
# #     answer = send_msg_authorization(bx24)
# #     bitr.expires = '/AUTH {}'.format(chat.chat_id)  # делаем пометку для того чтобы след.раз привязать
# #     bitr.save()
# #     # chat.chat_id  int(msg.split()[1])
#
# # elif '/AUTH' in bitr.expires:  # Есть пометка о переавторизации
# #     if chat.chat_id == int(bitr.expires.split()[1]):  # проверка что чат ID совпадает
# #         bitr.chats.add(chat)
# #         bitr.expires = ''.join(bitr.expires.split()[1:])
# #         bitr.save()
#
# # chat.chat_id  int(msg.split()[1])
# # -----------------------------
# # if message in ['/profile', 'P']:
# #     r_bx24 = bx24.call_method('user.current')   # (r_ -запрос) получение словаря
# #     answer = 'Ваш ID: {},\nИмя: {}, {}'.format(r_bx24['result']['ID'],
# #                                                r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
# #     # except Exception as err:
# #     #     print('==Ошибка err в Portal: ', err)
# #     #     url_tok = bx24.resolve_authorize_endpoint()  # Поучение ссылки для авторизации
# #     #     url_tok = '<a href="{}">Bitrix24</a>'.format(url_tok)
# #     #     answer = "Авторизуйтесь пож-та в: {} ".format(url_tok)
# # elif message in ['/help', '/start', 'H']:
# #     # r_b24 = send_bx24_webhook('profile')
# #     r_bx24 = bx24.call_method('profile')
# #     answer = 'Добро пожаловать в Bitrix24, {}.\n Команды:\n/task или "T" - просмотр задач и их дедлайн\n' \
# #              '/profile или "P" - просмотр своего профиля\n/Leads или "Лиды" - просмотр Лидов\n' \
# #              '/L "текст" - сообщение которое разместиться в живой ленте'.format(r_bx24['result']['NAME'])
# # elif message in ['/Leads', 'Лиды']:
# #     # r_b24 = send_bx24_webhook('crm.lead.get', id=1)   # r_b24 = send_bx24_webhook('crm.lead.list')
# #     r_bx24 = bx24.call_method('crm.lead.list')
# #     leads = r_bx24['result']
# #     answer = ''
# #     for i in leads:
# #         date = str(i['BIRTHDATE'])
# #         date = date.replace('T', ' ')[:16]
# #         answer = answer + '* {}\n ->ДР: {}\n'.format(i['TITLE'], date)
# #     answer = 'Лиды получены:\n {}'.format(answer)
# # elif message in ['/task', 'T']:
# #     r_bx24 = bx24.call_method('tasks.task.list')
# #     tasks = r_bx24['result']['tasks']
# #     answer = ''
# #     for i in tasks:
# #         answer = answer + '*' + i['title'] + '\n'
# #         try:
# #             date = str(i['deadline'])
# #             date = date.replace('T', ' ')[:16]
# #         except Exception as ex:
# #             print("---Исключение: {}".format(ex))
# #             date = "не установлен"
# #         answer = answer + " --> Дедлайн: {}\n".format(str(date))
# #     answer = '*** Кол-во задач: {} ***\n{}'.format(r_bx24['total'], answer)
# # elif '/L' in message:
# #     ll = message.split()
# #     if len(ll) > 1:
# #         msg = message[3:]
# #         bx24.call_method('log.blogpost.add', {'POST_TITLE': "-*** С телеграм бота @Bitr24_bot ***-", 'POST_MESSAGE': msg})
# #     r_bx24 = bx24.call_method('log.blogpost.get')
# #     print('=====В message IF ===: ', r_bx24)
# #     r_bx24['result'] = r_bx24['result'][:7]  # уменьшение кол-ва сообщ до 7
# #     msgs = ''
# #     for i in r_bx24['result']:
# #         msgs += "{}: {}\n".format(i['DATE_PUBLISH'][11:16], i['DETAIL_TEXT'])
# #     print(msgs)
# #     answer = '-** Последние сообщения: **-\n*' + msgs
# # else:
# #     r_bx24 = bx24.call_method('user.current')  # r_bx24 = send_bx24_webhook('profile') # через webhook, убрать
# #     answer = 'Что именно хотели, {} {}?'.format(r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
# # write_json(r_bx24, file_b24)  # запись в свой файл - b24.json для дальнейшего анализа
#
# # ----------------------------
# # except Exception as err:
# #     print('==Ошибка err в Portal: ', err)
# #     url_tok = bx24.resolve_authorize_endpoint()  # Поучение ссылки для авторизации
# #     url_tok = '<a href="{}">Bitrix24</a>'.format(url_tok)
# #     answer = "Авторизуйтесь пож-та в: {} ".format(url_tok)
#
# # bitr.bx24_name = bx24.call_method('user.current')['result']['NAME']
# # r_bx24 = bx24.call_method('user.current')  # (r_ -запрос) получение словаря
# # print(r_bx24)
# # bx24.get_tokens_from_db(bitr)
# # bitr.bx24_name = bx24.call_method('user.current')['result']['NAME']
# # bitr.slug = None  # удалить слаг, чтобы начинался с имени, а не 'code'
# # bitr.chats.add(chat)         # Привязываем записи в двух таблицах. Или так: chat.bitrs.add(bitr)
# # bitr.save()       # при сохранении будет новый слаг
# # print('== Имя Б24 занесесено в базу')
# # answer = 'Вы авторизовались!!!(code прошел)'
#
# # class Bx24(Bitrix24):
# #     def __init__(self, chat_id=None):
# #         super().__init__(domain='telebot.bitrix24.ru', client_id=client_id, client_secret=client_secret)
# #         self.chat_id = chat_id
# #
# #     def get_data(self):
# #         self.chat_id = Messages.objects.first().chat.chat_id
# #         self.user_id = Messages.objects.first().chat.bitrs.first()
# #         self.access_token = Bitr.objects.get(bx24_id=self.user_id).access_token
# #         self.refresh_token = Bitr.objects.get(bx24_id=self.user_id).refresh_token
# #
# #     def save_data(self):
# #         bitr = Bitr.objects.update_or_create(bx24_id=self.user_id, defaults={'access_token': self.access_token,
# #                                                                              'refresh_token': self.refresh_token})
# #         chat = Messages.objects.first().chat
# #         chat.bitrs.add(bitr)
#
#
# # def check_tokens(chat):
# #     # bitr = chat.bitrs.latest('access_token')    # Получение экз. с послед. изменениями токена.
# #     #
# #     # bx24.access_token = bitr.access_token   # получение посл. токенов с базы
# #     # bx24.refresh_token = bitr.refresh_token
# #     # bx24.refresh_tokens()        # Обновить текущие токены (время жизни 'access_token'-1 час)
# #     # print('---00000000 обновил токены:---', bx24.get_tokens())
# #
# #     # bx24.call_method('user.current')
# #     # Out[70]: {'error': 'NO_AUTH_FOUND', 'error_description': 'Wrong authorization data'}
# #     # r_bx24 = bx24.call_method('user.current')
# #     # auth_bx24 = True
# #     # if not bx24.get_tokens():
# #
# #     # bx24 = Bitrix24('telebot.bitrix24.ru', client_id, client_secret)  # Создание экземпляра Bitrix24.
# #     # bx24_id = request.session.get('bx24_id')
# #     # try:
# #     #     bx24_id = request.session['bx24_id']
# #     # except Exception:
# #     #     pass
# #
# #     bx24 = Bx24(chat_id=chat.chat_id)
# #     # Поиск последнего Битрикс пользователя под которым заходил пользователь телеграмм(ТГ)
# #     bitr = chat.bitrs.last()
# #     if bitr:    # Заходил ли пользователь ТГ в Битрикс
# #         bx24.access_token = bitr.access_token
# #         bx24.refresh_token = bitr.refresh_token
# #         Bind.objects.update_or_create(chat_id=chat.chat_id, defaults={'bx24_id': bx24.user_id,
# #                                                                       'message': chat.messages.first().message})
# #     elif Bind.objects.filter(message="code").last():  # есть ли записи с прошедшей авторизацией
# #         bind = Bind.objects.filter(message="code").last()   # забираем пследний этот экземпляр
# #         bind.message = chat.messages.first().message    # меням на новое сообшение
# #         bind.chat_id = chat.chat_id                     # добавляем чат ID
# #         bind.update()
# #
# #         bitr.chats.add(chat)   # связывем запись чата с битрикс записью
# #
# #         bx24.user_id = bind.bx24_id     # вытаскиваем битрикс ID, по которому вытащим токены
# #         bx24.access_token = bitr.access_token
# #         bx24.refresh_token = bitr.refresh_token
# #     else:
# #         url_tok = bx24.resolve_authorize_endpoint()  # Поучение ссылки для авторизации
# #         url_tok = '<a href="{}">Bitrix24</a>'.format(url_tok)
# #         answer = "Авторизуйтесь пож-та в: {} ".format(url_tok)
# #         send_message(chat.chat_id, answer, 'html')
# #         bx24.answer = '//AUTH//'
# #
# #     # bx24.user_id = bitr.bx24_id
# #     # bx24.access_token = bitr.access_token
# #     # bx24.refresh_token = bitr.refresh_token
# #
# #     if (not bx24.access_token) or (not bx24.refresh_token):
# #         bx24.answer = '//AUTH//'
# #         print('------====//AUTH//==----, ', answer, bx24.access_token)
# #     elif bx24.access_token == 'Expires':
# #         bx24.refresh_tokens()
# #         bx24.answer = '//EXPIRES//'
# #         print('------====//EXPIRES//==----, ', answer, bx24.access_token)
# #     else:
# #         bx24.answer = None
# #     return bx24
# #
# #     # try:
# #     #     r_bx24['result']
# #     # except Exception as e:
# #     #     print('==1 Требуется аунт== {}'.format(r_bx24))
# #     #     bx24.refresh_tokens()        # Обновить текущие токены (время жизни 'access_token'-1 час)
# #     #
# #     #
# #     #     auth_bx24 = False
# #     # else:
# #     #     print('==2 Аунт не треб. == {}'.format(r_bx24))
# #     #     # bx24.refresh_tokens()        # Обновить текущие токены (время жизни 'access_token'-1 час)
# #     # if not auth_bx24:
# #     #     url_tok = bx24.resolve_authorize_endpoint()  # Поучение ссылки для авторизации
# #     #     url_tok = '<a href="{}">Переход для авторизации на Bitrix24</a>'.format(url_tok)
# #     #     # date_msg = read_json(file_bx24_tok)['expires']
# #     #     date_msg = 1578264099
# #     #     date_msg = datetime.datetime.fromtimestamp(int(date_msg)).strftime('%H:%M:%S %d-%m-%Y')
# #     #     answer = "Авторизуйтесь пож-та:\n{}\nДата действия до: {}".format(url_tok, date_msg)
# #     # else:
# #     #     pass
# #     #     # r_b24 = send_bx24_webhook('profile')  # отправка запроса в битрикс24, получение словаря (webhook in)
# #     #     # bx24 = Bitrix24('telebot.bitrix24.ru', client_id, client_secret)  # в начале
# #     #     # bx24.resolve_authorize_endpoint()
# #     #     dict_tokens = bx24.get_tokens()         # Проверить токены или были ли заменены старые токены
# #     #     print('+++++*** Проверка токенов: {}'.format(dict_tokens))
# #     #     bx24.access_token = bitr.access_token  # получение посл. токенов с базы
# #     #     bx24.refresh_token = bitr.refresh_token
# #     #     # bx24.refresh_token(refresh_token)        # Обновить текущие токены (время жизни 'access_token'-1 час)
# #     # return bx24
#
#
# # def portal(chat):
# #     # bx24 = check_tokens(chat)
# #     bx24 = Bx24(chat_id=chat.chat_id)
# #     bx24 = Bx24()
# #     bx24.get_data()
# #
# #     message = chat.messages.first().message  # находим посл.сообщение
# #     if bx24.answer:
# #         message = bx24.answer
# #         print('=========11111111111===')
# #     if message in ['/profile', 'P']:
# #         r_bx24 = bx24.call_method('user.current')   # (r_ -запрос) получение словаря
# #         print("--Профиль Б24---: {} -=- {}".format(r_bx24, type(r_bx24)))
# #         answer = 'Ваш ID: {},\nИмя: {}, {}'.format(r_bx24['result']['ID'],
# #                                                    r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
# #     elif message in ['//AUTH//']:
# #         url_tok = bx24.resolve_authorize_endpoint()  # Поучение ссылки для авторизации
# #         url_tok = '<a href="{}">Bitrix24</a>'.format(url_tok)
# #         answer = "Авторизуйтесь пож-та в: {} ".format(url_tok)
# #
# #         r_bx24 = answer
# #     elif message in ['//EXPIRES//']:
# #         answer = "==Токены обновлены=="
# #         r_bx24 = answer
# #     elif message in ['/help', '/start', 'H']:
# #         # r_b24 = send_bx24_webhook('profile')
# #         r_bx24 = bx24.call_method('profile')
# #         answer = 'Добро пожаловать в Bitrix24, {}.\n Команды:\n/task или "T" - просмотр задач и их дедлайн\n' \
# #                  '/profile или "P" - просмотр своего профиля\n' \
# #                  '/L "текст" - сообщение которое разместиться в живой ленте'.format(r_bx24['result']['NAME'])
# #     elif message == 'Лиды':
# #         # r_b24 = send_bx24_webhook('crm.lead.get', id=1)   # r_b24 = send_bx24_webhook('crm.lead.list')
# #         r_bx24 = bx24.call_method('crm.lead.list')
# #         leads = r_bx24['result']
# #         answer = ''
# #         for i in leads:
# #             date = str(i['BIRTHDATE'])
# #             date = date.replace('T', ' ')[:16]
# #             answer = answer + '* {}\n ->ДР: {}\n'.format(i['TITLE'], date)
# #         answer = 'Лиды получены:\n {}'.format(answer)
# #     elif message in ['/task', 'T']:
# #         # r_b24 = send_bx24_webhook('tasks.task.list')
# #         r_bx24 = bx24.call_method('tasks.task.list')
# #
# #         tasks = r_bx24['result']['tasks']
# #         answer = ''
# #         for i in tasks:
# #             answer = answer + '*' + i['title'] + '\n'
# #             try:
# #                 date = str(i['deadline'])
# #                 date = date.replace('T', ' ')[:16]
# #             except Exception as ex:
# #                 print("---Исключение: {}".format(ex))
# #                 date = "не установлен"
# #             answer = answer + " --> Дедлайн: {}\n".format(str(date))
# #         answer = '*** Кол-во задач: {} ***\n{}'.format(r_bx24['total'], answer)
# #     elif '/L' in message:
# #         ll = message.split()
# #         if len(ll) > 1:
# #             msg = message[3:]
# #             # send_bx24_webhook('log.blogpost.add', POST_TITLE='-*** От БОССА ***-', POST_MESSAGE=msg)
# #             bx24.call_method('log.blogpost.add', {'POST_TITLE': "-*** С телеграм бота @Bitr24_bot ***-", 'POST_MESSAGE': msg})
# #         # r_b24 = send_bx24_webhook('log.blogpost.get')    # For webhook
# #         r_bx24 = bx24.call_method('log.blogpost.get')
# #         r_bx24['result'] = r_bx24['result'][:7]  # уменьшение кол-ва сообщ до 7
# #
# #         msgs = ''
# #         for i in r_bx24['result']:
# #             msgs += "{}: {}\n".format(i['DATE_PUBLISH'][11:16], i['DETAIL_TEXT'])
# #         print(msgs)
# #         answer = '-** Последние сообщения: **-\n*' + msgs
# #     else:
# #         r_bx24 = send_bx24_webhook('profile')
# #         answer = 'Что именно хотели, {} {}?'.format(r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
# #     write_json(r_bx24, file_b24)  # запись в свой файл - b24.json для дальнейшего анализа
# #     print('---Ответ answer в =portal--: ', answer)
# #     return answer
#
#
# # def auth(request):
# #     answer = ''
# #     if request.method == 'POST':        # if request.content_type == 'application/json':
# #         r = request.body.decode('utf-8')
# #         r = json.loads(r)
# #         print("--- Откуда такое = Значение POST 'r': {}".format(r))
# #
# #     else:
# #         r = request.GET     # получение словаря от битрикс24 после авторизации пользователем
# #         try:
# #             code_id = request.GET['code']   # получение 'code'-первый автор.код, для второго шага OAuth-авторизации
# #             bx24_tokens = bx24.request_tokens(code_id)  # Запрос токенов для взаимодействия с API Б24 (=полный слвоарь)
# #             print('========bx24.request_tokens(code_id)=======: ', bx24_tokens)
# #             write_json(bx24_tokens, file_bx24_tok)      # запись в файл
# #
# #             r_bx24 = bx24.call_method('user.current')  # получаем словарь данных указ.запроса
# #             msg = Messages.objects.first()  # находим посл.сообщение
# #             chat = msg.chat                 # находим по сообщ-ю чат пользователся
# #
# #             date_expires = bx24_tokens['expires']
# #             date_expires = datetime.datetime.fromtimestamp(int(date_expires)).strftime('%H:%M:%S %d-%m-%Y')
# #
# #             data = {'bx24_id': r_bx24['result']['ID'], 'bx24_name': r_bx24['result']['NAME'],
# #                     'access_token':  bx24_tokens['access_token'], 'refresh_token': bx24_tokens['refresh_token'],
# #                     'expires': date_expires}
# #             print("*** DO BITR ***", data)
# #             bitr = Bitr.objects.update_or_create(bx24_id=data['bx24_id'], defaults=data)[0]
# #
# #             bitr.chats.add(chat)  # привязываем чат к битрикс пользователю
# #             print('++++++++++++bbb2==: {}, ++++++: {}-==='.format(msg, chat))
# #
# #             # dict_tokens = bx24.get_tokens()         # Проверить токены или были ли заменены старые токены
# #             # bx24.refresh_token()        # Обновить текущие токены (время жизни 'access_token'-1 час)
# #         except Exception as e:
# #             print('-*****-Ошибка: {}'.format(e))
# #             url_tok = bx24.resolve_authorize_endpoint()  # Поучение ссылки для авторизации#
# #             url_tok = '<a href="{}">Переход для авторизации на Bitrix24</a>'.format(url_tok)
# #             msg = Messages.objects.first()  # находим посл.сообщение
# #             chat = msg.chat
# #             bitr = chat.bitrs.latest('access_token')  # Получение экз. с послед. изменениями токена.
# #             date_expires = bitr.expires
# #             answer = "- ==auth==Авторизуйтесь пож-та: <br>\n{} <br>\n Дата действия до: {}".format(url_tok, date_expires)
# #         else:
# #             r_bx24 = bx24.call_method('user.current')
# #             answer = 'Ваш ID: {},<br>\n Имя:  {}, {}<br>\n'.format(
# #                 r_bx24['result']['ID'], r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
# #             # answer += 'Ввернитесь в телеграм: <a href="https://xn--80affa3aj0al.xn--80asehdb/#/im?p=@Bitr24_bot">' \
# #             answer += 'Вернитесь в телеграм: <a href="tg://t.me/Bitr24_bot">' \
# #                       'К Боту</a>'
# #             # write_json(r_bx24, file_b24)
# #         print("-- Битрикс24 в Auth: {}".format(answer))
# #         print("++ Запрос "r": {} ++".format(r))
# #     return HttpResponse("Ответ Bitrix24:<br>\n{}".format(answer))
#
#
# # ------------ in bitr/tg----------------------------------
# # Watching for file changes with StatReloader
# # System check identified no issues (0 silenced).
# # February 03, 2020 - 13:16:58
# # Django version 2.2.6, using settings 'djherok.settings'
# # Starting development server at http://127.0.0.1:8000/
# # Quit the server with CONTROL-C.
# # === data in "rw_chat": {'chat_id': 241462113, 'lang_code': 'ru', 'first_name': 'Marat',
# #  'last_name': 'S', 'username': 'Marat2010'}
# # === Запрос request в "Tg.POST":  <WSGIRequest: POST '/bitr24/tg/'>
# # === Запрос r в "Tg.POST":  {'update_id': 555291024, 'message': {'message_id': 860, 'from': {'id': 241462113,
# #  'is_bot': False, 'first_name': 'Marat', 'last_name': 'S', 'username': 'Marat2010', 'language_code': 'ru'},
# #  'chat': {'id': 241462113, 'first_name': 'Marat', 'last_name': 'S', 'username': 'Marat2010', 'type': 'private'}, 'date': 1580725028, 'text': 'P'}}
# # === chat в Tg.POST === 241462113, Marat
# # ------====//AUTH//==----,  //AUTH// None
# # ------====//AUTH//==----,  //AUTH// None
# # =========11111111111===
# # ---Ответ answer в =portal--:  Авторизуйтесь пож-та в: <a href="https://telebot.bitrix24.ru/oauth/authorize/?client_id=local.5e04004ad5e626.19578281&response_type=code">Bitrix24</a>
# # [03/Feb/2020 13:17:10] "POST /bitr24/tg/ HTTP/1.1" 200 6949
# # === data in "rw_chat": {'chat_id': 241462113, 'lang_code': 'ru', 'first_name': 'Marat', 'last_name': 'S', 'username': 'Marat2010'}
# # === chat in "Tg.GET"=== 241462113, Marat
# # [03/Feb/2020 13:17:15] "GET /bitr24/tg/?code=48f3375e004336860043365600000001000003526ac777f7911bf78e60de53b234fb4a&state=&domain=telebot.bitrix24.ru&member_id=9c3d69f3a517c02b62fe8efa97972add&scope=im%2Cuser%2Clog%2Cdepartment%2Ctask%2Ccrm&server_domain=oauth.bitrix.info HTTP/1.1" 200 6949
# #
#
#
# # --------------- in bitr/auth -----------------
# # [03/Feb/2020 13:12:54] "GET /admin/jsi18n/ HTTP/1.1" 200 14909
# # [03/Feb/2020 13:13:03] "GET /bitr24/ HTTP/1.1" 200 5845
# # [03/Feb/2020 13:13:05] "GET /bitr24/bitr/ HTTP/1.1" 200 3608
# # ========bx24.request_tokens(code_id)=======:  {'access_token': '5600385e004336860043365600000001000003868123288a4b5d5218708e80fe2fe6e5', 'expires': 1580728406, 'expires_in': 3600, 'scope': 'app', 'domain': 'telebot.bitrix24.ru', 'server_endpoint': 'https://oauth.bitrix.info/rest/', 'status': 'L', 'client_endpoint': 'https://telebot.bitrix24.ru/rest/', 'member_id': '9c3d69f3a517c02b62fe8efa97972add', 'user_id': 1, 'refresh_token': '467f5f5e0043368600433656000000010000034029e253d27e8bde4a68cddbabbf671f'}
# # *** DO BITR *** {'bx24_id': '1', 'bx24_name': 'Marat', 'access_token': '5600385e004336860043365600000001000003868123288a4b5d5218708e80fe2fe6e5', 'refresh_token': '467f5f5e0043368600433656000000010000034029e253d27e8bde4a68cddbabbf671f', 'expires': '14:13:26 03-02-2020'}
# # ++++++++++++bbb2==: З, ++++++: 241462113, Marat-===
# # -- Битрикс24 в Auth: Ваш ID: 1,<br>
# #  Имя:  Marat, S<br>
# # Вернитесь в телеграм: <a href="tg://t.me/Bitr24_bot">К Боту</a>
# # ++ Запрос : <QueryDict: {'code': ['62f2375e00433686004336560000000100000362c4988d9965ce66f60d9678a6364bb9'], 'state': [''], 'domain': ['telebot.bitrix24.ru'], 'member_id': ['9c3d69f3a517c02b62fe8efa97972add'], 'scope': ['im,user,log,department,task,crm'], 'server_domain': ['oauth.bitrix.info']}> ++
# # [03/Feb/2020 13:13:26] "GET /bitr24/auth/?code=62f2375e00433686004336560000000100000362c4988d9965ce66f60d9678a6364bb9&state=&domain=telebot.bitrix24.ru&member_id=9c3d69f3a517c02b62fe8efa97972add&scope=im%2Cuser%2Clog%2Cdepartment%2Ctask%2Ccrm&server_domain=oauth.bitrix.info HTTP/1.1" 200 152
#
#
#
# # def up_data_chat(**kwargs):  # update данных чата бота (запись нового, обновление существующего, чтение)
# #     data_l = {}  # Cловарь в логе, если найдется
# #     number = 0   # Номер в списке, если найдется, или последний при добавлении
# #     ch_id = read_json(file_answ)['message']['chat']['id']
# #     try:
# #         ld = read_json(file_data_bot)   # чтение списка словарей чата
# #     except (FileNotFoundError, json.decoder.JSONDecodeError):
# #         ld = []
# #     for i, l in enumerate(ld):      # Поиск записи
# #         try:
# #             number = i                  # запоминаем номер в списке, чтобы потом можно обновить
# #             if l["chat_id"] == ch_id:
# #                 data_l = l.copy()       # нашли запись в логе
# #                 break
# #         except KeyError:
# #             data_l = {}
# #     if kwargs:              # При аргументах - обновление данных
# #         if not data_l:      # Первая запись в "лог"
# #             data_l = read_ans()  # вытаскиваем из answer.json
# #             num_req = 1             # счетчик обращений к записи
# #             data_l["num_req"] = num_req
# #             if 'message' in kwargs:     # создаем список запросов
# #                 data_l['requests'] = [kwargs['message']]
# #             data_l.update(kwargs)
# #             ld.append(data_l)   # добавляем запись в лог
# #             print("--Добав.нов.данн, № в списке: {}, Кол.запросов: {}, Данные: {}".format(len(ld), num_req, kwargs))
# #         else:                              # изменение словаря для записи в лог-список
# #             num_req = data_l["num_req"]
# #             num_req += 1 if ('message' in kwargs) else 0   # если новое сообщение 'message' - увел. счетчика
# #             data_l["num_req"] = num_req
# #             date_msg = read_ans()['date_msg']
# #             data_l.update({'date_msg': date_msg})   # Обновление времени запроса
# #             if 'message' in kwargs:
# #                 try:
# #                     req = data_l['requests']
# #                 except (AttributeError, KeyError):
# #                     req = []
# #                 msg = kwargs['message']
# #                 if len(req) >= 7:
# #                     req.pop(0)              # удаляем старые запросы
# #                 req.append(msg)             # дополняем список запросов
# #                 data_l['requests'] = req
# #             data_l.update(kwargs)     # добавление новых данных в случаях 'message', 'location' 'lang'...
# #             ld[number] = data_l     # запись в список словарей чата
# #             print("--Измен.дан. № в списке: {}, Кол.запросов: {}, Данные: {}".format(number+1, num_req, kwargs))
# #         write_json(ld, file_data_bot)  # запись в файл
# #     return data_l
# #
# #
# #     # date_expires = read_json(file_bx24_tok)['expires']
# #     # date_expires = 1578264099
# #     # date_expires = bx24_tokens['expires']
# #
# #     # if request.method == 'POST':        # if request.content_type == 'application/json':
# #     #     r = request.body.decode('utf-8')
# #     #     r = json.loads(r)
# #     #     write_json(r)   # Запсиь данных чата в файла answer.json.
# #     # chat_id = r['message']['chat']['id']
# #     # message = r['message']['text']
# #     # up_data_chat(chat_id=chat_id, message=message)  # обновление данных в списке словарей чата.
# #
# #     # Вы: {'error': 'expired_token', 'error_description': 'The access token provided has expired.'}
# #     # else:
# #     #     d = read_json(file_b24)
# #     #     d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)
# #     #
# #     #     data_bot = read_json(file_data_bot)
# #     #     ans_d_bot = ""
# #     #     for i in data_bot:
# #     #         ans_d_bot += 'ID: {:>9}. Вр: {}. Польз: {:>10}. Запросов: {:>4}. Посл: {} - ({}). Яз:{}\n' \
# #     #                      ' ---/ Запросы: {} \---\n'.\
# #     #             format(i['chat_id'], i['date_msg'], i['username'], i['num_req'],
# #     #                    i['location'][0], i['location'][1], i['lang_code'], i['requests'])
# #     #
# #     #     return HttpResponse("Ответ Bitrix24:\n{}\n Данные чата:\n{}".format
# #     #                         (d, ans_d_bot), content_type="application/json")
# #
# #
# #     # @django.views.decorators.csrf.csrf_exempt
# #     # def index(request):
# #     #     if request.method == 'POST':        # if request.content_type == 'application/json':
# #     #         r = request.body.decode('utf-8')
# #     #         r = json.loads(r)
# #     #         write_json(r)   # Запсиь данных чата в файла answer.json.
# #     #         chat_id = r['message']['chat']['id']
# #     #         message = r['message']['text']
# #     #         up_data_chat(chat_id=chat_id, message=message)  # обновление данных в списке словарей чата.
# #     #
# #     #         if message in ['/profile', 'P']:
# #     #             bx24 = Bitrix24('telebot.bitrix24.ru', client_id, client_secret)
# #     #             bx24.access_token = read_json(file_bx24_tok)['access_token']
# #     #             print(bx24.call_method('user.get'))
# #     #             try:
# #     #                 r_bx24 = bx24.call_method('user.get')
# #     #                 # r_bx24 = bx24.call_method('user.get')['error']
# #     #             except Exception:
# #     #                 refresh_token = read_json(file_bx24_tok)['refresh_token']
# #     #                 # bx24.refresh_token = refresh_token
# #     #                 bx24.refresh_tokens(refresh_token=refresh_token)  # Обновить текущие токены (время жизни 'access_token'-1 час)
# #     #                 r_bx24 = bx24.call_method('user.get')
# #     #
# #     #             print("--Тест в Телеграмм Битрикс24: {}".format(r_bx24))
# #     #             answer = 'Инфо:\n'
# #     #             for i in r_bx24['result']:
# #     #                 answer = answer + '* {}: {} {}\n'.format(i['NAME'], i['PERSONAL_MOBILE'], i['EMAIL'])
# #     #
# #     #         elif message in ['/help', '/start', 'H']:
# #     #             r_bx24 = send_bx24_webhook('profile')
# #     #             answer = 'Добро пожаловать в Bitrix24, {}.\n Команды:\n/task или "T" - просмотр задач и их дедлайн\n' \
# #     #                      '/profile или "P" - просмотр своего профиля\n' \
# #     #                      '/L "текст" - сообщение которое разместиться в живой ленте'.format(r_bx24['result']['NAME'])
# #     #         elif message == 'Лиды':
# #     #             # r_bx24 = send_bx24_webhook('crm.lead.get', id=1)
# #     #             r_bx24 = send_bx24_webhook('crm.lead.list')
# #     #             leads = r_bx24['result']
# #     #             answer = ''
# #     #             for i in leads:
# #     #                 date = str(i['BIRTHDATE'])
# #     #                 date = date.replace('T', ' ')[:16]
# #     #                 answer = answer + '* {}\n ->ДР: {}\n'.format(i['TITLE'], date)
# #     #             answer = 'Лиды получены:\n {}'.format(answer)
# #     #         elif message in ['/task', 'T']:
# #     #             r_bx24 = send_bx24_webhook('tasks.task.list')
# #     #             tasks = r_bx24['result']['tasks']
# #     #             answer = ''
# #     #             for i in tasks:
# #     #                 answer = answer + '*' + i['title'] + '\n'
# #     #                 try:
# #     #                     date = str(i['deadline'])
# #     #                     date = date.replace('T', ' ')[:16]
# #     #                 except Exception as ex:
# #     #                     print("---Исключение: {}".format(ex))
# #     #                     date = "не установлен"
# #     #                 answer = answer + " --> Дедлайн: {}\n".format(str(date))
# #     #             answer = '*** Кол-во задач: {} ***\n{}'.format(r_bx24['total'], answer)
# #     #         elif '/L' in message:
# #     #             ll = message.split()
# #     #             if len(ll) > 1:
# #     #                 msg = message[3:]
# #     #                 send_bx24_webhook('log.blogpost.add', POST_TITLE='-*** От БОССА ***-', POST_MESSAGE=msg)
# #     #             r_bx24 = send_bx24_webhook('log.blogpost.get')
# #     #             r_bx24['result'] = r_bx24['result'][:7]  # уменьшение кол-ва сообщ до 7
# #     #             msgs = ''
# #     #             for i in r_bx24['result']:
# #     #                 msgs += "{}: {}\n".format(i['DATE_PUBLISH'][11:16], i['DETAIL_TEXT'])
# #     #             print(msgs)
# #     #             answer = '-** Последние сообщения: **-\n*' + msgs
# #     #         else:
# #     #             r_bx24 = send_bx24_webhook('profile')
# #     #             answer = 'Что именно хотели, {} {}?'.format(r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
# #     #         write_json(r_bx24, file_b24)  # запись в свой файл - b24.json для дальнейшего анализа
# #     #
# #     #         # answer = answ_bx24(message)
# #     #         print(answer)
# #     #         r = send_message(chat_id, text=answer)
# #     #         return HttpResponse(r, content_type="application/json")
# #     #     else:
# #     #         d = read_json(file_b24)
# #     #         d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)
# #     #
# #     #         data_bot = read_json(file_data_bot)
# #     #         ans_d_bot = ""
# #     #         for i in data_bot:
# #     #             ans_d_bot += 'ID: {:>9}. Вр: {}. Польз: {:>10}. Запросов: {:>4}. Посл: {} - ({}). Яз:{}\n' \
# #     #                          ' ---/ Запросы: {} \---\n'.\
# #     #                 format(i['chat_id'], i['date_msg'], i['username'], i['num_req'],
# #     #                        i['location'][0], i['location'][1], i['lang_code'], i['requests'])
# #     #
# #     #         return HttpResponse("Ответ Bitrix24:\n{}\n Данные чата:\n{}".format
# #     #                             (d, ans_d_bot), content_type="application/json")
# #
# #
# #     # @django.views.decorators.csrf.csrf_exempt
# #     # def tg(request):
# #     #     if request.method == 'POST':        # if request.content_type == 'application/json':
# #     #         r = request.body.decode('utf-8')
# #     #         r = json.loads(r)
# #     #         print('---r---:{}'.format(r))
# #     #         write_json(r)   # Запсиь данных чата в файла answer.json.
# #     #         chat_id = r['message']['chat']['id']
# #     #         first_name = r['message']['chat']['first_name']
# #     #         username = r['message']['chat']['username']
# #     #         message = r['message']['text']
# #     #         chat_tg = {'chat_id': chat_id, 'first_name': first_name, 'username': username}
# #     #         print('--chat_tg--{}:'.format(chat_tg))
# #     #         print('--chat_id--:{}'.format(chat_id))
# #     #         try:
# #     #             chat = Chat.objects.get(chat_id=chat_id)
# #     #
# #     #         #     chat = Chat.objects.get(chat_id=100)
# #     #         #     chat = Chat.objects.get('chat_id' = int(chat_id))
# #     #         #     print('----chat---:'.format(chat))
# #     #         except Exception:
# #     #
# #     #             chat.chat_id = chat_id
# #     #         chat.mmessage.message=message
# #     #         chat.first_name = first_name
# #     #         chat.username = username
# #     #         # chat.objects['messages'] = message
# #     #         chat.message = message
# #     #         # message.message = message
# #     #         # chat.messages = message
# #     #         chat.save()
# #     #
# #     #
# #     #         # print('---chat---{}--msg----{}'.format(chat, message))
# #     #         answer = '-Все хорошо!!!-'
# #     #         r = send_message(chat_id, text=answer)
# #     #         return HttpResponse(r, content_type="application/json")
# #     #     # def get(self, request, slug):
# #     #     #     bitr = Bitr.objects.get(slug__iexact=slug)
# #     #     #     bound_form = BitrForm(instance=bitr)
# #     #     #     return render(request, 'bitr24/bitr_update_form.html', context={'form': bound_form, 'bitr': bitr})
# #     #     #
# #     #     # def post(self, request, slug):
# #     #     #     bitr = Bitr.objects.get(slug__iexact=slug)
# #     #     #     bound_form = BitrForm(request.POST, instance=bitr)
# #     #     #
# #     #     #     if bound_form.is_valid():
# #     #     #         new_tag = bound_form.save()
# #     #     #         return redirect(new_tag)
# #     #     #     return render(request, 'bitr24/bitr_update_form.html', context={'form': bound_form, 'bitr': bitr})
# #     #     else:
# #     #         return HttpResponse('<h1>qwe QWE Редирект</h1>')
# #     #
# #     #     # bitrs = Bitr.objects.all()
# #     #     # return render(request, 'bitr24/bitrs_list.html', context={'bitrs': bitrs})
# #
# #     # bx24 = Bitrix24('telebot.bitrix24.ru', client_id, client_secret)  # в начале
# #
# #     # bx24.access_token = read_json(file_bx24_tok)['access_token']
# #     # bx24.refresh_token = read_json(file_bx24_tok)['access_token']
# #     # bitr = Bitr.objects.get(chats=chat_id)
#
# # write_json(r)   # Запсиь данных чата в файла answer.json.
# # code_id = r['code']
# #
# # r_bx24 = '--POST запрос'
# # r = json.loads(r)
# # write_json(r)   # Запсиь данных чата в файла answer.json.
#
# # url_tok = 'https://telebot.bitrix24.ru/oauth/authorize/?client_id={}' \
# #           '&response_type=code'.format(client_id)
#
# # r_bx24 = bx24.call_method('user.get', {'ID': 1})
# # r_bx24 = bx24.call_method('user.get')
#
# # url_tok = 'https://telebot.bitrix24.ru/oauth/authorize/?client_id={}' \
# #           '&response_type=code'.format(client_id)
#
# # url_tok = 'https://telebot.bitrix24.ru/oauth/authorize/?client_id={}&response_type=code'.format(client_id)
# # url_tok - URL для запроса авторизации пользователем, после 'удачи' которого получим 'code'
# # bx24 = Bitrix24('telebot.bitrix24.ru', client_id, client_secret)  # Создание экземпляра.
