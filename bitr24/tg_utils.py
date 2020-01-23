import datetime
import json
import requests
import os

file_answ = './bitr24/answer.json'
file_data_bot = './bitr24/data_bot.json'

local_launch = True    # True - если локально с прокси и ngrok (для Телеграмм).
# local_launch = False    # False - если хостинг, без прокси (для Телеграмм).
if local_launch:
    token_telegram = os.environ['token_telegram3']
else:
    token_telegram = os.environ['token_telegram2']
URL = 'https://api.telegram.org/bot' + token_telegram + '/'
# proxies = {'https': 'https://70.89.113.137:443/'}
proxies = {'https': 'https://94.135.230.163:443/'}


def write_json(data, filename=file_answ, wa='w'):
    with open(filename, wa) as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


def read_json(filename=file_answ):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


def send_message(chat_id, text='--Привет, привет!-- )'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
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
        date_msg = datetime.datetime.fromtimestamp(int(date_msg)).strftime('%H:%M:%S %d-%m-%Y')
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


