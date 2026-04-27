"""Spouštěcí bod hry.

Drží jen minimum logiky: vytvoří `Game` a spustí hlavní smyčku.
"""

from game.game import Game


if __name__ == "__main__":
    Game().run()
