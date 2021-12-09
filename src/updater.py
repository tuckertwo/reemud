import random
import item
updates = []

def updateAll():
    for u in updates:
        u.update()

def register(thing):
    updates.append(thing)

def deregister(thing):
    updates.remove(thing)
    
def allocateLoot():
    loot = []
    for i in range(6):
        loot.append(item.Weapon("Sword", "A nondescript metal sword.", int(random.random() * 20), 3))
        x = item.Weapon("Sword", "A nondescript metal sword.", int(random.random() * 20), 3)
        y = item.Poison(int(random.random() * 15))
        y.applyTo(x, False)
        loot.append(x)
        loot.append(item.HealingPotion(int(random.random() * 15)))
        loot.append(item.Poison(int(random.random() * 15)))
        loot.append(item.Regeneration(int(random.random() * 15)))
        loot.append(item.Antidote())
        loot.append(item.Water())
        loot.append(item.DamageScroll(int(random.random() * 20)))
        loot.append(item.PoisonScroll(int(random.random() * 15)))
        loot.append(item.Fireball(int(random.random() * 20)))
    loot.append(item.Weapon("Epic sword", "This sword is so cool, its surprising its wielded by an ordinary skeleton", 100, 3))
    while len(loot) > 0:
        x = random.randrange(len(loot))
        y = random.choice(updates)
        if not y.name == "Player":
            y.giveItem(loot[x])
            loot.pop(x)
    