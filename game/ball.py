import pygame
import random

class Ball:
    def __init__(self, x, y, width, height, screen_width, screen_height):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])

        # store previous position for swept collision detection
        self.prev_x = x
        self.prev_y = y

    def move(self):
        # Save previous position
        self.prev_x = self.x
        self.prev_y = self.y

        # Update to new position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Wall bounce (top / bottom)
        if self.y <= 0:
            self.y = 0
            self.velocity_y *= -1
        elif self.y + self.height >= self.screen_height:
            self.y = self.screen_height - self.height
            self.velocity_y *= -1

    def _swept_rect(self):
        """Return a rect that covers both previous and current ball positions (swept AABB)."""
        left = min(self.prev_x, self.x)
        top = min(self.prev_y, self.y)
        right = max(self.prev_x + self.width, self.x + self.width)
        bottom = max(self.prev_y + self.height, self.y + self.height)
        return pygame.Rect(left, top, right - left, bottom - top)

    def check_collision(self, player, ai):
        """
        Use swept-rect collision detection to avoid tunneling.
        If swept rect intersects a paddle, reverse X velocity and place the ball
        just outside the paddle so it doesn't get stuck inside it.
        """
        swept = self._swept_rect()

        # helper to handle a single paddle
        def handle_paddle_collision(paddle):
            p_rect = paddle.rect()
            if swept.colliderect(p_rect):
                # Determine side of collision and push the ball outside the paddle
                # If ball was moving right and hits paddle (paddle is on right), place to left
                if self.velocity_x > 0:
                    # collided going right -> assume hit AI paddle on right
                    self.x = p_rect.left - self.width
                else:
                    # collided going left -> assume hit player paddle on left
                    self.x = p_rect.right
                # Reverse horizontal velocity
                self.velocity_x *= -1

                # Optionally tweak Y velocity based on where the ball hit the paddle:
                # offset = (ball_center_y - paddle_center_y) / (paddle.height/2)
                # self.velocity_y += offset * 2  # uncomment/tweak to add spin effect

                return True
            return False

        # Check both paddles
        # Prioritize whichever paddle is on the side the ball is moving toward
        if self.velocity_x > 0:
            # moving right: check AI first
            if handle_paddle_collision(ai):
                return
            handle_paddle_collision(player)
        else:
            # moving left: check player first
            if handle_paddle_collision(player):
                return
            handle_paddle_collision(ai)

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        # bounce to opposite player to keep game flowing
        self.velocity_x *= -1
        self.velocity_y = random.choice([-3, 3])
        # reset previous to avoid stale swept rect
        self.prev_x = self.x
        self.prev_y = self.y

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
