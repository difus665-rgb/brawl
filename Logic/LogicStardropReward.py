from database.DataBase import DataBase
import random
from Utils.Writer import Writer

class LogicStardropReward(Writer):
    def __init__(self, client, player, data=None):
        super().__init__(client)
        self.id = 24111
        self.player = player
        self.data_provided = data is not None
        self.mult1 = data if self.data_provided else {"Road": 0, "Season": 0, "Level": 0}
        self.all_brawlers = [i for i in range(40) if i not in [0, 1, 2, 3, 7, 8, 9, 14, 22, 27, 30, 33]]
        self.all_skins = [
            29, 15, 2, 109, 27, 139, 111, 137, 152, 75,
            25, 58, 98, 28, 92, 158, 130, 88, 93, 104, 
            132, 108, 45, 125, 117, 11, 126, 131, 20, 110,
            52, 159, 79, 44, 163, 91, 160, 99, 30, 128,
            71, 59, 26, 68, 147, 50, 96, 118, 94, 49, 95
        ]
        self.brawlers_abilities = [
            {"StarPowerCard": [76, 135], "GadgetCard": [255, 288], "Brawler": 0},
            {"StarPowerCard": [77, 138], "GadgetCard": [273], "Brawler": 1},
            {"StarPowerCard": [78, 137], "GadgetCard": [272], "Brawler": 2},
            {"StarPowerCard": [79, 150], "GadgetCard": [245], "Brawler": 3},
            {"StarPowerCard": [80, 156], "GadgetCard": [246], "Brawler": 4},
            {"StarPowerCard": [81, 151], "GadgetCard": [247], "Brawler": 5},
            {"StarPowerCard": [82, 158], "GadgetCard": [250, 293], "Brawler": 6},
            {"StarPowerCard": [83, 149], "GadgetCard": [251, 295], "Brawler": 7},
            {"StarPowerCard": [84, 136], "GadgetCard": [249], "Brawler": 8},
            {"StarPowerCard": [85, 155], "GadgetCard": [258, 294], "Brawler": 9},
            {"StarPowerCard": [86, 140], "GadgetCard": [264, 292], "Brawler": 10},
            {"StarPowerCard": [87, 154], "GadgetCard": [265, 290], "Brawler": 11},
            {"StarPowerCard": [88, 143], "GadgetCard": [243, 286], "Brawler": 12},
            {"StarPowerCard": [89, 144], "GadgetCard": [267], "Brawler": 13},
            {"StarPowerCard": [90, 148], "GadgetCard": [263, 289], "Brawler": 14},
            {"StarPowerCard": [91, 152], "GadgetCard": [268, 291], "Brawler": 15},
            {"StarPowerCard": [92, 139], "GadgetCard": [257], "Brawler": 16},
            {"StarPowerCard": [93, 160], "GadgetCard": [266], "Brawler": 17},
            {"StarPowerCard": [94, 157], "GadgetCard": [260], "Brawler": 18},
            {"StarPowerCard": [99, 142], "GadgetCard": [248, 287], "Brawler": 19},
            {"StarPowerCard": [104, 153], "GadgetCard": [261], "Brawler": 20},
            {"StarPowerCard": [109, 159], "GadgetCard": [252], "Brawler": 21},
            {"StarPowerCard": [114, 161], "GadgetCard": [253], "Brawler": 22},
            {"StarPowerCard": [119, 141], "GadgetCard": [276], "Brawler": 23},
            {"StarPowerCard": [124, 147], "GadgetCard": [242], "Brawler": 24},
            {"StarPowerCard": [129, 145], "GadgetCard": [262], "Brawler": 25},
            {"StarPowerCard": [134, 146], "GadgetCard": [275], "Brawler": 26},
            {"StarPowerCard": [168, 181], "GadgetCard": [259], "Brawler": 27},
            {"StarPowerCard": [186, 187], "GadgetCard": [270], "Brawler": 28},
            {"StarPowerCard": [192, 193], "GadgetCard": [271], "Brawler": 29},
            {"StarPowerCard": [198, 199], "GadgetCard": [274], "Brawler": 30},
            {"StarPowerCard": [204, 205], "GadgetCard": [269], "Brawler": 31},
            {"StarPowerCard": [210, 211], "GadgetCard": [254], "Brawler": 32},
            {"StarPowerCard": [222, 223], "GadgetCard": [256], "Brawler": 34},
            {"StarPowerCard": [228, 229], "GadgetCard": [277], "Brawler": 35},
            {"StarPowerCard": [234, 235], "GadgetCard": [278], "Brawler": 36},
            {"StarPowerCard": [240, 241], "GadgetCard": [244], "Brawler": 37},
            {"StarPowerCard": [283, 284], "GadgetCard": [285], "Brawler": 38},
            {"StarPowerCard": [300, 301], "GadgetCard": [302], "Brawler": 39}
        ]
        self.reward_types = [
            {'type': 'gold', 'amounts': [50, 100, 250, 500, 1000], 'weights': [0.60, 0.25, 0.10, 0.04, 0.01], 'id': 7},
            {'type': 'gems', 'amounts': [3, 7, 15, 49, 79], 'weights': [0.60, 0.25, 0.10, 0.04, 0.01], 'id': 8},
            {'type': 'brawler', 'amounts': [1], 'weights': [1.0], 'id': 1},
            {'type': 'skin', 'amounts': [1], 'weights': [1.0], 'id': 9},
            {'type': 'powerpoints', 'amounts': [25, 50, 150, 300, 500], 'weights': [0.60, 0.25, 0.10, 0.04, 0.01], 'id': 6},
            {'type': 'ability', 'amounts': [1], 'weights': [1.0], 'id': 4},
            {'type': 'doublers', 'amounts': [200, 300, 500, 1000, 1500], 'weights': [0.60, 0.25, 0.10, 0.04, 0.01], 'id': 2}
        ]
        self.type_weights = [0.50, 0.01, 0.03, 0.05, 0.20, 0.01, 0.20]

    def encode(self):
        self.writeVint(203)
        self.writeVint(0)
        self.writeVint(1)
        self.writeVint(100)
        self.writeVint(1)

        brawler_id = 0
        skin_id = 0
        ability_id = 0
        reward = random.choices(self.reward_types, weights=self.type_weights, k=1)[0]
        amount = random.choices(reward['amounts'], weights=reward['weights'], k=1)[0]

        if reward['type'] == 'brawler':
            available_brawlers = [
                b_id for b_id in self.all_brawlers 
                if self.player.UnlockedBrawlers.get(str(b_id), 0) == 0
            ]
            if not available_brawlers:
                reward = self.reward_types[0]
                amount = random.choices(reward['amounts'], weights=reward['weights'], k=1)[0]
            else:
                brawler_id = random.choice(available_brawlers)
                self.player.UnlockedBrawlers[str(brawler_id)] = 1
                DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
        elif reward['type'] == 'skin':
            available_skins = [
                b_id for b_id in self.all_skins 
                if self.player.UnlockedSkins.get(str(b_id), 0) == 0
            ]
            if not available_skins:
                reward = self.reward_types[0]
                amount = random.choices(reward['amounts'], weights=reward['weights'], k=1)[0]
            else:
                skin_id = random.choice(available_skins)
                self.player.UnlockedSkins[str(skin_id)] = 1
                DataBase.replaceValue(self, 'UnlockedSkins', self.player.UnlockedSkins)
        elif reward['type'] == 'powerpoints':
            unlocked_brawlers = [
                int(b_id) for b_id, status in self.player.UnlockedBrawlers.items() 
                if status == 1 and int(b_id) in self.all_brawlers
            ]
            if not unlocked_brawlers:
                reward = self.reward_types[0]
                amount = random.choices(reward['amounts'], weights=reward['weights'], k=1)[0]
            else:
                brawler_id = random.choice(unlocked_brawlers)
                current = self.player.brawlerPoints.get(str(brawler_id), 0)
                new_value = min(current + amount, 1410)
                amount = new_value - current
                if amount <= 0:
                    reward = self.reward_types[0]
                    amount = random.choices(reward['amounts'], weights=reward['weights'], k=1)[0]
                else:
                    self.player.brawlerPoints[str(brawler_id)] = new_value
                    DataBase.replaceValue(self, 'brawlerPoints', self.player.brawlerPoints)
        elif reward['type'] == 'ability':
            eligible_abilities = []
            for brawler_data in self.brawlers_abilities:
                brawler_id = brawler_data["Brawler"]
                if self.player.UnlockedBrawlers.get(str(brawler_id), 0) != 1:
                    continue
                brawler_level = self.player.brawlerPowerLevel.get(str(brawler_id), 1)
                if brawler_level >= 6:
                    for gadget_id in brawler_data["GadgetCard"]:
                        if str(gadget_id) not in self.player.StarPowerUnlocked or self.player.StarPowerUnlocked[str(gadget_id)] == 0:
                            eligible_abilities.append(('gadget', gadget_id, brawler_id))
                if brawler_level >= 8:
                    for sp_id in brawler_data["StarPowerCard"]:
                        if str(sp_id) not in self.player.StarPowerUnlocked or self.player.StarPowerUnlocked[str(sp_id)] == 0:
                            eligible_abilities.append(('starpower', sp_id, brawler_id))
            if not eligible_abilities:
                reward = random.choice([self.reward_types[0], self.reward_types[5]])
                amount = random.choices(reward['amounts'], weights=reward['weights'], k=1)[0]
            else:
                ability_type, ability_id, brawler_id = random.choice(eligible_abilities)
                self.player.StarPowerUnlocked[str(ability_id)] = 1
                DataBase.replaceValue(self, 'StarPowerUnlocked', self.player.StarPowerUnlocked)
        elif reward['type'] == 'gold':
            self.player.gold += amount
            DataBase.replaceValue(self, 'gold', self.player.gold)
        elif reward['type'] == 'gems':
            self.player.gems += amount
            DataBase.replaceValue(self, 'gems', self.player.gems)
        elif reward['type'] == 'doublers':
            self.player.tokensdoubler += amount
            DataBase.replaceValue(self, 'Tokens_Doubler', self.player.tokensdoubler)

        self.writeVint(amount)
        if reward['type'] == 'brawler':
            self.writeScId(16, brawler_id)
            self.writeScId(reward['id'], 0)
            self.writeVint(0) # CsvID 29
            self.writeVint(0) # CsvID 52
            self.writeVint(0) # CsvID 23
        elif reward['type'] == 'skin':
            self.writeVint(0)
            self.writeVint(reward['id'])
            self.writeScId(29, skin_id)
            self.writeVint(0) # CsvID 52
            self.writeVint(0) # CsvID 23
            self.writeVint(0) # ????
        elif reward['type'] == 'ability':
            self.writeScId(16, brawler_id)
            self.writeVint(reward['id'])
            self.writeVint(0) # CsvID 29
            self.writeVint(0) # CsvID 52
            self.writeScId(23, ability_id) # ????
        elif reward['type'] == 'powerpoints':
            self.writeScId(16, brawler_id)
            self.writeVint(reward['id'])
            self.writeVint(0) # CsvID 29
            self.writeVint(0) # CsvID 52
            self.writeVint(0) # CsvID 23
            self.writeVint(0) # ????
        else:
            self.writeScId(0, reward['id'])
            self.writeVint(0) # CsvID 29
            self.writeVint(0) # CsvID 52
            self.writeVint(0) # CsvID 23
            self.writeVint(0) # ????
        if self.data_provided:
            self.writeBoolean(False)
            self.writeVint(self.mult1["Road"])
            self.writeVint(self.mult1["Level"] + 2)
            self.writeVint(self.mult1["Season"])
            self.writeVint(1)
        self.writeVint(0)
        self.writeVint(0)
        self.writeVint(0)
        self.writeVint(0)