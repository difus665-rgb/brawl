import os
import sys
import stat
import json
import time
import requests
import subprocess
import threading
import logging

# =====================================================================
# 1. ЖЕСТКОЕ ЗАГЛУШЕНИЕ TELEGRAM-БОТА И БАЗЫ ДАННЫХ RECON (МЫ ИЗБЕГАЕМ КРАШЕЙ)
# =====================================================================

# Заглушка для telebot (Убирает ошибку Conflict 409)
try:
    import telebot
    class TeleBotMock:
        def __init__(self, *args, **kwargs): pass
        def __getattr__(self, name): return lambda *args, **kwargs: None
        def infinity_polling(self, *args, **kwargs):
            print("[ЗАГЛУШКА] Встроенный бот переведен в спящий режим."); time.sleep(36000)
        def polling(self, *args, **kwargs):
            print("[ЗАГЛУШКА] Встроенный бот переведен в спящий режим."); time.sleep(36000)
    telebot.TeleBot = TeleBotMock
    print("[УСПЕХ] Защита от конфликтов Telegram-бота активна.")
except ImportError:
    pass

# Заглушка для mysql.connector (Убирает ошибку Unknown MySQL server host)
try:
    import mysql.connector
    class MockCursor:
        def execute(self, *args, **kwargs): return None
        def fetchall(self, *args, **kwargs): return []
        def fetchone(self, *args, **kwargs): return None
        def close(self, *args, **kwargs): return None
    class MockConnection:
        def cursor(self, *args, **kwargs): return MockCursor()
        def commit(self, *args, **kwargs): pass
        def close(self, *args, **kwargs): pass
        def is_connected(self): return True
    
    # Подменяем метод коннекта, чтобы он возвращал фейковое рабочее соединение
    mysql.connector.connect = lambda *args, **kwargs: MockConnection()
    print("[УСПЕХ] База данных MySQL переведена в изолированный автономный режим.")
except ImportError:
    pass

# Отключаем спам-логи
logging.basicConfig(level=logging.INFO)
for logger_name in ['TeleBot', 'telebot', 'urllib3', 'mysql']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

# Настройка путей
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

for path in [current_dir, parent_dir]:
    if path not in sys.path: sys.path.append(path)
    for root, dirs, files in os.walk(path):
        if "Server" in dirs or "Logic" in dirs or "Utils" in dirs:
            if root not in sys.path: sys.path.append(root)

if not os.path.exists('config.json'):
    with open('config.json', 'w') as f:
        json.dump({"block": [], "buybp": [], "buybpold": [], "BPSEASON": 1, "NEXTSEASON": "01.01.27 00:00"}, f, indent=4)

# Глобальный класс заглушки для внутренних файлов (на всякий случай)
class DataBase:
    @staticmethod
    def get_connection(): return None
    @staticmethod
    def reset_brawlpass_for_all_players(): return
    @staticmethod
    def check_brawlpass_reset(): return False
    @staticmethod
    def createAccount(self): return


# =====================================================================
# 2. ЗАПУСК ТУННЕЛЯ PLAYIT.GG (ВЫВОД ССЫЛКИ ДЛЯ IP И ПОРТА)
# =====================================================================
def start_playit_tunnel():
    print("[PLAYIT] Подготовка агента Playit.gg...")
    playit_path = os.path.join(current_dir, "playit")
    
    if not os.path.exists(playit_path):
        try:
            url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"
            print(f"[PLAYIT] Скачивание агента из {url}...")
            r = requests.get(url, stream=True)
            with open(playit_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            st = os.stat(playit_path)
            os.chmod(playit_path, st.st_mode | stat.S_IEXEC)
            print("[PLAYIT] Агент успешно скачан!")
        except Exception as e:
            print(f"[ОШИБКА PLAYIT]: {e}")
            return

    def run_agent():
        try:
            print("[PLAYIT] Запуск туннеля...")
            process = subprocess.Popen(
                [playit_path, "--secret_path", os.path.join(current_dir, "playit-secret.json")],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            
            for line in process.stdout:
                line_str = line.strip()
                if "https://playit.gg/claim/" in line_str or "claim" in line_str.lower():
                    print("\n" + "!" * 70)
                    print("   === ВНИМАНИЕ! ССЫЛКА ДЛЯ ПОЛУЧЕНИЯ IP И ПОРТА ===")
                    print(f"   ОТКРОЙ ЕЁ В БРАУЗЕРЕ: {line_str}")
                    print("!" * 70 + "\n")
                else:
                    if "tunnel running" in line_str.lower() or "connected" in line_str.lower():
                        print(f"[PLAYIT LOG] {line_str}")
        except Exception as e:
            print(f"[ОШИБКА PLAYIT]: {e}")

    thread = threading.Thread(target=run_agent, name="PlayitAgent")
    thread.daemon = True
    thread.start()


# =====================================================================
# 3. ТОЧКА ВХОДА И ЗАПУСК СЕРВЕРА БРАВЛ СТАРС
# =====================================================================
if __name__ == "__main__":
    print("[ИНФО] Старт сервера в автономном файловом режиме...")
    start_playit_tunnel()
    time.sleep(3)
            
    server_imported = False
    ServerClass = None
    
    import_variants = [
        "Server.Server", "server.Server", "server.server", "bravl – копія.Server.Server"
    ]
    
    for variant in import_variants:
        try:
            mod = __import__(variant, fromlist=['Server'])
            ServerClass = getattr(mod, 'Server')
            server_imported = True
            print(f"[ИМПОРТ ОК] Модуль игры успешно загружен через: {variant}")
            break
        except Exception:
            continue

    if server_imported and ServerClass:
        print("[ИНФО] Лобби Brawl Stars успешно запущено на порту 0.0.0.0:9339! Ожидаю подключение туннеля...")
        try:
            server = ServerClass("0.0.0.0", 9339)
            server.start()
        except Exception as server_error:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА ИГРОВОГО СЕРВЕРА]: {server_error}")
    else:
        print("[ВНИМАНИЕ] Не удалось загрузить класс Server. Проверьте файлы проекта.")
        time.sleep(60)
