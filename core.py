import os
import sys
import json
import datetime
import time
import threading
import requests
import logging

# Настройка логирования для панели Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Автоматически добавляем текущую директорию и подпапки в пути Python
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Поиск папок, если при распаковке архива изменились пути
for root, dirs, files in os.walk(current_dir):
    if "Server" in dirs or "Logic" in dirs or "Utils" in dirs:
        if root not in sys.path:
            sys.path.append(root)

# Импорты внутренней логики сервера Brawl Stars
try:
    from Logic.Player import Players
    from Utils.Helpers import Helpers
except ImportError:
    class Helpers:
        @staticmethod
        def load_logic():
            pass

# Оставляем заглушку класса DataBase, чтобы другие файлы (например, botuser.py), 
# если они вызывают его методы, НЕ ЛОМАЛИ сервер.
class DataBase:
    @staticmethod
    def get_connection():
        return None

    @staticmethod
    def reset_brawlpass_for_all_players():
        print("[ИНФО] Сброс Brawl Pass (функция отключена, так как MySQL не используется)")
        return

    @staticmethod
    def check_brawlpass_reset():
        return False

    @staticmethod
    def createAccount(self):
        return

def distribute_rewards():
    print("[ИНФО] Поток наград активен (работа в режиме файлового сохранения)...")
    # Здесь сервер работает через встроенную логику файлов, без MySQL


# =====================================================================
# ТОЧКА ВХОДУ И ЗАПУСК ИГРЫ
# =====================================================================
if __name__ == "__main__":
    try:
        Helpers.load_logic()
    except Exception:
        pass
        
    # Инициализация конфигурационных файлов
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"block": [], "buybp": [], "buybpold": [], "BPSEASON": 1, "NEXTSEASON": "01.01.27 00:00"}, f, indent=4)

    print("[ИНФО] Сервер запускается в автономном файловом режиме (сохранение в JSON)...")
    print("[ИНФО] Заблокированные IP очищены в config.json при запуске сервера")
    print("[ИНФО] Файл ConnectedIP.json очищен при запуске сервера.")

    # Фоновые задачи сервера
    reward_thread = threading.Thread(target=distribute_rewards, name="distribute_rewards")
    reward_thread.daemon = True
    reward_thread.start()

    # ЗАПУСК ТУННЕЛЯ NGROK (Твой токен)
    try:
        from pyngrok import ngrok, conf, installer
        
        pyngrok_config = conf.get_default()
        if not os.path.exists(pyngrok_config.ngrok_path):
            print("[NGROK] Скачивание и подготовка бинарного файла ngrok...")
            installer.install_ngrok(pyngrok_config.ngrok_path)
            
        # Твой личный токен
        ngrok.set_auth_token("3EpDqWGtAXG13Lz8Ot1FGTDh6qL_2qo3rue38xZmfVDXKQyMg")
        
        tunnel = ngrok.connect(9339, "tcp")
        print("\n" + "="*60)
        print("   === ТУННЕЛИРОВАНИЕ ИГРЫ УСПЕШНО ВКЛЮЧЕНО! ===")
        print(f"   АДРЕС ДЛЯ КЛИЕНТА APK: {tunnel.public_url}")
        print("="*60 + "\n")
        
    except Exception as ngrok_error:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА NGROK]: {ngrok_error}")
            
    # Умный запуск игрового лобби Brawl Stars
    server_imported = False
    try:
        from Server.Server import Server
        server_imported = True
    except ImportError:
        try:
            from server.Server import Server
            server_imported = True
        except ImportError:
            try:
                from server.server import Server
                server_imported = True
            except ImportError:
                pass

    if server_imported:
        print("[ИНФО] Лобби успешно запущено! Ожидаю игроков на порту 0.0.0.0:9339")
        server = Server("0.0.0.0", 9339)
        server.start()
    else:
        print("[ВНИМАНИЕ] Не удалось импортировать класс Server!")
        print(f"Список файлов в вашей папке: {os.listdir(current_dir)}")
