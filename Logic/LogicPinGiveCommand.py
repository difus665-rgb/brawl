from database.DataBase import DataBase
import random
from Utils.Writer import Writer


class LogicPinGiveCommand(Writer):

    def __init__(self, client, player, pin):
        super().__init__(client)
        self.id = 24111
        self.player = player
        self.pin = pin


    def encode(self):
        # Box info
        self.writeVint(203) # CommandID
        self.writeVint(0)   # Unknown
        self.writeVint(1)   # Unknown
        self.writeVint(100)  # BoxID
        
        self.writeVint(1) # Value
        
        self.writeVint(1) # Value
        self.writeVint(0) # ScId
        self.writeVint(11) # Reward ID
        self.writeVint(0) # ScId
        self.writeScId(52, self.pin)
        self.player.UnlockedPins[str(self.pin)]=1
        DataBase.replaceValue(self, 'UnlockedPins', self.player.UnlockedPins)
        # Box end
        for i in range(13):
            self.writeVint(0)