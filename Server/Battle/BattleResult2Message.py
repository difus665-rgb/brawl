from Utils.Writer import Writer
from database.DataBase import DataBase
import random
import json
import sys
import os
import sqlite3
import pytz
from Logic.Quest import Quest
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class BattleResult2Message(Writer):
    def __init__(self, client, player, result):
        super().__init__(client)
        self.id = 23456
        self.player = player
        self.result = result
        self.bot_names = self.load_bot_names()
        self.config = self.load_config()
        self.double_tokens = self.config.get("DoubleTokensEvent", False)
        self.double_trophies = self.config.get("DoubleTrophiesEvent", False)
        self.log_battle_ends = self.config.get("LogBattleEnds", False)

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
    
    def load_config(self):
        try:
            with open("config.json", "r") as config_file:
                return json.load(config_file)
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            return {}

    def encode(self):
        brawler_trophies = self.player.brawlers_trophies[str(self.player.brawler_id)]
        win_val = 0
        lose_val = 0
        tokenGained = 0
        tropGained = 0
        if 0 <= brawler_trophies <= 49:
            win_val = 8
            lose_val = 0
        elif 50 <= brawler_trophies <= 99:
            win_val = 8
            lose_val = -1
        elif 100 <= brawler_trophies <= 199:
            win_val = 8
            lose_val = -2
        elif 200 <= brawler_trophies <= 299:
            win_val = 8
            lose_val = -3
        elif 300 <= brawler_trophies <= 399:
            win_val = 8
            lose_val = -4
        elif 400 <= brawler_trophies <= 499:
            win_val = 8
            lose_val = -5
        elif 500 <= brawler_trophies <= 599:
            win_val = 8
            lose_val = -6
        elif 600 <= brawler_trophies <= 699:
            win_val = 8
            lose_val = -7
        elif 700 <= brawler_trophies <= 799:
            win_val = 8
            lose_val = -8
        elif 800 <= brawler_trophies <= 899:
            win_val = 7
            lose_val = -9
        elif 900 <= brawler_trophies <= 999:
            win_val = 6
            lose_val = -10
        elif 1000 <= brawler_trophies <= 1099:
            win_val = 5
            lose_val = -11
        elif 1100 <= brawler_trophies <= 1199:
            win_val = 4
            lose_val = -12
        elif 1200 <= brawler_trophies <= 1250:
            win_val = 3
            lose_val = -12
        elif 1251 <= brawler_trophies:
            win_val = 3
            lose_val = -12

        if self.player.battle_result == 1:
            tropGained = lose_val
            tokenGained = min(10, self.player.player_tokens)
        elif self.player.battle_result == 0:
            tropGained = win_val
            tokenGained = min(20, self.player.player_tokens)

        # Расчёт токенов
        tokenevent = tokenGained if self.double_tokens else 0
        doubledtokens = min(tokenGained, self.player.tokensdoubler)  # Удвоители добавляют бонус, равный tokenGained
        totaltokens = tokenGained + tokenevent  + doubledtokens
        totaltokens2 = totaltokens  # Итоговые токены с удвоителями
        remainingtokens = self.player.tokensdoubler - doubledtokens  # Оставшиеся удвоители

        # Обновление ресурсов игрока
        self.player.player_tokens -= tokenGained
        if self.player.player_tokens < 0:
            self.player.player_tokens = 0
        self.player.tokensdoubler = remainingtokens
        if self.player.tokensdoubler < 0:
            self.player.tokensdoubler = 0
        self.player.BPTOKEN += totaltokens2

        # Сохранение в базе данных
        DataBase.replaceValue(self, 'Player_Tokens', self.player.player_tokens)
        DataBase.replaceValue(self, 'Tokens_Doubler', self.player.tokensdoubler)
        DataBase.replaceValue(self, 'BPTOKEN', self.player.BPTOKEN)

        # Запись данных в поток
        self.writeVint(1)  # Battle End Game Mode
        self.writeVint(self.player.battle_result)  # Result
        self.writeVint(tokenGained)  # Tokens Gained (итоговые токены)
        if tropGained >= 0:
            if self.player.vip == 1:
                tropGained += 15
                self.writeVint(tropGained * 2 if self.double_trophies else tropGained)  # Trophies Result
            else:
                self.writeVint(tropGained * 2 if self.double_trophies else tropGained)  # Trophies Result
        else:
            self.writeVint(-65 - tropGained)  # Trophies Result
        self.writeVint(0)  # Unknown (Power Play Related)
        self.writeVint(doubledtokens)  # Doubled Tokens (использованные удвоители)
        self.writeVint(tokenevent)  # Double Token Event
        self.writeVint(remainingtokens)  # Token Doubler Remaining
        self.writeVint(0)  # Big Game/Robo Rumble Time
        self.writeVint(0)  # Unknown (Championship Related)
        self.writeVint(0)  # Championship Level Passed
        self.writeVint(0)  # Challenge Reward Type (0 = Star Points, 1 = Star Tokens)
        self.writeVint(0)  # Challenge Reward Amount
        self.writeVint(0)  # Championship Losses Left
        self.writeVint(0)  # Championship Maximum Losses
        self.writeVint(0)  # Coin Shower Event
        if tropGained > 0:
            if self.player.vip == 1:
                self.writeVint(15)  # Underdog Trophies
            else:
                self.writeVint(0)  # Underdog Trophies
        else:
            self.writeVint(0)  # Underdog Trophies
        self.writeVint(16)  # 48-с Spectator, 32-Friendly, 16-Normal Victory, (-16)-Power Play
        self.writeVint(-64)  # Championship Challenge Type
        self.writeVint(0)  # Championship Cleared and Beta Quests

        # Players Array
        self.writeVint(6)  # Battle End Screen Players
        self.writeVint(1)  # Team and Star Player Type
        self.writeScId(16, self.player.brawler_id)  # Player Brawler
        self.writeScId(29, self.player.skin_id)  # Player Skin
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)])  # Your Brawler Trophies
        self.writeVint(0)  # Unknown (Power Play Related)
        self.writeVint(self.player.brawlerPowerLevel.get(str(self.player.brawler_id), 0) + 1)  # Brawler Power Level
        self.writeBoolean(True)  # HighID and LowID Array
        self.writeInt(0)  # HighID
        self.writeInt(self.player.low_id)  # LowID
        self.writeString(self.player.name)  # Your Name
        self.writeVint(self.player.player_experience)  # Player Experience Level
        self.writeVint(28000000 + self.player.profile_icon)  # Player Profile Icon
        self.writeVint(43000000 + self.player.name_color)  # Player Name Color
        if self.player.vip == 1:
            self.writeVint(43000000 + self.player.name_color)  # Player Name Color
        else:
            self.writeVint(0)  # Player Name Color

        # Bot 1
        if self.player.team == 0:
            if self.player.bot1_team == 0:
                self.writeVint(0)  # Team and Star Player Type
            else:
                self.writeVint(2)  # Team and Star Player Type
        else:
            if self.player.bot1_team == 0:
                self.writeVint(2)  # Team and Star Player Type
            else:
                self.writeVint(0)  # Team and Star Player Type
        self.writeScId(16, self.player.bot1)  # Bot 1 Brawler
        self.writeVint(0)  # Bot 1 Skin
        self.writeVint(max(0, self.player.brawlers_trophies[str(self.player.brawler_id)] + random.randint(-25, 25)))  # Brawler Trophies
        self.writeVint(0)  # Unknown (Power Play Related)
        self.writeVint(random.randint(6, 10))  # Brawler Power Level
        self.writeBoolean(False)  # HighID and LowID Array
        self.writeString(self.bot_names[0])  # Bot 1 Name
        self.writeVint(0)  # Player Experience Level
        self.writeVint(28000000)  # Player Profile Icon
        self.writeVint(43000000)  # Player Name Color
        self.writeVint(43000000)  # Player Name Color

        # Bot 2
        if self.player.team == 0:
            if self.player.bot2_team == 0:
                self.writeVint(0)  # Team and Star Player Type
            else:
                self.writeVint(2)  # Team and Star Player Type
        else:
            if self.player.bot2_team == 0:
                self.writeVint(2)  # Team and Star Player Type
            else:
                self.writeVint(0)  # Team and Star Player Type
        self.writeScId(16, self.player.bot2)  # Bot 2 Brawler
        self.writeVint(0)  # Bot 2 Skin
        self.writeVint(max(0, self.player.brawlers_trophies[str(self.player.brawler_id)] + random.randint(-25, 25)))  # Brawler Trophies
        self.writeVint(0)  # Unknown (Power Play Related)
        self.writeVint(random.randint(6, 10))  # Brawler Power Level
        self.writeBoolean(False)  # HighID and LowID Array
        self.writeString(self.bot_names[1])  # Bot 2 Name
        self.writeVint(0)  # Player Experience Level
        self.writeVint(28000000)  # Player Profile Icon
        self.writeVint(43000000)  # Player Name Color
        self.writeVint(43000000)  # Player Name Color

        # Bot 3
        if self.player.team == 0:
            if self.player.bot3_team == 0:
                self.writeVint(0)  # Team and Star Player Type
            else:
                self.writeVint(2)  # Team and Star Player Type
        else:
            if self.player.bot3_team == 0:
                self.writeVint(2)  # Team and Star Player Type
            else:
                self.writeVint(0)  # Team and Star Player Type
        self.writeScId(16, self.player.bot3)  # Bot 3 Brawler
        self.writeVint(0)  # Bot 3 Skin
        self.writeVint(max(0, self.player.brawlers_trophies[str(self.player.brawler_id)] + random.randint(-25, 25)))  # Brawler Trophies
        self.writeVint(0)  # Unknown (Power Play Related)
        self.writeVint(random.randint(6, 10))  # Brawler Power Level
        self.writeBoolean(False)  # HighID and LowID Array
        self.writeString(self.bot_names[2])  # Bot 3 Name
        self.writeVint(0)  # Player Experience Level
        self.writeVint(28000000)  # Player Profile Icon
        self.writeVint(43000000)  # Player Name Color
        self.writeVint(43000000)  # Player Name Color

        # Bot 4
        if self.player.team == 0:
            if self.player.bot4_team == 0:
                self.writeVint(0)  # Team and Star Player Type
            else:
                self.writeVint(2)  # Team and Star Player Type
        else:
            if self.player.bot4_team == 0:
                self.writeVint(2)  # Team and Star Player Type
            else:
                self.writeVint(0)  # Team and Star Player Type
        self.writeScId(16, self.player.bot4)  # Bot 4 Brawler
        self.writeVint(0)  # Bot 4 Skin
        self.writeVint(max(0, self.player.brawlers_trophies[str(self.player.brawler_id)] + random.randint(-25, 25)))  # Brawler Trophies
        self.writeVint(0)  # Unknown (Power Play Related)
        self.writeVint(random.randint(6, 10))  # Brawler Power Level
        self.writeBoolean(False)  # HighID and LowID Array
        self.writeString(self.bot_names[3])  # Bot 4 Name
        self.writeVint(0)  # Player Experience Level
        self.writeVint(28000000)  # Player Profile Icon
        self.writeVint(43000000)  # Player Name Color
        self.writeVint(43000000)  # Player Name Color

        # Bot 5
        if self.player.team == 0:
            if self.player.bot5_team == 0:
                self.writeVint(0)  # Team and Star Player Type
            else:
                self.writeVint(2)  # Team and Star Player Type
        else:
            if self.player.bot5_team == 0:
                self.writeVint(2)  # Team and Star Player Type
            else:
                self.writeVint(0)  # Team and Star Player Type
        self.writeScId(16, self.player.bot5)  # Bot 5 Brawler
        self.writeVint(0)  # Bot 5 Skin
        self.writeVint(max(0, self.player.brawlers_trophies[str(self.player.brawler_id)] + random.randint(-25, 25)))  # Brawler Trophies
        self.writeVint(0)  # Unknown (Power Play Related)
        self.writeVint(random.randint(6, 10))  # Brawler Power Level
        self.writeBoolean(False)  # HighID and LowID Array
        self.writeString(self.bot_names[4])  # Bot 5 Name
        self.writeVint(0)  # Player Experience Level
        self.writeVint(28000000)  # Player Profile Icon
        self.writeVint(43000000)  # Player Name Color
        self.writeVint(43000000)  # Player Name Color

        # Experience Array
        self.writeVint(2)  # Count
        self.writeVint(0)  # Normal Experience ID
        self.writeVint(10)  # Normal Experience Gained
        self.writeVint(8)  # Star Player Experience ID
        self.writeVint(0)  # Star Player Experience Gained

        # Rank Up and Level Up Bonus Array
        self.writeVint(0)  # Count

        # Trophies and Experience Bars Array
        self.writeVint(2)  # Count
        self.writeVint(1)  # Trophies Bar Milestone ID
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)])  # Brawler Trophies
        self.writeVint(self.player.brawlers_trophies[str(self.player.brawler_id)])  # Brawler Trophies for Rank
        self.writeVint(5)  # Experience Bar Milestone ID
        self.writeVint(self.player.player_experience)  # Player Experience
        self.writeVint(0)  # Player Experience for Level

        self.writeScId(28, 0)  # Player Profile Icon (Unused since 2017)
        self.writeBoolean(False)  # Play Again
        
        Quest.EncodeQuest(self) #Quest Logic
                    
        if self.player.name != "VBC26":
            if self.double_trophies:
                self.player.bet = tropGained * 2
            else:
                self.player.bet = tropGained
            if self.double_tokens:
                self.player.betTok = totaltokens2
            else:
                self.player.betTok = totaltokens2
            self.player.brawlers_trophies[str(self.player.brawler_id)] += self.player.bet
            DataBase.replaceValue(self, 'brawlersTrophies', self.player.brawlers_trophies)
            self.player.trioWINS = self.player.trioWINS + 1
            DataBase.replaceValue(self, 'trioWINS', self.player.trioWINS)
            self.player.player_experience += 10
            DataBase.replaceValue(self, 'playerExp', self.player.player_experience)

            if self.log_battle_ends:
                if not os.path.exists('JSON'):
                    os.makedirs('JSON')
                msk_time = datetime.now(pytz.timezone('Europe/Moscow'))
                timestamp = msk_time.strftime("%Y-%m-%d %H:%M:%S") + " MSK"
                battle_log = {
                    "low_id": self.player.low_id,
                    "timestamp": timestamp,
                    "battle_result": self.player.battle_result,
                    "trophy_change": self.player.bet
                }
                log_entry = json.dumps(battle_log)
                with open('JSON/battleends.json', 'a') as f:
                    f.write(log_entry + '\n')