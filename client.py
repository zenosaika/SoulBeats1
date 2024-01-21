import socket
import pygame
import pickle

from _class.Player import Player

# Server Config
SERVER_IP = 'localhost'
SERVER_PORT = 8888

# Game Config
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500


def update_display(screen, players):
    screen.fill((0, 0, 0))
    for p in players:
        pygame.draw.circle(screen, p.color, (p.x, p.y), 5)
    pygame.display.update()


# connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

# setup pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('NenePVP')

# setup players
me = Player(x=10, y=10, velocity=3, color=(255, 255, 255))
players = [me]

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
    try:
        client.send(pickle.dumps(me))
        data = client.recv(2048)
        if data:
            players = pickle.loads(data)
    except:
        print('disconnect from server.')
        running = False
        break

    # make a move
    me.move()

    # update display
    update_display(screen, players)

pygame.quit()