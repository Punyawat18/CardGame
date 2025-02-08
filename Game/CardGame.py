import random
import os
import json
import pygame

try:
    logging_path = os.path.join(os.path.dirname(__file__), "GameHistory")
except NameError:
    os.mkdir(f'{os.path.dirname(__file__)}/GameHistory')
    logging_path = os.path.join(os.path.dirname(__file__), "GameHistory")

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
    json.dump({}, f)  # Initialize with an empty dictionary

attack_card_name = ["Charge", "Punch", "Strike", "Slash", "Stab", "Fireball", "Lightning Bolt", "Ice Shard", "Wind Blade", "Earthquake"]
defense_card_name = ["Block", "Dodge", "Parry", "Deflect", "Absorb", "Reflect", "Counter", "Barrier", "Guardian", "Shield"]
heal_card_name = ["Heal", "Regenerate", "Recover", "Revive", "Renew", "Cure", "Potion", "Elixir", "Salve", "Bandage"]
turn_count = 0
move_count = 0
Whose_move = None

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


def restore_game_state(player, enemy, game_number, turn, move):
    with open(f'{logging_path}/{game_number}.json', 'r') as log_file:
        log_data = json.load(log_file)
        ## enumerate turn
        for turn_data in log_data["Game_Data"]:
            ## check if turn is the same
            if turn_data["Turn_Count"] == turn:
                for move_data in turn_data["Turn_Data"]:
                    if move_data["Move_Count"] == move:
                        player.health = move_data["Move_Data"]["player"]["health"]
                        player.defense = move_data["Move_Data"]["player"]["defense"]
                        player.energy = move_data["Move_Data"]["player"]["energy"]
                        player.hand = [Card(card["name"], card["cost"], card["type"], card["point_value"], card["card_id"]) for card in move_data["Move_Data"]["player"]["hand"]]
                        player.used = [Card(card["name"], card["cost"], card["type"], card["point_value"], card["card_id"]) for card in move_data["Move_Data"]["player"]["used"]]
                        player.discarded = [Card(card["name"], card["cost"], card["type"], card["point_value"], card["card_id"]) for card in move_data["Move_Data"]["player"]["discarded"]]

                        enemy.health = move_data["Move_Data"]["enemy"]["health"]
                        enemy.defense = move_data["Move_Data"]["enemy"]["defense"]
                        enemy.energy = move_data["Move_Data"]["enemy"]["energy"]
                        enemy.hand = [Card(card["name"], card["cost"], card["type"], card["point_value"], card["card_id"]) for card in move_data["Move_Data"]["enemy"]["hand"]]
                        enemy.used = [Card(card["name"], card["cost"], card["type"], card["point_value"], card["card_id"]) for card in move_data["Move_Data"]["enemy"]["used"]]
                        enemy.discarded = [Card(card["name"], card["cost"], card["type"], card["point_value"], card["card_id"]) for card in move_data["Move_Data"]["enemy"]["discarded"]]



def show_rewind_options():
    game_files = []
    for file in os.listdir(logging_path):
        if file.endswith(".json"):
            game_files.append(file)
    game_files.sort(key=lambda x: int(x.split('.')[0]))
    if not game_files:
        print("No previous games available for rewind.")
        return None

    print("Available games to rewind:")
    for i, game_file in enumerate(game_files):
        print(f'{i + 1}: {game_file}')

    game_choice = int(input("Choose a game to rewind (number): "))
    if game_choice < 1 or game_choice > len(game_files):
        print("Invalid game choice.")
        return None

    for game_file in game_files:
        if f'{game_choice}.json' == game_file:
            with open(f'{logging_path}/{game_file}', 'r') as f:
                log_data = json.load(f)
                print(f'Game {game_choice} has {log_data["Game_Data"][-1]["Turn_Count"]} turns.')
                turn_choice = int(input(f'Choose a turn to rewind to from 1 to {log_data["Game_Data"][-1]["Turn_Count"]}: '))
                if turn_choice < 1 or turn_choice > log_data["Game_Data"][-1]["Turn_Count"]:
                    print("Invalid turn choice.")
                    return None
                for turn_data in log_data["Game_Data"]:
                    if turn_data["Turn_Count"] == turn_choice:
                        move_choice = int(input(f'Choose a move to rewind to from 0 to {turn_data["Turn_Data"][-1]["Move_Count"]}: '))
                        if move_choice < 0 or move_choice > int(turn_data["Turn_Data"][-1]["Move_Count"]):
                            print("Invalid move choice.")
                            return None
                    return [game_choice, turn_choice, move_choice]

