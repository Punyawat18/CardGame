import json
import os

path = os.path.join(os.path.dirname(__file__), "GameHistory")
with open(f'{path}/12.json', 'r') as f:
    data = json.load(f)
    print(data['Game_Data'][2])