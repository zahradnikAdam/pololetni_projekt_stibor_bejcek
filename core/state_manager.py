import pygame
from ui.menu import Menu
from ui.hud import HUD

class StateManager:
    def __init__(self, game):
        self.game = game
        self.state = "menu"
        self.menu = Menu(game)
        self.hud = None  # nastavíme po výběru týmů

    def handle_event(self, event):
        if self.state == "menu":
            self.menu.handle_event(event)
        elif self.state == "game":
            # sem budeme později přidávat minihry a pause
            pass

    def update(self, match_engine):
        if self.state == "game":
            match_engine.update()
            # budoucí AI a minihry zde

    def draw(self, screen, match_engine):
        if self.state == "menu":
            self.menu.draw(screen)
        elif self.state == "game":
            screen.fill((0, 120, 0))  # pozadí hřiště
            if self.hud:
                self.hud.draw(screen)
            # vykreslení hráčů a enemy bude později