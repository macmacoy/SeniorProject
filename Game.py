import sys, pygame
import time
import os
import threading
import Colors
import ChordRecognizer
import Font
import SongFileBuilder
from queue import Queue, Empty
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.locals import *
from Song import Song
from Player import Player
from Images import chordImages, feedbackImages, starsImages, edgeImage, titleBackground

# for makin the app
import numpy.core._methods
import numpy.lib.format

def PlaySong(song, player): # take in song object

	flags = FULLSCREEN | DOUBLEBUF # fps is 4x better in fullscreen mode
	# flags = DOUBLEBUF
	screen = pygame.display.set_mode(screenSize, flags)

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

	chordFontSize = 75
	chordFont = Font.body(chordFontSize)
	lyricFontSize = 38
	lyricFont = Font.body(lyricFontSize)

	## intialize graphic components
	chordDisplay = Surface(chordDisplaySize)
	currentTimeMarker = Surface(currentTimeMarkerSize)
	currentTimeMarker.fill(Colors.darkGray)
	feedbackDisplay = getFeedbackImage(51, scaledForPlaySong=True) # initial
	chordTextsNotHit = []
	chordTextsHit = []
	for chord in chords:
		if chord["chord"] != "":
			chordTextsNotHit.append(chordFont.render(chord["chord"], False, Colors.mediumGray))
			chordTextsHit.append(chordFont.render(chord["chord"], False, Colors.white))
		else:
			chordTextsNotHit.append(chordFont.render("NC", False, Colors.mediumGray))
			chordTextsHit.append(chordFont.render("NC", False, Colors.white))

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

	def updateFeedbackScore(hit):
		if(hit):
			chordScore[chordIndex] = score(now-chords[chordIndex]["start"]-ChordRecognizer.RECORD_SECONDS)
		else:
			chordScore[chordIndex] = 0
		totalScore = 0
		initial = 10*[.5]
		for j in range(0,chordIndex+1):
			totalScore += chordScore[j]
		for i in initial:
			totalScore += i
		totalScore *= 100
		totalScore = totalScore / (chordIndex+1 + len(initial))
		return totalScore

	def scaleForCurrentChord(image):
		return pygame.transform.scale(image, (int(image.get_width()/1), int(image.get_height()/1)))

	def scaleForNextChord(image):
		return pygame.transform.scale(image, (int(image.get_width()/1), int(image.get_height()/1)))

	def scaleChordDisplayEdge(image):
		return pygame.transform.scale(image, (int(image.get_width()/4.2), int(image.get_height()/4.2)))

	def readKeyInput():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.K_ESCAPE:
				return

	totalScore = float(0)
	chordScore = len(chords)*[float(0)]
	hit = len(chords)*[False]

	## pygame clock was doing some preemptive rendering or something
	# clock = pygame.time.Clock()
	# start = toSeconds(pygame.time.get_ticks())
	# now = start

	start = time.time() + timeIntervalOnScreen/2
	now = time.time() - start
	pausedTime = 0

	chordIndex = 0
	lyricIndex = 0
	chordChanged = True
	lyricChanged = True

	paused = False
	timeRangeOnScreen = {"start":0.0, "end":0.0}
	while now < song.duration + timeIntervalOnScreen/2:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					# flags = FULLSCREEN | DOUBLEBUF # fps is 4x better in fullscreen mode
					flags = DOUBLEBUF
					screen = pygame.display.set_mode(screenSize, flags)
					return
				elif event.key == pygame.K_SPACE:
					if paused:
						now = time.time() - start
						start = start + (now - pausedTime)
						now = pausedTime
						paused = False
					else:
						pausedTime = now
						paused = True

		if not paused:
			if (now > chords[chordIndex]["end"]):
				if(not hit[chordIndex]):
					totalScore = updateFeedbackScore(False)
					feedbackDisplay = getFeedbackImage(totalScore, scaledForPlaySong=True)
				if chords[chordIndex] != chords[-1]:
					chordIndex += 1
				chordChanged = True
			if (now > lyrics[lyricIndex]["end"]):
				if lyrics[lyricIndex] != lyrics[-1]:
					lyricIndex += 1
				lyricChanged = True

			timeRangeOnScreen["start"] = now-timeIntervalOnScreen/2
			timeRangeOnScreen["end"] = now+timeIntervalOnScreen/2

			firstPixelOfChord = 0
			lastPixelOfChord = 0
			i = 0
			firstPixels = []
			chordTexts = []
			chordTextPlacements = []
			for chord in chords:
				if isInTimeRange(chord,timeRangeOnScreen):
					if chord["start"] > timeRangeOnScreen["start"]:
						firstPixelOfChord = ((chord["start"] - timeRangeOnScreen["start"])/timeIntervalOnScreen)*chordDisplaySize[0]
						firstPixels.append(firstPixelOfChord)
					else:
						firstPixelOfChord = 0
					if chord["end"] < timeRangeOnScreen["end"]:
						lastPixelOfChord = ((chord["end"] - timeRangeOnScreen["start"])/timeIntervalOnScreen)*chordDisplaySize[0]
					else:
						lastPixelOfChord = chordDisplaySize[0]
					try:  
						# c = q.get_nowait() # or q.get(timeout=.1)
						if q.get_nowait() == chords[chordIndex]["chord"]:
							if hit[chordIndex] == False:
								totalScore = updateFeedbackScore(True)
								feedbackDisplay = getFeedbackImage(totalScore, scaledForPlaySong=True)
							hit[chordIndex] = True
					except Empty:
					    pass
					if hit[i]:
						chordDisplay.fill(Colors.getColorForChord(chord["chord"]), Rect(firstPixelOfChord, 0, lastPixelOfChord-firstPixelOfChord, chordDisplaySize[1]))
						chordText = chordTextsHit[i]
					else:
						chordDisplay.fill(Colors.lightGray, Rect(firstPixelOfChord, 0, lastPixelOfChord-firstPixelOfChord, chordDisplaySize[1]))
						chordText = chordTextsNotHit[i]
					firstPixelOfText = ((chord["start"] - timeRangeOnScreen["start"])/timeIntervalOnScreen)*chordDisplaySize[0]
					chordTexts.append(chordText)
					chordTextPlacements.append((firstPixelOfText+50,(chordDisplaySize[1]/2)-chordText.get_rect().height/2+chordDisplayPlacement[1]))
					# chordDisplay.blit(chordText, (firstPixelOfText+25,(chordDisplaySize[1]/2)-chordText.get_rect().height/2))
				i += 1
			chordDisplay.fill(Colors.backgroundColor, Rect(lastPixelOfChord, 0, chordDisplaySize[0]-lastPixelOfChord, chordDisplaySize[1]))

			if lyricChanged:
				screen.fill(Colors.backgroundColor)
				lyricText = lyricFont.render(lyrics[lyricIndex]["lyric"], False, Colors.white)
				centeredLyricPlacement = (lyricPlacement[0]-lyricText.get_rect().width/2, lyricPlacement[1])
				screen.blit(lyricText, centeredLyricPlacement)

			# screen.blit(colorfulBackground, (0,0))
			screen.blit(chordDisplay, chordDisplayPlacement)
			screen.blit(feedbackDisplay, feedbackPlacement)

			if(chordIndex == len(chords)-1):
				scaledCurrentImageChord = scaleForCurrentChord(chordImages[chords[chordIndex]["chord"]])
			elif(now < chords[chordIndex+1]["start"] - 1):
				scaledCurrentImageChord = scaleForCurrentChord(chordImages[chords[chordIndex]["chord"]])
			else: 
				scaledCurrentImageChord = scaleForCurrentChord(chordImages[chords[chordIndex+1]["chord"]])
			scaledCurrentChordImagePlacement = (currentChordImagePlacement[0] - scaledCurrentImageChord.get_rect().width/2, currentChordImagePlacement[1])
			screen.blit(scaledCurrentImageChord, scaledCurrentChordImagePlacement)
			if(chordIndex != len(chords)-1):
				scaledNextImageChord = scaleForNextChord(chordImages[chords[chordIndex+1]["chord"]])
				scaledNextChordImagePlacement = (nextChordImagePlacement[0] - scaledNextImageChord.get_rect().width/2, nextChordImagePlacement[1])
				screen.blit(scaledNextImageChord, scaledNextChordImagePlacement)

			for firstPixel in firstPixels:
				scaledEdgeImage = scaleChordDisplayEdge(edgeImage)
				screen.blit(scaledEdgeImage, (firstPixel - scaledEdgeImage.get_rect().width/2, chordDisplayPlacement[1]-1))

			for z in range(0, len(chordTexts)):
				screen.blit(chordTexts[z], chordTextPlacements[z])

			# # ## for testing
			# pygame.draw.rect(screen, Colors.black, Rect(screenSize[0]/2, 750, 40, 40))
			# screen.blit(lyricFont.render(str(now), False, Colors.white), (screenSize[0]/2, 750))

			screen.blit(currentTimeMarker, currentTimeMarkerPlacement)
			# if lyricChanged:
			# 	lyricChanged = False
			# 	pygame.display.flip()
			# else:
			# 	pygame.display.update(chordDisplay.get_rect())
				# pygame.display.flip()
			pygame.display.flip()

			# clock.tick()
			# now = toSeconds(pygame.time.get_ticks()) - start
			now = time.time() - start

	# flags = FULLSCREEN | DOUBLEBUF # fps is 4x better in fullscreen mode
	flags = DOUBLEBUF
	screen = pygame.display.set_mode(screenSize, flags)

	print(str(totalScore))

	EndOfSongScreen(song, totalScore, player)

	# print ("fps: " + str(clock.get_fps()))
	# closeStream()

