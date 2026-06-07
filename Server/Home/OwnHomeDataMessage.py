from Utils.Writer import Writer
from Logic.Notifications import Notifications
from database.DataBase import DataBase
from Utils.Helpers import Helpers
from Logic.Shop import Shop
from Logic.Quest import Quest
from Logic.Tokens import Tokens
import json
from datetime import datetime
from Logic.EventSlots import EventSlots
from Server.Login.LoginFailedMessage import LoginFailedMessage
from Server.Home.BattleBan import BattleBan
from Logic.MCbyLkPrtctrd.MilestonesClaimHelpByLkPrtctrd import MilestonesClaimHelpByLkPrtctrd as LkPrtctrd
from Logic.MCbyLkPrtctrd.MilestonesClaimSupplyByLkPrtctrd import MilestonesClaimSupplyByLkPrtctrd as Supply
from Utils.Fingerprint import Fingerprint
from Files.CsvLogic.Characters import Characters
from Files.CsvLogic.Skins import Skins
from Files.CsvLogic.Cards import Cards
class OwnHomeDataMessage(Writer):

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 24101
        self.player = player
        self.timestamp = int(datetime.timestamp(datetime.now()))

    def encode(self):
        DataBase.loadAccount(self)

        self.writeVint(0)
        self.writeVint(self.timestamp)  # Timestamp

        self.writeVint(self.player.trophies)  # Player Trophies
        self.writeVint(self.player.highest_trophies)  # Player Max Reached Trophies
        self.writeVint(self.player.highest_trophies)
        self.writeVint(self.player.Troproad)
        self.writeVint(self.player.player_experience)  # Player exp
        #DataBase.replaceValue(self, "Troproad", 1)
        self.writeScId(28, self.player.profile_icon)  # Player Icon ID
        self.writeScId(43, self.player.name_color)  # Player Name Color ID

        self.writeVint(0)  # array

        # Selected Skins array
        self.writeVint(1)
        self.writeVint(29)
        self.writeVint(self.player.skin_id)  # skinID

        # Unlocked Skins array
