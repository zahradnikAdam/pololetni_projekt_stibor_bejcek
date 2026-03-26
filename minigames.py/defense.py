import pygame
import random
from minigames.base_minigame import BaseMiniGame

class DefenseMiniGame(BaseMiniGame):
    def __init__(self, match_engine):
        super().__init__(match_engine)
        self.enemy_pos = [(random.randint(100, 700), random.randint(100, 500)) for _ in range(10)]
        self.stopped = []

    def play(self, mouse_pos):
        for pos in self.enemy_pos:
            if pos not in self.stopped:
                rect = pygame.Rect(pos[0]-15, pos[1]-15, 30, 30)
                if rect.collidepoint(mouse_pos):
                    self.stopped.append(pos)
                    self.check_completion()

    def check_completion(self):
        if len(self.stopped) >= len(self.enemy_pos):
            self.completed = True

    def draw(self, screen):
        for pos in self.enemy_pos:
            color = (0, 0, 255) if pos in self.stopped else (255, 165, 0)
            pygame.draw.rect(screen, color, (pos[0]-15, pos[1]-15, 30, 30))
        font = pygame.font.Font(None, 36)
        text = font.render("Zastav soupeře!", True, (255, 255, 255))
        screen.blit(text, (250, 20))