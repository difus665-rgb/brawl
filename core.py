import sys
from unittest.mock import MagicMock

# --- ГЛОБАЛЬНАЯ НЕЙТРАЛИЗАЦИЯ ---
# Создаем фейковые объекты, которые ничего не делают
mock = MagicMock()
sys.modules['telebot'] = mock
sys.modules['telebot.apihelper'] = mock
sys.modules['mysql'] = mock
sys.modules['mysql.connector'] = mock
# ---------------------------------from multiprocessing import Process
import subprocess

def run_script(script_name):
    try:
        subprocess.run(['python3', script_name])
    except Exception as e:
        print(f"Ошибка при запуске {script_name}: {e}")

if __name__ == "__main__":
    files = ['core.py', 'anticheat.py', 'botuser.py']
    
    processes = []
    for file in files:
        process = Process(target=run_script, args=(file,))
        processes.append(process)
        process.start()
    
    
    # Ожидаем завершения всех процессов (магазин работает в фоне)
    for process in processes:
        process.join()
