import models.game
import unittest
import json

import logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)


class TestSequence(unittest.TestCase):
	def test_hello_twice(self):
		g = models.game.Game(open_play=True)
		result = g.process_raw_command('{"cmd":"hello","name":"TestBot","gameToken":"...","threshold":2}',self)
		print result
		result = g.process_raw_command('{"cmd":"hello","name":"TestBot","gameToken":"...","threshold":2}',self)
		print result
		result = g.process_raw_command('{"cmd":"count","resource":"plutonium"}',self)
		print result

	def test_hello_bye(self):
		g = models.game.Game(open_play=True)
		result = g.process_raw_command('{"cmd":"hello","name":"TestBot","gameToken":"...","threshold":2}',self)
		print result
		result = g.process_raw_command('{"cmd":"bye"}',self)
		print result

	def test_walk_tiles(self):
		g = models.game.Game()
		immediately_reachable = g.map.get(0,0).walk_tiles()
		self.assertEquals(len(immediately_reachable),4)

		subsequently_reachable = g.map.get(0,0).walk_tiles(times=2)
		self.assertEquals(len(subsequently_reachable),13)

	def test_alter_command_Q(self):
		g = models.game.Game(open_play=True,tokens=0)
		result = g.process_raw_command('{"cmd":"hello","name":"TestBot","gameToken":"...","threshold":2}',self)

		#mail
		result = g.process_json_command({"cmd":"mail"},self)
		#start with a move
		result = g.process_json_command({"cmd":"move","nanite":self.player.nanites[0].globalUUID,"dir":"N","times":3}, self)
		#now perform a mine
		result = g.process_json_command({"cmd":"mine","nanite":self.player.nanites[0].globalUUID,"times":3}, self)
		#now we're ready
		result = g.process_json_command({"cmd":"ready"},self)

		result = g.process_json_command({"cmd":"mail"},self)
		result = filter(lambda c: c.has_key("special") and c["special"]=="mine",result)
		self.assertGreater(len(result), 0, "Didn't get mine notification as expected")



	def test_end_game_condition(self):
		g = models.game.Game(tokens=2)
		class Session:
			pass
		p1 = Session()
		p2 = Session()

		result = g.process_json_command({"cmd":"hello","name":"p1","gameToken":g.tokens[0],"threshold":2}, p1)
		result = g.process_json_command({"cmd":"hello","name":"p1","gameToken":g.tokens[1],"threshold":2}, p2)

		#p1 duplicates a bunch of times
		result = g.process_json_command({"cmd":"duplicate","nanite":p1.player.nanites[0].globalUUID,"dir":"N","times":1}, p1)
		result = g.process_json_command({"cmd":"ready"},p1)

		result = g.process_json_command({"cmd":"ready"},p2)

		#
		result = g.process_json_command({"cmd":"duplicate","nanite":p1.player.nanites[0].globalUUID,"dir":"S","times":1}, p1)
		result = g.process_json_command({"cmd":"ready"},p1)

		result = g.process_json_command({"cmd":"ready"},p2)

		p1.endgame = False
		p2.endgame = False
		for i in range(0,15):
			mail = g.process_raw_command('{"cmd":"mail"}',p1)
			mail = json.loads(mail)
			if not isinstance(mail,list): mail = [mail] #the error case isn't a list
			for msg in mail:
				print msg,"that was the message"
				if msg.has_key("special") and msg["special"]=="endgame":
					p1.endgame = True

			mail = g.process_raw_command('{"cmd":"mail"}',p2)
			mail = json.loads(mail)
			for msg in mail:
				if msg["special"]=="endgame":
					p2.endgame = True

			result = g.process_raw_command('{"cmd":"ready"}',p1)
			result = g.process_raw_command('{"cmd":"ready"}',p2)

		self.assertTrue(p1.endgame)
		self.assertTrue(p2.endgame)





