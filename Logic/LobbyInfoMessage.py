from Utils.Writer import Writer
from datetime import datetime
from ping3 import ping
from shared import connected_ips
import time
import threading
from database.DataBase import DataBase

class LobbyInfoMessage(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.id = 23457
        self.player = player
        self.domain = self.player.ip_address
        self.running = True
        self.last_update = 0
        self.MessageCount = 0

    def get_ping(self):
        ping_seconds = ping(self.domain)
        if ping_seconds is None:
            return 'N/A'
        ping_ms = int(ping_seconds * 1000)
        return '<1' if ping_ms == 0 and ping_seconds > 0 else ping_ms

    def update_message_count(self):
        while self.running:
            current_time = time.time()
            if current_time - self.last_update >= 1:
                if hasattr(self.player, 'club_low_id') and self.player.club_low_id != 0:
                    DataBase.GetmsgCount(self, self.player.club_low_id)
                self.last_update = current_time
            time.sleep(0.1)

    def start_updater(self):
        self.updater_thread = threading.Thread(target=self.update_message_count)
        self.updater_thread.daemon = True
        self.updater_thread.start()

    def stop_updater(self):
        self.running = False
        if hasattr(self, 'updater_thread'):
            self.updater_thread.join()

    def encode(self):
        self.start_updater()
        
        now = datetime.now()
        ping_ms = self.get_ping()
        ip_count = len(connected_ips)
        
        if ping_ms == 'N/A':
            signal_bars = '✖ (No connection)'
            ping_color = '<c9>'  # Red for no connection
        elif ping_ms == '<1':
            signal_bars = '▆▇█'
            ping_color = '<c3>'  # Green for excellent ping
        elif ping_ms <= 50:
            signal_bars = '▅▆▇'
            ping_color = '<c3>'  # Green for good ping
        elif ping_ms <= 100:
            signal_bars = '▄▅▆'
            ping_color = '<c7>'  # Yellow for average ping
        elif ping_ms <= 150:
            signal_bars = '▃▄▅'
            ping_color = '<c7>'  # Yellow for average ping
        elif ping_ms <= 200:
            signal_bars = '▃▄'
            ping_color = '<c2>'  # Orange for poor ping
        elif ping_ms <= 300:
            signal_bars = '▂▃'
            ping_color = '<c2>'  # Orange for poor ping
        elif ping_ms <= 500:
            signal_bars = '▂'
            ping_color = '<c9>'  # Red for bad ping
        else:
            signal_bars = '▁'
            ping_color = '<c9>'  # Red for terrible ping
        
        message = (
            f"╔═════════════════╗\n"
            f"║     <cffff00>OWN BRAWL</c>                 ║\n"
            f"║     v1.0 BETA                         ║\n"
            f"║     t.me/ownbrawlik       ║\n"
            f"║     Пинг: {ping_color}{ping_ms}мс [{signal_bars}]</c>     ║\n"
            f"║     Онлайн: {ip_count}                       ║\n"
            f"╚═════════════════╝\n"
            f"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nСервер: <c000000>GER<cDD0000>MAN<cFFCE00>Y-2</c>\nПокупка доната: @ZoxDev :)\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        )
        
        self.writeVint(0)
        self.writeString(message)
        self.writeVint(0)