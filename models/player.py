import nanite
import Map
import random
import json
import uuid


class Player(object):
	def __init__(self,game):
		self.bandwidth = 15
		self.nanomaterial = 15
		self.plutonium = 0
		self.game = game
		self.nanites = []
		self.tick_notifications = []
		self.player_notifications = []
		self.lost = False
		self.session = None
		self.globalUUID = str(uuid.uuid4())
		self.ready = False
		self.name = None
		self.threshold = None
		self.has_signed_in = False

		#create an initial nanite
		tile = game.map.get(x=random.randint(-Map.PLAY_AREA,Map.PLAY_AREA),y=random.randint(-Map.PLAY_AREA,Map.PLAY_AREA))
		n = nanite.Nanite(player=self,tile=tile)
		assert len(self.nanites)==1
		self.send_or_schedule({"msg":"Hello.  Here's your initial nanite","nanite":self.nanites[0].globalUUID,"x":self.nanites[0].tile.x,"y":self.nanites[0].tile.y,"special":"initial"})

	def decrement_bandwidth(self,amt=1):
		if self.bandwidth<amt:
			raise Exception("You're out of bandwidth.")
		self.bandwidth -= amt

	##Send the message if the player is available, or schedule it to be sent the next time we see the player.
	def send_or_schedule(self,msg):
		print "scheduling a message for the future",msg
		self.player_notifications.append(msg)



	def tick(self):
		self.ready = False
		#send notifications from the previous tick
		for notification in self.tick_notifications:
			self.send_or_schedule(notification)
		self.tick_notifications = []
		
		self.deadpool = []
		for nanite in self.nanites:
			self.nanomaterial -= 1
			print "losing 1 nanomaterial for nanite ",nanite
			self.tick_notifications.extend(nanite.tick())
		if self.nanomaterial <= 0:
			kill = random.choice(self.nanites)
			self.nanites.remove(kill)
			self.deadpool.append(kill)
			self.tick_notifications.append({"msg":"a nanite was killed","nanite":kill.globalUUID})
			print "killed nanite",kill.globalUUID
		self.send_or_schedule({"special":"tick","msg":"A new tick has arrived.","tick":self.game.ticks,"nextTick":str(self.game.nextTick)})

		if len(self.nanites)==0:
			self.lost = True



	def process_json_command(self,json,session):
		if self.lost:
			return {"error":"You have lost the game."}
		nanite = None
		if json.has_key("nanite"):
			nanite = [nanite for nanite in self.nanites if nanite.globalUUID==json["nanite"]][0]
		

		if json["cmd"]=="message":
			for player in self.game.players:
				player.send_or_schedule({"msg":json["msg"],"special":"message","player":player.globalUUID})
			return {}
		if json["cmd"]=="mail":
			value =  self.player_notifications
			self.player_notifications = []
			return value
		elif json["cmd"]=="move":
			return nanite.immediate_or_schedule(nanite.move,json["times"],1,json["dir"])
		elif json["cmd"]=="mine":
			return nanite.immediate_or_schedule(nanite.mine,json["times"],1)
		elif json["cmd"]=="duplicate":
			return nanite.immediate_or_schedule(nanite.duplicate,json["times"],1,json["dir"])
		elif json["cmd"]=="count":
			count = -1
			if json["resource"]=="plutonium":
				count = self.plutonium
			elif json["resource"]=="nanomaterial":
				count = self.nanomaterial
			elif json["resource"]=="bandwidth":
				count = self.bandwidth
			self.decrement_bandwidth()
			return {"count":count}
		elif json["cmd"]=="bye":
			self.session.player = None
			self.session = None
			return {"special":"bye"}
		elif json["cmd"]=="ready":
			self.ready = True
			self.game.check_for_tick()
			return {}

		raise Exception("Command not known or not acceptable now: %s" % json["cmd"])






