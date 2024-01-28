class Tower:
    def __init__(self, x, y, max_hp, damage, radius, cooldown, team, type):
        self.x = x
        self.y = y

        self.hp = max_hp
        self.max_hp = max_hp

        self.team = team
        self.type = type

        self.damage = damage
        self.radius = radius
        self.cooldown = cooldown

        self.is_shoot = False
        self.shoot_to_xy = (x, y)
        self.last_shot_timestamp = 0

    def shoot(self, shoot_to_xy):
        self.is_shoot = True
        self.shoot_to_xy = shoot_to_xy