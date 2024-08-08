import os
import threading
from collections import defaultdict
import telebot
import time
import key
import http.server
import socketserver
from stop_list import stop_list_temp

bot = telebot.TeleBot(key.token)
stop_words = stop_list_temp

user_stats = defaultdict(lambda: defaultdict(int))
pending_verification = defaultdict(lambda: defaultdict(bool))


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для управления чатом. Напиши /help, чтобы узнать, что я умею.")
    if message.chat.id not in user_stats:
        user_stats[message.chat.id] = defaultdict(int)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     "/kick - кикнуть пользователя\n/mute - замутить пользователя на определенное время\n/unmute")


@bot.message_handler(commands=['kick'])
def kick_user(message):
    if message.reply_to_message and user_stats[message.chat.id][message.reply_to_message.from_user.id] <= 3 and \
            user_stats[message.chat.id][message.from_user.id] >= 50:
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
    if message.reply_to_message and user_stats[message.chat.id][message.from_user.id] >= 50:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.send_message(message.chat.id, "Невозможно замутить администратора.")
        else:
            duration = 30  # Значение по умолчанию - 30 минут
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
                elif duration > 1440:
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
    if message.reply_to_message and user_stats[message.chat.id][message.from_user.id] >= 50:
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
    if message.text.lower() == 'я не робот':
        if pending_verification[message.chat.id][message.from_user.id] == False:
            pending_verification[message.chat.id][message.from_user.id] = True
            bot.send_message(message.chat.id, f"{message.from_user.username}, спасибо за подтверждение.")
            return
        else:
            return  # Игнорируем, если проверка не активна для этого пользователя

    for word in stop_words:
        if word in message.text.lower():
            pending_verification[message.chat.id][message.from_user.id] = False
            threading.Thread(target=warn_and_kick, args=(message,)).start()
            break

    user_stats[message.chat.id][message.from_user.id] += 1


def kick_if_no_response(chat_id, user_id, username):
    time.sleep(120)
    if not pending_verification[chat_id][user_id]:
        bot.kick_chat_member(chat_id, user_id)
        bot.send_message(chat_id,
                         f"Пользователь {username} был удален из чата за подозрение в спаме")
        del pending_verification[chat_id][user_id]


def warn_and_kick(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id,
                     f"{message.from_user.username} Ваше сообщение было похоже на спам и было удалено")
    if user_stats[message.chat.id][message.from_user.id] <= 3:
        pending_verification[message.chat.id][message.from_user.id] = False
        bot.send_message(message.chat.id,
                         f"{message.from_user.username} Напишите : 'Я не робот' в течение 2 минут, чтобы Вас не удалили из чата")
        threading.Thread(target=kick_if_no_response,
                         args=(message.chat.id, message.from_user.id, message.from_user.username)).start()


def start_polling():
    bot.infinity_polling(none_stop=True)


if __name__ == '__main__':
    threading.Thread(target=start_polling).start()

    port = int(os.environ.get('PORT', 5000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()
