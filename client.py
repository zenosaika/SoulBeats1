import socket
import pickle
import pygame
import time
import math
from _thread import start_new_thread

from _class.Player import Player


SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

# Game Config
FPS = 60
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700

# Global Variables
room_joined = False
players = [] # store Player objects
towers = [] # store Tower objects
me = Player(x=15, y=15, character='Heron')

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


def load_image(path, resize_to=(-1, -1)):
    image = pygame.image.load(path)
    if resize_to != (-1, -1):
        image = pygame.transform.scale(image, resize_to)
    return image

images = {
    'Map': load_image('_asset/map.png', resize_to=(WINDOW_WIDTH, WINDOW_HEIGHT)),
}

def image_at(sheet, rectangle, resize_to, colorkey=None):
    # loads image from x, y, x+offset, y+offset
    rect = pygame.Rect(rectangle)
    image = pygame.Surface(rect.size)
    image.blit(sheet, (0, 0), rect)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)

    if resize_to != (-1, -1):
        image = pygame.transform.scale(image, resize_to)

    return image

def images_at(sheet, rects, resize_to, colorkey=None):
    # loads multiple images, supply a list of coordinates
    return [image_at(sheet, rect, resize_to, colorkey) for rect in rects]

def get_sprite_rects(y_start, num_of_col, col_width, row_height):
    return [(col*col_width, y_start, col_width, row_height) for col in range(num_of_col)]

animations = {
    'walk_top': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/king_frost.png'),
            rects=get_sprite_rects(514, 9, 64, 64),
            resize_to=(80, 80),
            colorkey=-1
        )
    },
    'walk_left': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/king_frost.png'),
            rects=get_sprite_rects(578, 9, 64, 64),
            resize_to=(80, 80),
            colorkey=-1
        )
    },
    'walk_bottom': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/king_frost.png'),
            rects=get_sprite_rects(643, 9, 64, 64),
            resize_to=(80, 80),
            colorkey=-1
        )
    },
    'walk_right': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/king_frost.png'),
            rects=get_sprite_rects(707, 9, 64, 64),
            resize_to=(80, 80),
            colorkey=-1
        )
    },
    'magic_wand': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/king_frost.png'),
            rects=get_sprite_rects(1792, 23, 64, 84)[1::3],
            resize_to=(80, 105),
            colorkey=-1
        )
    },
    'skill1': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/skill1.png'),
            rects=get_sprite_rects(0, 10, 26, 26),
            resize_to=(120, 120),
            colorkey=-1
        )
    },
    'skill2': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/skill2.png'),
            rects=get_sprite_rects(0, 10, 41, 41),
            resize_to=(150, 150),
            colorkey=-1
        )
    },
    'skill3': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/skill3.png'),
            rects=get_sprite_rects(0, 10, 58, 58),
            resize_to=(200, 200),
            colorkey=-1
        )
    },
    'megia_stand': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/megia.png'),
            rects=get_sprite_rects(128, 7, 64, 64),
            resize_to=(80, 80),
            colorkey=-1
        )
    },
    'megia_attack': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/megia.png'),
            rects=get_sprite_rects(1792, 23, 64, 64)[1::3],
            resize_to=(80, 80),
            colorkey=-1
        )
    },
    'megia_skill': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/megia_skill.png'),
            rects=get_sprite_rects(0, 10, 41, 41),
            resize_to=(240, 240),
            colorkey=-1
        )
    },
    'megia_dead': {
        'frame_cnt': 0,
        'images': images_at(
            sheet=load_image('_asset/megia.png'),
            rects=get_sprite_rects(1281, 6, 64, 64),
            resize_to=(80, 80),
            colorkey=-1
        )
    },
}

def play_animation(animation_name, duration):
    ani = animations[animation_name]
    duration_per_frame = 1 / FPS # seconds
    duration_per_image = duration / len(ani['images']) # seconds
    frame_per_image = duration_per_image / duration_per_frame

    if math.floor(ani['frame_cnt']/frame_per_image) >= len(ani['images']):
        ani['frame_cnt'] = 0

    image_at_this_frame = ani['images'][math.floor(ani['frame_cnt']/frame_per_image)] 
    ani['frame_cnt'] += 1

    return image_at_this_frame

def handle_packet(packet):
    global me, players, towers, room_joined
    header = packet['header']
    body = packet['body']

    if header == 'room_created':
        room_joined = True
        print('[ROOM]: Welcome!')
        print(f'[ROOM]: This room id is {body["room_id"]}')

    elif header == 'join_success':
        room_joined = True
        print('[ROOM]: Welcome!')

    elif header == 'join_failed':
        print(f'[SERVER]: {body["error"]}')

    elif header == 'update_server_state':
        players = body['players']
        towers = body['towers']
        me_tmp = body['me']

        timestamp_now = time.time()

        # update me here!
        me.hp = me_tmp.hp
        me.is_dead = me_tmp.is_dead
        me.is_respawn = me_tmp.is_respawn
        me.skill1_last_timestamp = me_tmp.skill1_last_timestamp
        me.skill2_last_timestamp = me_tmp.skill2_last_timestamp
        me.skill3_last_timestamp = me_tmp.skill3_last_timestamp

        # reset flag
        if timestamp_now - me.skill1_last_timestamp > 0.7:
            me.use_skill1 = False
        if timestamp_now - me.skill2_last_timestamp > 0.7:
            me.use_skill2 = False
        if timestamp_now - me.skill3_last_timestamp > 0.7:
            me.use_skill3 = False

