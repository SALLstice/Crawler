import random as r
import numpy as np
import math

TPHP = 0.25
TPA = 0.1
TPD = 0.2
TPF = 0.7
TPH = 0.1
TPK = 0.3
TPM = 0.2
TPC = 0.2
TREASURE_DROP_RATE  = .45
HAZARD_RATE         = .2
PERCENT_OPEN        = .1
PERCENT_SECRET      = .1
PERCENT_LOCKED      = .2
PERCENT_TRAPPED     = .1
WANDER_CHANCE       = 0.3
MONSTER_SPAWN_RATE  = 0.5

class Dungeon:
    def __init__(self, rooms):
        self.rooms = rooms

class Monster:
    def __init__(self, health, attack, roams = True, drops = None):
        self.health = health
        self.attack = attack
        self.roams = roams
        self.drops = drops

class Treasure:
    def __init__(self, affectedStat, statBonus, equipped = False):
        self.affectedStat = affectedStat
        self.statBonus = statBonus
        self.equipped = equipped

class Hazard:
    def __init__(self, hidden, damage, disarmed = False):
        self.hidden = hidden
        self.damage = damage
        self.disarmed = disarmed

    def disarm(self):
        player.starve(self.damage)
        self.disarmed = True

class Player:
    def __init__(self, MAXHP, attack, hungerBonus, position, inv, food):
        self.health = MAXHP
        self.MAXHP = MAXHP
        self.attack = attack
        self.hunger = 101 #1 extra for initial equipping
        self.position = position
        self.inventory = inv
        self.MAXHPBonus = 0
        self.damageBonus = 0
        self.defenseBonus = 0
        self.hungerBonus = hungerBonus
        self.equipment = None
        self.hasMap = False
        self.hasCompass = False
        self.keys = 0
        self.food = food

    def starve(self, hungerValue):
        if self.hunger > 0:
            self.hunger -= max(1,(hungerValue - self.hungerBonus))
        else:
            self.health -= max(1,(hungerValue - self.hungerBonus))

    def hurt(self, hurtValue):
        self.health -= max(0, hurtValue)

        if self.health <= 0:
            print(displayRoom(player.position))
            print("dead")
            quit()

    def heal(self, healValue):
        if self.health + healValue >= self.MAXHP + self.MAXHPBonus:
            self.health = self.MAXHP + self.MAXHPBonus
        else:
            self.health += healValue

    def eat(self):
        eatNum = min(player.food, 100-self.hunger)
        self.hunger += eatNum
        self.food -= eatNum

def buildDungeon(dSize):
    routeCount = 3
    a = np.empty([dSize, dSize], dtype=object)
    dmap = np.zeros([dSize, dSize], dtype="int16")
    count = 1

    row = dSize - 1
    col = int((dSize - 1) / 2)
    a[row][col] = buildRoom(count, row)
    dmap[row][col] = count

    for cnt in range(routeCount):
        row = dSize - 1
        col = int((dSize - 1) / 2)
        count = cnt * 100 + 2

        while True:
            if row == -1:
                break

            dir =  r.randrange(1, 6)

            if dir == 1 and col > 0:
                if not a[row][col].doors["W"].door:
                    a[row][col].doors["W"] = buildDoor()

                col -= 1

                if a[row][col] is None:
                    a[row][col] = buildRoom(count, row)
                    dmap[row][col] = count
                    count += 1

                if not a[row][col].doors["E"].door:
                    a[row][col].doors["E"] = buildDoor()

            elif dir in [2, 3]:
                if not a[row][col].doors["N"].door:
                    a[row][col].doors["N"] = buildDoor()

                row -= 1

                if row != -1 and a[row][col] is None:
                    a[row][col] = buildRoom(count, row)
                    dmap[row][col] = count
                    count += 1
                elif row == -1:
                    a[0][col].monsters = [Monster(dungeonSize,math.ceil(dungeonSize/3),False,Treasure("FK",0))]
                    a = setBossDoors(a, col)

                if a[row][col] is not None and row not in  [-1, dSize-1]:
                    if not a[row][col].doors["S"].door:
                        a[row][col].doors["S"] = buildDoor()

            elif dir == 4 and col < dungeonSize-1:
                if not a[row][col].doors["E"].door:
                    a[row][col].doors["E"] = buildDoor()

                col += 1

                if a[row][col] is None:
                    a[row][col] = buildRoom(count, row)
                    dmap[row][col] = count
                    count += 1

                if not a[row][col].doors["W"].door:
                    a[row][col].doors["W"] = buildDoor()

            elif dir == 5 and row != dungeonSize-1:
                if not a[row][col].doors["S"].door:
                    a[row][col].doors["S"] = buildDoor()

                row += 1

                if a[row][col] is None:
                    a[row][col] = buildRoom(count, row)
                    dmap[row][col] = count
                    count += 1

                if not a[row][col].doors["N"].door:
                    a[row][col].doors["N"] = buildDoor()

    return a, dmap

