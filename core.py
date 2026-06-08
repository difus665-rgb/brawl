import os
import json
import datetime
import time
import threading
import mysql.connector
from mysql.connector import Error
import requests

# Импорты внутренней логики твоего сервера
# (Убедись, что пути к папкам Logic и Utils верны относительно этого файла)
try:
    from Logic.Player import Players
    from Utils.Helpers import Helpers
except ImportError:
    # Если запуск происходит из папки Logic, заглушаем ошибку путей
    pass

class DataBase:
    @staticmethod
    def get_connection():
        try:
            # 1. Пытаемся получить данные напрямую из переменных окружения Railway
            host = os.getenv('MYSQLHOST')
            port = os.getenv('MYSQLPORT', '3306')
            user = os.getenv('MYSQLUSER')
            password = os.getenv('MYSQLPASSWORD')
            database = os.getenv('MYSQLDATABASE')

            # 2. Если в Railway пусто (или запуск локальный), читаем файл database.json
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
                    print("[ERROR] Файл database.json не найден, и переменные Railway отсутствуют!")
                    return None

            # 3. Защита от стандартных текстовых заглушек
            if host in ["DBHOST", "MYSQLHOST"] or not host:
                print("[ERROR] Ошибка подключения: в настройках до сих пор указана заглушка 'MYSQLHOST' или 'DBHOST'!")
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
            print(f"[ERROR] MySQL connection failed: {e}")
            return None

    @staticmethod
    def reset_brawlpass_for_all_players():
        conn = DataBase.get_connection()
        if not conn:
            print("[ERROR] Не удалось подключиться к базе данных для сброса Brawl Pass")
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
            
            print(f"[BP RESET] Сброшен Brawl Pass для {len(players)} игроков")
            DataBase.update_bp_config()
            
        except Error as e:
            print(f"[ERROR] Ошибка MySQL при сбросе Brawl Pass: {e}")
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
            print(f"Ошибка при получении региона: {e}")
            return 'Unknown'
            
    @staticmethod
    def check_brawlpass_reset():
        try:
            bp_time = Helpers().NEWBPTIME
            if bp_time == 0:
                print("[BP RESET] Обнаружено отрицательное время до нового сезона, инициирую сброс")
                DataBase.reset_brawlpass_for_all_players()
                return True
            return False
        except Exception as e:
            print(f"[ERROR] Ошибка при проверке сброса Brawl Pass: {e}")
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
            print("[BP CONFIG] Конфиг Brawl Pass обновлен")
        except Exception as e:
            print(f"[ERROR] Ошибка при обновлении конфига Brawl Pass: {e}")

    def createAccount(self):
        """Создание базовой структуры базы данных"""
        conn = DataBase.get_connection()
        if not conn:
            print("[ERROR] Не удалось подключиться к базе данных во время создания таблиц.")
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
            print("[MYSQL] Таблицы базы данных успешно проверены/созданы.")
        except Error as e:
            print(f"[ERROR] Ошибка MySQL при создании таблиц: {e}")
        finally:
            if 'cur' in locals() and cur:
                cur.close()
            if 'conn' in locals() and conn:
                conn.close()


# =====================================================================
# ТОЧКА ВХОДА И ЗАПУСК ВСЕХ СЕРВИСОВ
# =====================================================================
if __name__ == "__main__":
    try:
        Helpers.load_logic()
    except NameError:
        pass
        
    # Инициализация базовых файлов конфигурации
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"block": [], "buybp": [], "buybpold": [], "BPSEASON": 1, "NEXTSEASON": "01.01.27 00:00"}, f, indent=4)

    # Проверяем и создаем таблицы в MySQL
    print("[ИНФО] Проверка подключения к MySQL...")
    db_init = DataBase()
    db_init.createAccount()

    # Сброс логов при старте сервера
    print("[ИНФО] Заблокированные IP очищены в config.json при запуске сервера")
    print("[ИНФО] Файл ConnectedIP.json очищен при запуске сервера.")

    # ЗАПУСК ИСПРАВЛЕННОГО ТУННЕЛЯ NGROK
    try:
        from pyngrok import ngrok, conf, installer
        
        pyngrok_config = conf.get_default()
        
        # Скачиваем бинарный файл правильным для современных версий pyngrok методом
        if not os.path.exists(pyngrok_config.ngrok_path):
            print("[NGROK] Скачивание и подготовка бинарного файла ngrok...")
            installer.install_ngrok(pyngrok_config.ngrok_path)
            
        # !!! ВСТАВЬ СВОЙ АУТЕНТИФИКАЦИОННЫЙ ТОКЕН NGROK В СТРОКУ НИЖЕ !!!
        ngrok.set_auth_token("ТВОЙ_РЕАЛЬНЫЙ_ТОКЕН_NGROK")
        
        # Открываем чистый TCP туннель для трафика Brawl Stars (порт 9339)
        tunnel = ngrok.connect(9339, "tcp")
        
        print("\n" + "="*60)
        print("   === ТУННЕЛИРОВАНИЕ ИГРЫ УСПЕШНО ВКЛЮЧЕНО! ===")
        print(f"   АДРЕС ДЛЯ КЛИЕНТА APK: {tunnel.public_url}")
        print("="*60 + "\n")
        
    except Exception as ngrok_error:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА NGROK]: {ngrok_error}")
            
    # Запуск основного сервера
    try:
        from Server.Server import Server
        print("[ИНФО] Лобби запущено! 0.0.0.0:9339")
        server = Server("0.0.0.0", 9339)
        server.start()
    except ImportError:
        print("[ВНИМАНИЕ] Не удалось импортировать класс Server. Убедись, что папка Server лежит в корне проекта.")
