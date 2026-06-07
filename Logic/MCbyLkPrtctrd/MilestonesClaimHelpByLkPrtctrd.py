from random import randint as rint
from json import load as Lyney
from json import loads as Lyneys
from Utils.Writer import Writer
import json
from database.DataBase import DataBase

class MilestonesClaimHelpByLkPrtctrd(Writer):
    def __init__(self):
        # self.client = client  
        pass

    def GetAmountOfLevel(self, Level, Levels, Rewards):
        # Возвращает награду для указанного уровня
        for LkPrtctrd in range(len(Levels)):
            if Levels[LkPrtctrd] == Level:
                return Rewards[LkPrtctrd]
        return 0  # Если уровень не найден

    def GetAmountOfBox(self, boxdid):
        # Возвращает случайное количество для боксов
        boxes = [10, 11, 12]
        amts = [rint(9, 30), rint(250, 600), rint(35, 100)]
        for LkPrtctrd in range(len(boxes)):
            if boxes[LkPrtctrd] == boxdid:
                return amts[LkPrtctrd]
        return 0

    def GTFor(self, T, B):
        return range(T, B)

    def TighnariConvert(self, Tighnari):
        try:
            result = Lyneys(Tighnari.replace("\'", "\""))
            print(f"Converted JSON: {result}")
            return result
        except Exception as e:
            print(f"JSON parse error: {e}, input: {Tighnari}")  # Отладка
            return Tighnari

    def GetForm(self, Tighnari):
        try:
            tf = Lyneys(Tighnari.freepass)
        except:
            tf = Tighnari.freepass
        try:
            bf = Lyneys(Tighnari.buypass)
        except:
            bf = Tighnari.buypass
        bne = [LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd().GTFor(0, 30)]
        bwo = [LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd().GTFor(30, 62)]
        bex1 = [LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd().GTFor(62, 94)]
        bex2 = [LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd().GTFor(94, 101)]

        self.writeByte(1)

        bf0 = 0
        for LkPrtctrd in range(len(bne)):
            if bne[LkPrtctrd] in bf:
                LLkPrtctrd = 4
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd *= 2
                bf0 += LLkPrtctrd
        bf3 = 0
        for LkPrtctrd in range(len(bwo)):
            if bwo[LkPrtctrd] in bf:
                LLkPrtctrd = 1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd *= 2
                bf3 += LLkPrtctrd
        bf6 = 0
        for LkPrtctrd in range(len(bex1)):
            if bex1[LkPrtctrd] in bf:
                LLkPrtctrd = 1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd *= 2
                bf6 += LLkPrtctrd
        bf7 = 0
        for LkPrtctrd in range(len(bex2)):
            if bex2[LkPrtctrd] in bf:
                LLkPrtctrd = 1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd *= 2
                bf7 += LLkPrtctrd

        self.writeLkPrtctrdInt(bf0)
        self.writeLkPrtctrdInt(bf3)
        self.writeLkPrtctrdInt(bf6)
        self.writeLkPrtctrdInt(bf7)

        self.writeByte(1)

        # Free pass (freepass)
        tf1 = 0
        for LkPrtctrd in range(len(bne)):
            if bne[LkPrtctrd] in tf:
                LLkPrtctrd = 4
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd *= 2
                tf1 += LLkPrtctrd
        tf4 = 0
        for LkPrtctrd in range(len(bwo)):
            if bwo[LkPrtctrd] in tf:
                LLkPrtctrd = 1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd *= 2
                tf4 += LLkPrtctrd
        tf7 = 0
        for LkPrtctrd in range(len(bex1)):
            if bex1[LkPrtctrd] in tf:
                LLkPrtctrd = 1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd *= 2
                tf7 += LLkPrtctrd
        tf8 = 0
        for LkPrtctrd in range(len(bex2)):
            if bex2[LkPrtctrd] in tf:
                LLkPrtctrd = 1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd *= 2
                tf8 += LLkPrtctrd

        self.writeLkPrtctrdInt(tf1)
        self.writeLkPrtctrdInt(tf4)
        self.writeLkPrtctrdInt(tf7)
        self.writeLkPrtctrdInt(tf8)
        
    def GetFormOld(self,Tighnari):
        try:
            tf = Lyneys(Tighnari.freepassold)
        except:
            tf = Tighnari.freepassold
        try:
            bf = Lyneys(Tighnari.buypassold)
        except:
            bf = Tighnari.buypassold
        bne=[LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd().GTFor(0,30)]
        bwo=[LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd().GTFor(30,62)]
        bre=[LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd().GTFor(62,71)]
        self.writeByte(1)
        bf0 = 0
        for LkPrtctrd in range(len(bne)):
            if bne[LkPrtctrd] in bf:
                LLkPrtctrd=4
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd*=2
                bf0+=LLkPrtctrd
        bf3 = 0
        for LkPrtctrd in range(len(bwo)):
            if bwo[LkPrtctrd] in bf:
                LLkPrtctrd=1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd*=2
                bf3+=LLkPrtctrd
        self.writeLkPrtctrdInt(bf0)
        self.writeLkPrtctrdInt(bf3)
        self.writeLkPrtctrdInt(0)
        self.writeLkPrtctrdInt(0)
        self.writeByte(1)
        tf1 = 0
        for LkPrtctrd in range(len(bne)):
            if bne[LkPrtctrd] in tf:
                LLkPrtctrd=4
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd*=2
                tf1+=LLkPrtctrd
        tf4 = 0
        for LkPrtctrd in range(len(bwo)):
            if bwo[LkPrtctrd] in tf:
                LLkPrtctrd=1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd*=2
                tf4+=LLkPrtctrd
        tf7 = 0
        for LkPrtctrd in range(len(bre)):
            if bre[LkPrtctrd] in tf:
                LLkPrtctrd=1
                for LkPrtctrdd in range(LkPrtctrd):
                    LLkPrtctrd*=2
                tf7+=LLkPrtctrd
        self.writeLkPrtctrdInt(tf1)
        self.writeLkPrtctrdInt(tf4)
        self.writeLkPrtctrdInt(tf7)
        self.writeLkPrtctrdInt(0)
        

    def GetVipExist(self, lowid):
        with open("config.json", 'r') as f:
            config = json.load(f)
            return True if lowid in config["buybp"] else False
            
    def GetVipExistOld(self, lowid):
        with open("config.json", 'r') as f:
            config = json.load(f)
            return True if lowid in config["buybpold"] else False

    def BrawlPassEncode(self,client,userdata):
        config = DataBase.get_bp_config()
        self.writeVint(2)
        for i in [LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd.GTFor(self,1,2) if True]:
            self.writeVint(config['BPSEASON']) #BPSEASON
            self.writeVint(self.player.BPTOKEN)
            self.writeBoolean(MilestonesClaimHelpByLkPrtctrd().GetVipExist(userdata.low_id))
            self.writeVint(30)    
            MilestonesClaimHelpByLkPrtctrd.GetForm(self,self.player)
            
    def BrawlPassEncodeOld(self,client,userdata):
        config = DataBase.get_bp_config()
        for i in [LkPrtctrd for LkPrtctrd in MilestonesClaimHelpByLkPrtctrd.GTFor(self,1,2) if True]:
            self.writeVint(config['BPSEASONOLD']) #BPSEASONOLD
            self.writeVint(self.player.BPXP)
            self.writeBoolean(MilestonesClaimHelpByLkPrtctrd().GetVipExistOld(userdata.low_id))
            self.writeVint(30)    
            MilestonesClaimHelpByLkPrtctrd.GetFormOld(self,self.player)
            