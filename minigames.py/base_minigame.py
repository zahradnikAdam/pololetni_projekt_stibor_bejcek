from abc import ABC, abstractmethod

class BaseMiniGame(ABC):
    def __init__(self, match_engine):
        self.match_engine = match_engine
        self.completed = False

    @abstractmethod
    def play(self):
        """Spustí minihru"""
        pass

    @abstractmethod
    def draw(self, screen):
        """Vykreslí minihru"""
        pass