import sys
import pygame
from pygame import Rect

WIDTH = 800
HEIGHT = 600
FPS = 60


class MainMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font = pygame.font.SysFont(None, 48)
        self.small = pygame.font.SysFont(None, 22)
        self.tiny = pygame.font.SysFont(None, 20)
        self.selected = None
        self.difficulty = 'Normal'

        self.panel = Rect(WIDTH//2 - 360//2, HEIGHT//2 - 280//2, 360, 280)
        self.start_btn = Rect(WIDTH//2 - 70, self.panel.bottom - 50, 140, 40)
        self.knight_rect = Rect(self.panel.left + 30, self.panel.top + 70, 120, 120)
        self.mage_rect = Rect(self.panel.right - 150, self.panel.top + 70, 120, 120)
        self.diff_y = self.panel.bottom - 95
        self.easy_btn = Rect(self.panel.left + 20, self.diff_y, 100, 30)
        self.normal_btn = Rect(self.panel.centerx - 50, self.diff_y, 100, 30)
        self.hard_btn = Rect(self.panel.right - 120, self.diff_y, 100, 30)

        from assets import ASSETS
        self.knight_img = ASSETS.get_scaled('player_knight', (self.knight_rect.width, self.knight_rect.height))
        self.mage_img = ASSETS.get_scaled('player_mage', (self.mage_rect.width, self.mage_rect.height))

    def run(self):
        while True:
            result = self._handle_events()
            if result:
                return result
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                result = self._handle_key(event.key)
                if result:
                    return result
            if event.type == pygame.MOUSEBUTTONDOWN:
                result = self._handle_click(event.pos)
                if result:
                    return result
        return None

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit(0)
        if key == pygame.K_TAB:
            self.selected = 'Knight' if self.selected in (None, 'Mage', 'Wizard') else 'Wizard'
        if key in (pygame.K_RETURN, pygame.K_SPACE) and self.selected:
            return ('Knight' if self.selected == 'Knight' else 'Wizard', self.difficulty)
        if key == pygame.K_1:
            self.difficulty = 'Easy'
        if key == pygame.K_2:
            self.difficulty = 'Normal'
        if key == pygame.K_3:
            self.difficulty = 'Hard'
        return None

    def _handle_click(self, pos):
        if self.start_btn.collidepoint(pos) and self.selected:
            return ('Knight' if self.selected == 'Knight' else 'Wizard', self.difficulty)
        if self.knight_rect.collidepoint(pos):
            self.selected = 'Knight'
        if self.mage_rect.collidepoint(pos):
            self.selected = 'Mage'
        if self.easy_btn.collidepoint(pos):
            self.difficulty = 'Easy'
        if self.normal_btn.collidepoint(pos):
            self.difficulty = 'Normal'
        if self.hard_btn.collidepoint(pos):
            self.difficulty = 'Hard'
        return None

    def _draw_border(self, rect, active):
        color = (240, 200, 50) if active else (80, 80, 80)
        pygame.draw.rect(self.screen, color, rect.inflate(8, 8), 4, border_radius=6)

    def _draw_diff_btn(self, btn, label, active):
        bg = (240, 200, 50) if active else (70, 70, 70)
        fg = (20, 20, 20) if active else (220, 220, 220)
        pygame.draw.rect(self.screen, bg, btn, border_radius=6)
        text = self.tiny.render(label, True, fg)
        self.screen.blit(text, (btn.centerx - text.get_width()//2, btn.centery - text.get_height()//2))

    def _draw(self):
        self.screen.fill((20, 18, 22))
        pygame.draw.rect(self.screen, (28, 26, 32), self.panel, border_radius=8)
        title = self.font.render("Vyber si skin", True, (240, 240, 240))
        self.screen.blit(title, (self.panel.centerx - title.get_width()//2, self.panel.top + 12))

        if self.knight_img:
            self.screen.blit(self.knight_img, self.knight_rect.topleft)
        else:
            pygame.draw.rect(self.screen, (120, 160, 220), self.knight_rect)
        if self.mage_img:
            self.screen.blit(self.mage_img, self.mage_rect.topleft)
        else:
            pygame.draw.rect(self.screen, (160, 80, 200), self.mage_rect)

        self._draw_border(self.knight_rect, self.selected == 'Knight')
        self._draw_border(self.mage_rect, self.selected in ('Mage', 'Wizard'))

        ktxt = self.small.render('Knight', True, (220, 220, 220))
        mtxt = self.small.render('Wizard', True, (220, 220, 220))
        self.screen.blit(ktxt, (self.knight_rect.centerx - ktxt.get_width()//2, self.knight_rect.bottom + 8))
        self.screen.blit(mtxt, (self.mage_rect.centerx - mtxt.get_width()//2, self.mage_rect.bottom + 8))

        if self.selected:
            pygame.draw.rect(self.screen, (100, 220, 100), self.start_btn, border_radius=6)
            st = self.small.render('Start', True, (10, 10, 10))
        else:
            pygame.draw.rect(self.screen, (70, 70, 70), self.start_btn, border_radius=6)
            st = self.small.render('Vyber skin pro start', True, (180, 180, 180))
        self.screen.blit(st, (self.start_btn.centerx - st.get_width()//2, self.start_btn.centery - st.get_height()//2))

        hint = self.small.render('Klikni na portrét nebo stiskni Tab pro přepnutí', True, (150, 150, 150))
        self.screen.blit(hint, (self.panel.centerx - hint.get_width()//2, self.panel.bottom - 20))

        dtitle = self.tiny.render('Obtížnost (1/2/3):', True, (170, 170, 170))
        self.screen.blit(dtitle, (self.panel.left + 20, self.diff_y - 22))
        self._draw_diff_btn(self.easy_btn, 'Easy', self.difficulty == 'Easy')
        self._draw_diff_btn(self.normal_btn, 'Normal', self.difficulty == 'Normal')
        self._draw_diff_btn(self.hard_btn, 'Hard', self.difficulty == 'Hard')


class PauseMenu:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.small = pygame.font.SysFont(None, 28)
        self.tiny = pygame.font.SysFont(None, 22)
        self.resume_btn = Rect(WIDTH//2 - 90, HEIGHT//2 - 40, 180, 40)
        self.settings_btn = Rect(WIDTH//2 - 90, HEIGHT//2 + 10, 180, 40)
        self.quit_btn = Rect(WIDTH//2 - 90, HEIGHT//2 + 60, 180, 40)

    def run(self):
        while True:
            action = self._handle_events()
            if action:
                return action
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_r:
                    return 'resume'
                if event.key == pygame.K_q:
                    return 'quit'
                if event.key == pygame.K_s:
                    self._settings_loop()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.resume_btn.collidepoint(event.pos):
                    return 'resume'
                if self.settings_btn.collidepoint(event.pos):
                    self._settings_loop()
                if self.quit_btn.collidepoint(event.pos):
                    return 'quit'
        return None

    def _draw(self):
        self.screen.fill((12, 12, 16))
        title = self.small.render('PAUSED', True, (240, 240, 240))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
        pygame.draw.rect(self.screen, (100, 200, 100), self.resume_btn)
        pygame.draw.rect(self.screen, (100, 140, 220), self.settings_btn)
        pygame.draw.rect(self.screen, (200, 100, 100), self.quit_btn)
        rtxt = self.small.render('Resume (Esc / R)', True, (10, 10, 10))
        stxt = self.small.render('Settings (S)', True, (10, 10, 10))
        qtxt = self.small.render('Quit (Q)', True, (10, 10, 10))
        self.screen.blit(rtxt, (self.resume_btn.centerx - rtxt.get_width()//2, self.resume_btn.centery - rtxt.get_height()//2))
        self.screen.blit(stxt, (self.settings_btn.centerx - stxt.get_width()//2, self.settings_btn.centery - stxt.get_height()//2))
        self.screen.blit(qtxt, (self.quit_btn.centerx - qtxt.get_width()//2, self.quit_btn.centery - qtxt.get_height()//2))

    def _settings_loop(self):
        back_btn = Rect(WIDTH//2 - 90, HEIGHT - 90, 180, 40)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN):
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and back_btn.collidepoint(event.pos):
                    return

            self.screen.fill((14, 14, 20))
            title = self.small.render('SETTINGS', True, (240, 240, 240))
            self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))

            lines = [
                "Ovladani:",
                "- Pohyb: WASD / sipky",
                "- Skok: Space",
                "- Utok: F",
                "- Super utok: V",
                "- Pauza: Esc",
                "",
                "Pauza menu:",
                "- Resume: R nebo Esc",
                "- Settings: S",
                "- Quit: Q",
            ]
            y = 140
            for line in lines:
                surf = self.tiny.render(line, True, (210, 210, 210))
                self.screen.blit(surf, (WIDTH//2 - 170, y))
                y += 28

            pygame.draw.rect(self.screen, (120, 200, 120), back_btn, border_radius=6)
            btxt = self.small.render('Back', True, (10, 10, 10))
            self.screen.blit(btxt, (back_btn.centerx - btxt.get_width()//2, back_btn.centery - btxt.get_height()//2))

            pygame.display.flip()
            self.clock.tick(FPS)


def main_menu(screen, clock):
    return MainMenu(screen, clock).run()


def pause_menu(screen, clock):
    return PauseMenu(screen, clock).run()
