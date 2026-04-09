import pygame
import random
from player import Player
from level import LevelManager
from menu import main_menu, pause_menu
from assets import ASSETS


class Game:
    def __init__(self, width=800, height=600, fps=60):
        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = fps

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("PyGame — Modular Demo")
        clock = pygame.time.Clock()

        # debug: print available asset keys
        try:
            print("ASSETS keys:", [k for k, v in ASSETS.images.items() if v])
        except Exception:
            pass

        walls = [
            pygame.Rect(100, 100, 200, 24),
            pygame.Rect(400, 200, 24, 250),
            pygame.Rect(150, 400, 300, 24),
        ]

        # Zabraň hráči i nepřátelům odejít z mapy:
        # přidáme hraniční stěny kolem celé obrazovky.
        border = 24
        walls.extend([
            pygame.Rect(0, 0, self.WIDTH, border),  # top
            pygame.Rect(0, self.HEIGHT - border, self.WIDTH, border),  # bottom
            pygame.Rect(0, 0, border, self.HEIGHT),  # left
            pygame.Rect(self.WIDTH - border, 0, border, self.HEIGHT),  # right
        ])

        menu_result = main_menu(screen, clock)
        if isinstance(menu_result, tuple):
            selected_skin, difficulty = menu_result
        else:
            selected_skin, difficulty = menu_result, 'Normal'

        def apply_difficulty(enemies_list):
            # Easy/Normal/Hard upraví nepřátele (rychlost, HP, střelbu)
            if difficulty == 'Easy':
                hp_mul = 0.85
                spd_mul = 0.9
                proj_mul = 0.85
                cd_mul = 1.35
            elif difficulty == 'Hard':
                hp_mul = 1.15
                spd_mul = 1.05
                proj_mul = 1.1
                cd_mul = 0.85
            else:
                hp_mul = spd_mul = proj_mul = cd_mul = 1.0

            for e in enemies_list:
                try:
                    # "podle backgroundu" = podle levelu (každý level má svůj background)
                    lvl = level_manager.get_level_number()
                    level_speed_mul = {1: 0.95, 2: 1.0, 3: 1.05, 4: 1.08, 5: 1.1}.get(lvl, 1.0)

                    e.speed = float(getattr(e, 'speed', 1.0)) * spd_mul * level_speed_mul
                    e.projectile_speed = float(getattr(e, 'projectile_speed', 0.0)) * proj_mul
                    e.attack_cooldown_max = int(max(10, int(getattr(e, 'attack_cooldown_max', 50) * cd_mul)))
                    # HP upravíme jen na začátku levelu
                    e.max_hp = int(max(1, round(getattr(e, 'max_hp', getattr(e, 'hp', 1)) * hp_mul)))
                    e.hp = int(min(getattr(e, 'hp', e.max_hp), e.max_hp))
                except Exception:
                    pass

        # náhodný spawn hráče na začátku (mimo zdi)
        def random_free_pos(size):
            margin = border + 6
            for _ in range(200):
                x = random.randint(margin, self.WIDTH - margin - size)
                y = random.randint(margin, self.HEIGHT - margin - size)
                r = pygame.Rect(x, y, size, size)
                if not any(r.colliderect(w) for w in walls):
                    return x, y
            # fallback
            return self.WIDTH // 2 - size // 2, self.HEIGHT // 2 - size // 2

        spawn_x, spawn_y = random_free_pos(48)
        player = Player(spawn_x, spawn_y, skin=selected_skin)

        attack_effects = []
        player_projectiles = []
        enemy_projectiles = []
        heart_rect = None
        heart_timer = random.randint(self.FPS * 8, self.FPS * 14)
        max_lives = 5
        level_manager = LevelManager()
        enemies = level_manager.load_current()
        apply_difficulty(enemies)
        level_transition_timer = 0
        level_cleared_display = 0

        font = pygame.font.SysFont(None, 24)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        action = pause_menu(screen, clock)
                        if action == 'quit':
                            running = False
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_f:
                        a = player.attack()
                        if a:
                            kind, payload = a
                            if kind == 'melee':
                                attack_effects.append([payload, 6])
                            elif kind == 'ranged':
                                player_projectiles.append(payload)

            direction = player.handle_input()
            player.move(direction, walls)
            player.update()

            for eff in attack_effects[:]:
                eff[1] -= 1
                if eff[1] <= 0:
                    attack_effects.remove(eff)

            for eff in attack_effects:
                atk_rect = eff[0]
                for e in enemies[:]:
                    if atk_rect.colliderect(e.rect):
                        e.hp -= player.attack_damage
                        if e.hp <= 0:
                            enemies.remove(e)

            # player ranged projectiles
            for p in player_projectiles[:]:
                alive = True
                try:
                    alive = p.update(walls)
                except Exception:
                    alive = False
                if not alive:
                    player_projectiles.remove(p)
                    continue
                for e in enemies[:]:
                    if p.rect.colliderect(e.rect):
                        e.hp -= getattr(p, 'damage', player.attack_damage)
                        player_projectiles.remove(p)
                        if e.hp <= 0:
                            enemies.remove(e)
                        break

            # enemy melee + ranged attacks
            for e in enemies:
                # melee: damage on contact (with per-enemy cooldown)
                if getattr(e, 'attack_type', None) == 'melee':
                    if e.rect.colliderect(player.rect) and getattr(e, 'attack_cooldown', 0) <= 0:
                        player.take_damage(getattr(e, 'attack_damage', 1))
                        e.attack_cooldown = getattr(e, 'attack_cooldown_max', 50)

                # ranged: spawn projectile if ready
                p = None
                try:
                    p = e.try_attack(player)
                except Exception:
                    p = None
                if p:
                    enemy_projectiles.append(p)

            # heart spawn + pickup
            heart_size = 40
            if heart_rect is None:
                heart_timer -= 1
                if heart_timer <= 0:
                    hx, hy = random_free_pos(heart_size)
                    heart_rect = pygame.Rect(hx, hy, heart_size, heart_size)
                    heart_timer = random.randint(self.FPS * 10, self.FPS * 18)
            else:
                if player.rect.colliderect(heart_rect):
                    player.lives = min(max_lives, player.lives + 1)
                    heart_rect = None

            # update enemy projectiles
            for p in enemy_projectiles[:]:
                alive = True
                try:
                    alive = p.update(walls)
                except Exception:
                    alive = False
                if not alive:
                    enemy_projectiles.remove(p)
                    continue
                if p.rect.colliderect(player.rect):
                    player.take_damage(getattr(p, 'damage', 1))
                    enemy_projectiles.remove(p)

            # game over on 0 lives
            if player.lives <= 0:
                running = False

            if not enemies and level_transition_timer <= 0:
                level_manager.advance()
                if level_manager.has_next():
                    level_transition_timer = 30
                    level_cleared_display = 60
                else:
                    level_cleared_display = 180

            if level_transition_timer > 0:
                level_transition_timer -= 1
                if level_transition_timer == 0 and level_manager.has_next():
                    enemies = level_manager.load_current()
                    apply_difficulty(enemies)
                    enemy_projectiles.clear()
                    player_projectiles.clear()
                    heart_rect = None

            # background
            lvl = level_manager.get_level_number()
            bg_key = None
            for k in (f'background_{lvl}', f'level_{lvl}', f'bg_{lvl}', f'pozadi_{lvl}', 'background'):
                if ASSETS.get(k):
                    bg_key = k
                    break
            bg = ASSETS.get(bg_key) if bg_key else None
            if bg:
                # scale background to screen size if needed
                if bg.get_size() != (self.WIDTH, self.HEIGHT):
                    bg_s = pygame.transform.smoothscale(bg, (self.WIDTH, self.HEIGHT))
                else:
                    bg_s = bg
                screen.blit(bg_s, (0, 0))
            else:
                screen.fill((30, 30, 30))

            # walls (try to use wall tile if available)
            wall_img = ASSETS.get('wall')
            for w in walls:
                if wall_img:
                    # tile the wall rect with the wall image
                    tw, th = wall_img.get_size()
                    for x in range(w.left, w.right, tw):
                        for y in range(w.top, w.bottom, th):
                            screen.blit(wall_img, (x, y))
                else:
                    pygame.draw.rect(screen, (80, 80, 80), w)

            for e in enemies:
                e.update(player, walls)
                e.draw(screen)

            for p in player_projectiles:
                try:
                    p.draw(screen)
                except Exception:
                    pass

            for p in enemy_projectiles:
                try:
                    p.draw(screen)
                except Exception:
                    pass

            # draw heart pickup
            if heart_rect:
                heart_img = ASSETS.get_scaled('heart', (heart_rect.width, heart_rect.height))
                if heart_img:
                    screen.blit(heart_img, heart_rect.topleft)
                else:
                    pygame.draw.rect(screen, (220, 60, 80), heart_rect, border_radius=6)

            if not enemies and not level_manager.has_next() and level_cleared_display > 0:
                victory_surf = font.render("Vítězství! Všechny úrovně dokončeny.", True, (240, 220, 100))
                screen.blit(victory_surf, (self.WIDTH//2 - victory_surf.get_width()//2, self.HEIGHT//2 - 20))
                level_cleared_display -= 1
                if level_cleared_display <= 0:
                    running = False

            if level_cleared_display > 0 and level_manager.has_next():
                msg = f"Level {level_manager.get_level_number() - 1} cleared! Přechod na další..."
                txt = font.render(msg, True, (220, 220, 220))
                screen.blit(txt, (self.WIDTH//2 - txt.get_width()//2, 40))

            for eff in attack_effects:
                pygame.draw.rect(screen, (255, 180, 60), eff[0])

            player.draw(screen)

            hp_surf = font.render(f"HP: {player.hp}/{getattr(player, 'max_hp', player.hp)}   Lives: {getattr(player, 'lives', 0)}", True, (220, 220, 220))
            screen.blit(hp_surf, (8, 8))

            pygame.display.flip()
            clock.tick(self.FPS)

        pygame.quit()
