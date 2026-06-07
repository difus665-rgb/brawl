from Utils.Writer import Writer
from database.DataBase import DataBase
import json

class AllianceDataMessage(Writer):
    def __init__(self, client, player, clubHighID, clubLowID):
        super().__init__(client)
        self.id = 24301
        self.player = player
        self.clubHighID = clubHighID
        self.clubLowID = clubLowID

    def encode(self):
        # Проверяем, есть ли клуб
        if self.clubLowID > 0:
            club_data = DataBase.loadClub(self, self.clubLowID)
            if club_data:
                online = True if self.player.club_low_id == self.clubLowID else False
                self.writeBoolean(online)
                
                # ClubID
                self.writeInt(0)  # Club high ID
                self.writeInt(self.clubLowID)   # Club low ID
                self.writeString(self.clubName)  # Club name
                
                # Badge
                self.writeVint(8)
                self.writeVint(self.clubbadgeID)    # Club badge ID
                
                # Club settings
                self.writeVint(self.clubtype)    # Club type [1 = open, 2 = invite only, 3 = closed]
                members = json.loads(club_data[9]).get("members", {})
                self.writeVint(len(members))    # Club members count
                
                # Club trophies
                self.writeVint(self.clubtrophies)  # Club total trophies
                self.writeVint(self.clubtrophiesneeded)    # Club required trophies
                
                # Club Info
                self.writeVint(0)
                self.writeString("BY")  # Region
                self.writeVint(0)
                self.writeVint(self.clubfriendlyfamily)    # Family friendly status
                self.writeString(self.clubdescription)  # Description
                
                # Members list
                self.writeVint(len(members))    # Members list count
                for member_id, member_name in members.items():
                    try:
                        member_id_int = int(member_id)
                        DataBase.GetMemberData(self, member_id_int)
                        self.writeInt(0)               # High ID
                        self.writeInt(member_id_int)   # Low ID
                        self.writeVint(self.plrrole)   # Player club role
                        self.writeVint(self.plrtrophies)  # Trophies
                        self.writeVint(self.plrstatus)    # Player status
                        self.writeVint(0)
                        self.writeVint(0)
                        if self.plrvip:
                            self.writeString(f'{self.plrname}')
                        else:
                            self.writeString(self.plrname)
                        self.writeVint(self.plrexperience)
                        self.writeVint(28000000 + self.plricon)
                        self.writeVint(43000000 + self.plrnamecolor)
                        if self.plrvip:
                            self.writeVint(self.plrnamecolor)
                        else:
                            self.writeVint(0)
                    except ValueError:
                        print(f"[ВНИМАНИЕ] Неверный ID члена: {member_id}, пропускаем")
            else:
                # Клуб не найден
                self.writeBoolean(False)
                self.writeInt(0)  # Club high ID
                self.writeInt(0)  # Club low ID
        else:
            # Игрок не в клубе
            self.writeBoolean(False)
            self.writeInt(0)  # Club high ID
            self.writeInt(0)  # Club low ID