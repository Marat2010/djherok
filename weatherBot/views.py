# from django.shortcuts import render
# from django.core.files import File # from pprint import pprint # from proxy_requests import ProxyRequests
# from weatherBot.const import token_telegram, token_pyowm
from django.http import HttpResponse
import requests
import json
import pyowm
import django.views.decorators.csrf
import os
# from googletrans import Translator

# local_launch = True    # True - если локально с прокси и ngrok.
local_launch = False    # True - если локально с прокси и ngrok.
if local_launch:
    token_telegram = os.environ['token_telegram2']
else:
    token_telegram = os.environ['token_telegram']
token_pyowm = os.environ['token_pyowm']
file_answer = './weatherBot/answer.json'
file_answer_city = './weatherBot/city.txt'
file_data_bot = './weatherBot/data_bot.json'
URL = 'https://api.telegram.org/bot' + token_telegram + '/'
key_tr_ya = 'trnsl.1.1.20190928T185613Z.4d1d79f81bf497a8.75037b63bf025f65040895814428eadc0438f8a4'
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
    # print("---УРЛ и Словарьв send_message перед отправкой: ", url, answer)
    if local_launch:
        r = requests.post(url, json=answer, proxies=proxies)  # add proxies on local
    else:
        r = requests.post(url, json=answer)  # remove proxies on hosting
    return r


def get_wind_direction(deg):
    direct_ru = ['С ', 'СВ', ' В', 'ЮВ', 'Ю ', 'ЮЗ', ' З', 'СЗ']
    direction = ['\u21D3', '\u21D9', '\u21D0', '\u21D6', '\u21D1', '\u21D7', '\u21D2', '\u21D8']
    # С-⇓-21D3, СВ-⇙-21D9, В-⇐-21D0, ЮВ-⇖-21D6, Ю-⇑-21D1, ЮЗ-⇗-21D7, З-⇒-21D2, СЗ-⇘-21D8
    # direct = ['\u2193', '\u2199', '\u2190', '\u2196', '\u2191', '\u2197', '\u2192', '\u2198']
    #  С-↓-2193,СВ-↙,В-←,ЮВ-↖-u2196,Ю-↑,ЮЗ-↗,З-→,СЗ-↘.

    data_bot = read_json(file_data_bot)
    try:
        language_code = data_bot["language_code"]
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


def write_json(data, filename=file_answer):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_json(filename=file_answer):
    with open(filename, 'r') as f:
        r = json.load(f)
    return r


def get_icon(status='Неизвестно', weather_code=''):
    """В 'get_icon' лучше убрать проверку 'status'. Сделать проверку только по 'weather_code'
    в словаре со списком кодов, где вытащить ключ, который будет стикером 'Emoji Unicode'
    ('https://unicode-table.com/', 'https://unicode.org/emoji/charts/full-emoji-list.html').
        Описание кодов 'weather_code' 'https://openweathermap.org/weather-conditions'"""
    dict_status = {'Clear': "\U00002600", 'Snow': "\U00002744", 'Heavy snowfall': "\U00002744\U00002744",
                   'Clouds': "\U00002601", 'Few clouds': "\U000026C5",
                   'Rain': "\U0001F327", 'Light rain': "\U00002602", 'Moderate rain': "\U00002614",
                   'Thunderstorm': "\U000026C8", 'Mist': "\U0001F301"}
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


def decrease_record(record='', n=5):
    ll = record.split()
    if len(ll) > 1 and n == 5:
        for i, val in enumerate(ll):
            ll[i] = ll[i][0:n]
        rec = '.'.join(ll)
    else:
        if len(ll) == 1 and not n == 5:
            rec = record[0:n]
        else:
            rec = record
    return rec


def city_coords(message):
    ll = message.split(',')
    if len(ll) > 1:
        try:
            float(ll[1])
        except ValueError:
            return 'city'
        else:
            ll = [l.replace(' ', '') for l in ll]
            return ll
    else:
        return 'city'


