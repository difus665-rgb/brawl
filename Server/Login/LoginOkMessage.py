import time

from Utils.Writer import Writer


class LoginOkMessage(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.player = player
        self.id = 20104
        self.version = 1

    def encode(self):
        # Account ID
        self.writeInt(0)
        self.writeInt(self.player.low_id)

        # Home ID
        self.writeInt(0)
        self.writeInt(self.player.low_id)

        self.writeString(self.player.token)
        self.writeString()
        self.writeString()

        self.writeInt(34)
        self.writeInt(159)
        self.writeInt(1)

        self.writeString("dev") #prod - говно #dev - норм

        self.writeInt(0)
        self.writeInt(0)
        self.writeInt(0)

        self.writeString()
        self.writeString()
        self.writeString()

        self.writeInt(0)

        self.writeString()
        self.writeString(self.player.Region)
        self.writeString()

        self.writeInt(1)
        self.writeString()

        self.writeInt(2) # Url Entry Array Count
        self.writeString("https://game-assets.brawlstarsgame.com")
        self.writeString("http://a678dbc1c015a893c9fd-4e8cc3b1ad3a3c940c504815caefa967.r87.cf2.rackcdn.com")
        
        self.writeInt(2) # Url Entry Array Count
        self.writeString("https://raw.githubusercontent.com/IsaaSooBart/Project-LaserScratch/main/Files/EventAssets/") # Event Assets
        self.writeString("https://24b999e6da07674e22b0-8209975788a0f2469e68e84405ae4fcf.ssl.cf2.rackcdn.com/event-assets")
