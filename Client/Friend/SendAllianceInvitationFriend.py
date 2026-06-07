from Utils.Reader import BSMessageReader
import json
import mysql.connector
from mysql.connector import Error
from Server.Friend.FriendListMessage import FriendListMessage
from database.DataBase import DataBase

class SendAllianceInvitationFriend(BSMessageReader):
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
            return

        try:
            with conn.cursor() as cursor:
                # Update current player's friends
                cursor.execute('SELECT friends FROM plrs WHERE lowID=%s', (self.player.low_id,))
                user = cursor.fetchone()
                if user and user[0]:
                    friends = json.loads(user[0])
                    new_friend = {'id': self.LowID, 'state': 2}
                    if new_friend not in friends:
                        friends.append(new_friend)
                        friends_json = json.dumps(friends)
                        cursor.execute('UPDATE plrs SET friends=%s WHERE lowID=%s', 
                                     (friends_json, self.player.low_id))

                # Update target player's friends
                cursor.execute('SELECT friends FROM plrs WHERE lowID=%s', (self.LowID,))
                target_user = cursor.fetchone()
                if target_user and target_user[0]:
                    target_friends = json.loads(target_user[0])
                    new_friend2 = {'id': self.player.low_id, 'state': 3}
                    if new_friend2 not in target_friends:
                        target_friends.append(new_friend2)
                        target_friends_json = json.dumps(target_friends)
                        cursor.execute('UPDATE plrs SET friends=%s WHERE lowID=%s', 
                                     (target_friends_json, self.LowID))

                conn.commit()
                FriendListMessage(self.client, self.player).send()

        except Error as e:
            print(f"[ERROR] MySQL error in SendAllianceInvitationFriend: {e}")
        finally:
            if conn:
                conn.close()