def getFeedbackImage(totalScore, scaledForPlaySong=False):
	if (totalScore > 85):
		if scaledForPlaySong:
			return pygame.transform.scale(feedbackImages[6], (int(feedbackImages[6].get_width()/3.5), int(feedbackImages[6].get_height()/3.5)))
		else:
			return feedbackImages[6]
	elif (totalScore > 75):
		if scaledForPlaySong:
			return pygame.transform.scale(feedbackImages[5], (int(feedbackImages[5].get_width()/3.5), int(feedbackImages[5].get_height()/3.5)))
		else:
			return feedbackImages[5]
	elif (totalScore > 65):
		if scaledForPlaySong:
			return pygame.transform.scale(feedbackImages[4], (int(feedbackImages[4].get_width()/3.5), int(feedbackImages[4].get_height()/3.5)))
		else:
			return feedbackImages[4]
	elif (totalScore > 50):
		if scaledForPlaySong:
			return pygame.transform.scale(feedbackImages[3], (int(feedbackImages[3].get_width()/3.5), int(feedbackImages[3].get_height()/3.5)))
		else:
			return feedbackImages[3]
	elif (totalScore > 40):
		if scaledForPlaySong:
			return pygame.transform.scale(feedbackImages[2], (int(feedbackImages[2].get_width()/3.5), int(feedbackImages[2].get_height()/3.5)))
		else:
			return feedbackImages[2]
	elif (totalScore > 30):
		if scaledForPlaySong:
			return pygame.transform.scale(feedbackImages[1], (int(feedbackImages[1].get_width()/3.5), int(feedbackImages[1].get_height()/3.5)))
		else:
			return feedbackImages[1]
	else:
		if scaledForPlaySong:
			return pygame.transform.scale(feedbackImages[0], (int(feedbackImages[0].get_width()/3.5), int(feedbackImages[0].get_height()/3.5)))
		else:
			return feedbackImages[0]

