import json

class Song(object):

	def __init__(self, filename):

		with open(filename) as json_data:
		    data = json.load(json_data)

		    self.name = data.get("title")
		    self.artist = data.get("artist")
		    self.duration = data.get("duration")
		    self.tempo = data.get("tempo")
		    self.capo = data.get("capo")
		    if(self.capo == None):
		    	self.capo = 0

		    chord_data = data.get("chords")
		    self.chords = []
		    for i in range(0, len(chord_data)):
		    	if i < len(chord_data) - 1:
		    		self.chords.append({"start":chord_data[i]["timestamp"], "end":chord_data[i+1]["timestamp"], "chord":chord_data[i]["chord"]})
		    	else:
		    		self.chords.append({"start":chord_data[i]["timestamp"], "end":self.duration, "chord":chord_data[i]["chord"]})
		    
		    lyric_data = data.get("lyrics")
		    self.lyrics = []
		    for i in range(0, len(lyric_data)):
		    	if i < len(lyric_data) - 1:
		    		self.lyrics.append({"start":lyric_data[i]["timestamp"], "end":lyric_data[i+1]["timestamp"], "lyric":lyric_data[i]["lyric"]})
		    	else:
		    		self.lyrics.append({"start":lyric_data[i]["timestamp"], "end":self.duration, "lyric":lyric_data[i]["lyric"]})

		self.majorChords = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
		self.minorChords = ["Am","A#m","Bm","Cm","C#m","Dm","D#m","Em","Fm","F#m","Gm","G#m"]

	def incrementCapo(self):
		if self.capo < 12:
			for chord in self.chords:
				if chord["chord"] in self.majorChords:
					if self.majorChords.index(chord["chord"]) < len(self.majorChords)-1:
						chord["chord"] = self.majorChords[self.majorChords.index(chord["chord"])+1]
					else:
						chord["chord"] = self.majorChords[0]
				elif chord["chord"] in self.minorChords:
					if self.minorChords.index(chord["chord"]) < len(self.minorChords)-1:
						chord["chord"] = self.minorChords[self.minorChords.index(chord["chord"])+1]
					else:
						chord["chord"] = self.minorChords[0]
			self.capo = self.capo + 1

	def decrementCapo(self):
		if self.capo > 0:
			for chord in self.chords:
				if chord["chord"] in self.majorChords:
					if self.majorChords.index(chord["chord"]) > 0:
						chord["chord"] = self.majorChords[self.majorChords.index(chord["chord"])-1]
					else:
						chord["chord"] = self.majorChords[len(self.majorChords)-1]
				elif chord["chord"] in self.minorChords:
					if self.minorChords.index(chord["chord"]) > 0:
						chord["chord"] = self.minorChords[self.minorChords.index(chord["chord"])-1]
					else:
						chord["chord"] = self.minorChords[len(self.minorChords)-1]
			self.capo = self.capo - 1

	def speedUpTempoTo(self,bps):
		self.duration = self.duration * (self.tempo / bps)
		self.tempo = bps

	def getSongDifficulty(self): ## value is difficulty as an int between 1 and 6
		return 4