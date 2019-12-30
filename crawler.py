import random as r
import numpy as np

TPHP = 0.25
TPA = 0.1
TPD = 0.2
TPF = 0.7
TPH = 0.1
TPK = 0.3
TPM = 0.2
TPC = 0.2
TREASURE_DROP_RATE = 0.45
HAZARD_RATE = 0.3

class Dungeon:
    def __init__(self):
        pass

class Monster:
    def __init__(self, health, attack):
        self.health = health
        self.attack = attack

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
    def __init__(self, MAXHP, attack, hunger, position, inv):
        self.health = MAXHP
        self.MAXHP = MAXHP
        self.attack = attack
        self.hunger = hunger
        self.position = position
        self.inventory = inv
        self.MAXHPBonus = 0
        self.damageBonus = 0
        self.defenseBonus = 0
        self.hungerBonus = 0
        self.equipment = None
        self.hasMap = False
        self.hasCompass = False

    def starve(self, hungerValue):
        if self.hunger > 0:
            self.hunger -= max(1,(hungerValue - self.hungerBonus))
        else:
            self.health -= max(1,(hungerValue - self.hungerBonus))

    def hurt(self, hurtValue):
        self.health -= hurtValue
        if self.health <= 0:
            print("dead")
            quit()

    def heal(self, healValue):
        if self.health + healValue >= self.MAXHP + self.MAXHPBonus:
            self.health = self.MAXHP + self.MAXHPBonus
        else:
            self.health += healValue

def buildDungeon(dSize):

    routeCount = 2
    a = np.empty([dSize, dSize], dtype=object)
    dmap = np.zeros([dSize, dSize], dtype="int16")
    count = 1

    row = dSize - 1
    col = int((dSize - 1) / 2)
    a[row][col] = buildRoom(count)
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

                if a[row][col].doors["W"].state == -1:
                    a[row][col].doors["W"] = buildDoor()

                col -= 1

                if a[row][col] is None:
                    a[row][col] = buildRoom(count)
                    dmap[row][col] = count
                    count += 1

                if a[row][col].doors["E"].state == -1:
                    a[row][col].doors["E"] = buildDoor()

            elif dir in [2, 3]:

                if a[row][col].doors["N"].state == -1:
                    a[row][col].doors["N"] = buildDoor()

                row -= 1

                if row != -1 and a[row][col] is None:
                    a[row][col] = buildRoom(count)
                    dmap[row][col] = count
                    count += 1

                if a[row][col] is not None and row not in  [-1, dSize-1]:
                    if a[row][col].doors["S"] is None:
                        a[row][col].doors["S"] = buildDoor()

            elif dir == 4 and col < dungeonSize-1:

                if a[row][col].doors["E"].state == -1:
                    a[row][col].doors["E"] = buildDoor()

                col += 1

                if a[row][col] is None:
                    a[row][col] = buildRoom(count)
                    dmap[row][col] = count
                    count += 1

                if a[row][col].doors["W"].state == -1:
                    a[row][col].doors["W"] = buildDoor()

            elif dir == 5 and row != dungeonSize-1:

                if a[row][col].doors["S"].state == -1:
                    a[row][col].doors["S"] = buildDoor()

                row += 1

                if a[row][col] is None:
                    a[row][col] = buildRoom(count)
                    dmap[row][col] = count
                    count += 1

                if a[row][col].doors["N"].state == -1:
                    a[row][col].doors["N"] = buildDoor()

    return a, dmap, count

class Room:
    def __init__(self, ID, doors, monsters, treasures, hazard):
        self.ID = ID
        self.doors = doors
        self.monsters = monsters
        self.treasures = treasures
        self.hazard = hazard
        self.searched = False
        self.visited = False

