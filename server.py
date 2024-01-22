import socket
import pickle
from _thread import *

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8080


# store current Player instance of each player
players_dict = {}


LIMIT = 10
def handle_connection(conn, addr, connection_id):
    cnt = 0
    while cnt < LIMIT:
        try:
            data = conn.recv(2048)
            if data:
                players_dict[connection_id] = pickle.loads(data)
                players_list = [players_dict[id] for id in connections if id in players_dict]
                conn.send(pickle.dumps(players_list))
                cnt = 0
            else:
                cnt += 1
        except:
            break

    conn.close()
    connections.remove(connection_id)
    if connection_id in players_dict:
        del players_dict[connection_id]
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