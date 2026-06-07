import time, json, random, schedule
from database.DataBase import DataBase

class EventSlots:

    def loadEvents(self):
    	with open("JSON/events.json", "r") as f:
    		data=json.load(f)
    		return data

    def updateEventData(self, i, new):
    	with open("JSON/events.json", "r") as f:
    		data=json.load(f)
    	try:
    		data[str(i)]["ID"]=new
    	except:
    		data[str(i)]={}
    		data[str(i)]["ID"]=new
    	with open("JSON/events.json", "w") as f:
    		json.dump(data,f)

    def updateEventClaimed(self, i, new):
        with open("JSON/events.json", "r") as f:
            data=json.load(f)
        try:
            data[str(i)]["Collected"]=[new]
        except:
            data[str(i)]={}
            data[str(i)]["Collected"]=[new]
        with open("JSON/events.json", "w") as f:
            json.dump(data,f)

    def SetEventClaimed(self):
        TokenNew = 0
        EventSlots.updateEventClaimed(self, 0, TokenNew)
        EventSlots.updateEventClaimed(self, 1, TokenNew)
        EventSlots.updateEventClaimed(self, 2, TokenNew)
        EventSlots.updateEventClaimed(self, 3, TokenNew)
        EventSlots.updateEventClaimed(self, 4, TokenNew)
        EventSlots.updateEventClaimed(self, 5, TokenNew)
        EventSlots.updateEventClaimed(self, 6, TokenNew)

        schedule.every().day.at("12:00").do(SetEventClaimed)

    def SetEventSlotsData(self):
        gems = random.choice([7,8,9,10,11,12])
        sd = random.choice([13,14,15,16,32,33,43,45])
        bb = random.choice([50,51,132,144,160])
        heist = random.choice([4,5,54,81,82,83,159,295,301,336])
        star = random.choice([18,19,23,53,81,82,83,302])
        robowars = random.choice([97,98,99,131,142,264])
        EventSlots.updateEventData(self, 0, gems)
        EventSlots.updateEventData(self, 1, sd)
        EventSlots.updateEventData(self, 2, bb)
        EventSlots.updateEventData(self, 3, heist)
        EventSlots.updateEventData(self, 4, star)
        EventSlots.updateEventData(self, 5, robowars)
        #Maps
        #57 boss savasi - machine zone

    def Timer(self):
        result = time.localtime(int(time.time()))

        return (86400 - (result.tm_sec + (result.tm_min * 60) + (result.tm_hour * 3600)))

    def offset(self):
        events = EventSlots.loadEvents(self)
        Timer = EventSlots.Timer(self)

        count = len(events)
        self.writeVint(count)

        maps = events.values()

        for event in maps:

            self.writeVint(list(maps).index(event) + 1)
            self.writeVint(list(maps).index(event) + 1)
            self.writeVint(event['Ended'])  # IsActive | 0 = Active, 1 = Disabled
            self.writeVint(Timer)  # Timer

            self.writeVint(event['Tokens'])
            self.writeScId(15, event["ID"])

            if self.player.low_id in event['Collected']:
                self.writeVint(2)
            else:
                self.writeVint(1)

            self.writeString("Удвоенные шлюхи") # "Double Experience Event" Text
            self.writeVint(0)
            self.writeVint(0)  # Powerplay game played
            self.writeVint(0)  # Powerplay game left maximum

            if event['Modifier'] > 0:
                self.writeBoolean(True)
                self.writeVint(1)
            else:
                self.writeBoolean(False)

            self.writeVint(0)
            self.writeVint(0)