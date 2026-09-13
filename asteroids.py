import math
import random
import pygame
from circleShape import CircleShape
from constants import (
    LINE_WIDTH,
    ASTEROID_MIN_RADIUS,
    SCORE_LARGE,
    SCORE_MEDIUM,
    SCORE_SMALL,
    POWERUP_DROP_CHANCE,
)
from particle import create_explosion
from power_up import PowerUp


class Asteroid(CircleShape):
    containers: tuple[pygame.sprite.Group, ...] = ()

    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)

        # Procedurally build an irregular lumpy rock silhouette
        self.vertex_offsets: list[float] = []
        point_count = random.randint(10, 14)
        for _ in range(point_count):
            # Vary each vertex radius by +-25%
            self.vertex_offsets.append(random.uniform(0.75, 1.25))

    def get_polygon_points(self) -> list[pygame.Vector2]:
        points: list[pygame.Vector2] = []
        count = len(self.vertex_offsets)
        step = (2 * math.pi) / count
        for i, scale in enumerate(self.vertex_offsets):
            angle = i * step
            px = self.position.x + math.cos(angle) * (self.radius * scale)
            py = self.position.y + math.sin(angle) * (self.radius * scale)
            points.append(pygame.Vector2(px, py))
        return points

    def draw(self, screen: pygame.Surface) -> None:
        points = self.get_polygon_points()
        if len(points) >= 3:
            point_tuples = [(p.x, p.y) for p in points]
            pygame.draw.polygon(screen, "white", point_tuples, LINE_WIDTH)
        else:
            pygame.draw.circle(
                screen,
                "white",
                (int(self.position.x), int(self.position.y)),
                int(self.radius),
                LINE_WIDTH,
            )

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.wrap_around_screen()

    @property
    def score_value(self) -> int:
        if self.radius > ASTEROID_MIN_RADIUS * 2:
            return SCORE_LARGE
        if self.radius > ASTEROID_MIN_RADIUS:
            return SCORE_MEDIUM
        return SCORE_SMALL

    def split(self) -> int:
        earned_score = self.score_value
        self.kill()

        # Burst explosion particles
        create_explosion(
            self.position.x,
            self.position.y,
            count=18,
            speed_scale=140.0,
        )

        # Random powerup drop opportunity
        if random.random() < POWERUP_DROP_CHANCE:
            PowerUp(self.position.x, self.position.y)

        # Stop splitting once smallest scale is reached
        if self.radius <= ASTEROID_MIN_RADIUS:
            return earned_score

        # Spawn two smaller splitting asteroids
        random_angle = random.uniform(20, 50)
        vector_1 = self.velocity.rotate(random_angle)
        vector_2 = self.velocity.rotate(-random_angle)

        new_radius = self.radius - ASTEROID_MIN_RADIUS
        asteroid_1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid_2 = Asteroid(self.position.x, self.position.y, new_radius)

        asteroid_1.velocity = vector_1 * 1.2
        asteroid_2.velocity = vector_2 * 1.2

        return earned_score