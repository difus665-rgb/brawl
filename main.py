import os
import sys
import time
import stat
import requests
import subprocess
import threading
from multiprocessing import Process

def start_playit_tunnel():
    """Фоновый запуск туннеля Playit.gg с жесткой проверкой путей"""
    print("[PLAYIT] Подготовка агента Playit.gg...")
    playit_path = os.path.abspath(os.path.join(os.getcwd(), "playit"))
    
    if not os.path.exists(playit_path):
        try:
            url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"
            print(f"[PLAYIT] Скачивание агента в: {playit_path}")
            r = requests.get(url, stream=True)
            r.raise_for_status()
            
            with open(playit_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            
            try: os.sync()
            except: pass
            
            # Выдаем права на выполнение в Linux-контейнере Railway
            os.chmod(playit_path, os.stat(playit_path).st_mode | stat.S_IEXEC | 0o111)
            print("[PLAYIT] Агент успешно скачан и настроен!")
        except Exception as e:
            print(f"[ОШИБКА PLAYIT ПРИ СКАЧИВАНИИ]: {e}")
            return

    def run_agent():
        try:
            if not os.path.exists(playit_path):
                print("[КРИТИЧЕСКАЯ ОШИБКА PLAYIT]: Файл исчез перед запуском!")
                return
                
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
            print(f"[КРИТИЧЕСКАЯ ОШИБКА ТУННЕЛЯ]: {e}")

    thread = threading.Thread(target=run_agent, name="PlayitTunnel")
    thread.daemon = True
    thread.start()


def run_script(script_name):
    try:
        subprocess.run(['python3', script_name])
    except Exception as e:
        print(f"Ошибка при запуске {script_name}: {e}")


if __name__ == "__main__":
    print("[СИСТЕМА] Инициализация безопасного автономного режима...")
    
    # 1. Сначала запускаем туннель Playit
    start_playit_tunnel()
    time.sleep(3)
    
    # 2. Запускаем ИСКЛЮЧИТЕЛЬНО игровой сервер core.py
    # Файлы anticheat.py и botuser.py убраны из списка, чтобы заблокировать краш 409 и ошибки MySQL!
    files = ['core.py']
    
    processes = []
    for file in files:
        process = Process(target=run_script, args=(file,))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
