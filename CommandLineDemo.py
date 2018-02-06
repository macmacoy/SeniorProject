from Song import Song
import time
import os

my_song = Song("tests/test_song.json")

print ("Song: " + my_song.name)
print ("Artist: " + my_song.artist)
print ("Tempo: " + str(my_song.tempo))
print ("Capo: " + str(my_song.capo))

print ("Starting in ...")
for i in range(3,0):
	print ("   " + i + "   ")
	time.sleep(1)

chords = my_song.chords
lyrics = my_song.lyrics

lyricIndex = 0
chordIndex = 0
start = time.time()
print (lyrics[0]["lyric"])
print (" ------ " + chords[0]["chord"] + " ------ ")
while(time.time() < start + my_song.duration):
	now = time.time() - start
	if(now > chords[chordIndex]["end"]):
		chordIndex += 1
		os.system('clear')
		print (lyrics[lyricIndex]["lyric"])
		print (" ------ " + chords[chordIndex]["chord"] + " ------ "  + " <------- now")
	if(now > lyrics[lyricIndex]["end"]):
		lyricIndex += 1
		os.system('clear')
		print (lyrics[lyricIndex]["lyric"])
		print (" ------ " + chords[chordIndex]["chord"] + " ------ "  + " <------- now")