import pygame
import random
import math
from assets import ASSETS


class Projectile:
    def __init__(self, x, y, vel, size=10, damage=1, color=(255, 120, 80), sprite_key=None):
        self.rect = pygame.Rect(int(x), int(y), int(size), int(size))
        self.vel = pygame.Vector2(vel)
        self.damage = int(damage)
        self.color = color
        self.sprite_key = sprite_key
        self._sprite_cache = None
        if self.sprite_key:
            self._sprite_cache = ASSETS.get_scaled(self.sprite_key, (self.rect.width, self.rect.height))

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
        if self._sprite_cache:
            surface.blit(self._sprite_cache, self.rect.topleft)
            return
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
        projectile_size=10,
        projectile_sprite_key=None,
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
        self.projectile_size = int(projectile_size)
        self.projectile_sprite_key = projectile_sprite_key
        self.vel_y = 0.0
        self.gravity = 0.6
        self.jump_strength = 9.0
        self.max_fall_speed = 11.5
        self.on_ground = False
        self.jump_cooldown = 0

        # pro wander AI
        self.wander_dir = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.wander_dir.length_squared() == 0:
            self.wander_dir = pygame.Vector2(1, 0)
        else:
            self.wander_dir = self.wander_dir.normalize()
        self.wander_timer = random.randint(30, 120)

    def _jump(self):
        if self.on_ground and self.jump_cooldown <= 0:
            self.vel_y = -self.jump_strength
            self.on_ground = False
            self.jump_cooldown = 24

    def _is_one_way_platform(self, w):
        return w.width > w.height and w.height <= 24

    def _has_ground_ahead(self, move_x, walls):
        if move_x == 0:
            return True
        probe_x = self.rect.centerx + int((self.rect.width // 2 + 6) * (1 if move_x > 0 else -1))
        probe = pygame.Rect(probe_x, self.rect.bottom + 2, 4, 6)
        for w in walls:
            if probe.colliderect(w):
                return True
        return False

    def _move_platformer(self, move_x, walls):
        blocked_horizontally = False
        if move_x != 0:
            self.rect.x += int(round(move_x * self.speed))
            for w in walls:
                if self._is_one_way_platform(w):
                    # one-way platforms do not block horizontal movement
                    continue
                if self.rect.colliderect(w):
                    blocked_horizontally = True
                    if move_x > 0:
                        self.rect.right = w.left
                    else:
                        self.rect.left = w.right

        prev_bottom = self.rect.bottom
        self.vel_y = min(self.max_fall_speed, self.vel_y + self.gravity)
        self.rect.y += int(round(self.vel_y))
        self.on_ground = False
        for w in walls:
            if self.rect.colliderect(w):
                if self._is_one_way_platform(w):
                    if self.vel_y >= 0 and prev_bottom <= w.top + 6:
                        self.rect.bottom = w.top
                        self.vel_y = 0.0
                        self.on_ground = True
                    continue
                if self.vel_y > 0:
                    self.rect.bottom = w.top
                    self.vel_y = 0.0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = w.bottom
                    self.vel_y = 0.0
        return blocked_horizontally

    def update(self, player, walls):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

        move_x = 0.0
        if self.ai == 'follow':
            if player.rect.centerx > self.rect.centerx + 6:
                move_x = 1.0
            elif player.rect.centerx < self.rect.centerx - 6:
                move_x = -1.0
        else:  # wander
            if self.wander_timer <= 0:
                self.wander_dir = pygame.Vector2(random.choice([-1, 1]), 0)
                self.wander_timer = random.randint(30, 120)
            else:
                self.wander_timer -= 1

            move_x = self.wander_dir.x

        # Keep enemies on platforms unless they intentionally jump.
        if self.on_ground and not self._has_ground_ahead(move_x, walls):
            if self.ai == 'wander':
                self.wander_dir.x *= -1
                move_x = self.wander_dir.x
            else:
                move_x = 0.0

        blocked = self._move_platformer(move_x, walls)

        # Chce-li nepřítel k hráči a ten je výš, zkusí skočit.
        if self.on_ground and player.rect.centery < self.rect.centery - 24 and abs(player.rect.centerx - self.rect.centerx) < 260:
            self._jump()

        # Pokud narazí do stěny, zkusí jump + změnu směru.
        if blocked and self.on_ground:
            self._jump()
            if self.ai != 'follow':
                self.wander_dir.x *= -1

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
            self.rect.centerx - self.projectile_size // 2,
            self.rect.centery - self.projectile_size // 2,
            vel=vel,
            size=self.projectile_size,
            damage=self.attack_damage,
            color=(255, 140, 80),
            sprite_key=self.projectile_sprite_key,
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
        self.float_phase = random.uniform(0.0, 6.28)

    def update(self, player, walls):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Bat létá - ignoruje platformovou gravitaci a drží výšku kolem hráče.
        d = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        move = pygame.Vector2(0, 0)
        if d.length_squared() > 0:
            move = d.normalize()
        self.float_phase += 0.08
        move.y += 0.35 * math.sin(self.float_phase)
        if move.length_squared() > 0:
            move = move.normalize()

        self.rect.x += int(round(move.x * self.speed))
        for w in walls:
            if self.rect.colliderect(w):
                if move.x > 0:
                    self.rect.right = w.left
                elif move.x < 0:
                    self.rect.left = w.right

        self.rect.y += int(round(move.y * self.speed))
        for w in walls:
            if self.rect.colliderect(w):
                if move.y > 0:
                    self.rect.bottom = w.top
                elif move.y < 0:
                    self.rect.top = w.bottom


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
        super().__init__(
            x, y,
            size=72, speed=1.1, hp=16, color=(200, 50, 120),
            ai='follow', attack_type='ranged', attack_damage=1,
            attack_cooldown_max=60, attack_range=480, projectile_speed=5.5,
            projectile_size=24, projectile_sprite_key='meteor'
        )
        self.max_hp = 16
