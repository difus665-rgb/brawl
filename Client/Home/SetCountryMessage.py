from Utils.Reader import BSMessageReader
from Files.CsvLogic.Regions import Regions
from Server.SetRegionResponseMessage import SetRegionResponseMessage
from database.DataBase import DataBase

class SetCountryMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.id = 12998
        self.player = player
        self.client = client

    def decode(self):
        self.read_Vint()
        self.region_id = self.read_Vint()
        self.read_Vint()

    def process(self):
        self.player.Region = Regions().getRegionByID(self.region_id)
        DataBase.replaceValue(self, 'Region', self.player.Region)
        SetRegionResponseMessage(self.client, self.player).send()
