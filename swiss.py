import copy,re,sys,random


class Player:
    def __init__(self, name):
        self.name = name
        self.wins = []
        self.losses = []
        self.gameswon = 0
        self.sameLevelOpponentsPlayed = 0


roundPrefix = "Round: "
matchRegex = re.compile("(.*) (\d*) - (\d*) (.*)")
players = {"bye": Player("bye")}
readingNames = True
curRound = 0

playedThisRound = {}

if len(sys.argv) < 2:
    sys.exit("need to provide a tournament filename")

infile = open(sys.argv[1], 'r')
for line in infile:
    line = line.rstrip()
    print line
    if readingNames:
        if line == "--":
            readingNames = False
        else:
            players[line] = Player(line)
    else:
        if line.startswith(roundPrefix):
            accountForBye = -1
            if "bye" in playedThisRound:
                accountForBye = 0
            if curRound > 0 and len(playedThisRound) != len(players) + accountForBye:
                sys.exit("only " + str(len(playedThisRound)) + " accounted for in round " + str(curRound) + ", expected " + str(len(players)) + " players")
            playedThisRound = {}
            curRound = int(line[len(roundPrefix):])
        else:
            match = matchRegex.search(line).groups()
            p1 = match[0]
            p2 = match[3]
            p1score = match[1]
            p2score = match[2]
            if p1 in playedThisRound and p1 != "bye":
                sys.exit(p1 + " played twice in round " + str(curRound))
            if p2 in playedThisRound and p2 != "bye":
                sys.exit(p2 + " played twice in round " + str(curRound))
            playedThisRound[p1] = True
            playedThisRound[p2] = True

            players[p1].gameswon += int(p1score)
            players[p2].gameswon += int(p2score)
            if p1score > p2score:
                players[p1].wins.append(p2)
                players[p2].losses.append(p1)
            elif p1score < p2score:
                players[p1].losses.append(p2)
                players[p2].wins.append(p1)


def orderPlayersByPriority(playerList):
    orderedPlayers = {}
    for pname in playerList:
        if pname == "bye":
            continue
        p = players[pname]
        p.sameLevelOpponentsPlayed = 0
        level = len(p.wins)
        for oppname in playerList:
            opp = players[oppname]
            if oppname != pname \
            and level == len(opp.wins) \
            and (oppname in p.wins or oppname in p.losses):
                p.sameLevelOpponentsPlayed += 1
        if not level in orderedPlayers:
            orderedPlayers[level] = {}
        orderedPlayers[level][p.name] = p.sameLevelOpponentsPlayed
    return orderedPlayers


def getOpponent(pname, priority, otherRound):
    player = players[pname]
    playerLevel = len(player.wins)
    # start at the current level and try to find an opponent. if we can't, then drop to the next lower level
    for level in range(playerLevel, -1, -1):
        # don't consider players that they're playing in the other round we've already assigned
        thisLevelPlayers = [opp for opp in priority[level] if (pname not in otherRound or otherRound[pname] != opp)]

        # they cant play themself
        if pname in thisLevelPlayers:
            thisLevelPlayers.remove(pname)

        if "bye" in thisLevelPlayers:
            thisLevelPlayers.remove("bye")

        # good opponents are ones they haven't played yet
        goodOpponents = [opp for opp in thisLevelPlayers if (opp not in player.wins and opp not in player.losses)]
        if len(goodOpponents) > 0:
            return random.choice(goodOpponents)

        # if we can't find a good opponent, then give them a rematch against someone they've played
        alreadyPlayed = [opp for opp in thisLevelPlayers if (opp in player.wins or opp in player.losses)]
        if len(alreadyPlayed) > 0:
            return random.choice(alreadyPlayed)

    # we've gone through all lower levels trying to find an opponent, and we couldn't. so now we hand out byes
    return "bye"


prio = orderPlayersByPriority(players)
prio2 = copy.deepcopy(prio)
firstRoundStrings = []
secondRoundStrings = []

def assignMatches(priority, myMatches, otherRoundMatches):
    matchStrings = []
    for level in range(curRound, -1, -1):
        playersAtLevel = priority[level]
        sortedLevel = sorted(playersAtLevel, key=playersAtLevel.get, reverse=True)
        while len(sortedLevel) > 0:
            pname = sortedLevel.pop(0) # most high-risk player for rematches left in this level
            oppname = getOpponent(pname, priority, otherRoundMatches)
            player = players[pname]
            opp = players[oppname]

            myMatches[pname] = oppname
            myMatches[oppname] = pname
            matchStrings.append(pname + " # - # " + oppname)

            # we've assigned matches for this current player and their two opponents, so remove them from the maps
            del priority[len(player.wins)][pname]
            if oppname != "bye":
                del priority[len(opp.wins)][oppname]
                sortedLevel.remove(oppname)
    return matchStrings

firstRoundMatches = {}
firstRoundStrings = assignMatches(prio, firstRoundMatches, {})
secondRoundStrings = assignMatches(prio2, {}, firstRoundMatches)

print "Round: " + str(curRound + 1)
for match in firstRoundStrings:
    print match
print "Round: " + str(curRound + 2)
for match in secondRoundStrings:
    print match



