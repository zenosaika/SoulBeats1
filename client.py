import socket
import pickle
import pygame
import time
import math
import random
import colorsys
import pygame_textinput
from _thread import start_new_thread

from _class.Player import Player


SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

# Game Config
FPS = 60
GAME_WIDTH = 700
GAME_HEIGHT = 700
GRID_COL = 20
GRID_ROW = 20
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
GAME_DURATION = 60 # seconds

# Global Variables
room_joined = False
players = [] # store Player objects
towers = [] # store Tower objects
grid = [[-1]*GRID_COL for _ in range(GRID_ROW)]
scores = {}
me = Player(x=35, y=35, character='Heron')
is_game_start = False
game_start_timestamp = 0
current_room_id = -1

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

images = {
    'Map': load_image('_asset/map.png', resize_to=(GAME_WIDTH, GAME_HEIGHT)),
    'Lobby1': load_image('_asset/lobby1.png', resize_to=(GAME_WIDTH, GAME_HEIGHT)),
    'Lobby2': load_image('_asset/lobby2.png', resize_to=(GAME_WIDTH, GAME_HEIGHT)),
}

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
    global me, players, towers, grid, scores, room_joined, is_game_start, game_start_timestamp
    header = packet['header']
    body = packet['body']

    if header == 'room_created':
        room_joined = True
        print('[ROOM]: Welcome!')
        print(f'[ROOM]: This room id is {body["room_id"]}')
        global current_room_id
        current_room_id = body["room_id"]

    elif header == 'join_success':
        room_joined = True
        print('[ROOM]: Welcome!')

    elif header == 'join_failed':
        print(f'[SERVER]: {body["error"]}')

    elif header == 'check_game_status':
        is_game_start = body['is_game_start']
        game_start_timestamp =  body['game_start_timestamp']

    elif header == 'update_server_state':
        players = body['players']
        towers = body['towers']
        grid = body['grid']
        scores = body['scores']
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

    elif mode == 'check_game_status':
        s.send(pickle.dumps({
            'header': 'check_game_status',
            'body': {
                'me': me
            }
        }))

    try:
        packet = s.recv(4096) # return packet or null
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

def draw_username(screen, p, pos):
    font = pygame.font.SysFont('Comic Sans MS', 16)
    screen.blit(font.render(p.username, False, (255, 255, 255)), pos)

def render_player(screen, p):
    x = p.x - 40
    y = p.y - 60
    if p.use_skill1 or p.use_skill2 or p.use_skill3:
        # animate procedural orb first
        if p.use_skill1:
            screen.blit(play_animation('skill1', 0.7), (x-18, y))
        if p.use_skill2:
            screen.blit(play_animation('skill2', 0.7), (x-33, y))
        if p.use_skill3:
            screen.blit(play_animation('skill3', 0.7), (x-60, y-30))
        # then animate character and his wand
        screen.blit(play_animation('magic_wand', 0.7), (x, y))
    elif p.is_walk:
        screen.blit(play_animation(f'walk_{p.walk_direction}', 1.5), (x, y))
    else:
        screen.blit(animations[f'walk_{p.walk_direction}']['images'][0], (x, y))
    draw_hp(screen, p, pos=(x+7, y-10))
    draw_username(screen, p, pos=(x+7, y-35))

def render_tower(screen, t):
    if t.type != 'Destroyed_Tower':
        screen.blit(play_animation('megia_stand', 2), (t.x, t.y))
        draw_hp(screen, t, pos=(t.x+7, t.y-10))
        
        if t.is_shoot:
            screen.blit(play_animation('megia_skill', 0.7), (t.x-75, t.y-40))
            screen.blit(play_animation('megia_attack', 0.7), (t.x, t.y))
    else:
        screen.blit(animations['megia_dead']['images'][4], (t.x, t.y)) 

def render_room_id(screen):
    font = pygame.font.SysFont('Comic Sans MS', 15)
    screen.blit(font.render(f'Room ID: {current_room_id}', False, (255, 255, 255)), (WINDOW_WIDTH-120, 10))

def render_scoreboard(screen):
    font = pygame.font.SysFont('Comic Sans MS', 16)
    scoreboard = []

    for v in scores.values():
        scoreboard.append((v['score'], v['username']))

    scoreboard = sorted(scoreboard)

    for i, (score, username) in enumerate(scoreboard):
        score = f"{username} : {score} blocks"
        screen.blit(font.render(score, False, (255, 255, 255)), (15, 650-20*i))

    if is_game_start == False and len(scoreboard) > 0:
        winner = scoreboard[-1]
        render_text(screen, f'The winner is {winner[1]}', size=24, color=(255, 215, 0), pos=(250, 70), bg=(0, 0, 0, 128))
        # screen.blit(font.render(f'The winner is {winner[1]}', False, (255, 215, 0)), (250, 70))

