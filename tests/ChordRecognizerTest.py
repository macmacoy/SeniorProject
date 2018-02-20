#--------------------------------#
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#--------------------------------#
# Play guitar along

from ChordRecognizer import madmomChord #, pymirChord
from queue import Queue

while(True):
	q = Queue()
	print (madmomChord(q))
	# print pymirChord()