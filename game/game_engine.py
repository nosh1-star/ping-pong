import pygame
from .paddle import Paddle
from .ball import Ball

# Game Engine

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameEngine:
    def __init__(self, width, height):
        pygame.mixer.init()
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.large_font = pygame.font.SysFont("Arial", 60)

        self.winning_score = 5
        self.game_over = False
        self.winner_text = ""
        self.waiting_for_replay = False  # replay screen state
        # Load sound effects
        try:
            self.sound_paddle = pygame.mixer.Sound("sounds/paddle_hit.wav")
            self.sound_wall = pygame.mixer.Sound("sounds/wall_bounce.wav")
            self.sound_score = pygame.mixer.Sound("sounds/score.wav")
        except pygame.error:
            print("Warning: Sound files not found. Continuing without audio.")
            self.sound_paddle = None
            self.sound_wall = None
            self.sound_score = None

        # Smooth paddle velocity
        self.player_velocity = 0

    def handle_input(self):
        if self.game_over or self.waiting_for_replay:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self):
        if self.game_over or self.waiting_for_replay:
            return
        if self.player_velocity != 0:
            self.player.move(self.player_velocity, self.height)

        prev_vx, prev_vy = self.ball.velocity_x, self.ball.velocity_y

        self.ball.move()
        self.ball.check_collision(self.player, self.ai)

        if self.ball.velocity_y != prev_vy and self.sound_wall:
            self.sound_wall.play()
        if self.ball.velocity_x != prev_vx and self.sound_paddle:
            self.sound_paddle.play()

        # scoring
        if self.ball.x <= 0:
            self.ai_score += 1
            self.ball.reset()
            if self.sound_score:
                self.sound_score.play()
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.ball.reset()
            if self.sound_score:
                self.sound_score.play()

        self.ai.auto_track(self.ball, self.height, difficulty="medium")
        self.check_game_over()

    def render(self, screen):
        screen.fill(BLACK)

        # paddles, ball, center line
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        # scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width // 4, 20))
        screen.blit(ai_text, (self.width * 3 // 4, 20))

        if self.game_over:
            self.show_game_over(screen)
        elif self.waiting_for_replay:
            self.show_replay_menu(screen)

    def check_game_over(self):
        if self.player_score >= self.winning_score:
            self.game_over = True
            self.winner_text = "PLAYER WINS!"
        elif self.ai_score >= self.winning_score:
            self.game_over = True
            self.winner_text = "AI WINS!"

    def show_game_over(self, screen):
        text_surface = self.large_font.render(self.winner_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 40))
        screen.blit(text_surface, text_rect)

        # Display replay prompt
        prompt = self.font.render("Press any key to continue...", True, WHITE)
        prompt_rect = prompt.get_rect(center=(self.width // 2, self.height // 2 + 40))
        screen.blit(prompt, prompt_rect)

    def show_replay_menu(self, screen):
        """Show replay options."""
        title = self.large_font.render("Play Again?", True, WHITE)
        options = [
            "3 - Best of 3",
            "5 - Best of 5",
            "7 - Best of 7",
            "ESC - Exit"
        ]
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 100))
        screen.blit(title, title_rect)

        for i, opt in enumerate(options):
            text = self.font.render(opt, True, WHITE)
            rect = text.get_rect(center=(self.width // 2, self.height // 2 + i * 40))
            screen.blit(text, rect)

    def handle_event(self, event):
        """Handle keyboard input for game over / replay."""
        # If in game over state and a key is pressed -> move to replay menu
        if self.game_over and event.type == pygame.KEYDOWN:
            self.game_over = False
            self.waiting_for_replay = True

        # If showing replay menu, detect key choices
        elif self.waiting_for_replay and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_3:
                self.start_new_game(3)
            elif event.key == pygame.K_5:
                self.start_new_game(5)
            elif event.key == pygame.K_7:
                self.start_new_game(7)
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

    def start_new_game(self, best_of):
        """Reset everything and set a new winning score."""
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()
        self.winning_score = best_of
        self.waiting_for_replay = False
        self.game_over = False
        self.winner_text = ""
