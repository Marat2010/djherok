import telebot
import pyowm
import constants


bot = telebot.TeleBot(constants.token_telegram)
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


if __name__ == '__main__':
    bot.polling(none_stop=True)

