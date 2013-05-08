#this contains a "stripped down" implementation of Game
import Map
import json
import player
import nanite





class LocalGame(object):
	def __init__(self,local=False):
		self.open_play = True
		self.players = []
		self.map = Map.Map()
		self.ticks = 0

		pass

	def nanite_local_inject(self,n):
		n.blocked_for_ticks = 0

		def nanite_can_move_to(n,dir):
			next = n.tile.next(dir)
			if self.nanite_for_tile(next)==None: return True
			return False
		nanite.Nanite.can_move_to = nanite_can_move_to

	def all_nanites(self):
		return (nanite for p in self.players for nanite in p.nanites) #wizardry!

	def nanite_for_tile(self,tile):
		nanites = filter(lambda nanite: nanite.tile==tile,self.all_nanites())
		if len(nanites)==1:
			return nanites[0]
		return None

	def process_raw_command(self,str,session):
		try:
			struct = json.loads(str)
			result = self.process_json_command(struct,session)
			return json.dumps(result)
		except Exception as e:
			import traceback
			traceback.print_exc()
			return json.dumps({"error":e.message})

	def process_json_command(self,j,session):
		print "pjc",j
		if j.has_key("nanite"):
			nanite = [nanite for nanite in self.all_nanites() if nanite.globalUUID==j["nanite"]][0]
		if j.has_key("times"):
			session.pending_command_nanite = nanite
			session.pending_command_times = j["times"]
		else:
			session.pending_command_nanite = None
			session.pending_command_times = None
		if j["cmd"]=="hello":
			return {}
		elif j["cmd"]=="move":
			assert j.has_key("nanite")
			nanite.tile = nanite.tile.next(j["dir"])

	def process_single_json_response(self,struct,session):
		print "pjr",struct
		if struct==None: return
		#did it work?
		if not struct.has_key("error"):
			if session.pending_command_nanite:
				print "here for nanite",session.pending_command_nanite
				session.pending_command_nanite.blocked_for_ticks = session.pending_command_times
		session.pending_command_nanite = None
		session.pending_command_times = None

		if struct.has_key("special") and struct["special"]=="tick":
			self.ticks += 1
			for n in session.lplayer.nanites:
				if n.blocked_for_ticks > 0:
					n.blocked_for_ticks -= 1

		if struct.has_key("nanite"):
			n = [q for q in self.all_nanites() if q.globalUUID==struct["nanite"]]
			if len(n)==1: n=n[0]
		if struct.has_key("special") and struct["special"]=="initial":
			assert len(self.players) == 0
			self.players.append(player.Player(self))
			session.lplayer = self.players[0]
			self.nanite_local_inject(session.lplayer.nanites[0])
			session.lplayer.nanites[0].tile = self.map.get(struct["x"],struct["y"])
			session.lplayer.nanites[0].globalUUID=struct["nanite"]
		elif struct.has_key("special") and struct["special"]=="move":
			n.tile = self.map.get(struct["x"],struct["y"])
		elif struct.has_key("special") and struct["special"]=="duplicate":
			new_nanite = nanite.Nanite(player=session.lplayer,tile=self.map.get(struct["x"],struct["y"]))
			self.nanite_local_inject(new_nanite)
			new_nanite.globalUUID = struct["nanite"]


	def process_raw_response(self,str,session):
		struct = json.loads(str)
		if isinstance(struct,list):
			for item in struct:
				if item: self.process_single_json_response(item, session)
			return
		return self.process_single_json_response(struct, session)
		



