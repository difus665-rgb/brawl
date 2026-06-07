import logging
import json
import random
import time
from database.DataBase import DataBase
from Server.Club.MyAllianceMessage import MyAllianceMessage
from Server.Club.AllianceLeaveOkMessage import AllianceLeaveOkMessage
from Server.Club.AllianceChatServer import AllianceChatServer
from Server.Club.AllianceDataMessage import AllianceDataMessage
from Utils.Reader import BSMessageReader

logger = logging.getLogger(__name__)

class Leave_Message(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client
        self.clubmembercount = 0
        self.plrids = []

    def decode(self):
        pass

    def process(self):
        try:
            # Проверяем, состоит ли игрок в клубе
            if self.player.club_low_id == 0:
                logger.info(f"Игрок {self.player.low_id} не состоит в клубе")
                AllianceLeaveOkMessage(self.client, self.player).send()
                MyAllianceMessage(self.client, self.player, 0).send()
                return

            club_id = self.player.club_low_id
            logger.debug(f"Игрок {self.player.low_id} покидает клуб {club_id}")

            # Загружаем данные клуба
            db = DataBase()
            db.player = self.player
            club_data = db.loadClub(club_id)
            if not club_data:
                logger.error(f"Клуб {club_id} не найден")
                self.player.club_low_id = 0
                self.player.club_role = 0
                DataBase.replaceValue(db, 'clubID', 0)
                DataBase.replaceValue(db, 'clubRole', 0)
                AllianceLeaveOkMessage(self.client, self.player).send()
                MyAllianceMessage(self.client, self.player, 0).send()
                return

            # Переносим атрибуты
            self.clubmembercount = db.clubmembercount
            self.plrids = db.plrids

            # Парсим список участников
            try:
                members = json.loads(club_data[9]).get("members", {})
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка при разборе JSON members для клуба {club_id}: {e}")
                members = {}

            logger.info(f"Клуб {club_id}: {self.clubmembercount} участников")

            is_president = self.player.club_role == 2
            logger.debug(f"Игрок {self.player.low_id} - президент: {is_president}")

            # Выход из клуба
            if self.clubmembercount <= 1:
                # Если игрок последний, удаляем клуб
                logger.info(f"Удаляем клуб {club_id}, так как игрок {self.player.low_id} единственный участник")
                DataBase.AddMember(db, club_id, self.player.low_id, self.player.name, 0)
            else:
                # Удаляем игрока из клуба
                logger.info(f"Игрок {self.player.low_id} покидает клуб {club_id}")
                DataBase.AddMember(db, club_id, self.player.low_id, self.player.name, 2)
                DataBase.Addmsg(db, club_id, 4, 0, self.player.low_id, self.player.name, self.player.club_role, 2)

                # Если игрок - президент, передаем роль
                if is_president:
                    vice_presidents = []
                    veterans = []
                    regular_members = []

                    conn = DataBase.get_connection()
                    if not conn:
                        logger.error("Не удалось подключиться к базе данных")
                        return
                    try:
                        cur = conn.cursor()
                        for player_id_str, player_name in members.items():
                            try:
                                player_id = int(player_id_str)
                                if player_id == self.player.low_id:
                                    continue
                                # Проверяем, существует ли игрок в базе
                                cur.execute("SELECT clubRole, name FROM plrs WHERE lowID=%s", (player_id,))
                                player_data = cur.fetchone()
                                if not player_data:
                                    logger.warning(f"Игрок {player_id} не найден в базе plrs")
                                    continue

                                role = player_data[0]
                                name = player_data[1]

                                if role == 4:
                                    vice_presidents.append({"low_id": player_id, "name": name})
                                elif role == 3:
                                    veterans.append({"low_id": player_id, "name": name})
                                elif role == 1:
                                    regular_members.append({"low_id": player_id, "name": name})
                            except ValueError:
                                logger.warning(f"Неверный ID игрока: {player_id_str}, пропускаем")

                        logger.debug(f"Вице-президенты: {vice_presidents}, Ветераны: {veterans}, Участники: {regular_members}")

                        new_president = None
                        if vice_presidents:
                            new_president = random.choice(vice_presidents)
                            logger.info(f"Передаем роль вице-президенту {new_president['name']} (ID: {new_president['low_id']})")
                        elif veterans:
                            new_president = random.choice(veterans)
                            logger.info(f"Передаем роль ветерану {new_president['name']} (ID: {new_president['low_id']})")
                        elif regular_members:
                            new_president = random.choice(regular_members)
                            logger.info(f"Передаем роль участнику {new_president['name']} (ID: {new_president['low_id']})")

                        if new_president:
                            # Обновляем роль нового президента
                            cur.execute("UPDATE plrs SET clubRole=%s WHERE lowID=%s", (2, new_president['low_id']))
                            DataBase.Addmsg(db, club_id, 4, 0, new_president['low_id'], new_president['name'], 2, 2)
                            conn.commit()
                        else:
                            logger.warning(f"Не найдено подходящих участников для передачи роли президента в клубе {club_id}")
                    except Error as e:
                        logger.error(f"Ошибка MySQL при передаче роли: {e}")
                    finally:
                        cur.close()
                        conn.close()

            # Отправляем сообщения
            AllianceLeaveOkMessage(self.client, self.player).send()
            MyAllianceMessage(self.client, self.player, 0).send()
            for player_id in self.plrids:
                if player_id != self.player.low_id:
                    logger.debug(f"Отправляем AllianceDataMessage игроку {player_id}")
                    AllianceDataMessage(self.client, self.player, 0, club_id).send()

            # Обновляем данные игрока
            self.player.club_low_id = 0
            self.player.club_role = 0
            DataBase.replaceValue(db, 'clubID', 0)
            DataBase.replaceValue(db, 'clubRole', 0)

            self.player.last_club_exit_time = time.time()

        except Exception as e:
            logger.error(f"Ошибка при обработке выхода игрока {self.player.low_id}: {e}")
            AllianceLeaveOkMessage(self.client, self.player).send()
            MyAllianceMessage(self.client, self.player, 0).send()