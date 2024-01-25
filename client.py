import socket
import pygame
import pickle
from _thread import *

from _class.Player import Player

# Server Config
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

# Game Config
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500


def update_display(screen, players, towers):
    screen.blit(rpgmap, (0, 0)) # display map

    # update player
    for p in players:
        screen.blit(avatar, (p.x, p.y)) # display player

        # display player's hp
        pygame.draw.rect(screen, (100, 100, 100), (p.x, p.y-10, 60, 10))
        pygame.draw.rect(screen, (255, 0, 0), (p.x, p.y-9, 60*(p.hp/p.max_hp), 8))

    # update tower
    for tower in towers:
        if tower.is_shoot:
            pygame.draw.line(screen, (237, 47, 50), (tower.x, tower.y), tower.shoot_to_xy, 3) 

    pygame.display.update()


def fetch_server(me_copy):
    global me, players, towers
    client.send(pickle.dumps(me_copy))
    data = client.recv(2048)
    if data:
        me_tmp, players, towers = pickle.loads(data)
        me.hp = me_tmp.hp


# connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

# setup pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('FakeRoV')

# setup map and players
rpgmap = pygame.image.load('_assets/map.png') # from https://deepnight.net/tools/rpg-map/
rpgmap = pygame.transform.scale(rpgmap, (WINDOW_WIDTH, WINDOW_HEIGHT))
avatar = pygame.image.load('_assets/avatar.png') # from https://www.avatarsinpixels.com
avatar = pygame.transform.scale(avatar, (60, 60))
me = Player(x=10, y=10, max_hp=100, velocity=5, color=(255, 255, 255), team='blue')
players = []
towers = []

# game start!
running = True
while running:
    clock.tick(60) # 60 fps

    # for quit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # make a move
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        me.move(me.x, me.y-me.velocity)
    elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
        me.move(me.x-me.velocity, me.y)
    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
        me.move(me.x, me.y+me.velocity)
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        me.move(me.x+me.velocity, me.y)

    # hit
    if keys[pygame.K_SPACE]:
        me.hit()

    # update data from server
    me_copy = Player(x=me.x, y=me.y, max_hp=me.max_hp, velocity=me.velocity, color=me.color, team=me.team, is_hit=me.is_hit)
    start_new_thread(fetch_server, (me_copy,))

    # update display
    update_display(screen, players+[me], towers)

    # reset state
    me.is_hit = False

pygame.quit()
