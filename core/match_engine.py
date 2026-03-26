import random
import pygame


class MatchEngine:
    def __init__(self):
        self.time = 0
        self.score = [0, 0]
        self.possession = 50  # %

    def update(self):
        # čas běží
        self.time += 1 / 60

        # náhodná změna držení míče
        self.possession += random.randint(-1, 1)
        self.possession = max(0, min(100, self.possession))

        # náhodná šance na gól
        if random.random() < 0.001:
            if self.possession > 50:
                self.score[0] += 1
            else:
                self.score[1] += 1

    def draw(self, screen):
        font = pygame.font.Font(None, 36)

        # skóre
        score_text = font.render(f"{self.score[0]} : {self.score[1]}", True, (255, 255, 255))
        screen.blit(score_text, (370, 20))

        # čas
        time_text = font.render(f"Time: {int(self.time)}", True, (255, 255, 255))
        screen.blit(time_text, (20, 20))

        # držení míče
        pygame.draw.rect(screen, (255, 255, 255), (200, 550, 400, 20), 2)
        pygame.draw.rect(screen, (0, 0, 255), (200, 550, self.possession * 4, 20))