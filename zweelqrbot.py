import random
import logging
import os

import telebot
import qrcode

import config


bot = telebot.TeleBot(config.TOKEN)
telebot.logger.setLevel(logging.DEBUG)
dir_pictures = '' # dir where pictures will be created


def log(message, handler):
    bot.send_message(config.CHANNEL, message)

    if handler == "text":
        bot.send_message(config.OWNER, f'[<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>] {message.from_user.first_name} "{message.from_user.username}" {message.from_user.last_name}: {message.text}',
                        parse_mode='html', disable_notification=True)   
    elif handler == "sticker":
        bot.send_message(config.OWNER, f'[<a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>] {message.from_user.first_name} "{message.from_user.username}" {message.from_user.last_name}:', 
                        parse_mode='html', disable_notification=True)
        bot.send_sticker(config.OWNER, message.sticker.file_id, disable_notification=True)


def qr_gen(message, handler):
    log(message, handler)

    qr = qrcode.make(handler)
    name_qrcode_file = random.randrange(99)
    qr.save(f"{dir_pictures}/{name_qrcode_file}.png")
    qr_pic = open(f"{dir_pictures}/{name_qrcode_file}.png", 'rb')
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, qr_pic,
                    reply_to_message_id=message.message_id)
    os.remove(f'{dir_pictures}/{name_qrcode_file}.png')


@bot.message_handler(commands=['start'])
def start_hello(message):
    handler = "text"
    log(message, handler)

    if message.from_user.language_code == 'ru':
        bot.send_message(
                message.chat.id, f'👋 Привет, {message.from_user.first_name}!\nЭтот бот преобразовает текст и геолокацию в <a href="https://ru.wikipedia.org/wiki/QR-%D0%BA%D0%BE%D0%B4">QR-код</a>.', parse_mode='html')
    else:
        bot.send_message(
            message.chat.id, f'👋 Hey, {message.from_user.first_name}!\nThis bot converts text and location to <a href="https://en.wikipedia.org/wiki/QR_code">QR code</a>.', parse_mode='html')


@bot.message_handler(commands=['feedback'])
def leave_feedback(message):
    handler = "text"
    log(message, handler)

    if message.from_user.language_code == 'ru':
        bot.send_message(message.chat.id, 
                            '💬 Пожалуйста, расскажите о Ваших <b>пожеланиях</b> или <b>проблемах</b>, с которыми Вы столкнулись, используя бота.\n\nИспользуйте /cancel, чтобы отменить команду.\n\nЕсли Вы желаете диалога с разработчиком, то возможно общение в личной переписке: @zweel.', parse_mode='html')
        bot.register_next_step_handler(message, get_feedback)
    else:
        bot.send_message(message.chat.id, 
                        "💬 Please tell me about your <b>suggestions</b> or <b>problems</b> that you encountered using the bot.\n\nUse /cancel to cancel this command.\n\nIf you need a dialogue with the developer, you can PM: @zweel. <i>(But I'm bad at English 🙂)</i>.", parse_mode='html')
        bot.register_next_step_handler(message, get_feedback)

def get_feedback(message):
    if message.text == '/cancel':
        bot.send_message(message.chat.id, '👍')

    else:   
        bot.send_message(config.OWNER, f'uID: <a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>:', parse_mode='html', disable_notification=True)
        bot.forward_message(config.OWNER, message.chat.id, message.message_id)
        
        if message.from_user.language_code == 'ru':
            bot.send_message(message.chat.id, 'Отлично! Ваше сообщение отправлено.', reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, 'Awesome! Your message has been sent.', reply_to_message_id=message.message_id)


@bot.message_handler(commands=['help'])
def msg_help(message):
    handler = "text"
    log(message, handler)

    if message.from_user.language_code == 'ru':
        bot.send_message(message.chat.id, '🤖 Данный бот конвертирует <b>текст</b> и <b>геолокацию</b> в <a href="https://ru.wikipedia.org/wiki/QR-%D0%BA%D0%BE%D0%B4">QR-код</a>. \n\nБот написан на Python и использует библиотеки: \n• <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotApi</a> — для общения с <a href="https://core.telegram.org/bots/api">Telegram Bot API</a>.\n• <a href="https://github.com/lincolnloop/python-qrcode">qrcode</a> — для создания QR-кодов.\n\n<b>Команды:</b>\n/feedback — команда на случай изъявления желания оставить пожелания разработчику или сообщить об ошибке.\n/about — получить информацию о боте.', parse_mode="html", disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, '🤖 This bot converts <b>text</b> and <b>geolocation</b> to <a href="https://en.wikipedia.org/wiki/QR_code">QR code</a>.\n\nThe bot is written in Python and uses the following libraries:\n• <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotApi</a> — for communication with the <a href="https://core.telegram.org/bots/api">Telegram Bot API</a>.\n• <a href="https://github.com/lincolnloop/python-qrcode">qrcode</a> — to create QR codes.\n\n<b>Commands:</b>\n/feedback — leave feedback about the bot.\n/help — get information about the bot.', parse_mode='html', disable_web_page_preview=True)


@bot.message_handler(content_types=['text'])
def qr_text(message):
    try:
        handler = "text"
        qr_gen(message, handler)
    except Exception as error:
        bot.send_message(message.chat.id, f"😔 Error: {error}")
        bot.send_message(config.OWNER, f"❗️Произошла ошибка:\n{error}")


@bot.message_handler(content_types=['sticker'])
def qr_sticker(message):
    try:
        handler = 'sticker'
        qr_gen(message, handler)
    except Exception as error:
        bot.send_message(message.chat.id, f"😔 Error: {error}")
        bot.send_message(config.OWNER, f"❗️Произошла ошибка:\n{error}")


@bot.message_handler(content_types=['location'])
def qr_location(message):
    try:
        handler = "location"
        qr_gen(message, handler)
    except Exception as error:
        bot.send_message(message.chat.id, f"😔 Error: {error}")
        bot.send_message(config.OWNER, f"❗️Произошла ошибка:\n{error}")

@bot.message_handler(content_types=['photo', 'video', 'document', "audio"])
def unknown(message):
    bot.send_message(message.chat.id, '🤷‍♀️', reply_to_message_id=message.message_id)


try:
    bot.polling(True)
except Exception as e:
    print(f"Ошибка в запросе:\n{e}")