def get_observation(message, language_code):
    # global city_message
    owm = pyowm.OWM(token_pyowm, language=language_code)
    cit_coor = city_coords(message)
    if cit_coor == 'city':
        try:
            owm.weather_at_place(message)
        except Exception:
            answer_w = 'Такого города или места не знаю. Можно ввести GPS координаты. (Пример: 55.78, 49.12)'
            answer_w = translate_answ(answer_w)
            return answer_w
        else:
            # city_message = message
            with open(file_answer_city, 'w') as f:  # write str city to file
                f.write(message)

            data_bot = read_json(file_data_bot)
            data_bot["message"] = message
            write_json(data_bot, file_data_bot)

            observation = owm.weather_at_place(message)
            return observation
    else:
        try:
            owm.weather_at_coords(float(cit_coor[0]), float(cit_coor[1]))
        # except pyowm.exceptions.api_response_error.NotFoundError:
        except Exception:
            answer_w = 'Такого места не знаю. Координаты не верны. (Пример: 55.78, 49.12)'
            answer_w = translate_answ(answer_w)
            return answer_w
        else:
            # city_message = message
            with open(file_answer_city, 'w') as f:  # write str city to file
                f.write(message)

            data_bot = read_json(file_data_bot)
            data_bot["message"] = message
            write_json(data_bot, file_data_bot)

            observation = owm.weather_at_coords(float(cit_coor[0]), float(cit_coor[1]))
            return observation


def record_answer(coords, w):
    date_w = w.get_reference_time(timeformat='date')
    temp = w.get_temperature('celsius')["temp"]
    try:
        deg_wind = w.get_wind()['deg']
    except KeyError:
        deg_wind = "?"
    # key_temp = [key for key, val in w.get_temperature().items() if val == temp]
    with open(file_answer_city, 'r') as f:
        city_message = f.readline()
    answer_w = '{}: {} {}, Температура: {:4.1f} C°\n'.format(
                city_message, w.get_detailed_status(),
                get_icon(w.get_status(), w.get_weather_code()), temp)
    answer_w += 'Ветер: {:3.1f} м/c ({}°-{}).\n'.format(
                w.get_wind()["speed"], deg_wind, get_wind_direction(deg_wind))
    answer_w += 'Влажность: {} %.\nДавление: {} мм.рт.ст.\n'.format(
                w.get_humidity(), int(w.get_pressure()["press"]/1.333224))
    answer_w += 'Время(GMT+00): {}\n'.format(date_w.strftime("%H:%M %d.%m.%Y"))
    answer_w += ' Широта: {}, Долгота: {}\n'.format(coords.get_lat(), coords.get_lon())
    answer_w += ' Geonames: {}, ID:{}.'.format(coords.get_name(), coords.get_ID())
    answer_w = translate_answ(answer_w)
    # if city_coords(message) == 'city':
    #     lat = coords.get_lat()
    #     lon = coords.get_lon()
    # else:
    #     lat = message.split(',')[0]
    #     lon = message.split(',')[1]
    # link = 'https://www.google.ru/maps/@{},{},15z\n'.format(lat, lon).replace(' ', '')
    # answer_w += '\nНа карте: {}'.format(link)
    return answer_w


def see_map(message):
    data_bot = read_json(file_data_bot)
    language_code = data_bot["language_code"]

    observation = get_observation(message, language_code)
    coords = observation.get_location()
    if city_coords(message) == 'city':
        lat = coords.get_lat()
        lon = coords.get_lon()
    else:
        lat = message.split(',')[0]
        lon = message.split(',')[1]
    link = 'https://www.google.ru/maps/@{},{},15z\n'.format(lat, lon).replace(' ', '')
    answer_map = '\nНа карте: {}'.format(link)
    answer_map = translate_answ(answer_map)
    return answer_map


