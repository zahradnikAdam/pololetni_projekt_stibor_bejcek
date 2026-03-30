import pygame
import random
from assets import ASSETS


class Enemy:
    """Základní nepřítel s jednoduchou AI.

    - AI: 'follow' (sledování hráče) nebo 'wander' (náhodný pohyb)
    - má rychlost, hp, barvu
    """

    def __init__(self, x, y, size=40, speed=2, hp=3, color=(100, 200, 100), ai='wander'):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.ai = ai

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
        super().__init__(x, y, size=36, speed=1.5, hp=3, color=(100, 255, 100), ai='wander')
        self.max_hp = 3


class Bat(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, size=28, speed=3.0, hp=2, color=(200, 200, 255), ai='follow')
        self.max_hp = 2


class Skeleton(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, size=40, speed=2.2, hp=4, color=(220, 220, 180), ai='follow')
        self.max_hp = 4


class Rat(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, size=52, speed=0.9, hp=10, color=(150, 90, 90), ai='wander')
        self.max_hp = 10


class Dragon(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, size=72, speed=1.2, hp=25, color=(200, 50, 120), ai='follow')
        self.max_hp = 25
