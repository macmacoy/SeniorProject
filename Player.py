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

	def save(self):
		with open('save files/Player.json', 'w') as outfile:
			data = {}
			data["name"] = self.name
			data["points"] = self.points
			data["level"] = self.level
			json.dump(data, outfile)

	def songPlayed(score, songDifficulty):
		# score: 0-100
		# songDifficulty: 1-6
		self.pointsNeededForLevel = [0, 0, 5, 15, 30, 50, 75]
		if(score > 60): ## song passed
			self.points = self.points + songDifficulty
		if(self.points > self.pointsNeededForLevel[self.level+1] and self.level < 6):
			self.level = self.level + 1