import json
import time
from Utils.Writer import Writer
from database.DataBase import DataBase

class Notifications(Writer):
    def __init__(self, client, player):
        super().__init__(client)
        self.player = player
        self.timestamp = int(time.time())

    def GetNotifCount(self):
        """Возвращает количество уведомлений."""
        return len(self.player.notifications)

    def GetNotifByIndex(self, index):
        """Возвращает уведомление по индексу."""
        return self.player.notifications.get(str(index))

    def UpdateNotifData(self, index):
        """Обновляет статус уведомления (прочитано)."""
        notifications = self.player.notifications
        if str(index) in notifications:
            notifications[str(index)]['Read'] = True
            self.player.notifications = notifications
            DataBase.replaceValue(self, "notifications", json.dumps(notifications))