def answer_weather(message, language_code):
    observation = get_observation(message, language_code)
    print("Объект наблюдения: ", observation)
    if isinstance(observation, str):
        return observation  # Возврат сообщения о неудачи
    else:
        coords = observation.get_location()
        w = observation.get_weather()
        print("--Объект погды в answer_weather.--", w)

        data_bot = read_json(file_data_bot)  # Запись точки, местоположения
        data_bot["location"] = message
        write_json(data_bot, file_data_bot)
        return record_answer(coords, w)  # Формирование сообщения

# def answer_weather(message):
#     try:
#         owm.weather_at_place(message)
#     except pyowm.exceptions.api_response_error.NotFoundError:
#         answer_w = 'Такого города или места не знаю. Иностранные или некоторые города вводите на английском, ' \
#                     'например Сочи-Sochi, Киев-Kiev.'
#     else:
#         with open(file_answer_city, 'w') as f:   # write str city to file
#             f.write(message)
#         observation = owm.weather_at_place(message)
#         w = observation.get_weather()
#         date_w = w.get_reference_time(timeformat='date')
#         temp = w.get_temperature('celsius')["temp"]
#         try:
#             deg_wind = w.get_wind()['deg']
#         except KeyError:
#             deg_wind = "?"
#         answer_w = 'В городе {} {}, темп-ра: {:4.1f} C°\n'.format(w.get_detailed_status(),
#                                     get_icon(w.get_status(), w.get_weather_code()), temp)
#         answer_w += 'Ветер: {:3.1f} м/c ({}°-{})\n'.format(w.get_wind()["speed"],
#                                                            deg_wind,
#                                                            get_wind_direction(deg_wind))
#         answer_w += 'Влажн: {} %, Давл: {} мм.рт.ст.\n'.format(
#             w.get_humidity(),
#             int(w.get_pressure()["press"]/1.333224))
#         answer_w += 'Время(GMT+00): {}\n'.format(date_w.strftime("%H:%M %d.%m.%Y"))
#         answer_w += ' Где интересует погода или прогноз?:'
#     return answer_w
# ----------
# def forecast(message, days_fc=5):
#     try:
#         fc = owm.three_hours_forecast(message)
#         f = fc.get_forecast()
#         lst = f.get_weathers()
#     except pyowm.exceptions.api_response_error.NotFoundError:
#         answer_fc = 'Введите сначала город.'
#     except pyowm.exceptions.api_call_error.APICallError:
#         answer_fc = '-Введите сначала город. Возможно проблема с сетью-'
#     else:
#         answer_fc = '{} (время по GMT+00):\n'.format(message)
#         i = 0
#         for w in lst:
#             date_fc = w.get_reference_time(timeformat='date')
#             try:
#                 deg_wind = w.get_wind()['deg']
#             except KeyError:
#                 deg_wind = "?"
#             answer_fc += '{}ч:{:2}{:5.1f}C°,{:4.1f}м/с({:3}°-{:>2})\n'.format(
#                 date_fc.strftime("%d.%m %H"),
#                 get_icon(w.get_status(), w.get_weather_code()),
#                 w.get_temperature('celsius')["temp"],
#                 w.get_wind()["speed"],
#                 deg_wind,
#                 get_wind_direction(deg_wind))
#             if days_fc == 5:
#                 answer_fc = answer_fc.rstrip('\n')
#                 answer_fc += ', Вл:{:3}%, Давл:{:3}мм. {}\n'.format(
#                     w.get_humidity(),
#                     int(w.get_pressure()["press"]/1.333224),
#                     decrease_record(w.get_detailed_status()))
#             i += 1
#             if i > (days_fc*8):
#                 break
#     return answer_fc


