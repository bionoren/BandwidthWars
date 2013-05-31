import unittest
class TestSequence(unittest.TestCase):

	def tiledump(self,tiles):
		lyst = []
		for tile in tiles:
			toople = (tile.x,tile.y)
			lyst.append(str(toople).replace("(","{").replace(")","}"))

		print str(lyst).replace("(","{").replace(")","}").replace("'","")
	def test_startgame(self):
		import models.Map
		map = models.Map.Map()
		map.distribute_resources()


		nanomaterial_dist = []
		starttiles = []

	

		def immediate_count(map,resourcename):
			dist = 0
			dist += getattr(map.get(x,y),resourcename)
			dist += getattr(map.get(x-1,y),resourcename)
			dist += getattr(map.get(x+1,y),resourcename)
			dist += getattr(map.get(x,y-1),resourcename)
			dist += getattr(map.get(x,y+1),resourcename)
			return dist

		for x in range(-models.Map.PLAY_AREA, models.Map.PLAY_AREA):
			for y in range(-models.Map.PLAY_AREA,models.Map.PLAY_AREA):
				nanomaterial_distribution = immediate_count(map, "nanomaterial")
				bandwidth_distribution = immediate_count(map, "bandwidth")

				if nanomaterial_distribution >= 10 and nanomaterial_distribution <= 20 and bandwidth_distribution >= 10 and bandwidth_distribution <= 20:
					starttiles.append(map.get(x,y))


		self.tiledump(starttiles)

	def test_nanomaterial_center(self):
		import models.Map
		map = models.Map.Map()
		map.distribute_resources()
		lyst = []
		for x in range(-models.Map.GEN_AREA, models.Map.GEN_AREA):
			for y in range(-models.Map.GEN_AREA,models.Map.GEN_AREA):
				lyst.append('{%d,%d,%d}' % (x,y,map.get(x,y).nanomaterial))
		print str(lyst).replace('[','{').replace("'","").replace(']','}')







