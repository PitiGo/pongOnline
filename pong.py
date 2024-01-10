import pygame
import sys

# Inicializar Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 600
BALL_SPEED = [5, 5]
PADDLE_SPEED = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Configurar la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Funciones para dibujar la pelota y las paletas
def draw_ball(screen, x, y):
    pygame.draw.rect(screen, WHITE, (x, y, 20, 20))

def draw_paddle(screen, x, y):
    pygame.draw.rect(screen, WHITE, (x, y, 10, 100))

# Posiciones iniciales
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
paddle1_y, paddle2_y = HEIGHT // 2 - 50, HEIGHT // 2 - 50

# Bucle principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Movimiento de las paletas
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle1_y > 0:
        paddle1_y -= PADDLE_SPEED
    if keys[pygame.K_s] and paddle1_y < HEIGHT - 100:
        paddle1_y += PADDLE_SPEED
    if keys[pygame.K_UP] and paddle2_y > 0:
        paddle2_y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and paddle2_y < HEIGHT - 100:
        paddle2_y += PADDLE_SPEED

    # Movimiento de la pelota
    ball_x += BALL_SPEED[0]
    ball_y += BALL_SPEED[1]

    # Colisiones con la pared
    if ball_y <= 0 or ball_y >= HEIGHT - 20:
        BALL_SPEED[1] = -BALL_SPEED[1]
    
    # Colisiones con las paletas
    if ball_x <= 10 and paddle1_y <= ball_y <= paddle1_y + 100 or ball_x >= WIDTH - 30 and paddle2_y <= ball_y <= paddle2_y + 100:
        BALL_SPEED[0] = -BALL_SPEED[0]

    # Redibujar los elementos en la ventana
    screen.fill(BLACK)
    draw_ball(screen, ball_x, ball_y)
    draw_paddle(screen, 10, paddle1_y)
    draw_paddle(screen, WIDTH - 20, paddle2_y)

    pygame.display.flip()
    pygame.time.Clock().tick(60)  # 60 FPS
