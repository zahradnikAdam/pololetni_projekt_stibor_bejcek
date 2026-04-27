"""`LevelManager` – malý stavový objekt (OOP).

Drží:
- data o levelech (konfigurace),
- aktuální index (`current`),
a poskytuje metody, jak se v nich posouvat.

Je to „manager“ objekt: nemá render ani fyziku, jen spravuje stav postupu.
"""

from game.enemy import Slime, Bat, Skeleton, Rat, Dragon


class LevelManager:
    def __init__(self):
        # Každý level: seznam tuple (enemy_class, x, y)
        self.levels = [
            [(Slime, 120, 50), (Slime, 160, 80)],
            [(Bat, 600, 120), (Bat, 650, 140), (Slime, 200, 200)],
            [(Skeleton, 500, 400), (Slime, 480, 380), (Slime, 520, 380)],
            [(Rat, 260, 300), (Slime, 240, 260), (Bat, 300, 260)],
            [(Dragon, 700, 450)],
        ]
        self.current = 0

    def has_next(self):
        # Dotaz na stav objektu (bez vedlejších efektů).
        return self.current < len(self.levels)

    def load_current(self):
        # Factory-like metoda: z konfigurace vytvoří konkrétní objekty nepřátel.
        enemies = []
        if not self.has_next():
            return enemies
        spec = self.levels[self.current]
        for cls, x, y in spec:
            enemies.append(cls(x, y))
        return enemies

    def advance(self):
        # Změna stavu objektu (mutace): posune aktuální index.
        self.current += 1

    def get_level_number(self):
        # Číslo levelu pro UI (1-based).
        return self.current + 1
