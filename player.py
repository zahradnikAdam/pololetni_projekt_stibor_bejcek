import pygame
from assets import ASSETS


class Player:
    """Jednoduchá třída hráče pro 2D dungeon crawler.

    - pohyb pomocí WASD (rovněž podporuje šipky)
    - atributy: speed, hp
    - krátký útok (melee) s cooldownem
    - kolize se zdmi (řešení osově: nejprve X pak Y)
    """

    def __init__(self, x, y, size=48, speed=4, hp=10, skin='Knight'):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = speed
        self.hp = hp
        self.skin = skin

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
        """Provádí krátký útok před hráčem. Vrací `pygame.Rect` oblasti útoku nebo None, pokud je cooldown."""
        if self.attack_cooldown > 0:
            return None

        # vytvoříme malý obdélník před hráčem podle směru
        center = pygame.Vector2(self.rect.center)
        offset = self.facing * (self.rect.width // 2 + self.attack_range // 2)
        attack_center = center + offset

        size = (self.attack_range, self.rect.height // 2)
        attack_rect = pygame.Rect(0, 0, size[0], size[1])
        attack_rect.center = (int(attack_center.x), int(attack_center.y))

        self.attack_cooldown = self.attack_cooldown_max
        return attack_rect

    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, surface):
        # draw sprite if available
        key = 'player_knight' if self.skin == 'Knight' else 'player_mage'
        img = ASSETS.get_scaled(key, (self.rect.width, self.rect.height))
        if img:
            surface.blit(img, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

        # nakreslí směr pohledu
        end = (self.rect.centerx + int(self.facing.x * 16), self.rect.centery + int(self.facing.y * 16))
        pygame.draw.line(surface, (255, 220, 50), self.rect.center, end, 3)
