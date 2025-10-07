#before running the game please do install dependencies in requirements.txt file

import os
import sys

# Use psycopg2 only (simpler for beginners)
try:
    import psycopg2 as pg
except ImportError:
    print("Missing dependency: psycopg2-binary")
    print("Please run: pip install psycopg2-binary")
    sys.exit(1)

DB_PARAMS = {
    'dbname': os.getenv('PGDATABASE', 'postgres'),
    'user': os.getenv('PGUSER', 'postgres'),
    'password': os.getenv('PGPASSWORD', 'postgres'),
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', '5432')),
}

def connect():
    return pg.connect(**DB_PARAMS)

def init_game(rows=10, cols=20):
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT init_game(%s,%s)", (rows, cols))
        gid = cur.fetchone()[0]
        return gid

def get_board(gid):
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT get_board(%s)", (gid,))
        return cur.fetchone()[0]

def step(gid, direction):
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT step(%s,%s)::text", (gid, direction))
        return cur.fetchone()[0]

KEY_TO_DIR = {
    'w': 'U',
    's': 'D',
    'a': 'L',
    'd': 'R',
}

def read_key():
    """Read a single keypress from stdin (Linux/Mac)."""
    import termios, tty
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    print("Starting new SQL Snake game...")
    gid = init_game(10, 20)
    print(f"Game id: {gid}\n")

    current_dir = 'R'

    while True:
        os.system('clear')
        print(get_board(gid))
        print("Use WASD keys to move, q to quit.")

        ch = read_key()
        if ch == 'q':
            print("Quitting.")
            break
        if ch in KEY_TO_DIR:
            current_dir = KEY_TO_DIR[ch]

        status = step(gid, current_dir)
        if 'dead' in status:
            os.system('clear')
            print(get_board(gid))
            print("Game over! Final status:", status)
            break

if __name__ == "__main__":
    main()
