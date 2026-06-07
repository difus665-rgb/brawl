import os
import json
import requests
import time
from ipwhois import IPWhois
from Server.Login.LoginOkMessage import LoginOkMessage
from Server.Home.OwnHomeDataMessage import OwnHomeDataMessage
from Server.Login.LoginFailedMessage import LoginFailedMessage
from Utils.Helpers import Helpers
from database.DataBase import DataBase
from Server.Club.MyAllianceMessage import MyAllianceMessage
from Server.Club.AllianceStreamMessage import AllianceStreamMessage
from Server.Friend.FriendListMessage import FriendListMessage
from database.DevMessage import DevMessage
from Utils.Reader import BSMessageReader
from Utils.Tag2id import *
from Utils.Id2Tag import *

class LoginMessage(BSMessageReader):
    def __init__(self, client, player, initial_bytes):
        super().__init__(initial_bytes)
        self.player = player
        self.client = client

    def decode(self):
        self.player.high_id = self.read_int()
        self.player.low_id = self.read_int()
        self.player.token = self.read_string()
        self.major = self.read_int()
        self.minor = self.read_int()
        self.build = self.read_int()

    def process(self):
        with open('config.json', 'r') as config:
            settings = json.load(config)
        
        if self.check_ban():
            return

        if settings['maintenance']:
            self.player.err_code = 10
            LoginFailedMessage(self.client, self.player, "").send()
            return
        
        client_ip = self.client.getpeername()[0]
        region = self.get_region_by_ip(client_ip)
        self.player.Region = region
        
        if self.player.low_id == 0:
            plrsinfo = "database/Player/plr.db"
            if os.path.exists(plrsinfo):
                self.player.low_id = Helpers.randomID(self)
            else:
                self.player.low_id = 2
            self.player.HashTag = getHashtagfromId(self.player.low_id)
            self.player.token = Helpers().randomStringDigits()
            self.player.high_id = 0
            LoginOkMessage(self.client, self.player).send()
            DataBase.createAccount(self)
            OwnHomeDataMessage(self.client, self.player).send()
        
        if self.player.low_id >= 2:
            LoginOkMessage(self.client, self.player).send()
            OwnHomeDataMessage(self.client, self.player).send()
            try:
                MyAllianceMessage(self.client, self.player, self.player.club_low_id).send()
                AllianceStreamMessage(self.client, self.player, self.player.club_low_id, 0).send()
                DataBase.GetmsgCount(self, self.player.club_low_id)
            except:
                MyAllianceMessage(self.client, self.player, 0).send()
                AllianceStreamMessage(self.client, self.player, 0, 0).send()
            FriendListMessage(self.client, self.player).send()
            DevMessage(self.client, self.player).send()
        else:
            self.player.err_code = 8
            LoginFailedMessage(self.client, self.player, "Аккаунт не найден, удалите все данные о игре!").send()
            
    def get_region_by_ip(self, ip_address):
        try:
            url = f'http://ip-api.com/json/{ip_address}'
            response = requests.get(url)
            data = response.json()
            if data.get('status') == 'fail':
                return 'Unknown'
            return data.get('countryCode', 'Unknown')
        except requests.exceptions.RequestException:
            return 'Unknown'

    def check_ban(self):
        try:
            with open('JSON/banned.json', 'r') as f:
                bans = json.load(f)
            ban_info = bans.get(str(self.player.low_id))
            if ban_info:
                reason = ban_info['reason']
                unban_date = ban_info['unban_date']
                if unban_date is None:
                    self.player.err_code = 13
                    LoginFailedMessage(self.client, self.player, f"Вы заблокированы навсегда. Причина: {reason}. Подать апелляцию: @zoxdev").send()
                    return True
                unban_timestamp = int(time.mktime(time.strptime(unban_date, "%Y-%m-%d %H:%M:%S")))
                if time.time() < unban_timestamp:
                    remaining_time = unban_timestamp - time.time()
                    days = int(remaining_time // 86400)
                    hours = int((remaining_time % 86400) // 3600)
                    minutes = int((remaining_time % 3600) // 60)
                    self.player.err_code = 11
                    LoginFailedMessage(self.client, self.player, f"Вы заблокированы. Причина: {reason}. До разбана: {days} дн {hours} ч {minutes} мин. Апелляция: @zoxdev").send()
                    return True
                else:
                    del bans[str(self.player.low_id)]
                    with open('JSON/banned.json', 'w') as f:
                        json.dump(bans, f, indent=4)
            return False
        except FileNotFoundError:
            return False
        except Exception:
            return False