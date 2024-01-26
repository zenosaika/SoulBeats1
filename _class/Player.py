class Player:
    def __init__(self, x, y, max_hp, velocity, color, team, is_hit=False):
        self.x = x
        self.y = y
        self.max_hp = max_hp
        self.hp = max_hp
        self.velocity = velocity
        self.color = color
        self.is_hit = is_hit
        self.team = team
        self.is_dead = False
        self.dead_time = 0
        self.is_respawn = False
        self.respawn_cooldown = 3

    def move(self, x, y):
        self.x = x
        self.y = y

    def hit(self):
        self.is_hit = True