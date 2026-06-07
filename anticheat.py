import json
import os
import pytz
import schedule
import time
from datetime import datetime, timedelta

last_battle_times = {}
BAN_LOG_FILE = 'bans.log'
CONFIG_FILE = 'config.json'
BATTLE_LOG_FILE = 'JSON/battleends.json'
BANS_FILE = 'JSON/banned.json'
BATTLE_BAN_LOG_FILE = 'JSON/battlebanlog.json'

def log_ban(low_id, time_diff, trophy_change):
    msk_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
    log_entry = (
        f"[{msk_time}] BAN {low_id} | "
        f"Interval: {time_diff:.1f}s | "
        f"Trophies: +{trophy_change}\n"
    )
    with open(BAN_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def load_bans():
    try:
        with open(BANS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_bans(bans):
    with open(BANS_FILE, 'w') as f:
        json.dump(bans, f, indent=4)

def log_battle_ban(low_id, battle_entries):
    try:
        battle_logs = {}
        try:
            with open(BATTLE_BAN_LOG_FILE, 'r') as f:
                battle_logs = json.load(f)
        except FileNotFoundError:
            pass
        battle_logs[str(low_id)] = battle_entries[-2:] if len(battle_entries) >= 2 else battle_entries
        with open(BATTLE_BAN_LOG_FILE, 'w') as f:
            json.dump(battle_logs, f, indent=4)
    except Exception:
        pass

def check_battle_log():
    banned_ids = set(load_bans().keys())
    new_bans = set()
    player_battles = {}

    if not os.path.exists(BATTLE_LOG_FILE):
        return

    with open(BATTLE_LOG_FILE, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                low_id = entry.get('low_id')
                trophy_change = entry.get('trophy_change', 0)
                timestamp_str = entry.get('timestamp', '')

                if not low_id or not timestamp_str or str(low_id) in banned_ids:
                    continue

                try:
                    end_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S MSK')
                except ValueError:
                    continue

                if low_id not in player_battles:
                    player_battles[low_id] = []
                player_battles[low_id].append({'timestamp': timestamp_str, 'trophy_change': trophy_change})

                ban_reason = []
                time_diff = 0

                if low_id in last_battle_times:
                    prev_time = last_battle_times[low_id]
                    time_diff = (end_time - prev_time).total_seconds()
                    if 0 < time_diff < 30:
                        ban_reason.append(f"interval {time_diff:.1f}s")
                
                if trophy_change > 3:
                    ban_reason.append(f"+{trophy_change} trophies")

                if len(ban_reason) == 2:
                    new_bans.add(low_id)
                    log_ban(low_id, time_diff, trophy_change)
                    log_battle_ban(low_id, player_battles[low_id])

                last_battle_times[low_id] = end_time

            except (json.JSONDecodeError, KeyError):
                continue

    if new_bans:
        bans = load_bans()
        for low_id in new_bans:
            low_id_str = str(low_id)
            ban_count = bans.get(low_id_str, {}).get('ban_count', 0) + 1
            reason = "Использование запрещенного стороннего программного обеспечения"
            if ban_count == 1:
                unban_date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            elif ban_count == 2:
                unban_date = (datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                unban_date = None
            bans[low_id_str] = {
                'reason': reason,
                'unban_date': unban_date,
                'ban_count': ban_count
            }
        save_bans(bans)

def clear_battle_log():
    if os.path.exists(BATTLE_LOG_FILE):
        with open(BATTLE_LOG_FILE, 'w') as f:
            f.write('')

def main():
    msk_tz = pytz.timezone('Europe/Moscow')
    schedule.every().day.at("12:00", msk_tz).do(clear_battle_log)
    schedule.every(1).seconds.do(check_battle_log)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()