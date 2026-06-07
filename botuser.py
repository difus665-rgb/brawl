import telebot
from telebot import types
import sqlite3
import json
import os
import random
import re
import logging
from datetime import datetime as dt
from datetime import timedelta
import pytz
import time
import telebot.types as types
import threading
from threading import Thread
from mysql.connector import Error
from difflib import SequenceMatcher
import shlex
import pytz
import psutil
from database.DataBase import DataBase
import ping3
from collections import OrderedDict

bot = telebot.TeleBot("Токен сюды")

admins = [7014105936] # 7014 - не трогайте а то бот вылетит
tehs = []
managers = []
creator1 = []
creator2 = []
creator3 = []

def update_maintenance_status(new_status):
    try:
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)
        config['maintenance'] = new_status
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"[ERROR] Не удалось обновить config.json: {e}")
        return False

def is_admin(user_id):
    return user_id in admins or user_id in tehs

def escape_markdown(text):
    text = re.sub(r'([_\*`\[\]()~|>#+-=|{}.!])', r'\\\1', text)
    return text

def escape_markdown_v2(text):
    characters_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in characters_to_escape:
        text = text.replace(char, f'\\{char}')
    return text
    
def escape_markdown(text):
    return re.sub(r'([_*\[\]()~`>#+-=|{}.!])', r'\\\1', text)

def format_value(value):
    if value < 0:
        return f"{abs(value)} Отрицательное"
    return str(value)
    
def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_value(value):
    return f"{value}" if value >= 0 else f"-{abs(value)}"

def escape_html(text):
    import html
    return html.escape(text)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    response = (
        'Добро пожаловать в бота!\n\n'
        '⛔Команды:\n\n'
        '/name [name] - Узнать об аккаунте\n'
        '/info [id] - Узнать об аккаунте.\n'
        '/connect [id] [token] - Привязать аккаунт.\n'
        '/profile - Просмотр профиля.\n'
        '/unlink - Отвязать аккаунт.\n'
        '/top - Посмотреть топы.\n'
        '/recovery [old id] [new token] - Востановить аккаунт.\n\n'
        '/admin - Админ команды\n'
        '/tehadmin - Тех.Админ команды\n'
        '/manager - Менеджер команды\n\n'
        '/creator - Контент мейкеры\n'
    )
    try:
        bot.reply_to(message, response)
    except Exception as e:
        logger.error(f"Failed to reply to /start command: {e}")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id
    
    if user_id not in admins:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    try:
        bot.reply_to(message, (
            'Admin Commands!\n\n⛔ Команды:\n\n'
            '/toggle_trophies [false/true] - Двойные трофеи.\n'
            '/toggle_tokens [false/true] - Двойные токены.\n'
            '/vip [id] - Дать ВИП.\n'
            '/unvip [id] - Забрать ВИП.\n'
            '/settokens [id] [amount] - Установить токены.\n'
            '/addtokens [id] [amount] - Добавить токены.\n'
            '/untokens [id] [amount] - Забрать токены.\n'
            '/setgems [id] [amount] - Установить гемы.\n'
            '/addgems [id] [amount] - Добавить гемы.\n'
            '/ungems [id] [amount] - Забрать гемы.\n'
            '/setgold [id] [amount] - Установить золото.\n'
            '/addgold [id] [amount] - Добавить золото.\n'
            '/ungold [id] [amount] - Забрать золото.\n'
            '/unroom - Очистить румы.\n'
            '/teh - Тех. Перерыв.\n'
            '/unteh - Убрать Тех. Перерыв.\n'
            '/ban [id] - Забанить.\n'
            '/unban [id] - Разбанить.\n'
            '/code [code] - Создать код.\n'
            '/code_list - Список кодов.\n'
            '/uncode [code] - Удалить код.\n'
            '/autoshop - Автомагазин.\n'
            '/upshop - Обновить магазин.\n'
            '/rename [id] [new_name] - Изменить имя.\n'
            '/theme [theme] - Тема.\n'
            '/status [status] - Статус.\n'
            '/resetclubs - Удалить клубы.\n'
            '/bd - Сохранить базу данных сервера.\n'
            '/delete - [id] Удалить аккаунт.\n'
            '/token [id] - Просмотреть токены.\n'
            '/account [id] [token] - Востановить аккаунт.\n'
            '/resetbp [id] - Сброс BrawlPass.\n'
            '/addpass [id] - Дать BrawlPass.\n'
            '/removepass [id] - Забрать BrawlPass.\n'
            '/new_offer - Новая акция от 11 до беск.\n'
            '/remove_offer - Удалить акцию с 11.\n'
        ))
    except Exception as e:
        logger.error(f"Failed to reply to /admin command: {e}")

