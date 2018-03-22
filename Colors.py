
backgroundColor = 0, 0, 0
black = 0, 0, 0
white = 255, 255, 255
lightGray = 220, 220, 220
lightMediumGray = 170, 170, 170
mediumGray = 110, 110, 110
darkGray = 70, 70, 70

def getColorForScore(score):
	if score > .85:
		return (153, 255, 51)
	if score > .75:
		return (204, 255, 51)
	if score > .65:
		return (255, 255, 0)
	if score > .5:
		return (255, 153, 0)
	else:
		return (204, 51, 0)

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