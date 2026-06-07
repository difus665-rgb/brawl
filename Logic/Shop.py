import json, random

class Shop:
    """
    << Список ID предложений в магазине >>

    0 = Бесплатный ящик Brawl Box
    1 = Золото
    2 = Случайный боец
    3 = Боец
    4 = Скин
    5 = Звёздная сила / Гаджет
    6 = Ящик Brawl Box
    7 = Билеты (больше не работают)
    8 = Очки силы (для конкретного бойца)
    9 = Удвоитель жетонов
    10 = Мегаящик
    11 = Ключи (???)
    12 = Очки силы
    13 = Слот события (???)
    14 = Большой ящик
    15 = Рекламный ящик (больше не работает)
    16 = Гемы
    17 = Стардроп???
    19 = Пин для бойца
    20 = Коллекция пинов
    21 = Набор пинов
    22 = Набор пинов для бойца
    23 = Обычный пин (???)
    24 = Предложение скина в магазине (может не работать)
    94 = Скин (???)

    << Список BGR предложений в магазине >>

    Предложение жетонов = offer_generic
    Специальное предложение = offer_special
    Предложение за звёздные очки = offer_legendary
    Предложение монет = offer_coins (в версии 29 как offer_moon_festival)
    Предложение гемов = offer_gems
    Предложение ящиков = offer_boxes
    Предложение бойца = offer_finals
    Предложение Лунного Нового года = offer_lny
    Архивное предложение = offer_archive
    Хроматическое предложение = offer_chromatic
    Предложение Лунного фестиваля = offer_moon_festival
    Рождественское предложение = offer_xmas

    ET означает дополнительный текст.
    """
    
    token_doubler = {

        'Cost': 50,
        'Amount': 1000
    }
    
    gold = {
            'Cost': 20,
            'Amount': 150
}
    
    boxes = [
        {
            'Name': 'Big Box',
            'Cost': 30,
            'Multiplier': 3
        },

        {
            'Name': 'Mega Box',
            'Cost': 80,
            'Multiplier': 10
        }

    ]
    
    
    def loadOffers(self):
        self.offers=[]
        with open("JSON/offers.json", "r",encoding='utf-8') as f:
            data = json.load(f)
            for i in data.values():
                self.offers.append(i)
    def UpdateOfferData(self, i):
        with open("JSON/offers.json", "r",encoding='utf-8') as f:
            data = json.load(f)
        data[str(i)]["WhoBuyed"].append(int(self.player.low_id))
        with open("JSON/offers.json", "w",encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    def RemoveOffer(self, i):
        with open("JSON/offers.json", "r") as f:
            data = json.load(f, indent=4,)
        data.pop(str(i))
        with open("JSON/offers.json", "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)



    def EncodeShopOffers(self):
        Shop.loadOffers(self)
        wow = self.offers
        count = len(wow)
        self.writeVint(count)
        for i in range(count):
            item = wow[i]
            if item['ID'][0] != 0 and item['ID'][1] != 0 and item['ID'][2] != 0:
                self.writeVint(3)
                self.writeVint(item['ID'][0]) # ItemID
                self.writeVint(item['Multiplier'][0]) # Ammount
                self.writeScId(16, item['BrawlerID'][0])
                self.writeVint(item['SkinID'][0]) # ItemID
                self.writeVint(item['ID'][1]) # ItemID
                self.writeVint(item['Multiplier'][1]) # Ammount
                self.writeScId(16, item['BrawlerID'][1])
                self.writeVint(item['SkinID'][1]) # ItemID
                self.writeVint(item['ID'][2]) # ItemID
                self.writeVint(item['Multiplier'][2]) # Ammount
                self.writeScId(16, item['BrawlerID'][2])
                self.writeVint(item['SkinID'][2]) # ItemID

            elif item['ID'][0] != 0 and item['ID'][1] != 0:
                self.writeVint(2)
                self.writeVint(item['ID'][0]) # ItemID
                self.writeVint(item['Multiplier'][0]) # Ammount
                self.writeScId(16, item['BrawlerID'][0])
                self.writeVint(item['SkinID'][0]) # ItemID
                self.writeVint(item['ID'][1]) # ItemID
                self.writeVint(item['Multiplier'][1]) # Ammount
                self.writeScId(16, item['BrawlerID'][1])
                self.writeVint(item['SkinID'][1]) # ItemID

            else:
                if self.player.UnlockedBrawlers[f"{int(item['BrawlerID'][0])}"] == 1:
                    self.writeVint(1)
                    self.writeVint(item['ID'][0])
                    self.writeVint(item['Multiplier'][0])
                    self.writeScId(16, item['BrawlerID'][0])
                    self.writeVint(item['SkinID'][0])
                else:
                    self.writeVint(1)
                    self.writeVint(1) # ItemID
                    self.writeVint(0) # Ammount
                    self.writeScId(16, 0)
                    self.writeVint(0) # ItemID
                    
            self.writeVint(item['ShopType'])  # [0 = Offer, 2 = Skins 3 = Star Shop]

            self.writeVint(item['Cost'])  # Cost
            self.writeVint(item['Timer'])

            self.writeVint(item['OfferView']) # Offer View | 0 = Absolutely "NEW", 1 = "NEW", 2 = Viewed
            self.writeVint(100)
            if self.player.low_id in item["WhoBuyed"]:
                self.writeBoolean(True)
            else:
                if self.player.UnlockedBrawlers[f"{int(item['BrawlerID'][0])}"] == 0:
                    self.writeBoolean(True)
                else:
                    self.writeBoolean(False)
        
            self.writeBoolean(False)
            if self.player.UnlockedBrawlers[f"{int(item['BrawlerID'][0])}"] == 0:
                self.writeVint(0)
            else:
                self.writeVint(item['ShopDisplay'])# [0 = Normal, 1 = Daily Deals]
            self.writeVint(item['OldCost'])#oldCost
            self.writeVint(0)

            self.writeInt(0)
            self.write_string_reference(item['OfferTitle'])
            self.writeBoolean(False)
            self.writeString(item['OfferBGR'])
            self.writeVint(0)
            self.writeBoolean(False)
            self.writeVint(item['ETType']) # Extra Text Type | 1 = Factor(?x),
            self.writeVint(item['ETMultiplier']) # Extra Text
		#shopend