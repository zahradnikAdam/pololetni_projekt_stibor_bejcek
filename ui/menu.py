import pygame
import os

class Menu:
    def __init__(self, game):
        self.game = game
        self.font_title = pygame.font.Font(None, 48)
        self.font_team = pygame.font.Font(None, 36)

        # seznam týmů: (název, logo soubor)
        self.player_teams = [("Tým Modrých", "blue.png"), ("Tým Zelených", "green.png")]
        self.enemy_teams = [("Tým Červených", "red.png"), ("Tým Oranžových", "orange.png")]

        self.selected_player = 0
        self.selected_enemy = 0

        # načteme loga týmů
        self.team_logos = {}
        for name, file in self.player_teams + self.enemy_teams:
            path = os.path.join("assets", "images", file)
            self.team_logos[name] = pygame.transform.scale(pygame.image.load(path), (100, 100))

        self.state = "select_player"  # "select_player" nebo "select_enemy"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if self.state == "select_player":
                    self.selected_player = (self.selected_player + 1) % len(self.player_teams)
                else:
                    self.selected_enemy = (self.selected_enemy + 1) % len(self.enemy_teams)
            elif event.key == pygame.K_LEFT:
                if self.state == "select_player":
                    self.selected_player = (self.selected_player - 1) % len(self.player_teams)
                else:
                    self.selected_enemy = (self.selected_enemy - 1) % len(self.enemy_teams)
            elif event.key == pygame.K_RETURN:
                if self.state == "select_player":
                    self.state = "select_enemy"
                else:
                    # potvrzení týmů → start hry
                    self.game.start_match(
                        self.player_teams[self.selected_player][0],
                        self.enemy_teams[self.selected_enemy][0]
                    )

    def draw(self, screen):
        screen.fill((0, 120, 0))  # zelené hřiště

        if self.state == "select_player":
            # název sekce
            text = self.font_title.render("Vyber svůj tým", True, (255, 255, 255))
            screen.blit(text, (250, 50))

            # vykreslení týmů
            for i, (name, _) in enumerate(self.player_teams):
                color = (255, 255, 0) if i == self.selected_player else (255, 255, 255)
                x = 150 + i*200
                y = 150
                # logo
                screen.blit(self.team_logos[name], (x, y))
                # název
                name_text = self.font_team.render(name, True, color)
                screen.blit(name_text, (x, y + 110))

        elif self.state == "select_enemy":
            # název sekce
            text = self.font_title.render("Vyber soupeře", True, (255, 255, 255))
            screen.blit(text, (250, 50))

            # vykreslení nepřátelských týmů
            for i, (name, _) in enumerate(self.enemy_teams):
                color = (255, 255, 0) if i == self.selected_enemy else (255, 255, 255)
                x = 150 + i*200
                y = 150
                # logo
                screen.blit(self.team_logos[name], (x, y))
                # název
                name_text = self.font_team.render(name, True, color)
                screen.blit(name_text, (x, y + 110))