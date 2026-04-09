import sys
import pygame
from pygame import Rect

WIDTH = 800
HEIGHT = 600
FPS = 60


def main_menu(screen, clock):
    font = pygame.font.SysFont(None, 48)
    small = pygame.font.SysFont(None, 22)
    tiny = pygame.font.SysFont(None, 20)
    selected = None
    difficulty = 'Normal'

    panel = Rect(WIDTH//2 - 360//2, HEIGHT//2 - 280//2, 360, 280)
    start_btn = Rect(WIDTH//2 - 70, panel.bottom - 50, 140, 40)
    knight_rect = Rect(panel.left + 30, panel.top + 70, 120, 120)
    mage_rect = Rect(panel.right - 150, panel.top + 70, 120, 120)
    # difficulty buttons
    diff_y = panel.bottom - 95
    easy_btn = Rect(panel.left + 20, diff_y, 100, 30)
    normal_btn = Rect(panel.centerx - 50, diff_y, 100, 30)
    hard_btn = Rect(panel.right - 120, diff_y, 100, 30)

    # try load previews from assets
    from assets import ASSETS
    knight_img = ASSETS.get_scaled('player_knight', (knight_rect.width, knight_rect.height))
    mage_img = ASSETS.get_scaled('player_mage', (mage_rect.width, mage_rect.height))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_TAB:
                    # toggle selection
                    if selected is None:
                        selected = 'Knight'
                    else:
                        selected = 'Wizard' if selected == 'Knight' else 'Knight'
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected:
                        skin = 'Knight' if selected == 'Knight' else 'Wizard'
                        return (skin, difficulty)
                if event.key == pygame.K_1:
                    difficulty = 'Easy'
                if event.key == pygame.K_2:
                    difficulty = 'Normal'
                if event.key == pygame.K_3:
                    difficulty = 'Hard'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if start_btn.collidepoint((mx, my)) and selected:
                    skin = 'Knight' if selected == 'Knight' else 'Wizard'
                    return (skin, difficulty)
                if knight_rect.collidepoint((mx, my)):
                    selected = 'Knight'
                if mage_rect.collidepoint((mx, my)):
                    selected = 'Mage'
                if easy_btn.collidepoint((mx, my)):
                    difficulty = 'Easy'
                if normal_btn.collidepoint((mx, my)):
                    difficulty = 'Normal'
                if hard_btn.collidepoint((mx, my)):
                    difficulty = 'Hard'

        # background panel
        screen.fill((20, 18, 22))
        pygame.draw.rect(screen, (28, 26, 32), panel, border_radius=8)
        title = font.render("Vyber si skin", True, (240, 240, 240))
        screen.blit(title, (panel.centerx - title.get_width()//2, panel.top + 12))

        # portraits
        # Knight
        if knight_img:
            screen.blit(knight_img, knight_rect.topleft)
        else:
            pygame.draw.rect(screen, (120, 160, 220), knight_rect)
        # Mage/Wizard
        if mage_img:
            screen.blit(mage_img, mage_rect.topleft)
        else:
            pygame.draw.rect(screen, (160, 80, 200), mage_rect)

        # borders to show selection
        def draw_border(r, active):
            color = (240, 200, 50) if active else (80, 80, 80)
            pygame.draw.rect(screen, color, r.inflate(8, 8), 4, border_radius=6)

        draw_border(knight_rect, selected == 'Knight')
        draw_border(mage_rect, selected == 'Mage' or selected == 'Wizard')

        # labels
        ktxt = small.render('Knight', True, (220, 220, 220))
        mtxt = small.render('Wizard', True, (220, 220, 220))
        screen.blit(ktxt, (knight_rect.centerx - ktxt.get_width()//2, knight_rect.bottom + 8))
        screen.blit(mtxt, (mage_rect.centerx - mtxt.get_width()//2, mage_rect.bottom + 8))

        # start button (disabled until selection)
        if selected:
            pygame.draw.rect(screen, (100, 220, 100), start_btn, border_radius=6)
            st = small.render('Start', True, (10, 10, 10))
        else:
            pygame.draw.rect(screen, (70, 70, 70), start_btn, border_radius=6)
            st = small.render('Vyber skin pro start', True, (180, 180, 180))
        screen.blit(st, (start_btn.centerx - st.get_width()//2, start_btn.centery - st.get_height()//2))

        hint = small.render('Klikni na portrét nebo stiskni Tab pro přepnutí', True, (150,150,150))
        screen.blit(hint, (panel.centerx - hint.get_width()//2, panel.bottom - 20))

        # difficulty UI
        dtitle = tiny.render('Obtížnost (1/2/3):', True, (170, 170, 170))
        screen.blit(dtitle, (panel.left + 20, diff_y - 22))

        def draw_diff(btn, label, active):
            bg = (70, 70, 70)
            fg = (220, 220, 220)
            if active:
                bg = (240, 200, 50)
                fg = (20, 20, 20)
            pygame.draw.rect(screen, bg, btn, border_radius=6)
            t = tiny.render(label, True, fg)
            screen.blit(t, (btn.centerx - t.get_width()//2, btn.centery - t.get_height()//2))

        draw_diff(easy_btn, 'Easy', difficulty == 'Easy')
        draw_diff(normal_btn, 'Normal', difficulty == 'Normal')
        draw_diff(hard_btn, 'Hard', difficulty == 'Hard')

        pygame.display.flip()
        clock.tick(FPS)


def pause_menu(screen, clock):
    small = pygame.font.SysFont(None, 28)
    resume_btn = Rect(WIDTH//2 - 80, HEIGHT//2 - 20, 160, 40)
    quit_btn = Rect(WIDTH//2 - 80, HEIGHT//2 + 40, 160, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'resume'
                if event.key == pygame.K_q:
                    return 'quit'
                if event.key == pygame.K_r:
                    return 'resume'
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if resume_btn.collidepoint((mx, my)):
                    return 'resume'
                if quit_btn.collidepoint((mx, my)):
                    return 'quit'

        screen.fill((12, 12, 16))
        title = small.render('PAUSED', True, (240, 240, 240))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 80))

        pygame.draw.rect(screen, (100, 200, 100), resume_btn)
        pygame.draw.rect(screen, (200, 100, 100), quit_btn)
        rtxt = small.render('Resume (Esc / R)', True, (10, 10, 10))
        qtxt = small.render('Quit (Q)', True, (10, 10, 10))
        screen.blit(rtxt, (resume_btn.centerx - rtxt.get_width()//2, resume_btn.centery - rtxt.get_height()//2))
        screen.blit(qtxt, (quit_btn.centerx - qtxt.get_width()//2, quit_btn.centery - qtxt.get_height()//2))

        pygame.display.flip()
        clock.tick(FPS)
