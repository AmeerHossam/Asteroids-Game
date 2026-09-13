import math
import random
import pygame
from circleShape import CircleShape
from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_ACCELERATION,
    PLAYER_MAX_SPEED,
    PLAYER_FRICTION,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    RAPID_SHOOT_COOLDOWN,
    PLAYER_START_LIVES,
    PLAYER_RESPAWN_INVULNERABILITY,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from shot import Shot
from bomb_weapon import Bomb
from particle import Particle, create_explosion


class Player(CircleShape):
    containers: tuple[pygame.sprite.Group, ...] = ()

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0.0
        self.shoot_timer = 0.0
        self.bomb_timer = 0.0
        
        # Flight physics
        self.velocity = pygame.Vector2(0, 0)

        # Lives and invulnerability
        self.lives = PLAYER_START_LIVES
        self.invulnerable_timer = PLAYER_RESPAWN_INVULNERABILITY

        # Power-ups and weapons
        self.has_shield = False
        self.speed_boost_timer = 0.0
        self.triple_shot_timer = 0.0
        self.weapon_mode = "normal"  # "normal", "triple", "rapid"
        self.bombs_count = 2

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * (self.radius / 1.5)
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def collides_with(self, other: CircleShape) -> bool:
        """Verifies triangular ship collision against another circular shape."""
        tri_points = self.triangle()
        center = other.position

        # Check if asteroid center is close to any ship vertex
        for p in tri_points:
            if p.distance_to(center) <= other.radius:
                return True

        # Check ship center distance fallback
        if self.position.distance_to(center) <= (self.radius * 0.85 + other.radius):
            return True

        return False

    def draw(self, screen: pygame.Surface) -> None:
        # Invulnerability blinking effect
        if self.invulnerable_timer > 0 and int(self.invulnerable_timer * 12) % 2 == 0:
            return  # Skip rendering for flickering transparency

        # Ship hull
        tri = [(p.x, p.y) for p in self.triangle()]
        hull_color = "#00b4d8" if self.speed_boost_timer > 0 else "white"
        pygame.draw.polygon(screen, hull_color, tri, LINE_WIDTH)

        # Draw glowing shield bubble
        if self.has_shield:
            pygame.draw.circle(
                screen,
                "#00f5d4",
                (int(self.position.x), int(self.position.y)),
                int(self.radius + 8),
                2,
            )

    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_TURN_SPEED * dt

    def accelerate(self, dt: float, direction: float = 1.0) -> None:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        accel_rate = PLAYER_ACCELERATION
        if self.speed_boost_timer > 0:
            accel_rate *= 1.5

        self.velocity += forward * (accel_rate * direction * dt)

        # Clamp maximum speed
        max_speed = PLAYER_MAX_SPEED * (1.4 if self.speed_boost_timer > 0 else 1.0)
        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        # Thruster particle exhaust trail
        if direction > 0:
            rear = self.position - forward * self.radius
            exhaust_dir = (-forward).rotate(random.uniform(-25, 25))
            exhaust_vel = exhaust_dir * random.uniform(80, 150) + self.velocity * 0.4
            Particle(
                rear.x,
                rear.y,
                exhaust_vel,
                color=random.choice(["#ffb703", "#fb8500", "#ffffff"]),
                lifetime=0.25,
                size=3.0,
            )

    def shoot(self) -> None:
        if self.shoot_timer > 0:
            return

        cooldown = RAPID_SHOOT_COOLDOWN if self.weapon_mode == "rapid" else PLAYER_SHOOT_COOLDOWN_SECONDS
        self.shoot_timer = cooldown

        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        nose = self.position + forward * self.radius

        if self.weapon_mode == "triple" or self.triple_shot_timer > 0:
            # Spread shot with 3 angled bullets
            for angle_offset in (-18, 0, 18):
                dir_vec = pygame.Vector2(0, 1).rotate(self.rotation + angle_offset)
                bullet = Shot(nose.x, nose.y, color="#f72585")
                bullet.velocity = dir_vec * PLAYER_SHOOT_SPEED
        elif self.weapon_mode == "rapid":
            # Rapid fire streamlined pulse
            bullet = Shot(nose.x, nose.y, color="#48cae4", radius=3)
            bullet.velocity = forward * (PLAYER_SHOOT_SPEED * 1.25)
        else:
            # Standard single blaster
            bullet = Shot(nose.x, nose.y, color="white")
            bullet.velocity = forward * PLAYER_SHOOT_SPEED

    def drop_bomb(self) -> None:
        if self.bombs_count > 0 and self.bomb_timer <= 0:
            self.bombs_count -= 1
            self.bomb_timer = 0.5
            Bomb(self.position.x, self.position.y)

    def hit(self) -> bool:
        """Returns True if ship lost a life and destroyed, False if shielded or invulnerable."""
        if self.invulnerable_timer > 0:
            return False

        if self.has_shield:
            self.has_shield = False
            self.invulnerable_timer = 1.0
            create_explosion(self.position.x, self.position.y, count=16, color_palette=("#00f5d4", "#ffffff"))
            return False

        # Lose a life and trigger explosion
        self.lives -= 1
        create_explosion(self.position.x, self.position.y, count=32, speed_scale=220.0)
        self.respawn()
        return True

    def respawn(self) -> None:
        self.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0.0
        self.invulnerable_timer = PLAYER_RESPAWN_INVULNERABILITY

    def update(self, dt: float) -> None:
        self.shoot_timer -= dt
        self.bomb_timer -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
        if self.triple_shot_timer > 0:
            self.triple_shot_timer -= dt

        # Dampening / Space friction
        self.velocity *= math.pow(PLAYER_FRICTION, dt * 60)
        self.position += self.velocity * dt
        self.wrap_around_screen()

        # Keyboard input controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.accelerate(dt, 1.0)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.accelerate(dt, -0.6)  # Reverse braking thruster
        if keys[pygame.K_SPACE]:
            self.shoot()
        if keys[pygame.K_b] or keys[pygame.K_e]:
            self.drop_bomb()