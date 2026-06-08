import sys
from unittest.mock import MagicMock

# 1. СНАЧАЛА нейтрализуем библиотеки, чтобы они не крашили систему
mock = MagicMock()
sys.modules['telebot'] = mock
sys.modules['telebot.apihelper'] = mock
sys.modules['mysql'] = mock
sys.modules['mysql.connector'] = mock

from multiprocessing import Process
import subprocess

def run_core():
    # Запускаем только core.py
    subprocess.run(['python3', 'core.py'])

if __name__ == "__main__":
    print("[СИСТЕМА] Запуск сервера в безопасном режиме...")
    
    # 2. ЗАПУСКАЕМ ТОЛЬКО CORE.PY. 
    # Никакого anticheat.py, никакого botuser.py.
    # Они больше не существуют для системы.
    p = Process(target=run_core)
    p.start()
    p.join()
