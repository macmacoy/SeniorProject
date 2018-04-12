import os
import pygame

def header(size):
	return pygame.font.Font(os.path.join("fonts/Patua_One", 'PatuaOne-Regular.ttf'), size)

def body(size):
	return pygame.font.Font(os.path.join("fonts/Open_Sans", 'OpenSans-Regular.ttf'), size)

def body_bold(size):
	return pygame.font.Font(os.path.join("fonts/Open_Sans", 'OpenSans-Bold.ttf'), size)