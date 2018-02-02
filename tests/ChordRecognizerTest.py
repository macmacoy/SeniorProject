#--------------------------------#
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#--------------------------------#
# Play guitar along

from ChordRecognizer import madmomChord, pymirChord

while(True):
	print madmomChord()
	# print pymirChord()