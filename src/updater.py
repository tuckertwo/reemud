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
    for i in range(5):
        loot.append(item.Weapon("Sword", "A nondescript metal sword.", 6, 3))
        loot.append(item.HealingPotion(15))
        loot.append(item.Poison(15))
        loot.append(item.Regeneration(15))
        loot.append(item.Water(15))
        loot.append(item.DamageScroll(10))
        loot.append(item.PoisonScroll(3))
        loot.append(item.Fireball(8))
    loot.append(item.Weapon("Epic sword", "This sword is so cool, its surprising its wielded by an ordinary skeleton", 100, 3))
    while len(loot) > 0:
        x = random.randrange(len(loot))
        y = random.choice(updates)
        if not y.name == "Player":
            y.giveItem(loot[x])
            loot.pop(x)
    