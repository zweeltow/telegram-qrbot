import telebot
import config
import qrcode
import random
import os


bot = telebot.TeleBot(config.TOKEN)


def log(message, handler):
    bot.send_message(config.CHANNEL, f'{message}')

    if handler == "text":
        bot.send_message(config.OWNER, f'[<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>] {message.from_user.first_name} "{message.from_user.username}" {message.from_user.last_name}: {message.text}',
                        parse_mode='html', disable_notification=True)   
    elif handler == "sticker":
        bot.send_message(config.OWNER, f'[<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>] {message.from_user.first_name} "{message.from_user.username}" {message.from_user.last_name}:', 
                        parse_mode='html', disable_notification=True)
        bot.send_sticker(config.OWNER, message.sticker.file_id, disable_notification=True)
    

    return handler


def qr_gen(message, handler):
    log(message, handler)

    if handler == "text":
        loc = message.text
    elif handler == "sticker":
        loc = message.sticker
    elif handler == "location":
        loc = f"geo:{message.location.latitude},{message.location.longitude}"

    qr = qrcode.make(loc)
    name_qrcode = random.randrange(99)
    qr.save(f"/var/www/pybot/qrbot/qr/{name_qrcode}.png")
    qrpic = open(f"/var/www/pybot/qrbot/qr/{name_qrcode}.png", 'rb')
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, qrpic,
                    reply_to_message_id=message.message_id)
    os.remove(f'/var/www/pybot/qrbot/qr/{name_qrcode}.png')
        
    return handler


@bot.message_handler(commands=['start'])
def start_hello(message):
    log(message, "text")

    if message.from_user.language_code == 'ru':
        bot.send_message(
                message.chat.id, f'👋 Привет, {message.from_user.first_name}!\nЭтот бот преобразовает текст и геолокацию в <a href="https://ru.wikipedia.org/wiki/QR-%D0%BA%D0%BE%D0%B4">QR код</a>.', parse_mode='html')
    else:
        bot.send_message(
            message.chat.id, f'👋 Hey, {message.from_user.first_name}!\nThis bot converts text and geolocation to the <a href="https://en.wikipedia.org/wiki/QR_code">QR code</a>.', parse_mode='html')


@bot.message_handler(content_types=['text'])
def qr_text(message):
    try:
        qr_gen(message, "text")
    except Exception as error:
        bot.send_message(message.chat.id, f"😔 Error: {error}")
        bot.send_message(config.OWNER, f"❗️Произошла ошибка:\n{error}")


@bot.message_handler(content_types=['sticker'])
def qr_sticker(message):
    try:
        qr_gen(message, "sticker")
    except Exception as error:
        bot.send_message(message.chat.id, f"😔 Error: {error}")
        bot.send_message(config.OWNER, f"❗️Произошла ошибка:\n{error}")


@bot.message_handler(content_types=['location'])
def qr_location(message):
    try:
        qr_gen(message, "location")
    except Exception as error:
        bot.send_message(message.chat.id, f"😔 Error: {error}")
        bot.send_message(config.OWNER, f"❗️Произошла ошибка:\n{error}")


try:
    bot.infinity_polling()
except Exception as e:
    bot.send_message(config.OWNER, f"❗️Ошибка в запросе:\n{e}")