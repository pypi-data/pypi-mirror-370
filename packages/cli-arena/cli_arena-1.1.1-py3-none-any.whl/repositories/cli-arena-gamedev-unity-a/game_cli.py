#!/usr/bin/env python3
import sys
import argparse
from game_state import GameState
def main():
    parser = argparse.ArgumentParser(description='Game State Manager CLI')
    parser.add_argument('action', choices=['save', 'load', 'status', 'new'], help='Action to perform')
    parser.add_argument('--file', '-f', default='savegame.json', help='Save file name (default: savegame.json)')
    
    args = parser.parse_args()
    
    game = GameState()
    
    if args.action == 'save':
        game.save_to_file(args.file)
        
    elif args.action == 'load':
        if game.load_from_file(args.file):
            game.display_status()
        
    elif args.action == 'status':
        if game.load_from_file(args.file):
            game.display_status()
        else:
            print("No save file found. Showing default game state:")
            game.display_status()
            
    elif args.action == 'new':
        print("Creating new game state:")
        game.display_status()
        game.save_to_file(args.file)
if __name__ == '__main__':
    main()
