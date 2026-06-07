import json
import datetime
import time
import mysql.connector
from mysql.connector import Error
import requests
from Logic.Player import Players
from Utils.Helpers import Helpers

class DataBase:
    @staticmethod
    def get_connection():
        try:
            with open('./database.json', 'r') as f:
                db_config = json.load(f)
            conn = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                buffered=True
            )
            return conn
        except Error as e:
            print(f"[ERROR] MySQL connection failed: {e}")
            return None
            
    @staticmethod
    def reset_brawlpass_for_all_players():
        """Сбрасывает прогресс Brawl Pass для всех игроков"""
        conn = DataBase.get_connection()
        if not conn:
            print("[ERROR] Не удалось подключиться к базе данных")
            return

        try:
            cursor = conn.cursor()
            
            # 1. Получаем всех игроков
            cursor.execute("SELECT lowID, BPTOKEN, BPXP, freepass, buypass, freepassold, buypassold FROM plrs")
            players = cursor.fetchall()
            
            for player in players:
                # 2. Переносим текущие токены в опыт
                new_bpxp = player[1]  # BPXP = BPTOKEN
                
                # 3. Переносим текущие награды в архив
                freepass = DataBase.safe_json_load(player[3])
                buypass = DataBase.safe_json_load(player[4])
                freepassold = DataBase.safe_json_load(player[5])
                buypassold = DataBase.safe_json_load(player[6])
                
                if isinstance(freepass, list):
                    freepassold.extend(freepass)
                if isinstance(buypass, list):
                    buypassold.extend(buypass)
                
                # 4. Сбрасываем прогресс текущего сезона
                update_cursor = conn.cursor()
                update_cursor.execute("""
                    UPDATE plrs SET 
                        BPXP = %s,
                        BPTOKEN = 0,
                        freepass = '[]',
                        buypass = '[]',
                        freepassold = %s,
                        buypassold = %s
                    WHERE lowID = %s
                """, (
                    new_bpxp,
                    json.dumps(freepassold),
                    json.dumps(buypassold),
                    player[0]
                ))
                conn.commit()
                update_cursor.close()
            
            print(f"[BP RESET] Сброшен Brawl Pass для {len(players)} игроков")
            
            # 5. Обновляем конфиг
            DataBase.update_bp_config()
            
        except Error as e:
            print(f"[ERROR] Ошибка MySQL при сбросе Brawl Pass: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_region_by_ip(ip_address):
        """Метод для определения региона по IP."""
        try:
            url = f'http://ip-api.com/json/{ip_address}'
            response = requests.get(url)
            data = response.json()
            if data.get('status') == 'fail':
                return 'Unknown'
            return data.get('countryCode', 'Unknown')
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении региона: {e}")
            return 'Unknown'
            
    @staticmethod
    def check_brawlpass_reset():
        """Проверяет и выполняет сброс Brawl Pass при отрицательном времени"""
        try:
            bp_time = Helpers().NEWBPTIME
            if bp_time == 0:  # Если время отрицательное
                print("[BP RESET] Обнаружено отрицательное время до нового сезона, инициирую сброс")
                DataBase.reset_brawlpass_for_all_players()
                return True
            return False
        except Exception as e:
            print(f"[ERROR] Ошибка при проверке сброса Brawl Pass: {e}")
            return False

    @staticmethod
    def safe_json_load(data):
        """Безопасная загрузка JSON данных"""
        if not data:
            return []
        try:
            return json.loads(data)
        except:
            return data if isinstance(data, list) else []

    @staticmethod
    def update_bp_config():
        """Обновляет конфиг Brawl Pass после сброса"""
        try:
            with open('config.json', 'r+') as f:
                config = json.load(f)
                
                # 1. Переносим текущих покупателей в архив
                config["buybpold"].extend(config["buybp"])
                config["buybp"] = []
                
                # 2. Увеличиваем номер сезона
                config["BPSEASON"] += 1
                
                # 3. Устанавливаем новую дату следующего сезона (через 30 дней)
                next_season = datetime.datetime.now() + datetime.timedelta(days=30)
                config["NEXTSEASON"] = next_season.strftime("%d.%m.%y %H:%M")
                
                # 4. Сохраняем изменения
                f.seek(0)
                json.dump(config, f, indent=4)
                f.truncate()
                
            print("[BP CONFIG] Конфиг Brawl Pass обновлен")
        except Exception as e:
            print(f"[ERROR] Ошибка при обновлении конфига Brawl Pass: {e}")
            
    @staticmethod
    def get_bp_config():
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                return {
                    "BPSEASON": config.get("BPSEASON", 1),
                    "BPSEASONOLD": config.get("BPSEASONOLD", 1)
                }
        except Exception as e:
            print(f"[ERROR] Не удалось загрузить конфиг Brawl Pass: {e}")
            return {"BPSEASON": 1, "BPSEASONOLD": 1}

    def loadAccount(self):
        from Server.Login.LoginFailedMessage import LoginFailedMessage
        conn = DataBase.get_connection()
        if not conn:
            self.player.err_code = 1
            print(f"[ERROR] - {self.player.ip_address} - 0008")
            LoginFailedMessage(self.client, self.player, "Server Error: 8").send()
            return

        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM plrs WHERE token=%s", (self.player.token,))
            fetch = cur.fetchall()
            if fetch:
                user_data = fetch[0]
            else:
                user_data = None
                self.player.err_code = 1
                print(f"[ERROR] - {self.player.ip_address} - 0008")
                LoginFailedMessage(self.client, self.player, "Server Error: 8").send()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            user_data = None
            self.player.err_code = 1
            print(f"[ERROR] - {self.player.ip_address} - 0008")
            LoginFailedMessage(self.client, self.player, "Server Error: 8").send()
        finally:
            cur.close()
            conn.close()

        if user_data:
            self.player.low_id = user_data[1]
            self.player.name = user_data[2]
            self.player.trophies = user_data[3]
            self.player.gold = user_data[4]
            self.player.gems = user_data[5]
            self.player.starpoints = user_data[6]
            self.player.tickets = user_data[7]
            self.player.Troproad = user_data[8]
            self.player.profile_icon = user_data[9]
            self.player.name_color = user_data[10]
            self.player.club_low_id = user_data[11]
            self.player.club_role = user_data[12]
            self.player.brawler_id = user_data[14]
            self.player.skin_id = user_data[15]
            self.player.room_id = user_data[16]
            self.player.box = user_data[17]
            self.player.bigbox = user_data[18]
            self.player.online = user_data[19]
            self.player.vip = user_data[20]
            self.player.player_experience = user_data[21]
            self.player.ccc = user_data[23]
            self.player.trioWINS = user_data[24]
            self.player.sdWINS = user_data[25]
            self.player.theme = user_data[26]
            self.player.BPTOKEN = user_data[27]
            self.player.BPXP = user_data[28]
            self.player.quests = json.loads(user_data[29])
            try:
                self.player.freepass = json.loads(user_data[30])
            except:
                self.player.freepass = user_data[30]
            try:
                self.player.buypass = json.loads(user_data[31])
            except:
                self.player.buypass = user_data[31]
            self.player.notifRead = user_data[32]
            self.player.notifRead2 = user_data[33]
            self.player.ip_address = user_data[34]
            self.player.creation_date = user_data[35]
            self.player.Region = user_data[36]
            self.player.notifications = json.loads(user_data[37]) if user_data[37] else {}
            playerData = json.loads(user_data[38])
            friends = json.loads(user_data[22])
            brawlerData = json.loads(user_data[13])
            try:
                self.player.freepassold = json.loads(user_data[39])
            except:
                self.player.freepass = user_data[39]
            try:
                self.player.buypassold = json.loads(user_data[40])
            except:
                self.player.buypassold = user_data[40]
            self.player.player_tokens = playerData["Player_Tokens"]
            self.player.tokensdoubler = playerData["Tokens_Doubler"]
            self.player.last_token_time = playerData["last_token_time"]
            self.player.HashTag = playerData["HashTag"]
            self.player.test = playerData["Test"]
            self.player.debacle = playerData["Debacle"]
            self.player.boss_fight = playerData["Boss_Fight"]
            self.player.robo_cabin = playerData["Robo_Cabin"]
            self.player.power_race = playerData["Power_Race"]
            self.player.duo_wins = playerData["Duo_Wins"]
            self.player.highest_trophies = brawlerData["highest_trophies"]
            self.player.brawlers_trophies = brawlerData["brawlersTrophies"]
            self.player.UnlockedBrawlers = brawlerData["UnlockedBrawlers"]
            self.player.UnlockedSkins = brawlerData["UnlockedSkins"]
            self.player.brawlerPowerLevel = brawlerData["brawlerPowerLevel"]
            self.player.brawlerPoints = brawlerData["brawlerPoints"]
            self.player.Brawler_newTag = brawlerData["brawlerNewTag"]
            self.player.StarPowerUnlocked = brawlerData["StarPowerUnlocked"]
            self.player.UnlockedPins = brawlerData["UnlockedPins"]
            player_total_trophies = sum(self.player.brawlers_trophies[x] for x in self.player.brawlers_trophies)
            self.player.trophies = player_total_trophies
            DataBase.replaceValue(self, 'trophies', self.player.trophies)
            if self.player.trophies > self.player.highest_trophies:
                self.player.highest_trophies = self.player.trophies
                DataBase.replaceValue(self, 'highest_trophies', self.player.highest_trophies)

    def createAccount(self):
        """Создание нового аккаунта игрока в базе MySQL."""
        conn = DataBase.get_connection()
        if not conn:
            self.player.low_id = 2
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS plrs (
                    token VARCHAR(255),
                    lowID INT,
                    name VARCHAR(255),
                    trophies INT,
                    gold INT,
                    gems INT,
                    starpoints INT,
                    tickets INT,
                    Troproad INT,
                    profile_icon INT,
                    name_color INT,
                    clubID INT,
                    clubRole INT,
                    brawlerData JSON,
                    brawlerID INT,
                    skinID INT,
                    roomID INT,
                    box INT,
                    bigbox INT,
                    online INT,
                    vip INT,
                    playerExp INT,
                    friends JSON,
                    SCC TEXT,
                    trioWINS INT,
                    sdWINS INT,
                    theme INT,
                    BPTOKEN INT,
                    BPXP INT,
                    quests JSON,
                    freepass JSON,
                    buypass JSON,
                    notifRead INT,
                    notifRead2 INT,
                    ip_address VARCHAR(255),
                    creation_date VARCHAR(255),
                    Region VARCHAR(255),
                    notifications JSON,
                    playerData JSON,
                    freepassold JSON,
                    buypassold JSON,
                    PRIMARY KEY (token)
                )
            """)
            json_quests = json.dumps(self.player.quests)
            jsonFBP = json.dumps(self.player.freepass)
            jsonBBP = json.dumps(self.player.buypass)
            jsonFBPOLD = json.dumps(self.player.freepassold)
            jsonBBPOLD = json.dumps(self.player.buypassold)
            self.player.creation_date = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            self.player.Region = DataBase.get_region_by_ip(self.player.ip_address)
            var = (
                self.player.token, self.player.low_id, self.player.name, self.player.trophies,
                self.player.gold, self.player.gems, self.player.starpoints, self.player.tickets,
                self.player.Troproad, self.player.profile_icon, self.player.name_color,
                self.player.club_low_id, self.player.club_role,
                json.dumps({
                    "highest_trophies": self.player.highest_trophies,
                    "brawlersTrophies": self.player.brawlers_trophies,
                    "UnlockedBrawlers": self.player.UnlockedBrawlers,
                    "UnlockedSkins": self.player.UnlockedSkins,
                    "brawlerPowerLevel": self.player.brawlerPowerLevel,
                    "brawlerPoints": self.player.brawlerPoints,
                    "brawlerNewTag": self.player.Brawler_newTag,
                    "StarPowerUnlocked": self.player.StarPowerUnlocked,
                    "UnlockedPins": self.player.UnlockedPins
                }),
                self.player.brawler_id, self.player.skin_id, self.player.room_id,
                self.player.box, self.player.bigbox, self.player.online, self.player.vip,
                self.player.player_experience, json.dumps([]), self.player.ccc,
                self.player.trioWINS, self.player.sdWINS, self.player.theme,
                self.player.BPTOKEN, self.player.BPXP, json_quests, jsonFBP, jsonBBP,
                self.player.notifRead, self.player.notifRead2, self.player.ip_address,
                self.player.creation_date, self.player.Region, json.dumps(self.player.notifications),
                json.dumps({
                    "Player_Tokens": self.player.player_tokens, "Tokens_Doubler": self.player.tokensdoubler, "last_token_time": self.player.last_token_time, "HashTag": self.player.HashTag, "Test": self.player.test, "Debacle": self.player.debacle,
                    "Boss_Fight": self.player.boss_fight, "Robo_Cabin": self.player.robo_cabin,
                    "Power_Race": self.player.power_race, "Duo_Wins": self.player.duo_wins
                }), jsonFBPOLD, jsonBBPOLD
            )
            cur.execute("""
                INSERT INTO plrs VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
            """, var)
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            self.player.low_id = 2
        finally:
            cur.close()
            conn.close()
            
    def update_token(self, lowID, new_token):
        conn = DataBase.get_connection()
        if not conn:
            return "❌ Не удалось подключиться к базе данных."

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET token = %s WHERE lowID = %s", (new_token, lowID))
            conn.commit()
            return f"✅ Токен обновлён для аккаунта {lowID}."
        except Error as e:
            conn.rollback()
            return f"❌ Ошибка базы данных: {e}"
        finally:
            cursor.close()
            conn.close()
            
    def update_token_by_lowID(self, lowID, new_token):
        conn = DataBase.get_connection()
        if not conn:
            return "❌ Не удалось подключиться к базе данных."

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE plrs SET token = %s WHERE lowID = %s", (new_token, lowID))
            conn.commit()

            if cursor.rowcount > 0:
                return f"✅ Токен успешно обновлён для аккаунта с ID {lowID}."
            else:
                return f"❌ Аккаунт с ID {lowID} не найден."
        except Exception as e:
            conn.rollback()
            return f"❌ Ошибка MySQL: {e}"
        finally:
            cursor.close()
            conn.close()
            
    def get_id_by_hash(self, hash_tag):
        conn = DataBase.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT lowID FROM plrs WHERE JSON_EXTRACT(playerData, '$.HashTag') = %s", (hash_tag,))
            result = cursor.fetchone()
            return result['lowID'] if result else None
        except Exception as e:
            logger.error(f"[ERROR] get_id_by_hash: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
            
    def delete_player_by_token(self, token):
        conn = DataBase.get_connection()
        if not conn:
            return "❌ Не удалось подключиться к базе данных."

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM plrs WHERE token = %s", (token,))
            conn.commit()

            if cursor.rowcount > 0:
                return f"✅ Игрок с токеном `{token}` удален."
            else:
                return "❌ Игрок с таким токеном не найден."
        except Exception as e:
            conn.rollback()
            return f"❌ Ошибка MySQL: {e}"
        finally:
            cursor.close()
            conn.close()
            
    def deletePlayer(self, lowID):
        conn = DataBase.get_connection()
        if not conn:
            return "❌ Не удалось подключиться к базе данных."

        try:
            cursor = conn.cursor()

            # Удаляем игрока по ID
            cursor.execute("DELETE FROM plrs WHERE lowID = %s", (lowID,))
            conn.commit()

            if cursor.rowcount > 0:
                return f"✅ Игрок с ID {lowID} удален."
            else:
                return f"❌ Игрок с ID {lowID} не найден."
        except Error as e:
            conn.rollback()
            return f"❌ Ошибка MySQL: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    def get_token_by_lowID(self, lowID):
        conn = DataBase.get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT token FROM plrs WHERE lowID = %s", (lowID,))
            result = cursor.fetchone()
            return result['token'] if result else None
        except Exception as e:
            print(f"[ERROR] get_token_by_lowID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def delete_player_by_lowID(self, lowID):
        conn = DataBase.get_connection()
        if not conn:
            return "❌ Не удалось подключиться к базе данных."

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM plrs WHERE lowID = %s", (lowID,))
            conn.commit()

            if cursor.rowcount > 0:
                return f"✅ Игрок с ID {lowID} удален."
            else:
                return f"❌ Игрок с ID {lowID} не найден."
        except Exception as e:
            conn.rollback()
            return f"❌ Ошибка при удалении: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    def getSuggestions(self):
        """Получение предложений игроков, отсортированных по трофеям."""
        conn = DataBase.get_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SELECT lowID, name, trophies, profile_icon, name_color, friends FROM plrs ORDER BY trophies DESC LIMIT 50")
            result = cur.fetchall()
            return result
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def getLeaders(self):
        """Получение лидерборда игроков."""
        conn = DataBase.get_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SELECT lowID, name, trophies, profile_icon, name_color, clubID, vip FROM plrs WHERE name != %s ORDER BY trophies DESC LIMIT 150", ('VBC26',))
            result = cur.fetchall()
            return result
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def getAll(self):
        """Получение всех игроков из базы данных."""
        conn = DataBase.get_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM plrs")
            result = cur.fetchall()
            return result
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def GetLeaderboardByBrawler(self, ID):
        """Получение лидерборда, отсортированного по трофеям бойца."""
        conn = DataBase.get_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SELECT lowID, name, brawlerData, profile_icon, name_color, vip FROM plrs WHERE name != %s LIMIT 150", ('VBC26',))
            fetch = cur.fetchall()
            fetch.sort(key=lambda plr: json.loads(plr[2])['brawlersTrophies'].get(str(ID), 0) if isinstance(plr[2], str) else 0, reverse=True)
            return fetch
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def GetLeaderboardByRegionBrawler(self, ID, region=None):
        """Получение регионального лидерборда, отсортированного по трофеям бойца."""
        if region is None:
            region = self.player.Region
        conn = DataBase.get_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SELECT lowID, name, brawlerData, profile_icon, name_color, vip FROM plrs WHERE region = %s AND name != %s LIMIT 150", (region, 'VBC26'))
            fetch = cur.fetchall()
            fetch.sort(key=lambda plr: json.loads(plr[2])['brawlersTrophies'].get(str(ID), 0) if isinstance(plr[2], str) else 0, reverse=True)
            return fetch
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def getLeadersRegion(self, region=None):
        """Получение регионального лидерборда."""
        if region is None:
            region = self.player.Region
        conn = DataBase.get_connection()
        if not conn:
            return []
        try:
            cur = conn.cursor()
            cur.execute("SELECT lowID, name, trophies, profile_icon, name_color, clubID, vip FROM plrs WHERE region = %s AND name != %s ORDER BY trophies DESC LIMIT 150", (region, 'VBC26'))
            result = cur.fetchall()
            return result
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def setImmedatedValue(self, table, var, val, sqlsin):
        """Установка значения в указанной таблице."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(f"UPDATE `{table}` SET `{var}`=%s {sqlsin}", (val,))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def getSpecifiedValue(self, value_name):
        """Получение конкретного значения для игрока."""
        conn = DataBase.get_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT `{value_name}` FROM plrs WHERE token=%s", (self.player.token,))
            result = cur.fetchone()
            if result:
                return result[0]
            return None
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def updatePlayer(self, player):
        """Обновление уведомлений игрока."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("UPDATE plrs SET notifications=%s WHERE lowID=%s", (json.dumps(player.notifications), player.low_id))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def loadByToken(self, token):
        """Загрузка данных игрока по токену."""
        conn = DataBase.get_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM plrs WHERE token=%s", (token,))
            result = cur.fetchone()
            if result:
                return result
            return None
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return None
        finally:
            cur.close()
            conn.close()
            
    def dball():
        conn = DataBase.get_connection()
        if not conn:
            logger.error("[ERROR] Не удалось подключиться к базе данных.")
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT lowID FROM plrs")
            result = cursor.fetchall()
            logger.info(f"[INFO] Найдено игроков: {len(result)}")
            return result
        except Error as e:
            logger.error(f"[ERROR] Ошибка в dball(): {e}")
            return []
        finally:
            cursor.close()
            conn.close()
            
    def get_player_count():
        conn = DataBase.get_connection()
        if not conn:
            return "NO DATA"
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM plrs")
            count = cursor.fetchone()[0]
            return count
        except Error as e:
            logger.error(f"[ERROR] MySQL error in get_player_count(): {e}")
            return "NO DATA"
        finally:
            cursor.close()
            conn.close()

    def loadbyID(self, ID):
        """Загрузка данных игрока по lowID."""
        conn = DataBase.get_connection()
        if not conn:
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM plrs WHERE lowID=%s", (ID,))
            return cur.fetchone()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def set2All(self, var, val):
        """Установка значения для всех игроков."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(f"UPDATE plrs SET `{var}`=%s", (val,))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def callbackSQLQ(self, sqlcallback):
        """Выполнение пользовательского SQL-запроса."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(sqlcallback)
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def addNotification(self, lowId, notif_type, description, brawlerID, skinID, gems):
        conn = DataBase.get_connection()
        if not conn:
            return "Failed to connect to database."

        try:
            cur = conn.cursor()
            cur.execute("SELECT notifications FROM plrs WHERE lowID=%s", (lowId,))
            result = cur.fetchone()
            if result is None:
                return f"Игрок с lowID {lowId} не найден!"

            notifications = json.loads(result[0]) if result[0] else {}

            if notifications:
                current_keys = [int(key) for key in notifications.keys()]
                new_key = max(current_keys) + 1
            else:
                new_key = 2

            new_notification = {
                "ID": notif_type,
                "Read": False,
                "Timer": int(time.time()),
                "Desc": description,
                "BrawlerID": brawlerID,
                "SkinID": skinID,
                "Gems": gems
            }

            notifications[str(new_key)] = new_notification
            updated_notifications_json = json.dumps(notifications)

            cur.execute("UPDATE plrs SET notifications=%s WHERE lowID=%s", (updated_notifications_json, lowId))
            conn.commit()
            return "✅ Нотиф успешно добавлен"
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return f"❌ Ошибка при добавлении уведомления: {e}"
        finally:
            cur.close()
            conn.close()

    def addNotificationToAll(self, id, desc, brawlerId, skinId, gems):
        """Добавление уведомления всем игрокам."""
        conn = DataBase.get_connection()
        if not conn:
            return "Failed to connect to database."
        try:
            cur = conn.cursor()
            cur.execute("SELECT lowID, notifications FROM plrs")
            players = cur.fetchall()
            if not players:
                return "Нет игроков в базе данных."
            for player in players:
                lowId = player[0]
                result = player[1]
                notifications = json.loads(result) if result else {}
                if notifications:
                    current_keys = [int(key) for key in notifications.keys()]
                    new_key = max(current_keys) + 1
                else:
                    new_key = 2
                new_notification = {
                    "ID": id,
                    "Read": False,
                    "Timer": int(time.time()),
                    "Desc": desc,
                    "BrawlerID": brawlerId,
                    "SkinID": skinId,
                    "Gems": gems
                }
                notifications[str(new_key)] = new_notification
                updated_notifications_json = json.dumps(notifications)
                cur.execute("UPDATE plrs SET notifications=%s WHERE lowID=%s", (updated_notifications_json, lowId))
            conn.commit()
            return "Нотиф успешно добавлены всем игрокам."
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return f"Ошибка при добавлении уведомлений: {e}"
        finally:
            cur.close()
            conn.close()

    def removeNotification(self, lowId, notif_index):
        """Удаление уведомления для игрока."""
        conn = DataBase.get_connection()
        if not conn:
            return f"Failed to connect to database."
        try:
            cur = conn.cursor()
            cur.execute("SELECT notifications FROM plrs WHERE lowID=%s", (lowId,))
            result = cur.fetchone()
            if result is None:
                return f"❌ Игрок с lowID {lowId} не найден!"
            notifications = json.loads(result[0]) if result[0] else {}
            notif_index_str = str(notif_index)
            if notif_index_str in notifications:
                del notifications[notif_index_str]
                updated_notifications_json = json.dumps(notifications)
                cur.execute("UPDATE plrs SET notifications=%s WHERE lowID=%s", (updated_notifications_json, lowId))
                conn.commit()
                return f"✅ Нотиф с индексом {notif_index} успешно удален у игрока {lowId}."
            else:
                return "❌ Нотиф с таким индексом не найден!"
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
            return f"Ошибка при удалении уведомления: {e}"
        finally:
            cur.close()
            conn.close()
            
    def check_notification_exists(self, lowID, partial_description):
        conn = DataBase.get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT notifications FROM plrs WHERE lowID = %s", (lowID,))
            result = cursor.fetchone()

            if not result or not result['notifications']:
               return False

            try:
                notifs = json.loads(result['notifications'])
            except json.JSONDecodeError:
                return False

            for key, notif in notifs.items():
                if isinstance(notif, dict) and partial_description in notif.get('Desc', ''):
                    return True  # Такое уведомление уже есть
            return False  # Не найдено
        finally:
            cursor.close()
            conn.close()
            
    def find_notification_index(self, lowID, partial_description):
        conn = DataBase.get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT notifications FROM plrs WHERE lowID = %s", (lowID,))
            result = cursor.fetchone()

            if not result or not result['notifications']:
                return None

            try:
                notifs = json.loads(result['notifications'])
            except json.JSONDecodeError:
                print(f"[ERROR] Не удалось распарсить notifications для lowID {lowID}")
                return None

            # Ищем уведомление с совпадающим описанием
            for key, notif in notifs.items():
                if isinstance(notif, dict) and partial_description in notif.get('Desc', ''):
                    return key  # Возвращаем индекс уведомления
            return None
        finally:
            cursor.close()
            conn.close()

    def replaceValue(self, value_name, new_value):
        """Замена значения в записи игрока."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            if value_name == "3vs3Wins":
                value_name = "TvsTWins"
            if value_name in ["UnlockedSkins", "UnlockedPins", "StarPowerUnlocked", "brawlersTrophies", "brawlersTrophiesForRank", "brawlersSkins", "brawlerPoints", "UnlockedBrawlers", "brawlerPowerLevel", "chwins", "highest_trophies", "brawlerNewTag"]:
                cur.execute("SELECT brawlerData FROM plrs WHERE token=%s", (self.player.token,))
                data = json.loads(cur.fetchall()[0][0])
                data[value_name] = new_value
                cur.execute("UPDATE plrs SET brawlerData=%s WHERE token=%s", (json.dumps(data), self.player.token))
            elif value_name in ["last_token_time", "Tokens_Doubler", "Player_Tokens", "Test", "Debacle", "Boss_Fight", "Robo_Cabin", "Power_Race", "Duo_Wins"]:
                cur.execute("SELECT playerData FROM plrs WHERE token=%s", (self.player.token,))
                data = json.loads(cur.fetchall()[0][0])
                data[value_name] = new_value
                cur.execute("UPDATE plrs SET playerData=%s WHERE token=%s", (json.dumps(data), self.player.token))
            else:
                if value_name != "tranim":
                    cur.execute(f"UPDATE plrs SET `{value_name}`=%s WHERE token=%s", (new_value, self.player.token))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def replaceOtherValue(self, ID, value_name, new_value):
        """Замена значения для другого игрока по lowID."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            if value_name in ["UnlockedSkins", "UnlockedPins", "brawlersTrophies", "brawlersTrophiesForRank", "brawlersSkins"]:
                cur.execute("SELECT brawlerData FROM plrs WHERE lowID=%s", (ID,))
                data = json.loads(cur.fetchall()[0][0])
                data[value_name] = new_value
                cur.execute("UPDATE plrs SET brawlerData=%s WHERE lowID=%s", (json.dumps(data), ID))
            elif value_name == "Skins":
                cur.execute("SELECT skinsData FROM plrs WHERE lowID=%s", (ID,))
                data = json.loads(cur.fetchall()[0][0]) if cur.fetchall()[0][0] else {}
                data[value_name] = new_value
                cur.execute("UPDATE plrs SET skinsData=%s WHERE lowID=%s", (json.dumps(data), ID))
            else:
                cur.execute(f"UPDATE plrs SET `{value_name}`=%s WHERE lowID=%s", (new_value, ID))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def UpdateValue(self, var, new):
        """Увеличение значения в записи игрока."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT `{var}` FROM plrs WHERE token=%s", (self.player.token,))
            current_value = cur.fetchone()[0]
            cur.execute(f"UPDATE plrs SET `{var}`=%s WHERE token=%s", (current_value + new, self.player.token))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def createGameroomDB(self):
        """Создание игровой комнаты и инициализация чата."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS gr (
                    roomID INT PRIMARY KEY,
                    mapID INT,
                    gadget INT,
                    players JSON,
                    type INT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    roomID INT,
                    Event INT,
                    Tick INT,
                    plrid INT,
                    plrname VARCHAR(255),
                    plrrole INT,
                    Msg TEXT
                )
            """)
            plrs = {
                "0": {
                    "host": 1,
                    "lowID": self.player.low_id,
                    "name": self.player.name,
                    "Team": self.player.team,
                    "ctick": self.player.ctick,
                    "message": self.player.message,
                    "Ready": self.player.isReady,
                    "brawlerID": self.player.brawler_id,
                    "skinID": self.player.skin_id,
                    "starpower": self.player.starpower,
                    "gadget": self.player.gadget,
                    "profileIcon": self.player.profile_icon,
                    "namecolor": self.player.name_color,
                    "status": 0
                }
            }
            cur.execute("INSERT INTO gr VALUES (%s, %s, %s, %s, %s)", 
                        (self.player.room_id, self.player.map_id, 1, json.dumps(plrs), self.player.roomType))
            cur.execute("INSERT INTO chats VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (self.player.room_id, 2, 1, 0, "Cosmo Bot", 2, "Удачной игры!"))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def AddroomMSG(self, clubID, event, tick, Low_id, name, message):
        """Добавление сообщения в чат игровой комнаты."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS chats (roomID INT, Event INT, Tick INT, plrid INT, plrname VARCHAR(255), plrrole INT, Msg TEXT)")
            cur.execute("SELECT * FROM chats WHERE roomID=%s", (clubID,))
            fetch = cur.fetchall()
            cur.execute("INSERT INTO chats VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (clubID, event, len(fetch) + 1, Low_id, name, 0, message))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def GetMsgRoom(self, clubID):
        """Получение сообщений для игровой комнаты."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS chats (roomID INT, Event INT, Tick INT, plrid INT, plrname VARCHAR(255), plrrole INT, Msg TEXT)")
            cur.execute("SELECT * FROM chats WHERE roomID=%s", (clubID,))
            fetch = cur.fetchall()
            self.MessageCount = len(fetch) if fetch else 1
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def removeRoom(self):
        """Удаление игровой комнаты."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM gr WHERE roomID=%s", (self.player.room_id,))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def getRandomroomAndJoin(self, mapslot):
        """Присоединение к случайной игровой комнате с доступными слотами."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM gr")
            fetch = cur.fetchall()
            if fetch:
                for i in fetch:
                    plrData = json.loads(i[3])
                    if len(plrData) < 3:
                        l = str(len(plrData))
                        plrData[l] = {
                            "host": 0,
                            "lowID": self.player.low_id,
                            "name": self.player.name,
                            "Team": 0,
                            "ctick": self.player.ctick,
                            "message": self.player.message,
                            "Ready": self.player.isReady,
                            "brawlerID": self.player.brawler_id,
                            "skinID": self.player.skin_id,
                            "starpower": self.player.starpower,
                            "gadget": self.player.gadget,
                            "profileIcon": self.player.profile_icon,
                            "namecolor": self.player.name_color,
                            "status": 0
                        }
                        cur.execute("UPDATE gr SET players=%s WHERE roomID=%s", (json.dumps(plrData), i[0]))
                        conn.commit()
                        self.mapID = i[1]
                        self.useGadget = i[2]
                        self.playerCount = len(plrData)
                        self.plrData = plrData
                        self.player.roomType = i[4]
                        self.player.room_id = i[0]
                        break
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def leaveRoom(self, reqID):
        """Удаление игрока из игровой комнаты."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM gr WHERE roomID=%s", (self.player.room_id,))
            fetch = cur.fetchall()
            if fetch:
                plrData = json.loads(fetch[0][3])
                for i in plrData:
                    if plrData[i]["lowID"] == reqID:
                        plrData.pop(str(i))
                        cur.execute("UPDATE gr SET players=%s WHERE roomID=%s", (json.dumps(plrData), self.player.room_id))
                        conn.commit()
                        break
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def loadGameroom(self):
        """Загрузка данных игровой комнаты."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS gr (roomID INT PRIMARY KEY, mapID INT, gadget INT, players JSON, type INT)")
            cur.execute("SELECT * FROM gr WHERE roomID=%s", (self.player.room_id,))
            fetch = cur.fetchall()
            if fetch:
                self.mapID = fetch[0][1]
                self.useGadget = fetch[0][2]
                plrs = json.loads(fetch[0][3])
                self.playerCount = len(plrs)
                self.plrData = plrs
                self.roomType = fetch[0][4]
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def leaveFromRoom(self, lowID):
        """Удаление игрока из игровой комнаты по lowID."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM gr WHERE roomID=%s", (self.player.room_id,))
            fetch = cur.fetchall()
            if fetch:
                plrData = json.loads(fetch[0][3])
                for i in plrData:
                    if plrData[i]["lowID"] == lowID:
                        plrData.pop(str(i))
                        cur.execute("UPDATE gr SET players=%s WHERE roomID=%s", (json.dumps(plrData), fetch[0][0]))
                        conn.commit()
                        break
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def replaceGameroomValue(self, value_name, new_value, type):
        """Замена значения в игровой комнате."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM gr WHERE roomID=%s", (self.player.room_id,))
            fetch = cur.fetchall()
            if fetch:
                if type == "room":
                    cur.execute(f"UPDATE gr SET `{value_name}`=%s WHERE roomID=%s", (new_value, self.player.room_id))
                    conn.commit()
                elif type == "player":
                    plrData = json.loads(fetch[0][3])
                    for i in plrData:
                        if plrData[i]["lowID"] == self.player.low_id:
                            plrData[i][value_name] = new_value
                            cur.execute("UPDATE gr SET players=%s WHERE roomID=%s", (json.dumps(plrData), self.player.room_id))
                            conn.commit()
                            break
                elif type == "removePlayer":
                    plrData = json.loads(fetch[0][3])
                    for i in plrData:
                        if plrData[i]["host"] == 1:
                            cur.execute("DELETE FROM gr WHERE roomID=%s", (fetch[0][0],))
                            conn.commit()
                            break
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def getRoomAndJoin(self, joinerToken, roomID):
        """Присоединение к конкретной игровой комнате."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM gr WHERE roomID=%s", (roomID,))
            fetch = cur.fetchall()
            if fetch:
                self.reqID = fetch[0][0]
                plrsData = json.loads(fetch[0][3])
                l = str(len(plrsData))
                plrsData[l] = {
                    "host": 0,
                    "lowID": self.player.low_id,
                    "name": self.player.name,
                    "Team": 0,
                    "ctick": self.player.ctick,
                    "message": self.player.message,
                    "Ready": self.player.isReady,
                    "brawlerID": self.player.brawler_id,
                    "skinID": self.player.skin_id,
                    "starpower": self.player.starpower,
                    "gadget": self.player.gadget,
                    "profileIcon": self.player.profile_icon,
                    "namecolor": self.player.name_color,
                    "status": 0
                }
                self.mapID = fetch[0][1]
                self.useGadget = fetch[0][2]
                self.playerCount = len(plrsData)
                self.plrData = plrsData
                cur.execute("UPDATE gr SET players=%s WHERE roomID=%s", (json.dumps(plrsData), self.reqID))
                conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def UpdateGameroomPlayerInfo(self, low_id):
        """Обновление информации игрока в игровой комнате."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM gr WHERE roomID=%s", (self.player.room_id,))
            fetch = cur.fetchall()
            if fetch:
                plrsData = json.loads(fetch[0][3])
                self.reqID = fetch[0][0]
                for i in plrsData:
                    if plrsData[i]["lowID"] == low_id:
                        plrsData[i]["Team"] = self.player.team
                        plrsData[i]["ctick"] = self.player.ctick
                        plrsData[i]["message"] = self.player.message
                        plrsData[i]["Ready"] = self.player.isReady
                        plrsData[i]["brawlerID"] = self.player.brawler_id
                        plrsData[i]["skinID"] = self.player.skin_id
                        plrsData[i]["starpower"] = self.player.starpower
                        plrsData[i]["gadget"] = self.player.gadget
                        plrsData[i]["profileIcon"] = self.player.profile_icon
                        plrsData[i]["namecolor"] = self.player.name_color
                        plrsData[i]["status"] = self.player.state
                        cur.execute("UPDATE gr SET players=%s WHERE roomID=%s", (json.dumps(plrsData), self.reqID))
                        conn.commit()
                        break
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def createClub(self, clubid=None):
        conn = DataBase.get_connection()
        if not conn:
            print("[ОШИБКА] Не удалось подключиться к базе данных")
            return None
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clubs (
                    clubID INT PRIMARY KEY,
                    name VARCHAR(255),
                    `desc` TEXT,
                    region VARCHAR(255),
                    badgeID INT,
                    type INT,
                    trophiesneeded INT,
                    friendlyfamily INT,
                    trophies INT,
                    members JSON,
                    notif JSON
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS club_chats (
                    clubID INT,
                    Event INT,
                    Tick INT,
                    plrid INT,
                    plrname VARCHAR(255),
                    plrrole INT,
                    Msg TEXT
                )
            """)
            # Генерируем clubID
            cur.execute("SELECT MAX(clubID) FROM clubs")
            max_id = cur.fetchone()[0]
            clubid = (max_id or 0) + 1

            # Проверяем уникальность
            cur.execute("SELECT clubID FROM clubs WHERE clubID=%s", (clubid,))
            if cur.fetchone():
                print(f"[ОШИБКА] clubID {clubid} уже занят")
                clubid += 1

            # Формируем данные клуба
            data = {"members": {str(self.player.low_id): self.player.name}}
            notif = {}
            var = (
                clubid, str(self.clubName), str(self.clubdescription), str(self.clubregionID),
                self.clubbadgeID, self.clubtype, self.clubtrophiesneeded,
                self.clubfriendlyfamily, self.player.trophies,
                json.dumps(data), json.dumps(notif)
            )
            cur.execute("INSERT INTO clubs VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", var)
            cur.execute("INSERT INTO club_chats VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (clubid, 2, 1, self.player.low_id, str(self.player.name), 2, "Добро пожаловать в клуб! Соблюдайте правила игры, а так же любите друг друга!"))
        
            # Обновляем игрока
            cur.execute("UPDATE plrs SET clubID=%s, clubRole=%s WHERE lowID=%s", 
                        (clubid, 2, self.player.low_id))
        
            conn.commit()
        
            # Проверяем сохранение
            cur.execute("SELECT clubID, name FROM clubs WHERE clubID=%s", (clubid,))
            saved_club = cur.fetchone()
            if not saved_club:
                print(f"[ОШИБКА] Клуб с ID {clubid} не сохранён")
                return None
        
            self.player.club_low_id = clubid
            self.player.club_role = 2
            print(f"[ИНФО] Создан клуб с ID {clubid} для игрока {self.player.low_id}, роль: {self.player.club_role}")
            return clubid
        except Error as e:
            print(f"[ОШИБКА] Ошибка MySQL в createClub: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def setNotifData(self, text, by):
        """Установка данных уведомления для клуба."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clubs WHERE clubID=%s", (self.player.club_low_id,))
            fetch = cur.fetchall()
            if fetch:
                notifData = json.loads(fetch[0][10]) if fetch[0][10] else {}
                l = str(len(notifData))
                notifData[l] = {
                    "text": text,
                    "by": by,
                    "timer": datetime.datetime.timestamp(datetime.datetime.now())
                }
                cur.execute("UPDATE clubs SET notif=%s WHERE clubID=%s", (json.dumps(notifData), self.player.club_low_id))
                conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def CountClub(self):
        conn = DataBase.get_connection()
        if not conn:
            print("[ERROR] Failed to connect to database")
            return 0
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM clubs")
            count = cur.fetchone()[0]
            self.AllianceCount = count
            print(f"[DEBUG] Counted {count} clubs")
            return count
        except Error as e:
            print(f"[ERROR] MySQL error in CountClub: {e}")
            return 0
        finally:
            cur.close()
            conn.close()

    def LeaderClub(self):
        """Получение топ-клубов по трофеям."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clubs ORDER BY trophies DESC LIMIT 200")
            fetch = cur.fetchall()
            self.club_list = [int(i[0]) for i in fetch]
            self.AllianceCount = len(fetch)
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def LeaderClubRegion(self):
        """Получение топ-клубов по трофеям в регионе."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clubs WHERE region = %s ORDER BY trophies DESC LIMIT 200", (self.clubregion,))
            fetch = cur.fetchall()
            self.club_list = [int(i[0]) for i in fetch]
            self.AllianceCount = len(fetch)
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def loadClub(self, clubid):
        conn = DataBase.get_connection()
        if not conn:
            print("[ОШИБКА] Не удалось подключиться к базе данных")
            return None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clubs WHERE clubID=%s", (clubid,))
            club_data = cur.fetchone()
            if club_data:
                self.clubmembercount = 0
                self.plrids = []
                self.clubName = club_data[1]
                self.clubdescription = club_data[2]
                self.clubregion = club_data[3]
                self.clubbadgeID = club_data[4]
                self.clubtype = club_data[5]
                self.clubtrophiesneeded = club_data[6]
                self.clubfriendlyfamily = club_data[7]
                self.clubtrophies = 0
                try:
                    self.notifData = json.loads(club_data[10]) if club_data[10] else {}
                except IndexError:
                    print("[ВНИМАНИЕ] Столбец notif отсутствует, добавляем")
                    cur.execute("ALTER TABLE clubs ADD COLUMN notif JSON")
                    conn.commit()
                    self.notifData = {}
                data = json.loads(club_data[9])
                members = data.get("members", {})
                for player_id, player_name in members.items():
                    try:
                        player_id_int = int(player_id)
                        self.plrids.append(player_id_int)
                        self.clubmembercount += 1
                        DataBase.GetMemberData(self, player_id_int)
                        self.clubtrophies += self.plrtrophies
                    except ValueError:
                        print(f"[ВНИМАНИЕ] Неверный ID игрока: {player_id}, пропускаем")
                return club_data
            else:
                print(f"[ИНФО] Клуб не найден для clubLowID={clubid}")
                return None
        except Error as e:
            print(f"[ОШИБКА] Ошибка MySQL в loadClub: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def AddMember(self, AllianceID, PlayerID, PlayerName, Action):
        conn = DataBase.get_connection()
        if not conn:
            print("[ОШИБКА] Не удалось подключиться к базе данных")
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clubs WHERE clubID=%s", (AllianceID,))
            fetch = cur.fetchall()
            if not fetch:
                print(f"[ОШИБКА] Клуб {AllianceID} не найден в AddMember")
                cur.execute("UPDATE plrs SET clubID=0, clubRole=0 WHERE lowID=%s", (PlayerID,))
                conn.commit()
                if PlayerID == self.player.low_id:
                    self.player.club_low_id = 0
                    self.player.club_role = 0
                return
            data = json.loads(fetch[0][9])
            if Action == 0:
                cur.execute("DELETE FROM club_chats WHERE clubID=%s", (AllianceID,))
                cur.execute("DELETE FROM clubs WHERE clubID=%s", (AllianceID,))
                cur.execute("UPDATE plrs SET clubID=0, clubRole=0 WHERE clubID=%s", (AllianceID,))
                conn.commit()
            elif Action == 1:
                data["members"][str(PlayerID)] = PlayerName
                cur.execute("UPDATE clubs SET members=%s WHERE clubID=%s", (json.dumps(data), AllianceID))
                ol = fetch[0][8]
                cur.execute("UPDATE clubs SET trophies=%s WHERE clubID=%s", (ol + self.player.trophies, AllianceID))
                conn.commit()
            elif Action == 2:
                data['members'].pop(str(PlayerID), None)
                cur.execute("UPDATE clubs SET members=%s WHERE clubID=%s", (json.dumps(data), AllianceID))
                ol = fetch[0][8]
                cur.execute("UPDATE clubs SET trophies=%s WHERE clubID=%s", (ol - self.player.trophies, AllianceID))
                cur.execute("UPDATE plrs SET clubID=0, clubRole=0 WHERE lowID=%s", (PlayerID,))
                if PlayerID == self.player.low_id:
                    self.player.club_low_id = 0
                    self.player.club_role = 0
                if not data['members']:
                    cur.execute("DELETE FROM club_chats WHERE clubID=%s", (AllianceID,))
                    cur.execute("DELETE FROM clubs WHERE clubID=%s", (AllianceID,))
                conn.commit()
        except Error as e:
            print(f"[ОШИБКА] Ошибка MySQL в AddMember: {e}")
        finally:
            cur.close()
            conn.close()

    def GetMemberData(self, Low_id):
        """Получение данных члена клуба по lowID."""
        try:
            players = DataBase.loadbyID(self, Low_id)
            if players and players[1] == int(Low_id):
                self.lowplrid = players[1]
                self.plrrole = players[12]
                self.plrtrophies = players[3]
                self.plrname = players[2]
                self.plricon = players[9]
                self.plrnamecolor = players[10]
                self.plrexperience = players[21]
                self.plrstatus = players[19]
                self.plrvip = players[20]
            else:
                raise ValueError("Player not found")
        except Exception as e:
            print(f"[ERROR] GetMemberData: {e}")
            self.lowplrid = 1
            self.plrrole = 0
            self.plrtrophies = 0
            self.plrname = "Аккаунт удалён!"
            self.plricon = 5
            self.plrnamecolor = 1
            self.plrexperience = 999
            self.plrvip = 0
            self.plrstatus = 0

    def replaceClubValue(self, target, inf1, inf2, inf3, inf4, inf5):
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("UPDATE clubs SET `desc`=%s, badgeID=%s, type=%s, trophiesneeded=%s, friendlyfamily=%s WHERE clubID=%s",
                        (inf1, inf2, inf3, inf4, inf5, self.player.club_low_id))
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def GetmsgCount(self, clubID):
        conn = DataBase.get_connection()
        if not conn:
            self.MessageCount = 0
            return

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) AS count FROM club_chats WHERE clubID = %s", (clubID,))
            result = cursor.fetchone()
            self.MessageCount = result['count'] if result else 0
        except Error as e:
            print(f"[ERROR] MySQL error in GetmsgCount: {e}")
            self.MessageCount = 0
        finally:
            cursor.close()
            conn.close()

    def Addmsg(self, clubID, event, tick, Low_id, name, role, msg):
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            # Получаем текущий максимальный тик
            cur.execute("SELECT MAX(Tick) FROM club_chats WHERE clubID=%s", (clubID,))
            max_tick = cur.fetchone()[0] or 0
            new_tick = max_tick + 1
        
            # Вставляем сообщение с корректным тиком
            cur.execute("""
                INSERT INTO club_chats 
                (clubID, Event, Tick, plrid, plrname, plrrole, Msg)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (clubID, event, new_tick, Low_id, name, role, msg))
        
            conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()

    def DeleteAllMsg(self, clubID):
        """Удаление всех сообщений клуба, если их больше 50."""
        conn = DataBase.get_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM club_chats WHERE clubID=%s", (clubID,))
            fetch = cur.fetchall()
            if len(fetch) >= 50:
                cur.execute("DELETE FROM club_chats WHERE clubID=%s", (clubID,))
                conn.commit()
        except Error as e:
            print(f"[ERROR] MySQL error: {e}")
        finally:
            cur.close()
            conn.close()