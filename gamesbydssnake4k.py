import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 600
HEIGHT = 400
BLOCK_SIZE = 20
FPS = 60  # Changed to 60 FPS
UPDATE_INTERVAL = 100  # Milliseconds between updates (controls game speed)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Initialize audio mixer
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Sound generation functions
def generate_beep(frequency, duration):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray(n_samples * 2)
    
    for i in range(n_samples):
        t = i / sample_rate
        wave = int(32767 * (1 if (t * frequency % 1.0 < 0.5) else -1))
        buf[2*i] = wave & 0xff
        buf[2*i+1] = (wave >> 8) & 0xff
    
    return pygame.mixer.Sound(buffer=bytes(buf))

# Game sounds
eat_sound = generate_beep(880, 0.1)
game_over_sound = generate_beep(220, 0.5)

# Clock for controlling speed
clock = pygame.time.Clock()

# Initialize snake
snake = [[WIDTH//2, HEIGHT//2]]
snake_direction = 'RIGHT'
change_to = snake_direction

# Food
food = [
    random.randrange(1, (WIDTH//BLOCK_SIZE)) * BLOCK_SIZE,
    random.randrange(1, (HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE
]

# Score
score = 0

# Game over flag
game_over = False

# Timing variables
last_update = pygame.time.get_ticks()

# Font for score display
font = pygame.font.SysFont('arial', 20)

def show_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def game_over_screen():
    screen.fill(BLACK)
    go_text = font.render(f"Game Over! Score: {score}", True, RED)
    screen.blit(go_text, (WIDTH//2 - 100, HEIGHT//2 - 20))
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    sys.exit()

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_direction != 'DOWN':
                change_to = 'UP'
            if event.key == pygame.K_DOWN and snake_direction != 'UP':
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT and snake_direction != 'RIGHT':
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT and snake_direction != 'LEFT':
                change_to = 'RIGHT'

    # Game logic updates at fixed interval
    now = pygame.time.get_ticks()
    if now - last_update > UPDATE_INTERVAL:
        last_update = now
        
        # Update direction
        snake_direction = change_to

        # Move snake
        new_head = [snake[0][0], snake[0][1]]
        if snake_direction == 'UP':
            new_head[1] -= BLOCK_SIZE
        if snake_direction == 'DOWN':
            new_head[1] += BLOCK_SIZE
        if snake_direction == 'LEFT':
            new_head[0] -= BLOCK_SIZE
        if snake_direction == 'RIGHT':
            new_head[0] += BLOCK_SIZE

        # Check collisions
        if (new_head[0] >= WIDTH or new_head[0] < 0 or
            new_head[1] >= HEIGHT or new_head[1] < 0):
            game_over = True

        if new_head in snake:
            game_over = True

        if game_over:
            game_over_sound.play()
            game_over_screen()

        # Update snake position
        snake.insert(0, new_head)

        # Food consumption
        if snake[0] == food:
            score += 1
            eat_sound.play()
            food = [
                random.randrange(1, (WIDTH//BLOCK_SIZE)) * BLOCK_SIZE,
                random.randrange(1, (HEIGHT//BLOCK_SIZE)) * BLOCK_SIZE
            ]
        else:
            snake.pop()

    # Always render at 60 FPS
    screen.fill(BLACK)
    
    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, pygame.Rect(
            segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))
    
    # Draw food
    pygame.draw.rect(screen, RED, pygame.Rect(
        food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))
    
    show_score()
    pygame.display.update()
    clock.tick(FPS)  # Maintain 60 FPS rendering
