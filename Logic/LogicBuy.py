from Utils.Writer import Writer
from random import randint as r
from database.DataBase import DataBase
from Utils.Reader import BSMessageReader
from Logic.Shop import Shop

# 0,1 Бравлер
# 0,2 Удваители
# 0,4 Гаджет
# 0,5 Хз
# 0,6 Вылет
# 0,7 Монеты
# 0,8 Гемы
# 0,9 Выпадение
# 0,10 Гемы
# 0,11 Пин
# 0,12 Вылет

class LogicBuy(Writer):

    def __init__(self, client, player, id11, id22, id33, mult11, mult22, mult33, brawler11, brawler22, brawler33, skin11, skin22, skin33):
        super().__init__(client)
        self.id = 24111
        self.player = player

        self.id1 = id11
        self.id2 = id22
        self.id3 = id33
        
        self.mult1 = mult11
        self.mult2 = mult22
        self.mult3 = mult33

        self.brawler1 = brawler11
        self.brawler2 = brawler22
        self.brawler3 = brawler33
        
        self.skin1 = skin11
        self.skin2 = skin22
        self.skin3 = skin33

    def encode(self):
        self.writeVint(203)
        self.writeVint(0)
        self.writeVint(1)
        self.writeVint(100)
        
        if self.id1 != 0 and self.id2 != 0 and self.id3 != 0:
               self.writeVint(3) # Reward count
        elif self.id1 != 0 and self.id2 != 0:
               self.writeVint(2) # Reward count
        else:
               self.writeVint(1) # Reward count
        	
        
        if self.id1 == 1:
            self.writeVint(self.mult1) # Reward ammount
            self.writeScId(0, 7) # RewardID
            self.writeHexa('''00 00 00''')  # Reward end

            self.player.gold += self.mult1
            DataBase.replaceValue(self, 'gold', self.player.gold)
        elif self.id1 == 2: # Gems
            self.writeVint(self.mult1) # Reward ammount
            self.writeScId(0, 8) # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.gems += self.mult1
            DataBase.replaceValue(self, 'gems', self.player.gems)
        elif self.id1 == 3: # Gadget
            self.writeVint(self.mult1) # Reward Count
            self.writeVint(1) # Value
            self.writeVint(16, self.brawler1) # ScId 16
            self.writeVint(4) # Reward ID
            self.writeVint(0) # ScId 29
            self.writeVint(0) # ScId 52
            self.writeScId(23, self.skin1) # ScId 23
            self.writeVint(0)
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.StarPowerUnlocked[str(self.skin2)] = 1
            DataBase.replaceValue(self, 'StarPowerUnlocked', self.player.StarPowerUnlocked)
        elif self.id1 == 4: #tokensdoubler
            self.writeVint(self.mult1) # Reward ammount
            self.writeScId(0, 2) # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.tokensdoubler += self.mult1
            DataBase.replaceValue(self, 'Tokens_Doubler', self.player.tokensdoubler)
        elif self.id1 == 5: # Brawler
            self.writeVint(self.mult1)  # Reward amount
            self.writeScId(16, self.brawler1)  # CsvID
            self.writeVint(6)  # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
        elif self.id1 == 6: # Brawler
            self.writeVint(self.mult1)  # Reward amount
            self.writeScId(16, self.brawler1)  # CsvID
            self.writeVint(1)  # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.UnlockedBrawlers[str(self.brawler1)] = 1
            DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
        elif self.id1 == 7: # Skin
            self.writeVint(1) # Value
            self.writeVint(0) # ScId
            self.writeVint(9) # Reward ID
            self.writeScId(29, self.skin1) # ScId
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(1)
            self.writeVint(0)
            self.writeVint(0)
            self.player.UnlockedSkins[str(self.skin1)] = 1
            DataBase.replaceValue(self, 'UnlockedSkins', self.player.UnlockedSkins)
        elif self.id1 == 8: # Skin
            self.writeVint(1) # Value
            self.writeVint(0) # ScId
            self.writeVint(11) # Reward ID
            self.writeVint(0) # ScId
            self.writeScId(52, self.skin1)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
        if self.id2 == 1:
            self.writeVint(self.mult2) # Reward ammount
            self.writeScId(0, 8) # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.gems += self.mult2
            DataBase.replaceValue(self, 'gems', self.player.gems)
        elif self.id2 == 2: # Gems
            self.writeVint(self.mult2) # Reward ammount
            self.writeScId(0, 7) # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.gold += self.mult2
            DataBase.replaceValue(self, 'gold', self.player.gold)
        elif self.id2 == 3: # Gadget
            self.writeVint(self.mult1) # Reward Count
            self.writeVint(1) # Value
            self.writeVint(0) # ScId 16
            self.writeVint(4) # Reward ID
            self.writeVint(0) # ScId 29
            self.writeVint(0) # ScId 52
            self.writeScId(23, self.skin1) # ScId 23
            self.writeVint(0)
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.StarPowerUnlocked[str(self.skin2)] = 1
            DataBase.replaceValue(self, 'StarPowerUnlocked', self.player.StarPowerUnlocked)
        elif self.id2 == 5: # Brawler
            self.writeVint(self.mult2)  # Reward amount
            self.writeScId(16, self.brawler2)  # CsvID
            self.writeVint(6)  # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
        elif self.id2 == 6: # Brawler
            self.writeVint(self.mult2)  # Reward amount
            self.writeScId(16, self.brawler2)  # CsvID
            self.writeVint(1)  # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.UnlockedBrawlers[str(self.brawler2)] = 1
            DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
        elif self.id2 == 7: # Skin
            self.writeVint(1) # Value
            self.writeVint(0) # ScId
            self.writeVint(9) # Reward ID
            self.writeScId(29, self.skin2) # ScId
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(1)
            self.writeVint(0)
            self.writeVint(0)
            self.player.UnlockedSkins[str(self.skin2)] = 1
            DataBase.replaceValue(self, 'UnlockedSkins', self.player.UnlockedSkins)
        elif self.id2 == 8: # Skin
            self.writeVint(1) # Value
            self.writeVint(0) # ScId
            self.writeVint(11) # Reward ID
            self.writeVint(0) # ScId
            self.writeScId(52, self.skin1)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
        if self.id3 == 1:
            self.writeVint(self.mult3) # Reward ammount
            self.writeScId(0, 7) # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.gold += self.mult3
            DataBase.replaceValue(self, 'gold', self.player.gold)
        elif self.id3 == 3: # Gadget
            self.writeVint(self.mult1) # Reward Count
            self.writeVint(1) # Value
            self.writeVint(0) # ScId 16
            self.writeVint(4) # Reward ID
            self.writeVint(0) # ScId 29
            self.writeVint(0) # ScId 52
            self.writeScId(23, self.skin1) # ScId 23
            self.writeVint(0)
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.StarPowerUnlocked[str(self.skin2)] = 1
            DataBase.replaceValue(self, 'StarPowerUnlocked', self.player.StarPowerUnlocked)
        elif self.id3 == 2: # Gems
            self.writeVint(self.mult3) # Reward ammount
            self.writeScId(0, 8) # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.gems += self.mult3
            DataBase.replaceValue(self, 'gems', self.player.gems)
        elif self.id3 == 5: # Brawler
            self.writeVint(self.mult3)  # Reward amount
            self.writeScId(16, self.brawler3)  # CsvID
            self.writeVint(6)  # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
        elif self.id3 == 6: # Brawler
            self.writeVint(self.mult3)  # Reward amount
            self.writeScId(16, self.brawler3)  # CsvID
            self.writeVint(1)  # RewardID
            self.writeHexa('''00 00 00''')  # Reward end
            self.player.UnlockedBrawlers[str(self.brawler3)] = 1
            DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
        elif self.id3 == 7: # Skin
            self.writeVint(1) # Value
            self.writeVint(0) # ScId
            self.writeVint(9) # Reward ID
            self.writeScId(29, self.skin3) # ScId
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(1)
            self.writeVint(0)
            self.writeVint(0)
            self.player.UnlockedSkins[str(self.skin3)] = 1
            DataBase.replaceValue(self, 'UnlockedSkins', self.player.UnlockedSkins)
        elif self.id3 == 8: # Skin
            self.writeVint(1) # Value
            self.writeVint(0) # ScId
            self.writeVint(11) # Reward ID
            self.writeVint(0) # ScId
            self.writeScId(52, self.skin1)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)
            
        for i in range(13):
            self.writeVint(0)