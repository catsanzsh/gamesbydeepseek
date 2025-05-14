import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vibe Breakout")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

# Game objects
paddle_width = 80
paddle_height = 15
paddle_x = (WIDTH - paddle_width) // 2
paddle_y = HEIGHT - 40

ball_size = 15
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = 5 * random.choice([-1, 1])
ball_dy = -5

brick_width = 55
brick_height = 20
bricks = []

# Create bricks
for row in range(7):
    for col in range(10):
        brick_color = random.choice(COLORS)
        brick_x = col * (brick_width + 5) + 5
        brick_y = row * (brick_height + 5) + 50
        bricks.append(pygame.Rect(brick_x, brick_y, brick_width, brick_height))

score = 0

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill((0, 0, 0))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Paddle movement
    mouse_x = pygame.mouse.get_pos()[0]
    paddle_x = mouse_x - paddle_width // 2
    paddle_x = max(0, min(paddle_x, WIDTH - paddle_width))
    
    # Ball movement
    ball_x += ball_dx
    ball_y += ball_dy
    
    # Ball collisions
    if ball_x <= 0 or ball_x >= WIDTH - ball_size:
        ball_dx *= -1
    if ball_y <= 0:
        ball_dy *= -1
        
    # Paddle collision
    paddle_rect = pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)
    ball_rect = pygame.Rect(ball_x, ball_y, ball_size, ball_size)
    
    if ball_rect.colliderect(paddle_rect):
        ball_dy *= -1
        # Add some angle variation based on hit position
        hit_pos = (ball_x - paddle_x) / paddle_width
        ball_dx = 5 * (hit_pos - 0.5) * 2
    
    # Brick collisions
    for brick in bricks[:]:
        if ball_rect.colliderect(brick):
            bricks.remove(brick)
            ball_dy *= -1
            score += 10
            ball_y += ball_dy  # Prevent sticking
    
    # Reset if ball goes out
    if ball_y > HEIGHT:
        # Reset game
        ball_x = WIDTH // 2
        ball_y = HEIGHT // 2
        ball_dx = 5 * random.choice([-1, 1])
        ball_dy = -5
        score = 0
        # Rebuild bricks
        bricks = []
        for row in range(7):
            for col in range(10):
                brick_color = random.choice(COLORS)
                brick_x = col * (brick_width + 5) + 5
                brick_y = row * (brick_height + 5) + 50
                bricks.append(pygame.Rect(brick_x, brick_y, brick_width, brick_height))
    
    # Drawing
    # Draw bricks
    for i, brick in enumerate(bricks):
        pygame.draw.rect(screen, COLORS[i % len(COLORS)], brick)
    
    # Draw paddle
    pygame.draw.rect(screen, BLUE, (paddle_x, paddle_y, paddle_width, paddle_height))
    
    # Draw ball
    pygame.draw.ellipse(screen, RED, (ball_x, ball_y, ball_size, ball_size))
    
    # Draw score
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))
    
    # Win condition
    if not bricks:
        text = font.render("YOU WIN!", True, GREEN)
        screen.blit(text, (WIDTH//2 - 60, HEIGHT//2))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
