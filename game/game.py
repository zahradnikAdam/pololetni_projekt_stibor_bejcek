import pygame
import random
from player.player import Player
from game.level import LevelManager
from menu.menu import main_menu, pause_menu
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

        border = 24

        def build_border_walls():
            return [
                pygame.Rect(0, self.HEIGHT - border, self.WIDTH, border),  # floor
                pygame.Rect(0, 0, border, self.HEIGHT),  # left wall
                pygame.Rect(self.WIDTH - border, 0, border, self.HEIGHT),  # right wall
            ]

        def generate_level_walls(level_no, blocked_rects=None):
            blocked_rects = blocked_rects or []
            generated = build_border_walls()
            player_rect = blocked_rects[0] if blocked_rects else pygame.Rect(self.WIDTH // 2 - 24, 80, 48, 48)

            # Náhodné platformy: kombinace "schodů" + náhodných platforem.
            interior_count = min(6, 2 + level_no)
            max_tries = 320
            placed = 0

            # Základní schody, aby byly platformy vždy dosažitelné skokem.
            step_w = 160
            step_h = 20
            step_gap_y = 64
            x = border + 40
            y = self.HEIGHT - border - 72
            direction = 1
            for _ in range(5):
                x = max(border + 12, min(self.WIDTH - border - step_w - 12, x))
                y = max(90, min(self.HEIGHT - 140, y))
                generated.append(pygame.Rect(int(x), int(y), step_w, step_h))
                x += direction * 130
                y -= step_gap_y
                if x > self.WIDTH - border - step_w - 20 or x < border + 20:
                    direction *= -1

            # Garantovaná dostupná platforma nad startem hráče.
            starter_w = 220
            starter_h = 20
            starter_x = max(border + 12, min(self.WIDTH - border - starter_w - 12, player_rect.centerx - starter_w // 2))
            starter_y = self.HEIGHT - border - 86
            starter = pygame.Rect(int(starter_x), int(starter_y), starter_w, starter_h)
            if not any(starter.colliderect(existing) for existing in generated):
                generated.append(starter)

            for _ in range(max_tries):
                if placed >= interior_count:
                    break

                w = random.choice([120, 144, 168, 192, 216, 240])
                h = 20

                x = random.randrange(border + 10, self.WIDTH - border - w - 10, 24)
                y = random.randrange(80, self.HEIGHT - 120, 24)
                candidate = pygame.Rect(x, y, w, h)

                # Nepokládej zeď přes hráče/enemy spawny (s malým okrajem).
                if any(candidate.colliderect(r.inflate(90, 90)) for r in blocked_rects):
                    continue

                # Nepřekrývej se s jinými zdmi.
                if any(candidate.colliderect(existing) for existing in generated):
                    continue

                generated.append(candidate)
                placed += 1

            return generated

        def place_on_platform(rect, platforms):
            nearest = None
            for p in platforms:
                # Ignore side walls as landing surfaces.
                if p.width <= border:
                    continue
                if rect.centerx >= p.left - 8 and rect.centerx <= p.right + 8 and p.top >= rect.top:
                    if nearest is None or p.top < nearest.top:
                        nearest = p
            if nearest:
                rect.bottom = nearest.top
                return True
            return False

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

        # Spawn hráče v horní části; po vygenerování platforem ho "přicvakneme" na nejbližší.
        spawn_x = self.WIDTH // 2 - 24
        spawn_y = 80
        player = Player(spawn_x, spawn_y, skin=selected_skin)

        attack_effects = []
        player_projectiles = []
        super_projectiles = []
        enemy_projectiles = []
        heart_rect = None
        heart_timer = random.randint(self.FPS * 8, self.FPS * 14)
        max_lives = 5
        level_manager = LevelManager()
        enemies = level_manager.load_current()
        walls = generate_level_walls(level_manager.get_level_number(), [player.rect, *[e.rect for e in enemies]])
        player.snap_to_ground(walls)
        for e in enemies:
            place_on_platform(e.rect, walls)
            if hasattr(e, "vel_y"):
                e.vel_y = 0.0
        apply_difficulty(enemies)
        level_transition_timer = 0
        level_cleared_display = 0

        font = pygame.font.SysFont(None, 24)
        wall_img = ASSETS.get_scaled('wall', (24, 24))

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
                    elif event.key == pygame.K_SPACE:
                        player.jump()
                    elif event.key == pygame.K_f:
                        a = player.attack()
                        if a:
                            kind, payload = a
                            if kind == 'melee':
                                attack_effects.append([payload, 6])
                            elif kind == 'ranged':
                                player_projectiles.append(payload)
                    elif event.key == pygame.K_v:
                        sp = player.super_attack()
                        if sp:
                            super_projectiles.append(sp)

            move_x = player.handle_input()
            player.move(move_x, walls)
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

            # homing super projectiles
            for sp in super_projectiles[:]:
                alive = True
                hit_enemy = None
                try:
                    alive, hit_enemy = sp.update(enemies, walls)
                except Exception:
                    alive = False
                if hit_enemy is not None and hit_enemy in enemies:
                    hit_enemy.hp -= getattr(sp, 'damage', 999)
                    if hit_enemy.hp <= 0:
                        enemies.remove(hit_enemy)
                if not alive:
                    super_projectiles.remove(sp)

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
                    hx = random.randint(border + 20, self.WIDTH - border - heart_size - 20)
                    hy = 80
                    heart_rect = pygame.Rect(hx, hy, heart_size, heart_size)
                    place_on_platform(heart_rect, walls)
                    heart_rect.y -= heart_rect.height
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
                    walls = generate_level_walls(level_manager.get_level_number(), [player.rect, *[e.rect for e in enemies]])
                    player.snap_to_ground(walls)
                    for e in enemies:
                        place_on_platform(e.rect, walls)
                        if hasattr(e, "vel_y"):
                            e.vel_y = 0.0
                    apply_difficulty(enemies)
                    enemy_projectiles.clear()
                    player_projectiles.clear()
                    super_projectiles.clear()
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

            # walls (use img/wall.png as repeating 24x24 tile)
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

            for sp in super_projectiles:
                try:
                    sp.draw(screen)
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
            super_cd = getattr(player, 'super_cooldown', 0)
            super_txt = font.render(f"Super(V): {'READY' if super_cd <= 0 else super_cd}", True, (220, 220, 180))
            screen.blit(super_txt, (8, 30))

            pygame.display.flip()
            clock.tick(self.FPS)

        pygame.quit()
