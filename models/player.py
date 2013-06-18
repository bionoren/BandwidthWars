import nanite
import Map
import random
import json
import uuid
import logging


class Player(object):
    def __init__(self,game,tile=None):
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

        if self.game.debug:
            self.offsetx = 0
            self.offsety = 0
        else:
            self.offsetx = random.randint(-10,10)
            self.offsety = random.randint(-10,10)
        logging.info("cooperative consideration: player %s is offset by %d,%d" % (self.globalUUID,self.offsetx,self.offsety))

        #create an initial nanite
        if not tile:
            tile = game.map.get_good_tile()
        n = nanite.Nanite(player=self,tile=tile)
        assert len(self.nanites)==1
        self.send_or_schedule({"msg":"Hello.  Here's your initial nanite","nanite":self.nanites[0].globalUUID,"x":self.nanites[0].tile.x,"y":self.nanites[0].tile.y,"special":"initial"})

    def decrement_bandwidth(self,amt=1):
        if self.bandwidth<amt:
            raise Exception("You're out of bandwidth.")
        self.bandwidth -= amt

    def __confuddle(self,key,val):
        if key=="x":
            if val is not None:
                return val + self.offsetx
        if key=="y":
            if val is not None:
                return val + self.offsety
        return val

    def __unfuddle(self,key,val):
        if key=="x":
            return val - self.offsetx
        if key=="y":
            return val - self.offsety
        return val

    def __apply(self,struct,fn,**kwargs):
        if isinstance(struct, dict):
            transformDict = dict()
            for (key, val) in struct.iteritems():
                transformDict[key] = fn(key,val)
            return transformDict
        elif isinstance(struct, list):
            transformList = list()
            for item in struct:
                transformList.append(self.__apply(item, fn,**kwargs))
            return transformList
        elif isinstance(struct, tuple):
            raise Exception ("What to do with tuple?")
        else:
            return struct

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
            if self.game.ticks != 1:
                self.nanomaterial -= 1
                logging.info("losing 1 nanomaterial for nanite "+str(nanite))
            notifications = nanite.tick()
            for notification in notifications:
                self.send_or_schedule(notification)
        while self.nanomaterial < 0:
            kill = random.choice(self.nanites)
            self.nanites.remove(kill)
            self.deadpool.append(kill)
            self.tick_notifications.append({"msg":"a nanite was killed","nanite":kill.globalUUID})
            self.nanomaterial += 1
            print "killed nanite",kill.globalUUID
        self.send_or_schedule({"special":"tick","msg":"A new tick has arrived.","tick":self.game.ticks,"nextTick":str(self.game.nextTick)})

        if len(self.nanites)==0:
            self.lost = True

    def process_json_command(self,json,session):
        unfuddled_version = self.__apply(json,fn=self.__unfuddle)
        if not json['cmd'] == 'debugMap':
            logging.info("from %s> %s" % (self.globalUUID,unfuddled_version))
        result = self.__process_json_command(unfuddled_version, session)
        if not json['cmd'] == 'debugMap':
            logging.info("to %s> %s" % (self.globalUUID,result))
        transformed_result =  self.__apply(result,fn=self.__confuddle)
        return transformed_result

    def __process_json_command(self,json,session):
        if not json.has_key("times"):
            json["times"] = 1

        if json["cmd"]=="mail":
            value =  self.player_notifications
            self.player_notifications = []
            return value
        if self.lost:
            return {"error":"You have lost the game."}
        nanite = None
        if json.has_key("nanite"):
            nanite = [nanite for nanite in self.nanites if nanite.globalUUID==json["nanite"]][0]


        if json["cmd"]=="message":
            for player in self.game.players:
                player.send_or_schedule({"msg":json["msg"],"special":"message","player":player.globalUUID})
            return {}
        elif json["cmd"]=="move":
            return nanite.immediate_or_schedule(nanite.move,json["times"],1,json["dir"])
        elif json["cmd"]=="mine":
            return nanite.immediate_or_schedule(nanite.mine,json["times"],1)
        elif json["cmd"]=="duplicate":
            return nanite.immediate_or_schedule(nanite.duplicate,json["times"],1,json["dir"])
        elif json["cmd"]=="search":
            return nanite.immediate_or_schedule(nanite.search,json["times"],2,json["resource"])
        elif json["cmd"]=="clear":
            return nanite.immediate_or_schedule(nanite.clear,1,0)
        elif json["cmd"]=="count":
            count = -1
            if json["resource"]=="plutonium":
                count = self.plutonium
            elif json["resource"]=="nanomaterial":
                count = self.nanomaterial
            elif json["resource"]=="bandwidth":
                count = self.bandwidth
            self.decrement_bandwidth()
            return {"count":count,"special":"count","resource":json["resource"]}
        elif json["cmd"]=="bye":
            self.session.player = None
            self.session = None
            return {"special":"bye"}
        elif json["cmd"]=="ready":
            self.ready = True
            self.game.check_for_tick()
            return {}
        elif self.game.debug:
            if json["cmd"] == "listNanites":
                return {"nanites": map(lambda n: n.json(), self.nanites)}
            if json["cmd"] == "listResources":
                return {"nanomaterial": self.nanomaterial, "bandwidth": self.bandwidth, "plutonium": self.plutonium}
            if json["cmd"] == "debugMap":
                return {"map": map(lambda tile: tile.toJson(), self.game.map.gen_area_tiles())}

        raise Exception("Command not known or not acceptable now: %s" % json["cmd"])
