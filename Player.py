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

	def save(self):
		with open('save files/Player.json', 'w') as outfile:
			data = {}
			data["name"] = self.name
			data["points"] = self.points
			data["level"] = self.level
			data["songsPlayed"] = self.songsPlayed
			json.dump(data, outfile, indent=4)

	def playedSong(self, score, song):
		# score: 0-100
		# songDifficulty: 1-6
		self.pointsNeededForLevel = [0, 0, 5, 15, 30, 50, 75]
		if(not self.havePlayedSong(song)):
			self.points = self.points + (score/100)*song.getSongDifficulty()
			if(self.points > self.pointsNeededForLevel[self.level+1] and self.level < 6):
				self.level = self.level + 1
			self.songsPlayed["songs"].append(song.name)
			self.songsPlayed["artists"].append(song.artist)
		else:
			self.reorderPlayedSongs(song)
		self.save()

	def havePlayedSong(self, song):
		if song.name in self.songsPlayed["songs"]:
			index = self.songsPlayed["songs"].index(song.name)
			if song.artist == self.songsPlayed["artists"][index]:
				return True
		return False

	def reorderPlayedSongs(self, song):
		self.songsPlayed["songs"].remove(song.name)
		self.songsPlayed["artists"].remove(song.artist)
		self.songsPlayed["songs"].append(song.name)
		self.songsPlayed["artists"].append(song.artist)
