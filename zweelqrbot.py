import telebot
import config
import qrcode
import random
import os


bot = telebot.TeleBot(config.TOKEN)


def log(message):
    log_message_none = f'[<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>] {message.from_user.first_name} "{message.from_user.username}": {message.text}'
    log_message = f'[<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>] {message.from_user.first_name} "{message.from_user.username}" {message.from_user.last_name}: {message.text}'
    bot.send_message(config.logchannelid, f'{message}')
    bot.send_chat_action(message.chat.id, 'typing')
    if message.from_user.last_name == None:
        bot.send_message(config.logpm, log_message_none, disable_web_page_preview=None,
                         reply_to_message_id=None, reply_markup=None, parse_mode='html', disable_notification=True)
    else:
        bot.send_message(config.logpm, log_message, disable_web_page_preview=None,
                         reply_to_message_id=None, reply_markup=None, parse_mode='html', disable_notification=True)


@bot.message_handler(commands=['start'])
def start_hello(message):
    log(message)
    if message.from_user.last_name == None:
        bot.send_message(
            message.chat.id, f'Привет, {message.from_user.first_name}!\n\nЭтот бот преобразовает текст и стикеры в <a href="https://ru.wikipedia.org/wiki/QR-%D0%BA%D0%BE%D0%B4">QR-код</a>.', parse_mode='html', disable_web_page_preview=False)
    else:
        bot.send_message(
            message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!\n\nЭтот бот создает QR-код. Просто нипиши ему что-нибудь. Или отправь стикер, чтобы получить информацию о нем.')


def qr_gen(message):
    log(message)
    try:
        qr = qrcode.make(message.text)
        name_qrcode = random.randrange(99)
        qr.save(f"/var/www/pybot/qrbot/qr/{name_qrcode}.png")
        qrpic = open(f"/var/www/pybot/qrbot/qr/{name_qrcode}.png", 'rb')
        bot.send_chat_action(message.chat.id, 'upload_photo')
        bot.send_photo(message.chat.id, qrpic,
                       reply_to_message_id=message.message_id)
        os.remove(f'/var/www/pybot/qrbot/qr/{name_qrcode}.png')
    except Exception as error:
        bot.send_message(message.chat.id, "Произошла ошибка. :(")
        bot.send_message(config.logpm, f"Произошла ошибка!:\n{error}")


@bot.message_handler(content_types=['text'])
def send(message):
    try:
        qr_gen(message)
    except Exception as limit:
        bot.send_message(message.chat.id, f"Лимит: {limit}")


@bot.message_handler(content_types=['sticker'])
def qr_gen_sti(message):
    log(message)
    try:
        qr = qrcode.make(message.sticker)
        name_qrcode = random.randrange(99)
        qr.save(f"/var/www/pybot/qrbot/qr/{name_qrcode}.png")
        qrpic = open(f"/var/www/pybot/qrbot/qr/{name_qrcode}.png", 'rb')
        bot.send_chat_action(message.chat.id, 'upload_photo')
        bot.send_photo(message.chat.id, qrpic,
                       reply_to_message_id=message.message_id)
        os.remove(f'/var/www/pybot/qrbot/qr/{name_qrcode}.png')
    except Exception as error:
        bot.send_message(message.chat.id, "Произошла ошибка!")
        bot.send_message(config.logpm, f"Произошла ошибка!:\n{error}")


try:
    bot.infinity_polling()
except Exception as e:
    bot.send_message(config.logpm, f"Ошибка в запросе:\n{e}")
    print(str(e))
