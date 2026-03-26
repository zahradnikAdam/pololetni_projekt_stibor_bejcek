import pygame

class Player:
    def __init__(self, name, number, color=(0, 0, 255), position=(100, 300)):
        self.name = name
        self.number = number
        self.color = color
        self.position = list(position)  # [x, y]
        self.radius = 20

    def move(self, dx, dy):
        """Posun hráče"""
        self.position[0] += dx
        self.position[1] += dy

    def draw(self, screen):
        """Vykreslení hráče"""
        pygame.draw.circle(screen, self.color, self.position, self.radius)
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.number), True, (255, 255, 255))
        screen.blit(text, (self.position[0]-10, self.position[1]-10))
        name_text = font.render(self.name, True, (255, 255, 255))
        screen.blit(name_text, (self.position[0]-20, self.position[1]+15))