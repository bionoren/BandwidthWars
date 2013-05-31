PLAY_AREA = 20 #we confine the player to about this area
GEN_AREA = 50 #we compute resources way out here

CUTOFF_BEGIN = PLAY_AREA - 2

ALL_DIRECTIONS = ["N","S","E","W","NE","NW","SE","SW"]
import math
def dist(x,y,a,b):
	return math.sqrt((x-a)**2+(y-b)**2)

class Tile(object):
	def __init__(self,x,y,map):
		self.x = x
		self.y = y
		self.nanomaterial = 0
		self.plutonium = 0
		self.bandwidth = 0
		self.map = map

	def __repr__(self):
		return "<Tile %d, %d>" % (self.x,self.y)

	def toJson(self):
		return {"x": self.x, "y": self.y, "nanomaterial": self.nanomaterial, "bandwidth": self.bandwidth, "plutonium": self.plutonium}

	"""Counts the specified resource in the immediate tile and also the 4 immediately reachable tiles."""
	def immediate_count(self,resourcename):
		dist = 0
		dist += getattr(self,resourcename)
		dist += getattr(self.next("N"),resourcename)
		dist += getattr(self.next("S"),resourcename)
		dist += getattr(self.next("E"),resourcename)
		dist += getattr(self.next("W"),resourcename)
		return dist

	def next(self,str_dir,cardinal_only=False):
		if str_dir=="N":
			return self.map.get(self.x,self.y+1)
		elif str_dir=="S":
			return self.map.get(self.x,self.y-1)
		elif str_dir=="E":
			return self.map.get(self.x+1,self.y)
		elif str_dir=="W":
			return self.map.get(self.x-1,self.y)

		if cardinal_only: raise Exception("Not a cardinal direction")

		if str_dir=="NE":
			return self.next("N").next("E")
		elif str_dir=="NW":
			return self.next("N").next("W")
		elif str_dir=="SE":
			return self.next("S").next("E")
		elif str_dir=="SW":
			return self.next("S").next("W")

	def walk_tiles(self,times=1,cardinal_only=True):
		assert cardinal_only #not supported ATM
		results = [self.next("N"),self.next("E"),self.next("W"),self.next("S")]
		for i in range(1,times):
			for tile in list(results): #copy since we mutate the list
				next = tile.walk_tiles(times=times-1,cardinal_only=cardinal_only)
				next = filter(lambda t: t not in results,next)
				results += next
		return results

	def distance_to(self,other):
		return dist(self.x,self.y,other.x,other.y)

	def direction_derivation(self,other):
		if self.next("N")==other: return "N"
		elif self.next("S")==other: return "S"
		elif self.next("E")==other: return "E"
		elif self.next("W")==other: return "W"



class Map(object):
	def __init__(self):
		self.tiles = {}

	def playable_tiles(self):
		return (self.get(x,y) for x in range(-PLAY_AREA,PLAY_AREA) for y in range(-PLAY_AREA,PLAY_AREA))

	def valuable_tiles(self):
		return (self.get(x,y) for x in range(-GEN_AREA,GEN_AREA) for y in range(-GEN_AREA,GEN_AREA))

	def get_good_tile(self):
		good_tiles = filter(lambda t: t.immediate_count("nanomaterial") > 30 and t.immediate_count("nanomaterial") < 50,self.playable_tiles())
		good_tiles = filter(lambda t: t.immediate_count("bandwidth") > 30 and t.immediate_count("bandwidth") < 50,good_tiles)
		from random import choice
		return choice(good_tiles)


	def get(self,x,y):
		if not self.tiles.has_key(x):
			self.tiles[x] = {}
		row = self.tiles[x]
		if not row.has_key(y):
			row[y] = Tile(x,y,self)
		return row[y]


	def distribute_resources(self):
		import simplexnoise
		simplexnoise.reseed()
		for x in range(-GEN_AREA,GEN_AREA):
			for y in range(-GEN_AREA,GEN_AREA):
				tile = self.get(x,y)
				tile.nanomaterial = simplexnoise.scaled_octave_noise_2d(1, 1, 0.15, -100, 100, x, y)
				#decay if we're far from the center
				d = dist(x,y,0,0)
				if d > CUTOFF_BEGIN:
					decay = max(d-CUTOFF_BEGIN,1)
					tile.nanomaterial /= (decay)**2
					tile.nanomaterial = int(tile.nanomaterial)
					assert tile.nanomaterial <= 255
				if tile.nanomaterial < 0: tile.nanomaterial = 0 #clamp
		#bandwidth
		simplexnoise.reseed()
		for x in range(-GEN_AREA,GEN_AREA):
			for y in range(-GEN_AREA,GEN_AREA):
				tile = self.get(x,y)
				tile.bandwidth = simplexnoise.scaled_octave_noise_2d(1, 1, 0.15, -50, 50, x, y)
				if tile.bandwidth < 0: tile.bandwidth = 0 #clamp
		#plutonium
		simplexnoise.reseed()
		for x in range(-GEN_AREA,GEN_AREA):
			for y in range(-GEN_AREA,GEN_AREA):
				tile = self.get(x,y)
				tile.plutonium = simplexnoise.scaled_octave_noise_2d(1, 1, 0.3, -30, 30, x, y)
				if tile.plutonium < 0: tile.plutonium = 0 #clamp
