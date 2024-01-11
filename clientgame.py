import pygame
import sys
import socket
import pickle
import select

# Initialize Pygame and create the game window
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Online")

# Color definitions and font for score display
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 36)  # Font to display the score

# Network client configuration
server_address = ('localhost', 5555)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setblocking(False)  # Set the socket to non-blocking
try:
    client_socket.connect(server_address)
except BlockingIOError:
    # Expected due to non-blocking socket on connection
    pass
except socket.error as e:
    print(f"Could not connect to server: {e}")
    sys.exit()

def send_data_to_server(socket, data):
    """ Send data to the server. """
    try:
        socket.sendall(pickle.dumps(data))
    except (OSError, BrokenPipeError) as e:
        print(f"Error sending data to server: {e}")

def get_game_state(socket):
    """ Receive the game state from the server. """
    try:
        ready = select.select([socket], [], [], 0.1)  # Wait up to 0.1 seconds for data
        if ready[0]:
            data = socket.recv(2048)
            if data:
                try:
                    return pickle.loads(data)
                except pickle.UnpicklingError:
                    print("Error in data deserialization.")
                    return None
        return None
    except OSError as e:
        print(f"Error receiving data from server: {e}")
        return None

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

# Main client loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Handle user input
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP]:
        send_data_to_server(client_socket, {'action': 'move_up', 'player': 1})
    if keys[pygame.K_DOWN]:
        send_data_to_server(client_socket, {'action': 'move_down', 'player': 1})

    # Receive the game state from the server
    game_state = get_game_state(client_socket)

    # Draw game elements
    screen.fill(BLACK)
    if game_state:
        if all(key in game_state for key in ['ball_x', 'ball_y', 'paddle1_y', 'paddle2_y', 'score1', 'score2']):
            draw_ball(screen, game_state['ball_x'], game_state['ball_y'])
            draw_paddle(screen, 10, game_state['paddle1_y'])
            draw_paddle(screen, WIDTH - 20, game_state['paddle2_y'])
            draw_score(screen, game_state['score1'], game_state['score2'])

    pygame.display.flip()
    pygame.time.Clock().tick(60)  # 60 FPS for smoother gameplay
