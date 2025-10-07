"""
Simple Tetris implementation in Python using pygame.

Features:
- Playable Tetris with 7 tetrominoes
- Rotation, left/right, soft drop, hard drop
- Line clearing and scoring
- Next piece preview and hold

Controls:
- Left/Right Arrow: move
- Up Arrow or X: rotate clockwise
- Z: rotate counter-clockwise
- Down Arrow: soft drop
- Space: hard drop
- C: hold piece
- P: pause
- Esc / Q: quit

Requirements:
- Python 3.8+
- pygame (pip install pygame)

Save as tetris.py and run: python tetris.py
"""

import pygame
import random
import sys
from copy import deepcopy

# ---------- Configuration ----------
FPS = 60
CELL_SIZE = 30
COLS = 10
ROWS = 20
PLAY_WIDTH = COLS * CELL_SIZE
PLAY_HEIGHT = ROWS * CELL_SIZE
SIDE_PANEL = 200
WIDTH = PLAY_WIDTH + SIDE_PANEL + 40
HEIGHT = PLAY_HEIGHT + 40
TOP_LEFT_X = 20
TOP_LEFT_Y = 20

# Colors
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

SHAPE_COLORS = [
    (0, 240, 240),  # I - cyan
    (0, 0, 240),    # J - blue
    (240, 160, 0),  # L - orange
    (240, 240, 0),  # O - yellow
    (0, 240, 0),    # S - green
    (160, 0, 240),  # T - purple
    (240, 0, 0),    # Z - red
]

# Tetromino shapes (4x4 grids represented by strings)
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_NAMES = ['S', 'Z', 'I', 'O', 'J', 'L', 'T']

# ---------- Game Logic ----------
class Piece:
    def __init__(self, x, y, shape_index):
        self.x = x
        self.y = y
        self.shape_index = shape_index
        self.shape = SHAPES[shape_index]
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

    def get_cells(self):
        """Return list of (x,y) cells occupied by this piece relative to grid."""
        positions = []
        format = self.image()
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    positions.append((self.x + j - 2, self.y + i - 4))
        return positions


def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    for i in range(ROWS):
        for j in range(COLS):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid


def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(COLS) if grid[i][j] == BLACK] for i in range(ROWS)]
    accepted = [pos for row in accepted_positions for pos in row]

    for pos in piece.get_cells():
        x, y = pos
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and (x, y) not in accepted:
            return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 0:
            return True
    return False


def get_shape():
    index = random.randrange(len(SHAPES))
    return Piece(COLS // 2 - 2, -2, index)


def convert_shape_format(piece):
    positions = []
    format = piece.image()

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))

    return positions


def clear_rows(grid, locked):
    """Check for full rows and clear them. Return number of cleared rows."""
    inc = 0
    for i in range(ROWS - 1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            inc += 1
            # remove from locked
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if inc > 0:
        # shift every row above down
        new_locked = {}
        for (x, y), color in sorted(locked.items(), key=lambda x: x[0][1]):
            shift = 0
            for _ in range(inc):
                if y < ROWS and True:
                    shift += 1
            new_locked[(x, y + inc)] = color
        locked.clear()
        locked.update(new_locked)
    return inc

# ---------- Drawing Helpers ----------

def draw_text_middle(surface, text, size, y_offset=0):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, WHITE)

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - (label.get_width()/2), TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2 + y_offset))


def draw_grid(surface, grid):
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    for i in range(ROWS):
        pygame.draw.line(surface, GRAY, (sx, sy + i * CELL_SIZE), (sx + PLAY_WIDTH, sy + i * CELL_SIZE))
        for j in range(COLS):
            pygame.draw.line(surface, GRAY, (sx + j * CELL_SIZE, sy), (sx + j * CELL_SIZE, sy + PLAY_HEIGHT))


