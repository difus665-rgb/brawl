from database.DataBase import DataBase
from Utils.Reader import BSMessageReader
from Utils.Writer import Writer
import mysql.connector
from mysql.connector import Error
import json

class FriendSuggestionsMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.HighID = self.read_int()
        self.LowID = self.read_int()

    def process(self):
        sendStream = AddableFriendsMessage(self.client, self.player)
        sendStream.send()

class AddableFriendsMessage(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.id = 20199
        self.player = player

    def encode(self):
        db = DataBase.getSuggestions(self)
        friends = []
        
        # Fetch player's friends from MySQL
        conn = DataBase.get_connection()
        if conn and self.player.low_id > 2:
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT friends FROM plrs WHERE lowID=%s', (self.player.low_id,))
                    user = cursor.fetchone()
                    if user and user[0]:
                        friends = json.loads(user[0])
            except Error as e:
                print(f"[ERROR] MySQL error in AddableFriendsMessage: {e}")
            finally:
                conn.close()

        # Filter out existing friends and self
        filtered_db = [data for data in db if data[0] not in [friend['id'] for friend in friends] and data[0] != self.player.low_id]

        self.writeInt(len(filtered_db))  # Number of suggested friends
        for data in filtered_db:
            self.players = DataBase.loadbyID(self, data[0])
            if not self.players:
                continue

            self.writeInt(0)  # HighID
            self.writeInt(self.players[1])  # LowID

            # Empty strings for various fields
            for _ in range(6):
                self.writeString()

            self.writeInt(self.players[3])  # Trophies
            self.writeInt(0)  # Friend state (0 for suggestions)
            for _ in range(3):
                self.writeInt(0)

            self.writeBoolean(False)  # Unknown boolean

            self.writeString()  # Empty string
            self.writeInt(0)  # Unknown int

            self.writeBoolean(True)  # Is a player

            # Player name with VIP check
            self.writeString(f"{self.players[2]}")
            self.writeVint(100)  # Unknown constant
            self.writeVint(28000000 + self.players[9])  # Profile icon
            self.writeVint(43000000 + self.players[10])  # Name color
            if self.players[20] == 1:  # VIP check
                self.writeVint(43000000 + self.players[10])  # VIP name color
            else:
                self.writeVint(0)  # Default name color