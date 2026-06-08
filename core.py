import socket
import time
import os
import sqlite3
import json
from threading import Thread, Lock
from collections import defaultdict
from Logic.Device import Device
from Logic.Player import Players
from Logic.LogicMessageFactory import packets
from Utils.Config import Config
from Utils.Helpers import Helpers
from shared import connected_ips
import mysql.connector
from mysql.connector import Error
from pyngrok import ngrok

connection_timestamps = defaultdict(list)
connection_lock = Lock()
addr_lock = Lock()

def log_info(*args):
    print('[ИНФО]', *args)

class DataBase:
    @staticmethod
    def get_connection():
        try:
            with open('./database.json', 'r') as f:
                db_config = json.load(f)
            conn = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            return conn
        except FileNotFoundError:
            print("[ERROR] database.json file not found.")
            return None
        except KeyError as e:
            print(f"[ERROR] Missing key in database.json: {e}")
            return None
        except Error as e:
            print(f"[ERROR] MySQL connection failed: {e}")
            return None

    def create_all_tables(self):
        conn = DataBase.get_connection()
        if not conn:
            print("[ERROR] Failed to connect to database while creating tables.")
            return
        try:
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS plrs (
                    token VARCHAR(255),
                    lowID INT,
                    name VARCHAR(255),
                    trophies INT,
                    gold INT,
                    gems INT,
                    starpoints INT,
                    tickets INT,
                    Troproad INT,
                    profile_icon INT,
                    name_color INT,
                    clubID INT,
                    clubRole INT,
                    brawlerData JSON,
                    brawlerID INT,
                    skinID INT,
                    roomID INT,
                    box INT,
                    bigbox INT,
                    online INT,
                    vip INT,
                    playerExp INT,
                    friends JSON,
                    SCC TEXT,
                    trioWINS INT,
                    sdWINS INT,
                    theme INT,
                    BPTOKEN INT,
                    BPXP INT,
                    quests JSON,
                    freepass JSON,
                    buypass JSON,
                    notifRead INT,
                    notifRead2 INT,
                    ip_address VARCHAR(255),
                    creation_date VARCHAR(255),
                    Region VARCHAR(255),
                    notifications JSON,
                    playerData JSON,
                    PRIMARY KEY (token)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS gr (
                    roomID INT PRIMARY KEY,
                    mapID INT,
                    gadget INT,
                    players JSON,
                    type INT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    roomID INT,
                    Event INT,
                    Tick INT,
                    plrid INT,
                    plrname VARCHAR(255),
                    plrrole INT,
                    Msg TEXT
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS clubs (
                    clubID INT PRIMARY KEY,
                    name VARCHAR(255),
                    `desc` TEXT,
                    region VARCHAR(255),
                    badgeID INT,
                    type INT,
                    trophiesneeded INT,
                    friendlyfamily INT,
                    trophies INT,
                    members JSON,
                    notif JSON
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS club_chats (
                    clubID INT,
                    Event INT,
                    Tick INT,
                    plrid INT,
                    plrname VARCHAR(255),
                    plrrole INT,
                    Msg TEXT
                )
            """)

            conn.commit()
            print("[MYSQL CONNECT] Всё супер!.")
        except Error as e:
            print(f"[ERROR] MySQL error while creating tables: {e}")
        finally:
            cur.close()
            conn.close()

class Server:
    Clients = {"ClientCounts": 0, "Clients": {}}
    ThreadCount = 0
    MAX_THREADS = 99999999
    MAX_BYTES_PER_SECOND = 20480

    def __init__(self, ip: str, port: int):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.ip = ip
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.port))
        log_info(f'Лобби запущено! {self.ip}:{self.port}')
        self.clear_blocked_ips_in_config()
        self.clear_connected_ips()
        
        DataBase().create_all_tables()

        self.total_sent_bytes = 0
        self.total_received_bytes = 0
        self.blocked_ips = set()
        self.reported_blocked_ips = set()
        self.last_warning_time = 0

        Thread(target=self.monitor_load, daemon=True).start()
        Thread(target=self.cleanup_connection_logs, daemon=True).start()

    def clear_blocked_ips_in_config(self):
        try:
            with open('config.json', 'r') as config_file:
                settings = json.load(config_file)
            settings['block'] = []
            with open('config.json', 'w') as config_file:
                json.dump(settings, config_file, indent=4)
            log_info("Заблокированные IP очищены в config.json при запуске сервера")
        except Exception as e:
            log_info(f"Ошибка очистки config.json: {e}")

    def clear_connected_ips(self):
        try:
            with open('JSON/ConnectedIP.json', 'w') as log_file:
                json.dump([], log_file, indent=4)
            log_info("Файл ConnectedIP.json очищен при запуске сервера.")
        except Exception as e:
            log_info(f"Ошибка очистки ConnectedIP.json: {e}")

    def log_connection(self, ip):
        moscow_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 3 * 3600))  # UTC+3
        try:
            with sqlite3.connect("database/Player/plr.db") as conn:
                c = conn.cursor()
                c.execute("SELECT lowID, name FROM plrs WHERE SCC = ?", (ip,))
                result = c.fetchone()
        except Exception as e:
            log_info(f"[WARN] Ошибка чтения SQLite: {e}")
            result = None

        log_data = {
            "time": moscow_time,
            "ip": ip
        }

        try:
            with open('JSON/ConnectedIP.json', 'a', encoding='utf-8') as log_file:
                json.dump(log_data, log_file, ensure_ascii=False, indent=4)
                log_file.write('\n')
            log_info(f"Подключение: {log_data}")
        except Exception as e:
            log_info(f"Ошибка записи в ConnectedIP.json: {e}")

    def log_blocked_ip(self, ip):
        try:
            with open('JSON/blocked_ips.log', 'a', encoding='utf-8') as log_file:
                log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Блокировка IP: {ip}\n")
        except Exception as e:
            log_info(f"Ошибка записи в blocked_ips.log: {e}")

    def update_blocked_clients(self, ip):
        try:
            with open('config.json', 'r') as config_file:
                settings = json.load(config_file)
            if ip not in settings['block']:
                settings['block'].append(ip)
            with open('config.json', 'w') as config_file:
                json.dump(settings, config_file, indent=4)
            log_info(f"Заблокированные IP: {settings['block']}")
        except Exception as e:
            log_info(f"Ошибка обновления config.json: {e}")

    def cleanup_connection_logs(self):
        while True:
            time.sleep(60)
            current_time = time.time()
            with connection_lock:
                expired_ips = [
                    ip for ip, timestamps in connection_timestamps.items()
                    if all(current_time - t > 300 for t in timestamps)
                ]
                for ip in expired_ips:
                    del connection_timestamps[ip]
            log_info(f"[Cleanup] Очищено {len(expired_ips)} старых IP из логов подключений.")

    def monitor_load(self):
        while True:
            time.sleep(3600)
            log_info(f"Мониторинг нагрузки: {Server.ThreadCount} active clients, "
                     f"received {self.total_received_bytes // 1024} KB, sent {self.total_sent_bytes // 1024} KB")

    def start(self):
        while True:
            self.server.listen()
            try:
                client, address = self.server.accept()
            except Exception as e:
                log_info(f"Ошибка при приёме подключения: {e}")
                continue

            client_ip = address[0]

            if client_ip in self.blocked_ips:
                if client_ip not in self.reported_blocked_ips:
                    log_info(f"[AntiDDoS] Блокировка IP {client_ip} (уже в списке)")
                    self.reported_blocked_ips.add(client_ip)
                client.close()
                continue

            if Server.ThreadCount >= self.MAX_THREADS:
                if time.time() - self.last_warning_time > 10:
                    log_info(f"Превышено количество потоков ({Server.ThreadCount}). Подключение закрыто.")
                    self.last_warning_time = time.time()
                client.close()
                continue

            current_time = time.time()
            with connection_lock:
                connection_timestamps[client_ip] = [
                    t for t in connection_timestamps[client_ip]
                    if current_time - t < 1.0
                ]

                connection_timestamps[client_ip].append(current_time)

                if len(connection_timestamps[client_ip]) > 2:
                    if client_ip not in self.blocked_ips:
                        log_info(f"[AntiDDoS] БЛОКИРОВКА IP {client_ip}")
                        self.blocked_ips.add(client_ip)
                        self.update_blocked_clients(client_ip)
                        self.log_blocked_ip(client_ip)
                    client.close()
                    continue

            self.log_connection(client_ip)
            connected_ips.add(client_ip)
            ClientThread(client, address, self).start()
            Server.ThreadCount += 1


class ClientThread(Thread):
    MAX_RECEIVE_BYTES = 20480
    MAX_BYTES_PER_SECOND = 20480

    def __init__(self, client, address, server):
        super().__init__()
        self.client = client
        self.address = address
        self.device = Device(self.client)
        self.player = Players(self.device)
        self.server = server
        self.bytes_received_in_last_second = 0
        self.last_packet_time = time.time()
        self._warned_unknown = False

    def recvall(self, length):
        data = b''
        while len(data) < length:
            packet = self.client.recv(length - len(data))
            if not packet:
                return b''
            data += packet
        return data

    def run(self):
        client_ip = self.address[0]
        try:
            client_ip = self.client.getpeername()[0]
            self.player.ip_address = client_ip

            first_valid_packet_time = None
            timeout_seconds = 3             
            start_time = time.time()

            while True:
                header = self.client.recv(7)
                if len(header) != 7:
                    break

                packet_id = int.from_bytes(header[:2], 'big')
                length = int.from_bytes(header[2:5], 'big')
                data = self.recvall(length)
                if len(data) != length:
                    break

                self.server.total_received_bytes += length
                self.bytes_received_in_last_second += length

                if time.time() - self.last_packet_time >= 1:
                    if self.bytes_received_in_last_second > self.MAX_BYTES_PER_SECOND:
                        log_info(f"[AntiDDoS] IP {client_ip} превысил лимит трафика: {self.bytes_received_in_last_second} байт/сек")
                        self.server.blocked_ips.add(client_ip)
                        self.server.update_blocked_clients(client_ip)
                        self.server.log_blocked_ip(client_ip)
                        self.client.close()
                        return
                    self.bytes_received_in_last_second = 0
                    self.last_packet_time = time.time()

                if packet_id in packets:
                    first_valid_packet_time = time.time()
                    message = packets[packet_id](self.client, self.player, data)
                    message.decode()
                    message.process()
                else:
                    if not self._warned_unknown:
                        log_info(f"[WARN] Неизвестный packet_id: {packet_id} (IP: {client_ip})")
                        self._warned_unknown = True

                if first_valid_packet_time is None:
                    if time.time() - start_time > timeout_seconds:
                        log_info(f"[KICK] IP {client_ip} не отправил валидный пакет за {timeout_seconds} секунд. Кик.")
                        break

        except (ConnectionResetError, BrokenPipeError):
            pass  
        except Exception as e:
            log_info(f"[ERROR] Ошибка клиента {client_ip}: {e}")
        finally:
            self.client.close()
            connected_ips.discard(client_ip)
            Server.ThreadCount -= 1
            log_info(f"[INFO] IP {client_ip} вышел из игры")


if __name__ == "__main__":
    Helpers.load_logic()
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"block": []}, f, indent=4)
            
    # ЗАПУСК ТУННЕЛЯ NGROK ПЕРЕД СТАРТОМ СОКЕТОВ
    try:
        # ВСТАВЬ СВОЙ ТОКЕН В КАВЫЧКИ НИЖЕ (вместо ТВОЙ_ТОКЕН)
        ngrok.set_auth_token("3EpDqWGtAXG13Lz8Ot1FGTDh6qL_2qo3rue38xZmfVDXKQyMg")
        tunnel = ngrok.connect(9339, "tcp")
        print("\n" + "="*50)
        print("=== ТУННЕЛЕЛИРОВАНИЕ ИГРЫ УСПЕШНО ВКЛЮЧЕНО! ===")
        print(f"АДРЕС ДЛЯ КЛИЕНТА APK: {tunnel.public_url}")
        print("="*50 + "\n")
    except Exception as ngrok_error:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА NGROK]: {ngrok_error}")
            
    server = Server("0.0.0.0", 9339)
    server.start()   
