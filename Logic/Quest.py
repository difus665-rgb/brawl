import json
from database.DataBase import DataBase

class Quest:
    def EncodeQuest(self):
        self.writeBoolean(True)  # Quests Boolean
        if self.player.trophies >= 300:
            conn = DataBase.get_connection()
            if not conn:
                self.writeVint(0)
                return

            try:
                cur = conn.cursor()
                cur.execute("SELECT quests FROM plrs WHERE lowID=%s", (self.player.low_id,))
                result = cur.fetchone()
                if result and result[0]:
                    quests = json.loads(result[0])
                    questsCount = len(quests)
                else:
                    quests = []
                    questsCount = 0

                if questsCount > 0:
                    for item in quests:
                        self.writeVint(questsCount) #Кол-во квестов
                        self.writeVint(0) #Квест айди
                        self.writeVint(2) #Бравл пасс сезон хз
                        self.writeVint(item['MT'])  # Тип миссии победить/хилить/нанести
                        self.writeVint(item['counts'])  # Скок сделал
                        self.writeVint(item['win_count'])  # Скок надо
                        self.writeVint(item['prize'])  # Скок дадут
                        self.writeVint(0)  #ХЪ
                        self.writeVint(0)  # Текущий уровень (бой с боссом)
                        self.writeVint(0)  # Максимальный Уровень (бой с боссом)
                        self.writeVint(item['QT'])  # Квест тип | 0 = Сезонный, 1 = Дневной
                        self.writeBoolean(item['BPEX'])  # Для донатеров?
                        self.writeBoolean(True)
                        self.writeScId(16, item['id'])  # Боец
                        self.writeVint(item['GM'])  # Гей мод
                        self.writeVint(0)
                        self.writeVint(0)
                else:
                    self.writeVint(0)  # Нет квестов
            except Exception as e:
                self.writeVint(0)  # Записываем 0 в случае ошибки
            finally:
                cur.close()
                conn.close()
        else:
            self.writeVint(0)  # Нет квестов, если трофеев меньше 300