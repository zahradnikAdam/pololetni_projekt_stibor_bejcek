"""Model hráče a jeho „helper“ objekty.

OOP pohled:
- `Player` je stavový objekt (má vlastní data + metody, které tento stav mění).
- Projektily jsou samostatné objekty s vlastním `update()/draw()`. Hra je drží
  v seznamech (kompozice) místo toho, aby byly „natvrdo“ uvnitř `Player`.
"""

import pygame
from assets import ASSETS


class PlayerProjectile:
    """Datový objekt projektilu (vlastní stav + update/draw)."""
    def __init__(self, x, y, vel, size=10, damage=1, ttl=90, color=(120, 220, 255)):
        self.rect = pygame.Rect(int(x), int(y), int(size), int(size))
        self.vel = pygame.Vector2(vel)
        self.damage = int(damage)
        self.ttl = int(ttl)
        self.color = color

    def update(self, walls):
        self.ttl -= 1
        if self.ttl <= 0:
            return False

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


class HomingSuperProjectile:
    """Varianta projektilu s jiným chováním (jiný update)."""
    def __init__(self, x, y, size=16, speed=9.0, damage=2, ttl=120):
        self.rect = pygame.Rect(int(x), int(y), int(size), int(size))
        self.speed = float(speed)
        self.damage = int(damage)
        self.ttl = int(ttl)
        self.color = (255, 230, 70)

    def update(self, enemies, walls):
        self.ttl -= 1
        if self.ttl <= 0:
            return (False, None)

        if not enemies:
            return (False, None)

        # Priorita: Bat, jinak nejbližší cíl.
        bats = [e for e in enemies if e.__class__.__name__ == "Bat"]
        candidates = bats if bats else enemies
        target = min(candidates, key=lambda e: (pygame.Vector2(e.rect.center) - pygame.Vector2(self.rect.center)).length_squared())

        d = pygame.Vector2(target.rect.center) - pygame.Vector2(self.rect.center)
        if d.length_squared() == 0:
            d = pygame.Vector2(1, 0)
        else:
            d = d.normalize()

        self.rect.x += int(round(d.x * self.speed))
        self.rect.y += int(round(d.y * self.speed))

        for w in walls:
            if self.rect.colliderect(w):
                return (False, None)

        for e in enemies:
            if self.rect.colliderect(e.rect):
                return (False, e)

        return (True, None)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 1, border_radius=6)


