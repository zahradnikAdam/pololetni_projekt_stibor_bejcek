from models.team import Team
import random

class Enemy(Team):
    def __init__(self, name, color, players_info, difficulty=1):
        super().__init__(name, color, players_info)
        self.difficulty = difficulty  # 1 = lehký, 2 = střední, 3 = těžký

    def ai_move(self):
        """Jednoduchá AI pohybu nepřátelských hráčů"""
        for player in self.players:
            dx = random.randint(-1, 1) * self.difficulty
            dy = random.randint(-1, 1) * self.difficulty
            player.move(dx, dy)