def getStarsImage(totalScore):
	if (totalScore > 85):
		return starsImages[6]
	elif (totalScore > 75):
		return starsImages[5]
	elif (totalScore > 65):
		return starsImages[4]
	elif (totalScore > 50):
		return starsImages[3]
	elif (totalScore > 40):
		return starsImages[2]
	elif (totalScore > 30):
		return starsImages[1]
	else:
		return starsImages[0]

def userHasQuit():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return True
	return False

# def toSeconds(millis):
# 	return float(millis)*0.001

def MainMenu(player):
	buttonSize = (screenSize[0]/5, screenSize[1]/7)
	playSongButtonPlacement = (screenSize[0]/2 - buttonSize[0]/2, screenSize[1]*.45)
	playerStatsButtonPlacement = (screenSize[0]/2 - buttonSize[0]/2, screenSize[1]*.65)

	buttonTextSize = 40
	buttonFont = Font.body(buttonTextSize)
	playSongButtonText = buttonFont.render("Play Song", False, Colors.darkGray)
	playerStatsButtonText = buttonFont.render("Player Stats", False, Colors.darkGray)
	playSongButtonTextPlacement = (playSongButtonPlacement[0] + buttonSize[0]/2 - playSongButtonText.get_rect().width/2, playSongButtonPlacement[1] + buttonSize[1]/2 - playSongButtonText.get_rect().height/2)
	playerStatsButtonTextPlacement = (playerStatsButtonPlacement[0] + buttonSize[0]/2 - playerStatsButtonText.get_rect().width/2, playerStatsButtonPlacement[1] + buttonSize[1]/2 - playerStatsButtonText.get_rect().height/2)

	playSongButton = Rect(playSongButtonPlacement, buttonSize)
	playerStatsButton = Rect(playerStatsButtonPlacement, buttonSize)

	def scaleBackground(image):
		scalingFactor = screenSize[0] / image.get_width()
		return pygame.transform.scale(image, (int(image.get_width()*scalingFactor), int(image.get_height()*scalingFactor)))

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return True
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = event.pos
				if playSongButton.collidepoint(mouse_pos):
					SongsMenu(player)
				elif playerStatsButton.collidepoint(mouse_pos):
					PlayerStatsScreen(player)

		screen.blit(scaleBackground(titleBackground), (0,0))

		pygame.draw.rect(screen, Colors.white, playSongButton)  # draw button
		pygame.draw.rect(screen, Colors.white, playerStatsButton)  # draw button
		screen.blit(playSongButtonText, playSongButtonTextPlacement)
		screen.blit(playerStatsButtonText, playerStatsButtonTextPlacement)
		pygame.display.flip()

