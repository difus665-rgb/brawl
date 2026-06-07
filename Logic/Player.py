import json
import os, json, datetime
import requests
from Utils.Config import Config
from Utils.Fingerprint import Fingerprint
from Utils.Helpers import Helpers
from Files.CsvLogic.Emotes import Emotes
from Utils.Tag2id import *
from Utils.Id2Tag import *
from Files.CsvLogic.Characters import Characters
from Files.CsvLogic.Skins import Skins
from Files.CsvLogic.Cards import Cards
from Files.CsvLogic.Regions import Regions

class Players:
	try:
		config = open('config.json', 'r')
		content = config.read()
	except FileNotFoundError:
		print("Creating config.json...")
		Config.create_config()
		config = open('config.json', 'r')
		content = config.read()

	settings = json.loads(content)

	# Player data
	BPTOKEN = 0
	BPXP = 0
	quests = []
	freepass = []
	freepassold = []
	buypass = []
	buypassold = []
	ip_address = []
	user_agent = "None"
	Region = "None"
	creation_date = "None"
	HashTag = "#8GG"
	# Brawler data
	skins_id = Skins().get_skins_id()
	emotes_id  = Emotes().get_emotes_id()
	brawlers_id = Characters().get_brawlers_id()
	card_skills_id = Cards().get_spg_id()
	card_unlock_id = Cards().get_brawler_unlock()
	high_id = 0
	low_id = 0
	token = Helpers().randomStringDigits()
	IsFacebookLinked = 0
	FacebookID = "None"
	FacebookToken = "None"
	box_id = 0
	map_id = 7
	slot_index = 0
	room_id = 0
	brawler_id = 0
	skin_id = 0
	dudu = 0
	ban = 0
	bulletX = 1
	bulletY = 1
	hasbollX = 3150
	hasbollY = 4950
	battleX = 3125
	battleY = 9500
	angle = 0
	hasboll = False
	hasgoal = 1
	bulletCount = 0
	charge = 3000
	checker = 0
	inmm = False
	index = 0
	ccc = ""
	trioWINS = 0
	sdWINS = 0
	theme = 14
	#newprl
	highest_trophies = 0
	Brawler_newTag = {str(i): 1 for i in range(40) if i != 33}
	trophies = 0
	brawlers_trophies = {}
	for id in brawlers_id:
		brawlers_trophies.update({f'{id}': brawlers_trophies})
	
	brawlers_trophies = {str(i): 0 for i in range(40) if i != 33}
	bet = 0
	betTok = 0
	#lobby box
	box = 0
	bigbox = 0
	#lobby box end
	online = 2
	state = 0
	brawlerPoints = {str(i): 0 for i in range(40) if i != 33}
	UnlockedBrawlers = {str(i): (1 if i == 0 else 0) for i in range(40) if i != 33}
	brawlerPowerLevel = {str(i): 0 for i in range(40) if i != 33}
	UnlockedSkins = {str(i): 0 for i in range(301)}
	StarPowerUnlocked = {str(i): 0 for i in range(76, 402)}
	UnlockedPins = {str(i): 0 for i in range(406)}
	skinremove = 0
	brawlerem = 1
	starpoints = 0
	tickets = 0
	gems = 0
	gold = 100
	Troproad = 1
	profile_icon = 0
	name_color = 0
	player_experience = 0
	vip = 0
	notifRead = False
	notifRead2 = False
	notifications = {"2": {"ID": 3, "Read": False, "Timer": 1739268880, "Desc": "Добро пожаловать в OWN BRAWL!", "BrawlerID": 0, "SkinID": 0, "Gems": 30}}
	# Socket
	ClientDict = {}
	
	BrawlersUnlockedState = {}
	brawlers_spg_unlock = {}

	gadget = 255
	starpower = 76

	name = "VBC26"
	player_experience = 0
	do_not_distrub = 0

	test = 0
	debacle = 0
	boss_fight = 0
	robo_cabin = 0
	power_race = 0
	duo_wins = 0
	solo_wins = {}
	ThreeVSThree_wins = 0
	tokensdoubler = 0
	player_tokens = 200
	tokens = 0
	last_token_time = 0

	# Alliances
	club_high_id = 0
	club_low_id = 0
	club_role = 0

	# Message stuff...
	update_url = 'https://t.me/RoyaleStudio/339'
	patch_url = 'https://t.me/RoyaleStudio/339'
	patch_sha = Fingerprint.loadFinger("GameAssets/fingerprint.json")
	maintenance_time = 0

	err_code = 7
	maintenance = False
	patch = False

	if settings['Patch']:
		error_code = 7
		patch = True

	if settings['Maintenance']:
		err_code = 10
		maintenance = True
		maintenance_time = settings['MaintenanceTime']

	# Chat data
	message_tick = 0
	bot_message_tick = 0

    # Friendly game (Teams, info, result)
	battle_result = 0
	game_type = 0
	use_gadget = 1
	ctick = 0
	gadget = 255
	starpower = 76
	isReady = 0
	message = 0
	rank = 0
	team = 0
	isReady = 0

	bot1 = 0
	bot1_n = None
	bot1_team = 0
	bot2 = 0
	bot2_n = None
	bot2_team = 0
	bot3 = 0
	bot3_n = None
	bot3_team = 0
	bot4 = 0
	bot4_n = None
	bot4_team = 0
	bot5 = 0
	bot5_n = None
	bot5_team = 0
	bot6 = 0
	bot6_n = None
	bot6_team = 0
	bot7 = 0
	bot7_n = None
	bot7_team = 0
	bot8 = 0
	bot8_n = None
	bot8_team = 0
	bot9 = 0
	bot9_n = None
	bot9_team = 0

	def CreateNewBrawlersList():
		Players.BrawlersUnlockedState = {}
		for id in Players.brawlers_id:
			if id == 0:
				Players.BrawlersUnlockedState[str(id)] = 1
			else:
				Players.BrawlersUnlockedState[str(id)] = 0
		return Players.BrawlersUnlockedState

	def __init__(self, device):
		self.device = device