def handle_connection(s, mode, room_id=-1):
    if mode == 'update_state':
        s.send(pickle.dumps({
            'header': 'update_state',
            'body': {
                'me': me
            }
        }))
    
    elif mode == 'create_room':
        s.send(pickle.dumps({
            'header': 'create_room',
            'body': ''
        }))

    elif mode == 'join_room':
        s.send(pickle.dumps({
            'header': 'join_room',
            'body': {'room_id': room_id}
        }))

    try:
        packet = s.recv(2048) # return packet or null
        if packet:
            packet = pickle.loads(packet)
            handle_packet(packet)
    except Exception as e:
        ...

def draw_hp(screen, object, pos):
    x, y = pos
    hp_width = 70
    hp_height = 10
    pygame.draw.rect(screen, color=(100, 100, 100), rect=(x, y, hp_width, hp_height))
    pygame.draw.rect(screen, color=(255, 0, 0), rect=(x, y-1, hp_width*(object.hp/object.max_hp), hp_height-2))

def render_player(screen, p):
    if p.use_skill1 or p.use_skill2 or p.use_skill3:
        # animate procedural orb first
        if p.use_skill1:
            screen.blit(play_animation('skill1', 0.7), (p.x-18, p.y))
        if p.use_skill2:
            screen.blit(play_animation('skill2', 0.7), (p.x-33, p.y))
        if p.use_skill3:
            screen.blit(play_animation('skill3', 0.7), (p.x-60, p.y-30))
        # then animate character and his wand
        screen.blit(play_animation('magic_wand', 0.7), (p.x, p.y))
    elif p.is_walk:
        screen.blit(play_animation(f'walk_{p.walk_direction}', 1.5), (p.x, p.y))
    else:
        screen.blit(animations[f'walk_{p.walk_direction}']['images'][0], (p.x, p.y))
    draw_hp(screen, p, pos=(p.x+7, p.y-10))

def render_tower(screen, t):
    if t.type != 'Destroyed_Tower':
        screen.blit(play_animation('megia_stand', 2), (t.x, t.y))
        draw_hp(screen, t, pos=(t.x+7, t.y-10))
        
        if t.is_shoot:
            screen.blit(play_animation('megia_skill', 0.7), (t.x-75, t.y-40))
            screen.blit(play_animation('megia_attack', 0.7), (t.x, t.y))
    else:
        screen.blit(animations['megia_dead']['images'][4], (t.x, t.y)) 

def update_display(screen):
    # render map
    screen.blit(images['Map'], (0, 0))

    # render me
    render_player(screen, me)

    # render other players
    for p in players:
        render_player(screen, p)
    
    # render towers
    for t in towers:
        render_tower(screen, t)

    pygame.display.update()

def handle_move():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        me.move_to(me.x, me.y-me.velocity)
        me.is_walk = True
        me.walk_direction = 'top'
    elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
        me.move_to(me.x-me.velocity, me.y)
        me.is_walk = True
        me.walk_direction = 'left'
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        me.move_to(me.x, me.y+me.velocity)
        me.is_walk = True
        me.walk_direction = 'bottom'
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        me.move_to(me.x+me.velocity, me.y)
        me.is_walk = True
        me.walk_direction = 'right'
    else:
        me.is_walk = False

def dead():
    # move player to outside the map
    me.x = me.y = -500

def respawn():
    # move player back to the map
    me.x = me.y = 15

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2) ** 0.5

def handle_skill():
    timestamp_now = time.time()
    keys = pygame.key.get_pressed()

    # Skill 1 : Soul Blade
    if keys[pygame.K_SPACE] and timestamp_now - me.skill1_last_timestamp > skills[1]['cooldown']:
        me.skill1_last_timestamp = timestamp_now
        me.skill1()

    # Skill 2 : Soul Dash
    elif keys[pygame.K_e] and timestamp_now - me.skill2_last_timestamp > skills[2]['cooldown']:
        me.skill1_last_timestamp = timestamp_now
        target_object = me
        min_distance = 999999

        for p in players:
            dist = distance(me.x, me.y, p.x, p.y)
            if dist <= skills[2]['radius'] and dist < min_distance:
                min_distance = dist
                target_object = p
        
        for t in towers:
            if t.type != 'Destroyed_Tower':
                dist = distance(me.x, me.y, t.x, t.y)
                if dist <= skills[2]['radius'] and dist < min_distance:
                    min_distance = dist
                    target_object = t

        # dash to target object
        me.x = target_object.x
        me.y = target_object.y

        me.skill2()

    elif keys[pygame.K_q] and timestamp_now - me.skill3_last_timestamp > skills[3]['cooldown']:
        me.skill1_last_timestamp = timestamp_now
        me.skill3()

def main():
    # create TCP socket and connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))

    # setup pygame
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Soul Beats 1')

    # create or join room
    print('Welcome to Soul Beats 1 !!')
    print('1) Create New Room\n2) Join Room with Room ID')
    choice = input('Select 1 or 2 >> ')
    if choice == '1':
        handle_connection(s, mode='create_room')
    else:
        while not room_joined:
            room_id = int(input('Room ID >> '))
            handle_connection(s, mode='join_room', room_id=room_id)

    running = True
    while running: # game main loop
        clock.tick(FPS) # set FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        handle_move()
        handle_skill()

        if me.is_dead:
            dead()
        if me.is_respawn:
            respawn()

        try:
            start_new_thread(handle_connection, (s, 'update_state'))
        except Exception as e:
            print(e)

        update_display(screen)

    s.close()
    pygame.quit()


main()