#!/usr/bin/env pypy
import sys, pygame
import time
import os
import copy
import threading
from queue import Queue, Empty
from multiprocessing import Process, Pipe
# from threading import Thread
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.locals import *
from Song import Song
from ChordRecognizer import madmomChord, getStream, closeStream, RECORD_SECONDS

def listenForChords(you, audio, stream):
	while True:
		madmomChord(you,audio,stream)

me, you = Pipe()
audio, stream = getStream()

# q = Queue()
threads = []
threads.append(threading.Thread(target=listenForChords, args=(you,audio,stream)))
threads[-1].setDaemon(True)
threads[-1].start()

pygame.init()
pygame.font.init()

screenSize = (1400, 800)
chordDisplaySize = (screenSize[0], int(float(screenSize[1])/4))
chordDisplayPlacement = 0.5 * screenSize[1]

chordFontSize = 100
chordFont = pygame.font.SysFont('Comic Sans MS', chordFontSize)

flags = FULLSCREEN | DOUBLEBUF
# flags = DOUBLEBUF
screen = pygame.display.set_mode(screenSize, flags)
screen.set_alpha(None)
chordDisplay = Surface(chordDisplaySize)
chordDisplayRect = chordDisplay.get_rect()

timeIntervalOnScreen = 5.0 # seconds

def isInTimeRange(chord, timeRangeOnScreen):
	if chord["start"] > timeRangeOnScreen["start"] and chord["start"] < timeRangeOnScreen["end"]:
		return True
	elif chord["end"] > timeRangeOnScreen["start"] and chord["end"] < timeRangeOnScreen["end"]:
		return True
	elif chord["start"] < timeRangeOnScreen["start"] and chord["end"] > timeRangeOnScreen["end"]:
		return True
	else:
		return False

# def userHasQuit():
# 	for event in pygame.event.get():
# 		if event.type == pygame.QUIT:
# 			return True
# 	return False

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
gray = 220, 220, 220

song = Song("tests/test_song.json")
chords = song.chords
lyrics = song.lyrics

start = time.time()
now = time.time() - start
lastChordCheck = now
checkChordInterval = 0.35

totalScore = float(0)
chordScore = float(0)
hit = []
for chord in chords:
	hit.append(False)

chordIndex = 0

timeRangeOnScreen = {"start":0.0, "end":0.0};
while now < song.duration:
	# user quits
	# if userHasQuit():
	# 	sys.exit()

	now = time.time() - start

	if (now > chords[chordIndex]["end"]):
			chordIndex += 1

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
			if (now > (lastChordCheck + checkChordInterval)):
				c = me.recv()
				if c == chords[chordIndex]["chord"]:
					hit[i] = True
				lastChordCheck = now
				print(c)
				# try:
					# print (q.get())
					# q.task_done()
					# t = time.time()
					# print("blocked for " + str(time.time()-t))
					# for thread in threads:
					# 	print(thread.isAlive())
					# threads.append(threading.Thread(target=madmomChord, args=(you,audio,stream)))
					# threads[-1].setDaemon(True)
					# threads[-1].start()
				# except Empty:
				# 	print("got empty exception")
				# 	pass

				# try:
				# 	chordStr = q.get(False)
				# 	q.task_done()
				# 	print(str(now-lastChordCheck))
				# 	print(chordStr)
				# 	print("got from q")
				# 	p = Process(target=madmomChord, args=(q,))
				# 	p.daemon = True
				# 	p.start()
				# 	if chordStr == chords[chordIndex]["chord"]:
				# 		hit[chordIndex] = True
				# except Empty: 
				# 	pass
			if hit[i]:
				chordDisplay.fill(getColor(chord["chord"]), Rect(firstPixelOfChord, 0, lastPixelOfChord-firstPixelOfChord, chordDisplaySize[1]))
			else:
				chordDisplay.fill(gray, Rect(firstPixelOfChord, 0, lastPixelOfChord-firstPixelOfChord, chordDisplaySize[1]))
			firstPixelOfText = ((chord["start"] - timeRangeOnScreen["start"])/timeIntervalOnScreen)*chordDisplaySize[0]
			chordText = chordFont.render(chord["chord"], False, (255, 255, 255))
			chordDisplay.blit(chordText, (firstPixelOfText+25,(chordDisplaySize[1]/2)-(chordFontSize/3)))
		i += 1
	chordDisplay.fill(backgroundColor, Rect(lastPixelOfChord, 0, chordDisplaySize[0]-lastPixelOfChord, chordDisplaySize[1]))

	# screen.fill(backgroundColor)
	screen.blit(chordDisplay, (0, chordDisplayPlacement))
	pygame.display.update(chordDisplayRect)
	# pygame.display.flip()

closeStream(audio,stream)
sys.exit()
