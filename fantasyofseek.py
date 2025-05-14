import random
import sys
from time import sleep

class Player:
    def __init__(self, job, name):
        self.name = name
        self.job = job
        self.level = 1
        self.exp = 0
        self.hp = 50
        self.max_hp = 50
        self.mp = 15 if job == "Mage" else 0
        self.max_mp = 15 if job == "Mage" else 0
        self.strength = 8 if job == "Warrior" else 4
        self.defense = 8 if job == "Warrior" else 4
        self.magic = 10 if job == "Mage" else 0
        self.inventory = {"Potion": 3, "Ether": 1}
        self.weapon = "Wooden Sword" if job == "Warrior" else "Staff"
        self.armor = "Leather Armor"

class Enemy:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.hp = 10 + (level * 5)
        self.max_hp = 10 + (level * 5)
        self.strength = 2 + level
        self.defense = 2 + level
        self.exp = 5 * level
        self.gil = 3 * level

class Game:
    def __init__(self):
        self.party = []
        self.current_zone = "Pravoka"
        self.zones = {
            "Pravoka": {"enemies": ["Goblin", "Wolf"], "level": 1},
            "Marsh Cave": {"enemies": ["Sahag", "Crawler"], "level": 3},
            "Volcano": {"enemies": ["Bomb", "Fire Elemental"], "level": 5},
            "Flying Fortress": {"enemies": ["Iron Giant", "Warmech"], "level": 10}
        }
    
    def start_game(self):
        print("Final Fantasy Text Adventure")
        self.create_party()
        self.game_loop()
    
    def create_party(self):
        jobs = ["Warrior", "Thief", "Monk", "Mage"]
        for i in range(4):
            name = input(f"Name for {jobs[i]} {i+1}: ")
            self.party.append(Player(jobs[i], name))
    
    def game_loop(self):
        while True:
            print(f"\nCurrent Zone: {self.current_zone}")
            action = input("[1] Explore [2] Party [3] Inventory [4] Travel [5] Quit: ")
            
            if action == "1":
                self.explore()
            elif action == "2":
                self.show_party_status()
            elif action == "3":
                self.use_item()
            elif action == "4":
                self.travel()
            elif action == "5":
                sys.exit()
            else:
                print("Invalid choice!")
    
    def explore(self):
        if random.random() < 0.6:
            self.random_battle()
        else:
            print("You find nothing of interest...")
    
    def random_battle(self):
        zone_level = self.zones[self.current_zone]["level"]
        enemy_type = random.choice(self.zones[self.current_zone]["enemies"])
        enemy = Enemy(enemy_type, zone_level + random.randint(-1,1))
        print(f"\nA wild {enemy.name} appears!")
        self.battle_loop(enemy)
    
    def battle_loop(self, enemy):
        while enemy.hp > 0 and any(member.hp > 0 for member in self.party):
            print(f"\n{enemy.name} HP: {enemy.hp}/{enemy.max_hp}")
            for i, member in enumerate(self.party):
                if member.hp > 0:
                    print(f"{i+1}. {member.name} ({member.job}) HP: {member.hp}/{member.max_hp} MP: {member.mp}/{member.max_mp}")
            
            for member in self.party:
                if member.hp <= 0:
                    continue
                
                print(f"\n{member.name}'s turn:")
                action = input("[1] Attack [2] Magic [3] Item [4] Flee: ")
                
                if action == "1":
                    dmg = max(1, member.strength + random.randint(0, 3) - enemy.defense)
                    enemy.hp -= dmg
                    print(f"{member.name} deals {dmg} damage!")
                elif action == "2" and member.job == "Mage":
                    if member.mp >= 2:
                        dmg = member.magic + random.randint(0, 5)
                        enemy.hp -= dmg
                        member.mp -= 2
                        print(f"{member.name} casts Fire for {dmg} damage!")
                    else:
                        print("Not enough MP!")
                elif action == "3":
                    item = input("Choose item: " + ", ".join(member.inventory.keys()) + ": ")
                    if item in member.inventory and member.inventory[item] > 0:
                        if item == "Potion":
                            member.hp = min(member.max_hp, member.hp + 30)
                            print(f"{member.name} recovered 30 HP!")
                            member.inventory[item] -= 1
                elif action == "4":
                    if random.random() < 0.5:
                        print("Fled successfully!")
                        return
                    else:
                        print("Couldn't escape!")
                
                if enemy.hp <= 0:
                    print(f"{enemy.name} defeated!")
                    self.gain_rewards(enemy)
                    return
            
            # Enemy attack
            alive_members = [m for m in self.party if m.hp > 0]
            target = random.choice(alive_members)
            dmg = max(1, enemy.strength - target.defense)
            target.hp -= dmg
            print(f"{enemy.name} attacks {target.name} for {dmg} damage!")
            
            if all(member.hp <= 0 for member in self.party):
                print("Game Over!")
                sys.exit()
    
    def gain_rewards(self, enemy):
        exp = enemy.exp
        gil = enemy.gil
        print(f"Victory! Gained {exp} EXP and {gil} GIL!")
        
        for member in self.party:
            if member.hp > 0:
                member.exp += exp
                if member.exp >= member.level * 100:
                    self.level_up(member)
    
    def level_up(self, member):
        member.level += 1
        member.exp = 0
        member.max_hp += 10
        member.hp = member.max_hp
        if member.job == "Mage":
            member.max_mp += 5
            member.mp = member.max_mp
        member.strength += 2 if member.job in ["Warrior", "Monk"] else 1
        member.defense += 2 if member.job in ["Warrior"] else 1
        print(f"{member.name} reached level {member.level}!")
    
    def show_party_status(self):
        for member in self.party:
            print(f"{member.name} ({member.job}) Lv{member.level}")
            print(f"HP: {member.hp}/{member.max_hp} MP: {member.mp}/{member.max_mp}")
            print(f"STR: {member.strength} DEF: {member.defense}")
            print(f"EXP: {member.exp}/{member.level * 100}")
            print()
    
    def use_item(self):
        member = self.select_member()
        item = input("Choose item: " + ", ".join(member.inventory.keys()) + ": ")
        if item in member.inventory and member.inventory[item] > 0:
            if item == "Potion":
                member.hp = min(member.max_hp, member.hp + 30)
                print(f"{member.name} recovered 30 HP!")
                member.inventory[item] -= 1
    
    def select_member(self):
        for i, m in enumerate(self.party):
            print(f"{i+1}. {m.name} ({m.job})")
        choice = int(input("Select member: ")) - 1
        return self.party[choice]
    
    def travel(self):
        print("Available zones:")
        for zone in self.zones:
            print(f"- {zone}")
        self.current_zone = input("Choose destination: ")

if __name__ == "__main__":
    game = Game()
    game.start_game()
