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

def PlaySong(song): # take in song object
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

def userHasQuit():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return True
	return False

def toSeconds(millis):
	return float(millis)*0.001

def MainMenu():
	buttonSize = (screenSize[0]/5, screenSize[1]/7)
	playSongButtonPlacement = (screenSize[0]/2 - buttonSize[0]/2, screenSize[1]/3)
	playerStatsButtonPlacement = (screenSize[0]/2 - buttonSize[0]/2, screenSize[1]/2)

	buttonTextSize = 40
	buttonFont = pygame.font.SysFont('Comic Sans MS', buttonTextSize)
	playSongButtonText = buttonFont.render("Play Song", False, Colors.darkGray)
	playerStatsButtonText = buttonFont.render("Player Stats", False, Colors.darkGray)
	playSongButtonTextPlacement = (playSongButtonPlacement[0] + buttonSize[0]/2 - playSongButtonText.get_rect().width/2, playSongButtonPlacement[1] + buttonSize[1]/3)
	playerStatsButtonTextPlacement = (playerStatsButtonPlacement[0] + buttonSize[0]/2 - playerStatsButtonText.get_rect().width/2, playerStatsButtonPlacement[1] + buttonSize[1]/3)

	playSongButton = Rect(playSongButtonPlacement, buttonSize)
	playerStatsButton = Rect(playerStatsButtonPlacement, buttonSize)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return True
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = event.pos
				if playSongButton.collidepoint(mouse_pos):
					print("play song was pressed")
				elif playerStatsButton.collidepoint(mouse_pos):
					print("player stats button was pressed")

		screen.fill(Colors.backgroundColor)

		pygame.draw.rect(screen, Colors.white, playSongButton)  # draw button
		pygame.draw.rect(screen, Colors.white, playerStatsButton)  # draw button
		screen.blit(playSongButtonText, playSongButtonTextPlacement)
		screen.blit(playerStatsButtonText, playerStatsButtonTextPlacement)
		pygame.display.flip()

def SongsMenu():
	inputBoxSize = (screenSize[0]/3, screenSize[1]/15)
	songInputBox = InputBox(screenSize[0]/2 - inputBoxSize[0]/2, screenSize[1]/8, inputBoxSize[0], inputBoxSize[1], "Song")
	artistInputBox = InputBox(screenSize[0]/2 - inputBoxSize[0]/2, screenSize[1]/5, inputBoxSize[0], inputBoxSize[1], "Artist")
	songRectSize = (screenSize[0]/2, screenSize[1]/10)
	firstSongRectPlacement = (screenSize[0]/2 - songRectSize[0]/2, screenSize[1]/3)
	spaceBetweenSongs = 30 #px
	songFont = pygame.font.SysFont('Comic Sans MS', 40)

	nextPrevButtonFont = pygame.font.SysFont('Comic Sans MS', 40)
	prevText = nextPrevButtonFont.render("<<--", False, Colors.lightGray)
	nextText = nextPrevButtonFont.render("-->>", False, Colors.lightGray)
	prevButtonPlacement = (screenSize[0]/2 - 50, screenSize[1] - 100)
	nextButtonPlacement = (screenSize[0]/2 + 50, screenSize[1] - 100)
	prevTextPlacement = (screenSize[0]/2 - 50 - prevText.get_rect().width/2, screenSize[1] - 40)
	nextTextPlacement = (screenSize[0]/2 + 50 - nextText.get_rect().width/2, screenSize[1] - 40)
	nextPrevButtonSize = (screenSize[0]/15, screenSize[1]/20)
	prevButton = Rect(prevButtonPlacement, nextPrevButtonSize)
	nextButton = Rect(nextButtonPlacement, nextPrevButtonSize)
	pageNumPlacement = (screenSize[0]/2, prevTextPlacement[1])

	songsDirPath = "save files/songs"
	songFilePaths = [f for f in os.listdir(songsDirPath) if os.path.isfile(os.path.join(songsDirPath, f))]
	songs = []
	for songFilePath in songFilePaths:
		song = Song('save files/songs/' + songFilePath)
		songs.append(song)
	pageRects = [[]]
	pageTexts = [[]]
	pageNum = 1
	songOnPageIndex = 0
	for song in songs:
		songRectPlacement = (firstSongRectPlacement[0], firstSongRectPlacement[1] + songOnPageIndex*(songRectSize[1] + spaceBetweenSongs))
		if songRectPlacement[1]+songRectSize[1] > prevTextPlacement[1] - songRectSize[1]:
			songRectPlacement = firstSongRectPlacement
			pageNum = pageNum + 1
			pageRects.append([])
			pageTexts.append([])
			songOnPageIndex = 0
		else:
			songOnPageIndex = songOnPageIndex + 1
		pageRects[pageNum-1].append(Rect(songRectPlacement, songRectSize))
		pageTexts[pageNum-1].append(songFont.render(song.name, False, Colors.darkGray))
	pageNum = 1

	song = ''
	artist = ''
	while True:
		songInput = songInputBox.getSubmittedInput()
		artistInput = artistInputBox.getSubmittedInput()
		if(songInput != '' or artistInput != ''):
			song = songInput
			artist = artistInput
			print(song)
			print(artist)

		for event in pygame.event.get():
			songInputBox.handle_event(event)
			artistInputBox.handle_event(event)
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = event.pos
				if nextButton.collidepoint(mouse_pos) and pageNum < len(pageRects):
					pageNum = pageNum + 1
				elif prevButton.collidepoint(mouse_pos) and pageNum > 1:
					pageNum = pageNum - 1
		songInputBox.update()
		artistInputBox.update()
		screen.fill(Colors.backgroundColor)
		songInputBox.draw(screen)
		artistInputBox.draw(screen)

		for i in range(0,len(pageRects[pageNum-1])):
			pygame.draw.rect(screen, Colors.white, pageRects[pageNum-1][i])
			textPlacement = (pageRects[pageNum-1][i].x+pageRects[pageNum-1][i].width/2-pageTexts[pageNum-1][i].get_rect().width/2,pageRects[pageNum-1][i].y+pageRects[pageNum-1][i].height/3)
			screen.blit(pageTexts[pageNum-1][i], textPlacement)

		if pageNum < len(pageRects):
			pygame.draw.rect(screen, Colors.black, nextButton)
			screen.blit(nextText, nextButtonPlacement)
		if pageNum > 1:
			pygame.draw.rect(screen, Colors.black, prevButton)
			screen.blit(prevText, prevButtonPlacement)

		screen.blit(prevText, prevButtonPlacement)
		screen.blit(nextPrevButtonFont.render(str(pageNum), False, Colors.lightGray), pageNumPlacement)

		pygame.display.flip()


