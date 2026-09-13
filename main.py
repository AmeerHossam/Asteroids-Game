import random
import sys
import pygame
from constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    ASTEROID_MIN_RADIUS,
)
from logger import log_event, log_state
from player import Player
from asteroids import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from particle import Particle
from power_up import PowerUp
from bomb_weapon import Bomb


class Starfield:
    def __init__(self, count: int = 120) -> None:
        self.stars: list[dict] = []
        for _ in range(count):
            self.stars.append({
                "x": random.uniform(0, SCREEN_WIDTH),
                "y": random.uniform(0, SCREEN_HEIGHT),
                "speed": random.uniform(2, 12),
                "size": random.choice([1, 1, 1, 2]),
                "color": random.choice(["#3a405a", "#68507b", "#8892b0", "#ffffff"]),
            })

    def update(self, dt: float) -> None:
        for star in self.stars:
            star["y"] += star["speed"] * dt
            if star["y"] > SCREEN_HEIGHT:
                star["y"] = 0
                star["x"] = random.uniform(0, SCREEN_WIDTH)

    def draw(self, screen: pygame.Surface) -> None:
        for star in self.stars:
            pygame.draw.circle(
                screen,
                star["color"],
                (int(star["x"]), int(star["y"])),
                star["size"],
            )


def draw_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    score: int,
    high_score: int,
    player: Player,
) -> None:
    # Score & High Score
    score_surf = font.render(f"SCORE: {score}", True, "white")
    high_surf = font.render(f"HIGH: {high_score}", True, "#8892b0")
    screen.blit(score_surf, (20, 16))
    screen.blit(high_surf, (20, 44))

    # Lives mini-ship icons
    lives_label = font.render("LIVES:", True, "white")
    screen.blit(lives_label, (SCREEN_WIDTH - 220, 16))
    for i in range(max(0, player.lives)):
        lx = SCREEN_WIDTH - 140 + (i * 26)
        ly = 26
        pts = [(lx, ly - 8), (lx - 6, ly + 8), (lx + 6, ly + 8)]
        pygame.draw.polygon(screen, "#00f5d4", pts, 2)

    # Bombs available
    bombs_text = font.render(f"BOMBS: {player.bombs_count} [B]", True, "#ff477e")
    screen.blit(bombs_text, (SCREEN_WIDTH - 220, 46))

    # Active Weapon & Buffs
    buff_str = []
    if player.has_shield:
        buff_str.append("SHIELD")
    if player.speed_boost_timer > 0:
        buff_str.append("SPEED BOOST")
    if player.triple_shot_timer > 0 or player.weapon_mode == "triple":
        buff_str.append("TRIPLE SHOT")
    if player.weapon_mode == "rapid":
        buff_str.append("RAPID FIRE")

    if buff_str:
        buff_surf = font.render("ACTIVE: " + " | ".join(buff_str), True, "#fee440")
        screen.blit(buff_surf, (20, SCREEN_HEIGHT - 36))


def draw_game_over(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    score: int,
) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    game_over_surf = title_font.render("GAME OVER", True, "#e63946")
    screen.blit(
        game_over_surf,
        (SCREEN_WIDTH / 2 - game_over_surf.get_width() / 2, SCREEN_HEIGHT / 2 - 80),
    )

    score_surf = font.render(f"Final Score: {score}", True, "white")
    screen.blit(
        score_surf,
        (SCREEN_WIDTH / 2 - score_surf.get_width() / 2, SCREEN_HEIGHT / 2 - 10),
    )

    restart_surf = font.render("Press 'R' to Restart or 'ESC' to Quit", True, "#00f5d4")
    screen.blit(
        restart_surf,
        (SCREEN_WIDTH / 2 - restart_surf.get_width() / 2, SCREEN_HEIGHT / 2 + 30),
    )


def main() -> None:
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids Deluxe")
    clock = pygame.time.Clock()
    hud_font = pygame.font.SysFont("Courier", 20, bold=True)
    title_font = pygame.font.SysFont("Courier", 52, bold=True)

    starfield = Starfield(140)
    high_score = 0

    while True:
        # Sprite groups setup for new game session
        updatable = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        shots = pygame.sprite.Group()
        particles = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        bombs = pygame.sprite.Group()

        Player.containers = (updatable, drawable)
        Asteroid.containers = (asteroids, updatable, drawable)
        AsteroidField.containers = (updatable,)
        Shot.containers = (shots, updatable, drawable)
        Particle.containers = (particles, updatable, drawable)
        PowerUp.containers = (powerups, updatable, drawable)
        Bomb.containers = (bombs, updatable, drawable)

        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        asteroid_field = AsteroidField()
        score = 0
        game_over = False
        dt = 0.0

        session_running = True
        while session_running:
            log_state()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if game_over and event.key == pygame.K_r:
                        session_running = False  # Restart game
                    # Weapon toggling (1: Normal, 2: Triple, 3: Rapid)
                    if not game_over:
                        if event.key == pygame.K_1:
                            player.weapon_mode = "normal"
                        elif event.key == pygame.K_2:
                            player.weapon_mode = "triple"
                        elif event.key == pygame.K_3:
                            player.weapon_mode = "rapid"

            starfield.update(dt)

            if not game_over:
                updatable.update(dt)

                for asteroid in list(asteroids):
                    for shot in list(shots):
                        if asteroid.collides_with(shot):
                            log_event("asteroid_shot")
                            shot.kill()
                            earned = asteroid.split()
                            if earned is not None:
                                score += earned
                            if score > high_score:
                                high_score = score

                for bomb in list(bombs):
                    if bomb.is_detonating:
                        for asteroid in list(asteroids):
                            if asteroid.position.distance_to(bomb.position) <= bomb.current_blast_radius:
                                earned = asteroid.split()
                                if earned is not None:
                                    score += earned
                                if score > high_score:
                                    high_score = score

                for pup in list(powerups):
                    if pup.collides_with(player):
                        if pup.kind == PowerUp.TYPE_SHIELD:
                            player.has_shield = True
                        elif pup.kind == PowerUp.TYPE_SPEED:
                            player.speed_boost_timer = 10.0
                        elif pup.kind == PowerUp.TYPE_TRIPLE:
                            player.triple_shot_timer = 10.0
                        elif pup.kind == PowerUp.TYPE_BOMB:
                            player.bombs_count += 1
                        pup.kill()

                for asteroid in list(asteroids):
                    if player.collides_with(asteroid):
                        log_event("player_hit")
                        ship_destroyed = player.hit()
                        if ship_destroyed:
                            if player.lives <= 0:
                                game_over = True
                            else:
                                asteroid.split()
                        break
            else:
                # Update only particles while in game over screen
                particles.update(dt)

            screen.fill("#08090d")
            starfield.draw(screen)

            for obj in drawable:
                obj.draw(screen)

            draw_hud(screen, hud_font, score, high_score, player)

            if game_over:
                draw_game_over(screen, title_font, hud_font, score)

            pygame.display.flip()
            dt = clock.tick(60) / 1000.0


if __name__ == "__main__":
    main()