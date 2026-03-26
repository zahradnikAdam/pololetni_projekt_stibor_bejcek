import pygame
import random
from minigames.base_minigame import BaseMiniGame

class ShootingMiniGame(BaseMiniGame):
    def __init__(self, match_engine):
        super().__init__(match_engine)
        self.target_pos = [(random.randint(100, 700), random.randint(100, 500)) for _ in range(20)]
        self.clicked_targets = []

    def play(self, mouse_pos):
        for pos in self.target_pos:
            if pos not in self.clicked_targets:
                rect = pygame.Rect(pos[0]-10, pos[1]-10, 20, 20)
                if rect.collidepoint(mouse_pos):
                    self.clicked_targets.append(pos)
                    # náhodně gól nebo chytne gólman
                    if random.random() > 0.5:
                        self.match_engine.score[0] += 1
                    self.check_completion()

    def check_completion(self):
        if len(self.clicked_targets) >= len(self.target_pos):
            self.completed = True

    def draw(self, screen):
        for pos in self.target_pos:
            color = (0, 255, 0) if pos in self.clicked_targets else (255, 0, 0)
            pygame.draw.circle(screen, color, pos, 10)
        font = pygame.font.Font(None, 36)
        text = font.render("Střílej na bránu!", True, (255, 255, 255))
        screen.blit(text, (250, 20))