import os
import sys
import stat
import json
import time
import requests
import subprocess
import threading
import logging

# Настройка базового логирования для Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================================
# ЗАКРЫВАЕМ ВОПРОС С БОТОМ И MYSQL НА УРОВНЕ СИСТЕМНОГО КЕША PYTHON
# =====================================================================

# 1. Создаем абсолютную пустышку-заглушку для Telegram бота
class AbsoluteBotMock:
    def __init__(self, *args, **kwargs): pass
    def __getattr__(self, name): return lambda *args, **kwargs: None
    def infinity_polling(self, *args, **kwargs):
        print("[СИСТЕМА] Встроенный бот успешно переведен в режим сна."); time.sleep(360000)
    def polling(self, *args, **kwargs):
        print("[СИСТЕМА] Встроенный бот успешно переведен в режим сна."); time.sleep(360000)

# Принудительно заменяем модуль telebot во всей системе Python
import types
mock_telebot = types.ModuleType('telebot')
mock_telebot.TeleBot = AbsoluteBotMock
sys.modules['telebot'] = mock_telebot
print("[УСПЕХ] Жесткая блокировка TeleBot активирована.")

# 2. Создаем абсолютную пустышку-заглушку для Базы Данных MySQL
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

mock_mysql = types.ModuleType('mysql')
mock_mysql_connector = types.ModuleType('mysql.connector')
mock_mysql_connector.connect = lambda *args, **kwargs: MockConnection()
sys.modules['mysql'] = mock_mysql
sys.modules['mysql.connector'] = mock_mysql_connector
print("[УСПЕХ] Жесткая блокировка MySQL БД активирована.")

# Отключаем лишние системные логи
for logger_name in ['TeleBot', 'telebot', 'urllib3', 'mysql']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

# Настройка рабочих папок сервера Brawl Stars
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


# =====================================================================
# АВТОЗАПУСК ТУННЕЛЯ PLAYIT.GG (ПОЛУЧЕНИЕ IP И ПОРТА)
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
# СТАРТ ЧИСТОГО ИГРОВОГО ДВИЖКА BRAWL STARS
# =====================================================================
if __name__ == "__main__":
    print("[ИНФО] Старт сервера в автономном изолированном режиме...")
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
        print("[ИНФО] Лобби Brawl Stars успешно запущено на порту 0.0.0.0:9339!")
        try:
            server = ServerClass("0.0.0.0", 9339)
            server.start()
        except Exception as server_error:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА ИГРОВОГО СЕРВЕРА]: {server_error}")
    else:
        print("[ВНИМАНИЕ] Не удалось загрузить класс Server. Проверьте файлы проекта.")
        time.sleep(60)
