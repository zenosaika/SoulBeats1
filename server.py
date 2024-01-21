import socket
import pickle
from _thread import *

SERVER_IP = 'localhost'
SERVER_PORT = 8888


# store current Player instance of each player
players_dict = {}


def handle_connection(conn, addr, connection_id):
    while True:
        try:
            data = conn.recv(2048)
            if data:
                players_dict[connection_id] = pickle.loads(data)
                players_list = [players_dict[id] for id in connections if id in players_dict]
                conn.send(pickle.dumps(players_list))
        except:
            break

    conn.close()
    connections.remove(connection_id)
    print(f'{addr} disconnected.')


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((SERVER_IP, SERVER_PORT))
server.listen(2)
print('Server started!')

connections = [] # store connection id
current_connection_id = 0

while True:
    conn, addr = server.accept()
    connections.append(current_connection_id)
    print(f'{addr} joined the server!')
    start_new_thread(handle_connection, (conn, addr, current_connection_id))
    current_connection_id += 1