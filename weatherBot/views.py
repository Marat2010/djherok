# from django.shortcuts import render
# from django.core.files import File # from pprint import pprint # from proxy_requests import ProxyRequests
# from weatherBot.const import token_telegram, token_pyowm
from django.http import HttpResponse
import requests
import json
import pyowm
import django.views.decorators.csrf
import os
import datetime

# from googletrans import Translator

# local_launch = True    # True - если локально с прокси и ngrok.
local_launch = False    # True - если локально с прокси и ngrok.
if local_launch:
    token_telegram = os.environ['token_telegram2']
else:
    token_telegram = os.environ['token_telegram']
token_pyowm = os.environ['token_pyowm']
file_answ = './weatherBot/answer.json'
file_answer_city = './weatherBot/city.txt'
file_data_bot = './weatherBot/data_bot.json'
URL = 'https://api.telegram.org/bot' + token_telegram + '/'
token_trans_ya = os.environ['token_trans_ya']
url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
# owm = pyowm.OWM(token_pyowm, language='ru')
# proxies = {'https': 'https://178.32.55.52:443/', 'http': 'https://103.101.253.18:443/'}
# proxies = {'https': 'https://ua-139-170-1.fri-gate0.biz:443/'}
# Искать прокси с портом 443 ( https://awmproxy.com/freeproxy.php )
# proxies = {'https': 'https://70.89.113.137:443/'} .138 USA
proxies = {'https': 'https://70.89.113.137:443/'}
# proxies = {'https': 'https://46.151.83.231:443/'}
# proxies = {'https': 'https://203.162.21.216:8080/'}


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


def get_icon(status='Неизвестно', weather_code=''):
    """В 'get_icon' лучше убрать проверку 'status'. Сделать проверку только по 'weather_code'
    в словаре со списком кодов, где вытащить ключ, который будет стикером 'Emoji Unicode'
    ('https://unicode-table.com/', 'https://unicode.org/emoji/charts/full-emoji-list.html').
        Описание кодов 'weather_code' 'https://openweathermap.org/weather-conditions'"""
    dict_status = {'Clear': "\u2600", 'Snow': "\u2744", 'Heavy snowfall': "\u2744\u2744", 'Clouds': "\u2601",
                   'Few clouds': "\u26C5", 'Rain': "\U0001F327", 'Light rain': "\u2602", 'Moderate rain': "\u2614",
                   'Thunderstorm': "\u26C8", 'Mist': "\U0001F301", 'Smoke': "\U0001F32B", 'Haze': "\U0001F32B"}
    # Туман Mist: мост-1F301, 1F32B, Снег:- U+1F328,  2744. Снег U+2746 \U00002744 ❅ ❅❄❅❄ chr(10054)
    if status == 'Clouds':
        if weather_code in [801, 802]:
            status = 'Few clouds'
    if status == 'Snow':
        if weather_code == 622:
            status = 'Heavy snowfall'
    if status == 'Rain':
        if weather_code == 500:
            status = 'Light rain'
        elif weather_code == 501:
            status = 'Moderate rain'
    try:
        r = dict_status[status]
    except KeyError:
        r = '-"\U00002753"-'
    return r


def get_wind_direct(deg):
    direct_ru = ['С ', 'СВ', ' В', 'ЮВ', 'Ю ', 'ЮЗ', ' З', 'СЗ']
    direction = ['\u21D3', '\u21D9', '\u21D0', '\u21D6', '\u21D1', '\u21D7', '\u21D2', '\u21D8']
    # С-⇓-21D3, СВ-⇙-21D9, В-⇐-21D0, ЮВ-⇖-21D6, Ю-⇑-21D1, ЮЗ-⇗-21D7, З-⇒-21D2, СЗ-⇘-21D8
    #  С-↓-2193, СВ-↙-2199 ,В-←-2190, ЮВ-↖-2196, Ю-↑-2191, ЮЗ-↗-2197, З-→-2192, СЗ-↘-2198.
    try:
        language_code = up_data_chat()["lang_code"]
    except KeyError:
        language_code = 'en'
    if language_code == 'ru':
        direction = direct_ru

    res = "\U00002753"
    for i in range(0, 8):
        try:
            deg = int(deg)
        except ValueError:
            res = "\U00002753"
            break
        step = 45.
        min_c = i*step - 45/2.
        max_c = i*step + 45/2.
        if i == 0 and deg > 360-45/2.:
            deg = deg - 360
        if (deg >= min_c) and (deg <= max_c):
            res = direction[i]
            break
    return res


