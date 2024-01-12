import pygame
import sys

# Initialize Pygame and create the game window
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Local")

# Color definitions and font for score display
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 36)  # Font to display the score

# Game state initialization
game_state = {
    'ball_x': WIDTH // 2,
    'ball_y': HEIGHT // 2,
    'ball_dx': 3,
    'ball_dy': 3,
    'paddle1_y': HEIGHT // 2,
    'paddle2_y': HEIGHT // 2,
    'score1': 0,
    'score2': 0
}

def move_ball():
    """ Moves the ball and checks for collisions. """
    # Update ball position
    game_state['ball_x'] += game_state['ball_dx']
    game_state['ball_y'] += game_state['ball_dy']

    # Collision with top and bottom
    if game_state['ball_y'] <= 0 or game_state['ball_y'] >= HEIGHT - 20:
        game_state['ball_dy'] = -game_state['ball_dy']

    # Collision with paddles
    if game_state['ball_x'] <= 10 and game_state['paddle1_y'] < game_state['ball_y'] < game_state['paddle1_y'] + 100:
        game_state['ball_dx'] = -game_state['ball_dx']
    elif game_state['ball_x'] >= WIDTH - 30 and game_state['paddle2_y'] < game_state['ball_y'] < game_state['paddle2_y'] + 100:
        game_state['ball_dx'] = -game_state['ball_dx']

    # Scoring
    if game_state['ball_x'] <= 0:
        game_state['score2'] += 1
        reset_ball()
    elif game_state['ball_x'] >= WIDTH:
        game_state['score1'] += 1
        reset_ball()

def reset_ball():
    """ Resets the ball to the center of the screen with a random direction. """
    game_state['ball_x'] = WIDTH // 2
    game_state['ball_y'] = HEIGHT // 2
    game_state['ball_dx'] = -game_state['ball_dx']


def draw_ball(screen, x, y):
    """ Draw the ball on the screen. """
    pygame.draw.rect(screen, RED, (x, y, 20, 20))

def draw_paddle(screen, x, y):
    """ Draw a paddle on the screen. """
    pygame.draw.rect(screen, GREEN, (x, y, 10, 100))

def draw_score(screen, score1, score2):
    """ Draw the score on the screen. """
    score_text = font.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

def handle_input():
    """ Handles keyboard input for both players. """
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and game_state['paddle1_y'] > 0:
        game_state['paddle1_y'] -= 10
    if keys[pygame.K_s] and game_state['paddle1_y'] < HEIGHT - 100:
        game_state['paddle1_y'] += 10
    if keys[pygame.K_UP] and game_state['paddle2_y'] > 0:
        game_state['paddle2_y'] -= 10
    if keys[pygame.K_DOWN] and game_state['paddle2_y'] < HEIGHT - 100:
        game_state['paddle2_y'] += 10

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    handle_input()  # Handle player inputs

    move_ball()  # Move the ball and check for collisions

    # Draw game elements
    screen.fill(BLACK)
    draw_ball(screen, game_state['ball_x'], game_state['ball_y'])
    draw_paddle(screen, 10, game_state['paddle1_y'])
    draw_paddle(screen, WIDTH - 20, game_state['paddle2_y'])
    draw_score(screen, game_state['score1'], game_state['score2'])

    pygame.display.flip()
    pygame.time.Clock().tick(60)  # 60 FPS for smoother gameplay
