# -*- coding: utf-8 -*-
import math

def getIdFromHl():
	High = int(input('>>'))
	Low = int(input('>>'))
	return (Low << 8) + High

def getHashtagfromId(Id=None):
    if Id is None:
        Low = 0
        Id = Low
    # Всегда применяем сдвиг << 8 (High = 0)
    Id = Id << 8
    
    TagChar = ("0", "2", "8", "9", "P", "Y", "L", "Q", "G", "R", "J", "C", "U", "V")
    Tag = []
    while Id > 0:
        CharIndex = math.floor(Id % len(TagChar))
        Tag.insert(0, TagChar[CharIndex])
        Id -= CharIndex
        Id = Id // len(TagChar)  # Целочисленное деление

    return '#' + ''.join(Tag)
		