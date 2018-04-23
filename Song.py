import json

class Song(object):

	def __init__(self, filename):

		# with open(filename, encoding='utf8') as json_data:
		# 		data = json.load(json_data)
		with open(filename) as json_data:
			data = json.load(json_data)

			self.name = data.get("title")
			self.artist = data.get("artist")
			self.duration = data.get("duration")
			self.tempo = data.get("tempo")
			self.capo = data.get("capo")
			if "lyric_offset" in data.keys():
				lyric_offset = data.get("lyric_offset")
			else:
				lyric_offset = 0
			if "chord_offset" in data.keys():
				chord_offset = data.get("chord_offset")
			else:
				chord_offset = 0
			if(self.capo == None):
				self.capo = 0

			chord_data = data.get("chords")
			self.chords = []
			for i in range(0, len(chord_data)):
				if i < len(chord_data) - 1:
					if (chord_data[i]["timestamp"]+chord_offset >= 0):
						self.chords.append({"start":chord_data[i]["timestamp"]+chord_offset, "end":chord_data[i+1]["timestamp"]+chord_offset, "chord":chord_data[i]["chord"]})
				else:
					if (chord_data[i]["timestamp"]+chord_offset >= 0):
						self.chords.append({"start":chord_data[i]["timestamp"]+chord_offset, "end":self.duration+chord_offset, "chord":chord_data[i]["chord"]})
			
			lyric_data = data.get("lyrics")
			self.lyrics = []
			for i in range(0, len(lyric_data)):
				if i < len(lyric_data) - 1:
					if (lyric_data[i]["timestamp"]+lyric_offset >= 0):
						self.lyrics.append({"start":lyric_data[i]["timestamp"]+lyric_offset, "end":lyric_data[i+1]["timestamp"]+lyric_offset, "lyric":lyric_data[i]["lyric"]})
				else:
					if (lyric_data[i]["timestamp"]+lyric_offset >= 0):
						self.lyrics.append({"start":lyric_data[i]["timestamp"]+lyric_offset, "end":self.duration+lyric_offset, "lyric":lyric_data[i]["lyric"]})

		self.majorChords = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
		self.minorChords = ["Am","A#m","Bm","Cm","C#m","Dm","D#m","Em","Fm","F#m","Gm","G#m"]

		if (self.capo > 0):
			for i in range(0, self.capo):
				self.incrementCapo()
				self.capo = self.capo - 1


	def decrementCapo(self):
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
		self.capo = self.capo - 1

	def incrementCapo(self):
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
		self.capo = self.capo + 1

	def speedUpTempoTo(self,bps):
		self.duration = self.duration * (self.tempo / bps)
		self.tempo = bps

	def getSongDifficulty(self): ## value is difficulty as an int between 1 and 6
		chordDifficulties = {"A":2,"A#":3,"B":3,"C":1,"C#":3,"D":1,"D#":3,"E":1,"F":2,"F#":2,"G":1,"G#":3,"Am":1,"A#m":2,"Bm":3,"Cm":3,"C#m":2,"Dm":1,"D#m":2,"Em":1,"Fm":3,"F#m":2,"Gm":2,"G#m":2}
		
		chordDifficultyTotal=0
		keys = list(chordDifficulties.keys())
		for chord in self.chords:
			if chord in keys:
				chordDifficultyTotal = chordDifficultyTotal + chordDifficulties[chord["chord"]]
			else:
				chordDifficultyTotal = chordDifficultyTotal + 1
		chordDifficultyScore = (chordDifficultyTotal/len(self.chords)) * 2

		chordDurationTotal = 0
		durations = []
		for chord in self.chords:
			chordDurationTotal = chordDurationTotal + (chord["end"] - chord["start"])
			durations.append(chord["end"] - chord["start"])
		avgChordDuration = (chordDurationTotal/len(self.chords))
		if avgChordDuration <= 1:
			avgChordDurationScore = 6
		elif avgChordDuration <= 2:
			avgChordDurationScore = 5
		elif avgChordDuration <= 3:
			avgChordDurationScore = 4
		elif avgChordDuration <= 4:
			avgChordDurationScore = 3
		elif avgChordDuration <= 5:
			avgChordDurationScore = 2
		else:
			avgChordDurationScore = 1

		durations.sort()
		topTenPercent = int(len(durations) * 0.1)
		durationTotal = 0
		for duration in durations[:topTenPercent]: 
			durationTotal = durationTotal + duration
		topTenAvg = durationTotal/topTenPercent
		if topTenAvg <= 1:
			fastestChordDurationScore = 6
		elif topTenAvg <= 2:
			fastestChordDurationScore = 4
		else:
			fastestChordDurationScore = 2

		difficultyScore = (0.6 * chordDifficultyScore) + (0.25 * avgChordDurationScore) + (0.15 * fastestChordDurationScore)

		return int(round(difficultyScore))