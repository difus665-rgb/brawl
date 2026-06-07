from Utils.Reader import BSMessageReader
from Server.Battle.BattleLogMessage import BattleLogMessage

class GetBattleLog(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.id = 14114
        self.player = player
        self.client = client

    def decode(self):
    	pass

    def process(self, db):
        BattleLogMessage(self.client, self.player).send()