def forecast(message, language_code, days_fc=5):
    owm = pyowm.OWM(token_pyowm, language=language_code)
    cit_coor = city_coords(message)
    try:
        if cit_coor == 'city':
            fc = owm.three_hours_forecast(message)
        else:
            observation = owm.weather_at_coords(float(cit_coor[0]), float(cit_coor[1]))
            coords = observation.get_location()
            fc = owm.three_hours_forecast(coords.get_name())
        f = fc.get_forecast()
        lst = f.get_weathers()
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer_fc = 'Введите город или координаты. (Пример: 55.78, 49.12)'
        answer_fc = translate_answ(answer_fc)
        answer_fc = '{}\n'.format(answer_fc)

    except pyowm.exceptions.api_call_error.APICallError:
        answer_fc = 'Не могу дать прогноз в этой точке. Введите ближайший город.'
        answer_fc = translate_answ(answer_fc)
        answer_fc = '{}\n'.format(answer_fc)
    else:
        answer_fc = '{} (время GMT+00):'.format(message)
        answer_fc = translate_answ(answer_fc)
        answer_fc = '{}\n'.format(answer_fc)
        i = 0
        for w in lst:
            date_fc = w.get_reference_time(timeformat='date')
            try:
                deg_wind = w.get_wind()['deg']
            except KeyError:
                deg_wind = "?"
            answer_fc += '{}{}:{:2}{:5.1f}C°,{:4.1f}{}({:3}°-{:>2})\n'.format(
                date_fc.strftime("%d.%m %H"), decrease_record(translate_answ("ч"), 1),
                get_icon(w.get_status(), w.get_weather_code()),
                w.get_temperature('celsius')["temp"],
                w.get_wind()["speed"], decrease_record(translate_answ("м/с"), 3),
                deg_wind, get_wind_direction(deg_wind))
            if days_fc == 5:
                answer_fc = answer_fc.rstrip('\n')
                # answer_fc += '. Вл:{:3}%, Давл:{:3}мм. {:>6} - {:>10} :{:4}-{:4}\n'.format(
                # answer_fc += '. Вл:{:3}%, Давл:{:3}мм. {:>10}:\n'.format(
                answer_fc += '. {}:{:3}%. {}:{:3}{}. {:>10}\n'.format(
                    decrease_record(translate_answ("Влажность"), 2),
                    w.get_humidity(), decrease_record(translate_answ("Давление"), 4),
                    int(w.get_pressure()["press"]/1.333224), decrease_record(translate_answ("мм."), 2),
                    # w.get_weather_icon_name(), w.get_status(), w.get_weather_code())
                    decrease_record(w.get_detailed_status()))
            i += 1
            if i > (days_fc * 8):
                break
    # answer_fc = translate_answ(answer_fc)
    return answer_fc


def data_bot_rw(rw, **kwargs):
    pass
    # if rw == 'write':
    #     data_bot = read_json(file_data_bot)
    #
    #     data_bot["chat][id"] = chat_id
    #
    #     data_bot["language_code"] = language_code
    #     data_bot["chat]["message"] = message
    #     write_json(data_bot, file_data_bot)
    # else:
    #     data_bot = read_json(file_data_bot)
    #     return data_bot
    #
        # if data_bot["language_change"] == 'True':
        #     language_code = data_bot["language_code"]
        # else:
        #     pass


def translate_answ(message):
    data_bot = read_json(file_data_bot)
    # language_code = 'ru-{}'.format(data_bot["language_code"])
    try:
        language_code = data_bot["language_code"]
    except KeyError:
        language_code = 'en'
    answer_tr = message
    if not language_code == 'ru':
        data = {'key': key_tr_ya, 'lang': language_code, 'text': message}  # Параметры запроса
        try:
            r = requests.post(url_trans, data=data).json()
            # message = r['text'][0] if r['code'] == 200 else message = '--Could not translate--'
            if r['code'] == 200:
                answer_tr = r['text'][0]
            else:
                answer_tr = '--Could not translate- not 200-'
        except Exception:
            answer_tr = '--Could not translate--'
    return answer_tr

#         if not (language_code == 'ru'):
#             # message = translator.translate(message, dest='ru').text
#             message = translator.translate(message, src='ru', dest=language_code).text


