# Asteroids Deluxe 🚀☄️

**Asteroids Deluxe** is an enhanced, modern, object-oriented arcade space shooter built from scratch in Python utilizing the [Pygame](https://www.pygame.org/) library. Expanding upon the classic 1979 arcade formula, this project introduces rich state management, procedural rendering, modular weapon systems, dynamic power-ups, particle physics, and structured logging capabilities.

---

## 🌟 Features

*   **Procedural Asteroid Meshes:** Asteroids feature dynamically generated irregular polygon vertices for organic, non-uniform visual silhouettes.
*   **Advanced Player Flight Physics:** Features inertial momentum, acceleration thrust, space friction dampening, screen-wrap boundaries, and dynamic respawn invulnerability with visual flickering.
*   **Expanded Weapon Modes & Power-Ups:** 
    *   **Standard Blaster:** Single-shot high-velocity projectiles.
    *   **Triple Shot:** Spread shot pattern for broad field coverage.
    *   **Rapid Fire:** High-cadence stream of light pulses.
    *   **Smart Bombs:** Timed proximity charges that detonate into expanding shockwave fronts, decimating nearby hazards.
    *   **Shield Buffs:** Absorbs fatal collisions with a glowing energy bubble.
    *   **Speed Boosts:** Amplifies engine thrust and maximum flight speed.
*   **Particle Explosion Engine:** Radial particle bursts with custom color palettes, size scaling, velocity vectors, and natural deceleration fading upon asteroid splits or ship impacts.
*   **Immersive Starfield:** Layered, multi-speed drifting background stars for dynamic depth perception.
*   **Diagnostic Event & State Logger:** Automated snapshot logger that records real-time game telemetry, sprite group positions, velocities, and discrete event triggers to disk.

---

## 🏗️ Project Architecture

The project follows a rigorous, clean Object-Oriented Programming (OOP) design pattern, taking advantage of Pygame’s Sprite and Group containers for clean decoupling of update logic and rendering passes.

```
├── main.py             # Game loop, state machines, Starfield, HUD, and core controllers
├── player.py           # Player ship physics, polygon collision, and weapon triggers
├── asteroids.py        # Asteroid polygon generation, physics, and split logic
├── asteroidfield.py    # Infinite edge-spawning director and timer
├── bomb_weapon.py      # Proximity bomb timer, fuse states, and expanding shockwave logic
├── power_up.py         # Collectible buffs, float drift, and symbol mapping
├── particle.py         # Particle physics, alpha scaling, and explosion emitters
├── circleShape.py      # Base abstract class providing circular bounding collisions and screen wrap
├── constants.py        # Global game configuration parameters and tuning variables
└── logger.py           # JSONL state snapshot and gameplay event logging engine
```

---

## 🎮 Controls & Shortcuts

| Action | Control Key(s) | Description |
| :--- | :--- | :--- |
| **Steer Left / Right** | `A` / `D` or `LEFT` / `RIGHT` | Rotate ship heading |
| **Accelerate** | `W` or `UP` | Apply engine forward thrust |
| **Brake / Reverse** | `S` or `DOWN` | Apply reverse deceleration thruster |
| **Fire Weapon** | `SPACE` | Fire active weapon mode |
| **Deploy Bomb** | `B` or `E` | Drop a timed proximity shockwave bomb |
| **Switch Weapon (Normal)** | `1` | Switch to single-shot blaster |
| **Switch Weapon (Triple)** | `2` | Switch to triple spread shot |
| **Switch Weapon (Rapid)** | `3` | Switch to high-cadence rapid fire |
| **Restart Game** | `R` | Restart session upon Game Over |
| **Quit Game** | `ESC` or Window Close | Exit application |

---

## ⚙️ Installation & Setup

### Prerequisites
*   Python **3.10+**
*   pip package manager

### 1. Clone or Download Repository
Navigate to your target directory containing the project source files.

### 2. Install Dependencies
Install the required Pygame library:
```bash
pip install pygame
```

### 3. Run the Game
Execute the main entry point script:
```bash
python main.py
```

---

## 📊 Logging System

**Asteroids Deluxe** includes a diagnostic logging utility (`logger.py`) designed for telemetry monitoring and gameplay analysis:
*   **`game_state.jsonl`:** Captures periodic frame-by-frame snapshots (approx. once per second for up to 16 seconds) of active sprite groups, positions, velocities, radii, and screen dimensions.
*   **`game_events.jsonl`:** Records discrete gameplay milestones and event triggers (such as `asteroid_shot` and `player_hit`) with high-precision timestamps.

---

## 🛠️ Code Structure & Core Classes

*   **`CircleShape` (`circleShape.py`):** The foundational base class extending `pygame.sprite.Sprite`. Manages position vectors, velocity vectors, radius definitions, distance-based collision checks (`collides_with`), and toroidal screen wrapping (`wrap_around_screen`).
*   **`Player` (`player.py`):** Implements triangular vertex mapping, momentum physics, rotational handling, multi-mode firing routines, and invulnerability states.
*   **`Asteroid` (`asteroids.py`):** Handles irregular procedural polygon mapping using randomized vertex radii offsets, scoring metrics based on size scale, and recursive splitting mechanics.
*   **`AsteroidField` (`asteroidfield.py`):** Automatically samples screen boundaries to spawn incoming hazards at regular cadence intervals.