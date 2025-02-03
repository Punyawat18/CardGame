import pygame
import random
import os
import sys
import json
import atexit

try:
    logging_path = os.path.join(os.path.dirname(__file__), "GameHistory")
except NameError:
    os.mkdir(f'{os.path.dirname(__file__)}/GameHistory')
    logging_path = os.path.join(os.path.dirname(__file__))

round_count = None
try:
    with open(f'{logging_path}/GameCount.txt', 'r+') as f:
        round_count = int(f.read())
        round_count += 1
        f.seek(0)
        f.write(str(round_count))
except FileNotFoundError:
    with open(f'{logging_path}/GameCount.txt', 'w') as f:
        round_count = 1
        f.write(str(round_count))

#create log file
with open(f'{logging_path}/{round_count}.json', 'w') as f:
    pass

attack_card_name = ["Charge", "Punch", "Strike", "Slash", "Stab", "Fireball", "Lightning Bolt", "Ice Shard", "Wind Blade", "Earthquake"]
defense_card_name = ["Block", "Dodge", "Parry", "Deflect", "Absorb", "Reflect", "Counter", "Barrier", "Guardian", "Shield"]
heal_card_name = ["Heal", "Regenerate", "Recover", "Revive", "Renew", "Cure", "Potion", "Elixir", "Salve", "Bandage"]
turn_count = 0


class Card:
    def __init__(self, name, cost, type, point_value, card_id):
        self.name = name
        self.cost = cost
        self.type = type
        self.point_value = point_value
        self.card_id = card_id

    def __str__(self):
        return f'{self.card_id}: {self.name}, Cost: {self.cost}, Type: {self.type}, Value: {self.point_value}'
    
    def show(self):
        return {
            "name": self.name,
            "cost": self.cost,
            "type": self.type,
            "point_value": self.point_value,
            "card_id": self.card_id
        }

class Player:
    def __init__(self, name, deck):
        self.name = name
        self.health = 30
        self.defense = 0
        self.deck = deck
        self.hand = []
        self.used = []
        self.discarded = []
        self.energy = 0

    def draw(self):
        while len(self.hand) < 5:
            card = random.choice(self.deck)
            self.hand.append(card)
            self.deck.remove(card)
            

    def discard(self, card_id):
        discard_success = False
        for card in self.hand:
            if card.card_id == card_id:
                self.hand.remove(card)
                self.discarded.append(card)
                discard_success = True

        for card in self.used:
            if card.card_id == card_id:
                self.used.remove(card)
                self.discarded.append(card)
                discard_success = True
        
        if discard_success:
            for restore_card in self.used:
                self.deck.append(restore_card)
            self.used = []


    def play(self, card_id):
        for card in self.hand:
            if card.card_id == card_id:
                self.hand.remove(card)
                self.used.append(card)
                

    def show_hand(self):
        for card in self.hand:
            print(card)

    def show_used(self):
        for card in self.used:
            print(card)

    def healing(self, card_id):
        for card in self.hand:
            if card.card_id == card_id:
                self.health += card.point_value
                self.hand.remove(card)
                self.used.append(card)

#need change
    def take_damage(self, damage_taken):
        if self.defense > damage_taken:
            self.defense -= damage_taken
        elif self.defense > 0:
            damage_taken -= self.defense
            self.defense = 0
            self.health -= damage_taken
        else:
            self.health -= damage_taken

    def defend(self, card_id):
        for card in self.hand:
            if card.card_id == card_id:
                self.defense += card.point_value
                self.hand.remove(card)
                self.used.append(card)

    def __str__(self):
        return f'{self.name}, HP: {self.health}, DEF: {self.defense}, Energy: {self.energy}'
    
def Create_deck():
    deck = []
    card_num = 1
    for move in attack_card_name:
        deck.append(Card(move, random.randint(1, 3), "attack", random.randint(1, 10), card_num))
        card_num += 1
    for move in defense_card_name:
        deck.append(Card(move, random.randint(1, 3), "defense", random.randint(1, 10), card_num))
        card_num += 1
    for move in heal_card_name:
        deck.append(Card(move, random.randint(1, 3), "heal", random.randint(1, 10), card_num))
        card_num += 1
    return deck

"""
def graphics():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Card Game")
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
"""
## to be changed in move detect way
def Turn(player, enemy):
    print(f"{player.name}'s turn")
    player.energy = 5
    player.draw()

    action = None
    while True:

        logging(player, enemy)
        action = int(input("Choose an action: 1(Play), 2(Discard), 3(End Turn), 4(Check Status of Both Player)\n"))
        if action == 1:
            action_status = False
            player.show_hand()
            card_id = int(input("Enter the card number to use it : "))
            for card in player.hand:
                if card.card_id == card_id:
                    if card.cost <= player.energy:
                        player.energy -= card.cost
                        if card.type == "attack":
                            enemy.take_damage(card.point_value)
                        elif card.type == "defense":
                            player.defend(card.card_id)
                        elif card.type == "heal":
                            player.healing(card.card_id)
                        print("Card Played")
                        player.play(card.card_id)
                        action_status = True
                        break
                    else:
                        print("Not enough energy")
                        action_status = True
                        break
            if action_status:
                continue
            print("Card not exist or not in hand")
        elif action == 2:
            print("----------Current Hand----------")
            player.show_hand()
            print("------------Card Used-----------")
            player.show_used()
            card_id = int(input("Please Choose a Card to discard from above: "))
            player.discard(card_id)
        elif action == 4:
            print(f'You({player})')
            print(f'Enemy({enemy})')
        elif action == 3:
            break
        else:
            print("Invalid Action Please Choose Again")
    print("End of turn\n")
    print(f'You({player})')
    print(f'Enemy({enemy})')

def enemy_turn(player, enemy):
    print(f"{enemy.name}'s turn")
    enemy.energy = 5
    enemy.draw()
    end_using = False
    logging(player, enemy)
    while enemy.energy > 0:
        not_played = 0
        for card in enemy.hand:
            if card.cost <= enemy.energy:
                if card.type == "attack":
                    player.take_damage(card.point_value)
                elif card.type == "defense":
                    enemy.defend(card.card_id)
                elif card.type == "heal":
                    enemy.healing(card.card_id)
                print(f"{enemy.name} played {card.name}")
                enemy.play(card.card_id)
                break
            else:
                not_played += 1
                if not_played == len(enemy.hand):
                    end_using = True
                    break
        if end_using:
            break

        if len(enemy.deck) <= 5:
            enemy.discard(random.choice(enemy.used).card_id)
        
        #end turn
        print("End of turn\n")
        break

def logging(player, enemy):
    player_hand = {}
    for card in player.hand:
        player_hand.update(card.show())
    player_used = {}
    for card in player.used:
        player_used.update(card.show())
    player_discarded = {}
    for card in player.discarded:
        player_discarded.update(card.show())

    player_dict = {
        "name": player.name,
        "health": player.health,
        "defense": player.defense,
        "energy": player.energy,
        "hand": player_hand,
        "used": player_used,
        "discarded": player_discarded
    }
    with open(f'{logging_path}/{round_count}.json', 'a') as f:
        f.write(json.dumps(player_dict, indent=4))


def main():
    Create_deck()
    You = Player("Hoshisora", Create_deck())
    Enemy = Player("Kurayami", Create_deck())
    while True:
        Turn(You, Enemy)
        enemy_turn(You, Enemy)
        if You.health <= 0:
            print("You lose")
            break
        elif Enemy.health <= 0:
            print("You win")
            break

if __name__ == "__main__":
    main()

   # with open(f'{logging_path}/log.txt', 'w') as f: