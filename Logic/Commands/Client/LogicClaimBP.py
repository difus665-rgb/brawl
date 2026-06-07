class LogicClaimBP(Writer):
    def encode(self, client, player, id, k, bp, id2=0):
        self.client = client
        self.player = player
        self.id = id
        self.id2 = id2
        self.k = k
        self.bp = bp
        
        
        for i in range(61):
            if self.id == i:
                self.player.freepass = self.player.freepass + 4 * (2 ** i)
                DataBase.replaceValue(self, "freepass", self.player.freepass)
                DataBase.replaceValue(self, "BPTOKEN", self.player.BPTOKEN)
                break
        
        # Handling different reward cases based on `id`
        if self.id in [0,2,4,6,8,12,14,16,18,21,24,26,29,32,34,37,46,49,52,56,58]: #маленькие ящики
            LogicBoxDataCommand(self.client, self.player, 2, self.bp, self.id, 12).send() # 12 значит маленький ящик
        if self.id in [10,20,30,40,45,50,55,59]:
            LogicBoxDataCommand(self.client, self.player, 2, self.bp, self.id, 11).send() # 11 мега
        if self.id in [1,5,9,13,17,21,25,28,33,36,38,41,44,48,53]:
            LogicBoxDataCommand(self.client, self.player, 2, self.bp, self.id, 10).send() # 10 большой
        if self.id == 3: # гемы
            LogicBP(self.client, self.player, self.bp, self.id, 10, 8, 0, [0, 0], 0).send()
            self.player.gems = self.player.gems + 10
            DataBase.replaceValue(self, 'gems', self.player.gems)
        if self.id == 7: # монеты
            LogicBP(self.client, self.player, self.bp, self.id, 50, 7, 0, [0, 0], 0).send() #gold
            self.player.gold = self.player.gold + 50
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.id == 15: # гемы
            LogicBP(self.client, self.player, self.bp, self.id, 20, 8, 0, [0, 0], 0).send()
            self.player.gems = self.player.gems + 10
            DataBase.replaceValue(self, 'gems', self.player.gems)
        if self.id == 19: # золото 
            LogicBP(self.client, self.player, self.bp, self.id, 50, 7, 0, [0, 0], 0).send() #gold
            self.player.gold = self.player.gold + 50
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.id == 23: # гемы
            LogicBP(self.client, self.player, self.bp, self.id, 10, 8, 0, [0, 0], 0).send()
            self.player.gems = self.player.gems + 10
            DataBase.replaceValue(self, 'gems', self.player.gems)
        if self.id == 27: # значки усиления
            LogicBP(self.client, self.player, self.bp, self.id, 50, 6, self.k, [0, 0], 0).send()
        if self.id == 31: # золото
            LogicBP(self.client, self.player, self.bp, self.id, 100, 7, 0, [0, 0], 0).send() #gold
            self.player.gold = self.player.gold + 100
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.id == 35: # гемы
            LogicBP(self.client, self.player, self.bp, self.id, 10, 8, 0, [0, 0], 0).send()
            self.player.gems = self.player.gems + 10
            DataBase.replaceValue(self, 'gems', self.player.gems) #gems
        if self.id == 42: # ящик
            LogicBoxDataCommand(self.client, self.player, 2, self.bp, self.id, 12).send()
        if self.id == 43: # гемы
            LogicBP(self.client, self.player, self.bp, self.id, 10, 8, 0, [0, 0], 0).send()
            self.player.gems = self.player.gems + 10
            DataBase.replaceValue(self, 'gems', self.player.gems) #gems
        if self.id == 47: # золото
            LogicBP(self.client, self.player, self.bp, self.id, 200, 7, 0, [0, 0], 0).send() #gold
            self.player.gold = self.player.gold + 200
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.id == 51: # гемы
            LogicBP(self.client, self.player, self.bp, self.id, 20, 8, 0, [0, 0], 0).send()
            self.player.gems = self.player.gems + 20
            DataBase.replaceValue(self, 'gems', self.player.gems)
        if self.id == 57: # золото
            LogicBP(self.client, self.player, self.bp, self.id, 500, 7, 0, [0, 0], 0).send() #gold
            self.player.gold = self.player.gold + 500
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.id2 == 60: # усилялка 
            LogicBP(self.client, self.player, self.bp, self.id, 500, 6, self.k, [0, 0], 0).send() #zalupaя
    
    def encode2(self, client, player, id, k, bp, id2=0):
        self.client = client
        self.player = player
        self.id = id
        self.id2 = id2
        self.k = k
        self.bp = bp
        
        
        for i in range(61):
            if self.id == i:
                self.player.buypass = self.player.buypass + 4 * (2 ** i)
                DataBase.replaceValue(self, "buypass", self.player.buypass)
                DataBase.replaceValue(self, "BPTOKEN", self.player.BPTOKEN)
                break
        
        
        if self.id in [1,3,7,9,12,17,20,27,35,41]: # Brawl
            LogicBoxDataCommand(self.client, self.player, 2, self.bp, self.id, 12).send()
        if self.id in [0,5,10,23,33,37]: # Mega
            LogicBoxDataCommand(self.client, self.player, 2, self.bp, self.id, 11).send()
        if self.id in [2,4,8,25]:
            LogicBP(self.client, self.player, self.bp, self.id, 100, 7, 0, [0, 0], 0).send() # gold 100
            self.player.gold = self.player.gold + 100
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.id in [14,21]:
            LogicBP(self.client, self.player, self.bp, self.id, 200, 7, 0, [0, 0], 0).send() # gold 200
            self.player.gold = self.player.gold + 200
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.id in [31]:
            LogicBP(self.client, self.player, self.bp, self.id, 500, 7, 0, [0, 0], 0).send() # gold 500
            self.player.gold = self.player.gold + 500
            DataBase.replaceValue(self, 'gold', self.player.gold)
        if self.id in [16,19,22,24,26,28,30,32,34,36,38,40,42]: # 217 geyl
            LogicBP(self.client, self.player, self.bp, self.id, 20, 8, 0, [0, 0], 0).send()
            self.player.gems = self.player.gems + 20
            DataBase.replaceValue(self, 'gems', self.player.gems) # gems
        if self.id == 15: # макс
            LogicBP(self.client, self.player, self.bp, self.id, 1, 1, 15, [0, 0], 0).send()
            self.player.UnlockedBrawlers[str(15)] = 1
            DataBase.replaceValue(self, 'UnlockedBrawlers', self.player.UnlockedBrawlers)
        if self.id == 43: # GEYL скин
            LogicBP(self.client, self.player, self.bp, self.id, 1, 9, 0, [29, 214], 0).send()
            self.player.UnlockedSkins[str(214)] = 1
            DataBase.replaceValue(self, 'UnlockedSkins', self.player.UnlockedSkins)