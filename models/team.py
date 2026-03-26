from models.player import Player

class Team:
    def __init__(self, name, color, players_info):
        """
        players_info = list of tuples: [(name, number), ...]
        """
        self.name = name
        self.color = color
        self.players = [Player(name, number, color) for name, number in players_info]

    def draw(self, screen):
        for player in self.players:
            player.draw(screen)

    def move_player(self, player_index, dx, dy):
        self.players[player_index].move(dx, dy)