def SongsMenu(player):
	inputBoxSize = (screenSize[0]/3, screenSize[1]/15)
	songInputBox = InputBox(screenSize[0]/4 - inputBoxSize[0]/2, screenSize[1]/2.4, inputBoxSize[0], inputBoxSize[1], "Song")
	artistInputBox = InputBox(screenSize[0]/4 - inputBoxSize[0]/2, screenSize[1]/2, inputBoxSize[0], inputBoxSize[1], "Artist")
	songRectSize = (screenSize[0]/2.5, screenSize[1]/14)
	firstSongRectPlacement = (screenSize[0]*.75 - songRectSize[0]/2, screenSize[1]/4)
	spaceBetweenSongs = 30 #px

	songFont = Font.body_bold(30)
	titleFont = Font.header(50)
	nextPrevButtonFont = Font.body(40)
	pageNumFont = Font.body(40)
	playButtonFont = Font.body(25)
	backButtonFont = Font.body(40)
	capoDifficultyFont = Font.body(25)

	mySongsTitleText = titleFont.render("My songs", False, Colors.lightGray)
	downloadSongsTitleText = titleFont.render("Download a song", False, Colors.lightGray)
	playButtonText = playButtonFont.render("PLAY", False, Colors.white)
	prevText = nextPrevButtonFont.render("<", False, Colors.lightGray)
	nextText = nextPrevButtonFont.render(">", False, Colors.lightGray)
	capoText = capoDifficultyFont.render("Capo ", False, Colors.white)
	difficultyText = capoDifficultyFont.render("Diff: ", False, Colors.black)
	prevButtonPlacement = (screenSize[0]*.75 - 50 - prevText.get_rect().width/2, screenSize[1] - 70)
	nextButtonPlacement = (screenSize[0]*.75 + 50 - nextText.get_rect().width/2, screenSize[1] - 70)
	prevTextPlacement = prevButtonPlacement
	nextTextPlacement = nextButtonPlacement
	mySongsTitleTextPlacement = (firstSongRectPlacement[0] + songRectSize[0]/2 - mySongsTitleText.get_rect().width/2, firstSongRectPlacement[1] - 95)
	downloadSongsTitleTextPlacement = (screenSize[0]/4 - downloadSongsTitleText.get_rect().width/2, screenSize[1]/2.4 - 75)
	nextPrevButtonSize = (screenSize[0]/15, screenSize[1]/20)
	prevButton = Rect(prevButtonPlacement, nextPrevButtonSize)
	nextButton = Rect(nextButtonPlacement, nextPrevButtonSize)
	pageNumPlacement = (screenSize[0]*.75, prevTextPlacement[1])
	playSongButtonSize = (screenSize[0]/17, screenSize[1]/17)
	backButtonPlacement = (30, 15)
	backButtonText = backButtonFont.render("<", False, Colors.lightGray)
	backButtonSize = (backButtonText.get_rect().width, backButtonText.get_rect().height)
	backButton = Rect(backButtonPlacement, backButtonSize)
	capoTextPlacement = (mySongsTitleTextPlacement[0] + 215, mySongsTitleTextPlacement[1] + 55)

	songsDirPath = "save files/songs"
	songFilePaths = [f for f in os.listdir(songsDirPath) if os.path.isfile(os.path.join(songsDirPath, f))]
	songs = []
	z = 1
	for songFilePath in songFilePaths:
		if(songFilePath != ".DS_Store"):
			song = Song('save files/songs/' + songFilePath)
			songs.append(song)
	# sort by recently played?
	pageRects = [[]]
	pageTexts = [[]]
	playSongButtons = [[]]
	capoTexts = [[]]
	diffTexts = [[]]
	pageNum = 1
	songOnPageIndex = 0
	for song in songs:
		songRectPlacement = (firstSongRectPlacement[0], firstSongRectPlacement[1] + songOnPageIndex*(songRectSize[1] + spaceBetweenSongs))
		if songRectPlacement[1]+songRectSize[1] > pageNumPlacement[1]:
			songRectPlacement = firstSongRectPlacement
			pageNum = pageNum + 1
			pageRects.append([])
			pageTexts.append([])
			playSongButtons.append([])
			capoTexts.append([])
			diffTexts.append([])
			songOnPageIndex = 1
		else:
			songOnPageIndex = songOnPageIndex + 1
		pageRects[pageNum-1].append(Rect(songRectPlacement, songRectSize))
		pageTexts[pageNum-1].append(songFont.render(song.name, False, Colors.belizehole))
		playSongButtonPlacement = (songRectPlacement[0] + songRectSize[0] - playSongButtonSize[0] - 10, songRectPlacement[1]+5)
		playSongButtons[pageNum-1].append(Rect(playSongButtonPlacement, playSongButtonSize))
		capoTexts[pageNum-1].append(capoDifficultyFont.render(str(song.capo), False, Colors.belizehole))
	pageNum = 1

	song = ''
	artist = ''
	while True:
		songInput = songInputBox.getSubmittedInput()
		artistInput = artistInputBox.getSubmittedInput()
		if(songInput != '' or artistInput != ''):
			song = songInput
			artist = artistInput
			# create new song
			SongFileBuilder.downloadSong(songInput, artistInput)
			## replicated code (bad I know)
			songsDirPath = "save files/songs"
			songFilePaths = [f for f in os.listdir(songsDirPath) if os.path.isfile(os.path.join(songsDirPath, f))]
			songs = []
			z = 1
			for songFilePath in songFilePaths:
				if(songFilePath != ".DS_Store"):
					song = Song('save files/songs/' + songFilePath)
					songs.append(song)
			# sort by recently played?
			pageRects = [[]]
			pageTexts = [[]]
			playSongButtons = [[]]
			capoTexts = [[]]
			diffTexts = [[]]
			pageNum = 1
			songOnPageIndex = 0
			for song in songs:
				songRectPlacement = (firstSongRectPlacement[0], firstSongRectPlacement[1] + songOnPageIndex*(songRectSize[1] + spaceBetweenSongs))
				if songRectPlacement[1]+songRectSize[1] > pageNumPlacement[1]:
					songRectPlacement = firstSongRectPlacement
					pageNum = pageNum + 1
					pageRects.append([])
					pageTexts.append([])
					playSongButtons.append([])
					capoTexts.append([])
					diffTexts.append([])
					songOnPageIndex = 1
				else:
					songOnPageIndex = songOnPageIndex + 1
				pageRects[pageNum-1].append(Rect(songRectPlacement, songRectSize))
				pageTexts[pageNum-1].append(songFont.render(song.name, False, Colors.belizehole))
				playSongButtonPlacement = (songRectPlacement[0] + songRectSize[0] - playSongButtonSize[0] - 10, songRectPlacement[1]+5)
				playSongButtons[pageNum-1].append(Rect(playSongButtonPlacement, playSongButtonSize))
				capoTexts[pageNum-1].append(capoDifficultyFont.render(str(song.capo), False, Colors.belizehole))
				diffTexts[pageNum-1].append(capoDifficultyFont.render(str(song.getSongDifficulty()), False, Colors.belizehole))
			pageNum = 1
			## replicated code (bad I know)

		for event in pygame.event.get():
			songInputBox.handle_event(event)
			artistInputBox.handle_event(event)
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = event.pos
				if nextButton.collidepoint(mouse_pos) and pageNum < len(pageRects):
					pageNum = pageNum + 1
				elif prevButton.collidepoint(mouse_pos) and pageNum > 1:
					pageNum = pageNum - 1
				elif backButton.collidepoint(mouse_pos):
					return
				else:
					for i in range(0,len(playSongButtons[pageNum-1])):
						if playSongButtons[pageNum-1][i].collidepoint(mouse_pos):
							songIndex = (pageNum-1)*len(playSongButtons[0])+i
							PlaySong(songs[songIndex], player)
							break;
			elif event.type == pygame.QUIT:
				sys.exit()
		songInputBox.update()
		artistInputBox.update()
		screen.fill(Colors.backgroundColor)
		songInputBox.draw(screen)
		artistInputBox.draw(screen)
		screen.blit(downloadSongsTitleText, downloadSongsTitleTextPlacement)

		screen.blit(mySongsTitleText, mySongsTitleTextPlacement)
		screen.blit(capoText, capoTextPlacement)
		for i in range(0,len(pageRects[pageNum-1])):
			pygame.draw.rect(screen, Colors.white, pageRects[pageNum-1][i])
			# textPlacement = (pageRects[pageNum-1][i].x+pageRects[pageNum-1][i].width/2-pageTexts[pageNum-1][i].get_rect().width/2,pageRects[pageNum-1][i].y+pageRects[pageNum-1][i].height/3)
			textPlacement = (pageRects[pageNum-1][i].x+15, pageRects[pageNum-1][i].y+pageRects[pageNum-1][i].height/2 - pageTexts[pageNum-1][i].get_rect().height/2)
			screen.blit(pageTexts[pageNum-1][i], textPlacement)
			pygame.draw.rect(screen, Colors.alizarin, playSongButtons[pageNum-1][i])
			playSongButtonTextPlacement2 = (playSongButtons[pageNum-1][i].x + playSongButtons[pageNum-1][i].width/2 - playButtonText.get_rect().width/2, playSongButtons[pageNum-1][i].y + playSongButtons[pageNum-1][i].height/2 - playButtonText.get_rect().height/2)
			screen.blit(playButtonText, playSongButtonTextPlacement2)
			capoNumberPlacement = (textPlacement[0] + songRectSize[0] - 160, textPlacement[1] + 5)
			screen.blit(capoTexts[pageNum-1][i], capoNumberPlacement)

		if pageNum < len(pageRects):
			screen.blit(nextText, nextTextPlacement)
		if pageNum > 1:
			screen.blit(prevText, prevTextPlacement)

		pageNumText = pageNumFont.render(str(pageNum), False, Colors.lightGray)
		screen.blit(pageNumText, (pageNumPlacement[0] - pageNumText.get_rect().width/2, pageNumPlacement[1]))
		screen.blit(backButtonText, backButtonPlacement)

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
        self.font = Font.body_bold(38)
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
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+1))

    def getSubmittedInput(self):
    	if self.submitted:
    		self.submitted = False
    		submittedText = self.text
    		self.text = ''
    		return submittedText
    	return ''

