from Utils.Writer import Writer
from database.DataBase import DataBase
import json

class BrawlerLeaderGlobal(Writer):
    def __init__(self, client, player, ID):
        super().__init__(client)
        self.id = 24403
        self.player = player
        self.brawler = ID

    # Метод для получения трофеев бойца
    def by_tr(self, plr):
        return json.loads(plr[2])['brawlersTrophies'][str(self.brawler)]

    def encode(self):
        self.indexOfPlayer = 1
        self.writeVint(0)
        self.writeVint(0)
        self.writeScId(16, self.brawler)
        self.writeString()

        # Получаем данные из базы и сортируем по количеству трофеев (по убыванию)
        fetch = DataBase.GetLeaderboardByBrawler(self, self.brawler)
        fetch.sort(key=self.by_tr, reverse=True)

        # Подсчет количества игроков с трофеями > 0
        player_count = sum(1 for i in fetch if self.by_tr(i) > 0)
        self.writeVint(player_count)  # Записываем количество игроков

        # Перебираем игроков и записываем их данные
        for i in fetch:
            trophies = self.by_tr(i)
            if trophies > 0:
                self.writeVint(0)  # High ID
                self.writeVint(i[0])  # Low ID
                self.writeVint(1)

                # Записываем количество трофеев
                self.writeVint(trophies)
                self.writeVint(1)

                self.writeString("")  # Название клуба

                # Записываем имя игрока
                player_name = f"{i[1]}" if i[5] == 1 else i[1]
                self.writeString(player_name)

                self.writeVint(100)  # Уровень игрока
                self.writeVint(28000000 + i[3])
                self.writeVint(43000000 + i[4])

                # Дополнительная проверка для вывода корректных данных
                self.writeVint(43000000 + i[4] if i[5] == 1 else 0)
                self.writeVint(0)

        # Дополнительные параметры для завершения пакета данных
        self.writeVint(0)
        self.writeVint(1)  # Можно изменить при необходимости
        self.writeVint(0)
        self.writeVint(0)
        self.writeString(self.player.Region)