import os
import sys
import time
import stat
import requests
import subprocess
import threading
from multiprocessing import Process

def start_playit_tunnel():
    """Фоновый запуск туннеля Playit.gg для получения IP и порта"""
    print("[PLAYIT] Подготовка агента Playit.gg...")
    playit_path = os.path.join(os.getcwd(), "playit")
    
    if not os.path.exists(playit_path):
        try:
            url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux-amd64"
            print("[PLAYIT] Скачивание агента...")
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


def run_script(script_name):
    try:
        subprocess.run(['python3', script_name])
    except Exception as e:
        print(f"Ошибка при запуске {script_name}: {e}")


if __name__ == "__main__":
    print("[СИСТЕМА] Запуск сервера в безопасном автономном режиме (Без Бота и MySQL)...")
    
    # 1. Сразу запускаем туннель
    start_playit_tunnel()
    time.sleep(2)
    
    # 2. ЖЕСТКО ЗАПУСКАЕМ ТОЛЬКО CORE.PY (ИГРОВОЙ СЕРВЕР). 
    # Мы полностью вырезали 'anticheat.py' и 'botuser.py', чтобы они больше никогда не создавали ошибку 409 и не падали!
    files = ['core.py']
    
    processes = []
    for file in files:
        process = Process(target=run_script, args=(file,))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
