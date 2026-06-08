import os
import sys
import json
import threading
import requests
import logging
import subprocess
import stat

# Настройка логирования для панели Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Полностью пересобираем пути, учитывая структуру папок на хостинге
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Добавляем все папки в пути Python для исправления ошибок импорта
for path in [current_dir, parent_dir]:
    if path not in sys.path:
        sys.path.append(path)
    for root, dirs, files in os.walk(path):
        if "Server" in dirs or "Logic" in dirs or "Utils" in dirs:
            if root not in sys.path:
                sys.path.append(root)

# Безопасный импорт внутренней логики сервера Brawl Stars
try:
    from Logic.Player import Players
    from Utils.Helpers import Helpers
except ImportError:
    class Helpers:
        @staticmethod
        def load_logic(): pass

# Заглушка класса DataBase для совместимости с файлами сборки (файловый режим)
class DataBase:
    @staticmethod
    def get_connection(): return None
    @staticmethod
    def reset_brawlpass_for_all_players(): return
    @staticmethod
    def check_brawlpass_reset(): return False
    @staticmethod
    def createAccount(self): return

def distribute_rewards():
    print("[ИНФО] Фоновый поток наград активен (Файловый режим)...")

# Функция автоматической загрузки и запуска туннеля Playit.gg
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
                    if chunk:
                        f.write(chunk)
            st = os.stat(playit_path)
            os.chmod(playit_path, st.st_mode | stat.S_IEXEC)
            print("[PLAYIT] Агент успешно скачан и настроен!")
        except Exception as e:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА PLAYIT]: Не удалось скачать агент: {e}")
            return

    def run_agent():
        try:
            print("[PLAYIT] Запуск туннеля...")
            process = subprocess.Popen(
                [playit_path, "--secret_path", os.path.join(current_dir, "playit-secret.json")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                line_str = line.strip()
                if "https://playit.gg/claim/" in line_str:
                    print("\n" + "!"*60)
                    print("   === ВНИМАНИЕ! КЛЮЧ ДЛЯ АКТИВАЦИИ ТУННЕЛЯ ===")
                    print(f"   ПЕРЕЙДИ ПО ССЫЛКЕ ЧТОБЫ ЗАПУСТИТЬ СЕРВЕР:")
                    print(f"   {line_str}")
                    print("!"*60 + "\n")
                else:
                    if "tunnel running" in line_str.lower() or "connected" in line_str.lower():
                        print(f"[PLAYIT LOG] {line_str}")
        except Exception as e:
            print(f"[ERROR PLAYIT]: Ошибка во время работы процесса: {e}")

    thread = threading.Thread(target=run_agent, name="PlayitAgent")
    thread.daemon = True
    thread.start()


# =====================================================================
# ТОЧКА ВХОДА И ЗАПУСК СЕРВЕРА БРАВЛ СТАРС
# =====================================================================
if __name__ == "__main__":
    try:
        Helpers.load_logic()
    except Exception:
        pass
        
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"block": [], "buybp": [], "buybpold": [], "BPSEASON": 1, "NEXTSEASON": "01.01.27 00:00"}, f, indent=4)

    print("[ИНФО] Сервер запускается в автономном файловом режиме (JSON)...")

    # Запуск фонового распределения наград
    reward_thread = threading.Thread(target=distribute_rewards, name="distribute_rewards")
    reward_thread.daemon = True
    reward_thread.start()

    # СТАРТ ТУННЕЛЯ PLAYIT
    start_playit_tunnel()
            
    # Запуск основного игрового лобби Brawl Stars с умным поиском модулей
    server_imported = False
    ServerClass = None
    
    # Варианты импорта класса Server (учитывая регистр и вложенность папок хостинга)
    import_variants = [
        "Server.Server",
        "server.Server",
        "server.server",
        "bravl – копія.Server.Server"
    ]
    
    for variant in import_variants:
        try:
            mod = __import__(variant, fromlist=['Server'])
            ServerClass = getattr(mod, 'Server')
            server_imported = True
            print(f"[ИМПОРТ ОК] Успешно импортировано через: {variant}")
            break
        except (ImportError, AttributeError):
            continue

    if server_imported and ServerClass:
        print("[ИНФО] Лобби успешно запущено на порту 0.0.0.0:9339! Ожидаю туннель...")
        try:
            server = ServerClass("0.0.0.0", 9339)
            server.start()
        except Exception as server_error:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА ИГРОВОГО СЕРВЕРА]: {server_error}")
    else:
        print("[ВНИМАНИЕ] Не удалось импортировать класс Server ни одним способом!")
        print(f"Текущая директория выполнения: {os.getcwd()}")
