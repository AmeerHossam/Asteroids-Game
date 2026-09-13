import pygame
from circleShape import CircleShape
from constants import SHOT_RADIUS, LINE_WIDTH


class Shot(CircleShape):
    containers: tuple[pygame.sprite.Group, ...] = ()

    def __init__(
        self,
        x: float,
        y: float,
        color: str = "white",
        lifetime: float = 1.6,
        radius: float = SHOT_RADIUS,
    ) -> None:
        super().__init__(x, y, radius)
        self.color = color
        self.lifetime = lifetime

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position.x), int(self.position.y)),
            int(self.radius),
            0,  # Solid filled circle for high visibility
        )

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        self.position += self.velocity * dt
        self.wrap_around_screen()