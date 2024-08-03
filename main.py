import threading
from collections import defaultdict
import telebot
import time
import key

bot = telebot.TeleBot(key.token)
stop_words = ["анкета", "ссылка", "уникальное предложение", "доход", "деньги", "быстрый доход", "халтура",
              "легкие деньги", "нужны деньги?", "нужны деньги"]
user_stats = defaultdict(lambda: defaultdict(int))


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для управления чатом. Напиши /help, чтобы узнать, что я умею.")
    if message.chat.id not in user_stats:
        user_stats[message.chat.id] = defaultdict(int)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     "/kick - кикнуть пользователя\n/mute - замутить пользователя на определенное время\n/unmute - размутить пользователя\n/stats - показать статистику чата\n/selfstat - показать свою статистику")


@bot.message_handler(commands=['kick'])
def kick_user(message):
    if message.reply_to_message and user_stats[message.chat.id][message.reply_to_message.from_user.id] >= 50:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.send_message(message.chat.id, "Невозможно кикнуть администратора.")
        else:
            bot.kick_chat_member(chat_id, user_id)
            bot.send_message(message.chat.id, f"Пользователь {message.reply_to_message.from_user.username} был кикнут.")
    else:
        bot.send_message(message.chat.id,
                         "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите кикнуть или у вас не достаточно прав")


@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.reply_to_message and user_stats[message.chat.id][message.reply_to_message.from_user.id] >= 50:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.send_message(message.chat.id, "Невозможно замутить администратора.")
        else:
            duration = 60  # Значение по умолчанию - 1 минута
            args = message.text.split()[1:]
            if args:
                try:
                    duration = int(args[0])
                except ValueError:
                    bot.send_message(message.chat.id, "Неправильный формат времени.")
                    return
                if duration < 1:
                    bot.send_message(message.chat.id, "Время должно быть положительным числом.")
                    return
                if duration > 1440:
                    bot.send_message(message.chat.id, "Максимальное время - 1 день.")
                    return
            bot.restrict_chat_member(chat_id, user_id, until_date=time.time() + duration * 60)
            bot.send_message(message.chat.id,
                             f"Пользователь {message.reply_to_message.from_user.username} замучен на {duration} минут.")
    else:
        bot.send_message(message.chat.id,
                         "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите замутить.")


@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.reply_to_message and user_stats[message.chat.id][message.reply_to_message.from_user.id] >= 50:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True, can_send_media_messages=True,
                                 can_send_other_messages=True, can_add_web_page_previews=True)
        bot.send_message(message.chat.id, f"Пользователь {message.reply_to_message.from_user.username} размучен.")
    else:
        bot.send_message(message,
                         "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите размутить.")


@bot.message_handler(func=lambda message: True)
def check_message(message):
    user_stats[message.chat.id][message.from_user.id] += 1
    for word in stop_words:
        if word in message.text.lower():
            bot.send_message(message.chat.id,
                             f'{message.from_user.username}, ваше сообщение похоже на спам, удалите его и переформулируйте, иначе будете удалены из чата через 1 минуту')
            threading.Thread(target=warn_and_kick, args=(message,)).start()
            break
    else:
        print(message.text)


def warn_and_kick(message):
    time.sleep(60)
    bot.kick_chat_member(message.chat.id, message.from_user.id)
    bot.send_message(message.chat.id,
                     f"Пользователь {message.from_user.username} был удален из чата за подозрение в спаме")


bot.infinity_polling(none_stop=True)
