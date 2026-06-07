from Utils.Writer import Writer
from database.DataBase import DataBase
import random
import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class BattleResultDebacleMessage(Writer):
    def __init__(self, client, player, result):
        super().__init__(client)
        self.id = 23456
        self.player = player
        self.result = result
        self.bot_names = self.load_bot_names()  # Загружаем имена ботов из БД

    def load_bot_names(self):
        bot_names = []
        try:
            conn = sqlite3.connect("database/Player/plr.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM plrs")
            bot_names = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            print(f"Ошибка при загрузке имен ботов: {e}")
        while len(bot_names) < 5:
            bot_names.append(f"Bot{len(bot_names) + 1}")
        random.shuffle(bot_names)
        return bot_names

    def encode(self):
        brawler_trophies = self.player.brawlers_trophies[str(self.player.brawler_id)]
        win_val = 0
        lose_val = 0
        tokenGained = 0
        tropGained = 0
        if 0 <= brawler_trophies <= 49:
            win_val = 8
            lose_val = 0
        else:
            if 50 <= brawler_trophies <= 99:
                win_val = 8
                lose_val = -1
            if 100 <= brawler_trophies <= 199:
                win_val = 8
                lose_val = -2
            if 200 <= brawler_trophies <= 299:
                win_val = 8
                lose_val = -3
            if 300 <= brawler_trophies <= 399:
                win_val = 8
                lose_val = -4
            if 400 <= brawler_trophies <= 499:
                win_val = 8
                lose_val = -5
            if 500 <= brawler_trophies <= 599:
                win_val = 8
                lose_val = -6
            if 600 <= brawler_trophies <= 699:
                win_val = 8
                lose_val = -7
            if 700 <= brawler_trophies <= 799:
                win_val = 8
                lose_val = -8
            if 800 <= brawler_trophies <= 899:
                win_val = 7
                lose_val = -9
            if 900 <= brawler_trophies <= 999:
                win_val = 6
                lose_val = -10
            if 1000 <= brawler_trophies <= 1099:
                win_val = 5
                lose_val = -11
            if 1100 <= brawler_trophies <= 1199:
                win_val = 4
                lose_val = -12
            if 1200 <= brawler_trophies <= 1250:
                win_val = 3
                lose_val = -12
            if 1251 <= brawler_trophies:
                win_val = 3
                lose_val = -12
        if self.player.battle_result == 1:
            tropGained = lose_val
            tokenGained = 25
        elif self.player.battle_result == 0:
            tropGained = win_val
            tokenGained = 50
            self.player.debacle = self.player.debacle + 1
            
        self.writeVint(6) # Battle End Game Mode 
        self.writeVint(self.player.battle_result) # Result 
        self.writeVint(self.player.battle_result) # Tokens Gained
        self.writeVint(0) # Tokens Gained
        self.writeVint(0) # Unknown (Power Play Related)
        if self.player.vip == 1:
            self.writeVint(300) # Doubled Tokens
            tokenGained += 300
        else:
            self.writeVint(0) # Doubled Tokens
        self.writeVint(0) # Double Token Event
        self.writeVint(0) # Token Doubler Remaining
        self.writeVint(0) # Big Game/Robo Rumble Time
        self.writeVint(0) # Unknown (Championship Related)
        self.writeVint(0) # Championship Level Passed
        self.writeVint(0) # Challenge Reward Type (0 = Star Points, 1 = Star Tokens)
        self.writeVint(0) # Challenge Reward Ammount
        self.writeVint(0) # Championship Losses Left
        self.writeVint(0) # Championship Maximun Losses
        self.writeVint(0) # Coin Shower Event
        if tropGained > 0:
            if self.player.vip == 1:
                self.writeVint(15) # Underdog Trophies
            else:
                self.writeVint(0) # Underdog Trophies
        else:
            self.writeVint(0) # Underdog Trophies
        self.writeVint(16)# 48-спектатор 32-дружеская 16-обычная победа (-16) - повер плей
        self.writeVint(-64) # Championship Challenge Type
        self.writeVint(0) # Championship Cleared and Beta Quests
            
        # Players Array
        self.writeVint(self.player.players) # Battle End Screen Players
        
        self.writeVint(1) # Team and Star Player Type
        self.writeScId(16, self.player.brawler_id) # Player Brawler
        self.writeScId(29, self.player.skin_id) # Player Skin
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)]) # Your Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(self.player.brawlerPowerLevel.get(str(self.player.brawler_id), 0) + 1)
        self.writeBoolean(True) # HighID and LowID Array
        self.writeInt(0) # HighID
        self.writeInt(self.player.low_id) # LowID
        self.writeString(self.player.name) # Your Name
        self.writeVint(self.player.player_experience) # Player Experience Level
        self.writeVint(28000000 + self.player.profile_icon) # Player Profile Icon
        self.writeVint(43000000 + self.player.name_color) # Player Name Color
        if self.player.vip == 1:
            self.writeVint(43000000 + self.player.name_color) # Player Name Color
        else:
            self.writeVint(0) # Player Name Color
            
        if self.player.team == 0:
            if self.player.bot1_team == 0:
                self.writeVint(0) # Team and Star Player Type
            else:
                self.writeVint(2) # Team and Star Player Type
        else:
            if self.player.bot1_team == 0:
                self.writeVint(2) # Team and Star Player Type
            else:
                self.writeVint(0) # Team and Star Player Type
        self.writeScId(16, self.player.bot1) # Bot 1 Brawler
        self.writeVint(0) # Bot 1 Skin
        self.writeVint(max(0, self.player.brawlers_trophies[str(self.player.brawler_id)] + random.randint(-25, 25))) # Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(random.randint(6, 10)) # Brawler Power Level
        self.writeBoolean(False) # HighID and LowID Array
        self.writeString(self.bot_names[0]) # Bot 1 Name
        self.writeVint(0) # Player Experience Level
        self.writeVint(28000000) # Player Profile Icon
        self.writeVint(43000000) # Player Name Color
        self.writeVint(43000000) # Player Name Color
            
        if self.player.team == 0:
            if self.player.bot2_team == 0:
                self.writeVint(0) # Team and Star Player Type
            else:
                self.writeVint(2) # Team and Star Player Type
        else:
            if self.player.bot2_team == 0:
                self.writeVint(2) # Team and Star Player Type
            else:
                self.writeVint(0) # Team and Star Player Type
        self.writeScId(16, self.player.bot2) # Bot 2 Brawler
        self.writeVint(0) # Bot 2 Skin
        self.writeVint(max(0, self.player.brawlers_trophies[str(self.player.brawler_id)] + random.randint(-25, 25))) # Brawler Trophies
        self.writeVint(0) # Unknown (Power Play Related)
        self.writeVint(random.randint(6, 10)) # Brawler Power Level
        self.writeBoolean(False) # HighID and LowID Array
        self.writeString(self.bot_names[1]) # Bot 2 Name
        self.writeVint(0) # Player Experience Level
        self.writeVint(28000000) # Player Profile Icon
        self.writeVint(43000000) # Player Name Color
        self.writeVint(43000000) # Player Name Color
        
        # Experience Array
        self.writeVint(2) # Count
        self.writeVint(0) # Normal Experience ID
        self.writeVint(10) # Normal Experience Gained
        self.writeVint(8) # Star Player Experience ID
        self.writeVint(0) # Star Player Experience Gained

        # Rank Up and Level Up Bonus Array
        self.writeVint(0) # Count

        # Trophies and Experience Bars Array
        self.writeVint(2) # Count
        self.writeVint(1) # Trophies Bar Milestone ID
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)]) # Brawler Trophies
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)]) # Brawler Trophies for Rank
        self.writeVint(5) # Experience Bar Milestone ID
        self.writeVint(self.player.player_experience) # Player Experience
        self.writeVint(0) # Player Experience for Level
        
        self.writeVint(1)
        self.writeVint(0)
        self.writeVint(0)
        self.writeVint(1) # Mission Type
        self.writeVint(0) # Current Quest Goal
        self.writeVint(1) # Max Quest Goal
        self.writeVint(100) # Tokens Reward
        self.writeVint(0)
        self.writeVint(0) # Current Level 
        self.writeVint(0) # Max Level
        self.writeVint(1) # Quest Type | 0 = Season Quest, 1 = Daily Quest
        self.writeBoolean(False) # Brawl Pass Exclusive
        self.writeScId(16, 0) # Brawler ID
        self.writeVint(0) # Gamemode ID
        self.writeVint(0)
        
        self.writeScId(28, 0)  # Player Profile Icon (Unused since 2017)
        self.writeBoolean(False)  # Play Again
        if self.player.name != "VBC26":
            self.player.BPTOKEN = self.player.BPTOKEN + tokenGained
            DataBase.replaceValue(self, 'BPTOKEN', self.player.BPTOKEN)
            DataBase.replaceValue(self, 'Debacle', self.player.debacle)
            self.player.player_experience += 10
            DataBase.replaceValue(self, 'playerExp', self.player.player_experience)