def draw_window(surface, grid, score=0, level=1):
    surface.fill(BLACK)

    # Title
    font = pygame.font.SysFont('comicsans', 40)
    label = font.render('TETRIS', 1, WHITE)

    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - label.get_width()/2, 5))

    # Score
    font_small = pygame.font.SysFont('comicsans', 24)
    score_label = font_small.render(f'Score: {score}', 1, WHITE)
    level_label = font_small.render(f'Level: {level}', 1, WHITE)
    surface.blit(score_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 50))
    surface.blit(level_label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 90))

    # draw play area
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y

    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j], (sx + j * CELL_SIZE, sy + i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)

    # draw grid lines
    draw_grid(surface, grid)

    # border
    pygame.draw.rect(surface, WHITE, (sx, sy, PLAY_WIDTH, PLAY_HEIGHT), 4)


def draw_next_shape(surface, shape):
    font = pygame.font.SysFont('comicsans', 24)
    label = font.render('Next', 1, WHITE)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 140))

    format = shape.image()
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + 170

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, SHAPE_COLORS[shape.shape_index], (sx + j * CELL_SIZE, sy + i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)


def draw_hold_shape(surface, shape):
    font = pygame.font.SysFont('comicsans', 24)
    label = font.render('Hold', 1, WHITE)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 260))

    if not shape:
        return

    format = shape.image()
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + 300

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, SHAPE_COLORS[shape.shape_index], (sx + j * CELL_SIZE, sy + i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)

# ---------- Main Game Loop ----------

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    hold_piece = None
    hold_locked = False

    fall_time = 0
    fall_speed = 0.5  # seconds per cell fall
    level = 1
    score = 0
    lines_cleared_total = 0

    while run:
        grid = create_grid(locked_positions)
        dt = clock.tick(FPS) / 1000.0
        fall_time += dt

        # handle fall speed acceleration by level
        if lines_cleared_total >= level * 10:
            level += 1
            fall_speed = max(0.05, fall_speed * 0.9)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    run = False
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

                elif event.key == pygame.K_z:
                    current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)

                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

                elif event.key == pygame.K_c:
                    if not hold_locked:
                        if hold_piece is None:
                            hold_piece = Piece(COLS//2 - 2, -2, current_piece.shape_index)
                            current_piece = next_piece
                            next_piece = get_shape()
                        else:
                            temp = Piece(COLS//2 - 2, -2, current_piece.shape_index)
                            current_piece = Piece(COLS//2 - 2, -2, hold_piece.shape_index)
                            hold_piece = Piece(COLS//2 - 2, -2, temp.shape_index)
                        hold_locked = True

                elif event.key == pygame.K_p:
                    paused = True
                    while paused:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                                paused = False

        # automatic piece fall
        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y >= 0:
                grid[y][x] = SHAPE_COLORS[current_piece.shape_index]

        # when piece lands
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = SHAPE_COLORS[current_piece.shape_index]
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            hold_locked = False

            # clear rows
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                lines_cleared_total += cleared
                # scoring (classic-ish)
                if cleared == 1:
                    score += 40 * level
                elif cleared == 2:
                    score += 100 * level
                elif cleared == 3:
                    score += 300 * level
                elif cleared >= 4:
                    score += 1200 * level

        draw_window(win, grid, score, level)
        draw_next_shape(win, next_piece)
        draw_hold_shape(win, hold_piece)

        if check_lost(list(locked_positions.keys())):
            draw_text_middle(win, 'GAME OVER', 50)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()


"""
runnable Python file named tetris.py in a code canvas. It uses pygame and includes:

All 7 tetrominoes with rotation and collision handling

Left / right movement, soft drop, hard drop, rotate (CW/CCW)

Hold piece, next-piece preview, scoring, levels, and game-over detection

Pause, quit, and simple UI

How to run:

Install pygame if you don't have it: pip install pygame

Save the canvas file as tetris.py (it's already created in the code canvas) and run:
python tetris.py

Controls recap:

Left / Right arrows: move

Down arrow: soft drop

Space: hard drop

Up arrow or X: rotate clockwise

Z: rotate counter-clockwise

C: hold piece

P: pause

Esc or Q: quit
"""
