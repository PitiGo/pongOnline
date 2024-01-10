import pygame
import sys
import socket
import pickle
import select

# Inicializar Pygame y crear ventana
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Online")

# Colores y Fuente
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 36)  # Fuente para mostrar puntuación

# Configuración del cliente de red
server_address = ('localhost', 5555)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setblocking(False)  # Hacer el socket no bloqueante
try:
    client_socket.connect(server_address)
except BlockingIOError:
    # Se espera debido al socket no bloqueante en la conexión
    pass
except socket.error as e:
    print(f"No se pudo conectar al servidor: {e}")
    sys.exit()

def send_data_to_server(socket, data):
    try:
        socket.sendall(pickle.dumps(data))
    except (OSError, BrokenPipeError) as e:
        print(f"Error al enviar datos al servidor: {e}")

def get_game_state(socket):
    try:
        ready = select.select([socket], [], [], 0.1)
        if ready[0]:
            data = socket.recv(2048)
            if data:
                try:
                    return pickle.loads(data)
                except pickle.UnpicklingError:
                    print("Error en la deserialización de los datos.")
                    return None
        return None
    except OSError as e:
        print(f"Error al recibir datos del servidor: {e}")
        return None


def draw_ball(screen, x, y):
    pygame.draw.rect(screen, WHITE, (x, y, 20, 20))

def draw_paddle(screen, x, y):
    pygame.draw.rect(screen, WHITE, (x, y, 10, 100))

def draw_score(screen, score1, score2):
    score_text = font.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

# Bucle principal del cliente
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Manejar el input del usuario
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP]:
        send_data_to_server(client_socket, {'action': 'move_up', 'player': 1})
    if keys[pygame.K_DOWN]:
        send_data_to_server(client_socket, {'action': 'move_down', 'player': 1})

    # Recibir el estado del juego del servidor
    game_state = get_game_state(client_socket)

    # Dibujar elementos del juego
    screen.fill(BLACK)
    if game_state:
        if all(key in game_state for key in ['ball_x', 'ball_y', 'paddle1_y', 'paddle2_y', 'score1', 'score2']):
            draw_ball(screen, game_state['ball_x'], game_state['ball_y'])
            draw_paddle(screen, 10, game_state['paddle1_y'])
            draw_paddle(screen, WIDTH - 20, game_state['paddle2_y'])
            draw_score(screen, game_state['score1'], game_state['score2'])

    pygame.display.flip()
    pygame.time.Clock().tick(60)  # 60 FPS

