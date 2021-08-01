import sys
import os
from math import ceil
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
# https://talyian.github.io/ansicolors/ for quick inputs
ANSI_INFO_COLOR = "\x1b[38;5;212m" # Black on pink
ANSI_INFO_COLOR2 = "\x1b[38;5;39m" # Dark on ice blue


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
	#for i in range(_h):
	#	strRect += '\n' + ASCII_VLINE + (' ' * _w) + ASCII_VLINE
	strRect += ('\n' + ASCII_VLINE + (' ' * _w) + ASCII_VLINE) * _h # Pythonic way lol, not used to this.. 
	strRect += '\n' + ASCII_BOTTOMLEFT + (ASCII_HLINE * _w) + ASCII_BOTTOMRIGHT + '\n'
	sys.stdout.write(strRect)

def ansiRGB(rgbTuple):
	r, g, b, a = rgbTuple
	return f'\x1B[38;2;{r};{g};{b}m'

def ansiRGBDble(rgbTupleTop, rgbTupleBottom):
	fr, fg, fb, fa = rgbTupleTop
	br, bg, bb, ba = rgbTupleBottom
	return f'\x1B[48;2;{br};{bg};{bb}m\x1B[38;2;{fr};{fg};{fb}m' 

def getColorAtIndex(colorDict, dictIndex):
	if dictIndex < len(colorDict):
		return colorDict[dictIndex][0]
	else:
		return (0, 0, 0, 255)

def nfo(path, img):

	# TODO handle errors
	width, height = img.size
	if not(width and height):
		return

	# Convert to RGBA if needed (we handle RGBA tuple for pixel color scanning)
	originalImgMode = img.mode
	originalImgFormat = img.format
	if img.mode != "RGBA":
		img = img.convert("RGBA")

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
	# Sort list of colors by nb of occurence
	sortedDic = sorted(dicColors.items(), key=lambda x: x[1], reverse=True)

	# Analyze palette
	nbPix = width * height
	maxPalWidth = 50 # nb columns for palette
	sColBlocks = ''
	totCol = 0
	for key in sortedDic:
		val = key[1] # nb pixels for this color
		key = key[0] # (r,g,b,a) key tuple
		nbCol = ceil(val / nbPix * maxPalWidth)
		# Cumul et test si on dépasse
		if totCol >= maxPalWidth:
			break
		elif totCol + nbCol >= maxPalWidth: 
			nbCol = maxPalWidth - totCol
			if nbCol > 3: # dirty tricks to maximize palette info...
				nbCol -= 1
		totCol += nbCol
		sColBlocks += ansiRGB(key) + (block * nbCol) + ansiflagReset

	# Get number of colors
	nbColors = len(dicColors)
	
	# Create 2 strings to have a square mini palette
	palMini1 = ""
	palMini2 = ""
	if (nbColors >= 8):
		# show a 16 color palette
		for i in range(0, 8, 2):
			palMini1 += ansiRGBDble(getColorAtIndex(sortedDic, i), getColorAtIndex(sortedDic, i + 1)) + (halfTopBlock) + ansiflagReset
			palMini2 += ansiRGBDble(getColorAtIndex(sortedDic, i + 8), getColorAtIndex(sortedDic, i + 8 + 1)) + (halfTopBlock) + ansiflagReset
	else:
		# show a 4 color palette
		palMini1 += ansiRGB(getColorAtIndex(sortedDic, 0)) + (block) + (block) + ansiflagReset
		palMini1 += ansiRGB(getColorAtIndex(sortedDic, 1)) + (block) + (block) + ansiflagReset
		palMini2 += ansiRGB(getColorAtIndex(sortedDic, 2)) + (block) + (block) + ansiflagReset
		palMini2 += ansiRGB(getColorAtIndex(sortedDic, 3)) + (block) + (block) + ansiflagReset
	
	# Create lines with details on block colors
	listBlockCountLines = []
	if nbColors > 32:
		maxBlockShowed = 32
	else:
		maxBlockShowed = nbColors
	tmpLine = ''
	for i in range(maxBlockShowed): # // 8):
		tmpLine += ansiRGB(sortedDic[i][0]) + block + block + ansiflagReset + ' ' + f"{sortedDic[i][1]}".ljust(8 - 2, ' ')
		if i > 0 and (i + 1) % 8 == 0:
			listBlockCountLines.append(tmpLine)		
			tmpLine = ''
	if tmpLine != '':
		listBlockCountLines.append(tmpLine)

	# ===============================================
	# Display image information
	imgInfoHeight = 2 + len(listBlockCountLines)
	imgInfoWidth = 74
	imgInfoIndent2 = 25
	# Draw main rect
	rect(1, 1, imgInfoWidth, imgInfoHeight)

	# TODO ? Est-ce qu'on a vraiment besoin de tout ces cursorMove() ??? WTF tout ça pour code un rect() en ASCII...

	# Draw mini squared palette
	cursorMove(ANSI_MOVELINEPREV, str(imgInfoHeight + 2))
	cursorMove(ANSI_MOVEDOWN, '1')
	cursorMove(ANSI_MOVERIGHT, '2')
	sys.stdout.write(palMini1)
	cursorMove(ANSI_MOVELINENEXT, '1')
	cursorMove(ANSI_MOVERIGHT, '2')
	sys.stdout.write(palMini2)
	
	# First Line Content
	cursorMove(ANSI_MOVELINEPREV, '1')
	cursorMove(ANSI_MOVERIGHT, '8')
	sys.stdout.write(f"\x1b[1;31m{width}x{height}" + ansiflagReset + f" {(width * height)}")
	cursorMove(ANSI_MOVELINENEXT, '1')
	cursorMove(ANSI_MOVEUP, '1')
	cursorMove(ANSI_MOVERIGHT, str(imgInfoIndent2))
	sys.stdout.write(ANSI_INFO_COLOR + originalImgFormat + ansiflagReset)
	sys.stdout.write(f"  \x1b[1m{path}" + ansiflagReset)
	
	# Second Line content
	cursorMove(ANSI_MOVELINENEXT, '1')
	cursorMove(ANSI_MOVERIGHT, '8')
	sys.stdout.write(f"{nbColors} colors")
	sys.stdout.write("  " + ANSI_INFO_COLOR2 + originalImgMode + ansiflagReset)

	# cursorMove(ANSI_MOVELINENEXT, '1')
	# cursorMove(ANSI_MOVEUP, '1')
	# cursorMove(ANSI_MOVERIGHT, '22')
	
	# TODO Find palette color line and check size max
	# sometimes it don't have a space before the border 
	# (remove 1 from the biggest color (first) in the palette)

	cursorMove(ANSI_MOVELINENEXT, '1')
	cursorMove(ANSI_MOVEUP, '1')
	cursorMove(ANSI_MOVERIGHT, str(imgInfoIndent2))

	sys.stdout.write(sColBlocks)
	
	# Block count lines
	for i in range(len(listBlockCountLines)):
		cursorMove(ANSI_MOVELINENEXT, '1')
		cursorMove(ANSI_MOVERIGHT, '1')
		sys.stdout.write(listBlockCountLines[i])

	# Move for next rect
	cursorMove(ANSI_MOVELINENEXT, '2') # str(imgInfoHeight))

for infile in sys.argv[1:]:
	try:
		with Image.open(infile) as im:
			nfo(infile, im)
	except OSError:
		pass

