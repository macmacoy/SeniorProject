import sys, pygame
import time
import os
from pygame.surface import Surface
from pygame.rect import Rect
from Song import Song
from ChordRecognizer import madmomChord, RECORD_SECONDS

pygame.init()
pygame.font.init()

screenSize = (1400, 800)
chordDisplaySize = (screenSize[0], int(float(screenSize[1])/4))
chordDisplayPlacement = 0.5 * screenSize[1]

chordFontSize = 100
chordFont = pygame.font.SysFont('Comic Sans MS', chordFontSize)

screen = pygame.display.set_mode(screenSize, pygame.RESIZABLE)
chordDisplay = Surface(chordDisplaySize)

timeIntervalOnScreen = 4.0 # seconds

song = Song("tests/test_song.json")
chords = song.chords
lyrics = song.lyrics

def isInTimeRange(chord, timeRangeOnScreen):
	if chord["start"] > timeRangeOnScreen["start"] and chord["start"] < timeRangeOnScreen["end"]:
		return True
	if chord["end"] > timeRangeOnScreen["start"] and chord["end"] < timeRangeOnScreen["end"]:
		return True
	else:
		return False

def userHasQuit():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return True
	return False

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
		return (200,0,0)

backgroundColor = 0, 0, 0

start = time.time()
now = start
timeRangeOnScreen = {"start":0.0, "end":0.0};
while now - start < song.duration:
	# user quits
	if userHasQuit():
		sys.exit()

	now = time.time()-start

	timeRangeOnScreen = {"start":now-timeIntervalOnScreen/2, "end":now+timeIntervalOnScreen/2}
	firstPixelOfChord = 0
	lastPixelOfChord = 0
	for chord in chords:
		if isInTimeRange(chord,timeRangeOnScreen):
			if chord["start"] > timeRangeOnScreen["start"]:
				firstPixelOfChord = ((chord["start"] - timeRangeOnScreen["start"])/timeIntervalOnScreen)*chordDisplaySize[0]
			else:
				firstPixelOfChord = 0
			if chord["end"] < timeRangeOnScreen["end"]:
				lastPixelOfChord = ((chord["end"] - timeRangeOnScreen["start"])/timeIntervalOnScreen)*chordDisplaySize[0]
			else:
				lastPixelOfChord = chordDisplaySize[0]
			chordDisplay.fill(getColor(chord["chord"]), Rect(firstPixelOfChord, 0, lastPixelOfChord-firstPixelOfChord, chordDisplaySize[1]))
			chordText = chordFont.render(chord["chord"], False, (255, 255, 255))
			firstPixelOfText = ((chord["start"] - timeRangeOnScreen["start"])/timeIntervalOnScreen)*chordDisplaySize[0]
			chordDisplay.blit(chordText, (firstPixelOfText+25,(chordDisplaySize[1]/2)-(chordFontSize/3)))
	if lastPixelOfChord < chordDisplaySize[0]:
		chordDisplay.fill(backgroundColor, Rect(lastPixelOfChord, 0, chordDisplaySize[0]-lastPixelOfChord, chordDisplaySize[1]))

	screen.fill(backgroundColor)
	screen.blit(chordDisplay, (0, chordDisplayPlacement))
	pygame.display.flip()
sys.exit()