import os
import sys
import stat
import time
import requests
import subprocess
import threading

# --- НАСТРОЙКИ ---
# Укажи точное имя файла твоего сервера Brawl Stars (например: 'server.exe', './server', 'main.py' и т.д.)
SERVER_EXECUTABLE = "server.exe" 
# ------------------

current_dir = os.path.dirname(os.path.abspath(__file__))

def start_playit_tunnel():
    """Скачивает и запускает туннель Playit.gg, выводя ссылку активации в логи."""
    print("[PLAYIT] Подготовка агента Playit.gg...")
    playit_path = os.path.join(current_dir, "playit")
    
    # 1. Автоматическое скачивание, если файла нет
    if not os.path.exists(playit_path):
        try:
            url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"
            print(f"[PLAYIT] Скачивание агента из {url}...")
            r = requests.get(url, stream=True)
            with open(playit_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Даем права на выполнение (актуально для Linux/Railway)
            st = os.stat(playit_path)
            os.chmod(playit_path, st.st_mode | stat.S_IEXEC)
            print("[PLAYIT] Агент успешно скачан и настроен!")
        except Exception as e:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА PLAYIT]: Не удалось скачать агент: {e}")
            return

    # 2. Функция для чтения логов туннеля в реальном времени
    def run_agent():
        try:
            print("[PLAYIT] Запуск туннеля...")
            # Важно: перенаправляем stderr в stdout, чтобы поймать ссылку
            process = subprocess.Popen(
                [playit_path, "--secret_path", os.path.join(current_dir, "playit-secret.json")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                line_str = line.strip()
                # Красиво выделяем ссылку на привязку аккаунта в логах Railway
                if "https://playit.gg/claim/" in line_str or "claim" in line_str.lower():
                    print("\n" + "!" * 60)
                    print("   === ССЫЛКА ДЛЯ ПОЛУЧЕНИЯ IP И ПОРТА ===")
                    print(f"   {line_str}")
                    print("!" * 60 + "\n")
                else:
                    print(f"[PLAYIT LOG] {line_str}")
        except Exception as e:
            print(f"[ERROR PLAYIT]: Ошибка во время работы процесса: {e}")

    # Запускаем туннель в отдельном потоке, чтобы он не блокировал запуск сервера
    thread = threading.Thread(target=run_agent, name="PlayitAgent")
    thread.daemon = True
    thread.start()


def start_brawl_server():
    """Запускает основной сервер Brawl Stars."""
    print(f"[SERVER] Запуск сервера Brawl Stars ({SERVER_EXECUTABLE})...")
    server_path = os.path.join(current_dir, SERVER_EXECUTABLE)
    
    if not os.path.exists(server_path):
        print(f"[КРИТИЧЕСКАЯ ОШИБКА]: Файл сервера '{SERVER_EXECUTABLE}' не найден в папке!")
        return False

    try:
        # Если это .exe файл на Linux (Railway), запускаем через Wine, иначе напрямую
        if SERVER_EXECUTABLE.endswith(".exe"):
            # Проверяем, есть ли wine, если нет — пробуем напрямую (на случай если это Windows)
            cmd = ["wine", server_path] if os.name != "nt" else [server_path]
        else:
            # Для скриптов или бинарников Linux
            cmd = ["python", server_path] if SERVER_EXECUTABLE.endswith(".py") else [server_path]

        # Запуск сервера
        server_process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
        return server_process
    except Exception as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА СЕРВЕРА]: {e}")
        return False


if __name__ == "__main__":
    print("=== ИНИЦИАЛИЗАЦИЯ СБОРКИ ===")
    
    # Запускаем туннель Playit
    start_playit_tunnel()
    
    # Небольшая пауза, чтобы логи не перемешивались
    time.sleep(2) 
    
    # Запускаем сервер Brawl Stars
    server_proc = start_brawl_server()
    
    if server_proc:
        # Удерживаем скрипт активным, пока работает основной сервер
        try:
            server_proc.wait()
        except KeyboardInterrupt:
            print("[ЗАВЕРШЕНИЕ] Остановка сервера пользователем...")
            server_proc.terminate()
    else:
        # Если сервер упал или не запустился, не даем контейнеру мгновенно закрыться, чтобы ты успел прочитать логи
        print("[ВНИМАНИЕ] Сервер не смог запуститься. Ожидание 60 секунд перед закрытием...")
        time.sleep(60)
