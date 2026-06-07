from database.DataBase import DataBase
from Utils.Reader import BSMessageReader

class LogicRemoveNewTagBrawler(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.read_Vint()
        self.read_Vint()
        self.read_Vint()
        self.read_Vint()
        self.read_Vint()                  # csvID
        self.BrawlerID = self.read_Vint() # BrawlerID


    def process(self):
        if self.player.Brawler_newTag[str(self.BrawlerID)] == 1:
                self.player.Brawler_newTag[str(self.BrawlerID)] = 0
                DataBase.replaceValue(self, 'brawlerNewTag', self.player.Brawler_newTag)