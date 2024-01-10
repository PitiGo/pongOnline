import socket
import threading
import pickle
import time

# Estado inicial del juego
game_state = {
    'ball_x': 50,
    'ball_y': 50,
    'ball_dx': 3,
    'ball_dy': 3,
    'paddle1_y': 50,
    'paddle2_y': 50,
    'score1': 0,
    'score2': 0
}

WIDTH, HEIGHT = 800, 600
# Lista para mantener las conexiones de los clientes
clients = []
# Diccionario para asignar a cada cliente un número de jugador
player_assignment = {}

# Bloquear para la sincronización de hilos
lock = threading.Lock()

def move_ball():
    """ Mueve la pelota y verifica colisiones. """
    game_state['ball_x'] += game_state['ball_dx']
    game_state['ball_y'] += game_state['ball_dy']

    # Colisión con la parte superior e inferior
    if game_state['ball_y'] > HEIGHT - 20 or game_state['ball_y'] < 0:
        game_state['ball_dy'] *= -1

    # Colisión con las paletas
    if (game_state['ball_x'] < 20 and game_state['paddle1_y'] < game_state['ball_y'] < game_state['paddle1_y'] + 100) or \
       (game_state['ball_x'] > WIDTH - 20 and game_state['paddle2_y'] < game_state['ball_y'] < game_state['paddle2_y'] + 100):
        game_state['ball_dx'] *= -1

    # Punto marcado por el jugador 2
    if game_state['ball_x'] < 0:
        game_state['score2'] += 1
        reset_ball()

    # Punto marcado por el jugador 1
    if game_state['ball_x'] > WIDTH:
        game_state['score1'] += 1
        reset_ball()

def reset_ball():
    """ Restablece la posición de la pelota. """
    game_state['ball_x'] = WIDTH // 2
    game_state['ball_y'] = HEIGHT // 2
    game_state['ball_dx'] *= -1

def update_game_state(data, player):
    """
    Actualiza el estado del juego basado en los datos recibidos del cliente.
    """
    try:
        action = pickle.loads(data)
        print(f"Acción recibida: {action} de {player}")

        # Movimiento de la paleta
        if action['player'] == 1:
            if action['action'] == 'move_up' and game_state['paddle1_y'] > 0:
                game_state['paddle1_y'] -= 10
            elif action['action'] == 'move_down' and game_state['paddle1_y'] < HEIGHT - 100:
                game_state['paddle1_y'] += 10

        elif action['player'] == 2:
            if action['action'] == 'move_up' and game_state['paddle2_y'] > 0:
                game_state['paddle2_y'] -= 10
            elif action['action'] == 'move_down' and game_state['paddle2_y'] < HEIGHT - 100:
                game_state['paddle2_y'] += 10

    except Exception as e:
        print(f"Error al deserializar los datos: {e}")

def client_thread(conn, addr):
    global game_state, clients, player_assignment
    print(f"Conexión establecida con: {addr}")

    with lock:
        clients.append(conn)
        # Asignar jugador 1 o 2 dependiendo del orden de conexión
        player_assignment[conn] = 1 if len(player_assignment) == 0 else 2

    while True:
        try:
            # Recibir datos del cliente
            data = conn.recv(1024)
            if not data:
                print(f"Desconexión del cliente: {addr}")
                break

            # Procesar y actualizar el estado del juego
            with lock:
                player_number = player_assignment[conn]
                update_game_state(data, player_number)

        except Exception as e:
            print(f"Error en la conexión con {addr}: {e}")
            break

    with lock:
        clients.remove(conn)
        del player_assignment[conn]
    conn.close()

def game_loop():
    """ Bucle principal del juego que se ejecuta en un hilo separado. """
    while True:
        with lock:
            move_ball()
            state_to_send = pickle.dumps(game_state)
            for client in clients:
                try:
                    client.sendall(state_to_send)
                except Exception as send_error:
                    print(f"Error al enviar estado del juego: {send_error}")
        time.sleep(0.016)  # Aproximadamente 60FPS

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen()
    print("Servidor iniciado, esperando conexiones...")

    # Iniciar el bucle del juego en un hilo separado
    game_thread = threading.Thread(target=game_loop)
    game_thread.start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=client_thread, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
