from database.DataBase import DataBase
from Utils.Writer import Writer
import mysql.connector
from mysql.connector import Error


class AllianceStreamMessage(Writer):

    def __init__(self, client, player, clubLowID, type):
        super().__init__(client)
        self.id = 24311
        self.player = player
        self.eventType = type
        self.clubLowID = clubLowID

    def encode(self):
        if self.clubLowID == 0:
            self.writeVint(0)
            return

        # Получаем количество сообщений
        DataBase.GetmsgCount(self, self.clubLowID)
        self.writeVint(self.MessageCount)
        
        # Получаем соединение с базой данных
        conn = DataBase.get_connection()
        if not conn:
            self.writeVint(0)
            return
            
        try:
            with conn.cursor(dictionary=True) as cursor:
                # Получаем все сообщения чата клуба
                cursor.execute(
                    "SELECT * FROM club_chats WHERE clubID = %s ORDER BY Tick ASC", 
                    (self.clubLowID,)
                )
                messages = cursor.fetchall()
                
                # Кодируем каждое сообщение
                for msg in messages:
                    self.writeVint(msg['Event'])
                    self.writeVint(0)
                    self.writeVint(msg['Tick'])
                    self.writeVint(0)
                    self.writeVint(msg['plrid'])
                    self.writeString(msg['plrname'])
                    self.writeVint(msg['plrrole'])
                    self.writeVint(0)
                    self.writeVint(0)
                    
                    if msg['Event'] == 4:  # Системное сообщение
                        self.writeVint(int(msg['Msg']))  # Тип действия
                        self.writeVint(1)
                        self.writeVint(0)
                        self.writeVint(msg['plrid'])
                        self.writeString(msg['plrname'])
                    else:
                        self.writeString(msg['Msg'])  # Текст сообщения
                        
        except Error as e:
            print(f"[ERROR] MySQL error in AllianceStreamMessage: {e}")
            self.writeVint(0)
        finally:
            if conn:
                conn.close()