def setBossDoors(a, col):
    a[0][col].doors["N"].bossLocked = True

    if col != 0 and a[0][col-1] is not None and a[0][col-1].doors["E"].door:
        o = a[0][col - 1].doors["E"]
        o.opened = False
        o.locked = False
        o.secret = False
        o.hidden = False
        o.trapped = False
        o.trapHidden = False
        o.trapDamage = 0
        o.bossDoor = True

    if col != np.shape(a)[1]-1 and a[0][col+1] is not None and a[0][col+1].doors["W"].door:
        o = a[0][col + 1].doors["W"]
        o.opened = False
        o.locked = False
        o.secret = False
        o.hidden = False
        o.trapped = False
        o.trapHidden = False
        o.trapDamage = 0
        o.bossDoor = True

    if a[1][col] is not None and a[1][col].doors["N"].door:
        o = a[1][col].doors["N"]
        o.opened = False
        o.locked = False
        o.secret = False
        o.hidden = False
        o.trapped = False
        o.trapHidden = False
        o.trapDamage = 0
        o.bossDoor = True

    return a

class Room:
    def __init__(self, ID, doors, monsters, treasures, hazard):
        self.ID = ID
        self.doors = doors
        self.monsters = monsters
        self.treasures = treasures
        self.hazard = hazard
        self.searched = False
        self.visited = False