class Player:
    """Jednoduchá třída hráče pro 2D dungeon crawler.

    - pohyb vlevo/vpravo + skok (platformer)
    - atributy: speed, hp
    - krátký útok (melee) s cooldownem
    - kolize se zdmi (řešení osově: nejprve X pak Y)
    """

    def __init__(self, x, y, size=48, speed=4, hp=3, skin='Knight', lives=3):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = float(speed)
        self.max_hp = int(hp)
        self.hp = int(hp)
        self.lives = int(lives)
        self.skin = skin
        self.spawn_pos = (int(x), int(y))

        # krátká "nesmrtelnost" po zásahu, aby hráč neumřel během 1 frame
        self.hit_invuln = 0
        self.hit_invuln_max = 30

        # barva podle skinu
        if skin == 'Knight':
            self.color = (120, 160, 220)
        elif skin == 'Mage' or skin == 'Wizard':
            self.color = (160, 80, 200)
        else:
            self.color = (200, 30, 30)

        # facing je směr posledního pohybu (vektor jednotky)
        self.facing = pygame.Vector2(1, 0)
        self.vel_y = 0.0
        self.gravity = 0.58
        self.jump_strength = 12.8
        self.max_fall_speed = 12.0
        self.on_ground = False
        self.jump_buffer = 0
        self.jump_buffer_max = 8
        self.coyote_timer = 0
        self.coyote_max = 8

        # útok
        self.attack_cooldown = 0
        self.attack_cooldown_max = 24  # rámců
        self.attack_range = 32
        self.attack_damage = 1
        self.super_cooldown = 0
        self.super_cooldown_max = 180

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1

        if move.x != 0:
            self.facing = move

        return move.x

    def jump(self):
        # Buffer jump input so jump still triggers reliably.
        self.jump_buffer = self.jump_buffer_max

    def move(self, move_x, walls):
        # Horizontal movement
        if move_x != 0:
            self.rect.x += int(round(move_x * self.speed))
            for w in walls:
                if self.rect.colliderect(w):
                    if move_x > 0:
                        self.rect.right = w.left
                    else:
                        self.rect.left = w.right

        # Grace period after leaving ground.
        if self.on_ground:
            self.coyote_timer = self.coyote_max
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        if self.jump_buffer > 0 and self.coyote_timer > 0:
            self.vel_y = -self.jump_strength
            self.on_ground = False
            self.coyote_timer = 0
            self.jump_buffer = 0

        # Gravity + vertical movement
        self.vel_y = min(self.max_fall_speed, self.vel_y + self.gravity)
        self.rect.y += int(round(self.vel_y))
        self.on_ground = False
        for w in walls:
            if self.rect.colliderect(w):
                if self.vel_y > 0:
                    self.rect.bottom = w.top
                    self.on_ground = True
                    self.vel_y = 0.0
                elif self.vel_y < 0:
                    self.rect.top = w.bottom
                    self.vel_y = 0.0

    def respawn(self):
        self.hp = self.max_hp
        self.rect.topleft = self.spawn_pos
        self.vel_y = 0.0
        self.on_ground = False

    def snap_to_ground(self, walls):
        # Place player on nearest platform below spawn.
        feet_probe = pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, 2000)
        nearest = None
        for w in walls:
            if feet_probe.colliderect(w):
                if w.top >= self.rect.bottom:
                    if nearest is None or w.top < nearest.top:
                        nearest = w
        if nearest is not None:
            self.rect.bottom = nearest.top
            self.on_ground = True
            self.vel_y = 0.0
            self.coyote_timer = self.coyote_max

    def update(self):
        # Centralizace „tikání“ timerů/cooldownů do jedné metody.
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.super_cooldown > 0:
            self.super_cooldown -= 1
        if self.hit_invuln > 0:
            self.hit_invuln -= 1

    def take_damage(self, amount=1):
        """Sníží HP a řeší životy + respawn."""
        if self.hit_invuln > 0:
            return False
        self.hp -= int(amount)
        self.hit_invuln = self.hit_invuln_max
        if self.hp <= 0:
            self.lives -= 1
            if self.lives > 0:
                self.respawn()
        return True

    def draw(self, surface):
        # draw sprite if available
        key = 'player_knight' if self.skin == 'Knight' else 'player_mage'
        img = ASSETS.get_scaled(key, (self.rect.width, self.rect.height))
        if img:
            surface.blit(img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

        # lehké blikání při invulnerability
        if self.hit_invuln > 0 and (self.hit_invuln // 3) % 2 == 0:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        # nakreslí směr pohledu
        end = (self.rect.centerx + int(self.facing.x * 16), self.rect.centery + int(self.facing.y * 16))
        pygame.draw.line(surface, (255, 220, 50), self.rect.center, end, 3)

    def attack(self):
        """Útok podle skinu.

        - Knight: melee (vrací ('melee', pygame.Rect))
        - Wizard/Mage: ranged (vrací ('ranged', PlayerProjectile))
        - None, pokud je cooldown.
        """
        if self.attack_cooldown > 0:
            return None

        is_wizard = self.skin in ('Mage', 'Wizard')

        if is_wizard:
            # ranged: projektil ve směru pohledu
            dirv = pygame.Vector2(self.facing)
            if dirv.length_squared() == 0:
                dirv = pygame.Vector2(1, 0)
            else:
                dirv = dirv.normalize()

            speed = 8.0
            proj = PlayerProjectile(
                self.rect.centerx - 5,
                self.rect.centery - 5,
                vel=dirv * speed,
                size=10,
                damage=self.attack_damage,
                ttl=90,
                color=(120, 220, 255),
            )
            self.attack_cooldown = self.attack_cooldown_max
            return ('ranged', proj)

        # melee (Knight): malý obdélník před hráčem podle směru
        center = pygame.Vector2(self.rect.center)
        offset = self.facing * (self.rect.width // 2 + self.attack_range // 2)
        attack_center = center + offset

        size = (self.attack_range, self.rect.height // 2)
        attack_rect = pygame.Rect(0, 0, size[0], size[1])
        attack_rect.center = (int(attack_center.x), int(attack_center.y))

        self.attack_cooldown = self.attack_cooldown_max
        return ('melee', attack_rect)

    def super_attack(self):
        if self.super_cooldown > 0:
            return None
        p = HomingSuperProjectile(self.rect.centerx - 8, self.rect.centery - 8)
        self.super_cooldown = self.super_cooldown_max
        return p

