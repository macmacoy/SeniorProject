
backgroundColor = 0, 0, 0
black = 0, 0, 0
white = 255, 255, 255
lightGray = 220, 220, 220
lightMediumGray = 170, 170, 170
mediumGray = 110, 110, 110
darkGray = 70, 70, 70

def getColorForLevel(level):
	if level == 1:
		return (51, 204, 51)
	elif level == 2:
		return (0, 153, 255)
	elif level == 3:
		return (215, 215, 0)
	elif level == 4:
		return (255, 153, 51)
	elif level == 5:
		return (255, 102, 102)
	elif level == 6:
		return (102, 102, 255)
	return white

def getColorForChord(chord):
	if chord == "G":
		return (2, 224, 9)
	if chord == "Em":
		return (226, 151, 0)
	if chord == "C":
		return (219, 12, 8)
	if chord == "D":
		return (4, 89, 226)
	else:
		print("chord color not found")
		return (200,0,0)