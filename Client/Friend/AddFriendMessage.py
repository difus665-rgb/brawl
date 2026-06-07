from Utils.Reader import BSMessageReader
import json
import mysql.connector
from mysql.connector import Error
from Server.Friend.FriendListMessage import FriendListMessage
from Client.Friend.AddFriendFailedMessage import AddFriendFailedMessage
from database.DataBase import DataBase

class AddFriendMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.HighID = self.read_int()
        self.LowID = self.read_int()

    def process(self):
        conn = DataBase.get_connection()
        if not conn:
            AddFriendFailedMessage(self.client, self.player).send()
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT friends FROM plrs WHERE lowID=%s', (self.player.low_id,))
                user = cursor.fetchone()
                if not user:
                    AddFriendFailedMessage(self.client, self.player).send()
                    return

                friends_json = user[0]
                friends = json.loads(friends_json) if friends_json else []
                new_friend = {'id': self.LowID, 'state': 2}
                test_friend = {'id': self.LowID, 'state': 4}

                if test_friend in friends or new_friend in friends:
                    AddFriendFailedMessage(self.client, self.player).send()
                else:
                    friends.append(new_friend)
                    friends_json = json.dumps(friends)
                    cursor.execute('UPDATE plrs SET friends=%s WHERE lowID=%s', 
                                 (friends_json, self.player.low_id))

                    # Update target player's friends
                    cursor.execute('SELECT friends FROM plrs WHERE lowID=%s', (self.LowID,))
                    target_user = cursor.fetchone()
                    if not target_user:
                        AddFriendFailedMessage(self.client, self.player).send()
                        return

                    target_friends_json = target_user[0]
                    target_friends = json.loads(target_friends_json) if target_friends_json else []
                    new_friend2 = {'id': self.player.low_id, 'state': 3}
                    target_friends.append(new_friend2)
                    target_friends_json = json.dumps(target_friends)
                    cursor.execute('UPDATE plrs SET friends=%s WHERE lowID=%s', 
                                 (target_friends_json, self.LowID))

                    conn.commit()
                    FriendListMessage(self.client, self.player).send()

        except Error as e:
            print(f"[ERROR] MySQL error in AddFriendMessage: {e}")
            AddFriendFailedMessage(self.client, self.player).send()
        finally:
            if conn:
                conn.close()