from Utils.Reader import BSMessageReader
from database.DataBase import DataBase

class SendClubFriendMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.HighID = self.read_int()
        self.LowID = self.read_int()

    def process(self):
        # Добавление друга для текущего игрока
        player_data = DataBase.loadbyID(self, self.player.low_id)
        if player_data:
            friends = json.loads(player_data[22]) if player_data[22] else []
            new_friend = {'id': self.LowID, 'state': 2}
            friends.append(new_friend)
            DataBase.replaceValue(self, 'friends', friends)

        # Добавление текущего игрока как друга для целевого игрока
        target_data = DataBase.loadbyID(self, self.LowID)
        if target_data:
            target_friends = json.loads(target_data[22]) if target_data[22] else []
            new_friend2 = {'id': self.player.low_id, 'state': 3}
            target_friends.append(new_friend2)
            DataBase.replaceOtherValue(self, self.LowID, 'friends', target_friends)