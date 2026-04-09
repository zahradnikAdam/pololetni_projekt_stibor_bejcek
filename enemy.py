import pygame
import random
from assets import ASSETS


class Projectile:
    def __init__(self, x, y, vel, size=10, damage=1, color=(255, 120, 80)):
        self.rect = pygame.Rect(int(x), int(y), int(size), int(size))
        self.vel = pygame.Vector2(vel)
        self.damage = int(damage)
        self.color = color

    def update(self, walls):
        self.rect.x += int(self.vel.x)
        for w in walls:
            if self.rect.colliderect(w):
                return False
        self.rect.y += int(self.vel.y)
        for w in walls:
            if self.rect.colliderect(w):
                return False
        return True

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=3)


class Enemy:
    """Základní nepřítel s jednoduchou AI.

    - AI: 'follow' (sledování hráče) nebo 'wander' (náhodný pohyb)
    - má rychlost, hp, barvu
    """

    def __init__(
        self,
        x,
        y,
        size=40,
        speed=2,
        hp=3,
        color=(100, 200, 100),
        ai='wander',
        attack_type='melee',  # 'melee' nebo 'ranged'
        attack_damage=1,
        attack_cooldown_max=50,
        attack_range=260,
        projectile_speed=5.0,
    ):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.ai = ai
        self.attack_type = attack_type
        self.attack_damage = int(attack_damage)
        self.attack_cooldown = random.randint(0, int(attack_cooldown_max))
        self.attack_cooldown_max = int(attack_cooldown_max)
        self.attack_range = float(attack_range)
        self.projectile_speed = float(projectile_speed)

        # pro wander AI
        self.wander_dir = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.wander_dir.length_squared() == 0:
            self.wander_dir = pygame.Vector2(1, 0)
        else:
            self.wander_dir = self.wander_dir.normalize()
        self.wander_timer = random.randint(30, 120)

    def move(self, direction, walls):
        if direction.x != 0:
            self.rect.x += int(direction.x * self.speed)
            for w in walls:
                if self.rect.colliderect(w):
                    if direction.x > 0:
                        self.rect.right = w.left
                    else:
                        self.rect.left = w.right

        if direction.y != 0:
            self.rect.y += int(direction.y * self.speed)
            for w in walls:
                if self.rect.colliderect(w):
                    if direction.y > 0:
                        self.rect.bottom = w.top
                    else:
                        self.rect.top = w.bottom

    def update(self, player, walls):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # vyber směr podle AI
        if self.ai == 'follow':
            dirv = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
            if dirv.length_squared() > 0:
                dirv = dirv.normalize()
            else:
                dirv = pygame.Vector2(0, 0)
            self.move(dirv, walls)
        else:  # wander
            if self.wander_timer <= 0:
                self.wander_dir = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if self.wander_dir.length_squared() == 0:
                    self.wander_dir = pygame.Vector2(1, 0)
                else:
                    self.wander_dir = self.wander_dir.normalize()
                self.wander_timer = random.randint(30, 120)
            else:
                self.wander_timer -= 1

            self.move(self.wander_dir, walls)

    def try_attack(self, player):
        """Vrátí Projectile pro ranged útok, nebo None. Melee řeší Game smyčka přes kolizi."""
        if self.attack_cooldown > 0:
            return None

        # jednoduchý range check
        d = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if d.length_squared() > self.attack_range * self.attack_range:
            return None

        if self.attack_type != 'ranged':
            return None

        if d.length_squared() == 0:
            d = pygame.Vector2(1, 0)
        else:
            d = d.normalize()

        vel = d * self.projectile_speed
        p = Projectile(
            self.rect.centerx - 5,
            self.rect.centery - 5,
            vel=vel,
            size=10,
            damage=self.attack_damage,
            color=(255, 140, 80),
        )
        self.attack_cooldown = self.attack_cooldown_max
        return p

    def draw(self, surface):
        # choose asset key based on class name
        key_map = {
            'Slime': 'slime',
            'Bat': 'bat',
            'Skeleton': 'skeleton',
            'Rat': 'rat',
            'Dragon': 'dragon'
        }
        cls_name = self.__class__.__name__
        asset_key = key_map.get(cls_name, None)
        img = None
        if asset_key:
            img = ASSETS.get_scaled(asset_key, (self.rect.width, self.rect.height))

        if img:
            surface.blit(img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

        # health bar
        bar_w = self.rect.width
        bar_h = 5
        hp_ratio = max(self.hp / max(1, getattr(self, 'max_hp', self.hp)), 0)
        pygame.draw.rect(surface, (60, 60, 60), (self.rect.x, self.rect.y - 8, bar_w, bar_h))
        pygame.draw.rect(surface, (200, 50, 50), (self.rect.x, self.rect.y - 8, int(bar_w * hp_ratio), bar_h))


class Slime(Enemy):
    def __init__(self, x, y):
        # lehčí: méně HP a pomalejší
        super().__init__(x, y, size=36, speed=1.2, hp=2, color=(100, 255, 100), ai='wander', attack_type='melee', attack_damage=1, attack_cooldown_max=50, attack_range=70)
        self.max_hp = 2


class Bat(Enemy):
    def __init__(self, x, y):
        # ranged: lehčí (pomalejší, méně často)
        super().__init__(x, y, size=28, speed=2.6, hp=2, color=(200, 200, 255), ai='follow', attack_type='ranged', attack_damage=1, attack_cooldown_max=85, attack_range=300, projectile_speed=4.6)
        self.max_hp = 2


class Skeleton(Enemy):
    def __init__(self, x, y):
        # ranged: lehčí (méně HP, méně často)
        super().__init__(x, y, size=40, speed=2.0, hp=3, color=(220, 220, 180), ai='follow', attack_type='ranged', attack_damage=1, attack_cooldown_max=95, attack_range=320, projectile_speed=4.2)
        self.max_hp = 3


class Rat(Enemy):
    def __init__(self, x, y):
        # tank původně byl moc silný -> výrazně lehčí
        # ai='follow' aby aktivně útočil na hráče
        super().__init__(x, y, size=52, speed=1.0, hp=6, color=(150, 90, 90), ai='follow', attack_type='melee', attack_damage=1, attack_cooldown_max=55, attack_range=85)
        self.max_hp = 6


class Dragon(Enemy):
    def __init__(self, x, y):
        # boss: lehčí (méně HP, méně často, pomalejší střely)
        super().__init__(x, y, size=72, speed=1.1, hp=16, color=(200, 50, 120), ai='follow', attack_type='ranged', attack_damage=1, attack_cooldown_max=60, attack_range=480, projectile_speed=5.5)
        self.max_hp = 16
