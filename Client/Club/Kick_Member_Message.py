from Utils.Reader import BSMessageReader
from database.DataBase import DataBase
from Server.Club.MyAllianceMessage import MyAllianceMessage
from Server.Club.AllianceChatServer import AllianceChatServer
from Server.Club.KickMemberOK import AllianceKickMemberOK


class Kick_Member_Message(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.read_int()  # Не используется, возможно, HighID
        self.lowID = self.read_int()  # ID игрока, которого исключаем
        self.reason = self.read_string()  # Причина исключения

    def process(self):
        # Загружаем данные исключаемого игрока
        account = DataBase.loadbyID(self, self.lowID)
        if not account:
            return  # Игрок не найден, можно добавить логирование или ошибку

        # Проверяем, что текущий игрок имеет право исключать (например, роль 2 или 3)
        player_data = DataBase.loadbyID(self, self.player.low_id)
        if player_data and player_data[12] not in [2, 3]:  # clubRole: 2 (вице-президент), 3 (президент)
            return  # Нет прав, можно отправить ошибку

        # Удаляем игрока из клуба
        DataBase.AddMember(self, account[11], self.lowID, account[2], 2)  # account[11] — clubID, account[2] — имя

        # Обновляем clubID и clubRole исключаемого игрока
        DataBase.replaceOtherValue(self, self.lowID, "clubID", 0)
        DataBase.replaceOtherValue(self, self.lowID, "clubRole", 0)

        # Добавляем сообщение в чат клуба
        DataBase.Addmsg(self, self.player.club_low_id, 4, 1, self.lowID, self.player.name, self.player.club_role, 1)

        # Отправляем подтверждение исключения
        AllianceKickMemberOK(self.client, self.player).send()

        # Обновляем данные клуба и отправляем сообщение
        DataBase.loadClub(self, self.player.club_low_id)
        MyAllianceMessage(self.client, self.player, self.player.club_low_id).send()