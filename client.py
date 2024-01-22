import socket
import pygame
import pickle

from _class.Player import Player

# Server Config
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080

# Game Config
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500


def update_display(screen, players):
    screen.blit(rpgmap, (0, 0))
    # screen.fill((0, 0, 0))
    for p in players:
        screen.blit(avatar, (p.x, p.y))
        # pygame.draw.circle(screen, p.color, (p.x, p.y), 5)
    pygame.display.update()


def player_to_dict(player):
    return {
        'x': player.x,
        'y': player.y,
        'color': player.color,
        'velocity': player.velocity,
    }


def dict_to_player(dict):
    return Player(
        x=dict['x'], 
        y=dict['y'], 
        color=dict['color'],
        velocity=dict['velocity'],
    )


# connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

# setup pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('NeneFight')

# setup map and players
rpgmap = pygame.image.load('_assets/map.png') # from https://deepnight.net/tools/rpg-map/
rpgmap = pygame.transform.scale(rpgmap, (WINDOW_WIDTH, WINDOW_HEIGHT))
avatar = pygame.image.load('_assets/avatar.png') # from https://www.avatarsinpixels.com
avatar = pygame.transform.scale(avatar, (60, 60))
me = Player(x=10, y=10, velocity=5, color=(255, 255, 255))
players = []

# game start!
running = True
while running:
    clock.tick(60) # 60 fps

    # for quit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # update data from server
    client.send(pickle.dumps(player_to_dict(me)))
    data = client.recv(2048)
    if data:
        players = [dict_to_player(p) for p in pickle.loads(data)]

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

    # update display
    update_display(screen, players)

pygame.quit()