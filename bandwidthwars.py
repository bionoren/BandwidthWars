
import logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
#set their handler to INFO
logging.getLogger().handlers[0].level = logging.INFO

hdlr = logging.FileHandler('game.log')
hdlr.setFormatter(logging.Formatter(fmt=FORMAT))
hdlr.setLevel(logging.DEBUG)
logging.getLogger().addHandler(hdlr)
logging.info("Writing to game.log")



if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bandwidth Wars")
    parser.add_argument('--port',default=7171,type=int)
    parser.add_argument('--turn_max',default=60,help="The maximum time allocated per turn",type=int)
    parser.add_argument('--tokens',default=2,help="How many tokens should be generated for this game.",type=int)
    parser.add_argument('--open-play',dest='open_play',action='store_true',help="Whether the server allows just anyone to play.")
    parser.set_defaults(open_play=False)
    args = parser.parse_args()

    import models.game
    game = models.game.Game(max_interval=args.turn_max,tokens=args.tokens,open_play=args.open_play)

    from twisted.internet import protocol, reactor
    import twisted.protocols.basic

    class BW(twisted.protocols.basic.LineReceiver):

        def __init__(self):
            self.delimiter = '\n'
        def connectionMade(self):
            self.transport.write('{"msg":"Welcome to Bandwidth Wars","ver":0.1}\n')
        def lineReceived(self, data):
            if hasattr(self,"player"):
                player = self.player.gameToken
            else:
                player = "???"
            logging.debug("raw socket from %s> %s" % (player,data))
            result = game.process_raw_command(data, self)

            self.send_raw(result)

        def send_raw(self,data):
            if hasattr(self,"player") and self.player != None:
                player = self.player.gameToken
            else:
                player = "???"
            logging.debug("raw socket to %s> %s" % (player,data))
            self.transport.write(data+"\n")

    class BWFactory(protocol.Factory):
        def buildProtocol(self, addr):
            return BW()

    logging.info("Listening on port %d",args.port)
    reactor.listenTCP(args.port, BWFactory())
    reactor.run()
