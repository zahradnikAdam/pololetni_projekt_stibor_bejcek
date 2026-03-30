import pygame
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

        selected_skin = main_menu(screen, clock)
        player = Player(self.WIDTH // 2 - 24, self.HEIGHT // 2 - 24, skin=selected_skin)

        attack_effects = []
        level_manager = LevelManager()
        enemies = level_manager.load_current()
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
                    elif event.key == pygame.K_SPACE:
                        a = player.attack()
                        if a:
                            attack_effects.append([a, 6])

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

            # background
            bg = ASSETS.get('background')
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

            hp_surf = font.render(f"HP: {player.hp}", True, (220, 220, 220))
            screen.blit(hp_surf, (8, 8))

            pygame.display.flip()
            clock.tick(self.FPS)

        pygame.quit()
