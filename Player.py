import json

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