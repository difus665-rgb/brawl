from Logic.Notifications import Notifications
from database.DataBase import DataBase
from Logic.LogicBuy import LogicBuy
from Server.Login.LoginFailedMessage import LoginFailedMessage

from Utils.Reader import BSMessageReader
from Logic.MCbyLkPrtctrd.MilestonesClaimSupplyByLkPrtctrd import MilestonesClaimSupplyByLkPrtctrd


class LogicViewNotificationCommand(BSMessageReader):
    def __init__(self, client, player, initial_bytes, id, k, bp, id2=0):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.a = self.read_Vint()
        self.b = self.read_Vint()
        self.c = self.read_Vint()
        self.d = self.read_Vint()
        self.notif = self.read_Vint()

        self.notifData = Notifications.GetNotifByIndex(self, self.notif)
        try:
            self.notifID = self.notifData['ID']
        except:
            "Ignore"

    def process(self):
        # VIP Notifications
        if self.notif == 22801:
            MilestonesClaimSupplyByLkPrtctrd(self.client, self.player, "BPLkPrtctrd",
                                             {"Character": [0, 5], "Skin": [0, 11], "Type": 9, "Amount": 1, "Road": 0,
                                              "Season": 0, "Level": -2}).send()
            self.player.notifRead = True
            DataBase.replaceValue(self, 'notifRead', self.player.notifRead)
        if self.notif == 22802:
            MilestonesClaimSupplyByLkPrtctrd(self.client, self.player, "BPLkPrtctrd",
                                             {"Character": [0, 0], "Skin": [0, 0], "Type": 8, "Amount": 360, "Road": 0,
                                              "Season": 0, "Level": -2}).send()
            self.player.notifRead2 = True
            DataBase.replaceValue(self, 'notifRead2', self.player.notifRead)

        # Notifications
        try:
            if not self.notifData['Read']:
                if self.notifID == 1:
                    MilestonesClaimSupplyByLkPrtctrd(self.client, self.player, "BPLkPrtctrd",
                                                     {"Character": [0, self.notifData['BrawlerID']],
                                                      "Skin": [0, self.notifData['SkinID']], "Type": 9, "Amount": 1,
                                                      "Road": 0,
                                                      "Season": 0, "Level": -2}).send()
                    Notifications.UpdateNotifData(self, self.notif)

                if self.notifID == 2:
                    MilestonesClaimSupplyByLkPrtctrd(self.client, self.player, "BPLkPrtctrd",
                                                     {"Character": [0, self.notifData['BrawlerID']],
                                                      "Skin": [0, 0], "Type": 1, "Amount": 1,
                                                      "Road": 0,
                                                      "Season": 0, "Level": -2}).send()
                    Notifications.UpdateNotifData(self, self.notif)

                if self.notifID == 3:
                    MilestonesClaimSupplyByLkPrtctrd(self.client, self.player, "BPLkPrtctrd",
                                                     {"Character": [0, 0], "Skin": [0, 0], "Type": 8,
                                                      "Amount": self.notifData['Gems'], "Road": 0,
                                                      "Season": 0, "Level": -2}).send()
                    Notifications.UpdateNotifData(self, self.notif)
                if self.notifID == 4:
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
                            self.player.brawlers_trophies[brawler_id] = new_trophies
                    self.player.starpoints += total_starpoints
                    DataBase.replaceValue(self, 'brawlersTrophies', self.player.brawlers_trophies)
                    DataBase.replaceValue(self, 'starpoints', self.player.starpoints)
                    Notifications.UpdateNotifData(self, self.notif)
                    self.player.err_code = 1
                    LoginFailedMessage(self.client, self.player, 'Сброс сезона Успешен! Пожалуйста, перезайдите в игру!').send()
        except:
            "Ignore"