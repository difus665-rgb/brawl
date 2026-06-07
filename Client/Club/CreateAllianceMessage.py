from Server.Club.MyAllianceMessage import MyAllianceMessage
from Server.Club.AllianceJoinOkMessage import AllianceJoinOkMessage
from database.DataBase import DataBase
from Utils.Reader import BSMessageReader
from Server.Login.LoginFailedMessage import LoginFailedMessage

class CreateAllianceMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.clubName = self.read_string()
        self.clubdescription = self.read_string()
        
        self.BadgeIdentifier = self.read_Vint()
        self.clubbadgeID = self.read_Vint()
        
        self.RegionIdentifier = self.read_Vint()
        self.clubregionID = self.read_Vint()
        
        self.clubtype = self.read_Vint()
        self.clubtrophiesneeded = self.read_Vint()
        self.clubfriendlyfamily = self.read_Vint()

    def process(self):
        try:
            # Проверяем, состоит ли игрок в клубе
            if self.player.club_low_id != 0:
                DataBase.AddMember(self, self.player.club_low_id, self.player.low_id, self.player.name, 2)
                self.player.club_low_id = 0
                self.player.club_role = 0
                DataBase.replaceValue(self, 'clubID', 0)
                DataBase.replaceValue(self, 'clubRole', 0)

            # Устанавливаем параметры клуба
            self.player.clubName = self.clubName
            self.player.clubdescription = self.clubdescription
            self.player.clubbadgeID = self.clubbadgeID
            self.player.clubregionID = self.clubregionID
            self.player.clubtype = self.clubtype
            self.player.clubtrophiesneeded = self.clubtrophiesneeded
            self.player.clubfriendlyfamily = self.clubfriendlyfamily
            
            # Создаём клуб
            clubid = DataBase.createClub(self)
            if clubid:
                self.player.club_low_id = clubid
                self.player.club_role = 2
                DataBase.replaceValue(self, 'clubID', clubid)
                DataBase.replaceValue(self, 'clubRole', 2)
                AllianceJoinOkMessage(self.client, self.player).send()
                MyAllianceMessage(self.client, self.player, clubid).send()
            else:
                self.player.club_low_id = 0
                self.player.club_role = 0
                DataBase.replaceValue(self, 'clubID', 0)
                DataBase.replaceValue(self, 'clubRole', 0)
                MyAllianceMessage(self.client, self.player, 0).send()
        except Exception as e:
            self.player.club_low_id = 0
            self.player.club_role = 0
            DataBase.replaceValue(self, 'clubID', 0)
            DataBase.replaceValue(self, 'clubRole', 0)
            MyAllianceMessage(self.client, self.player, 0).send()