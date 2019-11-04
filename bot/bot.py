# -*- coding: utf-8 -*-
import config
import telebot
TOKEN = '919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE'
# https://api.telegram.org/bot856048822:AAG2vyULOMJ_xflmyAxU5KL-W-z5DyhJ9Gg/setWebhook?url=https://edcd2e43.ngrok.io/bot/

bot = telebot.TeleBot("TOKEN")


@bot.message_handler(content_type=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
     bot.polling(none_stop=True)

