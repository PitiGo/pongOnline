import socket
import threading
import pickle
import time

class PongServer:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.FPS = 60
        # Initialize the game state with default values
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
        self.clients = []  # List to maintain client connections
        self.player_assignment = {}  # Dictionary to assign each client a player number
        self.lock = threading.Lock()  # Lock for thread synchronization

    def move_ball(self):
        """ Moves the ball and checks for collisions. """
        self.game_state['ball_x'] += self.game_state['ball_dx']
        self.game_state['ball_y'] += self.game_state['ball_dy']

        # Check for collisions with the top and bottom of the screen
        if self.game_state['ball_y'] > self.HEIGHT - 20 or self.game_state['ball_y'] < 0:
            self.game_state['ball_dy'] *= -1

        # Check for collisions with the left paddle
        if self.game_state['ball_x'] < 25 and self.game_state['paddle1_y'] < self.game_state['ball_y'] < self.game_state['paddle1_y'] + 100:
            self.game_state['ball_dx'] *= -1

        # Check for collisions with the right paddle
        if self.game_state['ball_x'] > self.WIDTH - 45 and self.game_state['paddle2_y'] < self.game_state['ball_y'] < self.game_state['paddle2_y'] + 100:
            self.game_state['ball_dx'] *= -1

        # Check if player 2 scores
        if self.game_state['ball_x'] < 0:
            self.game_state['score2'] += 1
            self.reset_ball()

        # Check if player 1 scores
        if self.game_state['ball_x'] > self.WIDTH:
            self.game_state['score1'] += 1
            self.reset_ball()

    def reset_ball(self):
        """ Resets the ball to the center of the screen. """
        self.game_state['ball_x'] = self.WIDTH // 2
        self.game_state['ball_y'] = self.HEIGHT // 2
        self.game_state['ball_dx'] *= -1

    def update_game_state(self, data, player_number):
        """
        Updates the game state based on the action received from a client.
        """
        try:
            action = pickle.loads(data)
            print(f"Action received: {action} from player {player_number}")

            # Update paddle position based on the action
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
            print(f"Error in deserializing data: {e}")

    def client_thread(self, conn, addr):
        """ Handles a client connection in a separate thread. """
        print(f"Connection established with: {addr}")

        with self.lock:
            self.clients.append(conn)
            # Assign player 1 or 2 depending on the order of connection
            self.player_assignment[conn] = 1 if len(self.player_assignment) == 0 else 2

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"Client disconnected: {addr}")
                    break

                with self.lock:
                    player_number = self.player_assignment[conn]
                    self.update_game_state(data, player_number)

            except Exception as e:
                print(f"Error in connection with {addr}: {e}")
                break

        with self.lock:
            self.clients.remove(conn)
            del self.player_assignment[conn]
            conn.close()

    def game_loop(self):
        """ Runs the main game loop in a separate thread. """
        while True:
            with self.lock:
                self.move_ball()
                state_to_send = pickle.dumps(self.game_state)
                for client in self.clients:
                    try:
                        client.sendall(state_to_send)
                    except Exception as e:
                        print(f"Error sending game state: {e}")
            time.sleep(1 / self.FPS)  # Sleep to maintain the game speed

    def start_server(self):
        """ Starts the server and waits for client connections. """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', 5555))
        server.listen()
        print("Server started, waiting for connections...")

        game_thread = threading.Thread(target=self.game_loop)
        game_thread.start()

        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.client_thread, args=(conn, addr)).start()

if __name__ == "__main__":
    pong_server = PongServer()
    pong_server.start_server()
