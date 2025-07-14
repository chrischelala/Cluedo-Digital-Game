import pygame
from game_constants import *

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=BLACK, font_size=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.hovered = False
    
    def draw(self, screen, font=None):
        # Draw button with hover effect
        color = tuple(min(c + 20, 255) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Draw text
        if font is None:
            font = pygame.font.SysFont(None, self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered
    
    def check_click(self, mouse_pos, click):
        return self.rect.collidepoint(mouse_pos) and click

class UI:
    def __init__(self):
        # Initialize fonts
        self.title_font = pygame.font.SysFont(None, 40)
        self.heading_font = pygame.font.SysFont(None, 28)
        self.normal_font = pygame.font.SysFont(None, 18)
        self.small_font = pygame.font.SysFont(None, 14)
        
        # Game log scroll position
        self.log_scroll_offset = 0
        self.log_buttons = []
    
    def draw_start_menu(self, screen, num_players):
        screen.fill(LIGHT_GRAY)
        
        # Draw title
        title = self.title_font.render("CLUEDO", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # Draw player count selector
        text = self.heading_font.render("Select Number of Players:", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(text, text_rect)
        
        # Player count buttons
        buttons = []
        for i in range(3, 7):
            color = LIGHT_BLUE if i == num_players else WHITE
            btn = Button(SCREEN_WIDTH // 2 - 150 + (i - 3) * 80, 250, 60, 40, str(i), color, BLACK, 24)
            btn.draw(screen)
            buttons.append(btn)
        
        # Start button
        start_btn = Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50, "Character Selection", LIGHT_GREEN, BLACK, 24)
        start_btn.draw(screen)
        
        return buttons, start_btn
    
    def draw_character_selection(self, screen, selected_characters):
        # Clear screen
        screen.fill(LIGHT_GRAY)
        
        # Draw title
        title = self.title_font.render("Select Characters", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        # Draw character options
        char_buttons = []
        for i, character in enumerate(CHARACTERS):
            # Create a button for each character
            row = i // 3
            col = i % 3
            x = SCREEN_WIDTH // 2 - 300 + col * 200
            y = 120 + row * 100
            
            # Button color (highlight if selected)
            color = LIGHT_BLUE if i in selected_characters else WHITE
            btn = Button(x, y, 180, 80, character["name"], color, BLACK, 20)
            
            # Draw character color indicator
            pygame.draw.circle(screen, character["color"], (x + 20, y + 40), 15)
            
            btn.draw(screen)
            char_buttons.append(btn)
        
        # Start game button
        start_btn = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 50, "Start Game", LIGHT_GREEN, BLACK, 24)
        start_btn.draw(screen)

        if len(selected_characters) < len(CHARACTERS):
            help_text = self.small_font.render(f"Select {len(selected_characters) + 1} of 6", True, BLACK)
            screen.blit(help_text, (SCREEN_WIDTH // 2 - 70, 460))
        
        return char_buttons, start_btn
    
    def draw_player_panel(self, screen, players, current_player_idx):
        panel_rect = pygame.Rect(590, 20, 414, 230)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.heading_font.render("PLAYERS", True, BLACK)
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Player list
        for i, player in enumerate(players):
            y_pos = panel_rect.y + 45 + i * 30
            
            # Highlight current player
            if i == current_player_idx:
                indicator_rect = pygame.Rect(panel_rect.x + 5, y_pos - 2, panel_rect.width - 10, 24)
                pygame.draw.rect(screen, LIGHT_YELLOW, indicator_rect)
                pygame.draw.rect(screen, BLACK, indicator_rect, 1)
                screen.blit(self.normal_font.render("►", True, BLACK), (panel_rect.x + 10, y_pos))
            
            # Draw player color indicator
            pygame.draw.circle(screen, player["color"], (panel_rect.x + 40, y_pos + 10), 10) 
            pygame.draw.circle(screen, BLACK, (panel_rect.x + 40, y_pos + 10), 10, 1)  
            
            name_text = player["name"]
            if not player["active"]:
                name_text += " (Eliminated)"
            name_surf = self.normal_font.render(name_text, True, BLACK)
            screen.blit(name_surf, (panel_rect.x + 60, y_pos + 5))  
    
    def draw_player_cards(self, screen, player):
        panel_rect = pygame.Rect(590, 260, 414, 120)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.heading_font.render("YOUR CARDS", True, BLACK)
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Draw cards (3 cards side by side)
        card_width = 120
        card_height = 80
        card_spacing = 20
        
        # Center cards in the panel
        start_x = panel_rect.x + (panel_rect.width - (3 * card_width + 2 * card_spacing)) // 2
        start_y = panel_rect.y + 35
        
        for i, card in enumerate(player["cards"]):
            card_x = start_x + i * (card_width + card_spacing)
            card_y = start_y
            
            # Get appropriate color based on card type
            if card["type"] == CARD_TYPES["CHARACTER"]:
                color = LIGHT_PURPLE
                type_text = "Character"
            elif card["type"] == CARD_TYPES["WEAPON"]:
                color = LIGHT_RED
                type_text = "Weapon"
            elif card["type"] == CARD_TYPES["ROOM"]:
                color = LIGHT_BLUE
                type_text = "Room"
            else:
                color = WHITE
                type_text = "Unknown"
            
            # Draw card background
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(screen, color, card_rect)
            pygame.draw.rect(screen, BLACK, card_rect, 2)
            
            # Draw card type
            type_surf = self.small_font.render(type_text, True, BLACK)
            screen.blit(type_surf, (card_x + 5, card_y + 5))
            
            # Draw card name
            name_surf = self.normal_font.render(card["name"], True, BLACK)
            name_rect = name_surf.get_rect(center=(card_x + card_width // 2, card_y + card_height // 2))
            screen.blit(name_surf, name_rect)
    
    def draw_dice_panel(self, screen, dice_values, moves_left):
        panel_rect = pygame.Rect(590, 390, 414, 60)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.heading_font.render("DICE", True, BLACK)
        screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Draw dice
        die1, die2 = dice_values
        
        # First die
        die_rect = pygame.Rect(panel_rect.x + 100, panel_rect.y + 15, 30, 30)  # Smaller dice
        pygame.draw.rect(screen, WHITE, die_rect)
        pygame.draw.rect(screen, BLACK, die_rect, 2)
        die_text = self.normal_font.render(str(die1), True, BLACK)
        die_text_rect = die_text.get_rect(center=die_rect.center)
        screen.blit(die_text, die_text_rect)
        
        # Second die
        die_rect = pygame.Rect(panel_rect.x + 140, panel_rect.y + 15, 30, 30)  # Smaller dice
        pygame.draw.rect(screen, WHITE, die_rect)
        pygame.draw.rect(screen, BLACK, die_rect, 2)
        die_text = self.normal_font.render(str(die2), True, BLACK)
        die_text_rect = die_text.get_rect(center=die_rect.center)
        screen.blit(die_text, die_text_rect)
        
        # Total and moves left
        total_text = self.normal_font.render(f"Total: {die1 + die2}", True, BLACK)
        screen.blit(total_text, (panel_rect.x + 190, panel_rect.y + 22))
        
        if moves_left > 0:
            moves_text = self.normal_font.render(f"Moves left: {moves_left}", True, BLACK)
            screen.blit(moves_text, (panel_rect.x + 280, panel_rect.y + 22))
    
    def draw_controls(self, screen):
        controls_rect = pygame.Rect(590, 460, 414, 130)  
        pygame.draw.rect(screen, WHITE, controls_rect)
        pygame.draw.rect(screen, BLACK, controls_rect, 2)  
        
        # Title
        title = self.heading_font.render("CONTROLS", True, BLACK)
        screen.blit(title, (controls_rect.x + 10, controls_rect.y + 10))
        
        controls_font = pygame.font.SysFont(None, 20)  
        
        controls_left = [
            "D - Roll dice",
            "Arrow keys - Move",
            "ESC - Cancel"
        ]
        
        controls_right = [
            "S - Make suggestion",
            "A - Make accusation",
            "Enter - End turn"
        ]
        
        for i, control in enumerate(controls_left):
            y_pos = controls_rect.y + 40 + i * 22  
            control_text = controls_font.render(control, True, BLACK)
            screen.blit(control_text, (controls_rect.x + 20, y_pos))
        
        for i, control in enumerate(controls_right):
            y_pos = controls_rect.y + 40 + i * 22  
            control_text = controls_font.render(control, True, BLACK)
            screen.blit(control_text, (controls_rect.x + 220, y_pos))
        
    
    def draw_game_log(self, screen, game_log):
        log_rect = pygame.Rect(20, 590, 984, 158)
        pygame.draw.rect(screen, WHITE, log_rect)
        pygame.draw.rect(screen, BLACK, log_rect, 2)
        
        # Title
        title_area = pygame.Rect(log_rect.x, log_rect.y, log_rect.width, 30)
        pygame.draw.rect(screen, LIGHT_GRAY, title_area)
        title = self.heading_font.render("GAME LOG", True, BLACK)
        screen.blit(title, (log_rect.x + 10, log_rect.y + 5))
        
        # Create a clip area for the log entries
        log_content_rect = pygame.Rect(log_rect.x, log_rect.y + 30, log_rect.width, log_rect.height - 30)
        pygame.draw.rect(screen, WHITE, log_content_rect)
        
        # Create scroll buttons
        scroll_up_btn = Button(log_rect.x + log_rect.width - 60, log_rect.y + 5, 25, 20, "▲", LIGHT_GRAY, BLACK, 16)
        scroll_down_btn = Button(log_rect.x + log_rect.width - 30, log_rect.y + 5, 25, 20, "▼", LIGHT_GRAY, BLACK, 16)
        scroll_up_btn.draw(screen)
        scroll_down_btn.draw(screen)
        self.log_buttons = [scroll_up_btn, scroll_down_btn]
        
        # Draw scrollbar
        scrollbar_height = min(100, int(log_content_rect.height * (LOG_ENTRIES_PER_PAGE / max(1, len(game_log)))))
        scrollbar_position = log_content_rect.y
        if len(game_log) > LOG_ENTRIES_PER_PAGE:
            scrollbar_position += int((log_content_rect.height - scrollbar_height) * (self.log_scroll_offset / (len(game_log) - LOG_ENTRIES_PER_PAGE)))
        
        scrollbar_rect = pygame.Rect(log_rect.x + log_rect.width - 15, scrollbar_position, 10, scrollbar_height)
        pygame.draw.rect(screen, DARK_GRAY, scrollbar_rect)
        
        original_clip = screen.get_clip()
        screen.set_clip(log_content_rect)
        
        start_idx = max(0, min(self.log_scroll_offset, len(game_log) - LOG_ENTRIES_PER_PAGE))
        end_idx = min(start_idx + LOG_ENTRIES_PER_PAGE, len(game_log))
        visible_entries = game_log[start_idx:end_idx]
        
        for i, entry in enumerate(visible_entries):
            y_pos = log_content_rect.y + 5 + i * 18  
            log_text = self.normal_font.render(entry, True, BLACK)
            screen.blit(log_text, (log_content_rect.x + 10, y_pos))
        
        screen.set_clip(original_clip)
    
    def handle_log_scroll(self, mouse_pos, mouse_click, game_log):
        if len(game_log) <= LOG_ENTRIES_PER_PAGE:
            return False
            
        # Check if scroll buttons are clicked
        if mouse_click:
            # Scroll up button
            if self.log_buttons[0].check_click(mouse_pos, True):
                self.log_scroll_offset = max(0, self.log_scroll_offset - 1)
                return True
                
            # Scroll down button
            if self.log_buttons[1].check_click(mouse_pos, True):
                self.log_scroll_offset = min(len(game_log) - LOG_ENTRIES_PER_PAGE, self.log_scroll_offset + 1)
                return True
                
        return False
    
    def draw_card_ui(self, screen, card):
        if card is None:
            return None
            
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Card panel
        panel_width = 300
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.heading_font.render("Card Revealed", True, BLACK)
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
        screen.blit(title, title_rect)
        
        # Card type
        card_type_names = {
            CARD_TYPES["CHARACTER"]: "Character",
            CARD_TYPES["WEAPON"]: "Weapon",
            CARD_TYPES["ROOM"]: "Room"
        }
        card_type = card_type_names[card["type"]]
        type_text = self.normal_font.render(f"Type: {card_type}", True, BLACK)
        screen.blit(type_text, (panel_x + 50, panel_y + 80))
        
        # Card name
        name_text = self.heading_font.render(card["name"], True, BLACK)
        name_rect = name_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 150))
        screen.blit(name_text, name_rect)
        
        # Card visual representation
        if card["type"] == CARD_TYPES["CHARACTER"]:
            char_color = BLACK
            for character in CHARACTERS:
                if character["name"] == card["name"]:
                    char_color = character["color"]
                    break
                    
            # Draw character icon
            pygame.draw.circle(screen, char_color, (panel_x + panel_width // 2, panel_y + 220), 40)
            pygame.draw.circle(screen, BLACK, (panel_x + panel_width // 2, panel_y + 220), 40, 2)
        elif card["type"] == CARD_TYPES["WEAPON"]:
            # Draw weapon icon 
            weapon_rect = pygame.Rect(panel_x + panel_width // 2 - 30, panel_y + 200, 60, 40)
            pygame.draw.rect(screen, LIGHT_RED, weapon_rect)
            pygame.draw.rect(screen, BLACK, weapon_rect, 2)
        elif card["type"] == CARD_TYPES["ROOM"]:
            # Draw room icon (simple house shape)
            room_rect = pygame.Rect(panel_x + panel_width // 2 - 40, panel_y + 200, 80, 60)
            pygame.draw.rect(screen, LIGHT_BLUE, room_rect)
            pygame.draw.rect(screen, BLACK, room_rect, 2)
            
            roof_points = [(panel_x + panel_width // 2 - 50, panel_y + 200),
                          (panel_x + panel_width // 2, panel_y + 170),
                          (panel_x + panel_width // 2 + 50, panel_y + 200)]
            pygame.draw.polygon(screen, LIGHT_RED, roof_points)
            pygame.draw.polygon(screen, BLACK, roof_points, 2)
        
        ok_btn = Button(panel_x + 75, panel_y + 320, 150, 40, "OK", LIGHT_GREEN, BLACK, 20)
        ok_btn.draw(screen)
        
        return ok_btn
    
    def draw_notification_ui(self, screen, message):
        if message is None:
            return None
            
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        panel_width = 400
        panel_height = 200
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        title = self.heading_font.render("Suggestion Result", True, BLACK)
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
        screen.blit(title, title_rect)
        
        message_lines = []
        words = message.split()
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width = self.normal_font.size(test_line)[0]
            if test_width < panel_width - 40:
                current_line = test_line
            else:
                message_lines.append(current_line)
                current_line = word
        if current_line:
            message_lines.append(current_line)
        
        for i, line in enumerate(message_lines):
            msg_text = self.normal_font.render(line, True, BLACK)
            msg_rect = msg_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 80 + i * 20))
            screen.blit(msg_text, msg_rect)
        
        ok_btn = Button(panel_x + 125, panel_y + 140, 150, 40, "OK", LIGHT_GREEN, BLACK, 20)
        ok_btn.draw(screen)
        
        return ok_btn
        
    def draw_suggestion_ui(self, screen, selected_character, selected_weapon):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Suggestion panel
        panel_width = 600
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.heading_font.render("Make a Suggestion", True, BLACK)
        screen.blit(title, (panel_x + 20, panel_y + 20))
        
        # Character selection
        title = self.normal_font.render("Select Character:", True, BLACK)
        screen.blit(title, (panel_x + 20, panel_y + 70))
        
        char_buttons = []
        for i, character in enumerate(CHARACTERS):
            row = i // 3
            col = i % 3
            btn_x = panel_x + 20 + col * 190
            btn_y = panel_y + 100 + row * 45 
            
            # Highlight selected character
            color = LIGHT_BLUE if character["name"] == selected_character else WHITE
            btn = Button(btn_x, btn_y, 180, 35, character["name"], color, BLACK, 16)
            
            # Draw character color indicator
            pygame.draw.circle(screen, character["color"], (btn_x + 15, btn_y + 17), 8)
            
            btn.draw(screen)
            char_buttons.append((btn, character["name"]))
        
        # Weapon selection
        title = self.normal_font.render("Select Weapon:", True, BLACK)
        screen.blit(title, (panel_x + 20, panel_y + 200))
        
        weapon_buttons = []
        for i, weapon in enumerate(WEAPONS):
            # Weapon button
            row = i // 3
            col = i % 3
            btn_x = panel_x + 20 + col * 190
            btn_y = panel_y + 230 + row * 35  
            
            # Highlight selected weapon
            color = LIGHT_BLUE if weapon == selected_weapon else WHITE
            btn = Button(btn_x, btn_y, 180, 25, weapon, color, BLACK, 16)
            
            btn.draw(screen)
            weapon_buttons.append((btn, weapon))
        
        # Submit and Cancel buttons
        submit_btn = Button(panel_x + 150, panel_y + 340, 120, 40, "Submit", LIGHT_GREEN, BLACK, 20)
        submit_btn.draw(screen)
        
        cancel_btn = Button(panel_x + 330, panel_y + 340, 120, 40, "Cancel", LIGHT_RED, BLACK, 20)
        cancel_btn.draw(screen)
        
        return char_buttons, weapon_buttons, submit_btn, cancel_btn
    
    def draw_accusation_ui(self, screen, selected_character, selected_weapon, selected_room):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Accusation panel
        panel_width = 600
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Title
        title = self.heading_font.render("Make an Accusation", True, BLACK)
        screen.blit(title, (panel_x + 20, panel_y + 20))
        
        # Warning
        warning = self.normal_font.render("Warning: If wrong, you will be eliminated!", True, (200, 0, 0))
        screen.blit(warning, (panel_x + 20, panel_y + 50))
        
        # Character selection
        title = self.normal_font.render("Select Character:", True, BLACK)
        screen.blit(title, (panel_x + 20, panel_y + 90))
        
        char_buttons = []
        for i, character in enumerate(CHARACTERS):
            # Character button
            row = i // 3
            col = i % 3
            btn_x = panel_x + 20 + col * 190
            btn_y = panel_y + 120 + row * 40  
            
            # Highlight selected character
            color = LIGHT_BLUE if character["name"] == selected_character else WHITE
            btn = Button(btn_x, btn_y, 180, 30, character["name"], color, BLACK, 16)
            
            # Draw character color indicator
            pygame.draw.circle(screen, character["color"], (btn_x + 15, btn_y + 15), 8)
            
            btn.draw(screen)
            char_buttons.append((btn, character["name"]))
        
        # Weapon selection
        title = self.normal_font.render("Select Weapon:", True, BLACK)
        screen.blit(title, (panel_x + 20, panel_y + 210))
        
        weapon_buttons = []
        for i, weapon in enumerate(WEAPONS):
            # Weapon button
            row = i // 3
            col = i % 3
            btn_x = panel_x + 20 + col * 190
            btn_y = panel_y + 240 + row * 35

            # Highlight selected weapon
            color = LIGHT_BLUE if weapon == selected_weapon else WHITE
            btn = Button(btn_x, btn_y, 180, 25, weapon, color, BLACK, 16)
            
            btn.draw(screen)
            weapon_buttons.append((btn, weapon))
        
        # Room selection
        title = self.normal_font.render("Select Room:", True, BLACK)
        screen.blit(title, (panel_x + 20, panel_y + 320))
        
        room_buttons = []
        for i, room in enumerate(ROOMS):
            # Room button
            row = i // 3
            col = i % 3
            btn_x = panel_x + 20 + col * 190
            btn_y = panel_y + 350 + row * 35 

            # Highlight selected room
            color = LIGHT_BLUE if i == selected_room else WHITE
            btn = Button(btn_x, btn_y, 180, 25, room["name"], color, BLACK, 16)
            
            btn.draw(screen)
            room_buttons.append((btn, i))
        
        # Submit and Cancel buttons
        submit_btn = Button(panel_x + 150, panel_y + 450, 120, 40, "Submit", LIGHT_GREEN, BLACK, 20)
        submit_btn.draw(screen)
        
        cancel_btn = Button(panel_x + 330, panel_y + 450, 120, 40, "Cancel", LIGHT_RED, BLACK, 20)
        cancel_btn.draw(screen)
        
        return char_buttons, weapon_buttons, room_buttons, submit_btn, cancel_btn
    
    def draw_game_over(self, screen, solution, winner=None):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game over panel
        panel_width = 500
        panel_height = 300
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, WHITE, panel_rect)
        pygame.draw.rect(screen, BLACK, panel_rect, 2)
        
        # Title
        if winner:
            title = self.title_font.render(f"{winner} Wins!", True, (0, 128, 0))
        else:
            title = self.title_font.render("Game Over", True, (200, 0, 0))
        
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, panel_y + 50))
        screen.blit(title, title_rect)
        
        # Solution
        solution_text = self.heading_font.render("The solution was:", True, BLACK)
        solution_rect = solution_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 100))
        screen.blit(solution_text, solution_rect)
        
        murderer_text = self.normal_font.render(f"Murderer: {solution['murderer']}", True, BLACK)
        murderer_rect = murderer_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 140))
        screen.blit(murderer_text, murderer_rect)
        
        weapon_text = self.normal_font.render(f"Weapon: {solution['weapon']}", True, BLACK)
        weapon_rect = weapon_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 170))
        screen.blit(weapon_text, weapon_rect)
        
        room_text = self.normal_font.render(f"Room: {solution['room']}", True, BLACK)
        room_rect = room_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 200))
        screen.blit(room_text, room_rect)
        
        # Back to menu button
        menu_btn = Button(panel_x + 150, panel_y + 240, 200, 40, "Back to Menu", LIGHT_GREEN, BLACK, 20)
        menu_btn.draw(screen)
        
        return menu_btn