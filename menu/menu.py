"""UI objekty pro menu (OOP).

`MainMenu` a `PauseMenu` jsou samostatné třídy s vlastním stavem (co je vybrané,
co se zrovna zobrazuje) a vlastním `run()` cyklem. `Game` je používá jako
komponenty UI (kompozice), místo aby byl UI kód napsaný přímo v `Game`.
"""

import sys
import pygame
from pygame import Rect

class MainMenu:
    WIDTH = 800
    HEIGHT = 600
    FPS = 60

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.title_font = pygame.font.SysFont("Segoe UI", 62, bold=True)
        self.subtitle_font = pygame.font.SysFont("Segoe UI", 26)
        self.small = pygame.font.SysFont("Segoe UI", 22)
        self.tiny = pygame.font.SysFont("Segoe UI", 20)
        self.selected = None
        self.difficulty = 'Normal'
        self.frame = 0

        self.panel = Rect(self.WIDTH//2 - 420//2, self.HEIGHT//2 - 350//2, 420, 350)
        self.start_btn = Rect(self.WIDTH//2 - 92, self.panel.bottom - 54, 184, 44)
        self.knight_rect = Rect(self.panel.left + 34, self.panel.top + 78, 130, 130)
        self.mage_rect = Rect(self.panel.right - 164, self.panel.top + 78, 130, 130)
        self.diff_y = self.panel.bottom - 102
        self.easy_btn = Rect(self.panel.left + 20, self.diff_y, 100, 30)
        self.normal_btn = Rect(self.panel.centerx - 50, self.diff_y, 100, 30)
        self.hard_btn = Rect(self.panel.right - 120, self.diff_y, 100, 30)

        from assets import ASSETS
        self.knight_img = ASSETS.get_scaled('player_knight', (self.knight_rect.width, self.knight_rect.height))
        self.mage_img = ASSETS.get_scaled('player_mage', (self.mage_rect.width, self.mage_rect.height))

    def run(self):
        # Vykresluje menu do chvíle, než uživatel potvrdí výběr.
        while True:
            result = self._handle_events()
            if result:
                return result
            self._draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)
            self.frame += 1

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
        # Klávesové zkratky pro rychlé ovládání menu.
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
        glow = (250, 220, 90) if active else (100, 100, 115)
        border = (255, 235, 140) if active else (130, 130, 145)
        pygame.draw.rect(self.screen, glow, rect.inflate(14, 14), 3, border_radius=11)
        pygame.draw.rect(self.screen, border, rect.inflate(8, 8), 3, border_radius=9)

    def _draw_diff_btn(self, btn, label, active):
        bg = (230, 196, 92) if active else (56, 62, 78)
        fg = (24, 24, 24) if active else (226, 226, 236)
        outline = (255, 235, 155) if active else (86, 96, 126)
        pygame.draw.rect(self.screen, bg, btn, border_radius=8)
        pygame.draw.rect(self.screen, outline, btn, 2, border_radius=8)
        text = self.tiny.render(label, True, fg)
        self.screen.blit(text, (btn.centerx - text.get_width()//2, btn.centery - text.get_height()//2))

    def _draw(self):
        # gradient-like background with subtle stars
        self.screen.fill((16, 18, 28))
        for i in range(8):
            y = int((i / 8.0) * self.HEIGHT)
            shade = 22 + i * 4
            pygame.draw.rect(self.screen, (12, shade, 36 + i * 3), Rect(0, y, self.WIDTH, self.HEIGHT // 8 + 2))
        for i in range(18):
            x = (i * 47 + self.frame * (1 + (i % 3))) % self.WIDTH
            y = (i * 31 + self.frame // 2) % self.HEIGHT
            pygame.draw.circle(self.screen, (190, 200, 255), (x, y), 1)

        shadow = self.panel.inflate(20, 20)
        pygame.draw.rect(self.screen, (8, 10, 18), shadow, border_radius=18)
        pygame.draw.rect(self.screen, (30, 34, 48), self.panel, border_radius=16)
        pygame.draw.rect(self.screen, (78, 90, 120), self.panel, 2, border_radius=16)

        title = self.title_font.render("Dungeon Arena", True, (244, 244, 252))
        subtitle = self.subtitle_font.render("Vyber hrdinu a obtiznost", True, (188, 196, 220))
        title_y = self.panel.top - 88
        subtitle_y = title_y + title.get_height() - 2
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, title_y))
        self.screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, subtitle_y))

        head = self.small.render("Vyber si skin", True, (235, 235, 242))
        self.screen.blit(head, (self.panel.centerx - head.get_width()//2, self.panel.top + 24))

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

        ktxt = self.small.render('Knight', True, (224, 224, 234))
        mtxt = self.small.render('Wizard', True, (224, 224, 234))
        self.screen.blit(ktxt, (self.knight_rect.centerx - ktxt.get_width()//2, self.knight_rect.bottom + 8))
        self.screen.blit(mtxt, (self.mage_rect.centerx - mtxt.get_width()//2, self.mage_rect.bottom + 8))

        if self.selected:
            pygame.draw.rect(self.screen, (96, 214, 122), self.start_btn, border_radius=10)
            pygame.draw.rect(self.screen, (194, 255, 194), self.start_btn, 2, border_radius=10)
            st = self.small.render('Start Game', True, (10, 20, 10))
        else:
            pygame.draw.rect(self.screen, (70, 74, 86), self.start_btn, border_radius=10)
            pygame.draw.rect(self.screen, (120, 126, 146), self.start_btn, 2, border_radius=10)
            st = self.small.render('Vyber skin pro start', True, (196, 196, 208))
        self.screen.blit(st, (self.start_btn.centerx - st.get_width()//2, self.start_btn.centery - st.get_height()//2))

        hint = self.tiny.render('Klikni na portrét nebo stiskni Tab pro přepnutí', True, (168, 172, 188))
        # Place helper text below panel to avoid overlap with controls.
        hint_y = self.panel.bottom + 10
        self.screen.blit(hint, (self.panel.centerx - hint.get_width()//2, hint_y))

        self._draw_diff_btn(self.easy_btn, 'Easy', self.difficulty == 'Easy')
        self._draw_diff_btn(self.normal_btn, 'Normal', self.difficulty == 'Normal')
        self._draw_diff_btn(self.hard_btn, 'Hard', self.difficulty == 'Hard')


class PauseMenu:
    WIDTH = 800
    HEIGHT = 600
    FPS = 60

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.small = pygame.font.SysFont(None, 28)
        self.tiny = pygame.font.SysFont(None, 22)
        self.resume_btn = Rect(self.WIDTH//2 - 90, self.HEIGHT//2 - 40, 180, 40)
        self.settings_btn = Rect(self.WIDTH//2 - 90, self.HEIGHT//2 + 10, 180, 40)
        self.quit_btn = Rect(self.WIDTH//2 - 90, self.HEIGHT//2 + 60, 180, 40)

    def run(self):
        # Pauza blokuje hru, dokud hráč nezvolí resume/quit.
        while True:
            action = self._handle_events()
            if action:
                return action
            self._draw()
            pygame.display.flip()
            self.clock.tick(self.FPS)

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
        self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, self.HEIGHT//2 - 100))
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
        back_btn = Rect(self.WIDTH//2 - 90, self.HEIGHT - 90, 180, 40)
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
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 70))

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
                self.screen.blit(surf, (self.WIDTH//2 - 170, y))
                y += 28

            pygame.draw.rect(self.screen, (120, 200, 120), back_btn, border_radius=6)
            btxt = self.small.render('Back', True, (10, 10, 10))
            self.screen.blit(btxt, (back_btn.centerx - btxt.get_width()//2, back_btn.centery - btxt.get_height()//2))

            pygame.display.flip()
            self.clock.tick(self.FPS)
