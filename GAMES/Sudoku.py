import random

def print_grid(grid):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            print(grid[i][j] if grid[i][j] != 0 else ".", end=" ")
        print()

def is_valid(grid, row, col, num):
    # Check row
    if num in grid[row]:
        return False
    
    # Check column
    for i in range(9):
        if grid[i][col] == num:
            return False
    
    # Check 3x3 square
    start_row, start_col = row - row % 3, col - col % 3
    for i in range(3):
        for j in range(3):
            if grid[start_row + i][start_col + j] == num:
                return False
    return True

def solve(grid):
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(grid, row, col, num):
                        grid[row][col] = num
                        if solve(grid):
                            return True
                        grid[row][col] = 0
                return False
    return True

def generate_sudoku():
    grid = [[0 for _ in range(9)] for _ in range(9)]
    for _ in range(15):  # Fill some numbers randomly
        row, col = random.randint(0, 8), random.randint(0, 8)
        num = random.randint(1, 9)
        if is_valid(grid, row, col, num):
            grid[row][col] = num
    return grid

# Game
grid = generate_sudoku()
print("Welcome to Sudoku!")
print_grid(grid)

while True:
    try:
        row = int(input("Row (0-8): "))
        col = int(input("Col (0-8): "))
        num = int(input("Number (1-9): "))
        
        if grid[row][col] == 0 and is_valid(grid, row, col, num):
            grid[row][col] = num
            print_grid(grid)
        else:
            print("Invalid move!")
    except ValueError:
        print("Please enter valid integers.")
