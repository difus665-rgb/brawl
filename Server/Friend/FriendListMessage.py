import json
import mysql.connector
from mysql.connector import Error
from Utils.Writer import Writer
from Server.Friend.FriendOnlineStatusEntryMessage import FriendOnlineStatusEntryMessage
from database.DataBase import DataBase

class FriendListMessage(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.id = 20105
        self.player = player

    def encode(self):
        conn = DataBase.get_connection()
        if not conn:
            print(f"[ERROR] Failed to connect to database for player lowID {self.player.low_id}")
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT friends FROM plrs WHERE lowID=%s', (self.player.low_id,))
                user = cursor.fetchone()
                if not user:
                    return

                friends = json.loads(user[0]) if user[0] else []
                valid_friends = []

                self.writeInt(0)
                self.writeBoolean(True)
                self.writeInt(len(friends))

                for data in friends:
                    self.players = DataBase.loadbyID(self, data["id"])
                    if not self.players:
                        continue

                    valid_friends.append(data)

                    self.writeInt(0)
                    self.writeInt(self.players[1])

                    for _ in range(6):
                        self.writeString('')

                    self.writeInt(self.players[3])
                    self.writeInt(data["state"])
                    for _ in range(3):
                        self.writeInt(0)

                    self.writeBoolean(False)

                    self.writeString('')
                    self.writeInt(0)

                    self.writeBoolean(True)

                    self.writeString(f"{self.players[2]}")
                    self.writeVint(100)
                    self.writeVint(28000000 + self.players[9])
                    self.writeVint(43000000 + self.players[10])
                    self.writeVint(43000000 + self.players[10] if self.players[20] == 1 else 0)

                    FriendOnlineStatusEntryMessage(self.client, self.player, data["id"], self.players[19], self.players[16]).send()

                if valid_friends != friends:
                    updated_friends_json = json.dumps(valid_friends)
                    cursor.execute('UPDATE plrs SET friends=%s WHERE lowID=%s', 
                                 (updated_friends_json, self.player.low_id))
                    conn.commit()

        except Error as e:
            print(f"[ERROR] MySQL error in FriendListMessage for player lowID {self.player.low_id}: {e}")
        except Exception as e:
            print(f"[ERROR] General error in FriendListMessage for player lowID {self.player.low_id}: {e}")
        finally:
            if conn:
                conn.close()