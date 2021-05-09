import sys
import os
from PIL import Image

# System call
os.system("")

block = '█'
halfBottomBlock = '▄'
halfTopBlock = '▀'

ansiEsc = '\x1B['
ansiflagReset = ansiEsc + '0m'
# foreground ESC[38;2;{r};{g};{b}m
# background ESC[48;2;{r};{g};{b}m

def ansiRGB(rgbTuple):
	r, g, b, a = rgbTuple
	return f'\x1B[38;2;{r};{g};{b}m'

def ansiRGBDble(rgbTupleTop, rgbTupleBottom):
	fr, fg, fb, fa = rgbTupleTop
	br, bg, bb, ba = rgbTupleBottom
	return f'\x1B[48;2;{br};{bg};{bb}m\x1B[38;2;{fr};{fg};{fb}m' 

def nfo(path, img):
	# Show global image info
	print(path, img.format, f"{img.size} - {img.mode}")
	
	width, height = img.size
	if not(width and height):
		return

	print("dimensions ", width, height)

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
	for y in range(height // 2):
		line = ''
		for x in range(width):
			pixel, nextPixel = dicDbleLines[x, y]
			line += ansiRGBDble(pixel, nextPixel) + halfTopBlock + ansiflagReset
		print(line)

	# Draw palette
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
		print(key, val, nbCol)
		sColBlocks += ansiRGB(key) + (block * nbCol) + ansiflagReset

	print(sColBlocks)

for infile in sys.argv[1:]:
	try:
		with Image.open(infile) as im:
			nfo(infile, im)
	except OSError:
		pass

