# Config.py
import json
import os

class Config:
    @staticmethod
    def GetValue():
        with open("config.json", "r") as f:
            return json.load(f)