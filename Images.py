import sys, pygame
import os

feedbackImages = [pygame.image.load(os.path.join('images/feedback', '0.png')),
					pygame.image.load(os.path.join('images/feedback', '1.png')),
					pygame.image.load(os.path.join('images/feedback', '2.png')),
					pygame.image.load(os.path.join('images/feedback', '3.png')),
					pygame.image.load(os.path.join('images/feedback', '4.png')),
					pygame.image.load(os.path.join('images/feedback', '5.png')),
					pygame.image.load(os.path.join('images/feedback', '6.png'))]

starsImages = [pygame.image.load(os.path.join('images/feedback', '0stars.png')),
					pygame.image.load(os.path.join('images/feedback', '1stars.png')),
					pygame.image.load(os.path.join('images/feedback', '2stars.png')),
					pygame.image.load(os.path.join('images/feedback', '3stars.png')),
					pygame.image.load(os.path.join('images/feedback', '4stars.png')),
					pygame.image.load(os.path.join('images/feedback', '5stars.png')),
					pygame.image.load(os.path.join('images/feedback', '6stars.png'))]

chordImages = {"A":pygame.image.load(os.path.join('images/chords', 'A.gif')),
				"A#":pygame.image.load(os.path.join('images/chords', 'A#.gif')),
				"A#m":pygame.image.load(os.path.join('images/chords', 'A#m.gif')),
				"Am":pygame.image.load(os.path.join('images/chords', 'Am.gif')),
				"B":pygame.image.load(os.path.join('images/chords', 'B.gif')),
				"Bm":pygame.image.load(os.path.join('images/chords', 'Bm.gif')),
				"C":pygame.image.load(os.path.join('images/chords', 'C.gif')),
				"C#":pygame.image.load(os.path.join('images/chords', 'C#.gif')),
				"C#m":pygame.image.load(os.path.join('images/chords', 'C#m.gif')),
				"Cm":pygame.image.load(os.path.join('images/chords', 'Cm.gif')),
				"D":pygame.image.load(os.path.join('images/chords', 'D.gif')),
				"D#":pygame.image.load(os.path.join('images/chords', 'D#.gif')),
				"D#m":pygame.image.load(os.path.join('images/chords', 'D#m.gif')),
				"Dm":pygame.image.load(os.path.join('images/chords', 'Dm.gif')),
				"E":pygame.image.load(os.path.join('images/chords', 'E.gif')),
				"Em":pygame.image.load(os.path.join('images/chords', 'Em.gif')),
				"F":pygame.image.load(os.path.join('images/chords', 'F.gif')),
				"F#":pygame.image.load(os.path.join('images/chords', 'F#.gif')),
				"Fm":pygame.image.load(os.path.join('images/chords', 'Fm.gif')),
				"G":pygame.image.load(os.path.join('images/chords', 'G.gif')),
				"G#":pygame.image.load(os.path.join('images/chords', 'G#.gif')),
				"G#m":pygame.image.load(os.path.join('images/chords', 'G#m.gif')),
				"Gm":pygame.image.load(os.path.join('images/chords', 'Gm.gif'))}

# colorfulBackground = pygame.image.load(os.path.join('images/background', 'colorful.jpg'))