def buildRoom(count, row):
    global TPHP, TPA, TPD, TPF, TPH, TPK, TPM, TPC
    global TREASURE_DROP_RATE
    global HAZARD_RATE

    wall = Door(False,False,False,False,False,False,False,0)

    do = {"W": wall, "N": wall, "E": wall, "S": wall}
    mo = []
    tre = []
    haz = None

    # Add Monsters
    if r.random() <= MONSTER_SPAWN_RATE:
        smallMonChance = ((2*row)/dungeonSize) - 1
        mediumMonChance = -((((2*row)/dungeonSize)-1)**2)+1
        bigMonChance = -((2*row)/dungeonSize) + 1

        monToAdd = r.choices(population=["S","M","B"], weights=[smallMonChance,mediumMonChance,bigMonChance])[0]
        if monToAdd == "S":
            mo.append(Monster(2, 1))
        elif monToAdd == "M":
            mo.append(Monster(2, 2))
        elif monToAdd == "B":
            mo.append(Monster(3, 3))

    # Add Treasure
    treasureStat = 0
    treasureBonus = 0

    if r.random() < TREASURE_DROP_RATE:

        tresRoll = r.choices(population=['hp','a','d','f','h','k','c','m'], weights=[TPHP,TPA,TPD,TPF,TPH,TPK,TPC,TPM])[0]
        if tresRoll == 'hp':
            treasureStat = "HP"
            treasureBonus = r.choices(population=[1,2,3,4,5], weights=[10,7,5,3,2])[0]
        elif tresRoll == 'a':
            treasureStat = 'A'
            treasureBonus = r.choices(population=[2,3,4], weights=[10,4,1])[0]
        elif tresRoll == 'd':
            treasureStat = 'D'
            treasureBonus = r.choices(population=[1,2,3], weights=[10,4,1])[0]
        elif tresRoll == 'f':
            treasureStat = "F"
            treasureBonus = r.choices(population=[5,10,20], weights=[10,4,1])[0]
        elif tresRoll == 'h':
            treasureStat = 'H'
            treasureBonus = r.choices(population=[1,2], weights=[5,1])[0]
        elif tresRoll == 'k':
            treasureStat = 'K'
            treasureBonus = 0
        elif tresRoll == 'c':
            treasureStat = 'C'
            treasureBonus = 0
            TPC = 0
        elif tresRoll == "m":
            treasureStat = 'M'
            treasureBonus = 0
            TPM = 0
        else:
            print("something went wrong with treasure gen")

        if len(mo) == 0:
            tre.append(Treasure(treasureStat, treasureBonus))

            # Add Hazard
            if r.random() <= HAZARD_RATE:
                haz = Hazard(r.choices(population=[True, False], weights=[0.3, 0.7]), r.randint(1, 4))
        else:
            mo[0].drops = Treasure(treasureStat, treasureBonus)

    roomBuild = Room(count, do, mo, tre, haz)
    return roomBuild

def wanderingMonsters():
    for i in range(dungeonSize):
        for j in range(dungeonSize):
            if dungeon[i][j] is not None and not player.position == [i,j]:
                if dungeon[i][j].monsters:
                    opendoors = [door for door in dungeon[i][j].doors if dungeon[i][j].doors[door].door and dungeon[i][j].doors[door].opened]

                    if opendoors:
                        for monster in dungeon[i][j].monsters:
                            if r.random() <= WANDER_CHANCE and monster.roams:
                                wanderection = r.choices(opendoors)[0]
                                if wanderection == "N" and dungeon[i-1][j]:
                                    dungeon[i-1][j].monsters.append(monster)
                                elif wanderection == "E":
                                    dungeon[i][j+1].monsters.append(monster)
                                elif wanderection == "S":
                                    dungeon[i+1][j].monsters.append(monster)
                                elif wanderection == "W":
                                    dungeon[i][j-1].monsters.append(monster)

                                dungeon[i][j].monsters = [x for x in dungeon[i][j].monsters if x != monster]

class Door:
    def __init__(self, door, opened, locked, secret, hidden, trapped, trapHidden, trapDamage = 0, bossDoor = False, bossLocked = False):
        self.door = door
        self.opened = opened
        self.locked = locked
        self.secret = secret
        self.hidden = hidden
        self.trapped = trapped
        self.trapHidden = trapHidden
        self.trapDamage = trapDamage
        self.bossDoor = bossDoor
        self.bossLocked= bossLocked

    def open(self):
        self.opened = True
        self.locked = False
        self.secret = False
        self.hidden = False
        self.trapped = False

    def unlock(self):
        self.locked = False

def buildDoor():

    if r.random() <= PERCENT_OPEN:
        isOpen = True
        isLocked = False
        isSecret = False
        isHidden = False
        isTrapped = False
        trapHidden = False
        trapDamage = 0
    else:
        isOpen = False

        if r.random() <= PERCENT_LOCKED:
            isLocked = True
        else:
            isLocked = False

        if r.random() <= PERCENT_SECRET:
            isSecret = True
            isHidden = True
        else:
            isSecret = False
            isHidden = False

        if r.random() <= PERCENT_TRAPPED:
            isTrapped = True
            trapHidden = True
            trapDamage = r.randint(1,3)
        else:
            isTrapped = False
            trapHidden = False
            trapDamage= 0

    doorBuild = Door(True,isOpen,isLocked,isSecret,isHidden,isTrapped,trapHidden,trapDamage)

    return doorBuild

