Bandwidth Wars is a turn-based game that you play by writing a computer program to play it on your behalf.

Meta Rules
---

1.1 There is no rule that restricts a human player to entering a single bot into a game. The bot(s) may be distinct or they may be identical.  

1.2 There is no rule that prevents a human from playing in a game.  In this sense play can progress while a bot is being written or improved.

1.3 There is no rule that requires a player to disclose whether or not he is the author or maintainer of any bot, or to disclose any information about how the bot works.

1.4 In order to discourage "nerdsniping", there will be a mandatory waiting period of 7 days from the conclusion of one game to the next.

1.5 Unlike other games, which have a strong sense of "fair play", this game should follow the hacker ethos of "thinking outside the box".  If there is something you can exploit to win, use it, and then we will fix it later with a rules update.


Overview
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

A resource is mined by a nanite that stands in the square and uses the "mine" command.  The player receives approximately half of the tile's resource according to the following pseudocode:

```
player.bandwidth += random_gaussian(mean = tile.bandwidth / 2.0, stdev = tile.bandwidth / 4.0)
tile.bandwidth = tile.bandwidth / 2.0
```

Nanites
---

A nanite may perform any of the following operations:

* Move.  The nanite may move either N, S, E, or W.  
* Mine.  The nanite may mine the tile underneath it.
* Scan.  The nanite may scan all 8 tiles (N,S,E,W,NE,NW,SE,SW).  If any nanites are present in these spaces, then exactly one will be reported to the bot.
* Fire.  The nanite may fire a projectile in any of 8 directions.  This action consumes 1 plutonium.  The projectile moves at the rate of 1 square per tick.  If at any time any nanite is in the space with the projectile, it is killed.
* Duplicate.  The nanite spawns another nanite in any of 8 directions.  This action consumes 1 nanomaterial.  This operation fails silently if the requested space is obstructed by another nanite.

A nanite may only perform one command per tick.

Each command has a "times" flag which will cause the action to be performed once (immediately), twice (immediately and on the subsequent tick), or three times (immediately and on the two subsequent ticks).  Regardless of the value of the "times" flag, sending a command to a nanite consumes 1 bandwidth.  If the command is "scan", it costs 2 bandwidth.

If the nanite currently has orders, providing a new command to the nanite erases any previous orders.

At each tick, one nanomaterial for each living nanite is deducted from the player's resources.  Following this, if the player has less than zero nanomaterial, a nanite is selected at random and is killed.  A dead nanite's commands fail silently.

Global commands
---

The following commands are of "global scope"


* Hello - this command is used at the beginning (and only then) of the game to indicate the name of the bot playing.  This command is free.
* Count resource - returns the player's holdings in the specified resource.  This consumes 2 bandwidths (one for send and one for receive)
* Message - this sends a message to all the other players.  The format of the message is unspecified.  This command is free.

Game windup
---

After the conclusion of each game, a timestamped, interleaved log of all communications will be published for study or visualization.  (The log will have the transformations in "cooperative considerations" reversed for readability.)

Cooperative considerations
---

If you are playing multiple bots in a cooperative strategy, you should be aware of the following implementation details:

1.  The X and Y coordinates are randomly translated for each player.  In this way, map data is difficult to share between bots.
2.  Similarly, the nanite identifiers and player identifiers are not portable between bots.


Reference
---

This session is provided for reference.  Each command consists of a single-line JSON packet, followed by a single-line JSON response.  The ">" prompt is provided for readability, **but is not included in the bitstream**

```
{"msg":"Welcome to Bandwidth Wars","ver":1.0}

> {"cmd":"hello",name:"AwesomeBot","gameToken":"dc7b39c0-b2ee-11e2-9e96-0800200c9a66"}
{"msg":"Hello AwesomeBot.  Here's your initial nanite","nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66","x":24,"y":25,"nextTick":"2013-05-02T05:59:17Z"}

> {"cmd":"move","nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66","times":1,"dir":"N"}
{"nanite":"cd264700-b2ec-11e2-9e96-0800200c9a66",x:24,"y":24}
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
{}

#count resource
> {"cmd":"count","resource":"plutonium"}
{"count":25}

#message
> {"cmd":"message","msg":"Hello other players!"}
{"player":"215511c0-b2ee-11e2-9e96-0800200c9a66","msg":"Hello other players!"}
```
