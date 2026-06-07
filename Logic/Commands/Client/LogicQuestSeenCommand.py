from database.DataBase import DataBase
from Logic.Commands.Server.LogicQuestSeenDataCommand import LogicQuestSeenDataCommand

from Utils.Reader import BSMessageReader

class LogicQuestSeenCommand(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        pass


    def process(self):
        LogicQuestSeenDataCommand(self.client, self.player).send()