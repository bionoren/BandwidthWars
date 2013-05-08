Bandwidth Wars is a turn-based game that you play by writing a computer program to play it on your behalf.

Policy
---

1.1 There is no rule that restricts a human player to entering a single bot into a game. Tokens will be allocated in equal number to every player.  The bot(s) may be distinct or they may be identical.  

1.2 There is no rule that prevents a human from playing in a game.  In this sense play can progress while a bot is being written or improved.

1.3 There is no rule that requires a player to disclose whether or not he is the author or maintainer of any bot, or to disclose any information about how the bot works.

1.4 In order to discourage "nerdsniping", there will be a mandatory waiting period of 7 days from the conclusion of one game to the next.

1.5 Unlike other games, which have a strong sense of "fair play", this game should follow the hacker ethos of "thinking outside the box".  If there is something you can exploit to win, use it, and then we will fix it later with a rules/code update.

1.6 Except in cases where a bug prevents the game concluding with one winner or that prevent all players from opening a socket to the server, the server will not be updated during an active game, even if the server's behavior is absurd.  You are welcome to open an issue in http://github.com/drewcrawford/BandwidthWars/issues to report issues that may be fixed before the subsequent game.

1.6.1 To implement the previous rule, a player should report a severe outage to drew@sealedabstract.com.  Play will resume from the tick prior to the outage notice, at a time specified by the server administrator with at least 24 hours' notice.





Scenario
---

Your bot controls "nanites" that are wrestling for control over a foreign planet.  Your goal is to be the last man standing.

The world consists of a discrete two-dimensional grid of infinite size.  Resources are distributed on the grid according to a published, but nondeterministic algorithm, and they can be acquired by nanites.

The planet is so far away that radio communication from your bot to your nanites is limited. It is an important aspect of gameplay to carefully conserve the communications between your bot and the foreign planet.

Ticks
---
There is one tick per hour.  Commands are executed in real time, but as a practical matter the number of legal commands you can perform in a tick is very limited.  If you wait until the last minute to execute your commands, you are at the mercy of server availability as far as executing your commands before the next tick.


Resources
---

These resources are available

* bandwidth - Most commands have a fixed bandwidth cost.  Run out of bandwidth, and you can't issue any more commands.
* nanomaterial - Used in the creation and maintenance of nanites.
* plutonium - Fired as a projectile weapon at another nanite

A resource is mined by a nanite that stands in the square and uses the "mine" command.  The player receives approximately half of the tile's resources according to the following pseudocode:

```
player.bandwidth += random_gaussian(mean = tile.bandwidth / 2.0, stdev = tile.bandwidth / 4.0)
tile.bandwidth /= 2.0
```

In this way the resources of the tile decays.  This code is repeated for each kind of resource in response for any single mine command.

The initial resource allocation is as follows: 15 bandwidth, 15 nanomaterial, 0 plutonium.

Each bot begins with a single nanite in a random position.

The resource distribution on the map is specified by the server's reference implementation, but in general it is a design goal to place nanomaterial near the center of the playing area to prevent a player from simply moving its nanites infinitely far in one direction and thereby winning the game.

Nanites
---

A nanite may perform any of the following operations:

* Move.  The nanite may move either N, S, E, or W.  
* Mine.  The nanite may mine the tile underneath it.
* Scan.  The nanite may scan all 8 tiles (N,S,E,W,NE,NW,SE,SW).  If any nanites are present in these spaces, then exactly one will be reported to the bot.
* Fire.  The nanite may fire a projectile in any of 8 directions.  This action consumes 1 plutonium.  The projectile moves at the rate of 1 square per tick infinitely far.  If at any time any nanite is in the space with the projectile, it is killed.
* Duplicate.  The nanite spawns another nanite in any of 8 directions.  This action consumes 1 nanomaterial.  This operation fails silently if the requested space is obstructed by another nanite.

A nanite may only perform one command per tick.

Each command has a "times" flag which will cause the action to be performed once (immediately), twice (immediately and on the subsequent tick), or three times (immediately and on the two subsequent ticks).  Regardless of the value of the "times" flag, sending a command to a nanite consumes 1 bandwidth.  If the command is "scan", it costs 2 bandwidth.

