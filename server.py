import socket
import pickle
import time
from _thread import *

from _class.Tower import Tower

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8080


# game logic
HIT_COOLDOWN = 3 # seconds
HIT_RADIUS = 60 # pixels
HIT_DAMAGE = 10
last_hit_time = time.time()

# store current Player instance of each player
players_dict = {}
towers_list = [
    Tower(x=250, y=250, damage=10, cooldown=3, radius=150, team='red', last_shoot_time=0)
]


def distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2) ** 0.5


LIMIT = 10
def handle_connection(conn, addr, connection_id):
    cnt = 0
    while cnt < LIMIT:
        try:
            data = conn.recv(2048)
            if data:
                me = pickle.loads(data)
                if connection_id not in players_dict:
                    players_dict[connection_id] = me
                else:
                    players_dict[connection_id].x = me.x
                    players_dict[connection_id].y = me.y
                    players_dict[connection_id].is_hit = me.is_hit


                ##  GAME LOGIC
                # 1. player hit player
                global last_hit_time
                if (players_dict[connection_id].is_hit) and (time.time() - last_hit_time >= HIT_COOLDOWN):
                    last_hit_time = time.time() # start skill cooldown
                    for k, player in players_dict.items():
                        if k != connection_id:
                            dist = distance(me.x+30, me.y+30, player.x+30, player.y+30) # 30 is half of character size (to move x,y to center of character)
                            if dist <= HIT_RADIUS:
                                player.hp -= HIT_DAMAGE

                # 2. tower shoot player
                for tower in towers_list:
                    dist = distance(tower.x, tower.y, me.x, me.y)
                    time_pass = time.time() - tower.last_shoot_time
                    # reset tower animation flag after 0.5 sec
                    if time_pass >= 0.5:
                        tower.is_shoot = False
                    if (dist <= tower.radius) and (time_pass >= tower.cooldown):
                        tower.shoot((me.x+30, me.y+30))
                        tower.last_shoot_time = time.time()
                        players_dict[connection_id].hp -= tower.damage


                players_list = [players_dict[id] for id in connections if (id in players_dict) and (id != connection_id)]
                conn.send(pickle.dumps([players_dict[connection_id], players_list, towers_list]))
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