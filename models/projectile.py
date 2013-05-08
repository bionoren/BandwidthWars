class Projectile(object):
	def __init__(self,tile,game,direction):
		game.projectiles.append(self)
		self.tile = tile
		self.direction = direction

	def tick(self):
		self.tile = self.tile.next(self.direction)
		

