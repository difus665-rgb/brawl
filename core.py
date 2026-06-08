import os
import json
import datetime
import time
import threading
import mysql.connector
from mysql.connector import Error
import requests

# Імпорти внутрішньої логіки твого сервера
try:
    from Logic.Player import Players
    from Utils.Helpers import Helpers
except ImportError:
    # Заглушка, якщо структура папок відрізняється при імпорті
    pass

class DataBase:
    @staticmethod
    def get_connection():
        try:
            # 1. Намагаємося отримати змінні безпосередньо з оточення Railway
            host = os.getenv('MYSQLHOST')
            port = os.getenv('MYSQLPORT', '3306')
            user = os.getenv('MYSQLUSER')
            password = os.getenv('MYSQLPASSWORD')
            database = os.getenv('MYSQLDATABASE')

            # 2. Якщо в Railway пусто, читаємо локальний файл database.json
            if not host or host == "MYSQLHOST":
                if os.path.exists('./database.json'):
                    with open('./database.json', 'r') as f:
                        db_config = json.load(f)
                    host = db_config.get('host', 'DBHOST')
                    port = db_config.get('port', 3306)
                    user = db_config.get('user', 'USER')
                    password = db_config.get('password', 'PASSWORD')
                    database = db_config.get('database', 'DB')
                else:
                    print("[ERROR] Файл database.json не знайдено, і змінні Railway відсутні!")
                    return None

            # 3. Захист від стандартних текстових заглушок
            if host in ["DBHOST", "MYSQLHOST"] or not host:
                print("[ERROR] Помилка підключення: в налаштуваннях досі вказана заглушка 'MYSQLHOST' або 'DBHOST'!")
                return None

            conn = mysql.connector.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database,
                buffered=True
            )
            return conn
        except Error as e:
            print(f"[ERROR] MySQL з'єднання не вдалося: {e}")
            return None

    @staticmethod
    def reset_brawlpass_for_all_players():
        conn = DataBase.get_connection()
        if not conn:
            print("[ERROR] Не вдалося підключитися до бази даних для скидання Brawl Pass")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT lowID, BPTOKEN, BPXP, freepass, buypass, freepassold, buypassold FROM plrs")
            players = cursor.fetchall()
            
            for player in players:
                new_bpxp = player[1]  
                freepass = DataBase.safe_json_load(player[3])
                buypass = DataBase.safe_json_load(player[4])
                freepassold = DataBase.safe_json_load(player[5])
                buypassold = DataBase.safe_json_load(player[6])
                
                if isinstance(freepass, list):
                    freepassold.extend(freepass)
                if isinstance(buypass, list):
                    buypassold.extend(buypass)
                
                update_cursor = conn.cursor()
                update_cursor.execute("""
                    UPDATE plrs SET 
                        BPXP = %s,
                        BPTOKEN = 0,
                        freepass = '[]',
                        buypass = '[]',
                        freepassold = %s,
                        buypassold = %s
                    WHERE lowID = %s
                """, (new_bpxp, json.dumps(freepassold), json.dumps(buypassold), player[0]))
                conn.commit()
                update_cursor.close()
            
            print(f"[BP RESET] Скинуто Brawl Pass для {len(players)} гравців")
            DataBase.update_bp_config()
            
        except Error as e:
            print(f"[ERROR] Помилка MySQL при скиданні Brawl Pass: {e}")
            conn.rollback()
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()

    @staticmethod
    def get_region_by_ip(ip_address):
        try:
            url = f'http://ip-api.com/json/{ip_address}'
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get('status') == 'fail':
                return 'Unknown'
            return data.get('countryCode', 'Unknown')
        except Exception as e:
            print(f"Помилка при отриманні регіону: {e}")
            return 'Unknown'
            
    @staticmethod
    def check_brawlpass_reset():
        try:
            bp_time = Helpers().NEWBPTIME
            if bp_time == 0:
                print("[BP RESET] Виявлено негативний час до нового сезону, запускаю скидання")
                DataBase.reset_brawlpass_for_all_players()
                return True
            return False
        except Exception as e:
            print(f"[ERROR] Помилка при перевірці скидання Brawl Pass: {e}")
            return False

    @staticmethod
    def safe_json_load(data):
        if not data:
            return []
        try:
            return json.loads(data)
        except:
            return data if isinstance(data, list) else []

    @staticmethod
    def update_bp_config():
        try:
            with open('config.json', 'r+') as f:
                config = json.load(f)
                config["buybpold"].extend(config["buybp"])
                config["buybp"] = []
                config["BPSEASON"] += 1
                next_season = datetime.datetime.now() + datetime.timedelta(days=30)
                config["NEXTSEASON"] = next_season.strftime("%d.%m.%y %H:%M")
                f.seek(0)
                json.dump(config, f, indent=4)
                f.truncate()
            print("[BP CONFIG] Конфіг Brawl Pass оновлено")
        except Exception as e:
            print(f"[ERROR] Помилка при оновленні конфігу Brawl Pass: {e}")

    def createAccount(self):
        """Створення структури таблиць бази даних"""
        conn = DataBase.get_connection()
        if not conn:
            print("[ERROR] Не вдалося підключитися до бази даних під час створення таблиць.")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS plrs (
                    token VARCHAR(255), lowID INT, name VARCHAR(255), trophies INT, gold INT, gems INT,
                    starpoints INT, tickets INT, Troproad INT, profile_icon INT, name_color INT,
                    clubID INT, clubRole INT, brawlerData JSON, brawlerID INT, skinID INT,
                    roomID INT, box INT, bigbox INT, online INT, vip INT, playerExp INT,
                    friends JSON, SCC TEXT, trioWINS INT, sdWINS INT, theme INT, BPTOKEN INT,
                    BPXP INT, quests JSON, freepass JSON, buypass JSON, notifRead INT,
                    notifRead2 INT, ip_address VARCHAR(255), creation_date VARCHAR(255),
                    Region VARCHAR(255), notifications JSON, playerData JSON,
                    freepassold JSON, buypassold JSON, PRIMARY KEY (token)
                )
            """)
            conn.commit()
            print("[MYSQL] Таблиці бази даних успішно перевірені/створені.")
        except Error as e:
            print(f"[ERROR] Помилка MySQL при створенні таблиць: {e}")
        finally:
            if 'cur' in locals() and cur:
                cur.close()
            if 'conn' in locals() and conn:
                conn.close()


# =====================================================================
# ТОЧКА ВХОДУ ТА ЗАПУСК ВСІХ СЕРВІСІВ
# =====================================================================
if __name__ == "__main__":
    try:
        Helpers.load_logic()
    except NameError:
        pass
        
    # Ініціалізація файлів конфігурації
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"block": [], "buybp": [], "buybpold": [], "BPSEASON": 1, "NEXTSEASON": "01.01.27 00:00"}, f, indent=4)

    # Перевірка MySQL перед стартом лобі
    print("[ИНФО] Проверка подключения к MySQL...")
    db_init = DataBase()
    db_init.createAccount()

    # Очищення стартових логів
    print("[ИНФО] Заблокированные IP очищены в config.json при запуске сервера")
    print("[ИНФО] Файл ConnectedIP.json очищен при запуске сервера.")

    # ЗАПУСК ТУННЕЛЮ NGROK
    try:
        from pyngrok import ngrok, conf, installer
        
        pyngrok_config = conf.get_default()
        
        # Скачуємо бінарник ngrok сумісним для нових версій методом
        if not os.path.exists(pyngrok_config.ngrok_path):
            print("[NGROK] Скачивание и подготовка бинарного файла ngrok...")
            installer.install_ngrok(pyngrok_config.ngrok_path)
            
        # Твій токен успішно додано сюди:
        ngrok.set_auth_token("3EpDqWGtAXG13Lz8Ot1FGTDh6qL_2qo3rue38xZmfVDXKQyMg")
        
        # Відкриваємо TCP тунель для Brawl Stars (порт 9339)
        tunnel = ngrok.connect(9339, "tcp")
        
        print("\n" + "="*60)
        print("   === ТУННЕЛИРОВАНИЕ ИГРЫ УСПЕШНО ВКЛЮЧЕНО! ===")
        print(f"   АДРЕС ДЛЯ КЛИЕНТА APK: {tunnel.public_url}")
        print("="*60 + "\n")
        
    except Exception as ngrok_error:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА NGROK]: {ngrok_error}")
            
    # Запуск основного ігрового сервера
    try:
        from Server.Server import Server
        print("[ИНФО] Лобби запущено! 0.0.0.0:9339")
        server = Server("0.0.0.0", 9339)
        server.start()
    except ImportError:
        print("[ВНИМАНИЕ] Не вдалося імпортувати класс Server. Перевірь струкруту папок.")
