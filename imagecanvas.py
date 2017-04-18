from copy import copy, deepcopy
import random
import constants as ct

# Function just to print a plain blank canvas
#
def printBlankClusterCanvas(folderName = ".", size = 64**2, numOfClusters = 64):
	file = open("log_blank.txt", "w")
	for i in range(size):
		if i % numOfClusters == 0 and i != 0:
			file.write("\n")
		num = 0
		file.write(" " + str(num) + " ")
	file.close()

# Image Canvas is a class made to simplify the problem, to fit the images (represented 
# by ID numbers) in a txt canvas of numOfClusters x numOfClusters. This simplification 
# allow us to check for image intesection in a much easier way, avoiding dealing with 
# pixels everytime we need to make an operation. The result is stored in _clusterCanvas 
# and _embeddedPictures variables, which are read by mosaic method in mgallery.py to 
# convert from cluster to pixel coordinates.
#
# Cluster is the name given to each element in matrix _clusterCanvas. The _clusterCanvas
# has numOfClusters * numOfClusters elements, where numOfClusters = 2^clusterPow. An
# empty cluster value is 0.
#
class ImageCanvas:
	def __init__(self, minChunkSize, numOfClusters, smallestPixelChunk):
		self._initializeClusterCanvas(minChunkSize, numOfClusters, smallestPixelChunk)
		pass

	def _initializeClusterCanvas(self, minChunkSize, numOfClusters, smallestPixelChunk):
		self._minChunkSize = minChunkSize
		self._numOfClusters = numOfClusters
		self._smallestPixelChunk = smallestPixelChunk
		self._size = numOfClusters * numOfClusters
		self._clusterCanvas = [ct.CLSTR_NULL for i in range(self._size)]
		self._rating = float(0)
		self._embeddedPictures = []
		
	def _calculateCanvasRating(self, picturesUsed, pictures):
		return round(float((pictures - picturesUsed)/float(pictures)) * 100, 2)

	def getCanvasRating(self):
		return self._rating

	def getEmbedded(self):
		return self._embeddedPictures

	# Prints this clusterCanvas on a txt log. Each picture is represented by 
	# its ID.
	#
	def printClusterCanvas(self, folderName = "", canvasNumber = ""):
		if len(folderName) == 0:
			file = open("log" + str(canvasNumber) + ".txt", "w")
		else:
			file = open(folderName + "/log" + str(canvasNumber) + ".txt", "w")
		for i in range(self._size):
			if i % self._numOfClusters == 0 and i != 0:
				file.write("\n")
			num = self._clusterCanvas[i]
			if num < 10:
				file.write(" " + str(num) + " ")
			else:
				file.write(str(num) + " ")
		file.close()

	# Fetch chunk data based on picture chunk type. 
	#
	def _fetchChunk(self, picture):
		chunkType = picture.getChunkType()
		return (chunkType[0] * self._minChunkSize, \
				chunkType[1] * self._minChunkSize)

	# Converts a given cluster pivot to pixel coordinates. 
	#
	def _pivotToPixel(self, pivot):
		height, width = self._smallestPixelChunk
		x = (pivot[1] - 1)/self._minChunkSize * width
		y = (pivot[0] - 1)/self._minChunkSize * height
		return (x, y)

	# Tries to generate a Mosaic Canvas with each picture represented by a single number (ID). 
	# The Mosaic Canvas is generated as a cluster matrix of numbers so that each cluster 
	# represents a certain height and width, both in pixels. 
	#
	# The minimum chunk size is (numOfClusters/2**chunkPow) x (numOfClusters/2**chunkPow) clusters. 
	# The existing chunks are: 2 x 4, 2 x 2, 1 x 2 and 1 x 1, where each number represents a 
	# size in clusters, for example: 2 x 4 = 16 x 32 if each minimum chunk size is 8 x 8.
	#
	def genMosaicCanvas(self, pictures):
		attempt = 0
		pic0 = deepcopy(pictures[0])
		starterChunk = self._fetchChunk(pic0)
		pics = list(pictures[1:len(pictures)])
		
		starterChunkPosition = self._genRNDChunkPosition(starterChunk)
		self._placeChunkInCanvas(starterChunkPosition, starterChunk, pic0)
		self._embeddedPictures.append(pic0)
		anyPictureUsed = True

		while not self._stopCondition(pics, attempt, anyPictureUsed):
			attempt = attempt + 1
			anyPictureUsed = False
			unfittedList = []

			shuffledIndexes = [i for i in range(len(pics))]
			random.shuffle(shuffledIndexes)
			
			for i in range(len(pics)):
				sIdx = shuffledIndexes[i]
				p = deepcopy(pics[sIdx])
				c = self._fetchChunk(p)
				
				if not self._findPlaceForChunk(c, p):
					unfittedList.append(p)
				else:
					self._embeddedPictures.append(p)
					anyPictureUsed = True
			
			self._downGradePics(unfittedList)
			pics = list(unfittedList)
		
		if self.isComplete():
			print "> this canvas is completed! final attempt: " + str(attempt) + " <"
		else:
			print "> this canvas is NOT completed! <"
		self._rating = self._calculateCanvasRating(len(pics), len(pictures))
		print "rate of images used: " + str(self._rating) + "%"

	# Checks if a given chunk is placeable at pivot cluster position. 
	#
	def _isChunkPlaceableAt(self, pivot, chunk):
		pieces = self._getChunkBounds(pivot, chunk)
		for p in pieces:
			if self._clusterCanvas[self._rowColToCanvas(p)] != 0:
				return False
		return True

	# Find a place to place the picture (according to its chunk) on the cluster canvas.
	#
	def _findPlaceForChunk(self, chunk, picture):
		height, width = chunk
		step = self._minChunkSize
		for i in range(1, self._numOfClusters - height + 2, step):
			for j in range(1, self._numOfClusters - width + 2, step):
				if self._isChunkPlaceableAt((i, j), chunk):
					self._placeChunkInCanvas((i, j), chunk, picture)
					return True
		return False
	
	# Given a chunk and a pivot, get every cluster position.
	#
	def _getChunckPiecesPositions(self, pivot, chunk):
		pieces = []
		pivotRow, pivotCol = pivot
		height, width = chunk
		
		for i in range(pivotRow, pivotRow + height):
			for j in range(pivotCol, pivotCol + width):
				pieces.append((i, j))
		return pieces

	# Get the bounds in cluster coordinates 
	#
	def _getChunkBounds(self, pivot, chunk):
		pieces = []
		pivotRow, pivotCol = pivot
		height, width = chunk

		for j in range(pivotCol, pivotCol + width):
			pieces.append((pivotRow, j))
			pieces.append((pivotRow + height - 1, j))

		for i in range(pivotRow, pivotRow + height):
			pieces.append((i, pivotCol))
			pieces.append((i, pivotCol + width - 1))

		return pieces

	# Cluster canvas is completed if and only if there's no 0 left on the canvas.
	#
	def isComplete(self):
		for cluster in self._clusterCanvas:
			if cluster == 0:
				return False
		return True

	# anyPictureUsed stands for any picture used in the last loop iteration 
	# not anyPictureUsed means that no picture was used to complete the problem in the last iteration. 
	# This was used just to avoid useless loops after downgrading pictures. 
	#
	def _stopCondition(self, pictures, counter, anyPictureUsed):
		if self.isComplete() or pictures == [] or counter >= ct.MAX_TRIES or not anyPictureUsed:
			return True
		else:
			return False
	
	# Downgrades picture chunk to the immediately smallest chunk. 
	#
	def _downGradePics(self, pictures):
		downgradeFactor = 2
		for pic in pictures:
			if pic.isDowngradable():
				pic.reshape(downgradeFactor)

	def _placeChunkInCanvas(self, pivot, chunk, picture):
		picture.setPosition(self._pivotToPixel(pivot))
		pieces = self._getChunckPiecesPositions(pivot, chunk)
		for p in pieces:
			self._clusterCanvas[self._rowColToCanvas(p)] = picture.getID()

	# Converts row and column to array index representation. 
	#
	def _rowColToCanvas(self, tupleRowCol):
		return (tupleRowCol[0] - 1) * self._numOfClusters + tupleRowCol[1] - 1

	# Generates a random cluster pivot for a given chunk. 
	#
	def _genRNDChunkPosition(self, chunk):
		totalSteps = self._numOfClusters/self._minChunkSize
		height, width = chunk
		maxStepWidth = totalSteps - width/self._minChunkSize
		maxStepHeight = totalSteps - height/self._minChunkSize
		randRow = random.randint(0, maxStepHeight) * self._minChunkSize + 1
		randCol = random.randint(0, maxStepWidth) * self._minChunkSize + 1
		return (randRow, randCol)