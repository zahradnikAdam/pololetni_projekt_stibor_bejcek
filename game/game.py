"""Aplikační (OOP) „orchestrátor“.

Třída `Game` drží běh programu pohromadě – vlastní hlavní smyčku a skládá
spolu ostatní objekty (kompozice):
- `Player` (stav hráče),
- `LevelManager` (stav postupu),
- seznam `Enemy` instancí,
- jednoduché datové objekty jako projektily/pickupy.

`Game` sám není „entita“ jako hráč nebo enemy; je to koordinátor, který volá
`update()/draw()` na objektech a spravuje jejich životní cyklus.
"""

import pygame
import random
from player.player import Player
from game.level import LevelManager
from menu.menu import MainMenu, PauseMenu
from assets import ASSETS


class Game:
    def __init__(self, width=800, height=600, fps=60):
        self.WIDTH = width
        self.HEIGHT = height
        self.FPS = fps
        self.border = 24

    def _build_border_walls(self):
        return [
            pygame.Rect(0, self.HEIGHT - self.border, self.WIDTH, self.border),  # floor
            pygame.Rect(0, 0, self.border, self.HEIGHT),  # left wall
            pygame.Rect(self.WIDTH - self.border, 0, self.border, self.HEIGHT),  # right wall
        ]

    def _generate_level_walls(self, level_no, blocked_rects=None):
        blocked_rects = blocked_rects or []
        generated = self._build_border_walls()
        player_rect = blocked_rects[0] if blocked_rects else pygame.Rect(self.WIDTH // 2 - 24, 80, 48, 48)
        min_passage_width = 72
        min_vertical_gap = 34
        side_margin = 72
        max_jump_up = 125
        max_jump_horizontal = 180
        # Random guaranteed passage: every generated level gets a different walkable corridor.
        corridor_half = 44
        band_h = 80
        corridor_points = []
        y_mark = self.HEIGHT - self.border - 20
        x_mark = random.randint(self.border + 70, self.WIDTH - self.border - 70)
        while y_mark >= 40:
            corridor_points.append((x_mark, y_mark))
            x_mark = max(
                self.border + 70,
                min(self.WIDTH - self.border - 70, x_mark + random.randint(-140, 140))
            )
            y_mark -= band_h

        def corridor_x_for_y(y):
            if not corridor_points:
                return self.WIDTH // 2
            for i in range(len(corridor_points) - 1):
                x1, y1 = corridor_points[i]
                x2, y2 = corridor_points[i + 1]
                if y1 >= y >= y2:
                    denom = max(1, y1 - y2)
                    t = (y1 - y) / denom
                    return int(round(x1 + (x2 - x1) * t))
            return corridor_points[-1][0]

        def is_too_close_to_existing(candidate):
            # Keep enough space from side borders so visible gaps are truly passable.
            if candidate.left < self.border + side_margin:
                return True
            if candidate.right > self.WIDTH - self.border - side_margin:
                return True

            # Never place a platform across the guaranteed random corridor.
            mid_y = candidate.centery
            cx = corridor_x_for_y(mid_y)
            if candidate.left < cx + corridor_half and candidate.right > cx - corridor_half:
                return True

            for existing in generated:
                # side walls / floor keep their default behavior
                if existing.width <= self.border:
                    continue
                if existing.height > 30:
                    continue
                if candidate.colliderect(existing):
                    return True

                # Platforms on a similar height should not create tiny horizontal gaps.
                similar_height = abs(candidate.top - existing.top) <= min_vertical_gap
                if similar_height:
                    horizontal_gap = max(existing.left - candidate.right, candidate.left - existing.right)
                    if 0 <= horizontal_gap < min_passage_width:
                        return True

            return False

        def is_reachable_candidate(candidate):
            # Low platforms are naturally reachable from ground movement/jump.
            low_band_top = self.HEIGHT - self.border - 170
            if candidate.top >= low_band_top:
                return True

            # Otherwise it must be reachable from at least one lower platform.
            for p in generated:
                if p.width <= self.border or p.height > 30:
                    continue
                if p.top <= candidate.top:
                    continue

                vertical_up = p.top - candidate.top
                if vertical_up > max_jump_up:
                    continue

                horizontal_gap = max(p.left - candidate.right, candidate.left - p.right)
                if horizontal_gap <= max_jump_horizontal:
                    return True

            return False

        # Náhodné platformy: kombinace "schodů" + náhodných platforem.
        interior_count = min(6, 2 + level_no)
        max_tries = 320
        placed = 0

        # Základní schody, aby byly platformy vždy dosažitelné skokem.
        step_w = 148
        step_h = 20
        step_gap_y = 64
        x = self.border + 40
        y = self.HEIGHT - self.border - 72
        direction = 1
        for _ in range(5):
            x = max(self.border + side_margin, min(self.WIDTH - self.border - side_margin - step_w, x))
            y = max(90, min(self.HEIGHT - 140, y))
            step_candidate = pygame.Rect(int(x), int(y), step_w, step_h)
            if not is_too_close_to_existing(step_candidate) and is_reachable_candidate(step_candidate):
                generated.append(step_candidate)
            x += direction * 230
            y -= step_gap_y
            if x > self.WIDTH - self.border - side_margin - step_w or x < self.border + side_margin:
                direction *= -1

        # Garantovaná dostupná platforma nad startem hráče.
        starter_w = 220
        starter_h = 20
        starter_x = max(self.border + side_margin, min(self.WIDTH - self.border - side_margin - starter_w, player_rect.centerx - starter_w // 2))
        starter_y = self.HEIGHT - self.border - 86
        starter = pygame.Rect(int(starter_x), int(starter_y), starter_w, starter_h)
        if not is_too_close_to_existing(starter) and is_reachable_candidate(starter):
            generated.append(starter)

        for _ in range(max_tries):
            if placed >= interior_count:
                break

            w = random.choice([120, 144, 168, 192, 216, 240])
            h = 20

            x = random.randrange(self.border + side_margin, self.WIDTH - self.border - side_margin - w, 24)
            y = random.randrange(120, self.HEIGHT - 120, 24)
            candidate = pygame.Rect(x, y, w, h)

            # Nepokládej zeď přes hráče/enemy spawny (s malým okrajem).
            if any(candidate.colliderect(r.inflate(90, 90)) for r in blocked_rects):
                continue

            # Nepřekrývej se s jinými zdmi.
            if is_too_close_to_existing(candidate):
                continue
            if not is_reachable_candidate(candidate):
                continue

            generated.append(candidate)
            placed += 1

        return generated

    def _place_on_platform(self, rect, platforms):
        nearest = None
        for p in platforms:
            # Ignore side walls as landing surfaces.
            if p.width <= self.border:
                continue
            if rect.centerx >= p.left - 8 and rect.centerx <= p.right + 8 and p.top >= rect.top:
                if nearest is None or p.top < nearest.top:
                    nearest = p
        if nearest:
            rect.bottom = nearest.top
            return True
        return False

    def _apply_difficulty(self, enemies_list, difficulty, level_manager):
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

    def _show_end_screen(self, screen, clock, won):
        title_font = pygame.font.SysFont("Segoe UI", 58, bold=True)
        sub_font = pygame.font.SysFont("Segoe UI", 28)
        small_font = pygame.font.SysFont("Segoe UI", 22)
        frame = 0
        min_show_frames = int(self.FPS * 0.8)  # avoid instant close from buffered input
        panel = pygame.Rect(self.WIDTH // 2 - 260, self.HEIGHT // 2 - 130, 520, 260)
        replay_btn = pygame.Rect(panel.centerx - 95, panel.bottom - 92, 190, 42)

        while True:
            mouse_pos = pygame.mouse.get_pos()
            hover_replay = replay_btn.collidepoint(mouse_pos)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if frame < min_show_frames:
                    continue
                if event.type == pygame.KEYUP and event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                    return "quit"
                if event.type == pygame.KEYUP and event.key == pygame.K_r:
                    return "restart"
                if event.type == pygame.MOUSEBUTTONUP:
                    if hover_replay:
                        return "restart"
                    return "quit"

            base = (18, 28, 24) if won else (30, 16, 20)
            screen.fill(base)

            # jemný gradient
            for i in range(9):
                y = int((i / 9.0) * self.HEIGHT)
                if won:
                    c = (18 + i * 3, 34 + i * 5, 28 + i * 3)
                else:
                    c = (34 + i * 4, 18 + i * 2, 24 + i * 3)
                pygame.draw.rect(screen, c, pygame.Rect(0, y, self.WIDTH, self.HEIGHT // 9 + 2))

            # částicové tečky
            for i in range(30):
                x = (i * 53 + frame * (1 + (i % 4))) % self.WIDTH
                y = (i * 37 + frame // 2) % self.HEIGHT
                col = (200, 255, 210) if won else (255, 190, 190)
                pygame.draw.circle(screen, col, (x, y), 1)

            pygame.draw.rect(screen, (16, 16, 24), panel, border_radius=16)
            pygame.draw.rect(screen, (120, 140, 170), panel, 2, border_radius=16)

            if won:
                title = title_font.render("Viteztvi!", True, (244, 255, 228))
                line1 = sub_font.render("Dekuji za dohrani hry.", True, (218, 236, 220))
                line2 = small_font.render("Tvoje legenda v dungeonu pokracuje...", True, (182, 210, 186))
            else:
                title = title_font.render("Konec hry", True, (255, 225, 225))
                line1 = sub_font.render("Nevadi, zkus to znovu.", True, (230, 210, 210))
                line2 = small_font.render("Kazdy hrdina nekdy padne.", True, (214, 182, 182))

            btn_bg = (110, 210, 135) if hover_replay and frame >= min_show_frames else (74, 112, 86)
            btn_fg = (8, 20, 10) if hover_replay and frame >= min_show_frames else (220, 240, 225)
            pygame.draw.rect(screen, btn_bg, replay_btn, border_radius=10)
            pygame.draw.rect(screen, (180, 230, 190), replay_btn, 2, border_radius=10)
            replay_txt = small_font.render("Hrat znovu (R)", True, btn_fg)
            screen.blit(replay_txt, (replay_btn.centerx - replay_txt.get_width() // 2, replay_btn.centery - replay_txt.get_height() // 2))

            hint = small_font.render("Enter / Esc / klik mimo tlacitko = konec", True, (185, 185, 205))

            screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, panel.top + 28))
            screen.blit(line1, (self.WIDTH // 2 - line1.get_width() // 2, panel.top + 112))
            screen.blit(line2, (self.WIDTH // 2 - line2.get_width() // 2, panel.top + 150))
            screen.blit(hint, (self.WIDTH // 2 - hint.get_width() // 2, panel.bottom - 30))

            pygame.display.flip()
            clock.tick(self.FPS)
            frame += 1

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

        menu_result = MainMenu(screen, clock).run()
        if isinstance(menu_result, tuple):
            selected_skin, difficulty = menu_result
        else:
            selected_skin, difficulty = menu_result, 'Normal'

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
        shield_rect = None
        shield_timer = random.randint(self.FPS * 12, self.FPS * 20)
        power_rect = None
        power_timer = random.randint(self.FPS * 10, self.FPS * 18)
        shield_active_timer = 0
        power_active_timer = 0
        max_lives = 5
        level_manager = LevelManager()
        enemies = level_manager.load_current()
        walls = self._generate_level_walls(level_manager.get_level_number(), [player.rect, *[e.rect for e in enemies]])
        player.snap_to_ground(walls)
        player.spawn_pos = (int(player.rect.x), int(player.rect.y))
        for e in enemies:
            self._place_on_platform(e.rect, walls)
            if hasattr(e, "vel_y"):
                e.vel_y = 0.0
        self._apply_difficulty(enemies, difficulty, level_manager)
        level_transition_timer = 0
        level_cleared_display = 0

        font = pygame.font.SysFont(None, 24)
        wall_img = ASSETS.get_scaled('wall', (24, 24))
        game_won = False

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        action = PauseMenu(screen, clock).run()
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
                        dmg_mul = 2 if power_active_timer > 0 else 1
                        e.hp -= player.attack_damage * dmg_mul
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
                        dmg_mul = 2 if power_active_timer > 0 else 1
                        e.hp -= getattr(p, 'damage', player.attack_damage) * dmg_mul
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
                    # Super útok: Dragon na 5 ran, Rat na 2 rány.
                    if hit_enemy.__class__.__name__ == "Dragon":
                        super_damage = max(1, (int(getattr(hit_enemy, 'max_hp', hit_enemy.hp)) + 4) // 5)
                    elif hit_enemy.__class__.__name__ == "Rat":
                        super_damage = max(1, (int(getattr(hit_enemy, 'max_hp', hit_enemy.hp)) + 1) // 2)
                    else:
                        super_damage = int(getattr(sp, 'damage', 2))
                    if power_active_timer > 0:
                        super_damage *= 2
                    hit_enemy.hp -= super_damage
                    if hit_enemy.hp <= 0:
                        enemies.remove(hit_enemy)
                if not alive:
                    super_projectiles.remove(sp)

            # enemy melee + ranged attacks
            for e in enemies:
                # melee: damage on contact (with per-enemy cooldown)
                if getattr(e, 'attack_type', None) == 'melee':
                    dist = pygame.Vector2(player.rect.center).distance_to(pygame.Vector2(e.rect.center))
                    melee_range = float(getattr(e, 'attack_range', 85))
                    if dist <= melee_range and getattr(e, 'attack_cooldown', 0) <= 0:
                        if shield_active_timer <= 0:
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
                # rat special burst
                if hasattr(e, "try_special_attack"):
                    try:
                        shots = e.try_special_attack(player)
                    except Exception:
                        shots = []
                    for shot in shots:
                        enemy_projectiles.append(shot)

            # heart spawn + pickup
            heart_size = 40
            if heart_rect is None:
                heart_timer -= 1
                if heart_timer <= 0:
                    hx = random.randint(self.border + 20, self.WIDTH - self.border - heart_size - 20)
                    hy = 80
                    heart_rect = pygame.Rect(hx, hy, heart_size, heart_size)
                    self._place_on_platform(heart_rect, walls)
                    heart_rect.y -= heart_rect.height
                    heart_timer = random.randint(self.FPS * 10, self.FPS * 18)
            else:
                if player.rect.colliderect(heart_rect):
                    player.lives = min(max_lives, player.lives + 1)
                    heart_rect = None

            # shield spawn + pickup (dočasná imunita)
            shield_size = 40
            if shield_rect is None:
                shield_timer -= 1
                if shield_timer <= 0:
                    sx = random.randint(self.border + 20, self.WIDTH - self.border - shield_size - 20)
                    sy = 80
                    shield_rect = pygame.Rect(sx, sy, shield_size, shield_size)
                    self._place_on_platform(shield_rect, walls)
                    shield_rect.y -= shield_rect.height
                    shield_timer = random.randint(self.FPS * 14, self.FPS * 24)
            else:
                if player.rect.colliderect(shield_rect):
                    shield_active_timer = int(self.FPS * 6)
                    shield_rect = None

            # power spawn + pickup (dočasný bonus damage)
            power_size = 40
            if power_rect is None:
                power_timer -= 1
                if power_timer <= 0:
                    px = random.randint(self.border + 20, self.WIDTH - self.border - power_size - 20)
                    py = 80
                    power_rect = pygame.Rect(px, py, power_size, power_size)
                    self._place_on_platform(power_rect, walls)
                    power_rect.y -= power_rect.height
                    power_timer = random.randint(self.FPS * 12, self.FPS * 22)
            else:
                if player.rect.colliderect(power_rect):
                    power_active_timer = int(self.FPS * 7)
                    power_rect = None

            if shield_active_timer > 0:
                shield_active_timer -= 1
            if power_active_timer > 0:
                power_active_timer -= 1

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
                    if shield_active_timer <= 0:
                        player.take_damage(getattr(p, 'damage', 1))
                    enemy_projectiles.remove(p)

            # game over on 0 lives
            if player.lives <= 0:
                running = False

            # Trigger level clear transition only once per clear event.
            if not enemies and level_transition_timer <= 0 and level_cleared_display <= 0:
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
                    walls = self._generate_level_walls(level_manager.get_level_number(), [player.rect, *[e.rect for e in enemies]])
                    player.snap_to_ground(walls)
                    player.spawn_pos = (int(player.rect.x), int(player.rect.y))
                    for e in enemies:
                        self._place_on_platform(e.rect, walls)
                        if hasattr(e, "vel_y"):
                            e.vel_y = 0.0
                    self._apply_difficulty(enemies, difficulty, level_manager)
                    enemy_projectiles.clear()
                    player_projectiles.clear()
                    super_projectiles.clear()
                    heart_rect = None
                    shield_rect = None
                    power_rect = None
                    level_cleared_display = 0

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

            # draw shield pickup
            if shield_rect:
                shield_img = ASSETS.get_scaled('shield', (shield_rect.width, shield_rect.height))
                if shield_img:
                    screen.blit(shield_img, shield_rect.topleft)
                else:
                    pygame.draw.rect(screen, (80, 170, 255), shield_rect, border_radius=6)
                    pygame.draw.rect(screen, (220, 240, 255), shield_rect, 2, border_radius=6)

            # draw power pickup
            if power_rect:
                power_img = ASSETS.get_scaled('power', (power_rect.width, power_rect.height))
                if power_img:
                    screen.blit(power_img, power_rect.topleft)
                else:
                    pygame.draw.rect(screen, (255, 195, 65), power_rect, border_radius=6)
                    pygame.draw.rect(screen, (255, 245, 200), power_rect, 2, border_radius=6)

            if not enemies and not level_manager.has_next() and level_cleared_display > 0:
                victory_surf = font.render("Vítězství! Všechny úrovně dokončeny.", True, (240, 220, 100))
                screen.blit(victory_surf, (self.WIDTH//2 - victory_surf.get_width()//2, self.HEIGHT//2 - 20))
                level_cleared_display -= 1
                if level_cleared_display <= 0:
                    game_won = True
                    running = False

            if level_cleared_display > 0 and level_manager.has_next():
                msg = f"Level {level_manager.get_level_number() - 1} cleared! Přechod na další..."
                txt = font.render(msg, True, (220, 220, 220))
                screen.blit(txt, (self.WIDTH//2 - txt.get_width()//2, 40))
                level_cleared_display -= 1

            for eff in attack_effects:
                pygame.draw.rect(screen, (255, 180, 60), eff[0])

            player.draw(screen)

            hp_surf = font.render(f"HP: {player.hp}/{getattr(player, 'max_hp', player.hp)}   Lives: {getattr(player, 'lives', 0)}", True, (220, 220, 220))
            screen.blit(hp_surf, (8, 8))
            super_cd = getattr(player, 'super_cooldown', 0)
            super_txt = font.render(f"Super(V): {'READY' if super_cd <= 0 else super_cd}", True, (220, 220, 180))
            screen.blit(super_txt, (8, 30))
            if shield_active_timer > 0:
                shield_txt = font.render(f"Shield: {shield_active_timer // self.FPS + 1}s", True, (160, 215, 255))
                screen.blit(shield_txt, (8, 52))
            if power_active_timer > 0:
                power_txt = font.render(f"Power: {power_active_timer // self.FPS + 1}s", True, (255, 220, 120))
                screen.blit(power_txt, (8, 74))

            pygame.display.flip()
            clock.tick(self.FPS)

        end_action = self._show_end_screen(screen, clock, game_won)
        pygame.quit()
        if end_action == "restart":
            self.run()
