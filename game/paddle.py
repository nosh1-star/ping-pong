import pygame

class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 7

    def move(self, dy, screen_height):
        self.y += dy
        self.y = max(0, min(self.y, screen_height - self.height))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def auto_track(self, ball, screen_height, difficulty="medium"):
        """
    Make the AI track the ball with adjustable difficulty.
    difficulty can be 'easy', 'medium', or 'hard'.
    """
    # Difficulty settings: lower values = slower reaction
        difficulty_settings = {
        "easy": {"speed_factor": 0.6, "reaction_chance": 0.7},
        "medium": {"speed_factor": 0.8, "reaction_chance": 0.9},
        "hard": {"speed_factor": 1.0, "reaction_chance": 1.0}
    }

        settings = difficulty_settings.get(difficulty, difficulty_settings["medium"])

    # Add randomness to simulate missed reactions
        import random
        if random.random() > settings["reaction_chance"]:
            return  # Skip moving this frame (AI "hesitates")

    # Adjust effective speed based on difficulty
        move_speed = self.speed * settings["speed_factor"]

    # Track ball with a small offset to make it imperfect
        offset = random.randint(-20, 20)

    # Target center of ball, but with offset
        target_y = ball.y + offset

    # Move toward target
        if target_y < self.y:
         self.move(-move_speed, screen_height)
        elif target_y > self.y + self.height:
            self.move(move_speed, screen_height)
