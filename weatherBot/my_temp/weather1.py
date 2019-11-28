import requests
import json
import datetime
# from weatherBot.const import token_telegram, token_pyowm
import pyowm

token_pyowm = '1c4167b8491542040e7654217ecf9786'

owm = pyowm.OWM(token_pyowm, language='ru')
file_answer = './answer_weat1.json'
city_message = 'Казань, RU'
# days_fc = 5  #days of forecast


def get_wind_direction(deg):
    l = ['С ', 'СВ', ' В', 'ЮВ', 'Ю ', 'ЮЗ', ' З', 'СЗ']
    for i in range(0, 8):
        step = 45.
        min_c = i*step - 45/2.
        max_c = i*step + 45/2.
        if i == 0 and deg > 360-45/2.:
            deg = deg - 360
        if (deg >= min_c) and (deg <= max_c):
            res = l[i]
            break
    return res


def write_json(data, filename=file_answer): # write str city to file
    with open(filename, 'w') as f:
        f.write(data)


def read_json(filename=file_answer):
    with open(filename, 'r') as f:
        r = f.readline()
    return r


def answer_weather(message):
    global city_message
    try:
        owm.weather_at_place(message)
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer_w = 'Такого города или места не знаю. Иностранные или некоторые города вводите на английском, ' \
                    'например Сочи-Sochi, Киев-Kiev.'
    else:
        city_message = message  # write city
        observation = owm.weather_at_place(message)
        w = observation.get_weather()
        date_w = w.get_reference_time(timeformat='date')
        temp = w.get_temperature('celsius')["temp"]
        answer_w = 'В городе {}, темп-ра: {:4.1f} C°\n'.format(w.get_detailed_status(), temp)
        answer_w += 'Ветер: {:3.1f} м/c ({}°-{}).\n'.format(
            w.get_wind()["speed"],
            w.get_wind()["deg"],
            get_wind_direction(w.get_wind()["deg"]))
        answer_w += 'Влажн: {} %, Давл: {} мм.рт.ст.\n'.format(
            w.get_humidity(),
            int(w.get_pressure()["press"]/1.333224))
        answer_w += 'Время(GMT+00): {}\n'.format(date_w.strftime("%H:%M %d.%m.%Y"))
    return answer_w


def forecast(message, days_fc=5):
    try:
        fc = owm.three_hours_forecast(message)
        f = fc.get_forecast()
        lst = f.get_weathers()
    except pyowm.exceptions.api_response_error.NotFoundError:
        answer_fc = 'Введите сначала город.'
    except pyowm.exceptions.api_call_error.APICallError:
        answer_fc = '-Введите сначала город. Возможно проблема с сетью-'
    else:
        answer_fc = '{} (время по GMT+00):\n'.format(message)
        i = 0
        for w in lst:
            date_fc = w.get_reference_time(timeformat='date')
            answer_fc += '{}ч.: {:4.1f} C°, {:3.1f}м/с({:3}°-{:2})\n'.format(
                date_fc.strftime("%d.%m %H"),
                w.get_temperature('celsius')["temp"],
                w.get_wind()["speed"],
                w.get_wind()["deg"],
                get_wind_direction(w.get_wind()["deg"]))
            if days_fc == 5:
                answer_fc = answer_fc.rstrip('\n')
                answer_fc += ', Вл:{:3}%, Давл:{:3}мм. {}\n'.format(
                    w.get_humidity(),
                    int(w.get_pressure()["press"]/1.333224),
                    w.get_detailed_status())
            i += 1
            if i > (days_fc * 8):
                break
    return answer_fc


if __name__ == '__main__':
    while 1 == 1:
        message = input('Где интересует погода или прогноз? : \n')
        # if ('/stop' or "стоп") == message:
        if message in ['/stop', "стоп"]:
            print('Погода в городе ....Спасибо .')
            break
        elif '/help' in message:
            answer = ' Показывет погоду в городе.\
                    \nИностранные или некоторые города вводите на английском, '\
                     'например Сочи-Sochi, Киев-Kiev, можно добавить код ' \
                     'страны через запятую (New York,US).\n' \
                     'По нажатию "/..." - выбор Полного(5 дней) или Короткого(2 дня) прогноза с интервалом 3 часа.\n' \
                     'И не забываем, время по Гринвичу (GMT+00).'
        elif message in ['/fc_small', 'короче']:
            days_fc = 2
            answer = forecast(city_message, days_fc)
        elif message in ['/fc_full', 'полный']:
            answer = forecast(city_message)
        else:
            answer = answer_weather(message)
        print(answer)
print('Удачи )')



        # t1 = lst[1]
        # date_fc = t1.get_reference_time(timeformat='date')
        # print(date_fc, type(date_fc))
        # date = date_fc.strftime("%d.%m %H:%M")
        # print(date, type(date))

# fc = owm.three_hours_forecast('kazan')
# f = fc.get_forecast()
# lst = f.get_weathers()
# # print(f)
# # print(lst)
# for weather in lst:
#     # print(weather.get_reception_time('date'))
#     print(weather.get_reference_time('iso'), weather.get_detailed_status(),\
#           weather.get_temperature('celsius')["temp"])

# # Query for 3 hours weather forecast for the next 5 days over London
# >>> fc = owm.three_hours_forecast('London,uk')
#
# You can query for daily forecasts using:
# # Query for daily weather forecast for the next 14 days over London
# >>> fc = owm.daily_forecast('London,uk')
#
# # Daily weather forecast just for the next 6 days over London
# >>> fc = owm.daily_forecast('London,uk', limit=6)