def move(pos, dir):

    getAttacked(pos)

    roomDoor = dungeon[pos[0], pos[1]].doors[dir]

    if roomDoor.door:       #if door is not a wall
        if roomDoor.locked:
            if player.keys >= 1:
                prompt = input("B/P/K? ").upper()
            else:
                prompt = input("B/P? ").upper()

            if prompt == "B":
                player.hurt(1)
                roomDoor.unlock()
            if prompt == "P":
                player.starve(5)
                roomDoor.unlock()
            if prompt == "K":
                if player.keys >= 1:
                    player.keys -= 1
                    roomDoor.unlock()
        elif roomDoor.trapped:
            if roomDoor.trapHidden:
                player.hurt(roomDoor.trapDamage)
                roomDoor.trapHidden = False
            else:
                player.starve(roomDoor.trapDamage)
                roomDoor.trapped = False
        else:
            roomDoor.open()
            player.starve(1)

            if dir == "W":
                player.position[1] -= 1
                dungeon[player.position[0], player.position[1]].doors["E"].open()
            elif dir == "N":
                if pos[0] == 0 and dungeon[player.position[0], player.position[1]].doors["N"].bossLocked and "FK" in [o.affectedStat for o in player.inventory]:
                    print ("esc")
                    quit()
                elif pos[0] == 0:
                    pass
                else:
                    player.position[0] -= 1
                    dungeon[player.position[0], player.position[1]].doors["S"].open()
            elif dir == "E":
                player.position[1] += 1
                dungeon[player.position[0], player.position[1]].doors["W"].open()
            elif dir == "S":
                player.position[0] += 1
                dungeon[player.position[0], player.position[1]].doors["N"].open()

def fight(pos, action):
    action = int(action[1:])

    if action < len(dungeon[pos[0], pos[1]].monsters):
        dungeon[pos[0], pos[1]].monsters[action].health -= (player.attack + player.damageBonus)
        if dungeon[pos[0], pos[1]].monsters[action].health <= 0:
            if dungeon[pos[0], pos[1]].monsters[action].drops is not None:
                dungeon[pos[0], pos[1]].treasures.append(dungeon[pos[0], pos[1]].monsters[action].drops)
            del dungeon[pos[0], pos[1]].monsters[action]
        getAttacked(pos)

def getAttacked(pos):
    if len(dungeon[pos[0], pos[1]].monsters) >= 1:
        for mon in dungeon[pos[0], pos[1]].monsters:
            if mon.health > 0:
                player.hurt((mon.attack - player.defenseBonus))

def search(pos):
    pr = dungeon[pos[0], pos[1]]
    player.starve(3)

    for door in pr.doors:
        if pr.doors[door].door:
            if pr.doors[door].hidden:
                pr.doors[door].hidden = False
            elif pr.doors[door].trapped and pr.doors[door].trapHidden:
                pr.doors[door].trapHidden = False

    if pr.hazard:
        if pr.hazard.hidden:
            pr.hazard.hidden = False

    pr.searched = True

