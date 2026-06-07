import json
import time
from database.DataBase import DataBase
from mysql.connector import Error

class Tokens:
    def EncodeTokens(self):
        TOKENS_PER_TICK = 20
        TICK_INTERVAL = 1200  # 20 минут в секундах
        MAX_TOKENS = 200

        conn = DataBase.get_connection()
        if not conn:
            print("ОШИБКА: Не удалось подключиться к базе данных")
            self.writeVint(0)
            self.writeVint(self.player.player_tokens)
            self.writeVint(1200)
            self.writeVint(0)
            return

        try:
            cur = conn.cursor()
            cur.execute("SELECT playerData FROM plrs WHERE lowID=%s", (self.player.low_id,))
            result = cur.fetchone()

            if not result:
                self.writeVint(0)
                self.writeVint(self.player.player_tokens)
                self.writeVint(1200)
                self.writeVint(1)
                return

            player_data = json.loads(result[0]) if result[0] else {}
            current_tokens = player_data.get("Player_Tokens", 0)
            last_token_time = player_data.get("last_token_time", 0)

            current_time = int(time.time())
            elapsed_time = current_time - last_token_time
            ticks_passed = elapsed_time // TICK_INTERVAL

            # Рассчитываем, сколько токенов можно добавить (без превышения лимита)
            tokens_possible_to_add = ticks_passed * TOKENS_PER_TICK
            tokens_needed_to_max = MAX_TOKENS - current_tokens
            tokens_to_add = min(tokens_possible_to_add, tokens_needed_to_max)

            if tokens_to_add > 0:
                new_tokens = current_tokens + tokens_to_add
                player_data["Player_Tokens"] = new_tokens
                player_data["last_token_time"] = current_time - (elapsed_time % TICK_INTERVAL)
                cur.execute("UPDATE plrs SET playerData=%s WHERE lowID=%s",
                           (json.dumps(player_data), self.player.low_id))
                conn.commit()
                self.player.player_tokens = new_tokens
            else:
                self.player.player_tokens = current_tokens

            # Определяем время до следующего пополнения
            if self.player.player_tokens >= MAX_TOKENS:
                time_until_next = 0
            else:
                time_until_next = TICK_INTERVAL - (elapsed_time % TICK_INTERVAL)

            self.writeVint(0)
            self.writeVint(self.player.player_tokens)
            self.writeVint(time_until_next)
            self.writeVint(0)

        except Error as e:
            print(f"ОШИБКА MySQL в EncodeTokens: {e}")
            self.writeVint(0)
            self.writeVint(self.player.player_tokens)
            self.writeVint(1200)
            self.writeVint(0)
        finally:
            if 'cur' in locals():
                cur.close()
            if conn:
                conn.close()