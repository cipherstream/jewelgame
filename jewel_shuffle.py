import pygame
import random
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BOARD_SIZE = 8
CELL_SIZE = 60
BOARD_OFFSET_X = (WINDOW_WIDTH - BOARD_SIZE * CELL_SIZE) // 2
BOARD_OFFSET_Y = 80
FPS = 60

# Colors (cute pastel palette)
BACKGROUND = (255, 248, 240)
PANEL_COLOR = (255, 182, 193)
TEXT_COLOR = (139, 69, 19)
GRID_COLOR = (255, 218, 185)

# Jewel colors (cute and bright)
JEWEL_COLORS = {
    'red': (255, 99, 132),
    'blue': (54, 162, 235),
    'green': (75, 192, 192),
    'yellow': (255, 206, 86),
    'purple': (153, 102, 255),
    'orange': (255, 159, 64)
}

class JewelType(Enum):
    RED = 'red'
    BLUE = 'blue'
    GREEN = 'green'
    YELLOW = 'yellow'
    PURPLE = 'purple'
    ORANGE = 'orange'

class Jewel:
    def __init__(self, jewel_type, row, col):
        self.type = jewel_type
        self.row = row
        self.col = col
        self.x = BOARD_OFFSET_X + col * CELL_SIZE
        self.y = BOARD_OFFSET_Y + row * CELL_SIZE
        self.selected = False
        self.falling = False
        self.target_y = self.y
        
    def draw(self, screen):
        # Draw jewel shadow
        shadow_offset = 3
        pygame.draw.circle(screen, (200, 200, 200), 
                         (self.x + CELL_SIZE // 2 + shadow_offset, 
                          self.y + CELL_SIZE // 2 + shadow_offset), 
                         CELL_SIZE // 2 - 5)
        
        # Draw jewel
        color = JEWEL_COLORS[self.type.value]
        pygame.draw.circle(screen, color, 
                         (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2), 
                         CELL_SIZE // 2 - 5)
        
        # Draw highlight
        highlight_offset = CELL_SIZE // 4
        pygame.draw.circle(screen, (255, 255, 255), 
                         (self.x + CELL_SIZE // 2 - highlight_offset, 
                          self.y + CELL_SIZE // 2 - highlight_offset), 
                         CELL_SIZE // 6)
        
        # Draw selection indicator
        if self.selected:
            pygame.draw.circle(screen, (255, 215, 0), 
                             (self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2), 
                             CELL_SIZE // 2 - 2, 3)
    
    def update(self):
        if self.falling and self.y < self.target_y:
            self.y += 8
            if self.y >= self.target_y:
                self.y = self.target_y
                self.falling = False
    
    def set_position(self, row, col):
        self.row = row
        self.col = col
        self.x = BOARD_OFFSET_X + col * CELL_SIZE
        self.y = BOARD_OFFSET_Y + row * CELL_SIZE
        self.target_y = self.y

class GameBoard:
    def __init__(self):
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected_jewel = None
        self.score = 0
        self.moves = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.initialize_board()
        
    def initialize_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                jewel_type = random.choice(list(JewelType))
                self.grid[row][col] = Jewel(jewel_type, row, col)
        
        # Remove initial matches
        while self.find_matches():
            self.remove_matches()
            self.fill_empty_spaces()
    
    def draw(self, screen):
        # Draw background panel
        pygame.draw.rect(screen, PANEL_COLOR, 
                        (BOARD_OFFSET_X - 10, BOARD_OFFSET_Y - 10, 
                         BOARD_SIZE * CELL_SIZE + 20, BOARD_SIZE * CELL_SIZE + 20))
        
        # Draw grid
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = BOARD_OFFSET_X + col * CELL_SIZE
                y = BOARD_OFFSET_Y + row * CELL_SIZE
                pygame.draw.rect(screen, GRID_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 1)
        
        # Draw jewels
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].draw(screen)
        
        # Draw UI
        self.draw_ui(screen)
    
    def draw_ui(self, screen):
        # Draw title
        title_text = self.font.render("Jewel Shuffle", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
        screen.blit(title_text, title_rect)
        
        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, TEXT_COLOR)
        screen.blit(score_text, (50, 50))
        
        # Draw moves
        moves_text = self.small_font.render(f"Moves: {self.moves}", True, TEXT_COLOR)
        screen.blit(moves_text, (WINDOW_WIDTH - 150, 50))
    
    def handle_click(self, pos):
        x, y = pos
        
        # Check if click is within board
        if (x < BOARD_OFFSET_X or x > BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE or
            y < BOARD_OFFSET_Y or y > BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE):
            return
        
        # Calculate grid position
        col = (x - BOARD_OFFSET_X) // CELL_SIZE
        row = (y - BOARD_OFFSET_Y) // CELL_SIZE
        
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            clicked_jewel = self.grid[row][col]
            
            if self.selected_jewel is None:
                # Select first jewel
                self.selected_jewel = clicked_jewel
                clicked_jewel.selected = True
            else:
                # Check if clicking the same jewel
                if clicked_jewel == self.selected_jewel:
                    self.selected_jewel.selected = False
                    self.selected_jewel = None
                else:
                    # Check if jewels are adjacent
                    if self.are_adjacent(self.selected_jewel, clicked_jewel):
                        self.swap_jewels(self.selected_jewel, clicked_jewel)
                        self.moves += 1
                    else:
                        # Deselect first and select new
                        self.selected_jewel.selected = False
                        self.selected_jewel = clicked_jewel
                        clicked_jewel.selected = True
    
    def are_adjacent(self, jewel1, jewel2):
        row_diff = abs(jewel1.row - jewel2.row)
        col_diff = abs(jewel1.col - jewel2.col)
        return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
    
    def swap_jewels(self, jewel1, jewel2):
        # Swap in grid
        self.grid[jewel1.row][jewel1.col], self.grid[jewel2.row][jewel2.col] = \
            self.grid[jewel2.row][jewel2.col], self.grid[jewel1.row][jewel1.col]
        
        # Swap positions
        jewel1.row, jewel2.row = jewel2.row, jewel1.row
        jewel1.col, jewel2.col = jewel2.col, jewel1.col
        jewel1.set_position(jewel1.row, jewel1.col)
        jewel2.set_position(jewel2.row, jewel2.col)
        
        # Deselect
        jewel1.selected = False
        self.selected_jewel = None
        
        # Check for matches
        matches = self.find_matches()
        if matches:
            self.remove_matches()
            self.fill_empty_spaces()
        else:
            # Swap back if no matches
            self.grid[jewel1.row][jewel1.col], self.grid[jewel2.row][jewel2.col] = \
                self.grid[jewel2.row][jewel2.col], self.grid[jewel1.row][jewel1.col]
            
            jewel1.row, jewel2.row = jewel2.row, jewel1.row
            jewel1.col, jewel2.col = jewel2.col, jewel1.col
            jewel1.set_position(jewel1.row, jewel1.col)
            jewel2.set_position(jewel2.row, jewel2.col)
    
    def find_matches(self):
        matches = []
        
        # Check horizontal matches
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE - 2):
                if (self.grid[row][col] and self.grid[row][col + 1] and self.grid[row][col + 2]):
                    if (self.grid[row][col].type == self.grid[row][col + 1].type == 
                        self.grid[row][col + 2].type):
                        match = [(row, col), (row, col + 1), (row, col + 2)]
                        
                        # Extend match
                        k = col + 3
                        while k < BOARD_SIZE and self.grid[row][k] and \
                              self.grid[row][k].type == self.grid[row][col].type:
                            match.append((row, k))
                            k += 1
                        
                        matches.append(match)
        
        # Check vertical matches
        for col in range(BOARD_SIZE):
            for row in range(BOARD_SIZE - 2):
                if (self.grid[row][col] and self.grid[row + 1][col] and self.grid[row + 2][col]):
                    if (self.grid[row][col].type == self.grid[row + 1][col].type == 
                        self.grid[row + 2][col].type):
                        match = [(row, col), (row + 1, col), (row + 2, col)]
                        
                        # Extend match
                        k = row + 3
                        while k < BOARD_SIZE and self.grid[k][col] and \
                              self.grid[k][col].type == self.grid[row][col].type:
                            match.append((k, col))
                            k += 1
                        
                        matches.append(match)
        
        return matches
    
    def remove_matches(self):
        matches = self.find_matches()
        for match in matches:
            for row, col in match:
                self.grid[row][col] = None
                self.score += 10
    
    def fill_empty_spaces(self):
        # Move existing jewels down
        for col in range(BOARD_SIZE):
            empty_row = BOARD_SIZE - 1
            for row in range(BOARD_SIZE - 1, -1, -1):
                if self.grid[row][col] is not None:
                    if row != empty_row:
                        self.grid[empty_row][col] = self.grid[row][col]
                        self.grid[empty_row][col].set_position(empty_row, col)
                        self.grid[empty_row][col].falling = True
                        self.grid[row][col] = None
                    empty_row -= 1
        
        # Fill empty spaces with new jewels
        for col in range(BOARD_SIZE):
            for row in range(BOARD_SIZE):
                if self.grid[row][col] is None:
                    jewel_type = random.choice(list(JewelType))
                    self.grid[row][col] = Jewel(jewel_type, row, col)
                    self.grid[row][col].falling = True
                    self.grid[row][col].y = BOARD_OFFSET_Y - CELL_SIZE
                    self.grid[row][col].target_y = BOARD_OFFSET_Y + row * CELL_SIZE
    
    def update(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].update()
        
        # Check for cascading matches
        if not any(jewel.falling for row in self.grid for jewel in row if jewel):
            if self.find_matches():
                self.remove_matches()
                self.fill_empty_spaces()

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Jewel Shuffle - Cute Game for Kids!")
    clock = pygame.time.Clock()
    
    board = GameBoard()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    board.handle_click(event.pos)
        
        # Update
        board.update()
        
        # Draw
        screen.fill(BACKGROUND)
        board.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