def Turn(player, enemy):
    global turn_count, move_count, Whose_move
    Whose_move = "player"
    turn_count += 1
    move_count = 0
    print(f"{player.name}'s turn")
    player.energy = 5
    player.draw()

    action = None
    while True:
        action = int(input("Choose an action: 1(Play), 2(Discard), 3(End Turn), 4(Check Status of Both Player), 5(Rewind)\n"))
        if action == 1:
            move_count += 1
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
                        logging(player, enemy, turn_count, move_count)
                        break
                    else:
                        print("Not enough energy")
                        break
            else:
                print("Card not exist or not in hand")
        elif action == 2:
            move_count += 1
            print("----------Current Hand----------")
            player.show_hand()
            print("------------Card Used-----------")
            player.show_used()
            card_id = int(input("Please Choose a Card to discard from above: "))
            player.discard(card_id)
            logging(player, enemy, turn_count, move_count)
        elif action == 4:
            print(f'You({player})')
            print(f'Enemy({enemy})')
        elif action == 5:

            rewind_choice = None
            #debugging
            while rewind_choice == None:
                rewind_choice = show_rewind_options()
            game_number, turn, move = rewind_choice
            restore_game_state(player, enemy, game_number, turn, move)
        elif action == 3:
            break
        else:
            print("Invalid Action Please Choose Again")
    print("End of turn\n")
    print(f'You({player})')
    print(f'Enemy({enemy})')

def enemy_turn(player, enemy):
    global turn_count, move_count, Whose_move
    Whose_move = "enemy"
    turn_count += 1
    move_count = 0
    print(f"{enemy.name}'s turn")
    enemy.energy = 5
    enemy.draw()
    end_using = False
    logging(player, enemy, turn_count, move_count)
    while enemy.energy > 0:
        move_count += 1
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
                logging(player, enemy, turn_count, move_count)
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

def logging(player, enemy, turn_count, move_count):
    player_hand = [card.show() for card in player.hand]
    player_used = [card.show() for card in player.used]
    player_discarded = [card.show() for card in player.discarded]

    player_dict = {
        "name": player.name,
        "health": player.health,
        "defense": player.defense,
        "energy": player.energy,
        "hand": player_hand,
        "used": player_used,
        "discarded": player_discarded
    }

    enemy_hand = [card.show() for card in enemy.hand]
    enemy_used = [card.show() for card in enemy.used]
    enemy_discarded = [card.show() for card in enemy.discarded]

    enemy_dict = {
        "name": enemy.name,
        "health": enemy.health,
        "defense": enemy.defense,
        "energy": enemy.energy,
        "hand": enemy_hand,
        "used": enemy_used,
        "discarded": enemy_discarded
    }


    with open(f'{logging_path}/{round_count}.json', 'r+') as f:
        log_data = json.load(f)
        if "Game_Data" not in log_data:
            log_data["Game_Data"] = [{
                "Turn_Count": turn_count,
                "Turn_Data": [{
                    "Move_Count": move_count,
                    "Whose_Move": Whose_move,
                    "Move_Data": {
                        "player": player_dict,
                        "enemy": enemy_dict
                    }
                }]
            }]
        else:
            if turn_count not in [turn_data["Turn_Count"] for turn_data in log_data["Game_Data"]]:
                log_data["Game_Data"].append({
                    "Turn_Count": turn_count,
                    "Turn_Data": [{
                        "Move_Count": move_count,
                        "Whose_Move": Whose_move,
                        "Move_Data": {
                            "player": player_dict,
                            "enemy": enemy_dict
                        }
                    }]
                })
            else:
                if turn_count == log_data["Game_Data"][-1]["Turn_Count"]:
                    log_data["Game_Data"][-1]["Turn_Data"].append({
                        "Move_Count": move_count,
                        "Whose_Move": Whose_move,
                        "Move_Data": {
                            "player": player_dict,
                            "enemy": enemy_dict
                        }})

        f.seek(0)
        json.dump(log_data, f, indent=4)

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