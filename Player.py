import json

#####------------#####
# levels: 1-6		 #
# points needed for each level:
#	level 1: 0
# 	level 2: 5
# 	level 3: 15
# 	level 4: 30
#	level 5: 50
#	level 6: 75

class Player(object):

	def __init__(self):
		with open("save files/Player.json") as json_data:
		    data = json.load(json_data)

		    self.name = data.get("name")
		    self.points = data.get("points")
		    self.level = data.get("level")
		    self.songsPlayed = data.get("songsPlayed")
		    self.pointsNeededForLevel = [0, 0, 5, 15, 30, 50, 75]

	def save(self):
		with open('save files/Player.json', 'w') as outfile:
			data = {}
			data["name"] = self.name
			data["points"] = self.points
			data["level"] = self.level
			# sort songs based on score
			for i in range(0, len(self.songsPlayed["songs"])):
				for j in range(0, i):
					if self.songsPlayed["scores"][i] > self.songsPlayed["scores"][j]:
						songName = self.songsPlayed["songs"][i]
						songArtist = self.songsPlayed["artists"][i]
						songScore = self.songsPlayed["scores"][i]
						songDifficulty = self.songsPlayed["difficulties"][i]
						del self.songsPlayed["songs"][i]
						del self.songsPlayed["artists"][i]
						del self.songsPlayed["scores"][i]
						del self.songsPlayed["difficulties"][i]
						self.songsPlayed["songs"].insert(j, songName)
						self.songsPlayed["artists"].insert(j, songArtist)
						self.songsPlayed["scores"].insert(j, songScore)
						self.songsPlayed["difficulties"].insert(j, songDifficulty)
						break
			data["songsPlayed"] = self.songsPlayed
			json.dump(data, outfile, indent=4)

	def playedSong(self, score, song):
		# score: 0-100
		# songDifficulty: 1-6
		if(not self.havePlayedSong(song)):
			self.points = self.points + (score/100)*song.getSongDifficulty()
			if(self.points > self.pointsNeededForLevel[self.level+1] and self.level < 6):
				self.level = self.level + 1
			self.songsPlayed["songs"].append(song.name)
			self.songsPlayed["artists"].append(song.artist)
			self.songsPlayed["scores"].append(score)
			self.songsPlayed["difficulties"].append(song.getSongDifficulty())
		else:
			index = self.songsPlayed["songs"].index(song.name)
			if((score/100)*song.getSongDifficulty() - (self.songsPlayed["scores"][index]/100)*self.songsPlayed["difficulties"][index]):
				self.points = self.points + (score/100)*song.getSongDifficulty() - (self.songsPlayed["scores"][index]/100)*song.getSongDifficulty()
				self.songsPlayed["scores"][index] = score
				if(self.points > self.pointsNeededForLevel[self.level+1] and self.level < 6):
					self.level = self.level + 1
				if(self.songsPlayed["difficulties"][index] != song.getSongDifficulty()):
					self.songsPlayed["difficulties"][index] = song.getSongDifficulty()
			# self.reorderPlayedSongs(song)
		self.save()

	def havePlayedSong(self, song):
		if song.name in self.songsPlayed["songs"]:
			index = self.songsPlayed["songs"].index(song.name)
			if song.artist == self.songsPlayed["artists"][index]:
				return True
		return False

	def reorderPlayedSongs(self, song):
		index = self.songsPlayed["songs"].index(song.name)
		score = self.songsPlayed["scores"][index]
		self.songsPlayed["songs"].remove(song.name)
		self.songsPlayed["artists"].remove(song.artist)
		del self.songsPlayed["scores"][index]
		del self.songsPlayed["difficulties"][index]
		self.songsPlayed["songs"].append(song.name)
		self.songsPlayed["artists"].append(song.artist)
		self.songsPlayed["artists"].append(score)
		self.songsPlayed["artists"].append(song.getSongDifficulty())
