import player
import Map
import json
import datetime
import uuid
import logging
import pytz

INITIAL_COMMAND = "INITIAL_COMMAND"


class Game(object):
    def __init__(self,open_play=False,max_interval=60,tokens=1):
        self.open_play = open_play
        self.players = []
        self.map = Map.Map()
        self.map.distribute_resources()
        self.max_interval=max_interval
        self.ticks = 0
        self.nextTick = None
        self.tokens = []
        logging.info("Game starting up")
        for i in range(0,tokens):
            u = uuid.uuid4()
            logging.info("created token %s" % u)
            self.tokens.append(str(u))
            p = player.Player(game=self)
            p.gameToken = str(u)
            self.players.append(p)

        def configure():
                import threading
                self.activeTimer = threading.Timer(10,_step)
                self.activeTimer.start()
        def _step():
            try:
                if self.nextTick < datetime.datetime.utcnow():
                    self.tick()
            except Exception as e:
                import traceback
                traceback.print_exc()
            configure()
        self.tick()

    def all_nanites(self):
        return (nanite for p in self.players for nanite in p.nanites) #wizardry!

    def nanite_for_tile(self,tile):
        nanites = filter(lambda nanite: nanite.tile==tile,self.all_nanites())
        if len(nanites)==1:
            return nanites[0]
        return None

    def tick(self):
        self.ticks += 1
        self.nextTick = datetime.datetime.utcnow() + datetime.timedelta(minutes=self.max_interval)
        self.nextTick = self.nextTick.replace(tzinfo=pytz.utc)
        for player in self.players:
            player.tick()
        playing = [p for p in self.players if not p.lost]
        if len(playing)<=0:
            raise Exception("End of game condition.")

        logging.info("Below is the state of the current players.")
        for player in self.players:
            logging.info("A player named %s has gameToken %s and globalUUID %s." % (player.name,player.gameToken,player.globalUUID))
            logging.info("     They have %d nanomaterial, %d bandwidth, and %d plutnoium" % (player.nanomaterial, player.bandwidth, player.plutonium))
            logging.info("     Let me tell you about their nanites:")
            for nanite in player.nanites:
                logging.info("          They have a nanite called %s located at %d, %d" % (nanite.globalUUID, nanite.tile.x,nanite.tile.y))
            if len(player.nanites)==0:
                logging.info("          They have no nanites.")



    def check_for_tick(self):
        ready_players = [p for p in self.players if p.ready]
        if len(ready_players)==len(self.players):
            self.tick()



    def process_raw_command(self,str,session):
        try:
            if str==INITIAL_COMMAND:
                return json.dumps({"msg":"Welcome to Bandwidth Wars","ver":0.1})
            try:
                struct = json.loads(str)
            except:
                return json.dumps({"error":"The provided string is not a valid JSON object.  Unescape the string and then paste into http://json.parser.online.fr to see for yourself.","string":str})
            result = self.process_json_command(struct,session)
            if result==None:
                result = {}
            return json.dumps(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return json.dumps({"error":e.message})

    def process_json_command(self,json,session):            
        if hasattr(session,"player") and session.player:
            return session.player.process_json_command(json,session)
        elif json["cmd"]=="hello":
            #let's try and look up an existing player with that gametoken
            p = filter(lambda player: player.gameToken==json["gameToken"],self.players)
            currentPlayer = None
            if len(p)==1:
                currentPlayer = p[0]
                session.player = currentPlayer
                session.player.session = session
                if not session.player.name:
                    session.player.name = json["name"]
            elif self.open_play:
                session.player = player.Player(self)
                currentPlayer = session.player
                session.player.session = session
                session.player.name = json["name"]
                session.player.gameToken = json["gameToken"]
                self.players.append(session.player)
            else:
                raise Exception("Can't find player or token invalid")
            if not currentPlayer.has_signed_in:
                currentPlayer.has_signed_in = True
                currentPlayer.threshold = json["threshold"]
            return {"msg":"Welcome back %s.  Use 'mail' to check your messages." % session.player.name}


        raise Exception("Can't understand command")


