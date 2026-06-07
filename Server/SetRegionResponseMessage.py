from Utils.Writer import Writer
from database.DataBase import DataBase
from Files.CsvLogic.Regions import Regions
class SetRegionResponseMessage(Writer):

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 24178
        self.client = client
        self.player = player

    def encode(self):
        self.region_id = Regions().getIDByRegion(self.player.Region)
        self.writeVint(0)
        self.writeScId(14, self.region_id)