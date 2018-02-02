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
		    self.chords = data.get("song").get("chords")
		    self.lyrics = data.get("song").get("lyrics")

	def changeCapoTo(self,number):
		self.capo = number
		# for chord in self.chords:
		# 	change 

	def speedUpTempoTo(self,bps):
		self.duration = self.duration * (self.tempo / bps)
		self.tempo = bps