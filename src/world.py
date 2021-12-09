#!/usr/bin/env zsh
from room import Room
from player import Player
import item, monster, updater

def createWorld(player):
    itm01 = item.HealingPotion(20)

    #starting room
    a = Room("A grassy field. Several animals graze placidly. Flowers poke out from the green grass. The sun shines, the sky is blue, but ahead of you, to the north, the dark gate of a crumbling ruin yawns\nTip: Try the command 'inspect instruction manual'")
    itm1 = item.Book("Instruction Manual", "Every year, according to Sacred Tradition, our village sends one human sacrifice to the Evil Necromancer Cultists. This year, you have been unwillingly elected to fill that role! But if you somehow manage to defeat the Necromancer, you can come back home I guess.\n(Type Help for a list of actions)")
    itm1.putInRoom(a)
    for x in range(5):
        monster.Sheep(a)

    #dungeon enterance
    b = Room("The entry-hall of the ruin is dark and reeks of mildew. Rubble from the high ceiling litters the ground.")
    Room.connectRooms(a, "north", b)
    itm3 = item.Book("Water-soiled Journal", "Death closes in on me.... if only I knew how to use the equip and unequip commands to don or doff weapons and armor... or if I knew how to use the unlock command to open a locked door... or if I knew how to use the attack command to attack a monster... or to type 'look' to repeat a room's description... alas, I am doomed")
    itm4 = item.Weapon("Blunt rock", "Be careful with that thing! You could bash someone's head in.", 3, 5)
    itm5 = item.Key("Rusted Key")
    itm3.putInRoom(b)
    itm4.putInRoom(b)
    x = monster.Rat(b, "rat with a key in its mouth")
    x.giveItem(itm5)

    #dungeon corridor
    c = Room("A long and gloomy corridor stretches down into the ruin. It is bisected by a river of slowly-flowing blood!")
    itm6 = item.Door(itm5, "north", c)
    itm6.putInRoom(b)
    monster.Skeleton(c)
    monster.Skeleton(c)

    #blood river shrine
    d = Room("The blood river seems to have its source here, beneath a gigantic statue of a grim-faced bronze king. Ghostly chanting echoes from afar.")
    Room.connectRooms(c, "north", d)
    monster.Cultist(d)

    #converted storeroom
    e = Room("A dingy store-room. Two brown sleeping bags lie on the ground.")
    Room.connectRooms(d, "west", e)
    itm7 = item.Armor("Black leather armor", "Soiled and worn black leather armor", 1.1)
    monster.Ork(e)
    x = monster.Ork(e)
    x.giveItem(itm7)

    #storeroom
    f = Room("A dingy store-room.")
    Room.connectRooms(d, "east", f)
    itm8 = item.Book("Intraoffice Memo", "Why do we make the front enterance guards the weakest fighters? Almost as if we're intentionally allowing any adventurer who enters to get enough xp to level up with the level up command\n-Signed, the Necromancy Union")
    itm9 = item.Container("Large wooden crate", "A large wooden crate", [itm01, itm8])
    itm9.putInRoom(f)

    #west corridor s
    g = Room("A dim corridor")
    Room.connectRooms(e, "west", g)

    #e corridor s
    h = Room("A gloomy corridor")
    Room.connectRooms(f, "east", h)

    #meeting hall
    i = Room("A large, impressive-looking stone chair stands against the north wall, at the head of a long table. A large brass brazier lights the room.")
    Room.connectRooms(g, "south", i)
    IronKey = item.key("Iron Key")
    x = HeadCultist(i)
    x.giveItem(IronKey)

    #Boggle's room
    j = Room("This room bears all the signs of having once been a bedroom, but its furnishings have been smashed and burned into uselessness")
    Room.connectRooms(h, "south", j)
    monster.BigBeast("Boggle", j)

    #w corridor n
    k = Room("A shadowy corridor")
    Room.connectRooms(g, "north", k)

    #infuriating locked chest room
    kl = Room("An empty room except for a chest")
    Room.connectRooms(k, "west", kl)

    #e corridor n-Signed
    l = Room("A dusky corridor")
    Room.connectRooms(h, "north", l)

    #pantry
    lm = Room("A pantry, well-stocked with food. Unfortunately, you aren't hungry. I guess even necromancers have to eat")
    Room.connectRooms(l, "east", lm)
    monster.Rat(lm)
    monster.Rat(lm)
    monster.Rat(lm)

    #library
    m = Room("Shelves line the walls, books stacked neatly on them. Charts of various astrological configurations are tacked to the fine oak-paneled walls. Luxurious black furst cover the floor, and two unlit braziers hang from the ceiling")
    Room.connectRooms(k, "north", m)

    #wizard's laboratory:
    n = Room("A large table is cluttered with magical scrolls. A cauldron smolders over a hearth. A large purple wizard hat sits on a chair.")
    Room.connectRooms(l, "north", n)

    #barracks
    o = Room("An open chamber with many bunk beds, lined up in rows")
    Room.connectRooms(m, "east", o)
    Room.connectRooms(n, "west", o)

    #priest's bedroom
    p = Room("A thick carpet covers the stone floor in this room. A bed is canopied by silken curtains.")
    Room.connectRooms(o, "north", p)

    #commemoration hall
    q = Room("A high and solemn hall. Four tapestries adorn the walls. Two depict a grey star on a black background. The other two show scenes of black-robed priests plunging corpses into a huge undead cauldron, after which the corpses walk away. In the center of the room is another huge bronze statue with an iron crown.")
    Room.connectRooms(k, "east", q)
    Room.connectRooms(l, "west", q)

    #hidden spiral staircase
    r = Room("A winding spiral staircase goes down. Beside it is a very steep ramp. The necromancer's dungeon is ADA-compliant")
    qdoor = item.Door(IronKey, "north", r)
    qdoor.putInRoom(q)

    #morgue
    s = Room("This room is filled with crude wooden coffins. It reeks of carrion.")
    Room.connectRooms(r, "east", s)

    #wine cellar
    sr = Room("Mead and wine barrels line the walls of this room.")
    Room.connectRooms(s, "north", sr)

    #prison block
    t = Room("A rusted and disused prison block")
    Room.connectRooms(s, "east", t)
    monster.BigBeast("Hulking Ogre", t)

    #ghost room
    u = Room("A dusty room full of old furniture. It smells of age and mildew.")
    Room.connectRooms(sr, "east", u)
    Room.connectRooms(t, "north", u)
    monster.Ghost(u)

    #preperation room
    v = Room("A large stone slab sits in the center of this room. It is stained with dried blood")
    Room.connectRooms(u, "north", v)

    #alchemist's laboratory
    w = Room("This room looks like a small laboratory. It smells of formaldehyde. A wide table is cluttered with bubbling potions")
    Room.connectRooms(v, "west", w)
    mp1 = item.HealingPotion(70, "Mysterious Potion", "A mysterious swirling vial of potion")
    mp2 = item.Poison(70, "Mysterious Potion", "A mysterious swirling vial of potion")
    mp3 = item.Antidote("Mysterious Potion", "A mysterious swirling vial of potion")
    mp4 = item.Water("Mysterious Potion", "A mysterious swirling vial of potion")
    mp5 = item.Regeneration((70, "Mysterious Potion", "A mysterious swirling vial of potion")
    mp1.putInRoom(w)
    mp2.putInRoom(w)
    mp3.putInRoom(w)
    mp4.putInRoom(w)
    mp5.putInRoom(w)


    #alchemist's bedroom
    x = Room("A simple bedroom. A dirty shovel leans against the wall.")
    Room.connectRooms(v, "east", x)
    AncientKey = item.Key("Ancient Key")
    AncientKey.putInRoom(x)

    #Barrow1
    y = Room("A circular barrow. Along the walls are niches inhabited by ancient corpses.\nA sign stuck in the ground says 'Welcome to the barrow!!' with a smiley face crudely drawn")
    Room.connectRooms(v, "north", y)
    vdoor = item.Door(AncientKey, "north", y)
    vdoor.putInRoom(v)

    #Barrow2
    yy = Room("A circular barrow. Along the walls are niches inhabited by ancient corpses.")
    Room.connectRooms(y, "north", yy)

    yyy = Room("A circular barrow. Along the walls are niches inhabited by ancient corpses.")
    Room.connectRooms(y, "west", yy)

    yyyy = Room("A circular barrow. Along the walls are niches inhabited by ancient corpses.")
    Room.connectRooms(yyy, "west", yyyy)
    Room.connectRooms(yyy, "north", yyyy)

    y5 = Room("A circular barrow. Along the walls are niches inhabited by ancient corpses.")
    Room.connectRooms(y, "west", y5)
    Room.connectRooms(y5, "north", y5)

    y6 = Room("A circular barrow. Along the walls are niches inhabited by ancient corpses.")
    Room.connectRooms(yyyy, "north", y6)

    y7 = Room("A circular barrow. Along the walls are niches inhabited by ancient corpses.")
    Room.connectRooms(yy, "north", y7)
    Room.connectRooms(yy, "east", y7)
    Room.connectRooms(yy, "west", y7) #I don't care about geometry



    #BARROW OF THE LICH KING!!!!!!!
    z = Room("A grand hall, lit only by the sickly green bubbling of a huge cauldron, ornately inscribed with skulls. The ceiling is lost in darkness. At the far end of the hall stands a massive stone-hewn throne. A sign on top of it says 'Throne of the Lich King'")
    Room.connectRooms(z, "north", y6)

    player.location = a
    updater.allocateLoot()
