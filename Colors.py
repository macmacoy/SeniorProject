
backgroundColor = 0, 0, 0
white = 255, 255, 255
lightGray = 220, 220, 220
mediumGray = 110, 110, 110
darkGray = 70, 70, 70

def getColor(chord):
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