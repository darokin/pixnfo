import sys
import os
from PIL import Image

# System call
os.system("")

block = '█'
halfBottomBlock = '▄'
halfTopBlock = '▀'

ASCII_TOPLEFT = '┌'
ASCII_TOPRIGHT = '┐'
ASCII_BOTTOMLEFT = '└'
ASCII_BOTTOMRIGHT = '┘'
ASCII_VLINE = '│'
ASCII_HLINE = '─'

ansiEsc = '\x1B['
ansiflagReset = ansiEsc + '0m'
# foreground ESC[38;2;{r};{g};{b}m
# background ESC[48;2;{r};{g};{b}m

# Cursor movements
ANSI_MOVEUP = "A" # moves cursor up # lines
ANSI_MOVEDOWN = "B" # moves cursor down # lines
ANSI_MOVERIGHT = "C" # moves cursor right # columns
ANSI_MOVELEFT = "D" # moves cursor left # columns
ANSI_MOVELINENEXT = "E" # moves cursor to beginning of next line, # lines down
ANSI_MOVELINEPREV = "F" # moves cursor to beginning of previous line, # lines down
def cursorMove(direction, nbCharMove):
	sys.stdout.write(ansiEsc + nbCharMove + direction)

# Save and restore cursor position
def cursorSave():
	sys.stdout.write(ansiEsc + 's')
def cursorRestore():
	sys.stdout.write(ansiEsc + 'u')

# Draw a rectangle at X , Y with WITH AND HEIGHT
def rect(_px, _py, _w, _h):
	strRect = ASCII_TOPLEFT + (ASCII_HLINE * _w) + ASCII_TOPRIGHT
	for i in range(_h):
		strRect += '\n' + ASCII_VLINE + (' ' * _w) + ASCII_VLINE
	strRect += '\n' + ASCII_BOTTOMLEFT + (ASCII_HLINE * _w) + ASCII_BOTTOMRIGHT + '\n'
	sys.stdout.write(strRect)

def ansiRGB(rgbTuple):
	r, g, b, a = rgbTuple
	return f'\x1B[38;2;{r};{g};{b}m'

def ansiRGBDble(rgbTupleTop, rgbTupleBottom):
	fr, fg, fb, fa = rgbTupleTop
	br, bg, bb, ba = rgbTupleBottom
	return f'\x1B[48;2;{br};{bg};{bb}m\x1B[38;2;{fr};{fg};{fb}m' 

def nfo(path, img):

	width, height = img.size
	if not(width and height):
		return

	# Load image pixels
	imgPixelMap = img.load()
	
	# Init 2D array for double lines
	arrDbleLines = []
	dicDbleLines = {}
	#arrDbleLines = [[(0,0,0,0) for c in range(img.size[0])] for r in range(img.size[1])]
	for y in range(height // 2 + 1):
		row = []
		for x in range(width):
			row.append(((0,0,0,0), (0,0,0,0)))
			dicDbleLines[x, y] = ((0,0,0,0), (0,0,0,0))
		arrDbleLines.append(row)

	# Parcours pixels et affecte a arrDbleLines + compte les couleurs des pixels (add dans dicColors)
	dicColors = {}
	for y in range(height):
		line = ''
		for x in range(width):
			pixel = imgPixelMap[x, y]
			# For odd lines we take the line and the next one to arrDbleLines
			if y % 2 == 1:
				if y < img.size[1] - 1:
					pixelnl = imgPixelMap[x, y + 1]
				else:
					pixelnl = (0, 0, 0, 0)
				dicDbleLines[x, int((y // 2))] = (pixel, pixelnl)

			if pixel in dicColors:
				dicColors[pixel] += 1
			else:
				dicColors[pixel] = 1
	# Sort list of colors by nb of occurences
	sortedDic = sorted(dicColors.items(), key=lambda x: x[1], reverse=True)

	# Draw dble lines
	# for y in range(height // 2):
	# 	line = ''
	# 	for x in range(width):
	# 		pixel, nextPixel = dicDbleLines[x, y]
	# 		line += ansiRGBDble(pixel, nextPixel) + halfTopBlock + ansiflagReset
	# 	print(line)

	# Analyze palette
	nbPix = width * height
	maxPalWidth = 50 # nb columns for palette
	sColBlocks = ''
	totCol = 0
	for key in sortedDic:
		val = key[1] # nb pixels for this color
		key = key[0] # (r,g,b,a) key tuple
		nbCol = int(val / nbPix * maxPalWidth) - 1
		if nbCol <= 0 and totCol +  1 < maxPalWidth:
			nbCol = 1
		totCol += nbCol
		# print(key, val, nbCol)
		sColBlocks += ansiRGB(key) + (block * nbCol) + ansiflagReset

	# Display image information
	imgInfoHeight = 2
	# Draw main rect
	rect(1, 1, 68, imgInfoHeight)

	cursorMove(ANSI_MOVELINEPREV, str(imgInfoHeight + 2))
	cursorMove(ANSI_MOVEDOWN, '1')
	#cursorMove(ANSI_MOVERIGHT, '2')

	# ct = 0
	# for key in sortedDic:
	# 	ct += 1
	# 	if ct > 4:
	# 		break
	# 	val = key[1] # nb pixels for this color
	# 	key = key[0] # (r,g,b,a) key tuple
	# 	sys.stdout.write(ansiRGB(key) + (block) + ansiflagReset)
	# 	if (ct % 2 == 0):
	# 		cursorMove(ANSI_MOVEDOWN, '1')
	# 		cursorMove(ANSI_MOVELEFT, '2')


	cursorMove(ANSI_MOVERIGHT, '8')
	# # First Line Content
	sys.stdout.write(f"\x1b[1;31m{width}x{height}" + ansiflagReset)
	cursorMove(ANSI_MOVELINENEXT, '1')
	cursorMove(ANSI_MOVEUP, '1')
	cursorMove(ANSI_MOVERIGHT, '16')
	sys.stdout.write(f"\x1b[1m{path}" + ansiflagReset)
	
	# Second Line content
	cursorMove(ANSI_MOVELINENEXT, '1')
	cursorMove(ANSI_MOVERIGHT, '8')
	sys.stdout.write(f"\x1b[1;43m{img.format}" + ansiflagReset)
	
	cursorMove(ANSI_MOVELINENEXT, '1')
	cursorMove(ANSI_MOVEUP, '1')
	cursorMove(ANSI_MOVERIGHT, '16')
	sys.stdout.write(sColBlocks)
	
	cursorMove(ANSI_MOVELINENEXT, '2') #str(imgInfoHeight + 1))
	# print(path, img.format, f"{img.size} - {img.mode}")
	# Show global image info
	
	#print("dimensions ", width, height)

	# Show palette line
	#print(sColBlocks)

for infile in sys.argv[1:]:
	try:
		with Image.open(infile) as im:
			nfo(infile, im)
	except OSError:
		pass