def buildRoom(count):
    global TPHP, TPA, TPD, TPF, TPH, TPK, TPM, TPC
    global TREASURE_DROP_RATE
    global HAZARD_RATE

    do = {"W": Door(-1), "N": Door(-1), "E": Door(-1), "S": Door(-1)}
    mo = []
    tre = []
    haz = []

    # Add Hazards
    if r.random() <= HAZARD_RATE:
        haz = Hazard(r.choices(population=[True,False], weights=[0.3,0.7]),r.randint(1,4))
    else:
        haz = Hazard(True,0,True)

    # Add Monsters
    if count <= int(dungeonSize / 2):
        for i in range(r.randrange(0, 3)):
            mo.append(Monster(2, 1))
    elif count <= dungeonSize:
        for i in range(r.randrange(0, 2)):
            mo.append(Monster(2, 2))
    elif count <= dungeonSize * 2:
        for i in range(r.randrange(0, 2)):
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

        tre.append(Treasure(treasureStat, treasureBonus))

    roomBuild = Room(count, do, mo, tre, haz)
    return roomBuild

class Door:
    def __init__(self, state, trapped = False, trapDamage = 0):
        self.state = state
        # -1 : Wall
        #  0 : Open
        #  1 : Closed
        #  2 : Locked
        #  3 : Secret
        #  4 : Hidden
        self.trapped = trapped
        self.trapDamage = trapDamage

def buildDoor():
    PERCENT_SECRET = .1
    PERCENT_LOCKED = .2
    PERCENT_TRAPPED = .1

    randChoice = r.choices(population=['secret', 'locked', 'closed'],
                           weights=[PERCENT_SECRET, PERCENT_LOCKED, 1-(PERCENT_SECRET+PERCENT_LOCKED)])[0]

    if randChoice == 'secret':
        doorbuild = Door(4)
    elif randChoice == 'locked':
        doorbuild = Door(2)
    else:
        doorbuild = Door(1)



    return doorbuild

def move(pos, dir):

    getAttacked(pos)

    if dungeon[pos[0], pos[1]].doors[dir].state > -1:       #if door is not a wall
        if dungeon[pos[0], pos[1]].doors[dir].state == 2:
            prompt = input("B/P/K? ").upper()
            if prompt == "B":
                player.hurt(1)
                dungeon[pos[0], pos[1]].doors[dir].state = 1
            if prompt == "P":
                player.starve(5)
                dungeon[pos[0], pos[1]].doors[dir].state = 1
            if prompt == "K":
                for idx, item in enumerate(player.inventory):
                    if item.affectedStat == "K":
                        del player.inventory[idx]
                        dungeon[pos[0], pos[1]].doors[dir].state = 1
                        break
        else:
            dungeon[pos[0], pos[1]].doors[dir].state = 0
            player.starve(1)

            if dir == "W":
                player.position[1] -= 1
                dungeon[player.position[0], player.position[1]].doors["E"].state = 0
            elif dir == "N":
                if dungeon[pos[0], pos[1]].doors[dir].state > -1 and pos[0] == 0:
                    print ("esc")
                    quit()
                else:
                    player.position[0] -= 1
                    dungeon[player.position[0], player.position[1]].doors["S"].state = 0
            elif dir == "E":
                player.position[1] += 1
                dungeon[player.position[0], player.position[1]].doors["W"].state = 0
            elif dir == "S":
                player.position[0] += 1
                dungeon[player.position[0], player.position[1]].doors["N"].state = 0


def fight(pos, action):
    action = int(action[1:])

    dungeon[pos[0], pos[1]].monsters[action].health -= (player.attack + player.damageBonus)
    player.starve(2)

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
        if pr.doors[door].state > -1:
            if pr.doors[door].state == 4:
                pr.doors[door].state = 3

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

    if not pr.hazard.hidden and not pr.hazard.disarmed:
        roomDisplay += f"H:{pr.hazard.damage} "
    elif not pr.hazard.hidden and pr.hazard.disarmed:
        roomDisplay += f"H:{pr.hazard.damage}[D] "

    for door in pr.doors:
        if pr.doors[door].state > -1:
            if pr.doors[door].state != 4:
                dstat = door
                if pr.doors[door].state == 3:
                    dstat += "S"
                if pr.doors[door].state == 2:
                    dstat += "L"
                if pr.doors[door].state == 1:
                    dstat += "C"
                if pr.doors[door].state == 0:
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
    restLength = int(input("? "))

    while True:
        if (restLength <= 0) or (player.health >= player.MAXHP + player.MAXHPBonus):
            break
        restLength -= 1
        player.heal(1)
        player.starve(2)

