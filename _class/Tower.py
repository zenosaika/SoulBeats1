class Tower:
    def __init__(self, x, y, damage, cooldown, radius, team, last_shoot_time):
        self.x = x
        self.y = y
        self.damage = damage
        self.cooldown = cooldown
        self.radius = radius
        self.team = team
        self.last_shoot_time = last_shoot_time
        self.is_shoot = False
        self.shoot_to_xy = (x, y)

    def shoot(self, shoot_to_xy):
        self.is_shoot = True
        self.shoot_to_xy = shoot_to_xy