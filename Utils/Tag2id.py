# -*- coding: utf-8 -*-
import sys

def getId(Hashtag):
    TagChar = ("0", "2", "8", "9", "P", "Y", "L", "Q", "G", "R", "J", "C", "U", "V")
    
    if not Hashtag.startswith('#'):
        print('Wrong Hashtag: должен начинаться с #')
        return None

    TagArray = list(Hashtag[1:].upper())
    Id = 0
    for Character in TagArray:
        try:
            CharIndex = TagChar.index(Character)
        except ValueError:
            print('Wrong Hashtag: допустимые символы — "0", "2", "8", "9", "P", "Y", "L", "Q", "G", "R", "J", "C", "U", "V"')
            return None
        Id = Id * len(TagChar) + CharIndex

    Low = Id >> 8
    return Low



def getHLid(Hashtag):
	TagChar = ("0", "2", "8", "9", "P", "Y", "L", "Q", "G", "R", "J", "C", "U", "V")
	if not Hashtag.startswith('#'):
		print('Wrong Hashtag')
		return


	TagArray = list(Hashtag[1:].upper())
	Id = 0
	for i in range(len(TagArray)):
		Character = TagArray[i]
		try:
			CharIndex = TagChar.index(Character)
		except ValueError:
			print('Wrong Hashtag : should only contain "0", "2", "8", "9", "P", "Y", "L", "Q", "G", "R", "J", "C", "U" or "V"')
			sys.exit()
		Id *= len(TagChar)
		Id += CharIndex

	HighLow = []
	HighLow.append(Id % 256)
	HighLow.append((Id - HighLow[0]) >> 8)


	return HighLow