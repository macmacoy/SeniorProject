from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import json
import datetime
import LyricsSearch

class Song:
  def __init__(self):
    self.title = ""
    self.artist = ""
    self.youtube_url = ""
    self.duration = 0
    self.tempo = 0
    self.lyric_offset = 0.00
    self.capo = 0
    self.chords = []
    self.lyrics = []

  def toJSON(self):
    filename = "save files/songs/song_" + ''.join(self.title.split()).lower() + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
    data = {}
    data["title"] = self.title
    data["artist"] = self.artist
    data["youtube_url"] = self.youtube_url
    data["duration"] = self.duration
    data["tempo"] = self.tempo
    data["capo"] = self.capo
    data["chords"] = self.chords
    data["lyrics"] = self.lyrics
    # with open(filename, 'w', encoding='utf8') as json_file:
    #   json.dump(data, json_file, indent=4)
    with open(filename, 'w') as outfile:
      json.dump(data, outfile, indent=4)

def getLyrics(songTitle, songArtist):
  lyrics = LyricsSearch.MiniLyrics(songArtist, songTitle)
  highest = {"rating": 0, "rating_count": 0}
  for result in lyrics[:5]:
    # print(result)
    if ((result["rating"]) > (highest["rating"])) and (result["filetype"] == "lrc"):
      highest = result
  url = highest["url"]
  print(url)
  response = urlopen(url)
  data = response.read()            # a `bytes` object
  raw_lyrics = data.decode('utf-8') # a `str`; this step can't be used if data is binary
  return raw_lyrics

def getYoutubeUrl(songTitle, songArtist):
  textToSearch = songTitle + ' ' + songArtist
  query = quote(textToSearch)
  url = "https://www.youtube.com/results?search_query=" + query
  response = urlopen(url)
  html = response.read()
  soup = BeautifulSoup(html,'html.parser')
  vids = soup.findAll(attrs={'class':'yt-uix-tile-link'})
  return vids[0]['href'].split("=")[1].split("&")[0]

def getRawSongData(youtubeUrl):
  songDataUrl = 'https://play.riffstation.com/api/mir/songs?source=youtube&source_id=' + youtubeUrl
  rawSongData = json.load(urlopen(songDataUrl))
  return rawSongData["song"]

def parseSongData(songTitle, songArtist, youtubeUrl, lyrics, rawSongData):
  song = Song()
  song.title = songTitle
  song.artist = songArtist
  song.youtube_url = youtubeUrl
  song.duration = round(rawSongData["duration"], 2)
  song.tempo = round(rawSongData["tempo"])
  song.lyric_offset = 0
  if (rawSongData["capo"] == None):
    song.capo = 0
  else:
    song.capo = rawSongData["capo"]
  for event in rawSongData["song_events"]:
    recognizableChords = ["A#m","C#m","D#m","F#m","G#m","Am","Bm","Cm","Dm","Em","Fm","Gm","A#","C#","D#","F#","G#","A","B","C","D","E","F","G"]
    eventChord = ""
    for chord in recognizableChords:
      if event["name"].startswith(chord):
        eventChord = chord
        break
    song.chords.append({"timestamp": round(event["beat_time"], 2), "chord": eventChord})
  for line in lyrics.splitlines():
    if line and line.strip():
      if (line[0] != '[') or (not line[1].isdigit()):
        continue
      else:
        # NOT MATCHES: \[.+\]
        # MATCHES: \[([^\]]+)\]
        # don't forget to strip brackets
        minutes = line[1:3]
        seconds = line[4:6]
        milliseconds = line[7:9]
        timestamp = (int(minutes) * 60) + int(seconds) + (int(milliseconds) / 100.0)
        song.lyrics.append({"timestamp": timestamp, "lyric": line[10:]})
  return song

def downloadSong(songTitle, songArtist):

  lyrics = getLyrics(songTitle, songArtist)
  youtubeUrl = getYoutubeUrl(songTitle, songArtist)
  rawSongData = getRawSongData(youtubeUrl)
  parsedSongData = parseSongData(songTitle, songArtist, youtubeUrl, lyrics, rawSongData)
  
  parsedSongData.toJSON()

if __name__ == "__main__":
  main()
  