from Utils.Reader import BSMessageReader
from Logic.Commands.Client.LogicPurchaseBoxCommand import LogicPurchaseBoxCommand
from Logic.Commands.Client.LogicPurchaseOfferCommand import LogicPurchaseOfferCommand
from Logic.Commands.Client.LogicUpgradeBrawler import Upgrade_Brawler
from Logic.Commands.Client.LogicPurchaseHeroLvlUpMaterialCommand import LogicPurchaseHeroLvlUpMaterialCommand
from Logic.Commands.Client.LogicSelectSkinCommand import LogicSelectSkinCommand
from Logic.Commands.Client.LogicSetPlayerNameColorCommand import LogicSetPlayerNameColorCommand
from Logic.Commands.Client.LogicSetPlayerThumbnailCommand import LogicSetPlayerThumbnailCommand
from Logic.Commands.Client.LogicViewNotificationCommand import LogicViewNotificationCommand
from Logic.MCbyLkPrtctrd.MilestonesClaimByLkPrtctrd import MilestonesClaimByLkPrtctrd
from Logic.Commands.Client.LogicBuyBrawlPassCommand import LogicBuyBrawlPassCommand
from Logic.Commands.Client.LogicBrawlPassTokensCommand import LogicBrawlPassTokensCommand
from Logic.Commands.Client.LogicNewEventCommand import LogicNewEventCommand
from Logic.Commands.Client.LogicPurchaseDoubleCoinsCommand import LogicPurchaseDoubleCoinsCommand
from Logic.Commands.Client.LogicRemoveNewTagBrawler import LogicRemoveNewTagBrawler
from Logic.Commands.Client.LogicQuestSeenCommand import LogicQuestSeenCommand
from Server.Login.LoginFailedMessage import LoginFailedMessage
from Logic.Commands.Client.LogicSelectQuestBrawler import LogicSelectQuestBrawler
from Logic.Commands.Client.LogicSetPlayerStarpower import LogicSetPlayerStarpower

class EndClientTurn(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.client = client
        self.player = player

    def decode(self):
        self.a = self.read_Vint()
        self.b = self.read_Vint()
        self.c = self.read_Vint()
        self.d = self.read_Vint()
        self.commandID = self.read_Vint()

    def process(self):
        if self.commandID == 500 or self.commandID == 535:
            LogicPurchaseBoxCommand.decode(self)
            LogicPurchaseBoxCommand.process(self)
        elif self.commandID == 528:
            LogicViewNotificationCommand.decode(self)
            LogicViewNotificationCommand.process(self)
        elif self.commandID == 517:
            MilestonesClaimByLkPrtctrd.decode(self)
            MilestonesClaimByLkPrtctrd.process(self)
        elif self.commandID == 506:
            LogicSelectSkinCommand.decode(self)
            LogicSelectSkinCommand.process(self)
        elif self.commandID == 505:
            LogicSetPlayerThumbnailCommand.decode(self)
            LogicSetPlayerThumbnailCommand.process(self)
        elif self.commandID == 503:
            LogicNewEventCommand.decode(self)
            LogicNewEventCommand.process(self)
        elif self.commandID == 509:
            LogicPurchaseDoubleCoinsCommand.decode(self)
            LogicPurchaseDoubleCoinsCommand.process(self)
        elif self.commandID == 519:
            LogicPurchaseOfferCommand.decode(self)
            LogicPurchaseOfferCommand.process(self)
        elif self.commandID == 520:
            Upgrade_Brawler.decode(self)
            Upgrade_Brawler.process(self)
        elif self.commandID == 521:
            LogicPurchaseHeroLvlUpMaterialCommand.decode(self)
            LogicPurchaseHeroLvlUpMaterialCommand.process(self)
        elif self.commandID == 522:
            LogicRemoveNewTagBrawler.decode(self)
            LogicRemoveNewTagBrawler.process(self)
        elif self.commandID == 525:
            LogicSelectQuestBrawler.decode(self)
            LogicSelectQuestBrawler.process(self)
        elif self.commandID == 527:
            LogicSetPlayerNameColorCommand.decode(self)
            LogicSetPlayerNameColorCommand.process(self)
        elif self.commandID == 529:
            LogicSetPlayerStarpower.decode(self)
            LogicSetPlayerStarpower.process(self)
        elif self.commandID == 533:
            LogicQuestSeenCommand.decode(self)
            LogicQuestSeenCommand.process(self)
        elif self.commandID == 534:
            LogicBuyBrawlPassCommand.decode(self)
            LogicBuyBrawlPassCommand.process(self)
        elif self.commandID == 536:
            LogicBrawlPassTokensCommand.decode(self)
            LogicBrawlPassTokensCommand.process(self)
        elif self.commandID == -134217728:
            pass
        elif self.commandID == 203:
            pass
        elif self.commandID == 515:
            pass
        elif self.commandID == 218:
            print("Привет")
            pass
        else:
            print(f"[WARNING] Неизвестный пакет: {self.commandID}")
            #if self.commandID != 203:
                #self.player.err_code = 11
                #LoginFailedMessage(self.client, self.player, f"ERROR: {self.commandID}. Клиент и сервер не синхронизированы!").send()
                #print(f"[WARNING] Неизвестный пакет: {self.commandID}")