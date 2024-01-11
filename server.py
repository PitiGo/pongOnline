import socket
import threading
import pickle
import time

class PongServer:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.FPS=60
        self.game_state = {
            'ball_x': self.WIDTH // 2,
            'ball_y': self.HEIGHT // 2,
            'ball_dx': 3,
            'ball_dy': 3,
            'paddle1_y': self.HEIGHT // 2,
            'paddle2_y': self.HEIGHT // 2,
            'score1': 0,
            'score2': 0
        }
        self.clients = []
        self.player_assignment = {}
        self.lock = threading.Lock()

    def move_ball(self):
        """ Mueve la pelota y verifica colisiones. """
        self.game_state['ball_x'] += self.game_state['ball_dx']
        self.game_state['ball_y'] += self.game_state['ball_dy']

        # Colisión con la parte superior e inferior
        if self.game_state['ball_y'] > self.HEIGHT - 20 or self.game_state['ball_y'] < 0:
            self.game_state['ball_dy'] *= -1

        # Colisión con la paleta izquierda
        if self.game_state['ball_x'] < 25 and self.game_state['paddle1_y'] < self.game_state['ball_y'] < self.game_state['paddle1_y'] + 100:
            self.game_state['ball_dx'] *= -1

        # Colisión con la paleta derecha
        if self.game_state['ball_x'] > self.WIDTH - 45 and self.game_state['paddle2_y'] < self.game_state['ball_y'] < self.game_state['paddle2_y'] + 100:
            self.game_state['ball_dx'] *= -1

        # Punto marcado por el jugador 2
        if self.game_state['ball_x'] < 0:
            self.game_state['score2'] += 1
            self.reset_ball()

        # Punto marcado por el jugador 1
        if self.game_state['ball_x'] > self.WIDTH:
            self.game_state['score1'] += 1
            self.reset_ball()


    def reset_ball(self):
        """ Restablece la posición de la pelota. """
        self.game_state['ball_x'] = self.WIDTH // 2
        self.game_state['ball_y'] = self.HEIGHT // 2
        self.game_state['ball_dx'] *= -1

    def update_game_state(self, data, player_number):
        """
        Actualiza el estado del juego basado en los datos recibidos del cliente.
        """
        try:
            action = pickle.loads(data)
            print(f"Acción recibida: {action} de jugador {player_number}")

            # Movimiento de la paleta
            if player_number == 1:
                if action['action'] == 'move_up' and self.game_state['paddle1_y'] > 0:
                    self.game_state['paddle1_y'] -= 10
                elif action['action'] == 'move_down' and self.game_state['paddle1_y'] < self.HEIGHT - 100:
                    self.game_state['paddle1_y'] += 10

            elif player_number == 2:
                if action['action'] == 'move_up' and self.game_state['paddle2_y'] > 0:
                    self.game_state['paddle2_y'] -= 10
                elif action['action'] == 'move_down' and self.game_state['paddle2_y'] < self.HEIGHT - 100:
                    self.game_state['paddle2_y'] += 10

        except Exception as e:
            print(f"Error al deserializar los datos: {e}")

    def client_thread(self, conn, addr):
        """ Gestiona la conexión de un cliente. """
        print(f"Conexión establecida con: {addr}")

        with self.lock:
            self.clients.append(conn)
            # Asignar jugador 1 o 2 dependiendo del orden de conexión
            self.player_assignment[conn] = 1 if len(self.player_assignment) == 0 else 2

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"Desconexión del cliente: {addr}")
                    break

                with self.lock:
                    player_number = self.player_assignment[conn]
                    self.update_game_state(data, player_number)

            except Exception as e:
                print(f"Error en la conexión con {addr}: {e}")
                break

        with self.lock:
            self.clients.remove(conn)
            del self.player_assignment[conn]
            conn.close()

    def game_loop(self):
        """ Bucle principal del juego que se ejecuta en un hilo separado. """
        while True:
            with self.lock:
                self.move_ball()
                state_to_send = pickle.dumps(self.game_state)
                for client in self.clients:
                    try:
                        client.sendall(state_to_send)
                    except Exception as e:
                        print(f"Error al enviar estado del juego: {e}")
            time.sleep(1 / self.FPS)  # Aproximadamente 60FPS

    def start_server(self):
        """ Inicia el servidor y acepta conexiones. """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 5555))
        server.listen()
        print("Servidor iniciado, esperando conexiones...")

        game_thread = threading.Thread(target=self.game_loop)
        game_thread.start()

        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.client_thread, args=(conn, addr)).start()

if __name__ == "__main__":
    pong_server = PongServer()
    pong_server.start_server()
