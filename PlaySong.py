import sys, pygame
import time
import os
import threading
import Colors
from queue import Queue, Empty
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.locals import *
from Song import Song
from ChordRecognizer import madmomChord, closeStream

def listenForChords(q):
	while True:
		madmomChord(q)

q = Queue()

listeningThread = threading.Thread(target=listenForChords, args=(q,))
listeningThread.setDaemon(True)
listeningThread.start()

pygame.init()
pygame.font.init()

screenSize = (1400, 800)
chordDisplaySize = (screenSize[0], int(float(screenSize[1])/4))
chordDisplayPlacement = (0, 0.5*screenSize[1])
currentTimeMarkerSize = (5, chordDisplaySize[1]*1.2)
currentTimeMarkerPlacement = (screenSize[0]/2, chordDisplayPlacement[1]-(currentTimeMarkerSize[1]-chordDisplaySize[1])/2)
lyricPlacement = (screenSize[0]/2, screenSize[1]/10)

chordFontSize = 100
chordFont = pygame.font.SysFont('Comic Sans MS', chordFontSize)
lyricFontSize = 50
lyricFont = pygame.font.SysFont('Comic Sans MS', lyricFontSize)

chordDisplay = Surface(chordDisplaySize)
currentTimeMarker = Surface(currentTimeMarkerSize)

currentTimeMarker.fill(Colors.darkGray)

# flags = FULLSCREEN | DOUBLEBUF # fps is 4x better in fullscreen mode
flags = DOUBLEBUF
screen = pygame.display.set_mode(screenSize, flags)
screen.set_alpha(None)

timeIntervalOnScreen = 5.0 # seconds

def userHasQuit():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return True
	return False

def toSeconds(millis):
	return float(millis)*0.001

def isInTimeRange(chord, timeRangeOnScreen):
	if chord["start"] > timeRangeOnScreen["start"] and chord["start"] < timeRangeOnScreen["end"]:
		return True
	elif chord["end"] > timeRangeOnScreen["start"] and chord["end"] < timeRangeOnScreen["end"]:
		return True
	elif chord["start"] < timeRangeOnScreen["start"] and chord["end"] > timeRangeOnScreen["end"]:
		return True
	else:
		return False

def score(timeoff):
	if(timeoff < 2.5):
		return (float(1) - (float(1)/float(15))*timeoff*timeoff)
	else:
		return ((float(1) - (float(1)/float(6))*timeoff))

song = Song("tests/test_song.json")
chords = song.chords
lyrics = song.lyrics

totalScore = float(0)
chordScore = float(0)
hit = []
for chord in chords:
	hit.append(False)

clock = pygame.time.Clock()
start = toSeconds(pygame.time.get_ticks())
now = start

chordIndex = 0
lyricIndex = 0
lyricChanged = True

timeRangeOnScreen = {"start":0.0, "end":0.0}
while now < song.duration:
	# user quits
	if userHasQuit():
		sys.exit()

	if (now > chords[chordIndex]["end"]):
		chordIndex += 1
	if (now > lyrics[lyricIndex]["end"]):
		lyricIndex += 1
		lyricChanged = True

	timeRangeOnScreen["start"] = now-timeIntervalOnScreen/2
	timeRangeOnScreen["end"] = now+timeIntervalOnScreen/2

	firstPixelOfChord = 0
	lastPixelOfChord = 0
	i = 0
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
			try:  
				c = q.get_nowait() # or q.get(timeout=.1)
				if c == chords[chordIndex]["chord"]:
					hit[chordIndex] = True
				lastChordCheck = now
				# print(c)
			except Empty:
			    pass
			if hit[i]:
				chordDisplay.fill(Colors.getColor(chord["chord"]), Rect(firstPixelOfChord, 0, lastPixelOfChord-firstPixelOfChord, chordDisplaySize[1]))
				chordText = chordFont.render(chord["chord"], False, Colors.white)
			else:
				chordDisplay.fill(Colors.lightGray, Rect(firstPixelOfChord, 0, lastPixelOfChord-firstPixelOfChord, chordDisplaySize[1]))
				chordText = chordFont.render(chord["chord"], False, Colors.mediumGray)
			firstPixelOfText = ((chord["start"] - timeRangeOnScreen["start"])/timeIntervalOnScreen)*chordDisplaySize[0]
			chordDisplay.blit(chordText, (firstPixelOfText+25,(chordDisplaySize[1]/2)-(chordFontSize/3)))
		i += 1
	chordDisplay.fill(Colors.backgroundColor, Rect(lastPixelOfChord, 0, chordDisplaySize[0]-lastPixelOfChord, chordDisplaySize[1]))

	if lyricChanged:
		screen.fill(Colors.backgroundColor)
		lyricText = lyricFont.render(lyrics[lyricIndex]["lyric"], False, Colors.white)
		centeredLyricPlacement = (lyricPlacement[0]-lyricText.get_rect().width/2, lyricPlacement[1])
		screen.blit(lyricText, centeredLyricPlacement)

	screen.blit(chordDisplay, chordDisplayPlacement)
	screen.blit(currentTimeMarker, currentTimeMarkerPlacement)

	if lyricChanged:
		lyricChanged = False
		pygame.display.flip()
	else:
		pygame.display.update(chordDisplay.get_rect())
		# pygame.display.flip()

	clock.tick()
	now = toSeconds(pygame.time.get_ticks()) - start

print ("fps: " + str(clock.get_fps()))
# closeStream()
sys.exit()
