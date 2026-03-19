# Was It All A Dream?

A narrative-driven 2D platformer built with Pygame where you traverse four dream realms to wake up on Christmas morning. Each realm introduces unique mechanics, NPCs with story dialogue, and escalating challenges — from shrinking ice platforms to meteor-filled blizzards.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

---

## Gameplay

You play as a dreamer navigating four increasingly dangerous dream realms, guided by unique NPCs in each world. Defeat enemies, solve platforming challenges, collect ornaments, and uncover the story behind the dream.

**Difficulty Presets:** Easy, Medium, and Hard — adjustable per level.

---

## Levels

### Level 1 — The First Realm (Ice Domain)
Frozen platforms, shrinking ice, phantom tiles, countdown jumps, zigzag climbing, a red balloon flight, and a Santa sleigh finale.
- **Guide NPC:** Snow Miser

### Level 2 — The Second Realm (Sky Trial)
Island-hopping across the sky with mushroom enemies, ice arrow combat, and a full Santa boss fight (12 hits to defeat).
- **Guide NPCs:** Seraphiel & Lumen

### Level 3 — The Third Realm (Horizon Gate)
Wall sliding, wall jumping, wind zones, saw blades, falling icicles, collapsing platforms, teleporters, and snowball combat. No double jump — precision is everything.
- **Guide NPCs:** Zephyr, Nimbus & Solara

### Level 4 — The Fourth Realm (Frozen Christmas)
The final gauntlet: bomb fiends, glitch platforms, crumbling bridges, an Unreal Mode powerup, and a meteor run through a blizzard. Collect all ornaments to unlock the exit portal.
- **Guide NPCs:** Elder Frost, Holly, Jingle & Starlight

---

## Controls

| Action | Key |
|---|---|
| Move | `WASD` / Arrow Keys |
| Jump | `Space` / `W` / `Up` |
| Sprint / Dash | `Shift` |
| Shoot | `Left Click` / `F` / `X` |
| Talk to NPC | `E` |
| Respawn | `R` |
| Settings | `Esc` |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Pygame

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/was-it-all-a-dream.git
cd was-it-all-a-dream

# Install dependencies
pip install pygame

# Run the game
python main.py
```

---

## Project Structure

```
├── main.py               # Main menu, level select, settings, game launcher
├── settings.py           # Display constants (1280x720, 60 FPS)
├── player_sprites.py     # Owlet Monster sprite rendering & animation
├── sprite_animator.py    # Generic sprite sheet animation utility
├── wood_ui.py            # Wooden-themed UI components & in-game guide
├── levels/
│   ├── level1.py         # The First Realm — Ice Domain
│   ├── level2.py         # The Second Realm — Sky Trial
│   ├── level3.py         # The Third Realm — Horizon Gate
│   └── level4.py         # The Fourth Realm — Frozen Christmas
├── assets/
│   ├── audio/            # Background music (.mp3) & sound effects (.wav)
│   ├── fonts/            # Title, button, and pixel fonts
│   ├── backgrounds/      # Menu background image
│   └── sprites/
│       └── character/    # Owlet Monster sprite sheets (idle, walk, jump, death, climb)
└── entities/             # Reserved for future entity modules
```

---

## Features

- **4 full levels** with distinct themes, enemies, and platforming mechanics
- **Rich NPC dialogue** driving a cohesive narrative across all realms
- **8+ platform types** — ice, phantom, countdown, glitch, teleporting, collapsing, moving, and more
- **Combat system** — stomp enemies, shoot ice arrows and snowballs, fight bosses
- **Checkpoint system** with NPC-triggered story progression
- **Procedurally generated** main menu background with parallax mountains and weather
- **Consistent wooden UI** theme across all menus and dialogue panels
- **Full audio** — 8 music tracks and 24+ sound effects
- **Settings menu** — volume control, mute, fullscreen toggle, in-game guide
- **Animated player character** with smooth state transitions (idle, walk, jump, climb, death)

---

## Technical Details

| Property | Value |
|---|---|
| Resolution | 1280 x 720 |
| Target FPS | 60 |
| Gravity | 0.5–0.6 (per level) |
| Player Sprite | 32x32 base, scaled to ~57x51 |
| Camera | Smooth follow with shake effects |

---

## Built With

- [Pygame](https://www.pygame.org/) — Game engine and rendering
- [Python](https://www.python.org/) — Core language
- Standard library only (`math`, `random`, `os`, `sys`) — no additional dependencies

---

## Credits

Developed with passion for retro-style platformers. Character sprites use the Owlet Monster sprite set.
