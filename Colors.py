
turquoise = 26, 188, 156
greensea = 22, 160, 133
emerald = 46, 204, 113
nephritis = 39, 174, 96
peterriver = 52, 152, 219
belizehole = 41, 128, 185
amethyst = 155, 89, 182
wisteria = 142, 68, 173
wetasphalt = 52, 73, 94
midnightblue = 44, 62, 80
sunflower = 241, 196, 15
orange = 243, 156, 18
carrot  =230, 126, 34
pumpkin = 211, 84, 0
alizarin = 231, 76, 60
pomegranate = 192, 57, 43
clouds = 236, 240, 241
silver = 189, 195, 199
concrete = 149, 165, 166
asbestos = 127, 140, 141

backgroundColor = 0, 0, 0
black = 0, 0, 0
white = 255, 255, 255
lightGray = clouds
lightMediumGray = silver
mediumGray = concrete
darkGray = asbestos

majorChords = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
minorChords = ["Am","A#m","Bm","Cm","C#m","Dm","D#m","Em","Fm","F#m","Gm","G#m"]
chords = majorChords + minorChords
colors = [turquoise, emerald, peterriver, amethyst, sunflower, carrot]
chordColors = {}
colorIndex = 0
for chord in chords:
	chordColors[chord] = colors[colorIndex]
	colorIndex = colorIndex + 1
	if colorIndex > 5:
		colorIndex = 0

def getColorForLevel(level):
	if level == 1:
		return emerald
	elif level == 2:
		return peterriver
	elif level == 3:
		return amethyst
	elif level == 4:
		return carrot
	elif level == 5:
		return alizarin
	elif level == 6:
		return nephritis
	return white

def getColorForChord(chord):
	return chordColors[chord]
