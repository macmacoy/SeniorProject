import sys, pygame
import time
import os
import threading
import Colors
import ChordRecognizer
from queue import Queue, Empty
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.locals import *
from Song import Song
from Images import chordImages, feedbackImages

def PlaySong():
	song = Song("tests/test_song.json")
	chords = song.chords
	lyrics = song.lyrics

	## start thread that listens for chords
	def listenForChords(q):
		while True:
			ChordRecognizer.madmomChord(q)

	q = Queue()

	listeningThread = threading.Thread(target=listenForChords, args=(q,))
	listeningThread.setDaemon(True)
	listeningThread.start()

	## placement and scaling of graphic components
	chordDisplaySize = (screenSize[0], int(float(screenSize[1])/5))
	chordDisplayPlacement = (0, 0.6*screenSize[1])
	currentTimeMarkerSize = (5, chordDisplaySize[1]*1.2)
	currentTimeMarkerPlacement = (screenSize[0]/2, chordDisplayPlacement[1]-(currentTimeMarkerSize[1]-chordDisplaySize[1])/2)
	# lyricPlacement = (screenSize[0]/2, screenSize[1]/12) # lyrics at top
	lyricPlacement = (screenSize[0]/2, screenSize[1]/2.2) # lyrics in middle
	feedbackSize = (int(screenSize[1]/3), int(screenSize[1]/3))
	feedbackPlacement = (screenSize[0]/12, screenSize[0]/8)
	# currentChordImagePlacement = (screenSize[0]/2, screenSize[1]/5) # chords in middle
	# nextChordImagePlacement = (screenSize[0]*(3/4), screenSize[1]/6)
	currentChordImagePlacement = (screenSize[0]/2, screenSize[1]/14) # chords at top
	nextChordImagePlacement = (screenSize[0]*(3/4), screenSize[1]/10)

	chordFontSize = 100
	chordFont = pygame.font.SysFont('Comic Sans MS', chordFontSize)
	lyricFontSize = 50
	lyricFont = pygame.font.SysFont('Comic Sans MS', lyricFontSize)

	## intialize graphic components
	chordDisplay = Surface(chordDisplaySize)
	currentTimeMarker = Surface(currentTimeMarkerSize)
	currentTimeMarker.fill(Colors.darkGray)
	for i in range(0, len(feedbackImages)):
		feedbackImages[i] = pygame.transform.scale(feedbackImages[i], (int(feedbackImages[i].get_width()/3.5), int(feedbackImages[i].get_height()/3.5)))
	feedbackDisplay = feedbackImages[4] # initial

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

	def updateFeedbackScore():
		if(hit[chordIndex]):
			chordScore[chordIndex] = score(now-chords[chordIndex]["start"]-RECORD_SECONDS)
		else:
			chordScore[chordIndex] = 0
		totalScore = 0
		for j in range(0,chordIndex+1):
			totalScore += chordScore[j]
		totalScore = totalScore / (chordIndex+1)
		if (totalScore > 90):
			return feedbackImages[7]
		elif (totalScore > 80):
			return feedbackImages[6]
		elif (totalScore > 70):
			return feedbackImages[5]
		elif (totalScore > 60):
			return feedbackImages[4]
		elif (totalScore > 50):
			return feedbackImages[3]
		elif (totalScore > 40):
			return feedbackImages[2]
		elif (totalScore > 30):
			return feedbackImages[1]
		else:
			return feedbackImages[0]
			print("feedback display changed")

	def scaleForCurrentChord(image):
		return pygame.transform.scale(image, (int(image.get_width()/1), int(image.get_height()/1)))

	def scaleForNextChord(image):
		return pygame.transform.scale(image, (int(image.get_width()/1), int(image.get_height()/1)))

	totalScore = float(0)
	chordScore = len(chords)*[float(0)]
	hit = len(chords)*[False]

	clock = pygame.time.Clock()
	start = toSeconds(pygame.time.get_ticks())
	now = start

	chordIndex = 0
	lyricIndex = 0
	chordChanged = True
	lyricChanged = True

	timeRangeOnScreen = {"start":0.0, "end":0.0}
	while now < song.duration:
		# user quits
		if userHasQuit():
			sys.exit()

		if (now > chords[chordIndex]["end"]):
			if(not hit[chordIndex]):
				feedbackDisplay = updateFeedbackScore()
			chordIndex += 1
			chordChanged = True
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
						if hit[chordIndex] == False:
							feedbackDisplay = updateFeedbackScore()
						hit[chordIndex] = True
				except Empty:
				    pass
				if hit[i]:
					chordDisplay.fill(Colors.getColorForChord(chord["chord"]), Rect(firstPixelOfChord, 0, lastPixelOfChord-firstPixelOfChord, chordDisplaySize[1]))
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

		# screen.blit(colorfulBackground, (0,0))
		screen.blit(chordDisplay, chordDisplayPlacement)
		screen.blit(currentTimeMarker, currentTimeMarkerPlacement)
		screen.blit(feedbackDisplay, feedbackPlacement)

		scaledCurrentImageChord = scaleForCurrentChord(chordImages[chords[chordIndex]["chord"]])
		scaledCurrentChordImagePlacement = (currentChordImagePlacement[0] - scaledCurrentImageChord.get_rect().width/2, currentChordImagePlacement[1])
		screen.blit(scaledCurrentImageChord, scaledCurrentChordImagePlacement)
		if(chordIndex != len(chords)-1):
			scaledNextImageChord = scaleForNextChord(chordImages[chords[chordIndex+1]["chord"]])
			scaledNextChordImagePlacement = (nextChordImagePlacement[0] - scaledNextImageChord.get_rect().width/2, nextChordImagePlacement[1])
			screen.blit(scaledNextImageChord, scaledNextChordImagePlacement)

		# if lyricChanged:
		# 	lyricChanged = False
		# 	pygame.display.flip()
		# else:
		# 	pygame.display.update(chordDisplay.get_rect())
			# pygame.display.flip()
		pygame.display.flip()

		clock.tick()
		now = toSeconds(pygame.time.get_ticks()) - start

	print ("fps: " + str(clock.get_fps()))
	# closeStream()
	sys.exit()

def PlayerStats():


## initialize graphics engine
pygame.init()
pygame.font.init()

screenSize = (1400, 800)

## set up full display
# flags = FULLSCREEN | DOUBLEBUF # fps is 4x better in fullscreen mode
flags = DOUBLEBUF
screen = pygame.display.set_mode(screenSize, flags)
screen.set_alpha(None)

# PlaySong()




