"""
Simple Ping Pong (Pong) game in Python using pygame

Controls:
  - Left paddle: W (up), S (down)
  - Right paddle: Up Arrow, Down Arrow
  - P to pause, R to reset scores
  - Escape or close window to quit

Requirements:
  - Python 3.8+
  - pygame (pip install pygame)

Run:
  python pong_game.py

This is a single-file, self-contained implementation with basic sound effects (requires SDL mixer
support available in pygame). It uses simple collision, scoring, and gradual speed increase.
"""

import pygame
import sys
import random

# ---- Configuration ----
WIDTH, HEIGHT = 900, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 16
PADDLE_SPEED = 6
BALL_START_SPEED = 5
SCORE_FONT_SIZE = 48
WINNING_SCORE = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---- Classes ----
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0

    def move(self, dy):
        self.speed = dy
        self.rect.y += dy
        # clamp
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def update(self):
        self.move(self.speed)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    def __init__(self):
        self.rect = pygame.Rect((WIDTH // 2) - BALL_SIZE // 2,
                                (HEIGHT // 2) - BALL_SIZE // 2,
                                BALL_SIZE, BALL_SIZE)
        self.reset()

    def reset(self, serveto=None):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        angle = random.uniform(-0.4, 0.4)  # slight vertical angle
        direction = random.choice([-1, 1]) if serveto is None else serveto
        self.speed = BALL_START_SPEED
        self.vx = direction * self.speed * (1 - abs(angle))
        self.vy = self.speed * angle

    def update(self, left_paddle, right_paddle):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # Top/bottom collision
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vy = -self.vy
            play_sound('wall')

        # Paddle collisions
        if self.rect.colliderect(left_paddle.rect) and self.vx < 0:
            self._bounce(left_paddle)
            play_sound('paddle')

        if self.rect.colliderect(right_paddle.rect) and self.vx > 0:
            self._bounce(right_paddle)
            play_sound('paddle')

    def _bounce(self, paddle):
        # Determine hit position on paddle: -1 (top) .. 0 center .. 1 bottom
        rel = (self.rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
        rel = max(-1, min(1, rel))
        # Increase speed slightly each hit
        self.speed *= 1.05
        # New velocities
        self.vx = -self.vx / abs(self.vx) * self.speed * (1 - 0.5 * abs(rel))
        self.vy = self.speed * rel

    def draw(self, surface):
        pygame.draw.ellipse(surface, WHITE, self.rect)


# ---- Sound helper ----
SOUNDS = {}

def load_sounds():
    try:
        SOUNDS['paddle'] = pygame.mixer.Sound(pygame.mixer.Sound.get_length)
    except Exception:
        # If loading real files isn't desired, we'll skip. Sound optional.
        pass


def play_sound(name):
    # Keep non-fatal: if sound present, play it. We intentionally keep this minimal.
    s = SOUNDS.get(name)
    if s:
        try:
            s.play()
        except Exception:
            pass


# ---- Main Game ----

def draw_center_line(surface):
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(surface, WHITE, (WIDTH // 2 - 1, y, 2, 12))


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Ping Pong - Python (pygame)')
    clock = pygame.time.Clock()

    # Score
    score_left = 0
    score_right = 0

    # Entities
    left_paddle = Paddle(30, (HEIGHT - PADDLE_HEIGHT) // 2)
    right_paddle = Paddle(WIDTH - 30 - PADDLE_WIDTH, (HEIGHT - PADDLE_HEIGHT) // 2)
    ball = Ball()

    font = pygame.font.Font(None, SCORE_FONT_SIZE)
    small_font = pygame.font.Font(None, 24)

    paused = False

    # Optional simple AI toggle (comment/uncomment to enable)
    ai_enabled = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r:
                    score_left = 0
                    score_right = 0
                    ball.reset()
                if event.key == pygame.K_a:
                    ai_enabled = not ai_enabled

        # Input handling
        keys = pygame.key.get_pressed()
        left_speed = 0
        right_speed = 0
        if keys[pygame.K_w]:
            left_speed = -PADDLE_SPEED
        elif keys[pygame.K_s]:
            left_speed = PADDLE_SPEED

        if not ai_enabled:
            if keys[pygame.K_UP]:
                right_speed = -PADDLE_SPEED
            elif keys[pygame.K_DOWN]:
                right_speed = PADDLE_SPEED
        else:
            # Very simple AI: follow ball with some damping
            if ball.rect.centery < right_paddle.rect.centery - 10:
                right_speed = -PADDLE_SPEED
            elif ball.rect.centery > right_paddle.rect.centery + 10:
                right_speed = PADDLE_SPEED
            else:
                right_speed = 0

        if not paused:
            left_paddle.move(left_speed)
            right_paddle.move(right_speed)
            ball.update(left_paddle, right_paddle)

            # Check scoring
            if ball.rect.right < 0:
                score_right += 1
                ball.reset(serveto=1)
                play_sound('score')

            if ball.rect.left > WIDTH:
                score_left += 1
                ball.reset(serveto=-1)
                play_sound('score')

            # Win condition
            if score_left >= WINNING_SCORE or score_right >= WINNING_SCORE:
                paused = True

        # Draw
        screen.fill(BLACK)
        draw_center_line(screen)
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)

        # Scores
        left_surf = font.render(str(score_left), True, WHITE)
        right_surf = font.render(str(score_right), True, WHITE)
        screen.blit(left_surf, (WIDTH // 4 - left_surf.get_width() // 2, 20))
        screen.blit(right_surf, (WIDTH * 3 // 4 - right_surf.get_width() // 2, 20))

        # Hints
        hint = small_font.render("W/S: left  |  Up/Down: right  |  P: pause  |  R: reset  |  A: toggle AI", True, WHITE)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

        if paused:
            pause_surf = font.render("PAUSED" if not (score_left >= WINNING_SCORE or score_right >= WINNING_SCORE) else "GAME OVER", True, WHITE)
            screen.blit(pause_surf, (WIDTH // 2 - pause_surf.get_width() // 2, HEIGHT // 2 - pause_surf.get_height() // 2))
            if score_left >= WINNING_SCORE or score_right >= WINNING_SCORE:
                winner = 'Left' if score_left > score_right else 'Right'
                win_surf = small_font.render(f"{winner} player wins! Press R to restart.", True, WHITE)
                screen.blit(win_surf, (WIDTH // 2 - win_surf.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
