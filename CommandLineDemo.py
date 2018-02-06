from Song import Song
from ChordRecognizer import madmomChord
import time
import os

my_song = Song("tests/test_song.json")

os.system('clear')
print ("Song: " + my_song.name)
print ("Artist: " + my_song.artist)
print ("Tempo: " + str(my_song.tempo))
print ("Capo: " + str(my_song.capo))
print ("")
print ("Starting in ...")
for i in range(0,3):
	print ("   " + str(3-i) + "   ")
	time.sleep(1)

chords = my_song.chords
lyrics = my_song.lyrics

tab = " " * 50
def draw(hit):
	os.system('clear')
	print (lyrics[lyricIndex]["lyric"] + tab[len(lyrics[lyricIndex]["lyric"]):] + chords[chordIndex]["chord"] + " <----")
	if hit:
		print(tab[4:] + "-NICE!-")
	else:
		print(tab[1:] + "-X-")
	print("")
	if lyrics[lyricIndex]["end"] != my_song.duration and chords[chordIndex]["end"] != my_song.duration:
		# print("   next:   " + tab[9:] + "next:")
		print(lyrics[lyricIndex+1]["lyric"] + tab[len(lyrics[lyricIndex+1]["lyric"]):] + chords[chordIndex+1]["chord"])
	elif lyrics[lyricIndex]["end"] != my_song.duration:
		# print(tab[2:] + "next:")
		print(tab + lyrics[lyricIndex+1]["lyric"])
	elif chords[chordIndex]["end"] != my_song.duration:
		# print("   next:   ")
		print(tab + chords[chordIndex+1]["chord"])

lyricIndex = 0
chordIndex = 0
hit = False
start = time.time()
while(time.time() < start + my_song.duration):
	draw(hit)
	now = time.time() - start
	while(now < chords[chordIndex]["end"]):
		if (now > lyrics[lyricIndex]["end"]):
			lyricIndex += 1
			draw(hit)
		if hit == False:
			if madmomChord() == chords[chordIndex]["chord"]:
				hit = True
				redraw(hit)
		now = time.time() - start
	chordIndex += 1
	hit = False