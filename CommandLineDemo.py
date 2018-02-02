from Song import Song
import time

my_song = Song("tests/test_song.json")

print ("Song: " + my_song.name)
print ("Artist: " + my_song.artist)
print ("Tempo: " + str(my_song.tempo))
print ("Capo: " + str(my_song.capo))

chords = my_song.chords
lyrics = my_song.lyrics

lyricIndex = 0
chordIndex = 0
start = time.time()
while(time.time() < start + my_song.duration):
	now = time.time() - start
	if(now >= chords[chordIndex+1]["timestamp"]):
		print ("Chord : " + chords[chordIndex]["chord"])
		chordIndex += 1
	if(now >= lyrics[lyricIndex+1]["timestamp"]):
		print ("Lyric : " + lyrics[lyricIndex]["lyric"])
		lyricIndex += 1