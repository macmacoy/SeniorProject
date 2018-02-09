# for microphone input
import pyaudio
import wave

# for madmom chord recognition
from madmom.audio.chroma import DeepChromaProcessor
from madmom.features.chords import DeepChromaChordRecognitionProcessor

# for pymire chord recognition
from pymir import AudioFile
from pymir import Pitch
from pymir import Onsets

# constants
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 0.35
WAVE_OUTPUT_FILENAME = "myWaveFile.wav"

# records audio from microphone
def record(length):
	audio = pyaudio.PyAudio()
	 
	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
	                rate=RATE, input=True,
	                frames_per_buffer=CHUNK)
	#print "recording..."
	frames = []
	 
	for i in range(0, int(RATE / CHUNK * length)):
	    data = stream.read(CHUNK)
	    frames.append(data)
	#print "finished recording"
	 
	# stop Recording
	stream.stop_stream()
	stream.close()
	audio.terminate()
	 
	waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()

# returns a chord or 'N'
def madmomChord():

	record(RECORD_SECONDS)

	dcp = DeepChromaProcessor()
	decode = DeepChromaChordRecognitionProcessor()
	chroma = dcp('myWaveFile.wav')
	chord = (decode(chroma)[0][2])
	if ":maj" in chord:
		return chord.replace(':maj','')
	elif ":min" in chord:
		return chord.replace(':min','m')
	if chord == "N":
		return chord
	print ("ChordRecognizer.py: NOT ALL CASES ACCOUNTED FOR")
	return chord

# returns a chord
# more instable, but ability to give confidence
def pymirChord():

	record(RECORD_SECONDS)
	
	audiofile = AudioFile.open(WAVE_OUTPUT_FILENAME)

	o = Onsets.onsetsByFlux(audiofile)
	frames = audiofile.framesFromOnsets(o)

	#frameSize = 16384
	#frames = audioFile.frames(frameSize)

	chords = []
	frameIndex = 0
	startIndex = 0
	for frame in frames:
		spectrum = frame.spectrum()
		chroma = spectrum.chroma()
		# print chroma
		
		chord, score = Pitch.getChord(chroma)

		endIndex = startIndex + len(frame)

		startTime = startIndex / frame.sampleRate
		endTime = endIndex / frame.sampleRate

		# print "%.2f  | %.2f | %-4s | (%.2f)" % (startTime, endTime, chord, score)
	    
		chords.append([startTime, endTime, chord, score])

		frameIndex = frameIndex + 1
		startIndex = startIndex + len(frame)

	chord = {"chord": 'N', "confidence": 0}
	for interval in chords:
		if(interval[3] > chord["confidence"]):
			chord["chord"] = interval[2]
			chord["confidence"] = interval[3]
	return chord["chord"]
