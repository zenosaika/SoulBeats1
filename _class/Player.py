class Player:
    def __init__(self, x, y, character):
        self.x = x
        self.y = y
        self.character = character

        self.velocity = 5

        self.hp = 100
        self.max_hp = 100

        self.use_skill1 = False
        self.use_skill2 = False
        self.use_skill3 = False

        self.skill1_last_timestamp = 0
        self.skill2_last_timestamp = 0
        self.skill3_last_timestamp = 0

        self.is_dead = False
        self.death_timestamp = 0
        self.respawn_cooldown = 5
        self.is_respawn = False

        self.is_walk = False
        self.walk_direction = 'bottom'

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def skill1(self):
        self.use_skill1 = True

    def skill2(self):
        self.use_skill2 = True

    def skill3(self):
        self.use_skill3 = True