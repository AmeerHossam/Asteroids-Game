import pygame
from circleShape import CircleShape
from constants import BOMB_FUSE_SECONDS, BOMB_BLAST_RADIUS
from particle import create_explosion


class Bomb(CircleShape):
    containers: tuple[pygame.sprite.Group, ...] = ()

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 8)
        self.fuse_timer = BOMB_FUSE_SECONDS
        self.is_detonating = False
        self.blast_progress = 0.0
        self.max_blast_radius = BOMB_BLAST_RADIUS
        self.current_blast_radius = 0.0
        self.has_dealt_damage = False

    def update(self, dt: float) -> None:
        if not self.is_detonating:
            self.fuse_timer -= dt
            if self.fuse_timer <= 0:
                self.is_detonating = True
                create_explosion(
                    self.position.x,
                    self.position.y,
                    count=40,
                    speed_scale=260.0,
                )
        else:
            self.blast_progress += dt * 3.2
            self.current_blast_radius = self.max_blast_radius * min(1.0, self.blast_progress)
            if self.blast_progress >= 1.0:
                self.kill()

    def draw(self, screen: pygame.Surface) -> None:
        if not self.is_detonating:
            # Flashing warning beacon
            color = "red" if int(self.fuse_timer * 8) % 2 == 0 else "white"
            pygame.draw.circle(
                screen,
                color,
                (int(self.position.x), int(self.position.y)),
                int(self.radius),
            )
            pygame.draw.circle(
                screen,
                "orange",
                (int(self.position.x), int(self.position.y)),
                int(self.radius + 3),
                1,
            )
        else:
            # Expanding shockwave wave-front
            pygame.draw.circle(
                screen,
                "#ff0054",
                (int(self.position.x), int(self.position.y)),
                int(self.current_blast_radius),
                4,
            )
            pygame.draw.circle(
                screen,
                "#ffb703",
                (int(self.position.x), int(self.position.y)),
                max(1, int(self.current_blast_radius * 0.7)),
                2,
            )