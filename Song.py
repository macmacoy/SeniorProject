import json

class Song(object):

	def __init__(self, filename):

		with open(filename) as json_data:
		    data = json.load(json_data)

		    self.name = data.get("song").get("title")
		    self.artist = data.get("song").get("artist")
		    self.duration = data.get("song").get("duration")
		    self.tempo = data.get("song").get("tempo")
		    self.capo = data.get("song").get("capo")

		    chord_data = data.get("song").get("chords")
		    self.chords = []
		    for i in range(0, len(chord_data)):
		    	if i < len(chord_data) - 1:
		    		self.chords.append({"start":chord_data[i]["timestamp"], "end":chord_data[i+1]["timestamp"], "chord":chord_data[i]["chord"]})
		    	else:
		    		self.chords.append({"start":chord_data[i]["timestamp"], "end":self.duration, "chord":chord_data[i]["chord"]})
		    
		    lyric_data = data.get("song").get("lyrics")
		    self.lyrics = []
		    for i in range(0, len(lyric_data)):
		    	if i < len(lyric_data) - 1:
		    		self.lyrics.append({"start":lyric_data[i]["timestamp"], "end":lyric_data[i+1]["timestamp"], "lyric":lyric_data[i]["lyric"]})
		    	else:
		    		self.lyrics.append({"start":lyric_data[i]["timestamp"], "end":self.duration, "lyric":lyric_data[i]["lyric"]})

	def changeCapoTo(self,number):
		self.capo = number
		# for chord in self.chords:
		# 	change 

	def speedUpTempoTo(self,bps):
		self.duration = self.duration * (self.tempo / bps)
		self.tempo = bps