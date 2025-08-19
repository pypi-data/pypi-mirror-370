#!/usr/bin/env python3
import json
import os
from datetime import datetime
from typing import Dict, List, Any
class GameState:
    def __init__(self):
        self.player = {
            "name": "Player",
            "level": 1,
            "experience": 0,
            "health": 100,
            "mana": 50,
            "stats": {
                "strength": 10,
                "dexterity": 10,
                "intelligence": 10,
                "constitution": 10
            },
            "position": {
                "x": 0,
                "y": 0,
                "z": 0,
                "map": "starting_area"
            },
            "inventory": {
                "items": [
                    {"name": "Health Potion", "quantity": 3, "type": "consumable"},
                    {"name": "Iron Sword", "quantity": 1, "type": "weapon", "damage": 15},
                    {"name": "Leather Armor", "quantity": 1, "type": "armor", "defense": 10}
                ],
                "gold": 100,
                "max_slots": 20
            }
        }
        self.game_progress = {
            "current_quest": "Find the Ancient Relic",
            "completed_quests": ["Tutorial", "First Steps"],
            "discovered_locations": ["Village", "Forest"],
            "unlocked_skills": ["Basic Attack", "Heal"]
        }
        self.settings = {
            "difficulty": "normal",
            "sound_enabled": True,
            "auto_save": True
        }
        self.timestamp = datetime.now().isoformat()
    def to_dict(self) -> Dict[str, Any]:
        return {
            "player": self.player,
            "game_progress": self.game_progress,
            "settings": self.settings,
            "timestamp": self.timestamp,
            "version": "1.0"
        }
    def from_dict(self, data: Dict[str, Any]):
        self.player = data.get("player", {})
        self.game_progress = data.get("game_progress", {})
        self.settings = data.get("settings", {})
        self.timestamp = data.get("timestamp", datetime.now().isoformat())
    def save_to_file(self, filename: str = "savegame.json"):
        self.timestamp = datetime.now().isoformat()
        save_data = self.to_dict()
        
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"Game saved to {filename} at {self.timestamp}")
    def load_from_file(self, filename: str = "savegame.json"):
        if not os.path.exists(filename):
            print(f"Save file {filename} not found!")
            return False
        
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.from_dict(save_data)
            print(f"Game loaded from {filename}")
            print(f"Save timestamp: {self.timestamp}")
            return True
        except json.JSONDecodeError as e:
            print(f"Error loading save file: {e}")
            return False
    def display_status(self):
        print("\n=== GAME STATE ===")
        print(f"Player: {self.player['name']} (Level {self.player['level']})")
        print(f"Health: {self.player['health']}, Mana: {self.player['mana']}")
        print(f"Position: ({self.player['position']['x']}, {self.player['position']['y']}) in {self.player['position']['map']}")
        print(f"Gold: {self.player['inventory']['gold']}")
        print(f"Current Quest: {self.game_progress['current_quest']}")
        print(f"Items in inventory: {len(self.player['inventory']['items'])}")
        for item in self.player['inventory']['items']:
            print(f"  - {item['name']} x{item['quantity']}")
        print(f"Last saved: {self.timestamp}")