def transl_ans(msg):
    try:
        language_code = up_data_chat()["lang_code"]
    except KeyError:
        language_code = 'en'
    answer_tr = msg
    if not language_code == 'ru':
        data = {'key': token_trans_ya, 'lang': language_code, 'text': msg}  # Параметры запроса
        try:
            r = requests.post(url_trans, data=data).json()
            answer_tr = r['text'][0] if r['code'] == 200 else '---*** Could not translate ***---'
        except Exception:
            answer_tr = '---*** Could not translate ***---'
    return answer_tr


def see_map():
    lat = up_data_chat()['location'][3]
    lon = up_data_chat()['location'][4]
    # link = 'https://www.google.ru/maps/@{},{},14z\n'.format(lat, lon).replace(' ', '')
    link = 'https://www.google.ru/maps/@{},{},14z\n'.format(lat, lon)
    answer_map = '\n{}: {}'.format(transl_ans("На карте"), link)
    return answer_map


def decrease_record(record='', n=5):
    lr = record.split()
    if len(lr) > 1 and n == 5:
        for i, val in enumerate(lr):
            lr[i] = lr[i][0:n]
        rec = '.'.join(lr)
    elif n == 2 or n == 4:
        for i, val in enumerate(lr):
            lr[i] = lr[i][0:n]
        rec = lr[1] if len(lr) == 2 else lr[0]
    else:
        if len(lr) == 1 and not n == 5:
            rec = record[0:n]
        else:
            rec = record
    return rec


def forecast(d_fc=5):
    lang = up_data_chat()["lang_code"]
    owm = pyowm.OWM(token_pyowm, language=lang)
    try:
        msg = up_data_chat()['location'][0]
        cit_coord = city_coords(msg)
        if cit_coord == 'city':
            fc = owm.three_hours_forecast(msg)
        else:
            obs = owm.weather_at_coords(float(cit_coord[0]), float(cit_coord[1]))
            coords = obs.get_location()
            fc = owm.three_hours_forecast(coords.get_name())
        f = fc.get_forecast()
        lst = f.get_weathers()
    except (pyowm.exceptions.api_response_error.NotFoundError, KeyError):
        answer_fc = 'Введите город или координаты. (Пример: 55.78, 49.12)'
        answer_fc = transl_ans(answer_fc)
        answer_fc = '{}\n'.format(answer_fc)

    except pyowm.exceptions.api_call_error.APICallError:
        answer_fc = 'Не могу дать прогноз в этой точке. Введите ближайший город.'
        answer_fc = transl_ans(answer_fc)
        answer_fc = '{}\n'.format(answer_fc)
    else:
        answer_fc = '{} (время GMT+00):'.format(msg)
        answer_fc = transl_ans(answer_fc)
        answer_fc = '{}\n'.format(answer_fc)
        h_dec_tr = decrease_record(transl_ans("ч"), 1)
        mc_dec_tr = decrease_record(transl_ans("м/с"), 3)
        hu_dec_tr = decrease_record(transl_ans("Влажность"), 2)
        pr_dec_tr = decrease_record(transl_ans("Давление"), 4)
        mm_dec_tr = decrease_record(transl_ans("мм."), 2)
        i = 0
        for w in lst:
            date_fc = w.get_reference_time(timeformat='date')
            try:
                deg_wind = w.get_wind()['deg']
            except KeyError:
                deg_wind = "?"
            answer_fc += '{}{}:{:2}{:5.1f}C°,{:4.1f}{}({:3}°-{:>2})\n'.format(
                date_fc.strftime("%d.%m %H"), h_dec_tr,
                get_icon(w.get_status(), w.get_weather_code()),
                w.get_temperature('celsius')["temp"],
                w.get_wind()["speed"], mc_dec_tr,
                deg_wind, get_wind_direct(deg_wind))
            if d_fc == 5:
                answer_fc = answer_fc.rstrip('\n')
                # answer_fc += '. Вл:{:3}%, Давл:{:3}мм. {:>10}:\n'.format(
                answer_fc += '. {}:{:3}%. {}:{:3}{}. {:>10}\n'.format(
                    hu_dec_tr,
                    w.get_humidity(), pr_dec_tr,
                    int(w.get_pressure()["press"]/1.333224), mm_dec_tr,
                    # w.get_weather_icon_name(), w.get_status(), w.get_weather_code())
                    # decrease_record(transl_ans(w.get_detailed_status())))
                    decrease_record(w.get_detailed_status()))
            i += 1
            if i > (d_fc * 8):
                break
    return answer_fc