def EndOfSongScreen(song, totalScore, player):
	feedbackImage = getFeedbackImage(totalScore)
	starsImage = getStarsImage(totalScore)
	scaledStarsImage = pygame.transform.scale(starsImage, (int(starsImage.get_width()/3), int(starsImage.get_height()/3)))
	timeToWait = 1.5
	timeToExpand = 4
	timeToStayInMiddle = 2
	timeToMoveLeft = 2.5
	timeToWait2 = 0.5
	timeToWait3 = 1
	pointsIncreasePerSec = 5

	starsPlacement = (screenSize[0]/2 - scaledStarsImage.get_width()/2, screenSize[1]/1.4 - scaledStarsImage.get_height()/2)

	feedbackFont = pygame.font.SysFont('Calibri', 60)
	if totalScore > 50:
		feedbackText = feedbackFont.render("Nice!", False, Colors.white)
	else:
		feedbackText = feedbackFont.render("Keep working!", False, Colors.white)

	feedbackTextPlacement = (screenSize[0]/2 - feedbackText.get_rect().width/2, screenSize[1]/1.2)

	pointsRectSize = (screenSize[0]/5, screenSize[1]/1.5)
	pointsRectPlacement = (screenSize[0]*3/4 - pointsRectSize[0]/2, screenSize[1]/2 - pointsRectSize[1]/2)
	pointsRect = Rect(pointsRectPlacement, pointsRectSize)

	levelFont = pygame.font.SysFont('Calibri', 60)
	pointsFont = pygame.font.SysFont('Calibri', 40)
	prevLevel = player.level
	prevPoints = player.points
	player.playedSong(totalScore, song)
	level = player.level
	points = player.points

	prevPointsText = pointsFont.render(str(int(prevPoints)) + " points", False, Colors.white)
	pointsText = pointsFont.render(str(int(points)) + " points", False, Colors.white)
	prevPointsTextPlacment = (pointsRectPlacement[0] + pointsRectSize[0] + 5, pointsRectPlacement[1] + pointsRectSize[1] - pointsRectSize[1]*((prevPoints - player.pointsNeededForLevel[prevLevel])/player.pointsNeededForLevel[prevLevel+1]) - prevPointsText.get_rect().height/2)
	pointsTextPlacement = (pointsRectPlacement[0] + pointsRectSize[0] + 5, pointsRectPlacement[1] + pointsRectSize[1] - pointsRectSize[1]*((points - player.pointsNeededForLevel[level])/player.pointsNeededForLevel[level+1]) - pointsText.get_rect().height/2)
	levelText = levelFont.render(str(prevLevel), False, Colors.white)
	levelTextPlacement = (pointsRectPlacement[0] + pointsRectSize[0]/2 - levelText.get_rect().width/2, pointsRectPlacement[1] + pointsRectSize[1] + 10)
	playerPointsRectSize = (pointsRectSize[0], pointsRectSize[1]*((prevPoints - player.pointsNeededForLevel[prevLevel])/player.pointsNeededForLevel[prevLevel+1]))
	playerPointsRectPlacement = (pointsRectPlacement[0], pointsRectPlacement[1] + pointsRectSize[1] - pointsRectSize[1]*((prevPoints - player.pointsNeededForLevel[prevLevel])/player.pointsNeededForLevel[prevLevel+1])+2)
	playerPointsRect = Rect(playerPointsRectPlacement, playerPointsRectSize)
	coverPrevPointsTextRect = Rect(prevPointsTextPlacment[0], prevPointsTextPlacment[1], prevPointsText.get_rect().width, prevPointsText.get_rect().height)
	coverLevelTextRect = Rect(levelTextPlacement[0], levelTextPlacement[1], levelText.get_rect().width, levelText.get_rect().height)
	pointsTitleText = levelFont.render("Level", False, Colors.white)
	pointsTitleTextPlacment = (levelTextPlacement[0] - pointsTitleText.get_rect().width/2 + 10, levelTextPlacement[1] + 40)

	toPlaySongMenuButtonFont = pygame.font.SysFont('Calibri', 40)
	toPlaySongMenuButtonText = toPlaySongMenuButtonFont.render(">", False, Colors.white)
	toPlaySongMenuButtonSize = (toPlaySongMenuButtonText.get_rect().width, toPlaySongMenuButtonText.get_rect().height)
	toPlaySongMenuButtonPlacement = (screenSize[0]*9/10, screenSize[1]*9/10)
	toPlaySongMenuButton = Rect(toPlaySongMenuButtonPlacement, toPlaySongMenuButtonSize)

	start = time.time()
	now = time.time() - start
	while now < timeToWait:
		pygame.display.flip()
		now = time.time() - start
		if userHasQuit():
			sys.exit()

	start = time.time()
	now = time.time() - start
	while now < timeToExpand:
		scaledFeedbackImage = pygame.transform.scale(feedbackImage, (int(feedbackImage.get_width()/(1.8*timeToExpand/(now+.01))), int(feedbackImage.get_height()/(1.8*timeToExpand/(now+.01)))))
		feedbackPlacement = (screenSize[0]/2 - scaledFeedbackImage.get_width()/2, screenSize[1]/2.8 - scaledFeedbackImage.get_height()/2)
		screen.blit(scaledFeedbackImage, feedbackPlacement)
		pygame.display.flip()
		now = time.time() - start
		if userHasQuit():
			sys.exit()

	start = time.time()
	now = time.time() - start
	while now < timeToStayInMiddle:
		screen.blit(scaledFeedbackImage, feedbackPlacement)
		screen.blit(scaledStarsImage, starsPlacement)
		screen.blit(feedbackText, feedbackTextPlacement)
		pygame.display.flip()
		now = time.time() - start
		if userHasQuit():
			sys.exit()

	start = time.time()
	now = time.time() - start
	while now < timeToMoveLeft:
		scaledFeedbackImage = pygame.transform.scale(feedbackImage, (int(feedbackImage.get_width()/(1.8 + 1*(now/timeToMoveLeft))), int(feedbackImage.get_height()/(1.8 + 1*(now/timeToMoveLeft)))))
		scaledStarsImage = pygame.transform.scale(starsImage, (int(starsImage.get_width()/(3 + 1*(now/timeToMoveLeft))), int(starsImage.get_height()/(3 + 1*(now/timeToMoveLeft)))))
		feedbackPlacement = (screenSize[0]/(2+2*(now/timeToMoveLeft)) - scaledFeedbackImage.get_width()/2, screenSize[1]/(2.8 - 0.5*now/timeToMoveLeft) - scaledFeedbackImage.get_height()/2)
		starsPlacement = (screenSize[0]/(2+2*(now/timeToMoveLeft)) - scaledStarsImage.get_width()/2, screenSize[1]/(1.4 + 0.2*now/timeToMoveLeft) - scaledStarsImage.get_height()/2)
		screen.fill(Colors.backgroundColor)
		screen.blit(scaledFeedbackImage, feedbackPlacement)
		screen.blit(scaledStarsImage, starsPlacement)
		pygame.display.flip()
		now = time.time() - start
		if userHasQuit():
			sys.exit()

	start = time.time()
	now = time.time() - start
	while now < timeToWait2:
		pygame.display.flip()
		now = time.time() - start
		if userHasQuit():
			sys.exit()

	start = time.time()
	now = time.time() - start
	while now < timeToWait3:
		pygame.draw.rect(screen, Colors.lightGray, pointsRect)
		pygame.draw.rect(screen, Colors.getColorForLevel(prevLevel), playerPointsRect)
		screen.blit(levelText, levelTextPlacement)
		screen.blit(prevPointsText, prevPointsTextPlacment)
		pygame.display.flip()
		now = time.time() - start
		if userHasQuit():
			sys.exit()

	start = time.time()
	now = time.time() - start
	last = now
	tempPoints = prevPoints
	tempLevel = prevLevel
	increasing = True
	frate = .01
	while increasing:
		if now - last > frate:
			last = now
			tempPoints = tempPoints + frate*pointsIncreasePerSec
			if tempPoints > player.pointsNeededForLevel[tempLevel+1]:
				tempLevel = tempLevel + 1
				levelText = levelFont.render(str(tempLevel), False, Colors.white)
		playerPointsRectSize = (pointsRectSize[0], pointsRectSize[1]*((tempPoints - player.pointsNeededForLevel[tempLevel])/player.pointsNeededForLevel[tempLevel+1]))
		playerPointsRectPlacement = (pointsRectPlacement[0], pointsRectPlacement[1] + pointsRectSize[1] - pointsRectSize[1]*((tempPoints - player.pointsNeededForLevel[tempLevel])/player.pointsNeededForLevel[tempLevel+1])+2)
		playerPointsRect = Rect(playerPointsRectPlacement, playerPointsRectSize)
		pygame.draw.rect(screen, Colors.backgroundColor, coverPrevPointsTextRect)
		pygame.draw.rect(screen, Colors.lightGray, pointsRect)
		pygame.draw.rect(screen, Colors.getColorForLevel(tempLevel), playerPointsRect)
		pygame.draw.rect(screen, Colors.backgroundColor, coverLevelTextRect)
		screen.blit(levelText, levelTextPlacement)
		pygame.display.flip()
		now = time.time() - start
		if tempPoints >= points:
			increasing = False
		if userHasQuit():
			sys.exit()

	while True:
		playerPointsRectSize = (pointsRectSize[0], pointsRectSize[1]*((tempPoints - player.pointsNeededForLevel[tempLevel])/player.pointsNeededForLevel[tempLevel+1]))
		playerPointsRectPlacement = (pointsRectPlacement[0], pointsRectPlacement[1] + pointsRectSize[1] - pointsRectSize[1]*((tempPoints - player.pointsNeededForLevel[tempLevel])/player.pointsNeededForLevel[tempLevel+1])+2)
		playerPointsRect = Rect(playerPointsRectPlacement, playerPointsRectSize)
		pygame.draw.rect(screen, Colors.lightGray, pointsRect)
		pygame.draw.rect(screen, Colors.getColorForLevel(level), playerPointsRect)
		pygame.draw.rect(screen, Colors.backgroundColor, coverPrevPointsTextRect)
		screen.blit(levelText, levelTextPlacement)
		screen.blit(pointsText, pointsTextPlacement)
		screen.blit(toPlaySongMenuButtonText, toPlaySongMenuButtonPlacement)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = event.pos
				if toPlaySongMenuButton.collidepoint(mouse_pos):
					return
			if event.type == pygame.QUIT:
				sys.exit()