def pickupTreasure(pos):
    pr = dungeon[pos[0], pos[1]]

    getAttacked(pos)

    if not pr.hazard.disarmed:
        player.hurt(pr.hazard.damage)
        pr.hazard.hidden = False
        pr.hazard.disarmed = True
    else:
        for treasure in pr.treasures:
            if treasure.affectedStat not in ["C", "M"]:
                player.inventory.append(treasure)
            elif treasure.affectedStat == "C":
                player.hasCompass = True
            elif treasure.affectedStat == "M":
                player.hasMap = True

        dungeon[player.position[0], player.position[1]].treasures = None

def inventory():
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
        player.MAXHPBonus = 0
        player.damageBonus = 0
        player.defenseBonus = 0
        player.hungerBonus = 0

        for invItem in player.inventory:
            if usedItem == invItem:
                invItem.equipped = True
            else:
                invItem.equipped = False

    if usedItem.affectedStat == "HP": #Increase Max Health
        player.MAXHPBonus = usedItem.statBonus
    elif usedItem.affectedStat == "A": #increase damage
        player.damageBonus = usedItem.statBonus
    elif usedItem.affectedStat == "D": #increase armor
        player.defenseBonus = usedItem.statBonus
    elif usedItem.affectedStat == 'F': #feed
        player.hunger += usedItem.statBonus
        player.inventory = [y for y in player.inventory if y != usedItem]
    elif usedItem.affectedStat == "H": #satiation
        player.hungerBonus = usedItem.statBonus

def dispMap():
    vMap = np.full_like(dungeon, "   ")
    for i in range(vMap.shape[0]):
        for j in range(vMap.shape[1]):
            if dungeon[i][j] is not None:
                if i == player.position[0] and j == player.position[1] and player.hasCompass and dungeon[i][j].searched:
                    vMap[i][j] = '{x}'
                elif dungeon[i][j].visited and player.hasCompass and dungeon[i][j].searched:
                    vMap[i][j] = '{' + str(len([o.state for o in dungeon[i][j].doors.values() if o.state in [1,2,3]])) +'}'
                elif dungeon[i][j].visited and not player.hasCompass and dungeon[i][j].searched:
                    vMap[i][j] = "{ }"
                elif i == player.position[0] and j == player.position[1] and player.hasCompass:
                    vMap[i][j] = '[x]'
                elif dungeon[i][j].visited and player.hasCompass:
                    vMap[i][j] = '[' + str(len([o.state for o in dungeon[i][j].doors.values() if o.state in [1,2,3]])) +']'
                elif dungeon[i][j].visited and not player.hasCompass:
                    vMap[i][j] = "[ ]"
                elif player.hasMap:
                    vMap[i][j] = '( )'

    for rowidx in range(vMap.shape[0]):
        print(' '.join([str(elem) for elem in vMap[rowidx]]))

dungeonSize = max(5, int(input("Size? ")))
dungeon, dunmap, bossRoom = buildDungeon(dungeonSize)
MAX_HEALTH = 10
startingWeapon = Treasure("A",1)
player = Player(MAX_HEALTH, 1, 100, [dungeonSize - 1, int((dungeonSize - 1) / 2)], [startingWeapon])
useItem(startingWeapon)
action = 0

while action != "Q":

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
        inventory()
    elif action == "H":
        dungeon[player.position[0], player.position[1]].hazard.disarm()

    elif action == "HELP":
        print("NSEW: Move")
        print("FX: Fight X")
        print("P: Perception")
        print("R: Rest")
        print("T: Grab Treasure")
        print("I: Inventory")