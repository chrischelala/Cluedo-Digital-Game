import pygame
import sys
from game_constants import *
from board import GameBoard
from game_state import GameState
from ui import UI

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cluedo")
    
    # Initialize game components
    game_state = GameState()
    ui = UI()
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    mouse_down = False
    message = None
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    mouse_down = True
                    
                    # Handle scrolling in the game log
                    if game_state.game_phase == "playing":
                        ui.handle_log_scroll(mouse_pos, True, game_state.game_log)
                
                # Handle mouse wheel for scrolling game log
                elif event.button == 4:  # Scroll up
                    if game_state.game_phase == "playing":
                        ui.log_scroll_offset = max(0, ui.log_scroll_offset - 1)
                elif event.button == 5:  # Scroll down
                    if game_state.game_phase == "playing":
                        ui.log_scroll_offset = min(max(0, len(game_state.game_log) - LOG_ENTRIES_PER_PAGE), ui.log_scroll_offset + 1)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and mouse_down:  
                    mouse_click = True
                    mouse_down = False
            
            # Handle keyboard events when in playing mode
            elif event.type == pygame.KEYDOWN:
                if game_state.game_phase == "playing":
                    if event.key == pygame.K_ESCAPE:
                        # Close any open UI
                        game_state.showing_suggestion_ui = False
                        game_state.showing_accusation_ui = False
                        game_state.showing_card_ui = False
                        game_state.showing_notification_ui = False
                    
                    # Scroll the game log
                    elif event.key == pygame.K_UP and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        ui.log_scroll_offset = max(0, ui.log_scroll_offset - 1)
                    elif event.key == pygame.K_DOWN and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        ui.log_scroll_offset = min(max(0, len(game_state.game_log) - LOG_ENTRIES_PER_PAGE), ui.log_scroll_offset + 1)
                    
                    # Skip keyboard handling if a UI is showing
                    elif not (game_state.showing_suggestion_ui or 
                             game_state.showing_accusation_ui or 
                             game_state.showing_card_ui or
                             game_state.showing_notification_ui):
                        # Roll dice
                        if event.key == pygame.K_d:
                            if game_state.roll_dice():
                                message = f"Rolled {game_state.dice_values[0] + game_state.dice_values[1]}. Use arrow keys to move."
                            else:
                                message = "You can only roll dice once per turn."
                        
                        # Movement
                        elif event.key in (pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT):
                            if game_state.moves_left <= 0:
                                message = "No moves left. Roll dice (D) or end turn (Enter)."
                            else:
                                player = game_state.players[game_state.current_player_idx]
                                x, y = player["position"]
                                
                                # Check if player is in a room center
                                in_room_center = False
                                room_idx = None
                                for i, center in enumerate(game_state.board.room_centers):
                                    if (x, y) == center:
                                        in_room_center = True
                                        room_idx = i
                                        break
                                
                                # If in a room center, we need to handle exiting through one of the doors
                                if in_room_center and room_idx is not None:
                                    # Get all doors for this room
                                    doors = game_state.board.room_doors[room_idx]
                                    
                                    # If there are doors to exit through
                                    if doors:
                                        # Determine which door to use based on arrow key
                                        door_index = 0
                                        if len(doors) > 1:
                                            if event.key == pygame.K_UP and len(doors) > 0:
                                                door_index = 0
                                            elif event.key == pygame.K_RIGHT and len(doors) > 1:
                                                door_index = 1
                                            elif event.key == pygame.K_DOWN and len(doors) > 2:
                                                door_index = 2
                                            elif event.key == pygame.K_LEFT and len(doors) > 3:
                                                door_index = 3
                                            door_index = min(door_index, len(doors) - 1)
                                        
                                        # Move to the selected door
                                        door_x, door_y = doors[door_index]
                                        
                                        player["position"] = (door_x, door_y)
                                        game_state.moves_left -= 1
                                        
                                        # Get room name for message
                                        room_name = ROOMS[room_idx]["name"]
                                        game_state.add_to_log(f"{player['name']} exited the {room_name} through a door.")
                                        
                                        # Set a message for the player
                                        message = f"Exited {room_name} through a door. Moves left: {game_state.moves_left}"
                                    else:
                                        message = "No doors available to exit."
                                
                                # If not in a room center, handle normal movement
                                else:
                                    # Standard direction movement
                                    if event.key == pygame.K_UP:
                                        success, msg = game_state.move_player(x, y - 1)
                                    elif event.key == pygame.K_RIGHT:
                                        success, msg = game_state.move_player(x + 1, y)
                                    elif event.key == pygame.K_DOWN:
                                        success, msg = game_state.move_player(x, y + 1)
                                    elif event.key == pygame.K_LEFT:
                                        success, msg = game_state.move_player(x - 1, y)
                                    
                                    if success:
                                        message = msg
                                    else:
                                        message = msg or "Invalid move."
                        
                        # Make suggestion
                        elif event.key == pygame.K_s:
                            player = game_state.players[game_state.current_player_idx]
                            x, y = player["position"]
                            room_idx = game_state.board.get_room_at(x, y)
                            
                            # Check if at a door, get the room
                            if room_idx is None:
                                is_door, door_room_idx = game_state.board.is_door(x, y)
                                if is_door:
                                    room_idx = door_room_idx
                            
                            if room_idx is not None:
                                game_state.showing_suggestion_ui = True
                                game_state.selected_suggestion_character = None
                                game_state.selected_suggestion_weapon = None
                                message = f"Making suggestion in {ROOMS[room_idx]['name']}"
                            else:
                                message = "You must be in a room or at a door to make a suggestion."
                                game_state.add_to_log(message)
                        
                        # Make accusation
                        elif event.key == pygame.K_a:
                            game_state.showing_accusation_ui = True
                            game_state.selected_accusation_character = None
                            game_state.selected_accusation_weapon = None
                            game_state.selected_accusation_room = None
                            message = "Making an accusation"
                        
                        # End turn
                        elif event.key == pygame.K_RETURN:
                            game_state.end_turn()
                            message = f"Turn ended. It's {game_state.players[game_state.current_player_idx]['name']}'s turn."
        
        # Handle UI based on game phase
        if game_state.game_phase == "start_menu":
            # Draw start menu
            player_buttons, start_btn = ui.draw_start_menu(screen, game_state.num_players)
            
            # Check player count buttons
            for i, btn in enumerate(player_buttons):
                btn.check_hover(mouse_pos)
                if mouse_click and btn.check_click(mouse_pos, mouse_click):
                    game_state.num_players = i + 3
            
            # Check start button
            start_btn.check_hover(mouse_pos)
            if mouse_click and start_btn.check_click(mouse_pos, mouse_click):
                game_state.game_phase = "player_setup"
                game_state.selected_characters = []
        
        elif game_state.game_phase == "player_setup":
            # Draw character selection
            char_buttons, start_btn = ui.draw_character_selection(screen, game_state.selected_characters)
            
            # Check character buttons
            for i, btn in enumerate(char_buttons):
                btn.check_hover(mouse_pos)
                if mouse_click and btn.check_click(mouse_pos, mouse_click):
                    # Toggle character selection
                    if i in game_state.selected_characters:
                        game_state.selected_characters.remove(i)
                    elif len(game_state.selected_characters) < game_state.num_players:
                        game_state.selected_characters.append(i)
            
            # Check start button
            start_btn.check_hover(mouse_pos)
            if mouse_click and start_btn.check_click(mouse_pos, mouse_click) and len(game_state.selected_characters) == game_state.num_players:
                # Initialize the game
                game_state.initialize_game()
        
        elif game_state.game_phase == "playing":
            # Draw game board
            screen.fill(LIGHT_GRAY)
            game_state.board.render(screen)
            
            # Draw players 
            for i, player in enumerate(game_state.players):
                # Only draw active players
                if player["active"]:
                    is_current = (i == game_state.current_player_idx)
                    game_state.board.render_player(screen, player, is_current)
            
            # Draw valid moves
            if game_state.moves_left > 0:
                valid_moves = game_state.get_valid_moves()
                game_state.board.highlight_valid_moves(screen, valid_moves)
            
            # Draw player panel
            ui.draw_player_panel(screen, game_state.players, game_state.current_player_idx)
            
            # Draw current player's cards
            current_player = game_state.players[game_state.current_player_idx]
            ui.draw_player_cards(screen, current_player)
            
            # Draw dice panel
            ui.draw_dice_panel(screen, game_state.dice_values, game_state.moves_left)
            
            # Draw controls
            ui.draw_controls(screen)
            
            # Draw game log
            ui.draw_game_log(screen, game_state.game_log)
            
            # Add message to game log if there's a new message
            if message:
                game_state.add_to_log(message)
                message = None
            
            
            # When a card is being shown
            if game_state.showing_card_ui:
                ok_btn = ui.draw_card_ui(screen, game_state.card_being_shown)
                
                if ok_btn:
                    ok_btn.check_hover(mouse_pos)
                    if mouse_click and ok_btn.check_click(mouse_pos, mouse_click):
                        game_state.acknowledge_card()
                        
            # When there's a message to display
            elif game_state.showing_notification_ui:
                ok_btn = ui.draw_notification_ui(screen, game_state.notification_message)
                
                if ok_btn:
                    ok_btn.check_hover(mouse_pos)
                    if mouse_click and ok_btn.check_click(mouse_pos, mouse_click):
                        game_state.acknowledge_notification()
            
            # Suggestion 
            elif game_state.showing_suggestion_ui:
                char_buttons, weapon_buttons, submit_btn, cancel_btn = ui.draw_suggestion_ui(
                    screen, 
                    game_state.selected_suggestion_character,
                    game_state.selected_suggestion_weapon
                )
                
                # Check character buttons
                for btn, char_name in char_buttons:
                    btn.check_hover(mouse_pos)
                    if mouse_click and btn.check_click(mouse_pos, mouse_click):
                        game_state.selected_suggestion_character = char_name
                
                # Check weapon buttons
                for btn, weapon_name in weapon_buttons:
                    btn.check_hover(mouse_pos)
                    if mouse_click and btn.check_click(mouse_pos, mouse_click):
                        game_state.selected_suggestion_weapon = weapon_name
                
                # Check submit button
                submit_btn.check_hover(mouse_pos)
                if mouse_click and submit_btn.check_click(mouse_pos, mouse_click):
                    if game_state.selected_suggestion_character and game_state.selected_suggestion_weapon:
                        # Make suggestion
                        success, suggestion_msg = game_state.make_suggestion(
                            game_state.selected_suggestion_character,
                            game_state.selected_suggestion_weapon
                        )
                        
                        # Close UI
                        game_state.showing_suggestion_ui = False
                        if success:
                            message = "Suggestion made."
                        else:
                            message = suggestion_msg
                
                # Check cancel button
                cancel_btn.check_hover(mouse_pos)
                if mouse_click and cancel_btn.check_click(mouse_pos, mouse_click):
                    game_state.showing_suggestion_ui = False
                    message = "Suggestion canceled."
            
            # Accusation UI
            elif game_state.showing_accusation_ui:
                char_buttons, weapon_buttons, room_buttons, submit_btn, cancel_btn = ui.draw_accusation_ui(
                    screen,
                    game_state.selected_accusation_character,
                    game_state.selected_accusation_weapon,
                    game_state.selected_accusation_room
                )
                
                # Check character buttons
                for btn, char_name in char_buttons:
                    btn.check_hover(mouse_pos)
                    if mouse_click and btn.check_click(mouse_pos, mouse_click):
                        game_state.selected_accusation_character = char_name
                
                # Check weapon buttons
                for btn, weapon_name in weapon_buttons:
                    btn.check_hover(mouse_pos)
                    if mouse_click and btn.check_click(mouse_pos, mouse_click):
                        game_state.selected_accusation_weapon = weapon_name
                
                # Check room buttons
                for btn, room_idx in room_buttons:
                    btn.check_hover(mouse_pos)
                    if mouse_click and btn.check_click(mouse_pos, mouse_click):
                        game_state.selected_accusation_room = room_idx
                
                # Check submit button
                submit_btn.check_hover(mouse_pos)
                if mouse_click and submit_btn.check_click(mouse_pos, mouse_click):
                    if (game_state.selected_accusation_character and 
                        game_state.selected_accusation_weapon and 
                        game_state.selected_accusation_room is not None):
                        # Make accusation
                        correct, accusation_msg = game_state.make_accusation(
                            game_state.selected_accusation_character,
                            game_state.selected_accusation_weapon,
                            game_state.selected_accusation_room
                        )
                        
                        # Close UI
                        game_state.showing_accusation_ui = False
                        if correct:
                            message = "Correct accusation! You win!"
                        else:
                            message = "Incorrect accusation! You're eliminated."
                
                # Check cancel button
                cancel_btn.check_hover(mouse_pos)
                if mouse_click and cancel_btn.check_click(mouse_pos, mouse_click):
                    game_state.showing_accusation_ui = False
                    message = "Accusation canceled."
        
        elif game_state.game_phase == "game_over":
            # Draw game board (background)
            screen.fill(LIGHT_GRAY)
            game_state.board.render(screen)
            
            # Draw player panel
            ui.draw_player_panel(screen, game_state.players, game_state.current_player_idx)
            
            # Draw game log
            ui.draw_game_log(screen, game_state.game_log)
            
            # Get winner name if any
            winner_name = None
            if any(player["active"] for player in game_state.players):
                winner_name = game_state.players[game_state.current_player_idx]["name"]
            
            menu_btn = ui.draw_game_over(screen, game_state.solution, winner_name)
            
            # Check menu button
            menu_btn.check_hover(mouse_pos)
            if mouse_click and menu_btn.check_click(mouse_pos, mouse_click):
                # Reset the game
                game_state = GameState()
                ui = UI()  
        
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()