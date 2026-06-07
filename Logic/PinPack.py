from Utils.Writer import Writer
import random 
from database.DataBase import DataBase

class PinPack(Writer):

    def __init__(self, client, player):
        super().__init__(client)
        self.id = 24111
        self.player = player
        # Define pin rarities
        self.common = [1, 3, 5, 6, 8, 10, 13, 15, 18, 20, 24, 26, 30, 32, 35, 37, 40, 42, 45, 47, 50, 52, 55, 57, 60, 62, 66, 68, 71, 73, 77, 79, 82, 84, 86, 89, 91, 95, 97, 100, 102, 105, 107, 110, 112, 115, 117, 120, 122, 125, 127, 130, 132, 134, 136, 138, 141, 143, 145, 147, 149, 152, 154, 160, 162, 165, 167, 171, 173, 178, 180, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 216, 218, 219, 228, 230, 231, 278, 280, 281, 284, 286, 287, 290, 292, 302, 306, 308, 310, 337, 339, 341, 362, 364, 366, 370, 372, 374, 378, 380, 382, 400, 402, 404]
        self.rare = [2, 9, 14, 19, 25, 31, 36, 41, 46, 51, 56, 61, 67, 72, 78, 85, 90, 96, 101, 106, 111, 116, 121, 126, 131, 137, 142, 148, 153, 161, 166, 172, 179, 217, 229, 279, 285, 291, 307, 338, 363, 371, 379, 401]
        self.epic = [4, 11, 16, 21, 27, 33, 38, 43, 48, 53, 58, 63, 69, 74, 80, 87, 92, 98, 103, 108, 113, 118, 123, 128, 133, 139, 144, 150, 155, 163, 168, 174, 181, 220, 222, 223, 224, 225, 226, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 282, 288, 294, 295, 296, 297, 298, 299, 300, 301, 303, 304, 309, 311, 313, 314, 315, 316, 317, 318, 319, 329, 330, 331, 332, 333, 334, 335, 340, 342, 343, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 365, 367, 368, 373, 375, 376, 381, 383, 384, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 403, 405, 406]

    def get_random_pin(self, rarity_list):
        # Filter out already unlocked pins
        available_pins = [pin for pin in rarity_list if str(pin) not in self.player.UnlockedPins or self.player.UnlockedPins[str(pin)] != 1]
        
        if not available_pins:
            # If all pins are unlocked, just pick a random one from the rarity
            return random.choice(rarity_list)
        return random.choice(available_pins)

    def encode(self):
        # Get 2 common pins and 1 rare/epic pin
        pin_rewards = [
            self.get_random_pin(self.common),
            self.get_random_pin(self.common),
            self.get_random_pin(self.rare + self.epic)  # Combine rare and epic for 3rd pin
        ]
        
        # Write header
        self.writeVint(203)
        self.writeVint(0)
        self.writeVint(1)
        self.writeVint(100)  # Box ID
        
        # Write rewards count
        self.writeVint(len(pin_rewards))  # Number of items (3 pins)
        
        # Write each pin reward
        for pin_id in pin_rewards:
            self.writeVint(1)  # Reward amount
            self.writeVint(0)  # CsvID 16
            self.writeVint(11)  # Reward ID (pin)
            self.writeVint(0)  # CsvID 29
            self.writeScId(52, pin_id)  # Pin ID
            self.writeVint(0)  # CsvID 23
            self.writeVint(0)
            self.writeVint(0)
            
            # Update player's unlocked pins
            self.player.UnlockedPins[str(pin_id)] = 1
        
        # Save to database
        DataBase.replaceValue(self, 'UnlockedPins', self.player.UnlockedPins)
        
        for _ in range(13):
            self.writeVint(0)