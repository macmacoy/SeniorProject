# for microphone input
import pyaudio
import wave
# for chord recognition
from madmom.audio.chroma import DeepChromaProcessor
from madmom.features.chords import DeepChromaChordRecognitionProcessor

# returns a chord or 'N'
def chordFromMicrophone():

	### -------MICROPHONE INPUT------- ###
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	CHUNK = 1024
	RECORD_SECONDS = 0.35
	WAVE_OUTPUT_FILENAME = "myWaveFile.wav"
	 
	audio = pyaudio.PyAudio()
	 
	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
	                rate=RATE, input=True,
	                frames_per_buffer=CHUNK)
	#print "recording..."
	frames = []
	 
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
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
	### -------MICROPHONE INPUT------- ###

	### -------CHORD RECOGNITION------- ###
	dcp = DeepChromaProcessor()
	decode = DeepChromaChordRecognitionProcessor()
	chroma = dcp('myWaveFile.wav')
	chord = (decode(chroma)[0][2])
	return chord
	### -------CHORD RECOGNITION------- ###