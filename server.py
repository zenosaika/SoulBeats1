import socket
import pickle
import random
import time
from _thread import start_new_thread

from _class.Tower import Tower

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8080

# Server States
connections = {}
rooms = {}

# Skills
skills = {
    1: {
        'damage': 20,
        'radius': 50,
        'cooldown': 2,
    },
    2: {
        'damage': 20,
        'radius': 200,
        'cooldown': 5,
    },
    3: {
        'damage': 40,
        'radius': 100,
        'cooldown': 10,
    },
}

def create_towers():
    return {
        'center': Tower(320, 320, 40, 20, 120, 4, 'noteam', 'Small_Tower'),
    }

def create_room(conn, connection_id):
    # random 4-digit room_id
    room_id = random.randrange(1000, 10000)
    while room_id in rooms:
        room_id = random.randrange(1000, 10000)

    rooms[room_id] = {'players':{}, 'towers': create_towers()} # create new room
    connections[connection_id]['room_id'] = room_id # move this connection to the room

    # send room_id to client
    conn.send(pickle.dumps({
        'header': 'room_created',
        'body': {
            'room_id': room_id,
        }
    }))

def join_room(conn, connection_id, room_id):
    if room_id in rooms:
        connections[connection_id]['room_id'] = room_id # move this connection to the room
        conn.send(pickle.dumps({
            'header': 'join_success',
            'body': ''
        }))
    else:
        conn.send(pickle.dumps({
            'header': 'join_failed',
            'body': {'error': 'Invalid room id, try again.'}
        }))

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2) ** 0.5

def handle_skill(connection_id, players, towers):
    this_player = players[connection_id]
    timestamp_now = time.time()

    # Skill 1 : Soul Blade
    if (this_player.use_skill1 and
        timestamp_now - this_player.skill1_last_timestamp > skills[1]['cooldown']):
        this_player.skill1_last_timestamp = timestamp_now
        for k, v in players.items():
            if (k != connection_id and 
                distance(this_player.x, this_player.y, v.x, v.y) <= skills[1]['radius']):
                v.hp -= skills[1]['damage']
        for v in towers.values():
            if v.type != 'Destroyed_Tower':
                if distance(this_player.x, this_player.y, v.x, v.y) <= skills[1]['radius']:
                    v.hp -= skills[1]['damage']

    # Skill 2 : Soul Dash
    if (this_player.use_skill2 and
        timestamp_now - this_player.skill2_last_timestamp > skills[2]['cooldown']):
        this_player.skill2_last_timestamp = timestamp_now
        for k, v in players.items():
            if (k != connection_id and 
                distance(this_player.x, this_player.y, v.x, v.y) <= skills[2]['radius']):
                v.hp -= skills[2]['damage']
        for v in towers.values():
            if v.type != 'Destroyed_Tower':
                if distance(this_player.x, this_player.y, v.x, v.y) <= skills[2]['radius']:
                    v.hp -= skills[2]['damage']

    # Skill 3 : 
    if (this_player.use_skill3 and
        timestamp_now - this_player.skill3_last_timestamp > skills[3]['cooldown']):
        this_player.skill3_last_timestamp = timestamp_now
        for k, v in players.items():
            if (k != connection_id and 
                distance(this_player.x, this_player.y, v.x, v.y) <= skills[3]['radius']):
                v.hp -= skills[3]['damage']
        for v in towers.values():
            if v.type != 'Destroyed_Tower':
                if distance(this_player.x, this_player.y, v.x, v.y) <= skills[3]['radius']:
                    v.hp -= skills[3]['damage']

def tower_attack(connection_id, players, towers):
    this_player = players[connection_id]
    timestamp_now = time.time()

    for tower in towers.values():
        if tower.type != 'Destroyed_Tower':
            dist = distance(tower.x, tower.y, this_player.x, this_player.y)
            time_passed = timestamp_now - tower.last_shot_timestamp

            # reset 'is_shoot' flag after 0.5 sec
            if time_passed >= 0.5:
                tower.is_shoot = False

            # shoot to player
            if (dist <= tower.radius) and (time_passed > tower.cooldown):
                tower.shoot((this_player.x+30, this_player.y+30))
                tower.last_shot_timestamp = timestamp_now
                this_player.hp -= tower.damage

def handle_update_state(conn, connection_id, players, this_player, towers):
    # for first time
    if connection_id not in players:
        players[connection_id] = this_player

    # update this player state on server
    p = players[connection_id] # p is a Player object
    p.x = this_player.x
    p.y = this_player.y
    p.use_skill1 = this_player.use_skill1
    p.use_skill2 = this_player.use_skill2
    p.use_skill3 = this_player.use_skill3
    p.is_walk = this_player.is_walk
    p.walk_direction = this_player.walk_direction
    # update other states here!

    handle_skill(connection_id, players, towers)
    tower_attack(connection_id, players, towers)

    timestamp_now = time.time()

    # check if player is dead
    if not p.is_dead and p.hp <= 0:
        p.is_dead = True
        p.death_timestamp = timestamp_now

    # check if player is respawn
    if p.is_dead and timestamp_now - p.death_timestamp > p.respawn_cooldown:
        p.is_dead = False
        p.is_respawn = True
        p.hp = p.max_hp

    # check if tower is detroyed
    for t in towers.values():
        if t.hp <= 0:
            t.type = 'Destroyed_Tower'
    
    # send server states to client
    conn.send(pickle.dumps({
        'header': 'update_server_state',
        'body': {
            'me': p,
            'players': [v for k, v in players.items() if k!=connection_id],
            'towers': [v for v in towers.values()]
        }
    }))

    # reset flag
    p.is_respawn = False


def handle_packet(conn, packet, connection_id):
    header = packet['header']
    body = packet['body']

    if header == 'create_room':
        create_room(conn, connection_id)

    elif header == 'join_room':
        room_id = body['room_id']
        join_room(conn, connection_id, room_id)

    elif header == 'update_state':
        room_id = connections[connection_id]['room_id'] # get current room_id of this player 
        players = rooms[room_id]['players'] # dict of Player object of that room
        towers = rooms[room_id]['towers'] # dict of Player object of that room
        this_player = body['me']
        handle_update_state(conn, connection_id, players, this_player, towers)

def handle_connection(conn, addr, connection_id):
    while True:
        
        try:
            packet = conn.recv(2048) # return packet or null
            if packet:
                packet = pickle.loads(packet)
                handle_packet(conn, packet, connection_id) 
            else:
                break # client disconnected      
        except Exception as e:
            ...

    conn.close()
    print(f'{addr} disconnected.')

def main():
    # create TCP socket, bind port, and set to passive mode (listen)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SERVER_IP, SERVER_PORT))
    s.listen(2)
    print('server started.')
    
    connection_id = 0

    while True:
        conn, addr = s.accept()
        connections[connection_id] = {'conn': conn, 'addr': addr, 'room_id': -1}
        start_new_thread(handle_connection, (conn, addr, connection_id))
        print(f'{addr} joined the server.')
        connection_id += 1

main()