@bot.message_handler(commands=['tehadmin'])
def admin_command(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь Тех.Админом!")
        return

    try:
        bot.reply_to(message, (
            'Teh.Admin Commands!\n\n⛔ Команды:\n\n'
            '/toggle_trophies [false/true] - Двойные трофеи.\n'
            '/toggle_tokens [false/true] - Двойные токены.\n'
            '/vip [id] - Дать ВИП.\n'
            '/unvip [id] - Забрать ВИП.\n'
            '/settokens [id] [amount] - Установить токены.\n'
            '/addtokens [id] [amount] - Добавить токены.\n'
            '/untokens [id] [amount] - Забрать токены.\n'
            '/setgems [id] [amount] - Установить гемы.\n'
            '/addgems [id] [amount] - Добавить гемы.\n'
            '/ungems [id] [amount] - Забрать гемы.\n'
            '/setgold [id] [amount] - Установить золото.\n'
            '/addgold [id] [amount] - Добавить золото.\n'
            '/ungold [id] [amount] - Забрать золото.\n'
            '/unroom - Очистить румы.\n'
            '/teh - Тех. Перерыв.\n'
            '/unteh - Убрать Тех. Перерыв.\n'
            '/ban [id] - Забанить.\n'
            '/unban [id] - Разбанить.\n'
            '/code [code] - Создать код.\n'
            '/code_list - Список кодов.\n'
            '/uncode [code] - Удалить код.\n'
            '/autoshop - Автомагазин.\n'
            '/upshop - Обновить магазин.\n'
            '/rename [id] [new_name] - Изменить имя.\n'
            '/theme [theme] - Тема.\n'
            '/status [status] - Статус.\n'
            '/resetclubs - Удалить клубы.\n'
            '/delete - [id] Удалить аккаунт.\n'
            '/token [id] - Просмотреть токены.\n'
            '/account [id] [token] - Востановить аккаунт.\n'
            '/resetbp [id] - Сброс BrawlPass.\n'
            '/addpass [id] - Дать BrawlPass.\n'
            '/removepass [id] - Забрать BrawlPass.\n'
        ))
    except Exception as e:
        logger.error(f"Failed to reply to /tehadmin command: {e}")

@bot.message_handler(commands=['manager'])
def admin_command(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in managers and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь Менеджером!")
        return

    try:
        bot.reply_to(message, (
            'Manager Commands!\n\n⛔ Команды:\n\n'
            '/vip [id] - Дать ВИП.\n'
            '/unvip [id] - Забрать ВИП.\n'
            '/settokens [id] [amount] - Установить токены.\n'
            '/addtokens [id] [amount] - Добавить токены.\n'
            '/untokens [id] [amount] - Забрать токены.\n'
            '/addgems [id] [amount] - Добавить гемы.\n'
            '/ungems [id] [amount] - Забрать гемы.\n'
            '/addgold [id] [amount] - Добавить золото.\n'
            '/ungold [id] [amount] - Забрать золото.\n'
            '/resetbp [id] - Сброс BrawlPass.\n'
            '/addpass [id] - Дать BrawlPass.\n'
            '/removepass [id] - Забрать BrawlPass.\n'
        ))
    except Exception as e:
        logger.error(f"Failed to reply to /manager command: {e}")
        
def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

def escape_markdown(text):
    return re.sub(r'([_*\[\]()~`>#+-=|{}.!])', r'\\\1', text)

def escape_markdown_v2(text):
    characters_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in characters_to_escape:
        text = text.replace(char, f'\\{char}')
    return text

def format_value(value):
    return f"{value}" if value >= 0 else f"-{abs(value)}"

def is_admin(user_id):
    return user_id in admins or user_id in tehs or user_id in managers

def is_teh(user_id):
    return user_id in tehs or user_id in admins
    
def is_manager(user_id):
    return user_id in admins

@bot.message_handler(commands=['toggle_trophies'])
def toggle_trophies(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return
    
    config = load_config()

    if config.get("DoubleTrophiesEvent", False):
        config["DoubleTrophiesEvent"] = False
        bot.send_message(message.chat.id, "✅ Удвоение трофеев отключено.")
    else:
        config["DoubleTrophiesEvent"] = True
        bot.send_message(message.chat.id, "✅ Удвоение трофеев включено.")
    
    save_config(config)

@bot.message_handler(commands=['toggle_tokens'])
def toggle_tokens(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return
    
    config = load_config()

    if config.get("DoubleTokensEvent", False):
        config["DoubleTokensEvent"] = False
        bot.send_message(message.chat.id, "✅ Удвоение токенов отключено.")
    else:
        config["DoubleTokensEvent"] = True
        bot.send_message(message.chat.id, "✅ Удвоение токенов включено.")
    
    save_config(config)
    
    
@bot.message_handler(func=lambda message: message.text.startswith("/allquest"))
def allquest(message):
    chat_id = message.chat.id
    if chat_id in admins:
        try:
            conn = DataBase.get_connection()
            if not conn:
                bot.send_message(chat_id, "❌ Не удалось подключиться к базе данных.")
                return

            cursor = conn.cursor()

            cursor.execute("SELECT lowID, brawlerData, trophies FROM plrs")
            player_data = cursor.fetchall()

            for player in player_data:
                lowID = player[0]
                data = json.loads(player[1])
                unlocked = [int(key) for key, value in data['UnlockedBrawlers'].items() if value == 1]
                unlocked_brawlers = [unlocked] if unlocked else [[]]

                trophies = player[2]
                if trophies < 300:
                    continue

                cursor.execute("SELECT quests FROM plrs WHERE lowID = %s", (lowID,))
                current_quests = cursor.fetchone()
                current_quests = json.loads(current_quests[0]) if current_quests and current_quests[0] else []

                if len(current_quests) >= 18:
                    current_quests = []
                    cursor.execute("UPDATE plrs SET quests = %s WHERE lowID = %s", (json.dumps(current_quests), lowID))
                    conn.commit()

                quests = []
                for i in range(2):  # 2 ежедневных квеста
                    try:
                        brawler_id = random.choice(unlocked_brawlers[0])
                    except IndexError:
                        continue
                    win_count = 3
                    if win_count == 3:
                        prize = 100
                        mt = 1
                        qt = 1
                        gm = 0
                        bpex = False

                    quest = {
                        "id": brawler_id,
                        "state": 0,
                        "win_count": win_count,
                        "counts": 0,
                        "prize": prize,
                        "QT": qt,
                        "GM": gm,
                        "MT": mt,
                        "BPEX": bpex
                    }
                    quests.append(quest)

                current_quests.extend(quests)
                cursor.execute("UPDATE plrs SET quests = %s WHERE lowID = %s", (json.dumps(current_quests), lowID))
                conn.commit()

            cursor.close()
            conn.close()

            bot.send_message(chat_id, "✅ Квесты успешно сгенерированы для всех игроков!")
        
        except Exception as e:
            logger.error(f"[ERROR] /allquest: {e}")
            bot.send_message(chat_id, f"❌ Ошибка при генерации квестов: {str(e)}")
    else:
        bot.send_message(chat_id, "❌ У вас недостаточно прав для выполнения этой команды.")

@bot.message_handler(func=lambda message: message.text.startswith("/clearquests"))
def clearquests(message):
    chat_id = message.chat.id
    if chat_id in admins:
        try:
            conn = DataBase.get_connection()
            if not conn:
                bot.send_message(chat_id, "❌ Не удалось подключиться к базе данных.")
                return

            cursor = conn.cursor()

            cursor.execute("SELECT lowID FROM plrs")
            player_data = cursor.fetchall()

            for player in player_data:
                lowID = player[0]

                cursor.execute("UPDATE plrs SET quests = %s WHERE lowID = %s", (json.dumps([]), lowID))
                conn.commit()

            cursor.close()
            conn.close()

            bot.send_message(chat_id, "✅ Все квесты успешно очищены у всех игроков!")

        except Exception as e:
            logger.error(f"[ERROR] /clearquests: {e}")
            bot.send_message(chat_id, f"❌ Ошибка при очистке квестов: {str(e)}")
    else:
        bot.send_message(chat_id, "❌ У вас недостаточно прав для выполнения этой команды.")
        
@bot.message_handler(func=lambda message: message.text.startswith("/notif"))
def addNotif(message):
    chat_id = message.chat.id
    if chat_id in admins:
        if message.text.startswith("/notifall"):
            match = re.match(r'/notifall\s+(\d+)\s+"(.+?)"\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)', message.text)
            if match:
                param2, param3, param4, param5, param6 = int(match.group(1)), match.group(2), int(match.group(3)), int(match.group(4)), int(match.group(5))
                result = DataBase().addNotificationToAll(param2, param3, param4, param5, param6)
                bot.send_message(chat_id, result)
            else:
                bot.send_message(chat_id, "❌ Неверный формат команды. Используйте: /notifall <айди нотифа> \"описание\" <айди бравлера> <айди скина> <кол-во гемов>")
        else:
            match = re.match(r'\/notif\s+(\d+|\#\w+)\s+(\d+)\s+"(.+?)"\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)', message.text)
            if match:
                identifier = match.group(1)
                param2 = int(match.group(2))
                param3 = match.group(3)
                param4 = int(match.group(4))
                param5 = int(match.group(5))
                param6 = int(match.group(6))

                # Проверяем, является ли identifier хештегом
                if identifier.startswith("#"):
                    lowID = DataBase().get_id_by_hash(identifier)
                    if lowID is None:
                        bot.send_message(chat_id, "❌ Игрок с таким хештегом не найден.")
                        return
                    param1 = lowID
                else:
                    try:
                        param1 = int(identifier)
                    except ValueError:
                        bot.send_message(chat_id, "❌ Неверный формат lowID. Убедитесь, что это число или хештег.")
                        return

                # Вызываем метод добавления уведомления
                result = DataBase().addNotification(param1, param2, param3, param4, param5, param6)
                bot.send_message(chat_id, result)
            else:
                bot.send_message(chat_id, "Айди:\n1 - Скины\n2 - Боец\n3 - Гемы\n4 - Сбросс сезона\n5 - Старпоинты\n6 - Пины\n7 - Ящики")
                bot.send_message(chat_id, "❌ Неверный формат команды. Используйте: /notif <lowID | #хештег> <айди нотифа> \"описание\" <айди бравлера> <айди скина> <кол-во гемов>")
    else:
        bot.send_message(chat_id, "❌ У вас недостаточно прав!")
        
@bot.message_handler(func=lambda message: message.text.startswith("/unnotif"))
def removeNotif(message):
    chat_id = message.chat.id
    if chat_id in admins:
        match = re.match(r'/unnotif\s+(\d+|\#\w+)\s+(\d+)', message.text)
        if match:
            identifier = match.group(1)
            notif_index = int(match.group(2))

            # Получаем lowID по хештегу, если это хештег
            if identifier.startswith("#"):
                lowID = DataBase().get_id_by_hash(identifier)
                if lowID is None:
                    bot.send_message(chat_id, "❌ Игрок с таким хештегом не найден.")
                    return
            else:
                try:
                    lowID = int(match.group(1))
                except ValueError:
                    bot.send_message(chat_id, "❌ Неверный формат lowID. Используйте число или хештег (#...)")

            # Удаляем уведомление
            result = DataBase().removeNotification(lowID, notif_index)
            bot.send_message(chat_id, result)
        else:
            bot.send_message(chat_id, "❌ Неверный формат команды. Используйте: /unnotif <lowID | #хештег> <номер уведомления>")
    else:
        bot.send_message(chat_id, "❌ У вас недостаточно прав!")
        
@bot.message_handler(commands=['creator'])
def admin_command(message):
    user_id = message.from_user.id
    
    if user_id not in admins and user_id not in managers and user_id not in tehs and user_id not in creator1 and user_id not in creator2 and user_id not in creator3:
        bot.send_message(message.chat.id, "❌ Вы не являетесь Контент мейкером!")
        return

    try:
        bot.reply_to(message, (
            'Какой ваш уровень?!\n\n⛔ Команды:\n\n'
            '/creator1 - 1 Уровень\n'
            '/creator2 - 2 Уровень\n'
            '/creator3 - 3 Уровень\n'
        ))
    except Exception as e:
        logger.error(f"Failed to reply to /creator command: {e}")
        
REWARD_INTERVAL = 604800  # 1 неделя в секундах

rewards_running = False
last_distribution_time = 0

def distribute_rewards():
    global last_distribution_time
    while True:
        current_time = time.time()
        
        if current_time - last_distribution_time >= REWARD_INTERVAL:
            try:
                conn = DataBase.get_connection()
                if not conn:
                    logger.error("Failed to connect to MySQL in distribute_rewards")
                    continue

                cursor = conn.cursor()
                cursor.execute("SELECT lowID FROM plrs")
                creators = cursor.fetchall()

                for (lowID,) in creators:
                    gems, gold, BPTOKEN = get_rewards(lowID)
                    
                    if gems > 0 or gold > 0 or BPTOKEN > 0:
                        cursor.execute(
                            "UPDATE plrs SET gems = gems + %s, gold = gold + %s, BPTOKEN = BPTOKEN + %s WHERE lowID = %s",
                            (gems, gold, BPTOKEN, lowID)
                        )
                        conn.commit()

                        message = f"🎉 Вы получили награду: {gems} Гемов, {gold} Золота, {BPTOKEN} Токенов!"
                        bot.send_message(lowID, message)

                admin_message = "Сервер был перезапущен/награда выдана!"
                for admin_id in admins:
                    bot.send_message(admin_id, admin_message)

                last_distribution_time = current_time
            
            except Exception as e:
                logger.error(f"Error in distributing rewards: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

        time.sleep(1)

def get_rewards(lowID): #награды контенткрейтерам
    if lowID in creator1:
        return 10, 50, 100
    elif lowID in creator2:
        return 20, 150, 300
    elif lowID in creator3:
        return 50, 300, 750
    return 0, 0, 0

@bot.message_handler(commands=['content'])
def content_command(message):
    user_id = message.from_user.id
    if user_id in admins or user_id in tehs or user_id in managers:
        threading.Thread(target=immediate_distribution, daemon=True).start()
        bot.reply_to(message, "✅ Награды контентмейкерам были выданы немедленно.")
    else:
        bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды!")

def immediate_distribution():
    try:
        conn = DataBase.get_connection()
        if not conn:
            logger.error("Failed to connect to MySQL in immediate_distribution")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT lowID FROM plrs")
        creators = cursor.fetchall()

        for (lowID,) in creators:
            gems, gold, BPTOKEN = get_rewards(lowID)
            
            if gems > 0 or gold > 0 or BPTOKEN > 0:
                cursor.execute(
                    "UPDATE plrs SET gems = gems + %s, gold = gold + %s, BPTOKEN = BPTOKEN + %s WHERE lowID = %s",
                    (gems, gold, BPTOKEN, lowID)
                )
                conn.commit()

                message = f"🎉 Вы получили награду: {gems} Гемов, {gold} Золота, {BPTOKEN} Токенов!"
                bot.send_message(lowID, message)

    except Exception as e:
        logger.error(f"Error in immediate distribution: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def create_creator_handler(level, gems, gold, BPTOKEN):
    level = set(level)

    def creator_command(message):
        user_id = message.from_user.id
        
        if user_id in admins or user_id in tehs or user_id in managers:
            bot.send_message(message.chat.id, "❌ Вы не являетесь Контент мейкером!")
            return

        try:
            with sqlite3.connect('users.db') as users_conn:
                users_cursor = users_conn.cursor()
                users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
                row = users_cursor.fetchone()

                if row:
                    lowID = row[0]
                    conn = DataBase.get_connection()
                    if not conn:
                        bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
                        return

                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT SCC FROM plrs WHERE lowID = %s", (lowID,))
                        code_row = cursor.fetchone()

                        author_code = code_row[0] if code_row and code_row[0] else "нет кода"

                        if author_code != "нет кода":
                            cursor.execute("SELECT COUNT(*) FROM plrs WHERE SCC = %s", (author_code,))
                            count = cursor.fetchone()[0]
                        else:
                            count = 0

                        cursor.execute(
                            "UPDATE plrs SET gems = gems + %s, gold = gold + %s, BPTOKEN = BPTOKEN + %s WHERE lowID = %s",
                            (gems, gold, BPTOKEN, lowID)
                        )
                        conn.commit()
                    except Exception as e:
                        logger.error(f"Database operation failed: {e}")
                    finally:
                        cursor.close()
                        conn.close()

                    response_message = (
                        f'⛔ Ваш успех!\n\n'
                        f'1. Каждую неделю вы будете получать:\n'
                        f'{gems} Гемов, {gold} золота, {BPTOKEN} Токенов\n\n'
                        f"🔍 Кодом автора пользуются {count} аккаунта(ов).\n"
                        f"🔍 Ваш код: {author_code}"
                    )
                else:
                    response_message = "❌ Ошибка: Вы не привязали аккаунт."

            bot.reply_to(message, response_message)

        except Exception as e:
            logger.error(f"Failed to reply to creator command: {e}")
            bot.send_message(message.chat.id, "❌ Произошла ошибка при выполнении команды.")

    return creator_command

# Уровни креатерства
bot.message_handler(commands=['creator1'])(create_creator_handler(creator1, 10, 50, 100))
bot.message_handler(commands=['creator2'])(create_creator_handler(creator2, 20, 150, 300))
bot.message_handler(commands=['creator3'])(create_creator_handler(creator3, 50, 300, 750))

threading.Thread(target=distribute_rewards, daemon=True).start()

@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = message.from_user.id

    try:
        with sqlite3.connect('users.db') as users_conn:
            users_cursor = users_conn.cursor()
            users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
            row = users_cursor.fetchone()

        if row:
            lowID = row[0]

            player_data = loadbyID(lowID)
            if not player_data:
                bot.send_message(user_id, f"❌ Игрок с ID {lowID} не найден.")
                return
            data = loadbyID(lowID)
            if not data:
                bot.send_message(user_id, "❌ Аккаунт не найден в базе данных.")
                return
                
            try:
                playerData = json.loads(player_data.get('playerData', '{}'))
            except json.JSONDecodeError:
                logger.warning(f"[WARNING] playerData не является JSON для ID {lowID}")
                playerData = {}

            hash_tag = playerData.get("HashTag", "Отсутствует")

            token = data.get('token', '')
            name = data.get('name', 'Неизвестный')
            trophies = data.get('trophies', 0)
            gems = data.get('gems', 0)
            gold = data.get('gold', 0)
            starpoints = data.get('starpoints', 0)
            tickets = data.get('tickets', 0)
            vip = data.get('vip', 0)
            SCC = data.get('SCC', '')

            # Статусы
            vip_status = "Есть" if vip > 0 else "Отсутствует"
            with open("config.json", "r", encoding='utf-8') as f:
                config = json.load(f)
            bp_status = "Куплен" if lowID in config["buybp"] else "Отсутствует"

            # Обработка имени и кода автора
            name = escape_markdown(name.strip())
            author_code_status = SCC if SCC else "Отсутствует"

            # Роли и награды
            roles = []
            rewards = ""
            if user_id in creator1:
                roles.append("Creator - 1 Уровень")
                rewards = "10 Гемов, 50 золота, 100 Токенов каждую неделю."
            elif user_id in creator2:
                roles.append("Creator - 2 Уровень")
                rewards = "20 Гемов, 150 золота, 300 Токенов каждую неделю.\n5 Гемов, 75 золота, 150 Токенов за каждое использование кода."
            elif user_id in creator3:
                roles.append("Creator - 3 Уровень")
                rewards = "50 Гемов, 300 золота, 750 Токенов каждую неделю.\n15 Гемов, 150 золота, 300 Токенов за каждое использование кода.\nVIP статус."

            if user_id in admins:
                roles.append("Администратор")
            if user_id in tehs:
                roles.append("Тех.Админ")
            if user_id in managers:
                roles.append("Менеджер")

            role_str = ", ".join(roles) if roles else "Игрок"

            # Формируем сообщение
            profile_info = (
                f"🤠 Статистика аккаунта: {name}:\n\n"
                f"🆔 ID: {lowID}\n🔗 Хештег: {hash_tag}\n📱 Токен: `{token}`\n\n"
                f"🏆 Трофеи: {trophies}\n💎 Гемы: {gems}\n💸 Монеты: {gold}\n"
                f"🎟️ Билеты: {tickets}\n⭐ Старпоинты: {starpoints}\n\n"
                f"💳 VIP: {vip_status}\n🎫 BrawlPass: {bp_status}\n"
                f"🔑 Код автора: {author_code_status}\n"
                f"🌟 Роль: {role_str}"
            )

            if rewards:
                profile_info += f"\n🎁 Награды: {rewards}"

            bot.send_message(user_id, profile_info, parse_mode='Markdown')
        else:
            bot.send_message(user_id, "❌ Вы не привязали аккаунт. Используйте команду /connect.")
    
    except Exception as e:
        logger.error(f"[ERROR] /profile: {e}")
        bot.send_message(user_id, f"❌ Произошла ошибка: {str(e)}")
            
@bot.message_handler(commands=['delete'])
def handle_delete(message: types.Message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.send_message(user_id, "❌ У вас недостаточно прав.")
        return

    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.send_message(user_id, "❌ Используйте: /delete [lowID | #хештег]")
        return

    identifier = command_parts[1].strip()
    lowID_to_delete = None

    # Определяем lowID через хештег или напрямую
    if identifier.startswith("#"):
        lowID_to_delete = DataBase().get_id_by_hash(identifier)
        if not lowID_to_delete:
            bot.send_message(user_id, "❌ Игрок с таким хештегом не найден.")
            return
    else:
        try:
            lowID_to_delete = int(identifier)
        except ValueError:
            bot.send_message(user_id, "❌ ID должен быть числом или хештегом в формате #...")
            return

    # Удаляем игрока по lowID
    try:
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(user_id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM plrs WHERE lowID = %s", (lowID_to_delete,))
            conn.commit()

            if cursor.rowcount > 0:
                bot.send_message(user_id, f"✅ Аккаунт с lowID {lowID_to_delete} удален.")
            else:
                bot.send_message(user_id, f"❌ Аккаунт с lowID {lowID_to_delete} не найден.")
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logging.error(f"[ERROR] /delete: {e}")
        bot.send_message(user_id, f"❌ Произошла ошибка: {str(e)}")
            
@bot.message_handler(commands=['unlink'])
def unlink_account(message):
    user_id = message.from_user.id

    try:
        with sqlite3.connect('users.db') as bot_db_connection:
            bot_db_cursor = bot_db_connection.cursor()
            bot_db_cursor.execute("SELECT lowID, name FROM accountconnect WHERE id_user = ?", (user_id,))
            result = bot_db_cursor.fetchone()

        if result:
            lowID, name = result
            with sqlite3.connect('users.db') as bot_db_connection:
                bot_db_cursor = bot_db_connection.cursor()
                bot_db_cursor.execute("DELETE FROM accountconnect WHERE id_user = ?", (user_id,))
                bot_db_connection.commit()

            bot.send_message(message.chat.id, f"✅ Ваш аккаунт успешно отвязан: {name}.\n\n🆔 ID: {lowID}")
        else:
            bot.send_message(message.chat.id, "❌ Вы не привязали аккаунт. Используйте команду /connect.")
    
    except Exception as e:
        logger.error(f"Error in /unlink command: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['top'])
def top_command(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Топ по кубкам', callback_data='top_trophies_1'))
    keyboard.add(types.InlineKeyboardButton('Топ по ресурсам', callback_data='top_resources_1'))
    bot.send_message(message.chat.id, "Выберите тип топа:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('top_'))
def handle_top_callback(call):
    try:
        top_type, page = call.data.split('_')[1], int(call.data.split('_')[2])
        send_top(call.message, top_type, page)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logger.error(f"Error in handle_top_callback: {e}")
        bot.send_message(call.message.chat.id, f"❌ Произошла ошибка: {str(e)}")

def send_top(message, top_type='trophies', page=1):
    try:
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor(dictionary=True)
        limit = 10
        offset = (page - 1) * limit

        if top_type == 'trophies':
            query = """
                SELECT name, trophies FROM plrs 
                ORDER BY trophies DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            top_accounts = cursor.fetchall()
            header = "🏆 Топ аккаунты по кубкам:\n\n"
        else:
            query = """
                SELECT name, gems, gold, starpoints FROM plrs 
                ORDER BY (gems + gold + starpoints) DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            top_accounts = cursor.fetchall()
            header = "💎 Топ аккаунты по ресурсам:\n\n"

        if top_accounts:
            top_info = header
            for idx, account in enumerate(top_accounts, start=offset + 1):
                if top_type == 'trophies':
                    name, trophies = account['name'], account['trophies']
                    top_info += f"{idx}. {name}:\n🏆 Кубки: {trophies}\n\n"
                else:
                    name, gems, gold, starpoints = account['name'], account['gems'], account['gold'], account['starpoints']
                    top_info += f"{idx}. {name}:\n💎 Гемы: {gems}\n💰 Монеты: {gold}\n⭐ Старпоинты: {starpoints}\n\n"

            keyboard = types.InlineKeyboardMarkup()
            if page > 1:
                keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data=f'top_{top_type}_{page-1}'))
            keyboard.add(types.InlineKeyboardButton('➡️ Далее', callback_data=f'top_{top_type}_{page+1}'))
            
            bot.send_message(message.chat.id, top_info, reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "❌ Топ аккаунтов не найден!")
    
    except Exception as e:
        logger.error(f"Error in send_top function: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
@bot.message_handler(commands=['token'])
def token_command(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    try:
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(message.chat.id, "❌ Используйте: /token [lowID | #хештег]")
            return

        identifier = args[1].strip()
        lowID = None

        # Проверяем, является ли ввод хештегом
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if lowID is None:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        else:
            try:
                lowID = int(identifier)
            except ValueError:
                bot.send_message(message.chat.id, "❌ ID должен быть числом или хештегом в формате #...")
                return

        # Загружаем данные игрока
        player_data = loadbyID(lowID)
        if not player_data:
            bot.send_message(message.chat.id, f"❌ Аккаунт с lowID {lowID} не найден.")
            return

        # Извлекаем данные из playerData
        try:
            playerData = json.loads(player_data.get('playerData', '{}'))
        except json.JSONDecodeError:
            logger.warning(f"[WARNING] playerData не является JSON для ID {lowID}")
            playerData = {}

        # Получаем HashTag из playerData
        hash_tag = playerData.get("HashTag", "Отсутствует")

        # Основные поля
        name = player_data.get('name', 'Неизвестный')
        trophies = player_data.get('trophies', 0)
        gems = player_data.get('gems', 0)
        gold = player_data.get('gold', 0)
        tickets = player_data.get('tickets', 0)
        starpoints = player_data.get('starpoints', 0)
        vip = player_data.get('vip', 0)

        # Статус VIP
        vip_status = "Есть" if vip in [1, 2, 3] else "Отсутствует"

        # Формируем сообщение
        token_info = (
            f"📱 Токен аккаунта: `{player_data.get('token', '')}`\n"
            f"🆔 ID: {lowID}\n"
            f"🔗 Хештег: {hash_tag}\n"
            f"🤠 Имя: {name}\n\n"
        )

        bot.send_message(message.chat.id, token_info, parse_mode="Markdown")

    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат ID. Используйте число или хештег (#...)")
    except Exception as e:
        logger.error(f"[ERROR] /token: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['account'])
def update_token(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.send_message(message.chat.id, "❌ У вас недостаточно прав.")
        return

    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "❌ Используйте: /account [lowID | #хештег] [new_token]")
        return

    identifier = parts[1].strip()
    new_token = parts[2]

    # Определяем ID игрока
    player_id = None
    if identifier.startswith("#"):
        player_id = DataBase().get_id_by_hash(identifier)
        if not player_id:
            bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
            return
    else:
        try:
            player_id = int(identifier)
        except ValueError:
            bot.send_message(message.chat.id, "❌ ID должен быть числом или хештегом (#...)")
            return

    # Проверяем, существует ли игрок
    player_data = loadbyID(player_id)
    if not player_data:
        bot.reply_to(message, f"❌ Аккаунт с ID {player_id} не найден.")
        return

    # Обновляем токен через MySQL
    conn = DataBase.get_connection()
    if not conn:
        bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE plrs SET token = %s WHERE lowID = %s", (new_token, player_id))
        conn.commit()

        if cursor.rowcount == 0:
            bot.send_message(message.chat.id, "❌ Не удалось обновить токен. Возможно, игрок не найден.")
        else:
            bot.send_message(message.chat.id, f"✅ Токен для игрока с ID {player_id} успешно обновлён.")

    except Error as e:
        conn.rollback()
        logger.error(f"[ERROR] MySQL error in /account: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка базы данных: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        
PENDING_CODE_INPUT = {}  # Хранение пользователей, ожидающих ввода кода

@bot.message_handler(commands=['connect'])
def connect_command(message):
    user_id = message.from_user.id
    
    if user_id in PENDING_CODE_INPUT:
        bot.send_message(user_id, "❌ Вы уже начали процесс привязки.")
        return

    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(user_id, "❌ Используйте: /connect [lowID | #хештег]")
        return

    identifier = parts[1].strip()

    # Получаем lowID
    lowID = None
    if identifier.startswith("#"):
        lowID = DataBase().get_id_by_hash(identifier)
        if not lowID:
            bot.send_message(user_id, "❌ Игрок с таким хештегом не найден.")
            return
    else:
        if not identifier.isdigit():
            bot.send_message(user_id, "❌ ID должен быть числом или начинаться с `#`")
            return
        lowID = int(identifier)

    # Проверяем, есть ли уже привязанный аккаунт у этого пользователя
    with sqlite3.connect('users.db') as users_conn:
        users_cursor = users_conn.cursor()
        users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
        existing_account = users_cursor.fetchone()

    if existing_account:
        bot.send_message(user_id, "❌ Вы уже привязали аккаунт. Используйте `/unlink`, чтобы отвязать его.")
        return

    # Проверяем, не привязан ли этот lowID к кому-то ещё
    with sqlite3.connect('users.db') as users_conn:
        users_cursor = users_conn.cursor()
        users_cursor.execute("SELECT id_user FROM accountconnect WHERE lowID = ?", (lowID,))
        linked_user = users_cursor.fetchone()

    if linked_user:
        bot.send_message(user_id, f"❌ Этот аккаунт уже привязан!")
        return

    # Получаем данные игрока
    player_data = loadbyID(lowID)
    if not player_data:
        bot.send_message(user_id, f"❌ Аккаунт с ID {lowID} не найден!")
        return

    token = player_data.get('token', '')
    name = player_data.get('name', 'Неизвестный')
    trophies = player_data.get('trophies', 0)

    # Генерируем 4-значный код
    code = str(random.randint(1000, 9999))

    # Сохраняем код в JSON/SecretCodes.json
    secret_code_path = 'JSON/SecretCodes.json'
    try:
        with open(secret_code_path, 'r') as f:
            codes_data = json.load(f)
    except FileNotFoundError:
        codes_data = {"codes": []}

    entry = next((item for item in codes_data["codes"] if item.get("lowID") == lowID), None)
    if entry:
        entry.update({"code": code, "claimed": False})
    else:
        codes_data["codes"].append({
            "lowID": lowID,
            "code": code,
            "claimed": False
        })

    with open(secret_code_path, 'w') as f:
        json.dump(codes_data, f, indent=4)

    # Отправляем временное уведомление
    notif_result = DataBase().addNotification(
        lowID,
        notif_type=5,
        description=f"Был запрос к подключению аккаунта.\n<c1>Ваш код подтверждения: <c1></c><c3>{code}<c3></c>\n<c2>Если это не вы — проигнорируйте это сообщение.<c2></c>",
        brawlerID=0,
        skinID=52,
        gems=0
    )
    print(f"[DEBUG] Результат отправки уведомления: {notif_result}")

    # Ожидание ввода кода
    PENDING_CODE_INPUT[user_id] = {"lowID": lowID, "code": code}
    keyboard = types.InlineKeyboardMarkup()
    cancel_button = types.InlineKeyboardButton("❌ Отменить", callback_data="cancel_connect")
    keyboard.add(cancel_button)
    bot.send_message(user_id, "📩 Код подтверждения отправлен в игру. Введите его в чате Telegram.", reply_markup=keyboard)
     
def find_notification_index(self, lowID, partial_description):
    conn = DataBase.get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT notifications FROM plrs WHERE lowID = %s", (lowID,))
        result = cursor.fetchone()

        if not result or not result['notifications']:
            return None

        try:
            notifs = json.loads(result['notifications'])
        except json.JSONDecodeError:
            return None

        # Ищем уведомление по частичному совпадению в Desc
        for key, notif in notifs.items():
            if isinstance(notif, dict) and 'Desc' in notif:
                desc = notif['Desc']
                if partial_description in desc:
                    return key  # Возвращаем индекс уведомления
        return None
    finally:
        cursor.close()
        conn.close()
        
@bot.message_handler(func=lambda m: m.from_user.id in PENDING_CODE_INPUT)
def handle_verification_code(message):
    user_id = message.from_user.id
    data = PENDING_CODE_INPUT.get(user_id)

    if not data:
        return

    input_text = message.text.strip()
    if input_text == data['code']:
        lowID = data['lowID']

        try:
            # Обновляем статус claimed в SecretCodes.json
            with open('JSON/SecretCodes.json', 'r') as f:
                codes_data = json.load(f)

            for entry in codes_data['codes']:
                if entry.get('lowID') == lowID and entry.get('code') == data['code']:
                    entry['claimed'] = True
                    break

            with open('JSON/SecretCodes.json', 'w') as f:
                json.dump(codes_data, f, indent=4)

            # Загружаем данные игрока из MySQL
            player_data = loadbyID(lowID)
            if not player_data:
                bot.send_message(user_id, "❌ Аккаунт не найден.")
                del PENDING_CODE_INPUT[user_id]
                return

            token = player_data.get('token', '')
            name = player_data.get('name', 'Неизвестный')
            trophies = player_data.get('trophies', 0)
            username = message.from_user.username or ""

            # Привязываем аккаунт в SQLite
            with sqlite3.connect('users.db') as users_conn:
                cursor = users_conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS accountconnect (
                                    lowID INTEGER PRIMARY KEY,
                                    trophies INTEGER,
                                    name TEXT,
                                    id_user INTEGER,
                                    token TEXT,
                                    username TEXT
                                )''')
                cursor.execute("INSERT OR REPLACE INTO accountconnect (lowID, trophies, name, id_user, token, username) VALUES (?, ?, ?, ?, ?, ?)",
                               (lowID, trophies, name, user_id, token, username))
                users_conn.commit()

            # 🚫 Удаляем уведомление с кодом
            partial_desc = "Ваш код подтверждения:"  # Теперь ищем только по части текста
            notif_index = DataBase().find_notification_index(lowID, partial_desc)
            if notif_index is not None:
                DataBase().removeNotification(lowID, notif_index)
                print(f"[DEBUG] Уведомление с кодом удалено (индекс: {notif_index})")

            # ✅ Отправляем нотиф о привязке (если ещё не отправлено)
            success_notif_desc = "Вы успешно привязали аккаунт через OWN CONNECT!"
            if not DataBase().check_notification_exists(lowID, success_notif_desc):
                DataBase().addNotification(
                    lowID,
                    notif_type=1,
                    description=success_notif_desc,
                    brawlerID=0,
                    skinID=59,
                    gems=0
                )

            # ✉️ Отправляем ответ пользователю
            bot.send_message(user_id, f"✅ Аккаунт `{name}` успешно привязан!\n>ID: {lowID}\n>Кубки: {trophies}", parse_mode="Markdown")

            # 🧹 Очищаем состояние
            if user_id in PENDING_CODE_INPUT:
                del PENDING_CODE_INPUT[user_id]

        except Exception as e:
            logger.error(f"[ERROR] При обработке кода: {e}")
            bot.send_message(user_id, f"❌ Произошла ошибка: {str(e)}")
            if user_id in PENDING_CODE_INPUT:
                del PENDING_CODE_INPUT[user_id]
    else:
        bot.send_message(user_id, "❌ Неверный код. Попробуйте снова или нажмите ❌ Отменить.")
        
@bot.callback_query_handler(func=lambda call: call.data == "cancel_connect")
def cancel_connect_callback(call):
    user_id = call.from_user.id
    if user_id in PENDING_CODE_INPUT:
        del PENDING_CODE_INPUT[user_id]
        bot.answer_callback_query(call.id, text="❌ Привязка отменена.")
        bot.send_message(user_id, "❌ Привязка аккаунта отменена.")
    else:
        bot.answer_callback_query(call.id, text="❌ Нет активной операции.")
            
@bot.message_handler(commands=['info'])
def info_command(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(message.chat.id, "❌ Используйте: /info [lowID | #хештег]")
            return

        identifier = args[1]
        lowID = None

        # Проверяем, является ли ввод хештегом
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if lowID is None:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        else:
            try:
                lowID = int(identifier)
            except ValueError:
                bot.send_message(message.chat.id, "❌ Неверный формат. Используйте число или хештег.")
                return

        # Получаем данные игрока
        player_data = loadbyID(lowID)
        if not player_data:
            bot.send_message(message.chat.id, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Извлекаем данные из playerData
        playerData = json.loads(player_data.get('playerData', '{}'))
        hash_tag = playerData.get('HashTag', 'Отсутствует')
        name = player_data.get('name', 'Неизвестный')
        trophies = player_data.get('trophies', 0)
        gems = player_data.get('gems', 0)
        gold = player_data.get('gold', 0)
        tickets = player_data.get('tickets', 0)
        starpoints = player_data.get('starpoints', 0)
        vip = player_data.get('vip', 0)
        SCC = player_data.get('SCC', '')
        token = player_data.get('token', '')

        # Формируем ответ
        profile_info = (
            f"🤠 Статистика аккаунта: {name}\n"
            f"🆔 ID: {lowID}\n"
            f"📱 Токен: `{token}`\n"
            f"🔗 Хештег: {hash_tag}\n"
            f"🏆 Трофеи: {trophies}\n"
            f"💎 Гемы: {gems}\n"
            f"💸 Монеты: {gold}\n"
            f"🎟️ Билеты: {tickets}\n"
            f"⭐ Старпоинты: {starpoints}\n"
            f"💳 VIP: {'Есть' if vip > 0 else 'Отсутствует'}\n"
            f"🔑 Код автора: {SCC if SCC else 'Отсутствует'}"
        )
        bot.send_message(message.chat.id, profile_info, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"[ERROR] /info: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['resetbp'])
def reset_brawl_pass(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /resetbp [lowID | #хештег]")
        return

    identifier = args[1].strip()

    lowID = None
    if identifier.startswith("#"):
        # Поиск по хештегу
        lowID = DataBase().get_id_by_hash(identifier)
        if not lowID:
            bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
            return
    else:
        # Проверка, что это число
        if not identifier.isdigit():
            bot.send_message(message.chat.id, "❌ ID должен быть числом или начинаться с `#`")
            return
        lowID = int(identifier)

    try:
        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.send_message(message.chat.id, "❌ Аккаунт с таким lowID не найден!")
            return

        # Обновляем данные игрока
        freepass_data = json.dumps([])
        buypass_data = json.dumps([])

        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        cursor.execute("UPDATE plrs SET freepass = %s, buypass = %s, BPTOKEN = %s WHERE lowID = %s",
                       (freepass_data, buypass_data, 0, lowID))
        conn.commit()

        bot.send_message(message.chat.id, f"✅ Brawl Pass для аккаунта с ID {lowID} успешно сброшен.")

    except Exception as e:
        logger.error(f"[ERROR] /resetbp: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
@bot.message_handler(commands=['addpass'])
def add_brawl_pass(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте: /addpass [lowID | #хештег]")
        return

    identifier = args[1].strip()

    lowID = None
    if identifier.startswith("#"):
        lowID = DataBase().get_id_by_hash(identifier)
        if not lowID:
            bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
            return
    else:
        if not identifier.isdigit():
            bot.send_message(message.chat.id, "❌ ID должен быть числом или начинаться с `#`")
            return
        lowID = int(identifier)

    try:
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if lowID not in config["buybp"]:
            config["buybp"].append(lowID)
            bot.send_message(message.chat.id, f"✅ Brawl Pass добавлен для игрока с ID {lowID}.")
        else:
            bot.send_message(message.chat.id, f"❌ Brawl Pass уже выдан игроку с ID {lowID}.")

        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

    except Exception as e:
        logger.error(f"[ERROR] /addpass: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['removepass'])
def remove_brawl_pass(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.send_message(message.chat.id, "❌ Вы не являетесь администратором!")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте: /removepass [lowID | #хештег]")
        return

    identifier = args[1].strip()

    lowID = None
    if identifier.startswith("#"):
        lowID = DataBase().get_id_by_hash(identifier)
        if not lowID:
            bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
            return
    else:
        if not identifier.isdigit():
            bot.send_message(message.chat.id, "❌ ID должен быть числом или начинаться с `#`")
            return
        lowID = int(identifier)

    try:
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if lowID in config["buybp"]:
            config["buybp"].remove(lowID)
            bot.send_message(message.chat.id, f"✅ Brawl Pass удален у игрока с ID {lowID}.")
        else:
            bot.send_message(message.chat.id, f"❌ У игрока с ID {lowID} нет Brawl Pass.")

        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

    except Exception as e:
        logger.error(f"[ERROR] /removepass: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['name'])
def name_command(message):
    args = message.text.split(maxsplit=1)

    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /name [имя]")
        return

    name = args[1].strip()

    try:
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT lowID, name FROM plrs WHERE name = %s", (name,))
        plr_rows = cursor.fetchall()

        if plr_rows:
            keyboard = types.InlineKeyboardMarkup()
            for idx, row in enumerate(plr_rows):
                button_text = f"{idx + 1}. ID: {row['lowID']}, Имя: {row['name']}"
                keyboard.add(types.InlineKeyboardButton(button_text, callback_data=f'name_{row["lowID"]}'))

            bot.send_message(message.chat.id, f"Найдено несколько аккаунтов с именем `{name}`:", reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "❌ Аккаунт с указанным именем не найден.")

    except Exception as e:
        logger.error(f"[ERROR] /name: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
@bot.callback_query_handler(func=lambda call: call.data.startswith('name_'))
def handle_name_selection(call):
    try:
        lowID = int(call.data.split('_')[1])
        player_data = loadbyID(lowID)

        if not player_data:
            bot.send_message(call.message.chat.id, "❌ Аккаунт не найден.")
            return

        # Извлекаем данные
        token = player_data.get('token', '')
        name = player_data.get('name', 'Неизвестный')
        trophies = player_data.get('trophies', 0)
        gems = player_data.get('gems', 0)
        gold = player_data.get('gold', 0)
        tickets = player_data.get('tickets', 0)
        starpoints = player_data.get('starpoints', 0)
        vip = player_data.get('vip', 0)
        SCC = player_data.get('SCC', '')

        # Статус VIP
        vip_status = "Есть" if int(vip) in (1, 2, 3) else "Отсутствует"

        # Загрузка BrawlPass
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)
        bp_status = "Куплен" if lowID in config.get("buybp", []) else "Отсутствует"

        # Проверка привязки в users.db
        with sqlite3.connect('users.db') as bot_db_connection:
            bot_db_cursor = bot_db_connection.cursor()
            bot_db_cursor.execute("SELECT username FROM accountconnect WHERE lowID = ?", (lowID,))
            user_row = bot_db_cursor.fetchone()

        registration_info = f"Подтвержден: @{user_row[0]}" if user_row else "Аккаунт: Не подтвержден"

        # Формируем сообщение
        profile_info = (
            f"🤠 Статистика аккаунта: {escape_markdown(name.strip())}:\n\n"
            f"🆔 ID: {lowID}\n📱 Токен: `ONLYADMIN`\n\n"
            f"🏆 Трофеи: {trophies}\n💎 Гемы: {gems}\n💸 Монеты: {gold}\n"
            f"🎟️ Билеты: {tickets}\n⭐ Старпоинты: {starpoints}\n\n"
            f"💳 VIP: {vip_status}\n🎫 BrawlPass: {bp_status}\n"
            f"🔑 Код автора: {SCC if SCC else 'Отсутствует'}\n\n"
            f"{registration_info}"
        )

        bot.send_message(call.message.chat.id, profile_info, parse_mode='HTML')
        bot.delete_message(call.message.chat.id, call.message.message_id)

    except Exception as e:
        logger.error(f"[ERROR] handle_name_selection: {e}")
        bot.send_message(call.message.chat.id, f"❌ Произошла ошибка: {str(e)}")
            
PENDING_RECOVERY = {}

@bot.message_handler(commands=['recovery'])
def recovery_command(message):
    user_id = message.from_user.id

    if user_id in PENDING_RECOVERY:
        bot.send_message(user_id, "❌ Вы уже начали процесс восстановления.")
        return

    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(user_id, "❌ Используйте: /recovery [lost_identifier] [new_identifier]")
        bot.send_message(user_id, "Пример:\n/recovery #8YQ0QL0 #8V2G2JO")
        return

    lost_identifier = parts[1].strip()
    new_identifier = parts[2].strip()

    # Получаем lost_lowID
    lost_lowID = None
    if lost_identifier.startswith("#"):
        lost_lowID = DataBase().get_id_by_hash(lost_identifier)
        if not lost_lowID:
            bot.send_message(user_id, "❌ Потерянный игрок не найден по хештегу.")
            return
    elif lost_identifier.isdigit():
        lost_lowID = int(lost_identifier)
    else:
        bot.send_message(user_id, "❌ ID должен быть числом или начинаться с `#`")
        return

    # Получаем new_lowID
    new_lowID = None
    if new_identifier.startswith("#"):
        new_lowID = DataBase().get_id_by_hash(new_identifier)
        if not new_lowID:
            bot.send_message(user_id, "❌ Новый игрок не найден по хештегу.")
            return
    elif new_identifier.isdigit():
        new_lowID = int(new_identifier)
    else:
        bot.send_message(user_id, "❌ ID должен быть числом или начинаться с `#`")
        return

    # Проверяем, существует ли новый аккаунт
    new_player_data = loadbyID(new_lowID)
    if not new_player_data:
        bot.send_message(user_id, f"❌ Новый аккаунт с ID {new_lowID} не найден.")
        return

    # Проверяем, что потерянный аккаунт не привязан никем другим
    with sqlite3.connect('users.db') as users_conn:
        users_cursor = users_conn.cursor()
        users_cursor.execute("SELECT id_user FROM accountconnect WHERE lowID = ?", (lost_lowID,))
        result = users_cursor.fetchone()

    if result is None:
        bot.send_message(user_id, "❌ Потерянный аккаунт не привязан ни к одному Telegram-аккаунту.")
        return

    if result[0] != user_id:
        bot.send_message(user_id, "❌ Этот аккаунт привязан к другому Telegram-пользователю.")
        return

    # Проверяем, что новый аккаунт свободен
    with sqlite3.connect('users.db') as users_conn:
        users_cursor = users_conn.cursor()
        users_cursor.execute("SELECT id_user FROM accountconnect WHERE lowID = ?", (new_lowID,))
        linked_user = users_cursor.fetchone()

    if linked_user:
        bot.send_message(user_id, f"❌ Аккаунт с ID {new_lowID} уже привязан к другому пользователю.")
        return

    # Генерируем код
    code = str(random.randint(1000, 9999))

    # Обновляем SecretCodes.json
    secret_code_path = 'JSON/SecretCodes.json'
    try:
        with open(secret_code_path, 'r') as f:
            codes_data = json.load(f)
    except FileNotFoundError:
        codes_data = {"codes": []}

    entry = next((item for item in codes_data["codes"] if item.get("new_lowID") == new_lowID), None)
    if entry:
        entry.update({"lost_lowID": lost_lowID, "code": code, "claimed": False})
    else:
        codes_data["codes"].append({
            "lost_lowID": lost_lowID,
            "new_lowID": new_lowID,
            "code": code,
            "claimed": False
        })

    with open(secret_code_path, 'w') as f:
        json.dump(codes_data, f, indent=4)

    # Отправляем уведомление на новый аккаунт
    notif_result = DataBase().addNotification(
        new_lowID,
        notif_type=5,
        description=f"Был запрос к восстановлению аккаунта.\n<c1>Ваш код подтверждения: <c1></c><c3>{code}<c3></c>\n<c2>Если это не вы — проигнорируйте<c2></c>",
        brawlerID=0,
        skinID=0,
        gems=0
    )
    print(f"[DEBUG] Результат отправки уведомления: {notif_result}")

    # Сохраняем в PENDING_RECOVERY
    PENDING_RECOVERY[user_id] = {
        "lost_lowID": lost_lowID,
        "new_lowID": new_lowID,
        "code": code
    }

    # Кнопка отмены
    keyboard = types.InlineKeyboardMarkup()
    cancel_button = types.InlineKeyboardButton("❌ Отменить", callback_data="cancel_recovery")
    keyboard.add(cancel_button)
    bot.send_message(user_id, "📩 Код подтверждения отправлен в игру. Введите его в Telegram.", reply_markup=keyboard)
    
@bot.message_handler(func=lambda m: m.from_user.id in PENDING_RECOVERY)
def handle_recovery_code(message):
    user_id = message.from_user.id
    data = PENDING_RECOVERY.get(user_id)

    if not data:
        return

    input_text = message.text.strip()
    if input_text == data.get('code'):
        lost_lowID = data.get('lost_lowID')
        new_lowID = data.get('new_lowID')

        if not all([lost_lowID, new_lowID]):
            bot.send_message(user_id, "❌ Ошибка данных восстановления.")
            del PENDING_RECOVERY[user_id]
            return

        try:
            # Получаем данные нового аккаунта
            new_player = loadbyID(new_lowID)
            if not new_player:
                bot.send_message(user_id, "❌ Новый аккаунт не найден.")
                return

            new_token = new_player.get('token', '')
            if not new_token:
                bot.send_message(user_id, "❌ Токен нового аккаунта отсутствует.")
                return

            # Подключаемся к MySQL
            conn = DataBase.get_connection()
            if not conn:
                bot.send_message(user_id, "❌ Не удалось подключиться к базе данных.")
                return

            cursor = conn.cursor()

            try:
                # ❌ УДАЛЯЕМ НОВЫЙ АККАУНТ СРАЗУ (до обновления токена у старого)
                cursor.execute("DELETE FROM plrs WHERE lowID = %s", (new_lowID,))
                conn.commit()

                # ✅ Обновляем токен у потерянного аккаунта
                cursor.execute("UPDATE plrs SET token = %s WHERE lowID = %s", (new_token, lost_lowID))
                conn.commit()

                # Проверяем, было ли изменение
                if cursor.rowcount == 0:
                    bot.send_message(user_id, f"❌ Не удалось обновить токен у ID {lost_lowID}")
                    return

                # Удаляем уведомление с кодом из нового аккаунта (если осталось)
                notif_index = DataBase().find_notification_index(new_lowID, f"Ваш код подтверждения: <c3>{data['code']}</c3>")
                if notif_index is not None:
                    DataBase().removeNotification(new_lowID, notif_index)

                # Отправляем уведомление на потерянный аккаунт
                success_notif_result = DataBase().addNotification(
                    lost_lowID,
                    notif_type=5,
                    description="<c3>Аккаунт успешно восстановлен через OWN CONNECT!<c3></c>",
                    brawlerID=0,
                    skinID=0,
                    gems=0
                )
                print(f"[DEBUG] Результат добавления уведомления об успехе: {success_notif_result}")

                # Чистим состояние
                if user_id in PENDING_RECOVERY:
                    del PENDING_RECOVERY[user_id]

                bot.send_message(user_id, "✅ Аккаунт восстановлен! Перезайдите в игру.")

            finally:
                cursor.close()
                conn.close()

        except Exception as e:
            logger.error(f"[ERROR] handle_recovery_code: {e}")
            bot.send_message(user_id, f"❌ Ошибка при восстановлении: {str(e)}")
            if user_id in PENDING_RECOVERY:
                del PENDING_RECOVERY[user_id]
    else:
        bot.send_message(user_id, "❌ Неверный код. Попробуйте снова или нажмите ❌ Отменить.")


@bot.callback_query_handler(func=lambda call: call.data == "cancel_recovery")
def cancel_recovery_callback(call):
    user_id = call.from_user.id
    if user_id in PENDING_RECOVERY:
        del PENDING_RECOVERY[user_id]
        bot.answer_callback_query(call.id, text="❌ Процесс отменён.")
        bot.send_message(user_id, "❌ Процесс восстановления отменён.")
    else:
        bot.answer_callback_query(call.id, text="❌ Нет активной операции.")
        
# Структура для скинов
skins = {
    'common': [29, 15, 2, 109, 27, 139, 111, 137, 152, 75],
    'rare': [25, 58, 98, 28, 92, 158, 130, 88, 93, 104, 132, 108, 45, 125, 117, 11, 126, 131, 20, 110],
    'epic': [52, 159, 79, 44, 163, 91, 160, 99, 30, 128, 71, 59, 26, 68, 147, 50, 96, 118],
    'legendary': [94, 49, 95]
}

# Привязка цен к редкостям
skin_prices = {
    "common": (29, 29),
    "rare": (79, 79),
    "epic": (149, 149),
    "legendary": (299, 299)
}

def get_offers():
    with open("JSON/offers.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    offer_list = "Список акций:\n"
    for offer_id, offer_data in data.items():
        vault = offer_data['ShopType']
        daily = offer_data['ShopDisplay']
        current = ""
        types = ""

        if vault == 1:
            current = "Золото"
        elif vault == 0:
            current = "Кристаллы"

        if daily == 1:
            types = "Ежедневная"
        elif daily == 0:
            types = "Обычная"

        offer_list += f"\nАкция #{offer_id}\n"
        offer_list += f"Название: {offer_data['OfferTitle']}\n"
        offer_list += f"Тип: {types}\n"
        offer_list += f"Боец: {offer_data['BrawlerID'][0]}\n"
        offer_list += f"Скин: {offer_data['SkinID'][0]}\n"
        offer_list += f"Валюта: {current}\n"
        offer_list += f"Стоимость: {offer_data['Cost']}\n"
        offer_list += f"Множитель: {offer_data['Multiplier'][0]}\n"

    return offer_list
    
@bot.message_handler(commands=['list'])
def handle_list_offers(message):
    offer_list = get_offers()
    bot.send_message(chat_id=message.chat.id, text=offer_list)

import shlex
import json
import logging
from telebot import types

logger = logging.getLogger(__name__)

@bot.message_handler(commands=['new_offer'])
def add_offer(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды.")
        return

    try:
        # Обработка команды
        args = shlex.split(message.text)[1:]  # Пропускаем '/new_offer'
        
        # Проверяем количество аргументов (теперь 11)
        if len(args) != 11:
            bot.reply_to(message, """Список ID предложений в магазине:
0 = Бесплатный ящик Brawl Box
1 = Золото
2 = Случайный боец
3 = Боец
4 = Скин
5 = Звёздная сила / Гаджет
6 = Ящик Brawl Box
7 = Билеты (больше не работают)
8 = Очки силы (для конкретного бойца)
9 = Удвоитель жетонов
10 = Мегаящик
11 = Ключи (???)
12 = Очки силы
13 = Слот события (???)
14 = Большой ящик
15 = Рекламный ящик (больше не работают)
16 = Гемы
17 = СТАРДРОП???
19 = Пин для бойца
20 = Коллекция пинов
21 = Набор пинов
22 = Набор пинов для бойца
23 = Обычный пин (???)
24 = Предложение скина в магазине (может не работать)
94 = Скин (???)

Список BGR предложений:
Предложение жетонов = offer_generic
Специальное предложение = offer_special
Предложение за звёздные очки = offer_legendary
Предложение монет = offer_coins (в версии 29 как offer_moon_festival)
Предложение гемов = offer_gems
Предложение ящиков = offer_boxes
Предложение бойца = offer_finals
Предложение Лунного Нового года = offer_lny
Архивное предложение = offer_archive
Хроматическое предложение = offer_chromatic
Предложение Лунного фестиваля = offer_moon_festival
Рождественское предложение = offer_xmas

ET означает дополнительный текст.

Используйте команду /new_offer с аргументами в формате: /new_offer <ID> <Multiplier> <BrawlerID> <SkinID> <ShopType> <Cost> <OfferView> <ShopDisplay> <Oldcost> <OfferTitle> <OfferRGB>
ID - Айди акций, можно посмотреть в Logic/Shop.py или сообщением выше.\nMultiplier - Кол-во (с ящиками не работает).\nBrawlerID - Айди бойца.\nSkinID - айди скина.\nShopType - за какую валюту покупают предмет, пример: 0 - гемы, 1 - золото, 3 - старпоинты.\nCost - стоимость.\nOfferView - просмотренна ли акция или нет, пример: 0 - абсолютно новая, 1 - новая, 2 - просмотренна.\nShopDisplay - вид акции, пример: 0 - обыкновенная, 1 - дневная (квадратик).\nOldcost - старая цена.\nOfferTitle - название акции.\nOfferRGB - внешний вид (сообщение выше).
""")
            return

        # Парсим обязательные параметры
        try:
            offer_id = int(args[0])
            multiplier = int(args[1])
            brawler_id = int(args[2])
            skin_id = int(args[3])
            shop_type = int(args[4])
            cost = int(args[5])
            offer_view = int(args[6])
            shop_display = int(args[7])
            old_cost = int(args[8])
            offer_title = args[9]
            offer_bgr = args[10]
        except (ValueError, IndexError) as ve:
            bot.reply_to(message, f"❌ Ошибка в данных: {ve}")
            return

        # Формируем новую акцию
        new_offer = {
            "ID": [offer_id, 0, 0],
            "Multiplier": [multiplier, 0, 0],  # Основной множитель
            "BrawlerID": [brawler_id, 0, 0],
            "SkinID": [skin_id, 0, 0],
            "ShopType": shop_type,
            "Cost": cost,
            "Timer": 86400,
            "OfferView": offer_view,
            "WhoBuyed": [],
            "ShopDisplay": shop_display,
            "OldCost": old_cost,
            "OfferTitle": offer_title,
            "OfferBGR": offer_bgr,
            "ETType": 0,  # Зафиксируем значение ETType
            "ETMultiplier": multiplier  # Установим ETMultiplier равным Multiplier
        }

        # Сохраняем в файл
        try:
            with open('JSON/offers.json', 'r', encoding='utf-8') as f:
                offers = json.load(f)
            
            # Добавляем новую акцию
            offers[str(len(offers))] = new_offer
            
            with open('JSON/offers.json', 'w', encoding='utf-8') as f:
                json.dump(offers, f, indent=4, ensure_ascii=False)
            
            bot.reply_to(message, f"✅ Акция c айди #{offer_id} добавлена: {offer_title}")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"[ERROR] offers.json не найден или поврежден: {e}")
            bot.reply_to(message, "❌ Не удалось открыть файл акций.")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка записи offers.json: {e}")
            bot.reply_to(message, "❌ Ошибка сохранения акции.")

    except Exception as e:
        logger.error(f"[ERROR] /new_offer: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['rename'])
def change_name(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ У вас недостаточно прав для использования этой команды.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /rename [lowID | #хештег] [новое имя]")
            return

        identifier = parts[1].strip()
        new_name = parts[2]

        # Определяем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        else:
            if not identifier.isdigit():
                bot.send_message(message.chat.id, "❌ ID должен быть числом или начинаться с `#`")
                return
            lowID = int(identifier)

        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Обновляем имя через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET name = %s WHERE lowID = %s", (new_name, lowID))
            conn.commit()

            bot.send_message(message.chat.id, f"✅ Игроку с айди `{lowID}` изменено имя на '{new_name}'.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logger.error(f"[ERROR] /rename: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['remove_offer'])
def remove_offer(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ У вас недостаточно прав!")
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, '❌ Используйте: /remove_offer <ID>')
            return

        offer_id = parts[1]
        if int(offer_id) <= 13:
            bot.reply_to(message, f"❌ Акция с ID {offer_id} не может быть удалена!")
            return

        with open('JSON/offers.json', 'r', encoding='utf-8') as f:
            offers = json.load(f)

        if offer_id not in offers:
            bot.reply_to(message, f'❌ Акция с ID {offer_id} не найдена')
            return

        del offers[offer_id]

        with open('JSON/offers.json', 'w', encoding='utf-8') as f:
            json.dump(offers, f, indent=4)

        bot.reply_to(message, f'✅ Акция с ID {offer_id} удалена')

    except Exception as e:
        logger.error(f"[ERROR] /remove_offer: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['theme'])
def theme(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, """Выберите ID темы:
0 - Обычная
1 - Новый год (Снег)
2 - Красный новый год
3 - От клеш рояля
4 - Обычный фон с дефолт музыкой
5 - Желтые панды
7 - Роботы Зелёный фон
8 - Хэллуин 2019
9 - Пиратский фон (Новый год 2020)
10 - Фон с обновы с мистером п.
11 - Футбольный фон
12 - Годовщина Supercell
13 - Базар Тары
14 - Лето с монстрами
15 - Гавс
16 - Зайчики
Используйте: /theme [ID]""")
            return

        theme_id = int(parts[1])

        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET theme = %s", (theme_id,))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Тема для всех игроков изменена на ID {theme_id}.")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID темы должен быть числом.")
    except Exception as e:
        logger.error(f"[ERROR] /theme: {e}")
        bot.reply_to(message, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['code'])
def new_code(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ У вас недостаточно прав!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Используйте: /code [new code] (на английском)")
            return

        new_code = parts[1].upper()

        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if new_code in config["CCC"]:
            bot.reply_to(message, f"❌ Код {new_code} уже существует!")
            return

        config["CCC"].append(new_code)
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        bot.send_message(message.chat.id, f"✅ Новый код `{new_code}` добавлен!")

    except Exception as e:
        logger.error(f"[ERROR] /code: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['code_list'])
def code_list(message):
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        code_list = '\n'.join(data["CCC"])
        bot.send_message(message.chat.id, f"Список кодов:\n{code_list}")

    except Exception as e:
        logger.error(f"[ERROR] /code_list: {e}")
        bot.send_message(message.chat.id, "❌ Не удалось загрузить список кодов.")
        
@bot.message_handler(commands=['uncode'])
def del_code(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ У вас недостаточно прав!")
        return

    try:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "❌ Правильное использование: /uncode [code]")
            return

        code = message.text.split()[1]
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if code in config["CCC"]:
            config["CCC"].remove(code)
            with open("config.json", "w", encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            bot.send_message(message.chat.id, f"✅ Код `{code}` был удалён!")
        else:
            bot.send_message(message.chat.id, f"❌ Код `{code}` не найден!")

    except Exception as e:
        logger.error(f"[ERROR] /uncode: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['code_info'])
def code_info(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in creator1 and user_id not in creator2 and user_id not in creator3:
        bot.reply_to(message, "❌ У вас нет доступа к данной команде!")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❌ Используйте команду в формате: /code_info [code]")
        return

    code = args[1]

    try:
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if code not in config["CCC"]:
            bot.send_message(message.chat.id, f"❌ Код `{code}` не найден в списке.")
            return

        # Проверяем, сколько аккаунтов используют этот код через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM plrs WHERE SCC = %s", (code,))
        count = cursor.fetchone()[0]

        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

        if count > 0:
            bot.send_message(message.chat.id, f"🔍 Код `{code}` используется {count} аккаунтами.")
        else:
            bot.send_message(message.chat.id, f"❌ Код `{code}` не используется ни одним аккаунтом.")

    except FileNotFoundError:
        bot.send_message(message.chat.id, "❌ Файл конфигурации не найден.")
    except json.JSONDecodeError:
        bot.send_message(message.chat.id, "❌ Ошибка чтения конфигурации. Проверьте файл config.json.")
    except Exception as e:
        logger.error(f"[ERROR] /code_info: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['vip'])
def add_vip(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Правильное использование: /vip [lowID | #хештег]")
            return

        identifier = parts[1].strip()

        vip_id = None
        if identifier.startswith("#"):
            # Поиск по хештегу
            vip_id = DataBase().get_id_by_hash(identifier)
            if not vip_id:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        else:
            # Поиск по ID
            if not identifier.isdigit():
                bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
                return
            vip_id = int(identifier)

        # Проверяем, существует ли игрок
        player_data = loadbyID(vip_id)
        if not player_data:
            bot.send_message(message.chat.id, f"❌ Игрок с ID {vip_id} не найден.")
            return

        # Обновляем config.json
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if vip_id in config["vips"]:
            bot.send_message(message.chat.id, f"❌ Игрок с ID {vip_id} уже имеет VIP статус.")
            return

        config["vips"].append(vip_id)
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        # Обновляем поле `vip` в MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET vip = 1 WHERE lowID = %s", (vip_id,))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Вип статус выдан игроку с ID {vip_id}")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом или хештегом (#...)")
    except Exception as e:
        logger.error(f"[ERROR] /vip: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
@bot.message_handler(commands=['unvip'])
def del_vip(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Правильное использование: /unvip [lowID | #хештег]")
            return

        identifier = parts[1].strip()

        vip_id = None
        if identifier.startswith("#"):
            # Поиск по хештегу
            vip_id = DataBase().get_id_by_hash(identifier)
            if not vip_id:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        else:
            if not identifier.isdigit():
                bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
                return
            vip_id = int(identifier)

        # Проверяем, есть ли такой игрок
        player_data = loadbyID(vip_id)
        if not player_data:
            bot.send_message(message.chat.id, f"❌ Игрок с ID {vip_id} не найден.")
            return

        # Работаем с config.json
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if vip_id not in config["vips"]:
            bot.send_message(message.chat.id, f"❌ Игрок с ID {vip_id} не имеет VIP статуса.")
            return

        config["vips"].remove(vip_id)
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        # Обновляем в MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET vip = 0 WHERE lowID = %s", (vip_id,))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Вип статус забран у игрока с ID {vip_id}")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом или хештегом")
    except Exception as e:
        logger.error(f"[ERROR] /unvip: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
STAR_SKINS = {
    103: 500,
    102: 2500,
    100: 10000,
    101: 50000,
    120: 500,
    165: 10000,
    167: 500,
    123: 10000,
    118: 500,
    108: 500
}

def save_last_update():
    now = dt.now(pytz.timezone("Europe/Moscow"))
    update_time = now.strftime("%Y-%m-%d %H:%M:%S")
    with open("JSON/last_update.json", "w", encoding="utf-8") as f:
        json.dump({"last_update": update_time}, f, indent=4, ensure_ascii=False)
    
    for admin in admins:
        try:
            bot.send_message(admin, f"✅ Магазин обновлён в {update_time} по МСК")
        except Exception as e:
            print(f"Ошибка при отправке сообщения администратору {admin}: {e}")

def auto_shop():
    try:
        shop_items = [
            {"StarPowerCard": [76, 135], "GadgetCard": [255, 288], "Brawler": 0},
            {"StarPowerCard": [77, 138], "GadgetCard": [273], "Brawler": 1},
            {"StarPowerCard": [78, 137], "GadgetCard": [272], "Brawler": 2},
            {"StarPowerCard": [79, 150], "GadgetCard": [245], "Brawler": 3},
            {"StarPowerCard": [80, 156], "GadgetCard": [246], "Brawler": 4},
            {"StarPowerCard": [81, 151], "GadgetCard": [247], "Brawler": 5},
            {"StarPowerCard": [82, 158], "GadgetCard": [250, 293], "Brawler": 6},
            {"StarPowerCard": [83, 149], "GadgetCard": [251, 295], "Brawler": 7},
            {"StarPowerCard": [84, 136], "GadgetCard": [249], "Brawler": 8},
            {"StarPowerCard": [85, 155], "GadgetCard": [258, 294], "Brawler": 9},
            {"StarPowerCard": [86, 140], "GadgetCard": [264, 292], "Brawler": 10},
            {"StarPowerCard": [87, 154], "GadgetCard": [265, 290], "Brawler": 11},
            {"StarPowerCard": [88, 143], "GadgetCard": [243, 286], "Brawler": 12},
            {"StarPowerCard": [89, 144], "GadgetCard": [267], "Brawler": 13},
            {"StarPowerCard": [90, 148], "GadgetCard": [263, 289], "Brawler": 14},
            {"StarPowerCard": [91, 152], "GadgetCard": [268, 291], "Brawler": 15},
            {"StarPowerCard": [92, 139], "GadgetCard": [257], "Brawler": 16},
            {"StarPowerCard": [93, 160], "GadgetCard": [266], "Brawler": 17},
            {"StarPowerCard": [94, 157], "GadgetCard": [260], "Brawler": 18},
            {"StarPowerCard": [99, 142], "GadgetCard": [248, 287], "Brawler": 19},
            {"StarPowerCard": [104, 153], "GadgetCard": [261], "Brawler": 20},
            {"StarPowerCard": [109, 159], "GadgetCard": [252], "Brawler": 21},
            {"StarPowerCard": [114, 161], "GadgetCard": [253], "Brawler": 22},
            {"StarPowerCard": [119, 141], "GadgetCard": [276], "Brawler": 23},
            {"StarPowerCard": [124, 147], "GadgetCard": [242], "Brawler": 24},
            {"StarPowerCard": [129, 145], "GadgetCard": [262], "Brawler": 25},
            {"StarPowerCard": [134, 146], "GadgetCard": [275], "Brawler": 26},
            {"StarPowerCard": [168, 181], "GadgetCard": [259], "Brawler": 27},
            {"StarPowerCard": [186, 187], "GadgetCard": [270], "Brawler": 28},
            {"StarPowerCard": [192, 193], "GadgetCard": [271], "Brawler": 29},
            {"StarPowerCard": [198, 199], "GadgetCard": [274], "Brawler": 30},
            {"StarPowerCard": [204, 205], "GadgetCard": [269], "Brawler": 31},
            {"StarPowerCard": [210, 211], "GadgetCard": [254], "Brawler": 32},
            {"StarPowerCard": [222, 223], "GadgetCard": [256], "Brawler": 34},
            {"StarPowerCard": [228, 229], "GadgetCard": [277], "Brawler": 35},
            {"StarPowerCard": [234, 235], "GadgetCard": [278], "Brawler": 36},
            {"StarPowerCard": [240, 241], "GadgetCard": [244], "Brawler": 37},
            {"StarPowerCard": [283, 284], "GadgetCard": [285], "Brawler": 38},
            {"StarPowerCard": [300, 301], "GadgetCard": [302], "Brawler": 39}
        ]
        with open('JSON/offers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        used_skins = set()
        valid_brawler_ids = [i for i in range(0, 40) if i != 33]

        with open('config.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        available_skins = set(settings['Skinse'])
        
        # --- Первая акция: подарок ---
        choice = random.choice([1, 2, 3])

        if choice == 1:  
            gift_id = 1  # Золото  
            gold_amount = random.choice([25, 50, 75, 150, 300])  
            cost = random.randint(1, 15)  
            oldcost = cost + random.randint(1, 15)
        elif choice == 2:  
            gift_id = 16  # Гемы  
            gold_amount = random.randint(1, 10)  
            cost = random.randint(1, 15)  
            oldcost = cost + random.randint(1, 15)
        elif choice == 3:  
            gift_id = 6  # Например, новый предмет  
            gold_amount = 1  # Другое количество  
            cost = random.randint(1, 15)  # Другая стоимость
            oldcost = cost + random.randint(1, 15)

        data["0"] = {
            "ID": [gift_id, 0, 0],
            "Multiplier": [gold_amount, 0, 0],
            "BrawlerID": [0, 0, 0],
            "SkinID": [0, 0, 0],
            "ShopType": 1,
            "Cost": cost,
            "Timer": 86400,
            "OfferView": 0,
            "WhoBuyed": [],
            "ShopDisplay": 1,
            "OldCost": oldcost,
            "OfferTitle": "ПОДАРОК!",
            "OfferBGR": "0",
            "ETType": 0,
            "ETMultiplier": 0
        }
        
        selected_item = random.choice(shop_items)
        all_powerups = selected_item["GadgetCard"] + selected_item["StarPowerCard"]
        powerup_id = random.choice(all_powerups)
        powerup_cost = 1000 if powerup_id in selected_item["GadgetCard"] else 2000

        data["1"] = {
            "ID": [5, 0, 0],
            "Multiplier": [0, 0, 0],
            "BrawlerID": [selected_item["Brawler"], 0, 0],
            "SkinID": [powerup_id, 0, 0],
            "ShopType": 1,
            "Cost": powerup_cost,
            "Timer": 86400,
            "OfferView": 0,
            "WhoBuyed": [],
            "ShopDisplay": 1,
            "OldCost": 0,
            "OfferTitle": "УЛУЧШЕНИЕ",
            "OfferBGR": "0",
            "ETType": 0,
            "ETMultiplier": 0
        }
        
        for i in range(2, 6):
            if not valid_brawler_ids:
                bot.reply_to(message, "❌ Недостаточно бойцов для создания акций!")
                return

            multiplier = random.randint(10, 456)
            brawler_id = random.choice(valid_brawler_ids)
            valid_brawler_ids.remove(brawler_id)  # Удаляем выбранного бойца, чтобы не повторялся

            new_offer = {
                "ID": [8, 0, 0],
                "Multiplier": [multiplier, 0, 0],
                "BrawlerID": [brawler_id, 0, 0],
                "SkinID": [0, 0, 0],
                "ShopType": 1,
                "Cost": multiplier * 2,
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 1,
                "OldCost": 0,
                "OfferTitle": "ЕЖЕДНЕВНАЯ АКЦИЯ",
                "OfferBGR": "0",
                "ETType": 0,
                "ETMultiplier": 0
            }

            data[str(i)] = new_offer

        for i in range(6, 12):
            if not available_skins:
                bot.reply_to(message, "❌ Недостаточно скинов для создания акций!")
                return

            random_skin = random.choice(list(available_skins))
            available_skins.remove(random_skin)
            used_skins.add(random_skin)

            # Определение редкости
            all_skins_by_rarity = get_skin_ids_by_rarity(None)
            rarity = next((r for r, skins in all_skins_by_rarity.items() if random_skin in skins), 'common')
            cost = random.randint(*get_price_range_by_rarity(rarity))

            # Сохраняем старую стоимость
            old_cost = cost  

            # Определяем скидку с шансом 30%
            discount = 0
            if random.random() < 0.3:  # 30% шанс на скидку
                if rarity == 'common':
                    discount = 10
                elif rarity == 'rare':
                    discount = 30
                elif rarity == 'epic':
                    discount = 50
                elif rarity == 'legendary':
                    discount = 100

            # Применяем скидку, если она выпала
            cost = max(0, cost - discount)  # Цена не может быть меньше 0

            # Устанавливаем ShopType в 1, если это золотой скин
            shop_type = 1 if rarity in ['gold', 'silver'] else 0

            new_offer = {
                "ID": [4, 0, 0],
                "Multiplier": [0, 0, 0],
                "BrawlerID": [0, 0, 0],
                "SkinID": [random_skin, 0, 0],
                "ShopType": shop_type,
                "Cost": cost,
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 0,
                "OldCost": old_cost,  # Сохраняем старую стоимость
                "OfferTitle": "ЕЖЕДНЕВНЫЙ СКИН",
                "OfferBGR": "0",
                "ETType": 0,
                "ETMultiplier": 0
            }

            data[str(i)] = new_offer

        # Генерация 2 звездных скинов
        selected_star_skins = random.sample(list(STAR_SKINS.keys()), 2)

        for idx, skin_id in enumerate(selected_star_skins, start=12):
            new_star_offer = {
                "ID": [4, 0, 0],
                "Multiplier": [0, 0, 0],
                "BrawlerID": [0, 0, 0],
                "SkinID": [skin_id, 0, 0],
                "ShopType": 3,
                "Cost": STAR_SKINS[skin_id],
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 0,
                "OldCost": 0,
                "OfferTitle": "ЗВЁЗДНЫЙ СКИН",
                "OfferBGR": "0",
                "ETType": 0,
                "ETMultiplier": 0
            }

            data[str(idx)] = new_star_offer
            
        if random.random() < 0.1:
            next_index = str(len(data))
            data[next_index] = {
                "ID": [10, 0, 0],
                "Multiplier": [1, 0, 0],
                "BrawlerID": [0, 0, 0],
                "SkinID": [0, 0, 0],
                "ShopType": 3,
                "Cost": 1500,
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 0,
                "OldCost": 0,
                "OfferTitle": "ОСОБАЯ АКЦИЯ",
                "OfferBGR": "offer_legendary",
                "ETType": 0,
                "ETMultiplier": 0
            }
            
            next_index = str(len(data))
            data[next_index] = {
                "ID": [14, 0, 0],
                "Multiplier": [1, 0, 0],
                "BrawlerID": [0, 0, 0],
                "SkinID": [0, 0, 0],
                "ShopType": 3,
                "Cost": 500,
                "Timer": 86400,
                "OfferView": 0,
                "WhoBuyed": [],
                "ShopDisplay": 0,
                "OldCost": 0,
                "OfferTitle": "ОСОБАЯ АКЦИЯ",
                "OfferBGR": "offer_legendary",
                "ETType": 0,
                "ETMultiplier": 0
            }

        with open('JSON/offers.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        save_last_update()
    except Exception as e:
        print(f"Ошибка при обновлении магазина: {e}")
        
def schedule_auto_shop():
    now = dt.now(pytz.timezone("Europe/Moscow"))  # ✅ Используем dt вместо datetime.datetime
    next_run = now.replace(hour=11, minute=0, second=0, microsecond=0)
    
    if now >= next_run:
        next_run += timedelta(days=1)
    
    initial_delay = (next_run - now).total_seconds()

    def run_periodically():
        delay = initial_delay
        while True:
            time.sleep(delay)
            auto_shop()
            delay = 24 * 60 * 60  # 24 часа в секундах

    thread = threading.Thread(target=run_periodically, daemon=True)
    thread.start()

schedule_auto_shop()

@bot.message_handler(commands=['upshop'])
def manual_update(message):
    if message.from_user.id in admins:
        auto_shop()
        bot.reply_to(message, '✅ Акции успешно обновлены!')
    else:
        bot.reply_to(message, "❌ У вас недостаточно прав!")
        
        
def get_skin_ids_by_rarity(rarity=None):
    skin_ids = {
        'common': [29, 15, 2, 109, 27, 139, 111, 137, 152],
        'rare': [25, 28, 92, 158, 88, 93, 104, 132, 125, 117, 11, 126, 131, 20, 110, 135, 159, 75],
        'epic': [79, 44, 163, 91, 160, 99, 30, 128, 71, 26, 68, 147, 96, 118, 98, 254],
        'legendary': [94, 49, 95, 143],
        'gold': [185, 195, 197, 199, 221, 219],
        'silver': [224, 226, 186, 187, 196, 198, 200]
    }
    return skin_ids if rarity is None else skin_ids.get(rarity, [])  

def get_price_range_by_rarity(rarity):
    price_ranges = {
        'common': (29, 29),
        'rare': (79, 79),
        'epic': (149, 149),
        'legendary': (299, 299),
        'gold': (10000, 10000),
        'silver': (2500, 2500)
    }
    return price_ranges.get(rarity, (10, 20))
		
def is_numeric(value):
    return value.isdigit()

def validate_integer(value, non_negative=False):
    try:
        int_value = int(value)
        if non_negative:
            return int_value >= 0
        else:
            return int_value > 0
    except ValueError:
        return False
        
@bot.message_handler(commands=['setgems'])
def set_gems(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ У вас нет прав для использования этой команды.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /setgems [lowID | #хештег] [amount]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount < 0:
            bot.reply_to(message, "❌ Количество гемов должно быть ≥ 0!")
            return

        # Определяем lowID по хештегу или ID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ Неверный формат ID. Должно быть число или #хештег")
            return

        # Проверяем существование игрока
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Обновляем гемы через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET gems = %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Игроку с ID `{lowID}` установлено `{amount}` гемов.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ Количество должно быть числом.")
    except Exception as e:
        logger.error(f"[ERROR] /setgems: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['addgems'])
def add_gems(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ У вас нет прав для использования этой команды.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /addgems [lowID | #хештег] [amount]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount <= 0:
            bot.reply_to(message, "❌ Количество гемов должно быть положительным.")
            return

        # Определяем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ Неверный формат ID. Должно быть число или #хештег")
            return

        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Обновляем гемы
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET gems = gems + %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Игроку с ID `{lowID}` добавлено `{amount}` гемов.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ Количество должно быть числом > 0")
    except Exception as e:
        logger.error(f"[ERROR] /addgems: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['ungems'])
def un_gems(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ У вас нет прав для использования этой команды.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /ungems [lowID | #хештег] [amount]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount <= 0:
            bot.reply_to(message, "❌ Количество гемов должно быть положительным.")
            return

        # Определяем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        current_gems = player_data.get('gems', 0)
        if current_gems < amount:
            bot.send_message(message.chat.id, "❌ Недостаточно гемов у игрока.")
            return

        # Обновляем гемы в БД
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET gems = gems - %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ У игрока с ID `{lowID}` забрано `{amount}` гемов.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом, количество — положительным числом.")
    except Exception as e:
        logger.error(f"[ERROR] /ungems: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=['setgold'])
def set_gold(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /setgold [lowID | #хештег] [amount]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount < 0:
            bot.reply_to(message, "❌ Количество монет должно быть ≥ 0.")
            return

        # Получаем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Обновляем gold через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET gold = %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Игроку с ID `{lowID}` установлено `{amount}` монет.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID и количество должны быть числами.")
    except Exception as e:
        logger.error(f"[ERROR] /setgold: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['addgold'])
def add_gold(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /addgold [lowID | #хештег] [amount]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount <= 0:
            bot.reply_to(message, "❌ Количество должно быть положительным числом.")
            return

        # Получаем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем существование игрока
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Добавляем монеты через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET gold = gold + %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Игроку с ID `{lowID}` добавлено `{amount}` монет.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID и количество должны быть числами.")
    except Exception as e:
        logger.error(f"[ERROR] /addgold: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['ungold'])
def un_gold(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /ungold [lowID | #хештег] [amount]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount <= 0:
            bot.reply_to(message, "❌ Количество должно быть положительным числом.")
            return

        # Получаем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        current_gold = player_data.get('gold', 0)
        if current_gold < amount:
            bot.send_message(message.chat.id, "❌ Недостаточно монет у игрока.")
            return

        # Уменьшаем золото через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET gold = gold - %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ У игрока с ID `{lowID}` забрано `{amount}` монет.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID и количество должны быть числами.")
    except Exception as e:
        logger.error(f"[ERROR] /ungold: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        

@bot.message_handler(commands=['settokens'])
def set_tokens(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /settokens [lowID | #хештег] [количество]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount < 0:
            bot.reply_to(message, "❌ Количество токенов должно быть ≥ 0.")
            return

        # Определяем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Обновляем BPTOKEN через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET BPTOKEN = %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Игроку с ID `{lowID}` установлено `{amount}` токенов.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID и количество должны быть числами.")
    except Exception as e:
        logger.error(f"[ERROR] /settokens: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['addtokens'])
def add_tokens(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /addtokens [lowID | #хештег] [количество]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount <= 0:
            bot.reply_to(message, "❌ Количество должно быть положительным числом.")
            return

        # Получаем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем существование игрока
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Обновляем BPTOKEN через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET BPTOKEN = BPTOKEN + %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Игроку с ID `{lowID}` добавлено `{amount}` токенов.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID и количество должны быть числами.")
    except Exception as e:
        logger.error(f"[ERROR] /addtokens: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['untokens'])
def un_tokens(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs and user_id not in managers:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Используйте: /untokens [lowID | #хештег] [amount]")
            return

        identifier = parts[1].strip()
        amount = int(parts[2])

        if amount <= 0:
            bot.reply_to(message, "❌ Количество должно быть положительным числом.")
            return

        # Получаем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем существование игрока
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        current_tokens = player_data.get('BPTOKEN', 0)
        if current_tokens < amount:
            bot.send_message(message.chat.id, "❌ Недостаточно токенов у игрока.")
            return

        # Уменьшаем токены через MySQL
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET BPTOKEN = BPTOKEN - %s WHERE lowID = %s", (amount, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ У игрока с ID `{lowID}` забрано `{amount}` токенов.", parse_mode="Markdown")
        finally:
            cursor.close()
            conn.close()

    except ValueError:
        bot.reply_to(message, "❌ ID и количество должны быть числами.")
    except Exception as e:
        logger.error(f"[ERROR] /untokens: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=['ban'])
def ban(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Используйте: /ban [lowID | #хештег]")
            return

        identifier = parts[1].strip()

        # Определяем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Обновляем config.json
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if lowID in config["banID"]:
            bot.send_message(message.chat.id, f"❌ Игрок с ID {lowID} уже в списке банов.")
            return

        config["banID"].append(lowID)
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        bot.send_message(message.chat.id, f"✅ Бан выдан игроку с ID `{lowID}`.", parse_mode="Markdown")

    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
    except Exception as e:
        logger.error(f"[ERROR] /ban: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['unban'])
def unban(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Используйте: /unban [lowID | #хештег]")
            return

        identifier = parts[1].strip()

        # Определяем lowID
        lowID = None
        if identifier.startswith("#"):
            lowID = DataBase().get_id_by_hash(identifier)
            if not lowID:
                bot.send_message(message.chat.id, "❌ Игрок с таким хештегом не найден.")
                return
        elif identifier.isdigit():
            lowID = int(identifier)
        else:
            bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
            return

        # Проверяем, существует ли игрок
        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, f"❌ Игрок с ID {lowID} не найден.")
            return

        # Работаем с config.json
        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if lowID not in config["banID"]:
            bot.send_message(message.chat.id, f"❌ Игрок с ID {lowID} не в списке забаненных.")
            return

        config["banID"].remove(lowID)
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        bot.send_message(message.chat.id, f"✅ Разбан выдан игроку с ID `{lowID}`.", parse_mode="Markdown")

    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом или начинаться с `#`")
    except Exception as e:
        logger.error(f"[ERROR] /unban: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['unroom'])
def clear_room(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET roomID = 0")
            conn.commit()
            bot.send_message(message.chat.id, "✅ Все комнаты успешно очищены.")
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logger.error(f"[ERROR] /unroom: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['teh'])
def enable_maintenance(message):
    user_id = message.from_user.id
    if user_id not in admins:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        if update_maintenance_status(True):
            bot.reply_to(message, "✅ Технический перерыв включен.")
        else:
            bot.reply_to(message, "❌ Не удалось включить технический перерыв.")
    except Exception as e:
        logger.error(f"[ERROR] /teh: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['unteh'])
def disable_maintenance(message):
    user_id = message.from_user.id
    if user_id not in admins:
        bot.reply_to(message, "❌ Вы не являетесь администратором!")
        return

    try:
        if update_maintenance_status(False):
            bot.reply_to(message, "✅ Технический перерыв выключен.")
        else:
            bot.reply_to(message, "❌ Не удалось выключить технический перерыв.")
    except Exception as e:
        logger.error(f"[ERROR] /unteh: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
        
@bot.message_handler(commands=['resetclubs'])
def reset_clubs_command(message):
    user_id = message.from_user.id
    if user_id not in admins:
        bot.send_message(message.chat.id, "❌ У вас нет прав для выполнения этой команды.")
        return

    try:
        # Обновляем поля ClubID и ClubRole у всех игроков
        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET ClubID = 0, ClubRole = 0")
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        # Удаляем данные из таблицы clubs и chats
        try:
            conn = DataBase.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM clubs")
                cursor.execute("DELETE FROM chats")
                conn.commit()
        except Exception as e:
            logger.error(f"[ERROR] Ошибка при удалении клубов: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        bot.send_message(message.chat.id, "✅ Данные клубов успешно сброшены.")
    
    except Exception as e:
        logger.error(f"[ERROR] /resetclubs: {e}")
        bot.send_message(message.chat.id, f"❌ Произошла ошибка: {str(e)}")
        
def generate_status_message():
    try:
        # Инициализируем swap_used и swap_total до блока try-except
        swap_used = "NO DATA"
        swap_total = "NO DATA"

        # Получаем количество игроков
        try:
            players = dball()
            player_list = len(players) if isinstance(players, list) else "NO DATA"
        except Exception as e:
            logger.error(f"[ERROR] dball() failed: {e}")
            player_list = "NO DATA"

        # Чтение из config.json
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            ban_list = len(data.get("banID", []))
            vip_list = len(data.get("vips", []))
        except Exception as e:
            logger.warning(f"[WARNING] config.json не загружен: {e}")
            ban_list = "NO DATA"
            vip_list = "NO DATA"

        # RAM
        try:
            ram = psutil.virtual_memory()
            ram_total = f"{ram.total // (1024 ** 2)} МБ"
            ram_used = f"{ram.used // (1024 ** 2)} МБ"
        except Exception as e:
            logger.warning(f"[WARNING] RAM недоступна: {e}")
            ram_total = ram_used = "NO DATA"

        # CPU
        try:
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(percpu=True)
            cpu_load_details = ", ".join([f"ядра {i+1} - {p}%" for i, p in enumerate(cpu_percent)])
            cpu_info = f"{cpu_cores}/{cpu_threads} | {cpu_load_details}"
        except Exception as e:
            logger.warning(f"[WARNING] CPU недоступна: {e}")
            cpu_info = "NO DATA"

        # Диск
        try:
            disk = psutil.disk_usage('/')
            disk_total = f"{disk.total // (1024 ** 3)} ГБ"
            disk_used = f"{disk.used // (1024 ** 3)} ГБ"
        except Exception as e:
            logger.warning(f"[WARNING] Диск недоступен: {e}")
            disk_total = disk_used = "NO DATA"

        # Пинг
        try:
            ping_time = get_ping()
        except:
            ping_time = "NO DATA"

        # Формируем сообщение
        status_text = (
            "```diff\n"
            "📊 Статистика сервера:\n\n"
            f"+ Игроки: {player_list}\n"
            f"+ В бане: {ban_list}\n"
            f"+ VIP: {vip_list}\n\n"
            f"+ RAM: {ram_used} / {ram_total}\n"
            f"+ Swap: {swap_used} / {swap_total}\n"
            f"+ CPU: {cpu_info}\n"
            f"+ Диск: {disk_used} / {disk_total}\n"
            f"+ Пинг: {ping_time} мс\n"
            "```"
        )
        return status_text

    except Exception as e:
        logger.error(f"[ERROR] generate_status_message: {e}")
        return (
            "```diff\n"
            "❌ Ошибка генерации статистики\n"
            "```"
        )
        
def dball():
    conn = DataBase.get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT lowID FROM plrs")
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"[ERROR] dball: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
        
def loadbyID(ID):
        conn = DataBase.get_connection()
        if not conn:
            print("[ERROR] Не удалось подключиться к базе данных.")
            return None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM plrs WHERE lowID = %s", (ID,))
            result = cur.fetchone()
            if not result:
                print(f"[ERROR] Игрок с lowID={ID} не найден в базе данных.")
            return result
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return None
        finally:
            cur.close()
            conn.close()

@bot.message_handler(commands=['status'])
def status(message):
    user_id = message.from_user.id
    if user_id not in admins and user_id not in tehs:
        bot.reply_to(message, "❌ Вы не администратор!")
        return

    try:
        status_text = generate_status_message()
        keyboard = types.InlineKeyboardMarkup()
        refresh_button = types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh_status")
        keyboard.add(refresh_button)

        bot.send_message(
            message.chat.id,
            status_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"[ERROR] /status: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
    
last_status_text = {}

@bot.callback_query_handler(func=lambda call: call.data == "refresh_status")
def refresh_status_callback(call):
    try:
        new_status_text = generate_status_message()
        message_id = call.message.message_id

        if last_status_text.get(message_id) == new_status_text:
            bot.answer_callback_query(call.id, text="🔄 Нет изменений")
            return

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🔄 Обновить", callback_data="refresh_status"))

        bot.edit_message_text(
            new_status_text,
            chat_id=call.message.chat.id,
            message_id=message_id,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

        bot.answer_callback_query(call.id, text="🔄 Обновлено")
        last_status_text[message_id] = new_status_text

    except Exception as e:
        logger.error(f"[ERROR] refresh_status_callback: {e}")
        bot.answer_callback_query(call.id, text="❌ Не удалось обновить")
        
def get_ping(host='89.35.130.34'):
    try:
        response_time = ping3.ping(host, timeout=1)
        if response_time is not None:
            inflated_ping = response_time * 1000
            return f"{inflated_ping:.2f}"
        return "Не удалось измерить"
    except:
        return "NO DATA"
        
@bot.message_handler(commands=['delcode'])
def del_code(message):
    user_id = message.from_user.id
    
    if user_id not in creator2 and user_id not in creator3:
        bot.reply_to(message, "❌ Вы не являетесь контентмейкером!")
        return

    try:
        with sqlite3.connect('users.db') as users_conn:
            users_cursor = users_conn.cursor()
            users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
            row = users_cursor.fetchone()

        if not row:
            bot.reply_to(message, "❌ Вы не привязали аккаунт. Используйте /connect.")
            return

        lowID = row[0]

        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, "❌ Аккаунт не найден в базе данных.")
            return

        code = player_data.get('SCC', None)
        if not code:
            bot.send_message(message.chat.id, "❌ У вас нет кода автора для удаления.")
            return

        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if code in config["CCC"]:
            config["CCC"].remove(code)
            with open("config.json", "w", encoding='utf-8') as f:
                json.dump(config, f, indent=4)

        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET SCC = NULL WHERE lowID = %s", (lowID,))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Код автора `{code}` был удалён!")
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logger.error(f"[ERROR] /delcode: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")
  
@bot.message_handler(commands=['addcode'])
def new_code(message):
    user_id = message.from_user.id
    if user_id not in creator2 and user_id not in creator3:
        bot.reply_to(message, "❌ Вы не являетесь контентмейкером!")
        return

    try:
        with sqlite3.connect('users.db') as users_conn:
            users_cursor = users_conn.cursor()
            users_cursor.execute("SELECT lowID FROM accountconnect WHERE id_user = ?", (user_id,))
            row = users_cursor.fetchone()

        if not row:
            bot.reply_to(message, "❌ Вы не привязали аккаунт. Используйте /connect.")
            return

        lowID = row[0]

        player_data = loadbyID(lowID)
        if not player_data:
            bot.reply_to(message, "❌ Аккаунт не найден в базе данных.")
            return

        current_code = player_data.get('SCC', None)
        if current_code:
            bot.reply_to(message, "❌ У вас уже есть код автора. Удалите его командой /delcode.")
            return

        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Правильное использование: /code [new code] (на английском)")
            return

        new_code = parts[1].upper()

        with open("config.json", "r", encoding='utf-8') as f:
            config = json.load(f)

        if new_code in config["CCC"]:
            bot.send_message(message.chat.id, f"❌ Код `{new_code}` уже существует!")
            return

        config["CCC"].append(new_code)
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        conn = DataBase.get_connection()
        if not conn:
            bot.send_message(message.chat.id, "❌ Не удалось подключиться к базе данных.")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE plrs SET SCC = %s WHERE lowID = %s", (new_code, lowID))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Новый код `{new_code}` добавлен!")
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logger.error(f"[ERROR] /addcode: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            logger.error(f"[CRASH] Бот упал: {e}")
            bot.stop_polling()
            time.sleep(5)
            print("[Инфо] Перезапуск бота...")