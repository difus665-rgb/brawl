import os
import sys
import stat
import json
import time
import requests
import subprocess
import threading
import logging

# Настройка логирования для Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================================
# 1. ЖЕСТКАЯ ЗАЩИТА ЯДРА (УБИВАЕМ БОТА И MYSQL ДО ЗАГРУЗКИ SERVER.PY)
# =====================================================================

# Полностью перехватываем запуск потоков в Python на самом низком уровне
_original_start = threading.Thread.start
def _secure_start(self):
    t_name = str(self.name).lower()
    # Фильтруем любые потоки, связанные с ботом или наградами базы данных
    if any(x in t_name for x in ["telebot", "polling", "rewards", "bot", "mysql"]):
        print(f"[БЛОКИРОВКА СИСТЕМЫ] Фоновый поток '{self.name}' успешно отключен скриптом core.py.")
        return # Выходим, поток физически не запустится
    return _original_start(self)
threading.Thread.start = _secure_start

# Создаем системную пустышку для mysql.connector, чтобы distribute_rewards() не падала
import types
class _CursorMock:
    def execute(self, *args, **kwargs): return None
    def fetchall(self, *args, **kwargs): return []
    def fetchone(self, *args, **kwargs): return None
    def close(self, *args, **kwargs): return None
class _ConnMock:
    def cursor(self, *args, **kwargs): return _CursorMock()
    def commit(self, *args, **kwargs): pass
    def close(self, *args, **kwargs): pass
    def is_connected(self): return True

_mock_mysql = types.ModuleType('mysql')
_mock_mysql_connector = types.ModuleType('mysql.connector')
_mock_mysql_connector.connect = lambda *args, **kwargs: _ConnMock()
sys.modules['mysql'] = _mock_mysql
sys.modules['mysql.connector'] = _mock_mysql_connector

# Глушим логи самого телебота, чтобы они не засоряли консоль Railway
for log_name in ['TeleBot', 'telebot', 'urllib3']:
    logging.getLogger(log_name).setLevel(logging.CRITICAL)

print("[СИСТЕМА] Защита ядра активна. Конфликты с ботом и MySQL полностью нейтрализованы.")


# =====================================================================
# 2. АВТОЗАПУСК ТУННЕЛЯ PLAYIT.GG (ПОЛУЧЕНИЕ IP И ПОРТА)
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
    _original_start(thread) # Запускаем туннель в обход