def PlayerStatsScreen(player):
	pygame.display.flip()
	pointsRectSize = (screenSize[0]/5, screenSize[1]/1.5)
	pointsRectPlacement = (screenSize[0]*3/4 - pointsRectSize[0]/2, screenSize[1]/2 - pointsRectSize[1]/2)
	pointsRect = Rect(pointsRectPlacement, pointsRectSize)

	playerPointsRectSize = (pointsRectSize[0], pointsRectSize[1]*((player.points - player.pointsNeededForLevel[player.level])/player.pointsNeededForLevel[player.level+1]))
	playerPointsRectPlacement = (pointsRectPlacement[0], pointsRectPlacement[1] + pointsRectSize[1] - pointsRectSize[1]*((player.points - player.pointsNeededForLevel[player.level])/player.pointsNeededForLevel[player.level+1])+2)
	playerPointsRect = Rect(playerPointsRectPlacement, playerPointsRectSize)

	levelFont = Font.header(40)
	pointsFont = Font.body(35)
	levelText = levelFont.render(str(player.level), False, Colors.white)
	pointsText = pointsFont.render(str(int(player.points)) + " points", False, Colors.white)
	levelTextPlacement = (pointsRectPlacement[0] + pointsRectSize[0]/2 - levelText.get_rect().width/2, pointsRectPlacement[1] + pointsRectSize[1] + 10)
	pointsTextPlacement = (pointsRectPlacement[0] + pointsRectSize[0] + 5, pointsRectPlacement[1] + pointsRectSize[1] - pointsRectSize[1]*((player.points - player.pointsNeededForLevel[player.level])/player.pointsNeededForLevel[player.level+1]) - pointsText.get_rect().height/2)
	pointsTitleText = levelFont.render("Level", False, Colors.white)
	pointsTitleTextPlacment = (levelTextPlacement[0] - pointsTitleText.get_rect().width/2 + 10, levelTextPlacement[1] + 40)

	backButtonFont = Font.body(40)
	backButtonPlacement = (30, 15)
	backButtonText = backButtonFont.render("<", False, Colors.lightGray)
	backButtonSize = (backButtonText.get_rect().width, backButtonText.get_rect().height)
	backButton = Rect(backButtonPlacement, backButtonSize)

	topSongsTitleFont = Font.header(55)
	topSongsFont = Font.body(40)
	topSongsTitle = topSongsTitleFont.render("Top Songs", False, Colors.lightGray)
	topSongsTitlePlacement = (screenSize[0]/3 - topSongsTitle.get_rect().width/2, screenSize[1]/6)
	topSongsTitlesPlacement = (screenSize[0]/15, screenSize[1]/4)
	topSongsDifficultyPlacement = (screenSize[0]/3, screenSize[1]/4)
	topSongsScorePlacment = (screenSize[0]/2.2, screenSize[1]/4)
	topSongsTexts = []
	topSongsDifficultyTexts = []
	topSongsScoreTexts = []
	for i in range(0, len(player.songsPlayed["songs"])):
		topSongsTexts.append(topSongsFont.render(player.songsPlayed["songs"][i], False, Colors.white))
		topSongsDifficultyTexts.append(topSongsFont.render(str(player.songsPlayed["difficulties"][i]), False, Colors.white))
		topSongsScoreTexts.append(topSongsFont.render((str(player.songsPlayed["scores"][i]) + "%"), False, Colors.white))

	titleText = topSongsFont.render("Song", False, Colors.orange)
	difficultyText = topSongsFont.render("Difficulty", False, Colors.orange)
	scoreText = topSongsFont.render("Score", False, Colors.orange)
	titleTextPlacement = topSongsTitlesPlacement
	difficultyTextPlacment = (topSongsDifficultyPlacement[0] - difficultyText.get_rect().width/2 + 10, topSongsDifficultyPlacement[1])
	scoreTextPlacement = (topSongsScorePlacment[0] - scoreText.get_rect().width/2 + 55, topSongsScorePlacment[1])
	topSongsTitlesPlacement = (topSongsTitlesPlacement[0], topSongsTitlesPlacement[1] + 50)
	topSongsDifficultyPlacement = (topSongsDifficultyPlacement[0], topSongsDifficultyPlacement[1] + 50)
	topSongsScorePlacment = (topSongsScorePlacment[0], topSongsScorePlacment[1] + 50)

	screen.fill(Colors.backgroundColor)
	pygame.draw.rect(screen, Colors.lightGray, pointsRect)
	pygame.draw.rect(screen, Colors.getColorForLevel(player.level), playerPointsRect)
	screen.blit(topSongsTitle, topSongsTitlePlacement)
	screen.blit(titleText, titleTextPlacement)
	screen.blit(difficultyText, difficultyTextPlacment)
	screen.blit(scoreText, scoreTextPlacement)
	screen.blit(pointsTitleText, pointsTitleTextPlacment)
	for i in range(0, len(topSongsTexts)):
		screen.blit(topSongsTexts[i], topSongsTitlesPlacement)
		screen.blit(topSongsDifficultyTexts[i], topSongsDifficultyPlacement)
		screen.blit(topSongsScoreTexts[i], topSongsScorePlacment)
		topSongsTitlesPlacement = (topSongsTitlesPlacement[0], topSongsTitlesPlacement[1] + 50)
		topSongsDifficultyPlacement = (topSongsDifficultyPlacement[0], topSongsDifficultyPlacement[1] + 50)
		topSongsScorePlacment = (topSongsScorePlacment[0], topSongsScorePlacment[1] + 50)
		if (topSongsTitlesPlacement[1] > screenSize[1] - 200):
			break

	screen.blit(levelText, levelTextPlacement)
	screen.blit(pointsText, pointsTextPlacement)
	screen.blit(backButtonText, backButtonPlacement)

	while True:
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = event.pos
				if backButton.collidepoint(mouse_pos):
					return
			if event.type == pygame.QUIT:
				sys.exit()

player = Player()

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
# song = Song('save files/songs/' + "song_22_20180413230824.json")
# EndOfSongScreen(song, 80, player)
MainMenu(player)
# PlayerStatsScreen(player)

# songFilePath = 'song_letitbe_20180413153538.json'
# PlaySong(Song('save files/songs/' + songFilePath), player)
# SongsMenu()

# SongFileBuilder.downloadSong("Take It Easy", "The Eagles")
