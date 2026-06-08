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

# =====================================================================
# АБСОЛЮТНЫЙ БЛОКАТОР: КОРРЕКТНОЕ ГЛУШЕНИЕ TELEBOT И MYSQL (С МЕТОДОМ CLOSE)
# =====================================================================

class DeepMock(ModuleType):
    """Фейк-объект, имитирующий модули, функции и любые вложенные свойства"""
    def __init__(self, name):
        super().__init__(name)
    def __getattr__(self, item):
        # 1. Если просят бота
        if item in ('TeleBot', 'Bot'):
            class DummyBot:
                def __init__(self, *args, **kwargs): pass
                def __getattr__(self, name): return lambda *args, **kwargs: None
                def infinity_polling(self, *args, **kwargs): time.sleep(36000)
                def polling(self, *args, **kwargs): time.sleep(36000)
            return DummyBot
        
        # 2. Если вызывают mysql.connector.connect()
        if item == 'connect':
            class DummyCursor:
                def execute(self, *args, **kwargs): return None
                def fetchall(self, *args, **kwargs): return []
                def fetchone(self, *args, **kwargs): return None
                def close(self, *args, **kwargs): return None
            class DummyConn:
                def cursor(self, *args, **kwargs): return DummyCursor()
                def commit(self, *args, **kwargs): pass
                def close(self, *args, **kwargs): return None  # ЗАЩИТА ОТ КРАША НА СТРОКЕ 550!
                def is_connected(self): return True
            return lambda *args, **kwargs: DummyConn()
            
        return DeepMock(f"{self.__name__}.{item}")
    def __call__(self, *args, **kwargs):
        # Специальный фикс: если сам коннект вызывают напрямую как функцию, 
        # возвращаем объект, у которого ЕСТЬ метод close(), чтобы botuser.py не падал
        class FallbackConn:
            def cursor(self, *args, **kwargs):
                class FallbackCursor:
                    def execute(self, *args, **kwargs): return None
                    def fetchall(self, *args, **kwargs): return []
                    def fetchone(self, *args, **kwargs): return None
                    def close(self, *args, **kwargs): return None
                return FallbackCursor()
            def commit(self, *args, **kwargs): pass
            def close(self, *args, **kwargs): return None
            def is_connected(self): return True
        return FallbackConn()

# Заменяем все возможные вариации библиотек в оперативной памяти Python
sys.modules['telebot'] = DeepMock('telebot')
sys.modules['telebot.util'] = DeepMock('telebot.util')
sys.modules['telebot.apihelper'] = DeepMock('telebot.apihelper')
sys.modules['mysql'] = DeepMock('mysql')
sys.modules['mysql.connector'] = DeepMock('mysql.connector')

for log_name in ['TeleBot', 'telebot', 'urllib3', 'mysql']:
    logging.getLogger(log_name).setLevel(logging.CRITICAL)

print("[СИСТЕМА] Защита ядра активна. Конфликты с ботом и MySQL полностью нейтрализованы.")

# =====================================================================
# АВТОЗАПУСК ТУННЕЛЯ PLAYIT.GG (ПОЛУЧЕНИЕ IP И ПОРТА)
# =====================================================================
def start_playit_tunnel():
    print("[PLAYIT] Подготовка агента Playit.gg...")
    playit_path = os.path.join(os.getcwd(), "playit")
    
    if not os.path.exists(playit_path):
        try:
            url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"
            print(f"[PLAYIT] Скачивание агента...")
            r = requests.get(url, stream=True)
            with open(playit_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            os.chmod(playit_path, os.stat(playit_path).st_mode | 0o111)
            print("[PLAYIT] Агент готов!")
        except Exception as e:
            print(f"[ОШИБКА PLAYIT]: {e}")
            return

    def run_agent():
        try:
            print("[PLAYIT] Запуск туннеля...")
            process = subprocess.Popen(
                [playit_path, "--secret_path", os.path.join(os.getcwd(), "playit-secret.json")],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            
            for line in process.stdout:
                line_str = line.strip()
                if "https://playit.gg/claim/" in line_str or "claim" in line_str.lower():
                    print("\n" + "!" * 70)
                    print("   === ТВОЯ ССЫЛКА ДЛЯ ПОЛУЧЕНИЯ IP И ПОРТА ===")
                    print(f"   ЖМИ СЮДА: {line_str}")
                    print("!" * 70 + "\n")
                else:
                    if "tunnel running" in line_str.lower() or "connected" in line_str.lower():
                        print(f"[PLAYIT LOG] {line_str}")
        except Exception as e:
            print(f"[ОШИБКА PLAYIT]: {e}")

    thread = threading.Thread(target=run_agent, name="PlayitTunnel")
    thread.daemon = True
    thread.start()


# =====================================================================
# ЧИСТЫЙ ИМПОРТ И ЗАПУСК ТВОЕЙ ИГРЫ
# =====================================================================
if __name__ == "__main__":
    start_playit_tunnel()
    time.sleep(2)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    print("[ИНФО] Загрузка твоего оригинального Server.py...")
    try:
        import Server as OriginalServerModule
        
        print("[ИНФО] Запуск лобби Brawl Stars на порту 9339...")
        srv = OriginalServerModule.Server("0.0.0.0", 9339)
        srv.start()
        
    except Exception as err:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА ИГРЫ]: {err}")
        time.sleep(60)
