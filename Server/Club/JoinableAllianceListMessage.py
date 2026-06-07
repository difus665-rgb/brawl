from Utils.Writer import Writer
from database.DataBase import DataBase
from mysql.connector import Error

class JoinableAllianceListMessage(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.id = 24304
        self.player = player

    def encode(self):
        try:
            # Подсчитываем количество клубов и получаем их ID
            conn = DataBase.get_connection()
            if not conn:
                print("[ERROR] Failed to connect to database")
                self.writeVint(0)  # Количество клубов
                return
            try:
                cur = conn.cursor()
                cur.execute("SELECT clubID FROM clubs")
                club_list = [row[0] for row in cur.fetchall()]
                self.AllianceCount = len(club_list)
                print(f"[DEBUG] Counted {self.AllianceCount} clubs")
            except Error as e:
                print(f"[ERROR] MySQL error in CountClub: {e}")
                self.writeVint(0)
                return
            finally:
                cur.close()
                conn.close()

            # Кодируем количество клубов
            self.writeVint(self.AllianceCount)

            # Кодируем данные каждого клуба
            for club_id in club_list:
                club_data = DataBase.loadClub(self, club_id)
                if club_data:
                    self.writeInt(0)                     # ClubHighID
                    self.writeInt(club_id)               # ClubLowID
                    self.writeString(self.clubName)      # Club name

                    self.writeVint(8)                    # BadgeID type
                    self.writeVint(self.clubbadgeID)     # Club badge number

                    self.writeVint(self.clubtype)        # Club type

                    self.writeVint(self.clubmembercount) # Member count

                    self.writeVint(self.clubtrophies)    # Trophies total
                    self.writeVint(self.clubtrophiesneeded)  # Trophies needed
                    self.writeVint(0)                    # Unknown

                    self.writeString(self.clubregion)    # Region
                    self.writeVint(self.clubmembercount) # Members online (упрощённо)
                    self.writeVint(self.clubfriendlyfamily)  # Family friendly
                else:
                    print(f"[WARNING] Failed to load club with ID {club_id}")
        except Exception as e:
            print(f"[ERROR] Error in JoinableAllianceListMessage: {e}")
            self.writeVint(0)  # Количество клубов