def rec_ans(w):
    date_w = w.get_reference_time(timeformat='date')
    temp = w.get_temperature('celsius')["temp"]
    try:
        deg_wind = w.get_wind()['deg']
    except KeyError:
        deg_wind = "?"
    data = up_data_chat()

    msg = data["location"][0]
    geo_names = data["location"][1]
    geo_id = data["location"][2]
    lat = data["location"][3]
    lon = data["location"][4]

    answer_w = '{}: {} {}, Температура: {:4.1f} C°\n'.format(
                msg, w.get_detailed_status(),
                get_icon(w.get_status(), w.get_weather_code()), temp)
    answer_w += 'Ветер: {:3.1f} м/c ({}°-{}).\n'.format(
                w.get_wind()["speed"], deg_wind, get_wind_direct(deg_wind))
    answer_w += 'Влажность: {} %.\nДавление: {} мм.рт.ст.\n'.format(
                w.get_humidity(), int(w.get_pressure()["press"]/1.333224))
    answer_w += 'Время(GMT+00): {}\n'.format(date_w.strftime("%H:%M %d.%m.%Y"))
    answer_w += ' Широта: {}, Долгота: {}\n'.format(lat, lon)
    answer_w += ' Geonames: {}, ID:{}.'.format(geo_names, geo_id)
    answer_w = transl_ans(answer_w)
    return answer_w


def get_locate(obs):     # получение данных о точке
    try:
        coords = obs.get_location()  # получение координат, ID, Geonames, страну(country-RU)
    except AttributeError:
        print("---*** Ошибка в нахождении координат ***---")
    geo_names = coords.get_name()  # Geo_names
    geo_id = coords.get_ID()  # ID
    lat = coords.get_lat()  # широта
    lon = coords.get_lon()  # долгота
    location = [geo_names, geo_id, lat, lon]  # хранение информации о точка в таком порядке (0-будет само сообщение)
    return location


def city_coords(msg):       # проверка сообщения на имя или координаты
    l_msg = msg.split(',')
    if len(l_msg) > 1:
        try:
            float(l_msg[1])
        except ValueError:
            return 'city'
        else:
            l_msg = [l.replace(' ', '') for l in l_msg]
            return l_msg
    else:
        return 'city'


def get_obs(msg):
    lang = up_data_chat()["lang_code"]
    owm = pyowm.OWM(token_pyowm, language=lang)    # уст-ка языка для объекта OWM.
    cit_coord = city_coords(msg)                   # проверка сообщения на имя или координаты
    try:
        if cit_coord == 'city':
            obs = owm.weather_at_place(msg)        # получение объекта точки наблюдения по имени
        else:
            obs = owm.weather_at_coords(float(cit_coord[0]), float(cit_coord[1]))
    except Exception:
        answer_w = 'Такого города или места не знаю. Можно ввести GPS координаты. (Пример: 55.78, 49.12)'
        answer_w = transl_ans(answer_w)
        return answer_w
    else:
        location = get_locate(obs)        # получение данных о точке
        location.insert(0, msg)          # добавим нулевым элементом в список само сообщение
        up_data_chat(location=location)    # запись словаря данных в файл "лог"
        return obs


def answer_weather(msg):
    if msg == 'R':
        try:
            msg = up_data_chat()['location'][0]
        except Exception:
            msg = 'KAZAN, RU'
    obs = get_obs(msg)             # получение объекта точки наблюдения
    if isinstance(obs, str):
        return obs            # Возврат сообщения о неудачи
    else:
        w = obs.get_weather()
        return rec_ans(w)             # Формирование сообщения


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
        username = data_answer['message']['chat']['username']
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
            data_l.update(kwargs)
            ld.append(data_l)   # добавляем запись в лог
            print("--Добав.нов.данн, № в списке: {}, Кол.запросов: {}, Данные: {}".format(len(ld), num_req, kwargs))
        else:                              # изменение словаря для записи в лог-список
            num_req = data_l["num_req"]
            num_req += 1 if ('message' in kwargs) else 0   # если новое сообщение 'message' - увел. счетчика
            data_l["num_req"] = num_req
            date_msg = read_ans()['date_msg']
            data_l.update({'date_msg': date_msg})   # Обновление времени запроса
            data_l.update(kwargs)     # добавление новых данных в случаях 'message', 'location' 'lang'...
            ld[number] = data_l     # запись в список словарей чата
            print("--Измен.дан. № в списке: {}, Кол.запросов: {}, Данные: {}".format(number+1, num_req, kwargs))
        write_json(ld, file_data_bot)  # запись в файл
    return data_l


