class GameStats:
    """Track statistics for Alien Invasion"""

    def __init__(self, ai_game):
        """"Initialize statistics"""
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False
        with open("scores/highscore.txt") as file:
            self.high_score = int(file.read())

    def reset_stats(self):
        """Initialize stats that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
