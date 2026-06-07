from Utils.Writer import Writer
from random import randint as r
from database.DataBase import DataBase
from Logic.MCbyLkPrtctrd.MilestonesClaimHelpByLkPrtctrd import MilestonesClaimHelpByLkPrtctrd as Lyney 
import random as rnd
from Logic.Commands.Client.LogicBoxDataCommand import LogicBoxDataCommand as BOXES

class MilestonesClaimSupplyByLkPrtctrd(Writer):

    MAX_BRAWLER_POINTS = 1410
    EXCLUDED_BRAWLER_ID = [0, 1, 2, 3, 7, 8, 9, 14, 22, 27, 30]

    def __init__(self, client, player, what, data):
        super().__init__(client)
        self.id = 24111
        self.player = player
        self.id1 = what
        self.mult1 = data
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

    def encode(self):
        self.writeBool = self.writeBoolean
        self.writeVInt = self.writeVint

        if self.id1 == "BOXLkPrtctrd":
            boxtype = self.mult1["BoxDID"]
            money = Lyney().GetAmountOfBox(boxtype)
            moneygive = [money]
            try:
                del self.player.UnlockedBrawlers["48"]
            except KeyError:
                pass
                
            ownedbrs = [int(LkPrtctrd) for LkPrtctrd, x in self.player.UnlockedBrawlers.items() if int(x) == 1 and int(LkPrtctrd) < 40 and self.player.brawlerPoints.get(str(LkPrtctrd), 0) < self.MAX_BRAWLER_POINTS]
            ownedbrsforall = [int(LkPrtctrd) for LkPrtctrd, x in self.player.UnlockedBrawlers.items() if int(x) == 1 and int(LkPrtctrd) < 40]
            allbrswithoutown = [int(LkPrtctrd) for LkPrtctrd in range(40) if LkPrtctrd not in ownedbrsforall and LkPrtctrd != 33 and LkPrtctrd != 48]

            if boxtype == 11:
                ppcount = min(5, len(ownedbrs))
            elif boxtype == 10:
                ppcount = min(2, len(ownedbrs))
            else:
                ppcount = min(3, len(ownedbrs))

            powerpointsgive = []
            pointsgivetable = {
                "10": {"1": 10, "2": 25},
                "11": {"1": 80, "2": 200},
                "12": {"1": 30, "2": 75}
            }
            for _ in range(ppcount):
                if not ownedbrs:
                    break
                brawler = rnd.choice(ownedbrs)
                pointsnow = self.player.brawlerPoints.get(str(brawler), 0)
                pointsgive = rnd.randint(pointsgivetable[str(boxtype)]["1"], pointsgivetable[str(boxtype)]["2"])
                pointsgivefinish = min(pointsgive, self.MAX_BRAWLER_POINTS - pointsnow)
                ownedbrs.remove(brawler)
                if pointsgivefinish > 0:
                    if self.player.brawlerPowerLevel.get(str(brawler), 0) < 9:
                        powerpointsgive.append({"Brawler": brawler, "Points": pointsgivefinish})

            brawler_probabilities = {
                # Редкие бравлеры
                6: 15, 10: 15, 13: 15, 24: 15,
                # Сверхредкие
                19: 10, 18: 10, 25: 10, 34: 10,
                # Эпические
                15: 4, 4: 4, 16: 4, 20: 4, 26: 4, 30: 4,
                # Мифические
                36: 2, 29: 2, 11: 2, 17: 2, 21: 2,
                # Хроматические
                37: 1, 31: 1, 32: 1, 35: 1, 38: 1, 39: 1,
                # Легендарные
                5: 1, 12: 1, 23: 1, 28: 1
            }

            brawler_list = list(brawler_probabilities.keys())
            brawler_weights = list(brawler_probabilities.values())
            
            if boxtype == 10:
                brawler_weights = [weight * 1.2 for weight in brawler_weights]
            elif boxtype == 12:
                brawler_weights = [weight * 2 for weight in brawler_weights]
            elif boxtype == 11:
                brawler_weights = [weight * 1.5 for weight in brawler_weights]
            
            brsgivecount = 5
            brsgive = []
            for _ in range(brsgivecount):
                if not allbrswithoutown:
                    break
                if rnd.random() < 0.131:
                    brawler = rnd.choices(brawler_list, weights=brawler_weights, k=1)[0]
                    if brawler in allbrswithoutown and brawler not in self.EXCLUDED_BRAWLER_ID:
                        allbrswithoutown.remove(brawler)
                        brsgive.append(brawler)
                        
            tokensdoubler = []
            if rnd.random() < 0.2:
                if boxtype == 10:
                    tokensdoubler.append(200)
                elif boxtype == 11:
                    tokensdoubler.append(rnd.randint(200, 400))
                elif boxtype == 12:
                    tokensdoubler.append(rnd.randint(200, 600))
            gems = []
            if rnd.random() < 0.1:
                gems.append(rnd.choice([3, 5, 6, 8, 12]))

            abilitiesgive = []
            ability_probs = {
                10: [0.10, 0.05],  # Small Box
                11: [0.20, 0.10],  # Big Box
                12: [0.30, 0.15]   # Mega Box
            }.get(boxtype, [0.10, 0.05])
            selected_ability_ids = []
            for prob in ability_probs:
                if len(abilitiesgive) >= 2:
                    break
                if rnd.random() >= prob:
                    continue
                eligible_abilities = []
                for brawler_data in self.brawlers_abilities:
                    brawler_id = brawler_data["Brawler"]
                    if self.player.UnlockedBrawlers.get(str(brawler_id), 0) != 1:
                        continue
                    brawler_level = self.player.brawlerPowerLevel.get(str(brawler_id), 1)
                    if brawler_level >= 6:
                        for gadget_id in brawler_data["GadgetCard"]:
                            if (str(gadget_id) not in self.player.StarPowerUnlocked or 
                                self.player.StarPowerUnlocked.get(str(gadget_id), 0) == 0) and gadget_id not in selected_ability_ids:
                                eligible_abilities.append(('gadget', gadget_id, brawler_id))
                    if brawler_level >= 8:
                        for sp_id in brawler_data["StarPowerCard"]:
                            if (str(sp_id) not in self.player.StarPowerUnlocked or 
                                self.player.StarPowerUnlocked.get(str(sp_id), 0) == 0) and sp_id not in selected_ability_ids:
                                eligible_abilities.append(('starpower', sp_id, brawler_id))
                if not eligible_abilities:
                    continue
                ability_type, ability_id, brawler_id = rnd.choice(eligible_abilities)
                abilitiesgive.append({"AbilityID": ability_id, "Brawler": brawler_id})
                selected_ability_ids.append(ability_id)

            if boxtype == 10 and brsgive:
                powerpointsgive = []
                moneygive = []
            # мне надо чтобы при self.count =- 1 вызывалось сново это до тех пор пока не будет self.count = 0 и тогда вызов будет закрыт 
            self.writeVint(203)
            self.writeVint(0)
            self.writeVint(1)
            self.writeVint(boxtype)

            rewardcount = len(moneygive) + len(powerpointsgive) + len(brsgive) + len(abilitiesgive) + len(tokensdoubler) + len(gems)
            self.writeVint(rewardcount)
            
            for x in moneygive:
                self.writeVint(x)
                self.writeBPScId(0, 0)
                self.writeVint(7)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
            for x in powerpointsgive:
                self.writeVint(x["Points"])
                self.writeBPScId(16, x["Brawler"])
                self.writeVint(6)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
            for x in brsgive:
                self.writeVint(1)
                self.writeBPScId(16, x)
                self.writeVint(1)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
            for x in abilitiesgive:
                self.writeVint(1)
                self.writeBPScId(16, x["Brawler"])
                self.writeVint(4)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(23, x["AbilityID"])
                self.writeVint(0)
            for x in tokensdoubler:
                self.writeVint(x)
                self.writeBPScId(0, 0)
                self.writeVint(2)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
            for x in gems:
                self.writeVint(x)
                self.writeBPScId(0, 0)
                self.writeVint(8)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)

            self.writeBool(False)
            try:
                self.writeVint(self.mult1["Road"])
                self.writeVint(self.mult1["Level"] + 2)
                self.writeVint(self.mult1["Season"])
            except KeyError:
                self.writeVint(0)
                self.writeVint(0)
                self.writeVint(0)

            for _ in range(11):
                self.writeVInt(0)

            # Сохранение наград
                for x in moneygive:
                    self.player.gold += x
                    DataBase.replaceValue(self, 'gold', self.player.gold)
                for x in powerpointsgive:
                    if self.player.brawlerPowerLevel.get(str(x["Brawler"]), 0) < 9:
                        self.player.brawlerPoints[str(x["Brawler"])] = min(self.player.brawlerPoints.get(str(x["Brawler"]), 0) + x["Points"], self.MAX_BRAWLER_POINTS)
                        DataBase.replaceValue(self, 'brawlerPoints', self.player.brawlerPoints)
                for x in brsgive:
                    self.player.UnlockedBrawlers[str(x)] = 1
                    DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
                for x in tokensdoubler:
                    self.player.tokensdoubler += x
                    DataBase.replaceValue(self, 'Tokens_Doubler', self.player.tokensdoubler)
                for x in gems:
                    self.player.gems += x
                    DataBase.replaceValue(self, 'gems', self.player.gems)
                for x in abilitiesgive:
                    self.player.StarPowerUnlocked[str(x["AbilityID"])] = 1
                    DataBase.replaceValue(self, 'StarPowerUnlocked', self.player.StarPowerUnlocked)
                return

        if self.id1 == "BPLkPrtctrd":
            self.writeVint(203)
            self.writeVint(0)
            self.writeVint(1)
            try:
                self.writeVint(self.mult1["Box"])
            except KeyError:
                self.writeVint(100)

            if self.mult1["Type"] == 6:
                brawler = self.mult1["Character"][1]
                resbeen = self.player.brawlerPoints.get(str(brawler), 0)
                if resbeen + self.mult1["Amount"] > self.MAX_BRAWLER_POINTS:
                    resnewplus = self.MAX_BRAWLER_POINTS - resbeen
                    resnewmoney = self.mult1["Amount"] - resnewplus
                else:
                    resnewplus = self.mult1["Amount"]
                    resnewmoney = 0
                resnewpp = [resnewplus, resnewmoney * 2]
            elif self.mult1["Type"] == 4:
                brawler = self.mult1["Character"][1]
                ability_id = self.mult1["AbilityID"]
                resnewpp = [1, 0]

            rewardcount = 1
            if self.mult1["Type"] == 6:
                rewardcount = 2 if resnewpp[1] > 0 else 1
            elif self.mult1["Type"] == 9:
                rewardcount = 2 if self.player.UnlockedBrawlers.get(str(self.mult1['Character'][1]), 0) == 0 else 1
            elif self.mult1["Type"] == 11:
                rewardcount = 1 if self.player.UnlockedPins.get(str(self.mult1['Character']), 0) == 0 else 1
            elif self.mult1["Type"] == 4:
                rewardcount = 1

            self.writeVint(rewardcount)
            if self.mult1["Type"] not in [1, 6, 9, 11, 4]:
                self.writeVint(self.mult1["Amount"])
                self.writeBPScId(0, 0)
                self.writeVint(self.mult1["Type"])
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
            elif self.mult1["Type"] == 1:
                self.writeVint(self.mult1["Amount"])
                self.writeBPScId(16, self.mult1["Character"][1])
                self.writeVint(self.mult1["Type"])
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
            elif self.mult1["Type"] == 6:
                self.writeVint(resnewpp[0])
                self.writeBPScId(16, self.mult1["Character"][1])
                self.writeVint(6)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
                if resnewpp[1] > 0:
                    self.writeVint(resnewpp[1])
                    self.writeBPScId(0, 0)
                    self.writeVint(7)
                    self.writeBPScId(0, 0)
                    self.writeBPScId(0, 0)
                    self.writeBPScId(0, 0)
                    self.writeVint(0)
            elif self.mult1["Type"] == 9:
                if rewardcount == 2:
                    self.writeVint(1)
                    self.writeBPScId(16, self.mult1["Character"][1])
                    self.writeVint(1)
                    self.writeBPScId(0, 0)
                    self.writeBPScId(0, 0)
                    self.writeBPScId(0, 0)
                    self.writeVint(0)
                    self.player.UnlockedBrawlers[str(self.mult1["Character"][1])] = 1
                    DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
                self.writeVint(1)
                self.writeBPScId(16, self.mult1["Character"][1])
                self.writeVint(9)
                self.writeBPScId(29, self.mult1["Skin"][1])
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
            elif self.mult1["Type"] == 11:
                self.writeVint(1)
                self.writeVint(0)
                self.writeVint(11)
                self.writeVint(0)
                self.writeBPScId(52, self.mult1["Character"])
                self.writeVint(0)
                self.writeVint(0)
                self.writeVint(0)
                self.writeBoolean(False)
                self.writeVint(0)
                self.writeLogicLong(-1)
            elif self.mult1["Type"] == 4:
                self.writeVint(1)
                self.writeBPScId(16, self.mult1["Character"][1])
                self.writeVint(4)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeBPScId(23, self.mult1["AbilityID"])
                self.writeVint(0)

            self.writeBoolean(False)
            self.writeVint(self.mult1["Road"])
            self.writeVint(self.mult1["Level"] + 2)
            self.writeVint(self.mult1["Season"])
            self.writeVInt(0)
            self.writeVInt(0)
            self.writeVInt(0)
            self.writeVInt(0)
            self.writeVInt(0)

            # Дополнительное сохранение
            if self.mult1["Type"] == 7:
                self.player.gold += self.mult1['Amount']
                DataBase.replaceValue(self, 'gold', self.player.gold)
            elif self.mult1["Type"] == 2:
                self.player.tokensdoubler += self.mult1['Amount']
                DataBase.replaceValue(self, 'Tokens_Doubler', self.player.tokensdoubler)
            elif self.mult1["Type"] == 8:
                self.player.gems += self.mult1['Amount']
                DataBase.replaceValue(self, 'gems', self.player.gems)
            elif self.mult1["Type"] == 6:
                self.player.gold += resnewpp[1]
                DataBase.replaceValue(self, 'gold', self.player.gold)
                if self.player.brawlerPowerLevel.get(str(self.mult1["Character"][1]), 0) < 9:
                    self.player.brawlerPoints[str(self.mult1["Character"][1])] = min(self.player.brawlerPoints.get(str(self.mult1["Character"][1]), 0) + resnewpp[0], self.MAX_BRAWLER_POINTS)
                    DataBase.replaceValue(self, 'brawlerPoints', self.player.brawlerPoints)
            elif self.mult1["Type"] == 1:
                self.player.UnlockedBrawlers[str(self.mult1["Character"][1])] = 1
                DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
            elif self.mult1["Type"] == 11:
                self.player.UnlockedPins[str(self.mult1["Character"])] = 1
                DataBase.replaceValue(self, 'UnlockedPins', self.player.UnlockedPins)
            elif self.mult1["Type"] == 9:
                self.player.UnlockedSkins[str(self.mult1["Skin"][1])] = 1
                DataBase.replaceValue(self, 'UnlockedSkins', self.player.UnlockedSkins)
            elif self.mult1["Type"] == 4:
                self.player.StarPowerUnlocked[str(self.mult1["AbilityID"])] = 1
                DataBase.replaceValue(self, 'StarPowerUnlocked', self.player.StarPowerUnlocked)
            return
            
        if self.id1 == "BPPINS":
            self.writeVint(203)
            self.writeVint(0)
            self.writeVint(1)
            try:
                self.writeVint(self.mult1["Box"])
            except:
                self.writeVint(100)

            notAvailablePins = {328, 329, 330, 331, 332, 333, 334, 335, 361, 362, 363, 364,
            365, 366, 367, 368, 401, 402, 403,404, 405, 406, 526, 441, 444, 440, 446, 442,
            443, 521, 515, 516, 520, 518, 522, 517, 519, 521, 221, 222, 223, 224, 225, 226,
            293, 294, 295, 296, 297, 298, 299, 300, 312, 313, 314, 315, 316, 317, 318, 319,
            320, 321, 336, 337, 338, 339, 340, 341, 342, 343, 348, 349, 350, 351, 352, 353,
            354, 355, 328, 329, 330, 331, 332, 333, 334, 335, 361, 362, 363, 364, 365, 366,
            367, 368, 393, 394, 395, 396, 397, 398, 399, 400, 424, 425, 426, 427, 428, 429,
            430, 455, 456, 457, 507, 508, 509, 510, 511, 512, 513, 514, 523}

            available_pins = []
            for pin_id in range(524):
                if pin_id in notAvailablePins:
                    continue
                if str(pin_id) not in self.player.UnlockedPins or self.player.UnlockedPins[str(pin_id)] == 0:
                    available_pins.append(pin_id)

            pin_count = min(self.mult1["Count"], len(available_pins))
            selected_pins = rnd.sample(available_pins, pin_count) if available_pins else []

            self.writeVint(pin_count)

            for randompin in selected_pins:
                self.writeVint(1)
                self.writeBPScId(0, 0)
                self.writeVint(11)
                self.writeBPScId(0, 0)
                self.writeBPScId(52, randompin)
                self.writeBPScId(0, 0)
                self.writeBPScId(0, 0)
                self.writeVint(0)
                self.player.UnlockedPins[str(randompin)] = 1
                DataBase.replaceValue(self, 'UnlockedPins', self.player.UnlockedPins)

            self.writeBoolean(False)
            self.writeVint(self.mult1["Road"])
            self.writeVint(self.mult1["Level"] + 2)
            self.writeVint(self.mult1["Season"])
            for _ in range(5):
                self.writeVint(0)
                
                
        if self.id1 == "PINS":
            self.writeVint(203)
            self.writeVint(0)
            self.writeVint(1)
            try:
                self.writeVint(self.mult1["Box"])
            except:
                self.writeVint(100)

            notAvailablePins = {328, 329, 330, 331, 332, 333, 334, 335, 361, 362, 363, 364,
            365, 366, 367, 368, 401, 402, 403,404, 405, 406, 526, 441, 444, 440, 446, 442,
            443, 521, 515, 516, 520, 518, 522, 517, 519, 521, 221, 222, 223, 224, 225, 226,
            293, 294, 295, 296, 297, 298, 299, 300, 312, 313, 314, 315, 316, 317, 318, 319,
            320, 321, 336, 337, 338, 339, 340, 341, 342, 343, 348, 349, 350, 351, 352, 353,
            354, 355, 328, 329, 330, 331, 332, 333, 334, 335, 361, 362, 363, 364, 365, 366,
            367, 368, 393, 394, 395, 396, 397, 398, 399, 400, 424, 425, 426, 427, 428, 429,
            430, 455, 456, 457, 507, 508, 509, 510, 511, 512, 513, 514, 523}

            available_pins = []
            for pin_id in range(524):
                if pin_id in notAvailablePins:
                    continue
                if str(pin_id) not in self.player.UnlockedPins or self.player.UnlockedPins[str(pin_id)] == 0:
                    available_pins.append(pin_id)

            pin_count = min(self.mult1["Count"], len(available_pins))
            selected_pins = rnd.sample(available_pins, pin_count) if available_pins else []

            self.writeVint(pin_count)

            for randompin in selected_pins:
                self.writeVint(1)
                self.writeScId(0, 0)
                self.writeVint(11)
                self.writeScId(0, 0)
                self.writeScId(52, randompin)
                self.writeScId(0, 0)
                self.writeScId(0, 0)
                self.writeVint(0)
                self.player.UnlockedPins[str(randompin)] = 1
                DataBase.replaceValue(self, 'UnlockedPins', self.player.UnlockedPins)
                
        self.writeBool(False)
        try:
            self.writeVint(self.mult1["Road"])
            self.writeVint(self.mult1["Level"] + 2)
            self.writeVint(self.mult1["Season"])
        except:
            self.writeVint(0)
            self.writeVint(0)
            self.writeVint(0)