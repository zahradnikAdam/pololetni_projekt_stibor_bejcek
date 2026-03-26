import pygame

class HUD:
    def __init__(self, match_engine, player_team, enemy_team):
        self.match_engine = match_engine
        self.player_team = player_team
        self.enemy_team = enemy_team
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        # Skóre
        score_text = self.font.render(
            f"{self.match_engine.score[0]} : {self.match_engine.score[1]}", True, (255, 255, 255)
        )
        screen.blit(score_text, (350, 10))

        # Čas
        time_text = self.font.render(
            f"Time: {int(self.match_engine.time)}", True, (255, 255, 255)
        )
        screen.blit(time_text, (20, 10))

        # Držení míče
        pygame.draw.rect(screen, (255, 255, 255), (200, 550, 400, 20), 2)
        pygame.draw.rect(
            screen, (0, 0, 255), (200, 550, self.match_engine.possession * 4, 20)
        )

        # Názvy týmů
        player_text = self.font.render(self.player_team.name, True, self.player_team.color)
        enemy_text = self.font.render(self.enemy_team.name, True, self.enemy_team.color)
        screen.blit(player_text, (150, 560))
        screen.blit(enemy_text, (600, 560))