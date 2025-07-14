import random
import pygame
from game_constants import *
from board import GameBoard

class GameState:
    def __init__(self):
        self.board = GameBoard()
        self.players = []
        self.current_player_idx = 0
        self.dice_values = (0, 0)
        self.moves_left = 0
        self.game_log = []
        self.solution = None
        self.game_phase = "start_menu"  
        self.num_players = 3  
        self.selected_characters = []
        self.has_rolled = False  # Track if current player has rolled dice
        
        # Card tracking
        self.all_cards = []  # All cards in the game
        self.solution_cards = []  # Cards in the solution envelope
        self.player_showing_card = None  # Index of player showing a card
        self.card_being_shown = None  # Card currently being shown
        
        # UI state
        self.showing_suggestion_ui = False
        self.showing_accusation_ui = False
        self.showing_card_ui = False
        self.showing_notification_ui = False  # New flag for notification popups
        self.notification_message = None      # Message to show in notification popup
        self.selected_suggestion_character = None
        self.selected_suggestion_weapon = None
        self.selected_accusation_character = None
        self.selected_accusation_weapon = None
        self.selected_accusation_room = None
        self.current_suggestion = None  
    
    def initialize_game(self):
        self.players = []
        for i in range(self.num_players):
            char_idx = self.selected_characters[i]
            character = CHARACTERS[char_idx]
            self.players.append({
                "name": character["name"],
                "color": character["color"],
                "position": character["start_pos"],
                "active": True,
                "cards": []
            })
        
        self.all_cards = []
        
        for character in CHARACTERS:
            self.all_cards.append({
                "type": CARD_TYPES["CHARACTER"],
                "name": character["name"]
            })
        
        for weapon in WEAPONS:
            self.all_cards.append({
                "type": CARD_TYPES["WEAPON"],
                "name": weapon
            })
        
        for room in ROOMS:
            self.all_cards.append({
                "type": CARD_TYPES["ROOM"],
                "name": room["name"]
            })
        
        # Select the solution (murderer, weapon, room)
        character_cards = [c for c in self.all_cards if c["type"] == CARD_TYPES["CHARACTER"]]
        weapon_cards = [c for c in self.all_cards if c["type"] == CARD_TYPES["WEAPON"]]
        room_cards = [c for c in self.all_cards if c["type"] == CARD_TYPES["ROOM"]]
        
        murderer_card = random.choice(character_cards)
        weapon_card = random.choice(weapon_cards)
        room_card = random.choice(room_cards)
        
        self.solution_cards = [murderer_card, weapon_card, room_card]
        
        self.solution = {
            "murderer": murderer_card["name"],
            "weapon": weapon_card["name"],
            "room": room_card["name"]
        }
        
        print(f"Solution (for testing): {self.solution}")
        
        remaining_cards = [card for card in self.all_cards if card not in self.solution_cards]
        
        random.shuffle(remaining_cards)
        
        # Deal exactly 3 cards to each player
        for i, player in enumerate(self.players):
            start_idx = i * CARDS_PER_PLAYER
            end_idx = start_idx + CARDS_PER_PLAYER
            
            # Handle case where we might run out of cards
            if end_idx <= len(remaining_cards):
                player["cards"] = remaining_cards[start_idx:end_idx]
            else:
                # If we're at the end, give whatever cards are left
                player["cards"] = remaining_cards[start_idx:]
            
            # Add a log entry for each player's cards 
            card_names = [card["name"] for card in player["cards"]]
            print(f"{player['name']} has cards: {', '.join(card_names)}")
        
        # Initialize game state
        self.current_player_idx = 0
        self.moves_left = 0
        self.has_rolled = False
        self.game_log = []
        self.add_to_log(f"Game started with {self.num_players} players.")
        self.add_to_log(f"Each player has been dealt {CARDS_PER_PLAYER} cards.")
        self.add_to_log(f"It's {self.players[0]['name']}'s turn. Roll the dice.")
        
        self.game_phase = "playing"
    
    def add_to_log(self, message):
        self.game_log.append(message)
        if len(self.game_log) > MAX_LOG_ENTRIES:
            # Keep the log size within limits but don't remove entries
            # This allows scrolling through all entries
            pass
    
    def roll_dice(self):
        # Can only roll once per turn and if no moves left
        if self.has_rolled or self.moves_left > 0:
            return False
        
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        self.dice_values = (die1, die2)
        self.moves_left = die1 + die2
        self.has_rolled = True
        
        player_name = self.players[self.current_player_idx]["name"]
        self.add_to_log(f"{player_name} rolled {die1 + die2} ({die1}, {die2}).")
        
        return True
    
    def get_valid_moves(self):
        # Get valid moves for current player
        if self.moves_left <= 0:
            return []
        
        player = self.players[self.current_player_idx]
        x, y = player["position"]
        
        return self.board.get_valid_moves(x, y)
    
    def move_player(self, target_x, target_y):
        if self.moves_left <= 0:
            return False,
        
        player = self.players[self.current_player_idx]
        x, y = player["position"]
        
        # Check if move is valid
        valid_moves = self.get_valid_moves()
        if (target_x, target_y) not in valid_moves:
            return False, "Invalid move."
        
        # Update player position
        player["position"] = (target_x, target_y)
        self.moves_left -= 1
        
        # Check if player moved to a door
        is_door, room_idx = self.board.is_door(target_x, target_y)
        if is_door:
            room_name = ROOMS[room_idx]["name"]
            self.add_to_log(f"{player['name']} is at a door to {room_name}.")
            
            # Automatically move to room center
            room_center = self.board.room_centers[room_idx]
            player["position"] = room_center
            self.add_to_log(f"{player['name']} moved to the center of {room_name}.")
            
            return True, f"In {room_name}. Press 'S' to make a suggestion or move to a door to exit."
        
        # Check if player moved to room center
        for i, center in enumerate(self.board.room_centers):
            if (target_x, target_y) == center:
                room_name = ROOMS[i]["name"]
                self.add_to_log(f"{player['name']} is in the center of {room_name}.")
                return True, f"In {room_name}. Press 'S' to make a suggestion or move to a door to exit."
        
        return True, f"Moved to ({target_x}, {target_y}). Moves left: {self.moves_left}"
    
    def end_turn(self):
        # End the current player's turn and move to the next player
        self.moves_left = 0
        self.has_rolled = False
        
        # Find next active player
        next_idx = (self.current_player_idx + 1) % len(self.players)
        while not self.players[next_idx]["active"] and next_idx != self.current_player_idx:
            next_idx = (next_idx + 1) % len(self.players)
        
        if next_idx == self.current_player_idx and not self.players[next_idx]["active"]:
            self.game_phase = "game_over"
            self.add_to_log("Game over! All players have been eliminated.")
            return
        
        # Update current player
        self.current_player_idx = next_idx
        player_name = self.players[self.current_player_idx]["name"]
        self.add_to_log(f"It's {player_name}'s turn. Roll the dice.")
    
    def make_suggestion(self, character_name, weapon_name):
        # Make a suggestion about the murder
        player = self.players[self.current_player_idx]
        x, y = player["position"]
        
        # Check if player is in a room
        room_idx = self.board.get_room_at(x, y)
        if room_idx is None:
            # Check if at a door
            is_door, door_room_idx = self.board.is_door(x, y)
            if is_door:
                room_idx = door_room_idx
            else:
                return False, "You must be in a room or at a door to make a suggestion."
        
        room_name = ROOMS[room_idx]["name"]
        
        # Store the current suggestion
        self.current_suggestion = {
            "character": character_name,
            "weapon": weapon_name,
            "room": room_name
        }
        
        # Log the suggestion
        suggestion_text = f"{player['name']} suggests: {character_name} in the {room_name} with the {weapon_name}."
        self.add_to_log(suggestion_text)
        
        # Check if any player can disprove the suggestion
        for i, other_player in enumerate(self.players):
            if i == self.current_player_idx or not other_player["active"]:
                continue
            
            # Check if player has any of the suggested cards
            has_matching_cards = []
            for card in other_player["cards"]:
                if (card["type"] == CARD_TYPES["CHARACTER"] and card["name"] == character_name) or \
                   (card["type"] == CARD_TYPES["WEAPON"] and card["name"] == weapon_name) or \
                   (card["type"] == CARD_TYPES["ROOM"] and card["name"] == room_name):
                    has_matching_cards.append(card)
            
            if has_matching_cards:
                # This player can disprove
                self.player_showing_card = i
                
                # If only one card matches, show that one
                if len(has_matching_cards) == 1:
                    self.card_being_shown = has_matching_cards[0]
                else:
                    # If multiple cards match, randomly select one to show
                    self.card_being_shown = random.choice(has_matching_cards)
                
                self.showing_card_ui = True
                self.add_to_log(f"{other_player['name']} can disprove the suggestion.")
                
                card_type_names = {
                    CARD_TYPES["CHARACTER"]: "Character",
                    CARD_TYPES["WEAPON"]: "Weapon",
                    CARD_TYPES["ROOM"]: "Room"
                }
                
                card_type = card_type_names[self.card_being_shown["type"]]
                self.add_to_log(f"{other_player['name']} shows {player['name']} a {card_type} card.")
                
                # Create a card reveal message that only the suggesting player can see
                return True, f"{other_player['name']} shows you the {self.card_being_shown['name']} card, disproving your suggestion."
        
        # No one could disprove - show a notification popup
        self.add_to_log("No one could disprove the suggestion.")
        self.showing_notification_ui = True
        self.notification_message = "No one could disprove your suggestion. This card might be part of the solution!"
        return True, "No one could disprove your suggestion."
    
    def make_accusation(self, character_name, weapon_name, room_idx):
        """Make an accusation about the murder"""
        player = self.players[self.current_player_idx]
        room_name = ROOMS[room_idx]["name"]
        
        # Log the accusation
        accusation_text = f"{player['name']} accuses: {character_name} in the {room_name} with the {weapon_name}."
        self.add_to_log(accusation_text)
        
        # Check if accusation is correct
        is_correct = (character_name == self.solution["murderer"] and 
                      weapon_name == self.solution["weapon"] and 
                      room_name == self.solution["room"])
        
        if is_correct:
            self.add_to_log(f"{player['name']} wins! The accusation was correct.")
            self.game_phase = "game_over"
            return True, accusation_text
        else:
            self.add_to_log(f"{player['name']} made an incorrect accusation and is eliminated.")
            
            # Mark player as inactive
            player["active"] = False
            
            # Check if game is over (all players eliminated)
            active_players = [p for p in self.players if p["active"]]
            if not active_players:
                self.add_to_log("Game over! All players have been eliminated.")
                self.game_phase = "game_over"
            
            return False, accusation_text
    
    def acknowledge_card(self):
        """Player acknowledges seeing the card shown to them"""
        if self.showing_card_ui and self.player_showing_card is not None and self.card_being_shown is not None:
            showing_player = self.players[self.player_showing_card]["name"]
            current_player = self.players[self.current_player_idx]["name"]
            
            # Get the card type for better messaging
            card_type_names = {
                CARD_TYPES["CHARACTER"]: "Character",
                CARD_TYPES["WEAPON"]: "Weapon",
                CARD_TYPES["ROOM"]: "Room"
            }
            card_type = card_type_names[self.card_being_shown["type"]]
            
            # Log that the player has seen the card and can now eliminate it
            self.add_to_log(f"{current_player} acknowledges seeing the {card_type} card {self.card_being_shown['name']} from {showing_player}.")
            
            # Reset card showing state
            self.showing_card_ui = False
            self.player_showing_card = None
            self.card_being_shown = None
            return True
        return False
    
    def acknowledge_notification(self):
        """Player acknowledges a notification popup"""
        if self.showing_notification_ui:
            self.showing_notification_ui = False
            self.notification_message = None
            return True
        return False