@django.views.decorators.csrf.csrf_exempt
def index(request):
    if request.method == 'POST':        # if request.content_type == 'application/json':
        with open(file_answer_city, 'r') as f:
            city_message = f.readline()
        print("---Пред.сообш (Город):", city_message, type(city_message))
        r = request.body.decode('utf-8')
        r = json.loads(r)
        write_json(r)
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        try:
            language_code = r['message']['from']['language_code']
        except KeyError:
            language_code = 'en'
        data_bot = read_json(file_data_bot)
        try:
            language_code = data_bot["language_code"]
        except Exception:
            data_bot["language_code"] = language_code
        data_bot["chat_id"] = chat_id
        data_bot["message"] = message
        write_json(data_bot, file_data_bot)

        print('---код lang в начале:', language_code)
        print("---Чат ID и тек сообщ:", chat_id, type(chat_id), message, type(message))
        if '/start' in message:
            answer = 'Привет, {}.\n/help для помощи'.format(r['message']['chat']['first_name'])
        elif message in ['/help', 'H']:
            answer = 'Посмотреть погоду в городе, или по координатам (Пример: 55.78, 49.12).\n' \
                     'Иностранные или некоторые города вводите на английском (Пример: Сочи, Киев),' \
                     ' можно добавить код страны через запятую (New York, US).\n Команды:\n' \
                     '/fc_short или "S": - Короткий прогноз (2 дня)\n' \
                     '/fc_full или "F":- Полный прогноз (5 дней) с интервалом в 3 часа.\n' \
                     '/map или "M": - Посмотреть место на карте, если неуверенны, что задали нужное вам место\n' \
                     'И не забываем, время по Гринвичу (GMT+00).'
            answer = translate_answ(answer)
        elif message in ['/fc_short', 'S']:
            days_fc = 2
            answer = forecast(city_message, language_code, days_fc)
        elif message in ['/fc_full', 'F']:
            answer = forecast(city_message, language_code)
        elif message in ['/map', 'M']:
            answer = see_map(city_message)
        elif '/l' in message:
            try:
                if message.find(',') == -1:
                    ll = message.split()
                else:
                    ll = message.split(',')
                ll = [l.replace(' ', '') for l in ll]
                language_code = ll[1]
                # res = [x for x in lst if x % 3 == 0]
            except Exception:
                answer = "Не верно введено!"
                # answer = translate_answ(answer)
                language_code = 'en'
            else:
                data_bot = read_json(file_data_bot)
                data_bot["language_code"] = language_code
                data_bot["language_change"] = "True"
                write_json(data_bot, file_data_bot)
                answer = 'Изменен язык на "{}"\n ru,en,zh-китай,uk-украин,de-нем,' \
                         'fr-франц,it-италь,es-испан,ja-япон,tr-турец,ar-арабск...' \
                         '(https://yandex.ru/dev/translate/doc/dg/concepts/api-' \
                         'overview-docpage/)\n'.format(language_code)
            owm = pyowm.OWM(token_pyowm, language=language_code)
            print(owm)
        elif message in ['R']:
            answer = answer_weather(city_message, language_code)
        else:
            answer = answer_weather(message, language_code)
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json()
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)
        with open(file_answer_city, 'r') as f:
            city_message = f.readline()
        return HttpResponse("Последнее сообщение:\n" + d + "\nПосл. город: " + city_message,
                            content_type="application/json")

# fdfdffd---
# if __name__ == '__main__':
#     pass
# ------------
# "zh-CN" -китайский упрощенный в гугл переводчике, "zh" - в OWM

# def translate_answ(message):
#     translator = Translator()
#     data_bot = read_json(file_data_bot)
#     language_code = data_bot["language_code"]
#     try:
#         language_code = 'zh-CN' if language_code == 'zh' else language_code
#         # if language_code == 'zh':
#         #     language_code = 'zh-CN'
#         if not (language_code == 'ru'):
#             # message = translator.translate(message, dest='ru').text
#             message = translator.translate(message, src='ru', dest=language_code).text
#     except Exception:
#         # message = translator.translate(message, dest='en').text
#         message = message
#         # print("--- Не могу перевести----")
#     return message