def displayRoom(pos):
    roomDisplay = ''

    pr = dungeon[pos[0], pos[1]]
    pr.visited = True
    roomDisplay += f"PH:{player.health}/{player.MAXHP + player.MAXHPBonus} PA:{player.attack + player.damageBonus} " \
                   f"PD:{player.defenseBonus} PH:{player.hunger} ({player.hungerBonus}) "
    doorlist = []

    if pr.hazard:
        if not pr.hazard.hidden and not pr.hazard.disarmed:
            roomDisplay += f"H:{pr.hazard.damage} "
        elif not pr.hazard.hidden and pr.hazard.disarmed:
            roomDisplay += f"H:{pr.hazard.damage}[D] "

    for door in pr.doors:
        if pr.doors[door].door:
            if not pr.doors[door].hidden:
                dstat = door
                if pr.doors[door].bossDoor:
                    dstat += "B"
                if pr.doors[door].secret:
                    dstat += "S"
                if pr.doors[door].trapped and not pr.doors[door].trapHidden:
                    dstat += "T"
                if pr.doors[door].locked:
                    dstat += "L"
                if not pr.doors[door].opened:
                    dstat += "C"
                elif pr.doors[door].opened:
                    dstat += "O"
                doorlist.append(dstat)
    roomDisplay += f"{doorlist} "
    if pr.searched:
        roomDisplay += "P "

    if len(pr.monsters) >= 1:
        for idx, mon in enumerate(dungeon[pos[0], pos[1]].monsters):
            if mon.health >= 1:
                roomDisplay += (f"M{idx} MH:{mon.health} MA:{mon.attack} | ")
            else:
                pass
                #roomDisplay += (f"M{idx} MH:X MA:{mon.attack} | ")
    if pr.treasures is not None:
        for tres in dungeon[pos[0], pos[1]].treasures:
            roomDisplay += (f"T:{tres.affectedStat}, {tres.statBonus} ")

    return roomDisplay

def rest():
    restLength = input("? ")
    if restLength == '':
        restLength = 10000
    else:
        restLength = int(restLength)

    while True:
        if (restLength <= 0) or (player.health >= player.MAXHP + player.MAXHPBonus) \
                or len(dungeon[player.position[0], player.position[1]].monsters) > 0:
            break
        restLength -= 1
        player.heal(1)
        player.starve(2)
        wanderingMonsters()

def pickupTreasure(pos):
    pr = dungeon[pos[0], pos[1]]

    getAttacked(pos)

    if not pr.hazard or pr.hazard.disarmed:
        for treasure in pr.treasures:
            if treasure.affectedStat == "K":
                player.keys += 1
            elif treasure.affectedStat == "F":
                player.food += treasure.statBonus
                player.eat()
            elif treasure.affectedStat == "C":
                player.hasCompass = True
            elif treasure.affectedStat == "M":
                player.hasMap = True
            else:
                player.inventory.append(treasure)

        dungeon[player.position[0], player.position[1]].treasures = None

    elif pr.hazard and not pr.hazard.disarmed:
            damage = pr.hazard.damage - player.hungerBonus
            player.hurt(damage)
            pr.hazard.hidden = False
            pr.hazard.disarmed = True

def inventory(code):
    print(f"K: {player.keys}")
    print(f"F: {player.food}")
    item = input("? ").upper()
    if "F" in item:
        player.eat()

def equipment():
    for idx, item in enumerate(player.inventory):
        if item.equipped:
            print (f"* {idx}: {item.affectedStat}, {item.statBonus}")
        else:
            print(f"  {idx}: {item.affectedStat}, {item.statBonus}")
    equip = input("I? ")
    if equip != "":
        if ("D" in equip) or ("d" in equip):
            equip = int(equip[1:])
            dungeon[player.position[0],player.position[1]].treasures.append(player.inventory[equip])
            del player.inventory[equip]
        else:
            equip = int(equip)
            useItem(player.inventory[equip])

def useItem(usedItem):
    if usedItem.affectedStat != 'F':

        if not usedItem.equipped:
            player.starve(1)

        for invItem in player.inventory:
            if invItem.equipped and invItem.affectedStat == usedItem.affectedStat:
                unequip(invItem)
                invItem.equipped = False
            if usedItem == invItem:
                equip(usedItem)
                invItem.equipped = True

def equip(item):
    if item.affectedStat == "HP": #Increase Max Health
        player.MAXHPBonus += item.statBonus
    elif item.affectedStat == "A": #increase damage
        player.damageBonus += item.statBonus
    elif item.affectedStat == "D": #increase armor
        player.defenseBonus += item.statBonus
    elif item.affectedStat == "H": #satiation
        player.hungerBonus += item.statBonus

