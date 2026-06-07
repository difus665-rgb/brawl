from Utils.Writer import Writer
from database.DataBase import DataBase
import mysql.connector
from mysql.connector import Error
import time


class AllianceChatServer(Writer):
    _last_messages = {}  # Хранение последних сообщений по low_id

    def __init__(self, client, player, msg_content, clubID, isbot=False):
        super().__init__(client)
        self.msg_content = msg_content
        self.id = 24312
        self.player = player
        self.clubID = clubID
        self.isbot = isbot
        self.client = client
        self.message_timestamp = time.time()

    def is_duplicate_message(self):
        last_msg = self._last_messages.get(self.player.low_id)
        if last_msg:
            if (time.time() - last_msg['timestamp'] < 1.0) and last_msg['content'] == self.msg_content:
                return True
        return False

    def encode(self):
        # Проверка дублирования через временную метку
        if not self.isbot and self.is_duplicate_message():
            return

        conn = None
        try:
            conn = DataBase.get_connection()
            if not conn:
                print("[ERROR] Не удалось подключиться к базе данных.")
                return

            with conn.cursor(dictionary=True) as cursor:
                new_tick = 1
                if not self.isbot:
                    cursor.execute("""
                        SELECT Msg FROM club_chats 
                        WHERE clubID = %s AND plrid = %s 
                        ORDER BY Tick DESC LIMIT 1
                    """, (self.clubID, self.player.low_id))
                    last_db_msg = cursor.fetchone()

                    if last_db_msg and last_db_msg['Msg'] == self.msg_content:
                        cursor.execute("""
                            DELETE FROM club_chats 
                            WHERE clubID = %s AND plrid = %s 
                            ORDER BY Tick DESC LIMIT 1
                        """, (self.clubID, self.player.low_id))
                        conn.commit()

                    cursor.execute("SELECT MAX(Tick) AS max_tick FROM club_chats WHERE clubID = %s", (self.clubID,))
                    result = cursor.fetchone()
                    current_tick = result['max_tick'] if result and result['max_tick'] is not None else 0
                    new_tick = current_tick + 1

                    cursor.execute("""
                        INSERT INTO club_chats 
                        (clubID, Event, Tick, plrid, plrname, plrrole, Msg) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        self.clubID,
                        2,
                        new_tick,
                        self.player.low_id,
                        self.player.name,
                        self.player.club_role,
                        self.msg_content
                    ))
                    conn.commit()

                cursor.execute("SELECT * FROM club_chats WHERE clubID = %s ORDER BY Tick DESC LIMIT 1", (self.clubID,))
                last_message = cursor.fetchone()

                if not last_message:
                    return

                # Запись пакета клиенту
                self.writeVint(last_message['Event'])
                self.writeVint(0)
                self.writeVint(new_tick if not self.isbot else 1)  # Используем новый Tick
                self.writeVint(0)
                self.writeVint(last_message['plrid'])
                self.writeString(last_message['plrname'])
                self.writeVint(last_message['plrrole'])
                self.writeVint(0)
                self.writeVint(0)

                if last_message['Event'] == 4:
                    # Специальное событие (например, leave club)
                    self.writeVint(int(last_message['Msg']))
                    self.writeVint(1)
                    self.writeVint(0)
                    self.writeVint(last_message['plrid'])
                    self.writeString(last_message['plrname'])
                else:
                    self.writeString(last_message['Msg'])

                # Обновляем последнее сообщение игрока в памяти
                if not self.isbot:
                    self._last_messages[self.player.low_id] = {
                        'content': self.msg_content,
                        'timestamp': self.message_timestamp
                    }

        except Error as e:
            print(f"[ERROR] MySQL ошибка в AllianceChatServer: {e}")
        finally:
            if conn:
                conn.close()