@django.views.decorators.csrf.csrf_exempt
def index(request):
    if request.method == 'POST':        # if request.content_type == 'application/json':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        write_json(r)   # Запсиь данных чата в файла answer.json.
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        up_data_chat(chat_id=chat_id, message=message)  # обновление данных в списке словарей чата.

        if '/start' in message:
            first_name = up_data_chat()['first_name']
            answer = 'Привет, {}.\n/help для помощи'.format(first_name)
        elif message in ['/help', 'H']:
            answer = 'Посмотреть погоду в городе, или по координатам (Пример: 55.78, 49.12). \n' \
                     'Некоторые города вводите на английском языке (Пример: Сочи, Киев),' \
                     ' можно добавить код страны через запятую (New York, US). \n Команды:\n' \
                     '/fc_short или "S": - Короткий прогноз (2 дня)\n' \
                     '/fc_full или "F":- Полный прогноз (5 дней) с интервалом в 3 часа. Для удобства' \
                     ' просмотра лучше повернуть экран в книжный режим\n' \
                     '/map или "M": - Посмотреть место на карте, если неуверенны, что задали нужное вам место\n' \
                     '/l ** - Поменять язык (ru, en, de, fr, zh,... подставить вместо **). ' \
                     'Перевод осуществлен Yandex переводчиком.\n' \
                     'И не забываем, время по Гринвичу (GMT+00).'
            answer = transl_ans(answer)
        elif message in ['/fc_short', 'S']:
            days_fc = 2
            answer = forecast(days_fc)
        elif message in ['/fc_full', 'F']:
            answer = forecast()
        elif message in ['/map', 'M']:
            answer = see_map()
        elif '/l' in message:
            try:
                if message.find(',') == -1:
                    ll = message.split()
                else:
                    ll = message.split(',')
                ll = [l.replace(' ', '') for l in ll]
                lang_code = ll[1]
            except Exception:
                lang_code = 'en'
                answer = "Не верно введено!\n Установлено: 'en'"
            else:
                up_data_chat(lang_code=lang_code, lang_change=True)
                answer = 'Изменен язык на "{}"\n ru,en,zh-китай,uk-украин,de-нем,' \
                         'fr-франц,it-италь,es-испан,ja-япон,tr-турец,ar-арабск...' \
                         '(https://yandex.ru/dev/translate/doc/dg/concepts/api-' \
                         'overview-docpage/)\n'.format(lang_code)
            up_data_chat(lang_code=lang_code)
        elif message in ['R']:
            answer = answer_weather(message)
        else:
            answer = answer_weather(message)
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json()
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)

        data_bot = read_json(file_data_bot)
        # data_bot = json.dumps(data_bot, ensure_ascii=False, sort_keys=True)
        ans_d_bot = ""
        for i in data_bot:
            ans_d_bot += 'Чат: {:>9}. Время: {}. Польз: {:>10}. Запросов: {:>4}. Посл.запрос: {} - ({}).\n'.\
                format(i['chat_id'], i['date_msg'], i['username'], i['num_req'], i['location'][0], i['location'][1])

        return HttpResponse("Последнее сообщение:\n {}\n\n Данные чата:\n{}".format
                            (d, ans_d_bot), content_type="application/json")


# res = [x for x in lst if x % 3 == 0]
# fdfdffd---
# if __name__ == '__main__':
#     pass
# ------------
# "zh-CN" -китайский упрощенный в гугл переводчике, "zh" - в OWM

# def translate_answ(message):
#     translator = Translator()
#     data_bot = read_json(file_data_bot)
#     lang_code = data_bot["lang_code"]
#     try:
#         lang_code = 'zh-CN' if lang_code == 'zh' else lang_code
#         # if lang_code == 'zh':
#         #     lang_code = 'zh-CN'
#         if not (lang_code == 'ru'):
#             # message = translator.translate(message, dest='ru').text
#             message = translator.translate(message, src='ru', dest=lang_code).text
#     except Exception:
#         # message = translator.translate(message, dest='en').text
#         message = message
#         # print("--- Не могу перевести----")
#     return message





