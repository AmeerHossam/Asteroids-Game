import random
import pygame


class Particle(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group, ...] = ()

    def __init__(
        self,
        x: float,
        y: float,
        velocity: pygame.Vector2,
        color: pygame.Color | str,
        lifetime: float = 0.6,
        size: float = 3.0,
    ) -> None:
        if hasattr(self, "containers") and self.containers:
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = velocity
        self.color = pygame.Color(color)
        self.max_lifetime = lifetime
        self.current_life = lifetime
        self.initial_size = size

    def update(self, dt: float) -> None:
        self.current_life -= dt
        if self.current_life <= 0:
            self.kill()
            return

        self.position += self.velocity * dt
        self.velocity *= 0.96  # particle deceleration

    def draw(self, screen: pygame.Surface) -> None:
        alpha_ratio = max(0.0, self.current_life / self.max_lifetime)
        current_radius = max(1.0, self.initial_size * alpha_ratio)
        
        # Render glowing particle circle
        fade_color = pygame.Color(
            self.color.r,
            self.color.g,
            self.color.b,
        )
        pygame.draw.circle(
            screen,
            fade_color,
            (int(self.position.x), int(self.position.y)),
            int(current_radius),
        )


def create_explosion(
    x: float,
    y: float,
    count: int = 24,
    color_palette: tuple[str, ...] = ("#ffb703", "#fb8500", "#ffffff", "#d62828"),
    speed_scale: float = 180.0,
) -> None:
    """Spawns a radial burst of particles at given coordinates."""
    for _ in range(count):
        angle = random.uniform(0, 360)
        speed = random.uniform(30.0, speed_scale)
        velocity = pygame.Vector2(0, 1).rotate(angle) * speed
        color = random.choice(color_palette)
        life = random.uniform(0.3, 0.8)
        size = random.uniform(2.0, 4.5)
        Particle(x, y, velocity, color, life, size)