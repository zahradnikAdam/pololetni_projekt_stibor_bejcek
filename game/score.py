"""Skóre systému oddělené do samostatné OOP třídy."""


class ScoreTracker:
    """Počítá skóre za zásahy do enemy.

    Pozn.: body se přidávají jen za běžné zásahy (melee/ranged),
    super útok se do skóre nepřičítá.
    """

    def __init__(self, points_per_hit=10):
        self.points_per_hit = int(points_per_hit)
        self.score = 0
        self.hits = 0

    def register_hit(self):
        """Zapíše jeden validní hit a vrátí nové skóre."""
        self.hits += 1
        self.score += self.points_per_hit
        return self.score

    def get_score(self):
        return int(self.score)

    def get_hits(self):
        return int(self.hits)
