import re
from Logic.Commands.Server.LogicChangeAvatarNameCommand import LogicChangeAvatarNameCommand
from Server.Home.AvatarNameChangeFailedMessage import AvatarNameChangeFailedMessage
from Utils.Reader import BSMessageReader

class SetNameMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.username = self.read_string()
        self.state = self.read_Vint()

    def contains_only_valid_chars(self, name):
        if not name.strip():
            return False
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # Эмодзи смайликов
            "\U0001F300-\U0001F5FF"   # Символы, относящиеся к объектам
            "\U0001F680-\U0001F6FF"   # Транспорт и символы карты
            "\U0001F700-\U0001F77F"   # Алхимия
            "\U0001F780-\U0001F7FF"   # Геометрические фигуры
            "\U0001F800-\U0001F8FF"   # Разные символы
            "\U0001F900-\U0001F9FF"   # Руки, жесты и части тела
            "\U0001FA00-\U0001FA6F"   # Разные предметы
            "\U0001FA70-\U0001FAFF"   # Символы связанных объектов
            "\U00002600-\U000026FF"   # Различные символы (например, ☀, ☂, ☕)
            "\U00002700-\U000027BF"   # Различные символы (например, ✂, ✅)
            "\U0000200B"              # Zero Width Space
            "]+", flags=re.UNICODE
        )
        return not emoji_pattern.search(name)

    def process(self):
        if self.username and 2 <= len(self.username) <= 20 and self.contains_only_valid_chars(self.username):
            self.player.name = self.username
            LogicChangeAvatarNameCommand(self.client, self.player, self.state).send()
        else:
            AvatarNameChangeFailedMessage(self.client, self.player).send()