import uuid
import Map
import random
import projectile
import logging


class require_not_moved(object):

    def __init__(self):
        pass
    def __call__(dself, f):
        def _require_not_moved(self,*args,**kwargs):
            if self.moved_this_turn:
                    return {"error":"Already moved this turn.  The command queue was altered anyway."}
            returnValue = f(self,*args,**kwargs)
            if returnValue and returnValue.has_key("error"): return returnValue
            self.moved_this_turn = True
            return returnValue
        return _require_not_moved

    def __get__(self, instance, instancetype):
        import functools
        """Implement the descriptor protocol to make decorating instance 
        method possible.

        """

        # Return a partial function with the first argument is the instance 
        #   of the class decorated.
        return functools.partial(self.__call__, instance)

class Nanite(object):
    def __init__(self,tile,player):
        self.globalUUID = str(uuid.uuid4())
        self.tile = tile
        self.player = player
        player.nanites.append(self)
        self.moved_this_turn = False
        self.commandQueue = []

    def immediate_or_schedule(self,func,times,bandwidth,*args,**kwargs):
        if self.player.bandwidth < bandwidth:
            return {"error":"Not enough bandwidth"}
        self.player.bandwidth -= bandwidth
        self.commandQueue = []
        def wrap():
            return func(*args,**kwargs)
        for t in range(1,times):
            self.commandQueue.append(wrap)
        print "cq is",self.commandQueue
        result = wrap()
        
        return result


    @require_not_moved()
    def move(self,dir):
        newTile = self.tile.next(dir)
        if self.player.game.nanite_for_tile(newTile):
            return {"error":"This tile is occupied."}
        self.tile = self.tile.next(dir)
        return {"nanite":self.globalUUID,"x":self.tile.x,"y":self.tile.y,"special":"move"}

    @require_not_moved()
    def scan(self,dir):
        shuffled_dirs = list(Map.ALL_DIRECTIONS)
        random.shuffle(shuffled_dirs)
        all_nanites = self.player.game.all_nanites()
        scan_result = None
        for dir in shuffled_dirs:
            tile = self.tile.next(dir)
            s = filter(lambda n: n.tile==tile,all_nanites)
            if len(s):
                scan_result = s[0]
                break
        return {"nanite":self.globalUUID,"special":"scan","scan_result":scan_result}


    @require_not_moved()
    def search(self,resource):
        """ "2" spaces away (see #15) is somewhat nonintuitive.  What this implementation actually does is
          X
         XXX
        XXNXX
         XXX
          X

          Essentially this finds all squares reachable if the nanite has 2 turns to move.  Nonintuitively, this includes the space presently occupied by the nanite since the nanite can reach its current space in 2 steps."""
        spaces = self.tile.walk_tiles(times=2,cardinal_only=True)
        spaces = filter(lambda tile: getattr(tile,resource) >= self.player.threshold * 2,spaces)
        from random import choice
        if len(spaces) >= 1:
            chosen_one = choice(spaces)
        else:
            chosen_one = None
        if chosen_one:
            x = chosen_one.x
            y = chosen_one.y
        else:
            x = None
            y = None
        return {"nanite":self.globalUUID,"special":"search","x":x,"y":y,"resource":resource}



    @require_not_moved()
    def mine(self):
        self.player.bandwidth += random.normalvariate(mu = self.tile.bandwidth / 2.0, sigma = self.tile.bandwidth / 4.0)
        self.tile.bandwidth /= 2.0

        self.player.plutonium += random.normalvariate(mu = self.tile.plutonium / 2.0, sigma = self.tile.plutonium / 4.0)
        self.tile.plutonium /= 2.0

        self.player.nanomaterial += random.normalvariate(mu = self.tile.nanomaterial / 2.0, sigma = self.tile.nanomaterial / 4.0)
        self.tile.nanomaterial /= 2.0

        result = {"nanite":self.globalUUID,"special":"mine"}

        if self.tile.bandwidth + self.tile.plutonium + self.tile.nanomaterial < self.player.threshold:
            result["threshold"] = "<"
        else:
            result["threshold"] = ">="
        return result

    @require_not_moved()
    def fire(self,dir):
        p = projectile.Projectile(direction=dir,game=self.player.game,tile=self.tile)
        p.tick() #first tick to move into the initial space and do collision detection

    @require_not_moved()
    def duplicate(self,dir):
        newTile = self.tile.next(dir)
        if self.player.game.nanite_for_tile(newTile):
            return {"error":"This tile is occupied."}
        new_nanite = Nanite(tile=newTile,player=self.player)
        return {"special":"duplicate","nanite":new_nanite.globalUUID,"x":new_nanite.tile.x,"y":new_nanite.tile.y,"oldNanite":self.globalUUID}


    def clear(self):
        self.commandQueue = []






    def tick(self):
        tick_notifications = []
        self.moved_this_turn = False
        if len(self.commandQueue):
            command = self.commandQueue.pop(0)
            tick_notifications.append(command())
            logging.info("nanite generating tick notifications called %s" % tick_notifications)
        return tick_notifications




