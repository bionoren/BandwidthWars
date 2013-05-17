import models.game
import unittest
class TestSequence(unittest.TestCase):
	def test_hello_twice(self):
		g = models.game.Game(open_play=True)
		result = g.process_raw_command('{"cmd":"hello","name":"TestBot","gameToken":"..."}',self)
		print result
		result = g.process_raw_command('{"cmd":"hello","name":"TestBot","gameToken":"..."}',self)
		print result
		result = g.process_raw_command('{"cmd":"count","resource":"plutonium"}',self)
		print result
