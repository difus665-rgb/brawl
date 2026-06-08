import os
import sys
import stat
import json
import time
import requests
import subprocess
import threading
import logging
from types import ModuleType

# Настройка логирования для Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================================
# СВЕРХМОЩНЫЙ ИНЖЕКТОР: ПОЛНОЕ УНИЧТОЖЕНИЕ ТЕЛЕГРАМ-БОТА И MYSQL ИЗ СИСТЕМЫ
# =====================================================================

class DeepMock(ModuleType):
    """Класс-заглушка, который притворяется любым модулем, подмодулем или функцией."""
    def __init__(self, name):
        super().__init__(name)
    def __getattr__(self, item):
        # Если запрашивают класс бота (TeleBot), отдаем класс-пустышку
        if item in ('TeleBot', 'Bot'):
            class DummyBot:
                def __init__(self, *args, **kwargs): pass
                def __getattr__(self, name): return lambda *args, **kwargs: None
                def infinity_polling(self, *args, **kwargs):
                    print("[СИСТЕМА] Поток встроенного Telegram-бота заглушен."); time.sleep(360000)
                def polling(self, *args, **kwargs):
                    print("[СИСТЕМА] Поток встроенного Telegram-бота заглушен."); time.sleep(360000)
            return DummyBot
        # Если запрашивают коннект к MySQL
        if item == 'connect':
            class DummyCursor:
                def execute(self, *args, **kwargs): return None
                def fetchall(self, *args, **kwargs): return []
                def fetchone(self, *args, **kwargs): return None
                def close(self, *args, **kwargs): return None
            class DummyConn:
                def cursor(self, *args, **kwargs): return DummyCursor()
                def commit(self, *args, **kwargs): pass
                def close(self, *args, **kwargs): pass
                def is_connected(self): return True
            return lambda *args, **kwargs: DummyConn()
        
        # Для любых других подмодулей возвращаем такой же бесконечный Mock
        return DeepMock(f"{self.__name__}.{item}")
    def __call__(self, *args, **kwargs):
        return DeepMock("dummy_callable")

class AbsoluteImportBlocker:
    """Перехватчик системы импорта Python (sys.meta_path)"""
    def find_spec(self, fullname, path, target=None):
        # Намертво перехватываем telebot, mysql и все их внутренности (например, telebot.util, mysql.connector)
        if fullname.startswith("telebot") or fullname.startswith("mysql"):
            from importlib.machinery import ModuleSpec
            print(f"[ПЕРЕХВАТ ИМПОРТА] Модуль {fullname} успешно изолирован.")
            return ModuleSpec(fullname, None, origin="mock_system")
        return None
    def create_module(self, spec):
        return DeepMock(spec.name)
    def exec_module(self, module):
        pass

# Встраиваем перехватчик на первое место в систему Python
sys.meta_path.insert(0, AbsoluteImportBlocker())

# Дополнительно чистим логи, чтобы они не спамили
for log_name in ['TeleBot', 'telebot', 'urllib3', 'mysql']:
    logging.getLogger(log_name).setLevel(logging.CRITICAL)

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
# АВТОЗАПУСК ТУННЕЛЯ PLAYIT.GG (ВЫВОД ССЫЛКИ ДЛЯ IP И ПОРТА)
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
            os.chmod(playit_path, stat.S_IEXEC | st.st_mode)
            print("[PLAYIT] Агент успешно скачан!")
        except Exception as e:
            print(f"[ОШИБКА PLAYIT]: Не удалось скачать агент: {e}")
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