#        self.writeVint(365)
#        for i in range(365):
#            self.writeScId(29, int(i))

        self.writeVint(len(self.player.UnlockedSkins))
        for i in self.player.UnlockedSkins:
            if self.player.UnlockedSkins[str(i)]==1:
                self.writeScId(29, int(i))
            else:
                self.writeScId(29, 0)

        self.writeVint(0)  #New Item State

        self.writeVint(0) # ?
        self.writeVint(self.player.highest_trophies) # Highest Road Icon
        self.writeVint(1)
        self.writeVint(1)

        self.writeBoolean(False)  # "token limit reached message" if true

        self.writeVint(self.player.tokensdoubler)  # Token doubler ammount
        
        self.writeVint(60)  # Season End Timer
        self.writeVint(90)  # HZ
        self.writeVint(Helpers().NEWBPTIME) # Brawl Pass Timer

        self.writeVint(0)
        self.writeBoolean(False)
        self.writeBoolean(False)

        self.writeByte(4)  # related to shop token doubler

        for x in range(3):
            self.writeVint(2)

        self.writeVint(0) #name cost
        self.writeVint(0) #timer

        # Shop Array
        Shop.EncodeShopOffers(self)
        # Shop Array End

        # Tokens Array
        Tokens.EncodeTokens(self)
        # Tokens Array End

        self.writeVint(self.player.tickets)  # Tickets
        self.writeVint(1)

        self.writeScId(16, self.player.brawler_id)  # Selected Brawler

        self.writeString(self.player.Region)  # Location
        self.writeString(f"{self.player.ccc}")  # Supported Content Creator

		# Animation ID
        self.writeVint(2) #a dudka
        self.writeInt(4)
        self.writeLkPrtctrdInt(self.player.bet)
        self.writeInt(3)
        self.writeLkPrtctrdInt(self.player.betTok)

        self.writeVint(0)  # array
        
        LkPrtctrd.BrawlPassEncode(self, self.client, self.player)
        LkPrtctrd.BrawlPassEncodeOld(self, self.client, self.player)
        
        self.writeVint(1)
        self.writeVint(1)
        self.writeVint(1)

        Quest.EncodeQuest(self) #Quest Logic
        
        self.writeBoolean(True) # Emojis Boolean
        self.writeVint(len(self.player.emotes_id))
        for emotes_id in self.player.emotes_id:
            if self.player.UnlockedPins[str(emotes_id)]==1:
            	self.writeScId(52, emotes_id)
            	self.writeVint(1)
            	self.writeVint(1)
            	self.writeVint(1)
            else:
            	self.writeScId(52, 0)
            	self.writeVint(1)
            	self.writeVint(1)
            	self.writeVint(1)

        self.writeVint(2019049)

        self.writeVint(100)
        self.writeVint(10)

        for item in Shop.boxes:
            self.writeVint(item['Cost'])
            self.writeVint(item['Multiplier'])

        self.writeVint(Shop.token_doubler['Cost'])
        self.writeVint(Shop.token_doubler['Amount'])

        self.writeVint(500)
        self.writeVint(50)
        self.writeVint(999900)

        self.writeVint(0)  # array
        events = EventSlots.loadEvents(self)
        count = len(events)
        self.writeVint(count+1)
        
        #self.writeVint(7)  # Event slot count
        for i in range(count+1):
            self.writeVint(i)

        # Logic Events
        EventSlots.offset(self)

        self.writeVint(0)  # array

        # Logic Shop
        self.writeVint(8)
        for i in [20, 35, 75, 140, 290, 480, 800, 1250]:
            self.writeVint(i)

        self.writeVint(8)
        for i in [1, 2, 3, 4, 5, 10, 15, 20]:
            self.writeVint(i)

        self.writeVint(3)
        for i in [10, 30, 80]:  # Tickets price
            self.writeVint(i)

        self.writeVint(3)
        for i in [6, 20, 60]:  # Tickets amount
            self.writeVint(i)

        self.writeVint(1)#GOLD PACK #1
        self.writeVint(Shop.gold['Cost'])#GOLD PACK cOST #1

        self.writeVint(1)#GOLD PACK #1
        self.writeVint(Shop.gold['Amount'])#GOLD PACK aMMO #1
        
            
        self.writeVint(0)  # array
        self.writeVint(200)  # Max Tokens
        self.writeVint(20)  # Plus Tokens
        self.writeVint(60) #time
        self.writeVint(10)
        self.writeVint(5)
        self.writeVint(6)
        self.writeVint(50)
        self.writeVint(120)
        self.writeBoolean(True)  # Box boolean

        self.writeVint(1)  # Unknown Array
        self.writeScId(16, 39)
        self.writeInt(99999)
        self.writeInt(99999)

        self.writeVint(4)  # Menu Theme
        self.writeInt(1) #array
        #import random;self.player.theme = random.choice([LkPrtctrd for LkPrtctrd in range(15)])
        self.writeInt(41000000 + self.player.theme)  # Theme ID
        
        with open('config.json') as f:
            config = json.load(f)
        
        self.writeInt(14)  # DoubleTokens Event ID
        self.writeInt(1 if config.get("DoubleTokensEvent", False) else 0)
        
        self.writeInt(21) #Looking For Team State
        self.writeInt(1) #True or False
        
        self.writeInt(31) # Gold rush event
        self.writeInt(0) #True or False

        self.writeVint(0)  # array
        self.writeVint(0)  # array

        self.writeInt(self.player.high_id)
        self.writeInt(self.player.low_id)

        self.writeVint(2 + self.player.vip + self.player.vip + Notifications.GetNotifCount(self))  # array
        self.writeVint(81) #// FreeTextNotification
        self.writeInt(1) #// Notification Index
        self.writeBoolean(False) #// Read
        self.writeInt(0) # Time Ago
        self.writeString(f"Добро пожаловать на наш приватный сервер OWN BRAWL!\n<c3>Админы:</c> @ZoxDev\n<c3>Бот:</c> @ownbrawlbot")
        self.writeVint(1)#new notif
         
        

        if self.player.vip == 1:
            self.writeVint(94) #// SkinNotification
            self.writeInt(22801) #// Notification Index
            self.writeBoolean(self.player.notifRead) #// Read
            self.writeInt(0) # Time Ago
            self.writeString(f"Спасибо что покупаете OWN Premium :)")
            self.writeVint(29000000 + 206)
        
        if self.player.vip == 1:
            self.writeVint(89) #// GemNotification
            self.writeInt(22802) #// Notification Index
            self.writeBoolean(self.player.notifRead2) #// Read
            self.writeInt(0) # Time Ago
            self.writeString(f"Спасибо что покупаете OWN Premium :)")
            self.writeVint(1)
            self.writeVint(360)

            """
    << Notification IDs List >>
    
    99 = Трофейная лига
    94 = Скин
    93 = Боец
    92 = Очки силы для бойца
    91 = Билеты (Not use)
    90 = Custom Message
    89 = Кристалы
    88 = Удвоитель
    85 = Списание кристалов
    75 = Испытание
    ScId 72, 52 = Значек
    71 = Жетоны для бп
    
    """
        for index, notification in self.player.notifications.items():
            if notification['ID'] == 1:
                self.writeVint(94)  # SkinNotification
                self.writeInt(int(index))  # Notification Index
                self.writeBoolean(notification['Read'])  # Read
                self.writeInt(self.timestamp - notification['Timer'])  # Time Ago
                self.writeString(notification['Desc'])
                self.writeVint(29000000 + notification['SkinID'])
            if notification['ID'] == 2:
                self.writeVint(93)  # BrawlerNotification
                self.writeInt(int(index))  # Notification Index
                self.writeBoolean(notification['Read'])  # Read
                self.writeInt(self.timestamp - notification['Timer'])  # Time Ago
                self.writeString(notification['Desc'])
                self.writeVint(1)
                self.writeVint(16000000 + notification['BrawlerID'])
            if notification['ID'] == 3:
                self.writeVint(89)  # // GemNotification
                self.writeInt(int(index))  # // Notification Index
                self.writeBoolean(notification['Read'])  # // Read
                self.writeInt(self.timestamp - notification['Timer'])  # Time Ago
                self.writeString(notification['Desc'])
                self.writeVint(1)
                self.writeVint(notification['Gems'])
            if notification['ID'] == 4:
                self.writeVint(79)
                self.writeInt(int(index))
                self.writeBoolean(notification['Read'])
                self.writeInt(self.timestamp - notification['Timer'])
                self.writeString("Сброс сезона")
                opened_brawlers_count = sum(self.player.UnlockedBrawlers.values())
                self.writeVint(opened_brawlers_count)
                total_starpoints = 0
                for brawler_id, is_unlocked in self.player.UnlockedBrawlers.items():
                    if is_unlocked == 1:
                        brawlers_trophies = self.player.brawlers_trophies.get(brawler_id, 0)
                        if brawlers_trophies > 500:
                            trophy_loss = int(brawlers_trophies * 0.3)
                            new_trophies = brawlers_trophies - trophy_loss
                            if new_trophies < 500:
                                new_trophies = 500
                                trophy_loss = brawlers_trophies - 500  # Потерянные трофеи = разница
                            actual_loss = trophy_loss
                            star_points_gained = actual_loss
                        else:
                            trophy_loss = 0
                            actual_loss = 0
                            star_points_gained = 0
                            new_trophies = brawlers_trophies
                        total_starpoints += star_points_gained
                        self.writeVint(16000000 + int(brawler_id))
                        self.writeVint(brawlers_trophies)  # Показываем сколько осталось трофеев
                        self.writeVint(actual_loss)  # Отображаем сколько было потеряно
                        self.writeVint(star_points_gained)
            if notification['ID'] == 5:
                self.writeVint(81)  # SkinNotification
                self.writeInt(int(index))  # Notification Index
                self.writeBoolean(notification['Read'])  # Read
                self.writeInt(self.timestamp - notification['Timer'])  # Time Ago
                self.writeString(notification['Desc'])
                self.writeVint(1)

        self.writeVint(83) # Notification ID
        self.writeInt(0) # Notification Index 
        self.writeBoolean(True) # Notification Read
        self.writeInt(0) # Notification Time Ago
        self.writeString("ZoxDev") # Notification Text 1
        self.writeInt(0)
        self.writeString("Добро пожаловать в Speed Brawl!") # Notification Text 2
        self.writeInt(0)
        self.writeString("Поддержи наш проект купив гемы/випку!\nТакже заходи в наш тгк - @SpeedBrawlnw") # Notification Text 3
        self.writeInt(0)
        self.writeString("ТЕЛЕГРАМ")
        self.writeString("/b2d704b22b95a4d70f66e89da867a64b")
        self.writeString('3a35620676c1d08d12086257a5ae03eb612452d8')
        self.writeString("brawlstars://extlink?page=https%3A%2F%2Ft.me%2Fspeedbrawlnw")
        self.writeVint(3473)
		
        self.writeVint(0)
        self.writeBoolean(False)

        self.writeVint(0)
        self.writeVint(0)

        self.writeVint(self.player.high_id)  # High Id
        self.writeVint(self.player.low_id)  # Low Id

        self.writeVint(0)
        self.writeVint(0)

        self.writeVint(0)
        self.writeVint(0)

        if self.player.name == "VBC26":
            self.writeString("VBC26")  # Player Name
            self.writeVint(0)
        else:
            if self.player.vip == 1:
                self.writeString(f"{self.player.name}")  # Player Name
            else:
                self.writeString(f"{self.player.name}")  # Player Name
            self.writeVint(1)

        self.writeInt(0)

        self.writeVint(8)

        # Unlocked Brawlers & Resources array
        self.writeVint(len(self.player.card_unlock_id) + 4)  # count

        index = 0
        for unlock_id in self.player.card_unlock_id:
            self.writeScId(23, unlock_id)
            try:
                self.writeVint(self.player.UnlockedBrawlers[str(index)])
            except:
                self.writeVint(1)
            index += 1

        self.writeVint(5)  # csv id
        self.writeVint(1)  # resource id
        self.writeVint(0)  # resource amount
        
        self.writeVint(5)  # csv id
        self.writeVint(8)  # resource id
        self.writeVint(self.player.gold)  # resource amount
        
        self.writeVint(5)  # csv id
        self.writeVint(9)  # resource id
        self.writeVint(0)  # resource amount

        self.writeVint(5)  # csv id
        self.writeVint(10)  # resource id
        self.writeVint(self.player.starpoints)  # resource amount
        

        # Brawlers Trophies array
        self.writeVint(len(self.player.brawlers_trophies))  # brawlers count
        for brawler_id, trophies in self.player.brawlers_trophies.items():
                self.writeScId(16, int(brawler_id))
                self.writeVint(self.player.brawlers_trophies[f"{int(brawler_id)}"])

        # Brawlers Trophies for Rank array
        self.writeVint(len(self.player.brawlers_trophies))  # brawlers count
        for brawler_id, trophies in self.player.brawlers_trophies.items():
                self.writeScId(16, int(brawler_id))
                self.writeVint(self.player.brawlers_trophies[f"{int(brawler_id)}"])

        self.writeVint(0)  # array

        # Brawlers Upgrade Points array
        self.writeVint(len(self.player.brawlerPoints))  # brawlers count
        for brawler_id, trophies in self.player.brawlerPoints.items():
                self.writeScId(16, int(brawler_id))
                self.writeVint(self.player.brawlerPoints[f"{int(brawler_id)}"])

        # Brawlers Power Level array
        self.writeVint(len(self.player.brawlerPowerLevel))  # brawlers count
        for brawler_id, trophies in self.player.brawlerPowerLevel.items():
                self.writeScId(16, int(brawler_id))
                self.writeVint(self.player.brawlerPowerLevel[f"{int(brawler_id)}"])

        # Gadgets and Star Powers array
        self.writeVint(len(self.player.StarPowerUnlocked))
        for brawler_id, trophies in self.player.StarPowerUnlocked.items():
                self.writeScId(23, int(brawler_id))
                self.writeVint(self.player.StarPowerUnlocked[f"{int(brawler_id)}"])
                
        # "new" Brawler Tag array
        self.writeVint(len(self.player.UnlockedBrawlers))  # brawlers count
        for brawler_id, trophies in self.player.Brawler_newTag.items():
                self.writeScId(16, int(brawler_id))
                self.writeVint(self.player.Brawler_newTag[str(brawler_id)])

        self.writeVint(self.player.gems)  # Player Gems
        self.writeVint(self.player.gems)
        self.writeVint(1) # Отвечает за поиск комманды!!!
        if self.player.player_experience < 40:
            self.writeVint(0) # Tips Related
        else:
            self.writeVint(self.player.player_experience) # Tips Related
        self.writeVint(0) # Cumulative Purchased Gems
        self.writeVint(0) # Battles Count
        self.writeVint(0) # Win Count
        self.writeVint(0) # Lose Count
        self.writeVint(0) # Win/Loose Streak
        self.writeVint(0) # Npc Win Count
        self.writeVint(0) # Npc Lose Count
        self.writeVint(2) # Tutorial State
        self.writeVint(1585502369) # Current Time
        DataBase.replaceValue(self, 'online', 2)
        config = open('config.json', 'r')
        content = config.read()
        settings = json.loads(content)
        if self.player.gold < 0:
            self.player.gold = 0
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.player.gems < 0:
            self.player.gems = 0
            DataBase.replaceValue(self, 'gems', self.player.gems)
        if self.player.vip == 0:
            if self.player.low_id in settings['vips']:
                DataBase.replaceValue(self, 'vip', 1)
        if self.player.low_id in settings['banID']:
            update_url = 'https://t.me/zoxdev'
            self.player.err_code = 11
            LoginFailedMessage(self.client, self.player, 'Ваш аккаунт заблокирован!\nЕсли это ошибка - @ZoXDev').send()
        BattleBan(self.client, self.player)
        if self.player.BPTOKEN >= 53000:
            Supply(self.client, self.player, "BOXLkPrtctrd", {"BoxDID": 12}).send()
            self.player.BPTOKEN = 52500
            DataBase.replaceValue(self, "BPTOKEN", self.player.BPTOKEN)