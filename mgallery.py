###############################
##  A MOSAIC GALLERY SCRIPT  ##
###############################
##  Made with Python 2.7.9   ##
###############################

from PIL import Image
import os, utils
import constants as ct
import imagecanvas as ic
import picture as pct

# Reloads every associated module.
#
def _rld():
	reload(ic)
	reload(pct)
	reload(utils)
	reload(ct)

# Just clears the log folder to avoid mixing the past and
# current results.
#
def _clearLog():
	if os.path.exists(str(os.getcwd()) + "/log"):
		for file in os.listdir("log"):
			filePath = "log/" + str(file)
			try:
				if os.path.isfile(filePath):
					os.unlink(filePath)
			except Exception as e:
				print e
	else:
		os.mkdir("log")

def _stopCondition(attempt, maxAttempts):
	if attempt >= maxAttempts:
		return True

# Get the canvas that has the highest rate of image usage.
#
def _getHighest(canvasList):
	if len(canvasList) > 0:
		highest = canvasList[0]
		for canvas in canvasList:
			if highest.getCanvasRating() < canvas.getCanvasRating():
				highest = canvas
		return highest

def _generateBlankPixelCanvas(paperSize):
	width, height = paperSize
	blankCanvas = Image.new("RGB", paperSize)
	blankCanvas.paste(ct.BCKGRND_CLR, [0, 0, width, height])
	return blankCanvas

# Get each image from a canvas and paste it on a new image with paperSize dimensions.
# Uncomment picture.addID() to add the ID as a text overlay to each picture.
# 
def _pasteImagesInCanvas(paperSize, canvas, padding, color, debug):
	pixelCanvas = _generateBlankPixelCanvas(paperSize)
	for picture in canvas.getEmbedded():
		picture.addPadding(padding, color)
		if debug:
			picture.writeTXT('ID: ' + str(picture.getID()), 25, (0, 0))
			picture.writeTXT(picture.getName(), 25, (0, 30))
		pixelCanvas.paste(picture.getImage(), picture.getPosition())
	return pixelCanvas

def _savePixelCanvas(pixelCanvas, name = "mosaic_gallery.jpg"):
	pixelCanvas.save(name)

def _getPixelChunk(smallestPixelChunk):
	width = smallestPixelChunk[1]
	height = smallestPixelChunk[0]
	ar = float(width / height)

	if ar < 1:
		return [(2 * height, 4 * width),
				(2 * height, 2 * width),
				(height, 2 * width),
			  	(height, width)]
	else:
		return [(4 * height, 2 * width),
				(2 * height, 2 * width),
				(2 * height, width),
				(height, width)]

############################################################################################################
##                                       >>> Main program <<<                                             ##
############################################################################################################
# folderName: relative path to the folder that contains the images                                         #
# maxAttempts: maximum number of times the algorithm runs (highter values should improve the final result) #
# paperSize: the size in pixels of the paper (use numbers that are divisible by 8)                         #
# clusterPow: 2^clusterPow will define the minimum chunk size in clusters                                  #
# padding: padding in pixels to be added to each image                                                     #
# color: the padding color                                                                                 #
############################################################################################################
#
# This method tries to find a closed solution for the mosaic gallery problem. Be aware that a solution
# may not exist. It'll depend mostly on the number of images and the size of each individual image.
# Each image must be at least width/2^clusterPow x height/2^clusterPow in pixels to fit in the 
# smallest chunk available.
# 
# Instead of fiding a closed solution, given a collection of images, the program tries to guess by
# trial and error. For each attempt, it tries to fill the paper (final image) with each image inside
# img_folder. If it succeed, the result (an ImageCanvas) is stored in a list. Then, the program
# tries to find the ImageCanvas with hightest rate of image usage among the items in this list.
# Based on the hightest ImageCanvas, the program then outputs the big image (mosaic_gallery.jpg)
# with every successfully fit image on it. This means that not 100% of the images could be used.
# It most commomnly fits about 70 to 90% of the pictures (at least in this first version).
#
# Despite having two modes of mosaic composition (landscape and portrait) keep in mind that most of pictures
# are taken in landscape format. Hence, it's probably gonna be harder to complete the whole canvas in the
# portrait scenario.
#

def mosaic(folderName = "img_folder",
		   maxAttempts = ct.MAX_ATTEMPTS,
		   paperSize = ct.SZ_75x50,
		   clusterPow = ct.SZ_CLSTR,
		   padding = ct.DEF_PADDING,
		   color = ct.BCKGRND_CLR,
           debug = False):

	_rld()
	_clearLog()
	pictures = []
	attempt = 0
	minChunkSize = 2**clusterPow
	width = int(round(paperSize[0] / minChunkSize))
	height = int(round(paperSize[1] / minChunkSize))

	# pixel chunk is defined by (lines, columns) format, hence (height, width)
	# when resizing to the closest chunk, keep this in mind
	smallestPixelChunk = (height, width)
	pixelChunks = _getPixelChunk(smallestPixelChunk)
	canvasList = []

	print "pixel chunks: " + str(pixelChunks)

	count = 0
	for path, directory, files in os.walk(folderName):
		for f in files:
			if utils.isImage(f):
				count = count + 1
				p = path + "/" + f
				pictures.append(pct.Picture(f, p, Image.open(p), count))

	print str(len(pictures)) + " pictures to form a mosaic gallery"

	resizedPictures = []
	for i in range(len(pictures)):
		if pictures[i].resizeToClosestChunk(pixelChunks, smallestPixelChunk):
			resizedPictures.append(pictures[i])
		else:
			print "ID: " + str(pictures[i].getID()) + " with name " + pictures[i].getName() +\
				  " could not be resized"
	pictures = resizedPictures

	while not _stopCondition(attempt, maxAttempts):
		attempt = attempt + 1
		print "program at #" + str(attempt) + " attempt ..."
		canvas = ic.ImageCanvas(int(minChunkSize), int(minChunkSize**2), smallestPixelChunk)
		canvas.genMosaicCanvas(pictures)
		if canvas.isComplete():
			canvasList.append(canvas)
			canvas.printClusterCanvas("log", attempt)
	print "... " + str(len(canvasList)) + " completed image canvas"

	if len(canvasList) > 0:
		highest = _getHighest(canvasList)
		highest.printClusterCanvas("", "_highest")
		print str(highest.getCanvasRating()) + " is the highest rating of this simulation"

		pixelCanvas = _pasteImagesInCanvas(paperSize, highest, padding, color, debug)
		_savePixelCanvas(pixelCanvas)
	else:
		print "simulation endend without finding a solution for the problem ..."

if __name__ == '__main__':
	mosaic()