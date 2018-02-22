#--------------------------------#
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#--------------------------------#
# Play guitar along

from ChordRecognizer import madmomChord #, pymirChord
from multiprocessing import Process, Pipe

while(True):
	me, you = Pipe()
	madmomChord(you)
	print(me.recv())
	# print pymirChord()