def unequip(item):
    if item.affectedStat == "HP": #Increase Max Health
        player.MAXHPBonus -= item.statBonus
    elif item.affectedStat == "A": #increase damage
        player.damageBonus -= item.statBonus
    elif item.affectedStat == "D": #increase armor
        player.defenseBonus -= item.statBonus
    elif item.affectedStat == "H": #satiation
        player.hungerBonus -= item.statBonus

def dispMap():
    vMap = np.full_like(dungeon, "   ")
    for i in range(vMap.shape[0]):
        for j in range(vMap.shape[1]):
            if dungeon[i][j] is not None:
                room = dungeon[i][j]

                knownDoors = ''.join([door for door in room.doors if room.doors[door].door and not room.doors[door].hidden])
                box = ' '

                if knownDoors == "NE":
                    box = "└"
                elif knownDoors == "NS":
                    box = "│"
                elif knownDoors == "WN":
                    box = "┘"
                elif knownDoors == "WNE":
                    box = "┴"
                elif knownDoors == "NES":
                    box = "├"
                elif knownDoors == "WS":
                    box = "┐"
                elif knownDoors == "WES":
                    box = "┬"
                elif knownDoors == "WE":
                    box = "─"
                elif knownDoors == "WNES":
                    box ="┼"
                elif knownDoors == "WNS":
                    box = "┤"
                elif knownDoors == "ES":
                    box = "┌"

                if i == player.position[0] and j == player.position[1] and player.hasCompass and dungeon[i][j].searched:
                    vMap[i][j] = '{x}'
                elif dungeon[i][j].visited and player.hasCompass and dungeon[i][j].searched:
                    vMap[i][j] = '{' + box +'}'
                #elif dungeon[i][j].visited and not player.hasCompass and dungeon[i][j].searched:
                #    vMap[i][j] = "{ }"
                elif i == player.position[0] and j == player.position[1] and player.hasCompass:
                    vMap[i][j] = '[x]'
                elif dungeon[i][j].visited and player.hasCompass:
                    vMap[i][j] = '[' + box +']'
                elif dungeon[i][j].visited and not player.hasCompass:
                    vMap[i][j] = "[ ]"
                elif player.hasMap:
                    vMap[i][j] = "( )"

    for rowidx in range(vMap.shape[0]):
        print(' '.join([str(elem) for elem in vMap[rowidx]]))

dungeonSize = max(5, int(input("Size? ")))
dungeon, dunmap = buildDungeon(dungeonSize)
startingWeapon = Treasure("A",1)
bonus = input("S/H/C? ").upper()
if bonus == "S":
    attack = 1
else:
    attack = 0
if bonus == "H":
    hungerBonus = 1
else:
    hungerBonus = 0
if bonus == "C":
    MAX_HEALTH = 10
else:
    MAX_HEALTH = 5

player = Player(MAX_HEALTH, attack, hungerBonus, [dungeonSize - 1, int((dungeonSize - 1) / 2)], [startingWeapon], 5)
useItem(startingWeapon)
action = 0

while action != "QQ":

    action = input(displayRoom(player.position) + "? ").upper()

    if action in ["N", "S", "E", "W"]:
        move(player.position, action)
    elif "F" in action:
        fight(player.position, action)
    elif action == "M":
        dispMap()
    elif action == "P":
        search(player.position)
    elif action == "R":
        rest()
    elif action == "T":
        pickupTreasure(player.position)
    elif action == "I":
        inventory('i')
    elif action == "Q":
        equipment()
    elif action == "H":
        dungeon[player.position[0], player.position[1]].hazard.disarm()
    elif action == "HELP":
        print("NSEW: Move")
        print("FX: Fight X")
        print("P: Perception")
        print("R: Rest")
        print("T: Grab Treasure")
        print("I: Inventory")

    wanderingMonsters()