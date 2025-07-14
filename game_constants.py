# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (180, 180, 180)
BEIGE = (245, 245, 220)

# Room colors
STUDY_COLOR = (160, 230, 160)        # Light green
KITCHEN_COLOR = (230, 180, 230)      # Light purple
GARAGE_COLOR = (230, 180, 180)       # Light red
BATHROOM_COLOR = (180, 200, 250)     # Light blue
GAMES_ROOM_COLOR = (250, 250, 170)   # Light yellow
LIVING_ROOM_COLOR = (170, 210, 250)  # Sky blue
BEDROOM_COLOR = (250, 170, 170)      # Salmon
DINING_ROOM_COLOR = (170, 250, 200)  # Mint green

# Other UI Colors
LIGHT_BLUE = (200, 230, 255)
LIGHT_GREEN = (220, 255, 220)
LIGHT_YELLOW = (255, 255, 200)
LIGHT_RED = (255, 220, 220)
LIGHT_PURPLE = (230, 200, 255)
LIGHT_BROWN = (230, 210, 180)
DOOR_COLOR = (255, 220, 100)         # Bright yellow for doors

# Board dimensions
BOARD_WIDTH = 550
BOARD_HEIGHT = 550
TILE_SIZE = 25  # Size of each movement tile

# Board grid dimensions
GRID_WIDTH = 21
GRID_HEIGHT = 21

# Define the rooms with their properties 
ROOMS = [
    {"name": "Study", "position": (1, 1), "width": 6, "height": 6, "color": STUDY_COLOR},
    {"name": "Kitchen", "position": (14, 1), "width": 6, "height": 6, "color": KITCHEN_COLOR},
    {"name": "Garage", "position": (1, 8), "width": 6, "height": 5, "color": GARAGE_COLOR},
    {"name": "Bathroom", "position": (14, 8), "width": 6, "height": 5, "color": BATHROOM_COLOR},
    {"name": "Games Room", "position": (1, 14), "width": 6, "height": 6, "color": GAMES_ROOM_COLOR},
    {"name": "Living Room", "position": (14, 14), "width": 6, "height": 6, "color": LIVING_ROOM_COLOR},
    {"name": "Bedroom", "position": (8, 1), "width": 5, "height": 6, "color": BEDROOM_COLOR},
    {"name": "Dining Room", "position": (8, 14), "width": 5, "height": 6, "color": DINING_ROOM_COLOR},
]

# Door positions 
DOORS = [
    # Study (Room 1) 
    (3, 6, 0),    # Bottom door
    (6, 3, 0),    # Right side door
    
    # Kitchen (Room 2) 
    (14, 3, 1),   # Left side door
    (17, 6, 1),   # Bottom right door
    
    # Garage (Room 3)
    (6, 10, 2),   # Right side door
    (3, 8, 2),    # Top side door 
    (3, 12, 2),   # Bottom side door 
    
    # Bathroom (Room 4)
    (14, 10, 3),  # Left side door
    (17, 8, 3),   # Top side door 
    (17, 12, 3),  # Bottom side door 
    
    # Games Room (Room 5) 
    (6, 17, 4),   # Right side door
    (3, 14, 4),   # Top side door 
    
    # Living Room (Room 6) 
    (14, 17, 5),  # Left side door
    (17, 14, 5),  # Top side door 
    
    # Bedroom (Room 7)
    (10, 6, 6),   # Bottom door
    (8, 3, 6),    # Left side door
    (12, 3, 6),   # Right side door
    
    # Dining Room (Room 8)
    (10, 14, 7),  # Top door
    (8, 17, 7),   # Left side door
    (12, 17, 7),  # Right side door 
]

# Character definitions with starting positions in hallways near the center
CHARACTERS = [
    {"name": "Colonel Mustard", "color": (255, 215, 0), "start_pos": (10, 9)},  # Yellow
    {"name": "Miss Scarlet", "color": (255, 0, 0), "start_pos": (12, 10)},      # Red
    {"name": "Professor Plum", "color": (128, 0, 128), "start_pos": (8, 11)},   # Purple
    {"name": "Mr. Green", "color": (0, 128, 0), "start_pos": (11, 11)},         # Green
    {"name": "Mrs. White", "color": (255, 255, 255), "start_pos": (9, 10)},     # White
    {"name": "Mrs. Peacock", "color": (0, 0, 255), "start_pos": (10, 12)}       # Blue
]

# Weapon tokens
WEAPONS = [
    "Dagger",
    "Candlestick",
    "Pistol",
    "Wrench",
    "Lead Pipe",
    "Rope"
]

# Card types for dealing to players
CARD_TYPES = {
    "CHARACTER": 0,
    "WEAPON": 1,
    "ROOM": 2
}

# Game state constants
MAX_LOG_ENTRIES = 50  
LOG_ENTRIES_PER_PAGE = 8 
CARDS_PER_PLAYER = 3  # Each player is dealt exactly 3 cards