def render_skill_cooldown(screen):
    font = pygame.font.SysFont('Comic Sans MS', 16)
    timestamp_now = time.time()

    skill1_cooldown = skills[1]['cooldown'] - (timestamp_now - me.skill1_last_timestamp)
    skill1_cooldown = 'Ready!' if skill1_cooldown <= 0 else f'{skill1_cooldown:.0f}'
    screen.blit(font.render(f'[SPACE] Soul Eater : {skill1_cooldown}', False, (255, 255, 255)), (475, 610))

    skill2_cooldown = skills[2]['cooldown'] - (timestamp_now - me.skill2_last_timestamp)
    skill2_cooldown = 'Ready!' if skill2_cooldown <= 0 else f'{skill2_cooldown:.0f}'
    screen.blit(font.render(f'       [E]   Soul Daze : {skill2_cooldown}', False, (255, 255, 255)), (475, 630))

    skill3_cooldown = skills[3]['cooldown'] - (timestamp_now - me.skill3_last_timestamp)
    skill3_cooldown = 'Ready!' if skill3_cooldown <= 0 else f'{skill3_cooldown:.0f}'
    screen.blit(font.render(f'       [Q]   Soul Blue : {skill3_cooldown}', False, (255, 255, 255)), (475, 650))

def render_timeleft(screen):
    font = pygame.font.SysFont('Comic Sans MS', 28)
    timestamp_now = time.time()

    timeleft = GAME_DURATION - (timestamp_now - game_start_timestamp)
    timeleft = 'Match Finished' if timeleft <= 0 else f'   {timeleft:.0f} seconds'
    screen.blit(font.render(timeleft, False, (255, 255, 255)), (266, 30))

def render_text(screen, text, size, color, pos, bg=(-1, -1, -1, 0)):
    if bg != (-1, -1, -1, 0):
        padding = 5 
        text_bg = pygame.Surface((len(text)*size/2+padding*2, size+padding*2), pygame.SRCALPHA)
        text_bg.fill((bg[0], bg[1], bg[2], bg[3]))                        
        screen.blit(text_bg, (pos[0]-padding, pos[1]))
    font = pygame.font.SysFont('Comic Sans MS', size)
    screen.blit(font.render(text, False, color), pos)

def update_display(screen):
    # render map
    screen.blit(images['Map'], (0, 0))

    # render grid painting
    grid_width = GAME_WIDTH / GRID_COL
    grid_height = GAME_HEIGHT / GRID_ROW
    for i in range(GRID_ROW):
        for j in range(GRID_COL):
            if grid[i][j] != -1:
                color = grid[i][j][1]
                color_surface = pygame.Surface((grid_width, grid_height), pygame.SRCALPHA)
                color_surface.fill((color[0], color[1], color[2], 128))                         
                screen.blit(color_surface, (j*grid_width, i*grid_height))

    # render me
    render_player(screen, me)

    # render other players
    for p in players:
        render_player(screen, p)
    
    # render towers
    for t in towers:
        render_tower(screen, t)

    # render rightbar menu
    # pygame.draw.rect(screen, (32, 32, 32), pygame.Rect(GAME_WIDTH, 0, WINDOW_WIDTH-GAME_WIDTH, WINDOW_HEIGHT))

    render_scoreboard(screen)
    render_skill_cooldown(screen)
    render_timeleft(screen)
    render_room_id(screen)

    if is_game_start == False and me.ready == False:
        render_text(screen, 'Press R to Ready', size=24, color=(255, 255, 255), pos=(265, 335), bg=(0, 0, 0, 128))

    pygame.display.update()

def is_in_world_border(x, y):
    if (30 <= x <= GAME_WIDTH-30) and (30 <= y <= GAME_HEIGHT-30):
        return True
    return False

def handle_move():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        if is_in_world_border(me.x, me.y-me.velocity):
            me.move_to(me.x, me.y-me.velocity)
        me.is_walk = True
        me.walk_direction = 'top'
    elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
        if is_in_world_border(me.x-me.velocity, me.y):
            me.move_to(me.x-me.velocity, me.y)
        me.is_walk = True
        me.walk_direction = 'left'
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        if is_in_world_border(me.x, me.y+me.velocity):
            me.move_to(me.x, me.y+me.velocity)
        me.is_walk = True
        me.walk_direction = 'bottom'
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        if is_in_world_border(me.x+me.velocity, me.y):
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
    me.x = me.y = 30

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2) ** 0.5

def handle_skill():
    timestamp_now = time.time()
    keys = pygame.key.get_pressed()

    # Skill 1 : Soul Eater
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

    # Skill 3 : Soul Blue
    elif keys[pygame.K_q] and timestamp_now - me.skill3_last_timestamp > skills[3]['cooldown']:
        me.skill1_last_timestamp = timestamp_now
        me.skill3()

