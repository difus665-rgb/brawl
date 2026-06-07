#LogicSecretHandshakeCommand.py
from Utils.Reader import Reader
from Server.Login.LoginFailedMessage import LoginFailedMessage


class LogicSecretHandshakeCommand(BSMessageReader):
    def __init__(self, client, player, data):
        super().__init__(data)
        self.client = client
        self.player = player

    def decode(self):
        self.read_Vint()  # Command ID (1488)
        self.read_Vint()  # Version
        self.secret_key = self.read_Int()

    def process(self):
        SECRET_KEY = 0xCAFEBABE

        if not hasattr(self.player, 'handshake_verified'):
            self.player.handshake_verified = False

        if self.secret_key != SECRET_KEY:
            print(f"[SECURITY] Клиент {self.player.low_id} прислал неверный ключ: {hex(self.secret_key)}")
            LoginFailedMessage(self.client, self.player, "Ошибка безопасности: неверный ключ").send()
            self.client.close()
            return

        self.player.handshake_verified = True
        print(f"[SECURITY] Клиент {self.player.low_id} прошёл проверку.")