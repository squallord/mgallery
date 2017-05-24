####################################
##  IMAGE MANIPULATION FUNCTIONS  ##
####################################

from PIL import Image, ImageDraw, ImageFont
import constants as ct

# Performs padding operation OUTSIDE the image.
#
def addPaddingOut(image, padding = ct.DEF_PADDING):
	if isinstance(image, basestring):
		img = Image.open(image)
	elif isinstance(image, Image.Image):
		img = image
	else:
		print "illegal path to image"

	pad = (padding, padding)
	newImg = Image.new("RGB", (img.size[0] + pad[0], img.size[1] + pad[1]))
	newImg.paste(ct.BCKGRND_CLR, [0, 0, newImg.size[0], newImg.size[1]])
	newImg.paste(img, (padding/2, padding/2))
	return newImg

# Performs padding operation INSIDE the image.
#
def addPaddingIn(image, padding = ct.DEF_PADDING, color = ct.BCKGRND_CLR):
	if isinstance(image, basestring):
		img = Image.open(image)
	elif isinstance(image, Image.Image):
		img = image
	else:
		print "illegal path to image"

	draw = ImageDraw.Draw(img)
	for i in range(padding):
		draw.rectangle([0 + (i - 1), 0 + (i - 1), img.size[0] - (i - 1), img.size[1] - (i - 1)], outline = color)
	
	return img

# Performs a centered crop operation with width and height.
#
def cropImage(image, width, height):
	if isinstance(image, basestring):
		img = Image.open(image)
	elif isinstance(image, Image.Image):
		img = image
	else:
		print "illegal path to image"
	
	offsetX = (img.size[0] - width)/2
	offsetY = (img.size[1] - height)/2
	img = img.crop((offsetX, offsetY, offsetX + width, offsetY + height))
	return img

# Change the image aspect ratio to match the square root of two.
#
def changeAR(image):
	if isinstance(image, basestring):
		img = Image.open(image)
	elif isinstance(image, Image.Image):
		img = image
	else:
		print "illegal path to image"

	width, height = img.size
	aspectRatio = float(width)/height
	if aspectRatio > 1:	
		if aspectRatio > ct.DEF_AR:
			width = int(height * ct.DEF_AR)
		else:
			height = int(width * 1/ct.DEF_AR)
	else:
		if aspectRatio > 1/ct.DEF_AR:
			width = int(height * 1/ct.DEF_AR)
		else: 
			height = int(width * ct.DEF_AR)

	return cropImage(img, width, height)

# Shrink image by a given factor keeping the aspect ratio.
#
def shrinkAndKeepAR(image, factor):
	if isinstance(image, basestring):
		img = Image.open(image)
	elif isinstance(image, Image.Image):
		img = image
	else:
		print "illegal path to image"
	
	if factor > 1 or factor <= 0:
		print "factor must be less than one and greater than zero"
	else:
		width, height = img.size
		return img.resize((int(width * factor), int(height * factor)))

def drawText(image, imageText):
	# make a blank image for the text, initialized to transparent text color
	img = image.convert('RGBA')
	txt = Image.new('RGBA', img.size, (255, 255, 255, 0))

	# get a font
	fnt = ImageFont.truetype('fonts/Anonymous.ttf', 80)
	
	# get a drawing context
	d = ImageDraw.Draw(txt)

	# draw text with partial opacity
	d.text((10,10), imageText, font=fnt, fill=(0, 0, 0, 150))

	return Image.alpha_composite(img, txt)

# Performs cropping followed by padding OUTSIDE operations.
#
def cropAndPadOut(image, width, height, padding):
	return addPaddingOut(cropImage(image, width, height), padding)

# Performs cropping followed by padding INSIDE operations.
#
def cropAndPadIn(image, width, height, padding):
	return addPaddingIn(cropImage(image, width, height), padding)

###################################
##  FILE MANIPULATION FUNCTIONS  ##
###################################

def isImage(file):
	components = file.split('.')
	ext = components[len(components) - 1].lower()
	if ext == 'png' or ext == 'jpg' or ext == 'jpeg' or ext == 'bmp':
		return True
	else:
		return False

def getCurrent(path):
	current = path.split('/')
	return current[len(current) - 1]

def getFileExtension(file):
	components = file.split('.')
	return components[len(components) - 1]

def printInfo(path, directories, files):
	count = len(path.split('/'))
	print 'Level: ' + str(count)
	print 'Path: ' + path
	print 'Directories: ' + ', '.join(directories)
	#print 'Files: ' + ', '.join(files)
	print 'Current Directory: ' + getCurrent(path)

	for file in files:
		if isImage(file):
			img = Image.open(path + '/' + file)
			width, height = img.size
			print '   ' + file + ' --> ' + getFileExtension(file) + \
			' width: ' + str(width) + \
			'px, height: ' + str(height) + \
			', AR: ' + str(round(float(width)/height, 5))
	print '--------------------------------------------------------------------'

# Print directory tree
def printDT(foldername = '.'):
	for path, directories, files in os.walk(foldername):
		printInfo(path, directories, files)