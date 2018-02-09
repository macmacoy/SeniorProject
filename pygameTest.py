import sys, pygame
from pygame.surface import Surface
from pygame.rect import Rect
import time
pygame.init()

chordSequence = [(0, 1, "G"), (1, 2, "Em"), (2, 3, "C"), (3, 4, "D")] # format: (begin, end, chord name)
songlength = 4

timeIntervalOnScreen = 3

def isInTimeRange(chordRange, timeRangeOnScreen):
	if chordRange[0] > timeRangeOnScreen[0] and chordRange[0] < timeRangeOnScreen[1]:
		return True
	if chordRange[1] > timeRangeOnScreen[0] and chordRange[1] < timeRangeOnScreen[1]:
		return True
	else:
		return False

black = 0, 0, 0

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
		return (0,0,0)

screenSize = (800, 600)
chordDisplaySize = (800, 200)

screen = pygame.display.set_mode(screenSize)
chordDisplay = Surface(chordDisplaySize)

start = time.time()
timeRangeOnScreen = (0,0)
nextPixel = 0
while 1:
	# user quits
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    now = time.time()-start
    # song ends
    if(now > songlength):
    	sys.exit()

    timeRangeOnScreen = (now-timeIntervalOnScreen/2, now+timeIntervalOnScreen/2)
    firstPixel = 0
    lastPixel = 0
    for chord in chordSequence:
    	if isInTimeRange(chord[0:2],timeRangeOnScreen):
    		if chord[0] > timeRangeOnScreen[0]:
    			firstPixel = ((chord[0] - timeRangeOnScreen[0])/timeIntervalOnScreen)*chordDisplaySize[0]
    		else:
    			firstPixel = 0
    		if chord[1] < timeRangeOnScreen[1]:
    			lastPixel = ((chord[1] - timeRangeOnScreen[0])/timeIntervalOnScreen)*chordDisplaySize[0]
    		else:
    			lastPixel = chordDisplaySize[0]
    		chordDisplay.fill(getColor(chord[2]), Rect(firstPixel, 0, lastPixel-firstPixel, chordDisplaySize[1]))
    if lastPixel < chordDisplaySize[0]:
    	chordDisplay.fill(black, Rect(lastPixel, 0, chordDisplaySize[0]-lastPixel, chordDisplaySize[1]))

    screen.fill(black)
    screen.blit(chordDisplay, (0, 200))
    pygame.display.flip()
