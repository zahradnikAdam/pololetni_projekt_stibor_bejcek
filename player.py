import pygame
from assets import ASSETS


class PlayerProjectile:
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


class Player:
    """Jednoduchá třída hráče pro 2D dungeon crawler.

    - pohyb pomocí WASD (rovněž podporuje šipky)
    - atributy: speed, hp
    - krátký útok (melee) s cooldownem
    - kolize se zdmi (řešení osově: nejprve X pak Y)
    """

    def __init__(self, x, y, size=48, speed=4, hp=3, skin='Knight', lives=3):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
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

        # útok
        self.attack_cooldown = 0
        self.attack_cooldown_max = 24  # rámců
        self.attack_range = 32
        self.attack_damage = 1

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1

        if move.length_squared() > 0:
            move = move.normalize()
            self.facing = move

        return move

    def move(self, direction, walls):
        # Pohyb a jednoduché řešení kolizí (osově separované)
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

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
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
                self.hp = self.max_hp
                self.rect.topleft = self.spawn_pos
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
