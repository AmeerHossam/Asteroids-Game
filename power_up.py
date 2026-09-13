import math
import random
import pygame
from circleShape import CircleShape
from constants import POWERUP_RADIUS


class PowerUp(CircleShape):
    containers: tuple[pygame.sprite.Group, ...] = ()

    TYPE_SHIELD = "shield"
    TYPE_SPEED = "speed"
    TYPE_TRIPLE = "triple"
    TYPE_BOMB = "bomb"

    COLOR_MAP = {
        TYPE_SHIELD: "#00f5d4",   # Cyan
        TYPE_SPEED: "#fee440",    # Gold
        TYPE_TRIPLE: "#f72585",   # Magenta
        TYPE_BOMB: "#ff477e",     # Coral Pink
    }

    def __init__(self, x: float, y: float, powerup_type: str | None = None) -> None:
        super().__init__(x, y, POWERUP_RADIUS)
        if powerup_type is None:
            self.kind = random.choice([
                self.TYPE_SHIELD,
                self.TYPE_SPEED,
                self.TYPE_TRIPLE,
                self.TYPE_BOMB,
            ])
        else:
            self.kind = powerup_type

        self.color = self.COLOR_MAP.get(self.kind, "#ffffff")
        self.lifetime = 14.0  # Despawns after 14s if uncollected
        self.hover_timer = random.uniform(0, 6.28)
        
        # Slow floating drift
        drift_angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2(0, 1).rotate(drift_angle) * random.uniform(15, 35)

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        self.hover_timer += dt * 4.0
        self.position += self.velocity * dt
        self.wrap_around_screen()

    def draw(self, screen: pygame.Surface) -> None:
        # Pulsing outer ring
        pulse = (math.sin(self.hover_timer) + 1) * 0.5
        display_radius = self.radius + (pulse * 2.0)

        # Draw outer glowing ring
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position.x), int(self.position.y)),
            int(display_radius),
            2,
        )

        # Draw inner indicator symbol
        center = (int(self.position.x), int(self.position.y))
        if self.kind == self.TYPE_SHIELD:
            pygame.draw.circle(screen, self.color, center, int(self.radius * 0.5))
        elif self.kind == self.TYPE_SPEED:
            # Draw speed bolt line
            p1 = (center[0] - 3, center[1] - 5)
            p2 = (center[0] + 3, center[1] + 5)
            pygame.draw.line(screen, self.color, p1, p2, 3)
        elif self.kind == self.TYPE_TRIPLE:
            # Draw three bullet dots
            for offset in (-4, 0, 4):
                pygame.draw.circle(screen, self.color, (center[0] + offset, center[1]), 2)
        elif self.kind == self.TYPE_BOMB:
            pygame.draw.circle(screen, self.color, center, 4)
            pygame.draw.line(screen, "white", center, (center[0] + 4, center[1] - 5), 2)