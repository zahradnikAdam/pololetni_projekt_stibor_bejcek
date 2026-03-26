import pygame
import sys

from core.state_manager import StateManager
from core.match_engine import MatchEngine


class Game:
    def __init__(self):
        pygame.init()

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Football Game")

        self.clock = pygame.time.Clock()
        self.running = True

        self.state_manager = StateManager(self)
        self.match_engine = MatchEngine()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.state_manager.handle_event(event)

    def update(self):
        self.state_manager.update(self.match_engine)

    def draw(self):
        self.screen.fill((0, 120, 0))  # zelené hřiště

        self.state_manager.draw(self.screen, self.match_engine)

        pygame.display.flip()