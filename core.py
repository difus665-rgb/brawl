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

# Полное отключение логов telebot во избежание спама ошибками 409
for bot_logger in ['TeleBot', 'telebot']:
    l = logging.getLogger(bot_logger)
    l.setLevel(logging.CRITICAL)
    l.propagate = False

# Настройка путей
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Регистрируем все возможные папки в путях среды
for path in [current_dir, parent_dir]:
    if path not in sys.path:
        sys.path.append(path)
    for root, dirs, files in os.walk(path):
        if "Server" in dirs or "Logic" in dirs or "Utils" in dirs:
            if root not in sys.path:
                sys.path.append(root)

# Создаем пустой config.json, если его нет
if not os.path.exists('config.json'):
    with open('config.json', 'w') as f:
        json.dump({"block": [], "buybp": [], "buybpold": [], "BPSEASON": 1, "NEXTSEASON": "01.01.27 00:00"}, f, indent=4)


# =====================================================================
# НАСТРОЙКА И АВТОЗАПУСК ТУННЕЛЯ PLAYIT.GG (ПОЛУЧЕНИЕ IP И ПОРТА)
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
                    if chunk:
                        f.write(chunk)
            st = os.stat(playit_path)
            os.chmod(playit_path, st.st_mode | stat.S_IEXEC)
            print("[PLAYIT] Агент успешно скачан!")
        except Exception as e:
            print(f"[ОШИБКА PLAYIT]: Не удалось скачать агент: {e}")
            return

    def run_agent():
        try:
            print("[PLAYIT] Запуск туннеля...")
            # Принудительно направляем stderr в stdout, чтобы поймать ссылку
            process = subprocess.Popen(
                [playit_path, "--secret_path", os.path.join(current_dir, "playit-secret.json")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                line_str = line.strip()
                # Ловим ссылку для генерации IP и Порта
                if "https://playit.gg/claim/" in line_str or "claim" in line_str.lower():
                    print("\n" + "!" * 70)
                    print("   === ВНИМАНИЕ! ССЫЛКА ДЛЯ ПОЛУЧЕНИЯ IP И ПОРТА ===")
                    print(f"   ОТКРОЙ ЕЁ В БРАУЗЕРЕ: {line_str}")
                    print("!" * 70 + "\n")
                else:
                    if "tunnel running" in line_str.lower() or "connected" in line_str.lower():
                        print(f"[PLAYIT] {line_str}")
        except Exception as e:
            print(f"[ОШИБКА PLAYIT]: {e}")

    thread = threading.Thread(target=run_agent, name="PlayitAgent")
    thread.daemon = True
    thread.start()


# =====================================================================
# ТОЧКА ВХОДА И ЗАПУСК ЧИСТОГО ИГРОВОГО ЛОББИ
# =====================================================================
if __name__ == "__main__":
    print("[ИНФО] Старт сервера в чистом автономном режиме...")
    
    # Сначала запускаем туннель
    start_playit_tunnel()
    time.sleep(3)
            
    # Динамический чистый импорт только класса Server
    server_imported = False
    ServerClass = None
    
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
            print(f"[ИМПОРТ ОК] Модуль игры загружен через: {variant}")
            break
        except Exception:
            continue

    if server_imported and ServerClass:
        print("[ИНФО] Лобби Brawl Stars успешно инициализировано на порту 9339!")
        try:
            # Запуск чистого сокет-сервера без старых потоков бота и баз данных
            server = ServerClass("0.0.0.0", 9339)
            server.start()
        except Exception as server_error:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА ИГРОВОГО СЕРВЕРА]: {server_error}")
    else:
        print("[ВНИМАНИЕ] Не удалось запустить класс Server. Проверьте структуру папок.")
        # Предотвращаем мгновенное закрытие контейнера для чтения логов
        time.sleep(120)