If the nanite currently has orders, providing a new command to the nanite replaces any previous orders.

At each tick, one nanomaterial for each living nanite is deducted from the player's resources.  Following this, if the player has less than zero nanomaterial, a nanite is selected at random and is killed.  A dead nanite's commands fail silently.  If a nanite died during the previous tick, this fact is reported to you at the next tick.

Global commands
---

The following commands are of "global scope"


* Hello - this command is used at the beginning (and only then) of the connection to indicate which bot is playing.  This command is free.
* Count resource - returns the player's holdings in the specified resource.  This consumes 2 bandwidths (one for send and one for receive)
* Message - this sends a message to all the other players.  The format of the message is unspecified.  This command is free.
* Bye - this message signals your intent to disconnect.  Using this message is optional but can resolve a race condition in receiving special messages.
* Ready - this is a special message that indicates you are done with your turn.  If all clients support "ready" and do not do a lot of computation, games are much faster.
* Mail - This command delivers messages to the player.  Certain events such as game ticks, nanite death, and so on, might occur while you are not paying attention.  Rather than require you to futz about with responding to messages at literally any time (which is hard), you simply poll for these messages when you are interested in processing them.

Game windup
---

After the conclusion of each game, a timestamped, interleaved log of all communications will be published for study or visualization.  (The log will have the transformations in "cooperative considerations" reversed for readability.)

Cooperative considerations
---

If you are playing multiple bots in a cooperative strategy, you should be aware of the following implementation details:

1.  The X and Y coordinates are randomly translated for each player.  The X and Y axes may be exchanged.  The X or Y axes may be mirrored in orientation.  In this way, map data is difficult to share between bots.
2.  Similarly, the nanite identifiers and player identifiers are not portable between bots.


Reference
---

This session is provided for reference.  Each command consists of a single-line JSON packet, followed by a single-line JSON response.  The ">" prompt is provided for readability, **but is not included in the bitstream**

```
{"msg":"Welcome to Bandwidth Wars","ver":1.0}

> {"cmd":"hello","name":"AwesomeBot","gameToken":"dc7b39c0-b2ee-11e2-9e96-0800200c9a66"}
{"msg": "Welcome back AwesomeBot.  Use 'mail' to check your messages."}

> {"cmd":"mail"}
[{"msg": "Hello.  Here's your initial nanite", "x": 7, "nanite": "70816e39-28c1-4bbc-9cc3-11b9c22b31c1", "y": -14, "special": "initial"}, {"msg": "A new tick has arrived.", "nextTick": "2013-05-08 22:57:35.890330", "tick": 1, "special": "tick"}]

> {"cmd":"mail"}
[]

> {"cmd":"move","nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66","times":1,"dir":"N"}
{"nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66",x:24,"y":24,"special":"move"}
> {"cmd":"move","nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66","times":1,"dir":"N"}
{"error":"This nanite cannot move until the next tick."}
^H
```

Sample requests and responses for commands are also provided (assuming they are legal to run):

```
#mining
> {"cmd":"mine","nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66"}
{}

#scanning
> {"cmd":"scan","nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66"}
{"x":25,"y":24,"nanite":"1b8110a0-b2ee-11e2-9e96-0800200c9a66","player":"215511c0-b2ee-11e2-9e96-0800200c9a66"}
#or
{}

#firing
> {"cmd":"fire","nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66","dir":"N"}
{}

#duplicating
> {"cmd":"fire","nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66","dir":"N"}
{"special":"duplicate","nanite":"631cc280-b634-11e2-9e96-0800200c9a66","x":25,"y":26}

#count resource
> {"cmd":"count","resource":"plutonium"}
{"count":25}

#message
> {"cmd":"message","msg":"Hello other players!"}
{"player":"215511c0-b2ee-11e2-9e96-0800200c9a66","msg":"Hello other players!"}

#bye
> {"cmd":"bye"}
{"special":"bye"}

#ready
> {"cmd":"ready"}
{}
```
