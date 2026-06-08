from multiprocessing import Process
import subprocess

def run_script(script_name):
    try:
        # Используем python3 для запуска
        subprocess.run(['python3', script_name])
    except Exception as e:
        print(f"Ошибка при запуске {script_name}: {e}")

if __name__ == "__main__":
    # ВНИМАНИЕ: МЫ ОСТАВИЛИ ТОЛЬКО CORE.PY
    # anticheat.py и botuser.py удалены из списка, чтобы они не крашили сервер
    files = ['core.py']
    
    processes = []
    for file in files:
        process = Process(target=run_script, args=(file,))
        processes.append(process)
        process.start()
    
    # Ожидаем завершения процесса сервера
    for process in processes:
        process.join()