class InputBox:

    def __init__(self, x, y, w, h, empty_text='', text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.border_rect = pygame.Rect(x-5, y-5, w+10, h+10)
        self.initialX = x
        self.box_color = Colors.lightGray
        self.border_color = Colors.darkGray
        self.text_color = Colors.darkGray
        self.empty_text_color = Colors.lightMediumGray
        self.empty_text = empty_text
        self.text = text
        self.font = pygame.font.SysFont('Comic Sans MS', 60)
        self.txt_surface = self.font.render(text, True, self.text_color)
        self.active = False
        self.submitted = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
            # Change the current color of the input box.
            # self.box_color = Colors.lightGray if self.active else Colors.mediumGray
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submitted = True
            if self.active:
	            # if event.key == pygame.K_RETURN:
	            #     self.submitted = True
	            if event.key == pygame.K_BACKSPACE:
	                self.text = self.text[:-1]
	            else:
	                self.text += event.unicode
	            # Re-render the text.
	            self.txt_surface = self.font.render(self.text, True, self.text_color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(screenSize[0]/3, self.txt_surface.get_width()+10)
        self.rect.w = width
        if width > screenSize[0]/3:
        	self.rect.x = self.initialX - (self.txt_surface.get_width()+10 - screenSize[0]/3)/2
        	self.border_rect.x = self.initialX - (self.txt_surface.get_width()+10 - screenSize[0]/3)/2
        if self.text == '':
        	self.txt_surface = self.font.render(self.empty_text, True, self.empty_text_color)
        else:
        	self.txt_surface = self.font.render(self.text, True, self.text_color)

    def draw(self, screen):
        # Blit the rect.
        if self.active:
        	pygame.draw.rect(screen, self.border_color, self.border_rect)
        pygame.draw.rect(screen, self.box_color, self.rect)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

    def getSubmittedInput(self):
    	if self.submitted:
    		self.submitted = False
    		submittedText = self.text
    		self.text = ''
    		return submittedText
    	return ''

## initialize graphics engine
pygame.init()
pygame.font.init()

screenSize = (1400, 800)

# set up full display
# flags = FULLSCREEN | DOUBLEBUF # fps is 4x better in fullscreen mode
flags = DOUBLEBUF
screen = pygame.display.set_mode(screenSize, flags)
screen.set_alpha(None)

# songFilePath = 'test_song.json'
# PlaySong(Song('save files/songs/' + songFilePath))
# MainMenu()
SongsMenu()