def main():
    # create TCP socket and connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))

    # setup pygame
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.mixer.music.load('_asset/NightShade.mp3')
    pygame.display.set_caption('Soul Beats 1')

    # create or join room
    print('Welcome to Soul Beats 1 !!')

    font = pygame.font.SysFont("superclarendon", 55)
    manager = pygame_textinput.TextInputManager(validator = lambda input: len(input) <= 8)
    textinput_custom = pygame_textinput.TextInputVisualizer(manager=manager, font_object=font)

    textinput_custom.cursor_width = 4
    textinput_custom.cursor_blink_interval = 400 # blinking interval in ms
    textinput_custom.antialias = False
    textinput_custom.font_color = (0, 85, 170)

    while True: # Set Username Loop
        # screen.fill((0, 0, 0))
        screen.blit(images['Lobby1'], (0, 0))

        events = pygame.event.get()

        # Feed it with events every frame
        textinput_custom.update(events)

        # Get its surface to blit onto the screen
        # screen.blit(textinput.surface, (10, 10))
        len_text = len(textinput_custom.value)
        screen.blit(textinput_custom.surface, (WINDOW_WIDTH/2 - 16*len_text, WINDOW_HEIGHT/2 - 20))

        # Modify attributes on the fly - the surface is only rerendered when .surface is accessed & if values changed
        textinput_custom.font_color = [(c+10)%255 for c in textinput_custom.font_color]

        for event in events:
            if event.type == pygame.QUIT:
                exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            if 0 < len(textinput_custom.value) <= 8:
                me.username = textinput_custom.value
                break

        pygame.display.update()
        clock.tick(30)

    pygame.display.set_caption(f'Soul Beats 1 ({me.username})')

    font = pygame.font.SysFont("superclarendon", 55)
    manager = pygame_textinput.TextInputManager(validator = lambda input: len(input) <= 4)
    textinput_custom = pygame_textinput.TextInputVisualizer(manager=manager, font_object=font)

    textinput_custom.cursor_width = 4
    textinput_custom.cursor_blink_interval = 400 # blinking interval in ms
    textinput_custom.antialias = False
    textinput_custom.font_color = (0, 85, 170)

    # Create a surface for the button
    button_surface = pygame.Surface((150, 50))

    # Render text on the button
    font2 = pygame.font.SysFont("superclarendon", 23)
    text = font2.render("New Room", True, (0, 0, 0))
    text_rect = text.get_rect(center=(button_surface.get_width()/2, button_surface.get_height()/2))
    button_rect = pygame.Rect(20, WINDOW_HEIGHT - 70, 150, 50)

    while not room_joined: # Join Room Loop
        # screen.fill((0, 0, 0))
        screen.blit(images['Lobby2'], (0, 0))

        events = pygame.event.get()

        # Feed it with events every frame
        textinput_custom.update(events)

        len_text = len(textinput_custom.value)
        screen.blit(textinput_custom.surface, (WINDOW_WIDTH/2 - 18*len_text, WINDOW_HEIGHT/2 - 24))

        # Modify attributes on the fly - the surface is only rerendered when .surface is accessed & if values changed
        textinput_custom.font_color = [(c+10)%255 for c in textinput_custom.font_color]

        for event in events:
            if event.type == pygame.QUIT:
                exit()
        
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    handle_connection(s, mode='create_room')
        
        if button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(button_surface, (127, 255, 212), (1, 1, 148, 48))
        else:
            pygame.draw.rect(button_surface, (0, 0, 0), (0, 0, 150, 50))
            pygame.draw.rect(button_surface, (255, 255, 255), (1, 1, 148, 48))
            pygame.draw.rect(button_surface, (0, 0, 0), (1, 1, 148, 1), 2)
            pygame.draw.rect(button_surface, (0, 100, 0), (1, 48, 148, 10), 2)

        # Shwo the button text
        button_surface.blit(text, text_rect)

        # Draw the button on the screen
        screen.blit(button_surface, (button_rect.x, button_rect.y))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            if len(textinput_custom.value) == 4:
                global current_room_id
                current_room_id = int(textinput_custom.value)
                handle_connection(s, mode='join_room', room_id=current_room_id)

        pygame.display.update()
        clock.tick(30)


    # random color
    # _h, _s, _l = random.random(), 0.5+random.random()/2.0, 0.4+ random.random()/5.0
    # r, g, b = [int(256*i) for i in colorsys.hls_to_rgb(_h, _l, _s)]
    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    me.color = (r, g, b)

    running = True
    while running: # game main loop
        clock.tick(FPS) # set FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r] and is_game_start == False:
            me.ready = True

        if is_game_start:
            if me.ready: # for the first time
                me.ready = False
                me.x = me.y = 30
                pygame.mixer.music.play(loops = 0, start = 10.0, fade_ms = 0)

            handle_move()
            handle_skill()

            if me.is_dead:
                dead()
            if me.is_respawn:
                respawn()

            try:
                start_new_thread(handle_connection, (s, 'update_state'))
            except Exception as e:
                ...

        try:
            start_new_thread(handle_connection, (s, 'check_game_status'))
        except Exception as e:
            ...

        update_display(screen)

    s.close()
    pygame.quit()


main()