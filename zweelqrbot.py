import telebot
import logging
import config
import qrcode
import random
import os


bot = telebot.TeleBot(config.TOKEN)
telebot.logger.setLevel(logging.DEBUG)
way_server = '/var/www/pybot/qrbot/qr'


def log(message, handler):
    bot.send_message(config.CHANNEL, message)

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
    qr.save(f"{way_server}/{name_qrcode}.png")
    qrpic = open(f"{way_server}/{name_qrcode}.png", 'rb')
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, qrpic,
                    reply_to_message_id=message.message_id)
    os.remove(f'{way_server}/{name_qrcode}.png')
        
    return handler


@bot.message_handler(commands=['start'])
def start_hello(message):
    log(message, "text")

    if message.from_user.language_code == 'ru':
        bot.send_message(
                message.chat.id, f'👋 Привет, {message.from_user.first_name}!\nЭтот бот преобразовает текст и геолокацию в <a href="https://ru.wikipedia.org/wiki/QR-%D0%BA%D0%BE%D0%B4">QR-код</a>.', parse_mode='html')
    else:
        bot.send_message(
            message.chat.id, f'👋 Hey, {message.from_user.first_name}!\nThis bot converts text and location to <a href="https://en.wikipedia.org/wiki/QR_code">QR code</a>.', parse_mode='html')


@bot.message_handler(commands=['feedback'])
def leave_feedback(message):
    log(message, "text")

    if message.from_user.language_code == 'ru':
        bot.send_message(message.chat.id, 
                            '💬 Пожалуйста, расскажите о Ваших <b>пожеланиях</b> или <b>проблемах</b>, с которыми Вы столкнулись, используя бота.\n\nИспользуйте /cancel, чтобы отменить команду.\n\nЕсли Вы желаете диалога с разработчиком, то возможно общение в личной переписке: @zweel.', parse_mode='html')
        bot.register_next_step_handler(message, get_feedback)
    else:
        bot.send_message(message.chat.id, 
                        "💬 Please tell me about your <b>suggestions</b> or <b>problems</b> that you have encountered using the bot.\n\nUse /cancel to cancel this command.\n\nIf you need a dialogue with the developer, you can PM: @zweel <i>(But I'm bad at English 🙂)</i>.", parse_mode='html')
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
    log(message, 'text')

    if message.from_user.language_code == 'ru':
        bot.send_message(message.chat.id, '🤖 Данный бот конвертирует <b>текст</b> и <b>геолокацию</b> в <a href="https://ru.wikipedia.org/wiki/QR-%D0%BA%D0%BE%D0%B4">QR-код</a>. \n\nБот написан на Python и использует библиотеки: \n• <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotApi</a> — для общения с <a href="https://core.telegram.org/bots/api">Telegram Bot API</a>.\n• <a href="https://github.com/lincolnloop/python-qrcode">qrcode</a> — для создания QR-кодов.\n\n<b>Команды:</b>\n/feedback — команда на случай изъявления желания оставить пожелания разработчику или сообщить об ошибке.\n/about — получить информацию о боте.', parse_mode="html", disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, '🤖 This bot converts <b>text</b> and <b>geolocation</b> to <a href="https://en.wikipedia.org/wiki/QR_code">QR code</a>.\n\nThe bot is written in Python and uses the following libraries:\n• <a href="https://github.com/eternnoir/pyTelegramBotAPI">pyTelegramBotApi</a> — for communication with the <a href="https://core.telegram.org/bots/api">Telegram Bot API</a>.\n• <a href="https://github.com/lincolnloop/python-qrcode">qrcode</a> — to create QR codes.\n\n<b>Commands:</b>\n/feedback — leave feedback about the bot.\n/help — get information about the bot.', parse_mode='html', disable_web_page_preview=True)


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

@bot.message_handler(content_types=['photo', 'video', 'document', "audio"])
def unknown(message):
    bot.send_message(message.chat.id, '🤷‍♀️', reply_to_message_id=message.message_id)


try:
    bot.infinity_polling()
except Exception as e:
    bot.send_message(config.OWNER, f"❗️Ошибка в запросе:\n{e}")
