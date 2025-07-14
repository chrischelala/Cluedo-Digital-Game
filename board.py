import pygame
from game_constants import *

class GameBoard:
    def __init__(self):
        self.board_rect = pygame.Rect(20, 20, BOARD_WIDTH, BOARD_HEIGHT)
        
        # Create Movement grid (Tiles as hallway are walkable)
        self.grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Mark every room as non-walkable areas once entering them (0)
        for room in ROOMS:
            rx, ry = room["position"]
            width, height = room["width"], room["height"]
            
            for y in range(ry, ry + height):
                for x in range(rx, rx + width):
                    self.grid[y][x] = 0  # Room interior is not walkable
        
        # Mark outer walls of the board as non-walkable
        for y in range(GRID_WIDTH):
            self.grid[y][0] = 0  # Left wall
            self.grid[y][GRID_WIDTH-1] = 0  # Right wall
            
        for x in range(GRID_HEIGHT):
            self.grid[0][x] = 0  # Top wall
            self.grid[GRID_HEIGHT-1][x] = 0  # Bottom wall
        
        # Initialize center of rooms and doors
        self.room_centers = []
        self.room_doors = [[] for _ in range(len(ROOMS))]
        
        # Set room centers
        for room in ROOMS:
            x = room["position"][0] + room["width"] // 2
            y = room["position"][1] + room["height"] // 2
            self.room_centers.append((x, y))
        
        # Create hallway paths around rooms if needed
        self._ensure_hallway_paths()
        
        # Mark doors as walkable and organize by room
        for door_x, door_y, room_idx in DOORS:
            # Make doors walkable
            self.grid[door_y][door_x] = 2 
            self.room_doors[room_idx].append((door_x, door_y))
        
        # Make sure all rooms have at least one door
        self._verify_room_doors()
        
        # Ensure all doors connect to hallways
        self._ensure_door_connectivity()
    
    def _ensure_hallway_paths(self):
        # Create hallway paths to ensure accessibility between rooms
        for x in range(1, GRID_WIDTH-1):
            # Horizontal middle hallway
            self.grid[GRID_HEIGHT//2][x] = 1
        
        for y in range(1, GRID_HEIGHT-1):
            # Vertical middle hallway
            self.grid[y][GRID_WIDTH//2] = 1
    
    def _verify_room_doors(self):
        # Verify that all rooms have sufficient doors
        for i, doors in enumerate(self.room_doors):
            print(f"Room {i} ({ROOMS[i]['name']}) has {len(doors)} doors")
            
            if len(doors) < 1:
                print(f"WARNING: Room {ROOMS[i]['name']} has no doors!")
    
    def _ensure_door_connectivity(self):
        # Ensure all doors connect to walkable hallway tiles
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  

        for room_idx, doors in enumerate(self.room_doors):
            for door_x, door_y in doors:
                # Check if this door has at least one adjacent walkable tile
                has_walkable_exit = False
                
                for dx, dy in directions:
                    nx, ny = door_x + dx, door_y + dy
                    if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and 
                        self.grid[ny][nx] == 1):  
                        has_walkable_exit = True
                        break
                
                if not has_walkable_exit:
                    # Create a walkable hallway tile next to this door
                    for dx, dy in directions:
                        nx, ny = door_x + dx, door_y + dy
                        if (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and 
                            nx > 0 and nx < GRID_WIDTH-1 and ny > 0 and ny < GRID_HEIGHT-1):
                            
                            # Check if this position is inside a room (besides the door's room)
                            in_other_room = False
                            for other_idx, room in enumerate(ROOMS):
                                if other_idx == room_idx:
                                    continue  
                                
                                rx, ry = room["position"]
                                width, height = room["width"], room["height"]
                                
                                if rx <= nx < rx + width and ry <= ny < ry + height:
                                    in_other_room = True
                                    break
                            
                            if not in_other_room:
                                self.grid[ny][nx] = 1  
                                print(f"Created hallway at ({nx}, {ny}) for door to {ROOMS[room_idx]['name']}")
                                break
    
    def is_walkable(self, x, y):
        # Check if a position is walkable
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        return self.grid[y][x] > 0  
    
    def is_door(self, x, y):
        # Check if a position is a door and return the room index
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False, -1
        
        # Check if this position is in our door list
        for door_x, door_y, room_idx in DOORS:
            if x == door_x and y == door_y:
                return True, room_idx
        
        return False, -1
    
    def get_room_at(self, x, y):
        for i, room in enumerate(ROOMS):
            rx, ry = room["position"]
            width = room["width"]
            height = room["height"]
            
            if rx <= x < rx + width and ry <= y < ry + height:
                return i
        
        return None

    def get_valid_moves(self, x, y):
        moves = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  
        
        # Check if player is at a room center
        for room_idx, center in enumerate(self.room_centers):
            if (x, y) == center:
                # If at room center, can move to any door of this room
                for door_x, door_y in self.room_doors[room_idx]:
                    moves.append((door_x, door_y))
                return moves
        
        # Check if player is at a door
        is_door, room_idx = self.is_door(x, y)
        if is_door:
            # If at a door, can move to room center
            moves.append(self.room_centers[room_idx])
            
            # Also can move to any adjacent hallway tile
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                # Make sure it's a valid hallway tile
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and self.grid[ny][nx] == 1:
                    moves.append((nx, ny))
            
            return moves
        
        # Standard hallway movement
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Can move to doors
            is_door, _ = self.is_door(nx, ny)
            if is_door:
                moves.append((nx, ny))
                continue
            
            # Can move to walkable tiles
            if self.is_walkable(nx, ny):
                moves.append((nx, ny))
        
        return moves
    
    def render(self, screen):
        # Render the game board
        # Draw the background
        pygame.draw.rect(screen, LIGHT_GRAY, self.board_rect)
        pygame.draw.rect(screen, BLACK, self.board_rect, 2)
        
        # Draw the grid (hallways)
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                x = col * TILE_SIZE + self.board_rect.x
                y = row * TILE_SIZE + self.board_rect.y
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                
                # Draw tile based on type
                if self.grid[row][col] == 1: 
                    pygame.draw.rect(screen, WHITE, rect)
                    pygame.draw.rect(screen, DARK_GRAY, rect, 1)
        
        # Draw rooms
        for i, room in enumerate(ROOMS):
            rx, ry = room["position"]
            width, height = room["width"], room["height"] 
            x = rx * TILE_SIZE + self.board_rect.x
            y = ry * TILE_SIZE + self.board_rect.y
            w = width * TILE_SIZE
            h = height * TILE_SIZE
            
            # Draw room fill
            room_rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(screen, room["color"], room_rect)
            
            # Draw room borders
            pygame.draw.rect(screen, BLACK, room_rect, 2)
            
            # Draw room name
            font = pygame.font.SysFont(None, 16)
            text = font.render(room["name"], True, BLACK)
            text_rect = text.get_rect(center=(x + w // 2, y + h // 2))
            screen.blit(text, text_rect)
        
        # Draw doors on top of rooms
        for door_x, door_y, room_idx in DOORS:
            door_screen_x = door_x * TILE_SIZE + self.board_rect.x
            door_screen_y = door_y * TILE_SIZE + self.board_rect.y
            
            # Get room properties
            room = ROOMS[room_idx]
            rx, ry = room["position"]
            room_w, room_h = room["width"], room["height"]
            
            # Draw door
            door_rect = pygame.Rect(door_screen_x, door_screen_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, DOOR_COLOR, door_rect)
            
            # Determine which wall to break (if door is on a boundary)
            if door_x == rx:  
                pygame.draw.line(screen, room["color"], 
                                (door_screen_x, door_screen_y),
                                (door_screen_x, door_screen_y + TILE_SIZE), 2)
            elif door_x == rx + room_w - 1:  
                pygame.draw.line(screen, room["color"], 
                                (door_screen_x + TILE_SIZE, door_screen_y),
                                (door_screen_x + TILE_SIZE, door_screen_y + TILE_SIZE), 2)
            elif door_y == ry:  
                pygame.draw.line(screen, room["color"], 
                                (door_screen_x, door_screen_y),
                                (door_screen_x + TILE_SIZE, door_screen_y), 2)
            elif door_y == ry + room_h - 1:  
                pygame.draw.line(screen, room["color"], 
                                (door_screen_x, door_screen_y + TILE_SIZE),
                                (door_screen_x + TILE_SIZE, door_screen_y + TILE_SIZE), 2)
            
            is_boundary_door = (door_x == rx or door_x == rx + room_w - 1 or
                               door_y == ry or door_y == ry + room_h - 1)
            
            if not is_boundary_door:
                pygame.draw.rect(screen, DOOR_COLOR, door_rect)
                pygame.draw.rect(screen, BLACK, door_rect, 1)
    
    def render_player(self, screen, player, is_current):
        x, y = player["position"]
        
        player_count = 0
        player_index = 0
        
        color_sum = sum(player["color"])
        offset_index = color_sum % 4 
        
        # Calculate offsets for multiple players in the same position
        offset_patterns = [
            (0, 0),     
            (-5, -5),    
            (5, -5),    
            (5, 5),      
            (-5, 5),     
        ]
        
        offset_x, offset_y = offset_patterns[offset_index]
        
        # Calculate position with offset
        screen_x = x * TILE_SIZE + self.board_rect.x + TILE_SIZE // 2 + offset_x
        screen_y = y * TILE_SIZE + self.board_rect.y + TILE_SIZE // 2 + offset_y
        
        # Draw player token (slightly smaller to accommodate multiple players)
        radius = TILE_SIZE // 2 - 4
        pygame.draw.circle(screen, player["color"], (screen_x, screen_y), radius)
        pygame.draw.circle(screen, BLACK, (screen_x, screen_y), radius, 1)
        
        # Highlight current player
        if is_current:
            pygame.draw.circle(screen, WHITE, (screen_x, screen_y), radius + 1, 1)
    
    def screen_to_board(self, screen_x, screen_y):
        # Convert screen coordinates to board coordinates
        if not self.board_rect.collidepoint(screen_x, screen_y):
            return None
        
        board_x = (screen_x - self.board_rect.x) // TILE_SIZE
        board_y = (screen_y - self.board_rect.y) // TILE_SIZE
        
        if 0 <= board_x < GRID_WIDTH and 0 <= board_y < GRID_HEIGHT:
            return (board_x, board_y)
        
        return None
    
    def highlight_valid_moves(self, screen, valid_moves):
        # Highlight valid moves on the board
        for x, y in valid_moves:
            screen_x = x * TILE_SIZE + self.board_rect.x
            screen_y = y * TILE_SIZE + self.board_rect.y
            
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            s.fill((255, 255, 0, 128))
            screen.blit(s, (screen_x, screen_y))