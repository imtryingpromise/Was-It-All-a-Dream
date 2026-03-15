import pygame
import sys
import math
import random
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from player_sprites import init_player_sprite, draw_player_sprite
    _SPRITES_AVAILABLE = True
except ImportError:
    _SPRITES_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# ── Palette ──────────────────────────────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_TOP = (100, 160, 230)
SKY_BOT = (180, 220, 255)
CLOUD_WHITE = (245, 248, 255)
SUN_YELLOW = (255, 230, 80)
SUN_GOLD = (255, 190, 30)
GRASS_GREEN = (80, 180, 80)
GRASS_DARK = (55, 130, 55)
DIRT_BROWN = (160, 110, 60)
HOLY_GOLD = (255, 215, 50)
HOLY_WHITE = (240, 250, 255)
ANGEL_BLUE = (160, 200, 255)
ANGEL_GOLD = (255, 220, 100)
HERO_BROWN = (180, 120, 60)
HERO_GREEN = (60, 130, 60)
ARROW_BROWN = (140, 90, 30)
SANTA_RED = (200, 40, 40)
SANTA_WHITE = (240, 240, 240)
BALLOON_BLUE = (60, 130, 220)
BALLOON_DARK = (40, 90, 180)
GIFT_RED = (210, 50, 50)
GIFT_GREEN = (50, 170, 70)
GIFT_GOLD = (255, 200, 50)
MUSHROOM_RED = (200, 50, 50)
MUSHROOM_CAP = (210, 60, 60)
FIRE_ORANGE = (255, 140, 30)
FIRE_RED = (255, 60, 20)
FIRE_YELLOW = (255, 220, 50)
SPIRIT_WHITE = (220, 240, 255)
SPIRIT_GOLD = (255, 230, 120)
GRAY = (140, 140, 140)
DARK_GRAY = (80, 80, 80)
XMAS_GREEN = (30, 160, 50)
XMAS_GOLD = (255, 200, 50)
XMAS_RED = (200, 30, 30)
RED = (220, 50, 50)
ORANGE = (255, 160, 30)
CYAN = (0, 220, 255)
PURPLE = (160, 50, 200)
BROWN = (139, 90, 43)

# ── Ice arrow colours ──────────────────────────────────────────────────────
ICE_BLUE   = (140, 210, 255)
ICE_WHITE  = (220, 245, 255)
ICE_DARK   = ( 80, 160, 220)
ICE_CORE   = (200, 240, 255)

# ── Physics ───────────────────────────────────────────────────────────────────
GRAVITY = 0.55
JUMP_VELOCITY = -13
MOVE_SPEED = 5
SPRINT_SPEED = 8
MAX_FALL_SPEED = 15
DEATH_Y = 900
PLAYER_MAX_HEARTS = 3
INVINCIBILITY_FRAMES = 90
ARROW_SPEED = 14
ARROW_LIFETIME = 80
ARROW_COOLDOWN = 22

# ── Santa boss ────────────────────────────────────────────────────────────────
SANTA_MAX_HP = 12  # hits to kill
SANTA_BALLOON_INTERVAL = 120  # frames between balloon throws
SANTA_BALLOON_SPEED = 5
BALLOON_LIFETIME = 90

# ── Story dialogues ──────────────────────────────────────────────────────────
STORY_DIALOGUES = {
    "intro": [
        ("Seraphiel", "...Can you hear me, Dreamer?"),
        ("Seraphiel", "You fell once again! endless realm took you down."),
        ("Seraphiel", "But the sun is not done with you yet, Fear no more the heat o' the sun."),
        ("Seraphiel", "I am Seraphiel — guardian of this sky realm. The third of the four."),
        ("Seraphiel", "I channeled the light of the sun and called your spirit back."),
        ("Seraphiel", "You were a spark of light drifting through the cold. Now you are here."),
        ("Seraphiel", "This realm is called the Sky Trial. It is beautiful... but it is not safe."),
        ("Seraphiel", "The Nightmare has corrupted the festive creatures here. They will hunt you."),
        ("Seraphiel", "MOVEMENT: Arrow keys or WASD to move. SPACE or UP to jump. SHIFT to sprint."),
        ("Seraphiel", "DOUBLE JUMP: Jump again in mid-air. Use it wisely on the floating islands."),
        ("Seraphiel", "BOW: LEFT-CLICK anywhere on screen to fire an arrow toward that point."),
        ("Seraphiel", "STOMP: Land on top of mushroom enemies to squash them."),
        ("Seraphiel", "If you fall, I will call you back again. The sun always rises."),
        ("Seraphiel", "Climb the floating islands. Find the portal. Wake up."),
        ("Seraphiel", "One more thing — there is something flying above this realm. Something large."),
        ("Seraphiel", "Watch the skies, Dreamer. And press ESC for settings, R to respawn."),
    ],
    "cp1": [
        ("Lumen", "Hey! Over here! Are you the one Seraphiel summoned?"),
        ("Lumen", "I am Lumen. A wandering light spirit. I have been trapped in this realm."),
        ("Lumen", "The islands ahead are trickier. The gaps are wider. Don't rush."),
        ("Lumen", "Also... that thing in the sky? It is getting closer."),
        ("Lumen", "I saw it earlier. Red coat. Flying contraption. Throwing things down."),
        ("Lumen", "Whatever it is, it is not friendly. Keep your bow ready."),
        ("Lumen", "You can do this. Seraphiel chose you for a reason."),
    ],
    "cp2": [
        ("Seraphiel", "Dreamer. You are doing well. The islands are rising — you are climbing."),
        ("Seraphiel", "I need to warn you. Santa has fully entered this realm now."),
        ("Seraphiel", "He carries water balloons filled with corrupted sky-water. Each one stings."),
        ("Seraphiel", "You must shoot him down. Your arrows can pierce his balloon vessel."),
        ("Seraphiel", "It will take many hits. He is reinforced by nightmare energy."),
        ("Seraphiel", "But every arrow counts. Every hit weakens him."),
        ("Seraphiel", "Stay mobile. The balloons fall where you stand — keep moving."),
        ("Seraphiel", "When he falls... a gift will drop. That gift holds power. Collect it."),
        ("Seraphiel", "The portal home is beyond. Finish this."),
    ],
    "cp3": [
        ("Lumen", "Almost there! I can see the portal from here!"),
        ("Lumen", "The sky is fighting back now — those mushrooms are frenzied."),
        ("Lumen", "Santa should be appearing any moment. Don't panic. Breathe. Aim."),
        ("Lumen", "You have been through fire, shadow, and now this. You are almost free."),
        ("Lumen", "One more push. The dream ends beyond that portal."),
    ],
    "ending": [
        ("Seraphiel", "...You did it, Dreamer."),
        ("Seraphiel", "The sky realm is free. The nightmare's grip on it is broken."),
        ("Lumen", "I watched the whole thing! You shot Santa out of the sky!"),
        ("Lumen", "I was hiding behind a cloud the entire time, but STILL. Amazing."),
        ("Seraphiel", "The gift you claimed holds a fragment of the sun's power."),
        ("Seraphiel", "Carry it forward. The cold cannot touch it."),
        ("Seraphiel", "The final realm is the hardest. But you have climbed the sky now."),
        ("Seraphiel", "You have faced fire, shadow, and the sky trial."),
        ("Seraphiel", "You are almost home."),
        ("Lumen", "Hey. When you wake up... look at the sky for me, will you?"),
        ("Lumen", "Even a dreaming sky is beautiful. The real one must be amazing."),
        ("Seraphiel", "Step through the portal, Dreamer. Christmas celebration is waiting."),
        ("", "The portal blazes with warmth. You step through."),
        ("", "The sky dissolves into golden light."),
        ("", "The frozen christmas realm waits. But for a moment — just a moment —"),
        ("", "you feel the sun on your face. Real sunlight. Warm and certain."),
        ("", "One realm left, Good Luck!"),
    ],
}

# ── Sound (graceful fallback) ─────────────────────────────────────────────────
# level3.py lives in levels/, audio lives in ../assets/audio/
_LEVELS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_LEVELS_DIR)
SOUND_DIR    = os.path.join(_BASE, "assets", "audio")
MUSIC_FILE   = os.path.join(_BASE, "assets", "audio", "Level3MusicNew.mp3")
ENDING_MUSIC = os.path.join(_BASE, "assets", "audio", "soundsending.mp3")
PRESENT_MUSIC = os.path.join(_BASE, "assets", "audio", "captured_present.mp3")

SOUND_FILES = {
    "jump":         "jump.wav",
    "death":        "death.wav",
    "respawn":      "hit.wav",           # no respawn.wav, reuse hit
    "stomp":        "stomp.wav",
    "monster_kill": "monster_kill.wav",
    "powerup":      "powerup.wav",
    "checkpoint":   "checkpoint.wav",
    "win":          "powerup.wav",       # no win.wav, reuse powerup
    "shoot":        "shoot.wav",
    "arrow_hit":    "hit.wav",           # use hit.wav for arrow impacts
    "santa_die":    "bomb_explode.wav",
    "balloon_hit":  "death.wav",
    "soul_rise":    "hit.wav",           # no soul_rise.wav, fallback
    "soul_land":    "stomp.wav",         # no soul_land.wav, fallback
}


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_loaded = False
        print(f"[AUDIO] Sound dir: {SOUND_DIR}")
        print(f"[AUDIO] Music file exists: {os.path.isfile(MUSIC_FILE)} -> {MUSIC_FILE}")
        for name, fn in SOUND_FILES.items():
            path = os.path.join(SOUND_DIR, fn)
            exists = os.path.isfile(path)
            print(f"[AUDIO] {name}: {'OK' if exists else 'MISSING'} -> {path}")
            try:
                self.sounds[name] = pygame.mixer.Sound(path) if exists else None
            except Exception as e:
                print(f"[AUDIO] ERROR loading {name}: {e}")
                self.sounds[name] = None
        if os.path.isfile(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                self.music_loaded = True
                print("[AUDIO] Music loaded OK")
            except Exception as e:
                print(f"[AUDIO] Music load ERROR: {e}")

    def play(self, n):
        s = self.sounds.get(n)
        if s:
            s.play()

    def start_music(self, loops=-1, volume=0.5):
        if self.music_loaded:
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()

    def start_ending_music(self):
        if os.path.isfile(ENDING_MUSIC):
            try:
                pygame.mixer.music.load(ENDING_MUSIC)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
            except:
                pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
class Camera:
    def __init__(self, w, h):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.width = w
        self.height = h
        self.shake_amount = 0.0
        self.shake_x = 0
        self.shake_y = 0

    def update(self, r):
        self.offset_x += (r.centerx - self.width // 3 - self.offset_x) * 0.10
        ty = r.centery - self.height // 2
        self.offset_y += (ty - self.offset_y) * 0.06
        self.offset_y = max(-300, min(self.offset_y, 200))
        if self.shake_amount > 0.5:
            self.shake_x = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_y = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_amount *= 0.82
        else:
            self.shake_amount = 0
            self.shake_x = self.shake_y = 0

    def add_shake(self, a):
        self.shake_amount = min(self.shake_amount + a, 22)

    def apply(self, rect):
        return pygame.Rect(
            rect.x - int(self.offset_x) + self.shake_x,
            rect.y - int(self.offset_y) + self.shake_y,
            rect.width, rect.height)


# ---------------------------------------------------------------------------
# Particles / Effects
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, lifetime=30, size=4,
                 gravity=0.1, fade=True):
        self.x, self.y = float(x), float(y)
        self.color = color
        self.vel_x, self.vel_y = vx, vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.base_size = size
        self.gravity_val = gravity
        self.fade = fade

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity_val
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface, camera):
        a = self.lifetime / self.max_lifetime if self.fade else 1.0
        sz = max(1, int(self.base_size * a))
        c = tuple(max(0, min(255, int(v * a))) for v in self.color)
        p = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        pygame.draw.rect(surface, c, (p.x, p.y, sz, sz))


class RingEffect:
    def __init__(self, x, y, color, max_radius=120, speed=4, width=4):
        self.x, self.y = x, y
        self.color = color
        self.radius = 0
        self.max_radius = max_radius
        self.speed = speed
        self.width = width

    def update(self):
        self.radius += self.speed
        return self.radius < self.max_radius

    def draw(self, surface, camera):
        a = 1.0 - (self.radius / self.max_radius)
        c = tuple(max(0, min(255, int(v * a))) for v in self.color)
        w = max(1, int(self.width * a))
        p = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        if 0 <= p.x <= SCREEN_WIDTH and 0 <= p.y <= SCREEN_HEIGHT:
            pygame.draw.circle(surface, c, (p.x, p.y), int(self.radius), w)


class FlashOverlay:
    def __init__(self, color, duration=15, max_alpha=180):
        self.color = color
        self.duration = duration
        self.timer = duration
        self.max_alpha = max_alpha
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.fill(color[:3])

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def draw(self, surface):
        self.surface.set_alpha(int(self.max_alpha * (self.timer / self.duration)))
        surface.blit(self.surface, (0, 0))


class DamageFlash:
    """Red vignette on damage."""

    def __init__(self):
        self.timer = 20
        self.max_timer = 20

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def draw(self, surface):
        a = int(160 * (self.timer / self.max_timer))
        if a <= 0:
            return
        w, h = surface.get_size()
        t = 60
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(t):
            ia = int(a * (1 - i / t))
            if ia > 0:
                pygame.draw.rect(s, (220, 30, 30, ia),
                                 (i, i, w - 2 * i, h - 2 * i), 1)
        surface.blit(s, (0, 0))


# ---------------------------------------------------------------------------
# Cloud (pixel-art style with shadow blobs — like the reference screenshot)
# ---------------------------------------------------------------------------
class Cloud:
    def __init__(self, x=None, y=None, speed=None, size=None):
        self.x = x if x is not None else random.uniform(0, SCREEN_WIDTH)
        self.y = y if y is not None else random.uniform(30, SCREEN_HEIGHT * 0.55)
        self.speed = speed if speed is not None else random.uniform(0.15, 0.45)
        self.size = size if size is not None else random.uniform(0.8, 1.8)
        # Each cloud gets a fixed random seed so it looks consistent every frame
        self.seed = random.randint(0, 9999)

    def update(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH + 300:
            self.x = -300
            self.y = random.uniform(30, SCREEN_HEIGHT * 0.55)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        s = self.size
        rng = random.Random(self.seed)

        # ── Shadow blobs (purple-grey, offset down-right) ──
        shadow_c = (160, 150, 185)   # muted purple-grey like the screenshot
        shadow_blobs = [
            (int(10 * s),  int(10 * s),  int(24 * s)),
            (int(-14 * s), int(14 * s),  int(18 * s)),
            (int(28 * s),  int(14 * s),  int(16 * s)),
            (int(6 * s),   int(20 * s),  int(14 * s)),
        ]
        for ox, oy, r in shadow_blobs:
            pygame.draw.circle(surface, shadow_c, (cx + ox, cy + oy), max(1, r))

        # ── Main white cloud blobs (chunky, blocky like pixel art) ──
        # Use large overlapping circles with flat bottom feel
        main_c  = (245, 248, 255)   # near-white
        light_c = (255, 255, 255)   # brightest highlight

        main_blobs = [
            (0,            0,           int(28 * s)),
            (int(-26 * s), int(8 * s),  int(20 * s)),
            (int(26 * s),  int(8 * s),  int(22 * s)),
            (int(-10 * s), int(14 * s), int(18 * s)),
            (int(14 * s),  int(16 * s), int(16 * s)),
            (int(-38 * s), int(14 * s), int(13 * s)),
            (int(40 * s),  int(16 * s), int(12 * s)),
        ]
        for ox, oy, r in main_blobs:
            pygame.draw.circle(surface, main_c, (cx + ox, cy + oy), max(1, r))

        # ── Pixel-art "blocky" highlight on top-left of each main blob ──
        highlight_offsets = [
            (int(-6 * s),  int(-10 * s), int(10 * s)),
            (int(-30 * s), int(-2 * s),  int(8 * s)),
            (int(20 * s),  int(-4 * s),  int(9 * s)),
        ]
        for ox, oy, r in highlight_offsets:
            pygame.draw.circle(surface, light_c, (cx + ox, cy + oy), max(1, r))

        # ── Hard pixel-art edge: draw a 1-pixel dark outline on bottom ──
        # Gives that crisp retro look
        outline_c = (180, 185, 200)
        for ox, oy, r in main_blobs:
            pygame.draw.circle(surface, outline_c, (cx + ox, cy + oy), max(1, r), 1)


# ---------------------------------------------------------------------------
# Floating Island Platform
# ---------------------------------------------------------------------------
class IslandPlatform:
    def __init__(self, x, y, w, h=22):
        self.rect = pygame.Rect(x, y, w, h)

    def is_active(self):
        return True

    def get_rect(self):
        return self.rect

    def on_player_land(self, player):
        pass

    def update(self):
        pass

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -80 or sr.left > SCREEN_WIDTH + 80:
            return

        # ── Stone brick body ──
        STONE_MID   = (140,  80,  90)   # main brick colour (pinkish-red like screenshot)
        STONE_DARK  = ( 90,  45,  55)   # mortar / shadow
        STONE_LIGHT = (175, 110, 120)   # highlight face of brick
        STONE_TOP   = (110,  60,  70)   # top row darker cap

        body = pygame.Rect(sr.x, sr.y + 10, sr.width, sr.height + 40)
        # Fill solid
        pygame.draw.rect(surface, STONE_MID, body)

        # Horizontal mortar lines every 10px
        for my in range(body.top + 10, body.bottom, 10):
            pygame.draw.line(surface, STONE_DARK, (body.left, my), (body.right, my), 1)

        # Vertical brick joints — stagger every row
        rng = random.Random(sr.x * 13 + sr.y * 7)
        brick_w = rng.randint(18, 26)
        for row_i, my in enumerate(range(body.top, body.bottom, 10)):
            offset = (brick_w // 2) if row_i % 2 == 1 else 0
            bx = body.left - offset
            while bx < body.right:
                pygame.draw.line(surface, STONE_DARK, (bx, my), (bx, min(my + 10, body.bottom)), 1)
                # Light highlight on left face of each brick
                pygame.draw.line(surface, STONE_LIGHT, (bx + 1, my + 1), (bx + 1, min(my + 9, body.bottom - 1)), 1)
                bx += brick_w

        # Dark shadow on right and bottom edges
        pygame.draw.rect(surface, STONE_DARK, (body.right - 3, body.top, 3, body.height))
        pygame.draw.rect(surface, STONE_DARK, (body.left, body.bottom - 3, body.width, 3))

        # Top cap row (slightly darker)
        pygame.draw.rect(surface, STONE_TOP, (sr.x, sr.y + 8, sr.width, 6))

        # ── Grass top strip ──
        GRASS_TOP   = ( 80, 170,  70)
        GRASS_SHADE = ( 55, 120,  50)
        GRASS_DARK2 = ( 40,  90,  40)
        pygame.draw.rect(surface, GRASS_TOP,   (sr.x - 1, sr.y - 2, sr.width + 2, 12), border_radius=2)
        pygame.draw.rect(surface, GRASS_SHADE, (sr.x,     sr.y + 5, sr.width,      4))

        # Pixel-art grass tufts — blocky 2px wide spikes
        rng2 = random.Random(sr.x * 31 + sr.y * 17)
        tx = sr.x + 3
        while tx < sr.right - 3:
            th = rng2.randint(3, 7)
            pygame.draw.rect(surface, GRASS_DARK2, (tx, sr.y - 2 - th, 2, th))
            tx += rng2.randint(5, 11)

        # ── Pixel-art trees on top (like the screenshot) ──
        # Only add trees based on platform width and a deterministic seed
        tree_rng = random.Random(sr.x * 99 + sr.y * 43)
        # Decide how many trees (0 to 2 depending on width)
        n_trees = 0
        if sr.width > 60:  n_trees = 1
        if sr.width > 110: n_trees = 2
        if sr.width > 180: n_trees = 3

        # Pick tree x positions spread across the platform
        tree_positions = []
        if n_trees == 1:
            tree_positions = [sr.x + sr.width // 2]
        elif n_trees == 2:
            tree_positions = [sr.x + sr.width // 3, sr.x + 2 * sr.width // 3]
        elif n_trees == 3:
            tree_positions = [sr.x + sr.width // 4,
                              sr.x + sr.width // 2,
                              sr.x + 3 * sr.width // 4]

        for tx2 in tree_positions:
            self._draw_pixel_tree(surface, tx2, sr.y - 2, tree_rng)

    def _draw_pixel_tree(self, surface, cx, base_y, rng):
        """Draw a chunky pixel-art tree like the reference screenshot."""
        TRUNK_DARK  = (100,  60,  30)
        TRUNK_LIGHT = (140,  90,  45)
        POT_RED     = (160,  60,  60)
        POT_DARK    = (110,  35,  35)
        LEAF_MID    = ( 55, 130,  55)
        LEAF_DARK   = ( 35,  90,  40)
        LEAF_LIGHT  = ( 80, 170,  65)

        # Randomise tree height a little
        trunk_h = rng.randint(14, 22)
        canopy_r = rng.randint(12, 18)

        # Pot (small brick-style pot at base)
        pot_w, pot_h = 14, 10
        pot_x = cx - pot_w // 2
        pot_y = base_y - pot_h
        pygame.draw.rect(surface, POT_RED,  (pot_x,     pot_y,     pot_w,     pot_h), border_radius=2)
        pygame.draw.rect(surface, POT_DARK, (pot_x,     pot_y,     pot_w,     2))       # top rim
        pygame.draw.rect(surface, POT_DARK, (pot_x,     pot_y + pot_h - 2, pot_w, 2))  # bottom
        pygame.draw.rect(surface, POT_DARK, (pot_x + pot_w - 2, pot_y, 2, pot_h))      # right shadow

        # Trunk (2 wide for pixel art feel)
        trunk_top = pot_y - trunk_h
        pygame.draw.rect(surface, TRUNK_DARK,  (cx - 2, trunk_top, 4, trunk_h))
        pygame.draw.rect(surface, TRUNK_LIGHT, (cx - 2, trunk_top, 2, trunk_h))  # highlight left

        # Canopy — layered circles for chunky pixel feel
        canopy_cy = trunk_top
        # Shadow layer (dark, slightly offset down)
        pygame.draw.circle(surface, LEAF_DARK,  (cx + 2, canopy_cy + 3), canopy_r)
        # Main canopy
        pygame.draw.circle(surface, LEAF_MID,   (cx,     canopy_cy),     canopy_r)
        # Highlight (top-left dome)
        pygame.draw.circle(surface, LEAF_LIGHT, (cx - canopy_r // 3, canopy_cy - canopy_r // 3),
                           max(3, canopy_r // 2))
        # Hard outline (1px dark ring — pixel art style)
        pygame.draw.circle(surface, LEAF_DARK,  (cx,     canopy_cy),     canopy_r, 1)


# ---------------------------------------------------------------------------
# NPC
# ---------------------------------------------------------------------------
class NPC:
    WIDTH, HEIGHT = 24, 40

    def __init__(self, x, y, dialogue_key, name="Seraphiel"):
        self.rect = pygame.Rect(x, y - self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.dialogue_key = dialogue_key
        self.name = name
        self.talked = False
        self.bob = random.uniform(0, math.pi * 2)
        self.proximity_shown = False

    def check_proximity(self, player):
        dx = abs(player.rect.centerx - self.rect.centerx)
        dy = abs(player.rect.centery - self.rect.centery)
        return dx < 65 and dy < 65

    def draw(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20:
            return
        bob = int(math.sin(tick * 0.04 + self.bob) * 2)
        bx, by = sr.x, sr.y + bob

        is_angel = "Seraphiel" in self.name
        robe_c = ANGEL_BLUE if is_angel else HOLY_GOLD

        # Robe
        pygame.draw.polygon(surface, robe_c,
                            [(bx + 4, by + 14), (bx + 20, by + 14),
                             (bx + 22, by + 40), (bx, by + 40)])
        # Head
        pygame.draw.circle(surface, (220, 190, 160), (bx + 12, by + 10), 8)
        pygame.draw.arc(surface, robe_c, (bx + 2, by, 20, 18), 0.3, 2.8, 3)

        # Eyes
        pygame.draw.circle(surface, WHITE, (bx + 9, by + 9), 2)
        pygame.draw.circle(surface, WHITE, (bx + 15, by + 9), 2)
        pygame.draw.circle(surface, BLACK, (bx + 9, by + 10), 1)
        pygame.draw.circle(surface, BLACK, (bx + 15, by + 10), 1)

        if is_angel:
            # Halo
            halo_pulse = abs(math.sin(tick * 0.05)) * 0.3 + 0.7
            halo_c = tuple(min(255, int(v * halo_pulse)) for v in HOLY_GOLD)
            pygame.draw.ellipse(surface, halo_c, (bx + 2, by - 10, 20, 7), 2)
            # Wings
            wing_a = abs(math.sin(tick * 0.06)) * 8
            pygame.draw.polygon(surface, (220, 230, 255),
                                [(bx + 12, by + 16),
                                 (bx - 12, by + 8 - int(wing_a)),
                                 (bx - 8, by + 20)])
            pygame.draw.polygon(surface, (220, 230, 255),
                                [(bx + 12, by + 16),
                                 (bx + 36, by + 8 - int(wing_a)),
                                 (bx + 32, by + 20)])
            # Sword
            pygame.draw.line(surface, (180, 180, 220), (bx + 22, by + 6), (bx + 22, by + 38), 3)
            pygame.draw.line(surface, HOLY_GOLD, (bx + 16, by + 22), (bx + 28, by + 22), 2)
            pygame.draw.circle(surface, HOLY_GOLD, (bx + 22, by + 6), 4)
            glow = abs(math.sin(tick * 0.1))
            gs = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(gs, (255, 230, 100, int(80 * glow)), (8, 8), 8)
            surface.blit(gs, (bx + 14, by - 2))
        else:
            # Lumen: glowing orb staff
            pygame.draw.line(surface, BROWN, (bx + 22, by + 8), (bx + 22, by + 38), 2)
            pygame.draw.circle(surface, CYAN, (bx + 22, by + 6), 5)
            pygame.draw.circle(surface, WHITE, (bx + 22, by + 6), 2)

        # Name tag
        if not self.talked:
            font = pygame.font.SysFont("consolas", 10, bold=True)
            tag = font.render(self.name, True, HOLY_GOLD)
            surface.blit(font.render(self.name, True, BLACK), (bx + 12 - tag.get_width() // 2 + 1, by - 13))
            surface.blit(tag, (bx + 12 - tag.get_width() // 2, by - 14))
            # Exclamation pulse
            ep = abs(math.sin(tick * 0.1)) * 0.5 + 0.5
            ec = lerp_color(HOLY_GOLD, WHITE, ep)
            ef = pygame.font.SysFont("consolas", 14 + int(ep * 2), bold=True)
            exc = ef.render("!", True, ec)
            surface.blit(exc, (bx + 12 - exc.get_width() // 2, by - 28))

        if self.proximity_shown and not self.talked:
            font2 = pygame.font.SysFont("consolas", 11)
            prompt = font2.render("[E] Talk", True, WHITE)
            pw, ph = prompt.get_width() + 8, prompt.get_height() + 4
            px2, py2 = bx + 12 - pw // 2, by - 40
            pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pill.fill((0, 0, 0, 140))
            surface.blit(pill, (px2, py2))
            surface.blit(prompt, (px2 + 4, py2 + 2))


# ---------------------------------------------------------------------------
# Dialogue Box
# ---------------------------------------------------------------------------
class DialogueBox:
    def __init__(self, dialogues):
        self.dialogues = dialogues
        self.index = 0
        self.active = True
        self.char_index = 0
        self.char_speed = 1.5
        self.char_timer = 0
        self.done_typing = False

    def advance(self):
        if not self.done_typing:
            self.char_index = len(self.dialogues[self.index][1])
            self.done_typing = True
        else:
            self.index += 1
            self.char_index = 0
            self.char_timer = 0
            self.done_typing = False
            if self.index >= len(self.dialogues):
                self.active = False

    def update(self):
        if not self.active or self.done_typing:
            return
        self.char_timer += self.char_speed
        full = self.dialogues[self.index][1]
        self.char_index = min(int(self.char_timer), len(full))
        if self.char_index >= len(full):
            self.done_typing = True

    def draw(self, surface, tick):
        if not self.active:
            return
        box_h = 130
        box_y = SCREEN_HEIGHT - box_h - 20
        box_rect = pygame.Rect(40, box_y, SCREEN_WIDTH - 80, box_h)

        bg = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        r = 6
        for cx2, cy2 in [(r, r), (box_rect.width - r, r),
                         (r, box_rect.height - r), (box_rect.width - r, box_rect.height - r)]:
            pygame.draw.circle(bg, (8, 18, 40, 220), (cx2, cy2), r)
        pygame.draw.rect(bg, (8, 18, 40, 220), (r, 0, box_rect.width - 2 * r, box_rect.height))
        pygame.draw.rect(bg, (8, 18, 40, 220), (0, r, box_rect.width, box_rect.height - 2 * r))
        surface.blit(bg, box_rect.topleft)
        pygame.draw.rect(surface, HOLY_GOLD, box_rect, 2, border_radius=6)

        # Corner ornaments
        for cx3, cy3 in [(box_rect.left + 3, box_rect.top + 3),
                         (box_rect.right - 3, box_rect.top + 3),
                         (box_rect.left + 3, box_rect.bottom - 3),
                         (box_rect.right - 3, box_rect.bottom - 3)]:
            pygame.draw.circle(surface, ANGEL_BLUE, (cx3, cy3), 5)
            pygame.draw.circle(surface, HOLY_GOLD, (cx3, cy3), 3)

        speaker, text = self.dialogues[self.index]
        fn = pygame.font.SysFont("consolas", 17, bold=True)
        ft = pygame.font.SysFont("consolas", 14)
        if speaker:
            nc = HOLY_GOLD if "Seraphiel" in speaker else CYAN
            surface.blit(fn.render(speaker, True, BLACK), (box_rect.x + 17, box_rect.y + 11))
            ns = fn.render(speaker, True, nc)
            surface.blit(ns, (box_rect.x + 16, box_rect.y + 10))
            pygame.draw.line(surface, nc,
                             (box_rect.x + 16, box_rect.y + 30),
                             (box_rect.x + 16 + ns.get_width(), box_rect.y + 30), 1)
            text_y = box_rect.y + 36
        else:
            text_y = box_rect.y + 14

        shown = text[:self.char_index]
        words = shown.split(" ")
        line = ""
        ly = text_y
        max_w = box_rect.width - 32
        for word in words:
            test = line + (" " if line else "") + word
            if ft.size(test)[0] > max_w:
                surface.blit(ft.render(line, True, HOLY_WHITE), (box_rect.x + 16, ly))
                ly += 20
                line = word
            else:
                line = test
        if line:
            surface.blit(ft.render(line, True, HOLY_WHITE), (box_rect.x + 16, ly))

        if self.done_typing and (tick // 20) % 2 == 0:
            lbl = "[ENTER] Continue..." if self.index < len(self.dialogues) - 1 else "[ENTER] Close"
            surface.blit(ft.render(lbl, True, GRAY),
                         (box_rect.right - ft.size(lbl)[0] - 16, box_rect.bottom - 22))

        pg_f = pygame.font.SysFont("consolas", 11)
        surface.blit(pg_f.render(f"{self.index + 1}/{len(self.dialogues)}", True, (60, 60, 80)),
                     (box_rect.x + 16, box_rect.bottom - 18))


# ---------------------------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------------------------
class Checkpoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y - 50, 20, 50)
        self.spawn_x = x
        self.spawn_y = y - 60
        self.activated = False
        self.glow = 0
        self.base_y = y

    def update(self):
        if self.activated:
            self.glow = (self.glow + 3) % 360

    def check(self, player):
        if not self.activated and player.rect.colliderect(self.rect):
            self.activated = True
            player.set_checkpoint(self.spawn_x, self.spawn_y)
            return True
        return False

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        cx = sr.centerx
        # Pole
        pygame.draw.rect(surface, BROWN, (cx - 3, sr.bottom - 12, 6, 12))
        # Star on top
        star_c = HOLY_GOLD if self.activated else DARK_GRAY
        pygame.draw.circle(surface, star_c, (cx, sr.bottom - 60), 7)
        if self.activated:
            gp = abs(math.sin(math.radians(self.glow))) * 0.5 + 0.5
            pygame.draw.circle(surface, WHITE, (cx, sr.bottom - 60), 4)
            # Light rays
            for i in range(6):
                a = math.radians(self.glow + i * 60)
                x1 = cx + int(math.cos(a) * 8)
                y1 = sr.bottom - 60 + int(math.sin(a) * 8)
                x2 = cx + int(math.cos(a) * 14)
                y2 = sr.bottom - 60 + int(math.sin(a) * 14)
                pygame.draw.line(surface, HOLY_GOLD, (x1, y1), (x2, y2), 1)
            pygame.draw.rect(surface, tuple(int(v * gp) for v in HOLY_GOLD), sr.inflate(8, 8), 2)


# ---------------------------------------------------------------------------
# Exit Portal
# ---------------------------------------------------------------------------
class ExitPortal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y - 80, 60, 80)
        self.pulse = 0
        self.particles = []

    def update(self):
        self.pulse = (self.pulse + 2) % 360
        if random.random() < 0.5:
            self.particles.append([
                self.rect.centerx + random.randint(-20, 20),
                float(self.rect.bottom - 5),
                random.uniform(-0.3, 0.3),
                random.uniform(-2.0, -0.8),
                random.randint(30, 55),
                random.choice([HOLY_GOLD, SUN_YELLOW, WHITE, ANGEL_BLUE])
            ])
        self.particles = [[x + vx, y + vy, vx, vy, t - 1, c]
                          for x, y, vx, vy, t, c in self.particles if t > 1]

    def check(self, player):
        return player.rect.colliderect(self.rect)

    def draw(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        cx, cy = sr.centerx, sr.centery
        p = abs(math.sin(math.radians(self.pulse)))

        # Glow
        for gr, ga in [(70, 30), (50, 55), (35, 90)]:
            gs = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*SUN_GOLD, int(ga * (0.6 + 0.4 * p))), (gr, gr), gr)
            surface.blit(gs, (cx - gr, cy - 10 - gr))

        # Pillar archway
        pw = 10
        pygame.draw.rect(surface, (160, 130, 60), (sr.x - 4, sr.y + 16, pw, sr.height - 16))
        pygame.draw.rect(surface, (160, 130, 60), (sr.right - pw + 4, sr.y + 16, pw, sr.height - 16))
        pygame.draw.ellipse(surface, (160, 130, 60), (sr.x - 4, sr.y - 4, sr.width + 8, 42))

        # Inner portal glow
        inner = pygame.Rect(sr.x + 8, sr.y + 18, sr.width - 16, sr.height - 22)
        void = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        for row in range(inner.height):
            t2 = row / max(1, inner.height - 1)
            rc = lerp_color((255, 230, 80), (200, 240, 255), t2)
            al = 180 + int(75 * p)
            pygame.draw.line(void, (*rc, min(255, al)), (0, row), (inner.width, row))
        surface.blit(void, inner.topleft)

        # Particles
        for px, py, _, _, pt, pc in self.particles:
            pp = camera.apply(pygame.Rect(int(px), int(py), 1, 1))
            al = min(255, int(pt * 5))
            sz = 1 + int(pt / 18)
            ps = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*pc, al), (sz, sz), sz)
            surface.blit(ps, (pp.x - sz, pp.y - sz))

        # Label
        font = pygame.font.SysFont("consolas", 11, bold=True)
        lbl = font.render("The way home...", True, HOLY_GOLD)
        ly = sr.top - 22 + int(math.sin(tick * 0.05) * 3)
        surface.blit(lbl, (cx - lbl.get_width() // 2, ly))


# ---------------------------------------------------------------------------
# Arrow  (player projectile)
# ---------------------------------------------------------------------------
class Arrow:
    RADIUS = 4

    def __init__(self, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        norm = math.sqrt(vx * vx + vy * vy) or 1
        self.vx = vx / norm * ARROW_SPEED
        self.vy = vy / norm * ARROW_SPEED
        self.lifetime = ARROW_LIFETIME
        self.alive = True
        self.angle = math.atan2(vy, vx)
        self.trail = []  # frost trail: list of (x, y, alpha)

    def update(self):
        # Save trail point before moving
        self.trail.append((self.x, self.y, 200))
        if len(self.trail) > 10:
            self.trail.pop(0)
        self.trail = [(x, y, a - 22) for x, y, a in self.trail if a > 22]

        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # slight gravity
        self.angle = math.atan2(self.vy, self.vx)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
        return self.alive

    def get_rect(self):
        return pygame.Rect(int(self.x) - self.RADIUS, int(self.y) - self.RADIUS,
                           self.RADIUS * 2, self.RADIUS * 2)

    def draw(self, surface, camera, tick):
        if not self.alive:
            return

        # ── Frost trail ──
        for i, (tx, ty, ta) in enumerate(self.trail):
            tp = camera.apply(pygame.Rect(int(tx), int(ty), 1, 1))
            frac = (i + 1) / max(1, len(self.trail))
            r = max(1, int(4 * frac))
            a = max(0, min(255, int(ta * frac)))
            ts = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            c = lerp_color(ICE_DARK, ICE_WHITE, frac)
            pygame.draw.circle(ts, (*c, a), (r + 1, r + 1), r)
            surface.blit(ts, (tp.x - r - 1, tp.y - r - 1))

        p = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))

        # ── Shaft ──
        length = 18
        ex = p.x + int(math.cos(self.angle) * length)
        ey = p.y + int(math.sin(self.angle) * length)
        pygame.draw.line(surface, (60, 60, 80), (p.x + 1, p.y + 1), (ex + 1, ey + 1), 2)  # shadow
        pygame.draw.line(surface, ICE_DARK,  (p.x, p.y), (ex, ey), 3)
        pygame.draw.line(surface, ICE_WHITE, (p.x, p.y), (ex, ey), 1)

        # ── Ice crystal tip ──
        pygame.draw.circle(surface, ICE_BLUE,  (ex, ey), 4)
        pygame.draw.circle(surface, ICE_WHITE, (ex, ey), 2)
        if tick % 4 < 2:  # sparkle blink
            pygame.draw.line(surface, WHITE, (ex - 3, ey), (ex + 3, ey), 1)
            pygame.draw.line(surface, WHITE, (ex, ey - 3), (ex, ey + 3), 1)

        # ── Tail feathers ──
        bx = p.x + int(math.cos(self.angle + math.pi) * 8)
        by = p.y + int(math.sin(self.angle + math.pi) * 8)
        pygame.draw.line(surface, ICE_WHITE, (bx, by),
                         (bx + int(math.cos(self.angle + math.pi / 2) * 5),
                          by + int(math.sin(self.angle + math.pi / 2) * 5)), 1)
        pygame.draw.line(surface, ICE_WHITE, (bx, by),
                         (bx + int(math.cos(self.angle - math.pi / 2) * 5),
                          by + int(math.sin(self.angle - math.pi / 2) * 5)), 1)


# ---------------------------------------------------------------------------
# Water Balloon  (Santa projectile)
# ---------------------------------------------------------------------------
class WaterBalloon:
    RADIUS = 9

    def __init__(self, x, y, target_x, target_y):
        self.x = float(x)
        self.y = float(y)
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy) or 1
        # Give balloon an arc: aim below target
        self.vx = (dx / dist) * SANTA_BALLOON_SPEED
        self.vy = (dy / dist) * SANTA_BALLOON_SPEED - 2
        self.lifetime = BALLOON_LIFETIME
        self.alive = True
        self.splashing = False
        self.splash_timer = 0
        self.splash_x = 0
        self.splash_y = 0

    def update(self, platforms):
        if self.splashing:
            self.splash_timer -= 1
            return self.splash_timer > 0
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.18  # gravity
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            return False
        # Check platform collision
        br = self.get_rect()
        for plat in platforms:
            if plat.is_active() and br.colliderect(plat.get_rect()):
                self.splashing = True
                self.splash_timer = 18
                self.splash_x = int(self.x)
                self.splash_y = plat.get_rect().top
                return True
        return True

    def get_rect(self):
        return pygame.Rect(int(self.x) - self.RADIUS, int(self.y) - self.RADIUS,
                           self.RADIUS * 2, self.RADIUS * 2)

    def draw(self, surface, camera, tick):
        if not self.alive:
            return
        if self.splashing:
            # Splash ripple
            sp = camera.apply(pygame.Rect(self.splash_x, self.splash_y, 1, 1))
            r = int((18 - self.splash_timer) * 2.5)
            a = max(0, int(255 * self.splash_timer / 18))
            pygame.draw.circle(surface, (100, 160, 255), (sp.x, sp.y), r, 2)
            for _ in range(2):
                ox = random.randint(-r, r)
                pygame.draw.circle(surface, (150, 200, 255), (sp.x + ox, sp.y - random.randint(0, 4)), 2)
            return
        p = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        # Balloon body
        pygame.draw.circle(surface, BALLOON_DARK, (p.x, p.y), self.RADIUS + 1)
        pygame.draw.circle(surface, BALLOON_BLUE, (p.x, p.y), self.RADIUS)
        pygame.draw.circle(surface, (140, 190, 255), (p.x - 2, p.y - 2), 3)
        # String
        pygame.draw.line(surface, (180, 180, 200), (p.x, p.y + self.RADIUS), (p.x + 2, p.y + self.RADIUS + 5), 1)


# ---------------------------------------------------------------------------
# Mushroom Enemy
# ---------------------------------------------------------------------------
class MushroomEnemy:
    WIDTH, HEIGHT = 28, 28

    def __init__(self, x, y, pl, pr, speed=1.3):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.patrol_left = pl
        self.patrol_right = pr
        self.speed = speed
        self.direction = 1
        self.alive = True
        self.death_timer = 0
        self.squish_timer = 0
        self.tick = 0

    def update(self):
        if not self.alive:
            self.death_timer -= 1
            return
        if self.squish_timer > 0:
            self.squish_timer -= 1
            if self.squish_timer <= 0:
                self.alive = False
                self.death_timer = 1
            return
        self.tick += 1
        self.rect.x += int(self.speed * self.direction)
        if self.rect.x >= self.patrol_right:
            self.rect.x = self.patrol_right
            self.direction = -1
        elif self.rect.x <= self.patrol_left:
            self.rect.x = self.patrol_left
            self.direction = 1

    def stomp(self):
        self.squish_timer = 12

    def kill(self):
        self.alive = False
        self.death_timer = 1

    def check_collision(self, player):
        if not self.alive or self.squish_timer > 0 or not player.alive:
            return None
        if not self.rect.colliderect(player.rect):
            return None
        if player.vel_y > 0 and player.rect.bottom <= self.rect.centery + 8:
            return "stomp"
        return "kill_player"

    def draw(self, surface, camera, tick):
        if not self.alive:
            return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
            return
        if self.squish_timer > 0:
            flat = pygame.Rect(sr.x - 4, sr.bottom - 8, sr.width + 8, 8)
            pygame.draw.rect(surface, BROWN, flat)
            pygame.draw.ellipse(surface, MUSHROOM_RED, (flat.x, flat.y - 4, flat.width, 8))
            return
        bob = int(math.sin(self.tick * 0.2) * 1.5)
        # Stem
        pygame.draw.rect(surface, BROWN, (sr.x + 4, sr.centery + bob, sr.width - 8, sr.height // 2))
        # Cap
        cr = pygame.Rect(sr.x - 2, sr.y + bob, sr.width + 4, sr.height // 2 + 4)
        pygame.draw.ellipse(surface, MUSHROOM_RED, cr)
        # Spots
        for sx2, sy2, r2 in [(cr.x + 6, cr.y + 5, 3), (cr.right - 8, cr.y + 4, 3), (cr.centerx, cr.y + 2, 2)]:
            pygame.draw.circle(surface, WHITE, (sx2, sy2 + bob), r2)
        # Feet
        pygame.draw.ellipse(surface, (100, 65, 30), (sr.x + 2, sr.bottom + bob - 4, 8, 5))
        pygame.draw.ellipse(surface, (100, 65, 30), (sr.right - 10, sr.bottom + bob - 4, 8, 5))
        # Eyes
        ey2 = sr.centery - 2 + bob
        po = 1 if self.direction > 0 else -1
        for ex2 in [sr.centerx - 6, sr.centerx + 6]:
            pygame.draw.circle(surface, WHITE, (ex2, ey2), 4)
            pygame.draw.circle(surface, BLACK, (ex2 + po, ey2 + 1), 2)


# ---------------------------------------------------------------------------
# Santa Boss
# ---------------------------------------------------------------------------
class SantaBoss:
    WIDTH, HEIGHT = 80, 80
    DAMAGE_STAGES = [10, 7, 5, 3, 1]  # hp thresholds for visual stages

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.hp = SANTA_MAX_HP
        self.max_hp = SANTA_MAX_HP
        self.alive = True
        self.dead = False
        self.death_timer = 0
        self.explosion_timer = 0
        self.invincibility = 0  # frames after being hit
        self.balloon_cooldown = 0
        self.tick = 0
        # Movement
        self.vx = 1.8
        self.base_y = float(y)
        self.descent = 0.0  # total descent over fight
        self.appeared = False
        self.appear_timer = 0
        # Gift drop
        self.gift_dropped = False
        self.gift = None

    def hit(self):
        if self.invincibility > 0 or self.dead:
            return False
        self.hp -= 1
        self.invincibility = 20
        if self.hp <= 0:
            self.dead = True
            self.explosion_timer = 60
            return True
        return False

    def update(self, player_x, player_y, platforms, balloons):
        if not self.alive:
            return
        self.tick += 1
        if self.invincibility > 0:
            self.invincibility -= 1

        if self.dead:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.alive = False
                # Drop gift
                if not self.gift_dropped:
                    self.gift_dropped = True
                    self.gift = GiftPickup(self.rect.centerx, self.rect.centery)
            return

        # Appear from right edge
        if not self.appeared:
            self.appear_timer += 1
            self.rect.x -= 2
            if self.rect.x < player_x + 300:
                self.appeared = True
            return

        # Side-to-side movement
        self.rect.x += int(self.vx)
        # Bounce off world edges (wide range)
        if self.rect.x > player_x + 500:
            self.vx = -abs(self.vx)
        elif self.rect.x < player_x - 300:
            self.vx = abs(self.vx)

        # Gradual descent: total 200px over full fight
        progress = 1.0 - self.hp / self.max_hp
        target_descent = progress * 200
        if self.descent < target_descent:
            self.descent += 0.4
        self.rect.y = int(self.base_y + self.descent + math.sin(self.tick * 0.03) * 12)

        # Throw balloons
        self.balloon_cooldown -= 1
        # Shoot faster as hp drops
        interval = max(50, SANTA_BALLOON_INTERVAL - int((1.0 - progress) * 0) - int(progress * 60))
        if self.balloon_cooldown <= 0 and self.appeared:
            self.balloon_cooldown = interval
            balloons.append(WaterBalloon(
                self.rect.centerx, self.rect.bottom,
                player_x, player_y))

    def draw(self, surface, camera, tick):
        if not self.alive:
            return
        sr = camera.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20:
            return

        # Explosion effect
        if self.dead:
            prog = 1.0 - self.explosion_timer / 60
            for i in range(3):
                er = int((40 + i * 30) * prog)
                ec = [FIRE_ORANGE, FIRE_RED, FIRE_YELLOW][i]
                ea = max(0, int(255 * (1 - prog)))
                if er > 0:
                    pygame.draw.circle(surface, tuple(max(0, min(255, int(c * ea / 255))) for c in ec),
                                       (sr.centerx, sr.centery), er)
            if self.explosion_timer > 30:
                pygame.draw.circle(surface, WHITE, (sr.centerx, sr.centery), int(20 * prog))
            return

        # Damage stage: visual degradation
        damage_stage = 0
        for i, threshold in enumerate(self.DAMAGE_STAGES):
            if self.hp <= threshold:
                damage_stage = i + 1

        # Invincibility flicker
        if self.invincibility > 0 and (self.invincibility // 3) % 2 == 0:
            return

        cx, cy = sr.centerx, sr.centery

        # ── Balloon vessel ──
        # Balloon string
        string_sway = int(math.sin(self.tick * 0.04) * 6)
        balloon_cx = cx + string_sway
        balloon_cy = cy - 40

        # Balloon (gets more torn per stage)
        balloon_r = 32
        balloon_c = lerp_color(BALLOON_BLUE, (160, 80, 80), damage_stage / 5)
        pygame.draw.circle(surface, balloon_c, (balloon_cx, balloon_cy), balloon_r)
        pygame.draw.circle(surface, tuple(min(255, v + 40) for v in balloon_c),
                           (balloon_cx - 8, balloon_cy - 10), 10)

        # Damage cracks on balloon
        if damage_stage >= 1:
            for i in range(damage_stage * 2):
                a = i * math.pi / damage_stage + self.tick * 0.01
                x1 = balloon_cx + int(math.cos(a) * 18)
                y1 = balloon_cy + int(math.sin(a) * 18)
                x2 = balloon_cx + int(math.cos(a + 0.3) * (balloon_r - 2))
                y2 = balloon_cy + int(math.sin(a + 0.3) * (balloon_r - 2))
                pygame.draw.line(surface, (100, 60, 60), (x1, y1), (x2, y2), 1)

        # String from balloon to Santa
        for i in range(8):
            t = i / 7
            sx = balloon_cx + int((cx - balloon_cx) * t) + int(math.sin(t * math.pi + self.tick * 0.05) * 3)
            sy = balloon_cy + int((cy - 28 - balloon_cy) * t)
            pygame.draw.circle(surface, (180, 180, 200), (sx, sy), 1)

        # ── Santa body ──
        body_r = pygame.Rect(cx - 22, cy - 20, 44, 44)
        santa_c = lerp_color(SANTA_RED, (120, 40, 40), damage_stage / 5)
        pygame.draw.ellipse(surface, santa_c, body_r)

        # Belt
        pygame.draw.rect(surface, BLACK, (cx - 22, cy + 2, 44, 5))
        pygame.draw.rect(surface, XMAS_GOLD, (cx - 6, cy, 12, 8))

        # White trim
        pygame.draw.ellipse(surface, SANTA_WHITE, (cx - 23, cy - 23, 46, 14))
        pygame.draw.ellipse(surface, SANTA_WHITE, (cx - 24, cy + 18, 48, 12))

        # Head
        pygame.draw.circle(surface, (220, 180, 155), (cx, cy - 28), 14)
        # Hat
        pygame.draw.polygon(surface, santa_c,
                            [(cx - 14, cy - 28), (cx + 14, cy - 28), (cx + 6, cy - 50), (cx - 4, cy - 50)])
        pygame.draw.rect(surface, SANTA_WHITE, (cx - 15, cy - 32, 30, 7))
        pygame.draw.circle(surface, SANTA_WHITE, (cx + 4, cy - 50), 4)

        # Eyes (angry on low hp)
        if damage_stage >= 3:
            pygame.draw.line(surface, BLACK, (cx - 8, cy - 32), (cx - 4, cy - 30), 2)
            pygame.draw.line(surface, BLACK, (cx + 8, cy - 32), (cx + 4, cy - 30), 2)
        pygame.draw.circle(surface, BLACK, (cx - 5, cy - 28), 2)
        pygame.draw.circle(surface, BLACK, (cx + 5, cy - 28), 2)

        # Arms (holding a balloon sack)
        pygame.draw.line(surface, santa_c, (cx - 22, cy - 4), (cx - 38, cy + 10), 5)
        pygame.draw.line(surface, santa_c, (cx + 22, cy - 4), (cx + 38, cy + 10), 5)
        pygame.draw.circle(surface, BALLOON_BLUE, (cx + 40, cy + 12), 8)

        # HP bar above Santa
        bar_w = 90
        bar_x = cx - bar_w // 2
        bar_y = sr.y - 26
        pygame.draw.rect(surface, (40, 40, 40), (bar_x - 2, bar_y - 2, bar_w + 4, 14))
        ratio = self.hp / self.max_hp
        bar_c = lerp_color(FIRE_RED, GRASS_GREEN, ratio)
        pygame.draw.rect(surface, bar_c, (bar_x, bar_y, int(bar_w * ratio), 10))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, 10), 1)
        hp_f = pygame.font.SysFont("consolas", 9, bold=True)
        hp_t = hp_f.render(f"SANTA {self.hp}/{self.max_hp}", True, WHITE)
        surface.blit(hp_t, (cx - hp_t.get_width() // 2, bar_y - 1))


# ---------------------------------------------------------------------------
# Gift Power-up (dropped by Santa)
# ---------------------------------------------------------------------------
class GiftPickup:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vy = -3.0
        self.on_ground = False
        self.collected = False
        self.tick = 0
        self.rect = pygame.Rect(int(x) - 14, int(y) - 14, 28, 28)

    def update(self, platforms):
        self.tick += 1
        if not self.on_ground:
            self.vy += 0.3
            self.y += self.vy
            self.rect.y = int(self.y) - 14
            for plat in platforms:
                if plat.is_active() and self.rect.colliderect(plat.get_rect()):
                    self.rect.bottom = plat.get_rect().top
                    self.y = float(self.rect.y + 14)
                    self.vy = 0
                    self.on_ground = True
                    break

    def check(self, player):
        if self.collected or not player.alive:
            return False
        if self.rect.colliderect(player.rect):
            self.collected = True
            return True
        return False

    def draw(self, surface, camera, tick):
        if self.collected:
            return
        bob = math.sin(self.tick * 0.08) * 4 if self.on_ground else 0
        sr = camera.apply(pygame.Rect(int(self.x) - 14, int(self.y - bob) - 14, 28, 28))
        # Gift box
        pygame.draw.rect(surface, GIFT_RED, sr, border_radius=3)
        pygame.draw.rect(surface, GIFT_GREEN, (sr.x, sr.centery - 3, sr.width, 6))
        pygame.draw.rect(surface, GIFT_GREEN, (sr.centerx - 3, sr.y, 6, sr.height))
        # Bow
        pygame.draw.circle(surface, GIFT_GOLD, (sr.centerx - 5, sr.y), 4)
        pygame.draw.circle(surface, GIFT_GOLD, (sr.centerx + 5, sr.y), 4)
        pygame.draw.circle(surface, WHITE, (sr.centerx, sr.y), 3)
        # Glow
        glow_a = int(abs(math.sin(self.tick * 0.1)) * 80 + 40)
        gs = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*HOLY_GOLD, glow_a), (25, 25), 25)
        surface.blit(gs, (sr.centerx - 25, sr.centery - 25))
        # Label
        font = pygame.font.SysFont("consolas", 10, bold=True)
        lbl = font.render("POWER GIFT!", True, HOLY_GOLD)
        surface.blit(lbl, (sr.centerx - lbl.get_width() // 2, sr.y - 16))


# ---------------------------------------------------------------------------
# Player (Archer)
# ---------------------------------------------------------------------------
class Player:
    WIDTH, HEIGHT = 28, 36

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.spawn_x = x
        self.spawn_y = y
        self.alive = True
        self.respawn_timer = 0
        self.facing_right = True
        self.jump_count = 0
        self.max_jumps = 2
        self.hearts = PLAYER_MAX_HEARTS
        self.invincibility = 0
        self.death_count = 0
        self.kill_count = 0
        self.shoot_cooldown = 0
        self.sprinting = False
        self.was_on_ground = False
        self.squash_timer = 0
        self.has_gift_power = False
        self.gift_power_timer = 0
        self.riding_platform = None
        # Sprite animation
        if _SPRITES_AVAILABLE:
            init_player_sprite(self)

    def set_checkpoint(self, x, y):
        self.spawn_x = x
        self.spawn_y = y

    def take_damage(self):
        if self.invincibility > 0:
            return False
        self.hearts -= 1
        self.invincibility = INVINCIBILITY_FRAMES
        if self.hearts <= 0:
            self.die()
        return True

    def die(self):
        self.alive = False
        self.respawn_timer = 80
        self.death_count += 1
        if _SPRITES_AVAILABLE:
            self._spr_state = 'death'; self._spr_frame = 0
            self._spr_tick = 0; self._spr_death_done = False

    def respawn(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.vel_x = self.vel_y = 0
        self.alive = True
        self.on_ground = False
        self.hearts = PLAYER_MAX_HEARTS
        self.invincibility = 0
        self.jump_count = 0

    def update(self, keys, platforms):
        if not self.alive:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawn()
            return None

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincibility > 0:
            self.invincibility -= 1
        if self.gift_power_timer > 0:
            self.gift_power_timer -= 1
            if self.gift_power_timer <= 0:
                self.has_gift_power = False

        # Movement
        move = 0.0
        self.sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed = SPRINT_SPEED if self.sprinting else MOVE_SPEED
        if self.has_gift_power:
            speed += 2
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += speed
            self.facing_right = True

        friction = 0.28
        if move:
            self.vel_x += (move - self.vel_x) * friction
        else:
            self.vel_x *= 0.72
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0

        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

        jumped = False
        if self.on_ground and self.jump_count == 0 and (
                keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False
            self.riding_platform = None
            jumped = True
            self.jump_count = 1

        # Horizontal collision
        self.rect.x += int(self.vel_x)
        for plat in platforms:
            if not plat.is_active():
                continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.rect.bottom <= pr.top + 6:
                    continue
                if self.vel_x > 0:
                    self.rect.right = pr.left
                elif self.vel_x < 0:
                    self.rect.left = pr.right
                self.vel_x = 0

        self.was_on_ground = self.on_ground
        self.on_ground = False
        self.riding_platform = None

        vy = int(self.vel_y)
        if self.vel_y > 0 and vy == 0:
            vy = 1
        self.rect.y += vy

        for plat in platforms:
            if not plat.is_active():
                continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.vel_y > 0:
                    self.rect.bottom = pr.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                    plat.on_player_land(self)
                elif self.vel_y < 0:
                    self.rect.top = pr.bottom
                    self.vel_y = 0

        if self.rect.top > DEATH_Y:
            self.alive = False; self.respawn_timer = 80; self.death_count += 1
            if _SPRITES_AVAILABLE:
                self._spr_state = 'death'; self._spr_frame = 0
                self._spr_tick = 0; self._spr_death_done = False

        return "jump" if jumped else None

    def try_shoot_arrow(self, target_x, target_y):
        if self.shoot_cooldown <= 0 and self.alive:
            cd = ARROW_COOLDOWN
            if self.has_gift_power:
                cd = max(8, cd - 8)
            self.shoot_cooldown = cd
            sx = self.rect.right + 4 if self.facing_right else self.rect.left - 4
            sy = self.rect.centery - 4
            # Direction toward mouse
            dx = target_x - sx
            dy = target_y - sy
            return Arrow(sx, sy, dx, dy)
        return None

    def activate_gift_power(self):
        self.has_gift_power = True
        self.gift_power_timer = 600  # 10 seconds

    def draw(self, surface, camera, tick):
        if not self.alive:
            # Still draw death animation if sprites available
            if _SPRITES_AVAILABLE:
                draw_player_sprite(self, surface, camera, tick,
                                   unreal_tint_fn=lambda t: (255, 220, 50))
            return

        if self.on_ground and not self.was_on_ground:
            self.squash_timer = 6
        if self.squash_timer > 0:
            self.squash_timer -= 1

        # Invincibility flicker
        if self.invincibility > 0 and (self.invincibility // 4) % 2 == 0:
            return

        # Gift power glow (drawn before sprite)
        if self.has_gift_power:
            sr_glow = camera.apply(self.rect)
            gp = abs(math.sin(tick * 0.12)) * 0.5 + 0.5
            gs = pygame.Surface((sr_glow.width + 16, sr_glow.height + 16), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*HOLY_GOLD, int(60 * gp)), (0, 0, sr_glow.width + 16, sr_glow.height + 16), border_radius=4)
            surface.blit(gs, (sr_glow.x - 8, sr_glow.y - 8))

        # Use sprite sheet if available, otherwise fall back to drawn character
        if _SPRITES_AVAILABLE:
            draw_player_sprite(self, surface, camera, tick,
                               unreal_tint_fn=lambda t: (255, 220, 50))
            return

        # ── Fallback: drawn archer character ──────────────────────────────
        sr = camera.apply(self.rect)
        if self.vel_y < -3 and not self.on_ground:
            stretch = 4
            sr = sr.inflate(-4, stretch * 2)
            sr.bottom += stretch
        elif self.squash_timer > 0:
            sq = int(self.squash_timer * 0.8)
            sr = sr.inflate(sq * 2, -sq * 2)
            sr.bottom += sq

        # Body (tunic)
        pygame.draw.rect(surface, HERO_GREEN, sr)
        belt_y = sr.y + sr.height - 14
        pygame.draw.rect(surface, BROWN, (sr.x, belt_y, sr.width, 4))
        pygame.draw.rect(surface, XMAS_GOLD, (sr.centerx - 4, belt_y - 1, 8, 6))
        pygame.draw.polygon(surface, (40, 100, 40),
                            [(sr.x, sr.bottom), (sr.x - 3, sr.bottom + 6),
                             (sr.x + sr.width // 2, sr.bottom + 3),
                             (sr.right + 3, sr.bottom + 6), (sr.right, sr.bottom)])
        face_y = sr.y + 6
        pygame.draw.rect(surface, (220, 185, 145), (sr.x + 4, face_y, sr.width - 8, 12))
        pygame.draw.polygon(surface, HERO_BROWN,
                            [(sr.x + 2, face_y + 2), (sr.x + sr.width - 2, face_y + 2),
                             (sr.x + sr.width + 2, face_y - 5), (sr.x - 2, face_y - 5)])
        ey = sr.y + 10
        if self.facing_right:
            pygame.draw.rect(surface, WHITE, (sr.x + 14, ey, 7, 5))
            pygame.draw.rect(surface, BLACK, (sr.x + 17, ey + 1, 3, 3))
        else:
            pygame.draw.rect(surface, WHITE, (sr.x + 7, ey, 7, 5))
            pygame.draw.rect(surface, BLACK, (sr.x + 7, ey + 1, 3, 3))
        bow_x = sr.left - 6 if self.facing_right else sr.right + 6
        bow_y = sr.centery
        bow_arc_rect = pygame.Rect(bow_x - 5, bow_y - 12, 10, 24)
        if self.facing_right:
            pygame.draw.arc(surface, ARROW_BROWN, bow_arc_rect, math.pi / 2, 3 * math.pi / 2, 3)
            pygame.draw.line(surface, (200, 200, 220), (bow_x - 5, bow_y - 12), (bow_x - 5, bow_y + 12), 1)
        else:
            pygame.draw.arc(surface, ARROW_BROWN, bow_arc_rect, -math.pi / 2, math.pi / 2, 3)
            pygame.draw.line(surface, (200, 200, 220), (bow_x + 5, bow_y - 12), (bow_x + 5, bow_y + 12), 1)
        nock_x = bow_x + (4 if self.facing_right else -4)
        pygame.draw.line(surface, ARROW_BROWN, (nock_x, bow_y - 6),
                         (nock_x + (10 if self.facing_right else -10), bow_y - 2), 1)


# ---------------------------------------------------------------------------
# Level Builder
# ---------------------------------------------------------------------------
def create_level():
    platforms = []
    checkpoints = []
    mushrooms = []
    npcs = []

    # ── Section 1: Ground intro (0 – 2200) ──
    # Wide starting ground
    platforms.append(IslandPlatform(0, 520, 500))
    npcs.append(NPC(120, 520, "intro", "Seraphiel"))
    platforms.append(IslandPlatform(650, 490, 160))
    platforms.append(IslandPlatform(930, 450, 160))
    platforms.append(IslandPlatform(1200, 490, 160))
    platforms.append(IslandPlatform(1480, 450, 200))
    platforms.append(IslandPlatform(1780, 490, 300))
    mushrooms.append(MushroomEnemy(700, 464, 650, 790, speed=1.2))
    mushrooms.append(MushroomEnemy(1800, 464, 1780, 2060, speed=1.3))
    checkpoints.append(Checkpoint(1820, 490))
    npcs.append(NPC(1870, 490, "cp1", "Lumen"))

    # ── Section 2: Rising islands (2200 – 4800) ──
    platforms.append(IslandPlatform(2200, 440, 150))
    platforms.append(IslandPlatform(2480, 400, 140))
    platforms.append(IslandPlatform(2760, 360, 140))
    platforms.append(IslandPlatform(3060, 320, 140))
    platforms.append(IslandPlatform(3340, 360, 140))
    platforms.append(IslandPlatform(3640, 310, 140))
    platforms.append(IslandPlatform(3930, 350, 160))
    platforms.append(IslandPlatform(4220, 300, 140))
    platforms.append(IslandPlatform(4520, 340, 180))
    mushrooms.append(MushroomEnemy(2490, 374, 2480, 2600, speed=1.4))
    mushrooms.append(MushroomEnemy(3350, 334, 3340, 3460, speed=1.5))
    mushrooms.append(MushroomEnemy(4230, 274, 4220, 4340, speed=1.5))
    checkpoints.append(Checkpoint(4540, 340))
    npcs.append(NPC(4580, 340, "cp2", "Seraphiel"))

    # ── Section 3: Sky peaks (5000 – 8000) ──
    platforms.append(IslandPlatform(5000, 280, 150))
    platforms.append(IslandPlatform(5300, 240, 140))
    platforms.append(IslandPlatform(5620, 200, 140))
    platforms.append(IslandPlatform(5940, 240, 140))
    platforms.append(IslandPlatform(6260, 200, 130))
    platforms.append(IslandPlatform(6580, 240, 140))
    platforms.append(IslandPlatform(6900, 200, 140))
    platforms.append(IslandPlatform(7220, 240, 140))
    platforms.append(IslandPlatform(7540, 220, 200))  # wide rest before boss
    mushrooms.append(MushroomEnemy(5310, 214, 5300, 5420, speed=1.6))
    mushrooms.append(MushroomEnemy(6270, 174, 6260, 6380, speed=1.6))
    mushrooms.append(MushroomEnemy(7230, 214, 7220, 7360, speed=1.7))
    checkpoints.append(Checkpoint(7560, 220))
    npcs.append(NPC(7610, 220, "cp3", "Lumen"))

    # ── Section 4: Final approach (8200 – 10200) ──
    platforms.append(IslandPlatform(8200, 240, 150))
    platforms.append(IslandPlatform(8500, 200, 140))
    platforms.append(IslandPlatform(8800, 240, 150))
    platforms.append(IslandPlatform(9100, 200, 140))
    platforms.append(IslandPlatform(9400, 240, 180))
    platforms.append(IslandPlatform(9700, 200, 160))
    platforms.append(IslandPlatform(10000, 240, 400))  # final wide platform
    mushrooms.append(MushroomEnemy(8510, 174, 8500, 8620, speed=1.7))
    mushrooms.append(MushroomEnemy(9410, 214, 9400, 9560, speed=1.8))
    mushrooms.append(MushroomEnemy(10020, 214, 10000, 10360, speed=1.8))

    exit_portal = ExitPortal(10310, 240)

    return platforms, checkpoints, mushrooms, npcs, exit_portal


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None or self.screen.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Endless Dream — The Sky Trial")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 48)
        self.tiny_font = pygame.font.SysFont("consolas", 12, bold=True)

        self.sfx = SoundManager()
        self.state = "playing"
        self.tick = 0
        self.level_time = 0
        self.win_timer = 0
        self.freeze_frames = 0
        self.respawn_fade = 0
        self.music_volume = 0.5
        self.music_muted = False
        self.settings_cursor = 0

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = []
        self.rings = []
        self.flashes = []
        self.damage_flashes = []
        self.score_popups = []
        self.arrows = []
        self.balloons = []
        self.clouds = [Cloud() for _ in range(18)]

        # Santa boss (spawns at section 3)
        self.santa = None
        self.santa_spawned = False
        self.santa_spawn_x = 7800  # spawns when player reaches ~x=5000
        self.santa_trigger_x = 5000

        self.gift = None  # GiftPickup after Santa dies

        self.dialogue_box = None
        self.pending_state = None

        # Death / resurrection state
        self.soul_state = None  # None / "rising" / "panning" / "falling"
        self.soul_x = 0.0
        self.soul_y = 0.0
        self.soul_target_y = 0.0
        self.soul_timer = 0
        self.soul_trail = []
        self.fire_overlay_alpha = 0
        self.sun_blaze = 0  # 0-255 for sun blaze effect

        self.ending_shown = False
        self.credits_scroll = 0.0
        self.credits_max_scroll = 3000

        self.load_level()

    # ------------------------------------------------------------------
    def load_level(self):
        self.platforms, self.checkpoints, self.mushrooms, self.npcs, self.exit_portal = create_level()
        self.player = Player(100, 460)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles.clear()
        self.rings.clear()
        self.flashes.clear()
        self.damage_flashes.clear()
        self.score_popups.clear()
        self.arrows.clear()
        self.balloons.clear()
        self.santa = None
        self.santa_spawned = False
        self.gift = None
        self.dialogue_box = None
        self.tick = 0
        self.level_time = 0
        self.win_timer = 0
        self.freeze_frames = 0
        self.respawn_fade = 0
        self.soul_state = None
        self.soul_trail = []
        self.fire_overlay_alpha = 0
        self.sun_blaze = 0
        self.ending_shown = False

    def _exit_to_menu(self):
        self.sfx.stop_music()
        self.running = False
        pygame.event.clear()

    def _apply_volume(self):
        pygame.mixer.music.set_volume(0.0 if self.music_muted else self.music_volume)

    def start_dialogue(self, key, return_state="playing"):
        if key in STORY_DIALOGUES:
            self.dialogue_box = DialogueBox(STORY_DIALOGUES[key])
            self.pending_state = return_state
            self.state = "dialogue"

    # ------------------------------------------------------------------
    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._exit_to_menu()
                    return
                if event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_mouse_click(event.pos)
            if not self.running:
                return

            if self.freeze_frames > 0:
                self.freeze_frames -= 1
            elif self.state == "playing" and self.soul_state is not None:
                self._update_soul()
                self.tick += 1
                for c in self.clouds:
                    c.update()
            elif self.state == "playing":
                self._update()
            elif self.state == "win":
                self.win_timer += 1
                for c in self.clouds:
                    c.update()
            elif self.state in ("dialogue", "ending"):
                if self.dialogue_box:
                    self.dialogue_box.update()
                for c in self.clouds:
                    c.update()
                self.tick += 1
            elif self.state == "credits":
                if self.credits_scroll < self.credits_max_scroll:
                    self.credits_scroll += 0.6
                self.tick += 1
                for c in self.clouds:
                    c.update()

            if self.respawn_fade > 0:
                self.respawn_fade -= 1
            self._draw()
            self.clock.tick(FPS)

    # ------------------------------------------------------------------
    def _handle_mouse_click(self, pos):
        if self.state != "playing":
            return
        if not self.player.alive or self.soul_state is not None:
            return
        # Convert screen pos to world pos
        wx = pos[0] + int(self.camera.offset_x) - self.camera.shake_x
        wy = pos[1] + int(self.camera.offset_y) - self.camera.shake_y
        arrow = self.player.try_shoot_arrow(wx, wy)
        if arrow:
            self.arrows.append(arrow)
            self.sfx.play("shoot")
            # Ice muzzle flash particles
            for _ in range(6):
                self.particles.append(Particle(
                    self.player.rect.centerx, self.player.rect.centery - 4,
                    random.choice([ICE_BLUE, ICE_WHITE, ICE_CORE, WHITE]),
                    random.uniform(-2, 2), random.uniform(-2.5, 0.5), 12, random.randint(2, 4), 0.1))

    # ------------------------------------------------------------------
    def _handle_key(self, key):
        if self.state == "credits":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._exit_to_menu()
            return

        if self.state in ("dialogue", "ending"):
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                if self.dialogue_box:
                    self.dialogue_box.advance()
                    if not self.dialogue_box.active:
                        self.dialogue_box = None
                        if self.state == "ending":
                            self.state = "credits"
                            self.credits_scroll = 0.0
                        else:
                            self.state = self.pending_state or "playing"
            return

        if self.state == "settings":
            n_items = 5
            if key == pygame.K_ESCAPE:
                self.state = "playing"
            elif key in (pygame.K_UP, pygame.K_w):
                self.settings_cursor = (self.settings_cursor - 1) % n_items
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.settings_cursor = (self.settings_cursor + 1) % n_items
            elif key in (pygame.K_LEFT, pygame.K_a):
                if self.settings_cursor == 0:
                    self.music_volume = max(0.0, round(self.music_volume - 0.1, 1))
                    self._apply_volume()
            elif key in (pygame.K_RIGHT, pygame.K_d):
                if self.settings_cursor == 0:
                    self.music_volume = min(1.0, round(self.music_volume + 0.1, 1))
                    self._apply_volume()
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.settings_cursor == 1:
                    self.music_muted = not self.music_muted
                    self._apply_volume()
                elif self.settings_cursor == 2:
                    self.state = "playing"
                elif self.settings_cursor == 3:
                    self.load_level()
                    self.state = "playing"
                    self.sfx.start_music(volume=self.music_volume)
                elif self.settings_cursor == 4:
                    self._exit_to_menu()
            return

        if self.state == "win":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                if not self.ending_shown:
                    self.ending_shown = True
                    self.start_dialogue("ending", "ending_done")
                    self.state = "ending"
                    self.sfx.start_ending_music()
            return

        # Playing
        if key == pygame.K_ESCAPE:
            self.state = "settings"
            self.settings_cursor = 2
        elif key == pygame.K_r:
            self.player.hearts = 0
            self.player.die()
            self.sfx.play("death")
        elif key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            if self.player.alive and not self.player.on_ground and self.player.jump_count == 1:
                self.player.vel_y = JUMP_VELOCITY * 0.85
                self.player.jump_count = 2
                self.sfx.play("jump")
                for _ in range(4):
                    self.particles.append(Particle(
                        self.player.rect.centerx + random.randint(-6, 6),
                        self.player.rect.bottom,
                        random.choice([WHITE, SUN_YELLOW]),
                        random.uniform(-1, 1), random.uniform(-0.5, 0.5), 12, 2, 0.08))
        elif key == pygame.K_e:
            for npc in self.npcs:
                if npc.check_proximity(self.player) and not npc.talked:
                    npc.talked = True
                    self.start_dialogue(npc.dialogue_key)
                    break

    # ------------------------------------------------------------------
    def _update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()

        for plat in self.platforms:
            plat.update()

        result = self.player.update(keys, self.platforms)
        if result == "jump":
            self.sfx.play("jump")
            for _ in range(5):
                self.particles.append(Particle(
                    self.player.rect.centerx + random.randint(-8, 8),
                    self.player.rect.bottom,
                    random.choice([WHITE, SUN_YELLOW, HOLY_GOLD]),
                    random.uniform(-1.5, 1.5), random.uniform(-0.5, 0.5),
                    15, random.randint(2, 4), 0.08))

        if self.player.alive:
            self.camera.update(self.player.rect)

        # NPC proximity
        for npc in self.npcs:
            npc.proximity_shown = npc.check_proximity(self.player)

        # Checkpoints
        for cp in self.checkpoints:
            cp.update()
            if self.player.alive and cp.check(self.player):
                self.sfx.play("checkpoint")
                for _ in range(18):
                    a = random.uniform(0, math.pi * 2)
                    s = random.uniform(1, 4)
                    self.particles.append(Particle(
                        cp.rect.centerx, cp.rect.top,
                        random.choice([HOLY_GOLD, WHITE, SUN_YELLOW]),
                        math.cos(a) * s, math.sin(a) * s, 30, 3, 0.05))

        # Spawn Santa when player reaches trigger
        if (not self.santa_spawned and self.player.alive
                and self.player.rect.x >= self.santa_trigger_x):
            self.santa_spawned = True
            self.santa = SantaBoss(self.santa_spawn_x, -80)

        # Update Santa
        if self.santa and self.santa.alive:
            self.santa.update(
                self.player.rect.centerx, self.player.rect.centery,
                self.platforms, self.balloons)
            # Gift from Santa
            if self.santa.gift and not self.gift:
                self.gift = self.santa.gift

        # Arrow vs Santa
        for arrow in self.arrows:
            if not arrow.alive:
                continue
            if (self.santa and self.santa.alive and not self.santa.dead
                    and arrow.get_rect().colliderect(self.santa.rect)):
                arrow.alive = False
                killed = self.santa.hit()
                self._arrow_hit_fx(int(arrow.x), int(arrow.y), big=killed)
                if killed:
                    self.sfx.play("santa_die")
                    self.camera.add_shake(16)
                    self.flashes.append(FlashOverlay(FIRE_ORANGE, 20, 160))
                else:
                    self.sfx.play("arrow_hit")
                    self.camera.add_shake(4)

            # Arrow vs platforms
            if not arrow.alive:
                continue
            ar = arrow.get_rect()
            for plat in self.platforms:
                if plat.is_active() and ar.colliderect(plat.get_rect()):
                    arrow.alive = False
                    for _ in range(6):
                        self.particles.append(Particle(
                            arrow.x, arrow.y,
                            random.choice([ICE_BLUE, ICE_WHITE, ICE_CORE]),
                            random.uniform(-2.5, 2.5), random.uniform(-2, 0.5),
                            14, random.randint(2, 4), 0.08))
                    break

        self.arrows = [a for a in self.arrows if a.update()]

        # Balloon updates
        for bal in self.balloons:
            bal.update(self.platforms)
            if not bal.splashing and bal.alive:
                if bal.get_rect().colliderect(self.player.rect):
                    if self.player.take_damage():
                        bal.splashing = True
                        bal.splash_timer = 18
                        bal.splash_x = self.player.rect.centerx
                        bal.splash_y = self.player.rect.top
                        if self.player.alive:
                            self.camera.add_shake(7)
                            self.sfx.play("balloon_hit")
                            self.damage_flashes.append(DamageFlash())
                            # Knockback
                            dx = self.player.rect.centerx - (
                                self.santa.rect.centerx if self.santa else self.player.rect.centerx)
                            self.player.vel_x = 6 * (1 if dx >= 0 else -1)
                            self.player.vel_y = -5
                        else:
                            self._player_death_fx()
                            self.sfx.play("death")
        self.balloons = [b for b in self.balloons if b.alive or b.splashing]

        # Gift pickup
        if self.gift:
            self.gift.update(self.platforms)
            if self.gift.check(self.player):
                self.player.activate_gift_power()
                try:
                    present_snd = pygame.mixer.Sound(PRESENT_MUSIC)
                    present_snd.set_volume(0.8)
                    present_snd.play()
                except:
                    self.sfx.play("powerup")
                self._gift_fx(self.gift.x, self.gift.y)
                self.score_popups.append((self.gift.x, self.gift.y - 20, "POWER GIFT!", 90, HOLY_GOLD))
                self.gift = None

        # Mushroom collisions
        for mush in self.mushrooms:
            mush.update()
            coll = mush.check_collision(self.player)
            if coll == "stomp":
                self._stomp_fx(mush)
                mush.stomp()
                self.player.vel_y = -10
                self.player.kill_count += 1
                self.sfx.play("stomp")
                self.freeze_frames = 3
            elif coll == "kill_player":
                if self.player.take_damage():
                    if self.player.alive:
                        self.camera.add_shake(8)
                        self.sfx.play("death")
                        self.damage_flashes.append(DamageFlash())
                        dx = self.player.rect.centerx - mush.rect.centerx
                        self.player.vel_x = 7 * (1 if dx >= 0 else -1)
                        self.player.vel_y = -5
                    else:
                        self._player_death_fx()
                        self.sfx.play("death")

        self.mushrooms = [m for m in self.mushrooms
                          if m.alive or (hasattr(m, 'squish_timer') and m.squish_timer > 0) or m.death_timer > 0]

        # Exit portal
        self.exit_portal.update()
        if self.player.alive and self.exit_portal.check(self.player):
            self.state = "win"
            self.sfx.play("win")
            self.sfx.stop_music()

        # Particles
        self.particles = [p for p in self.particles if p.update()]
        self.rings = [r for r in self.rings if r.update()]
        self.flashes = [f for f in self.flashes if f.update()]
        self.damage_flashes = [d for d in self.damage_flashes if d.update()]
        self.score_popups = [(x, y - 0.8, t, ti - 1, c) for x, y, t, ti, c in self.score_popups if ti > 0]

        # Landing / footstep particles
        if self.player.alive:
            if self.player.on_ground and not self.player.was_on_ground:
                for _ in range(7):
                    self.particles.append(Particle(
                        self.player.rect.centerx + random.randint(-10, 10),
                        self.player.rect.bottom,
                        random.choice([GRASS_GREEN, WHITE, SUN_YELLOW]),
                        random.uniform(-2, 2), random.uniform(-1.5, 0), 16, 3, 0.1))
            if self.player.on_ground and abs(self.player.vel_x) > 1 and self.tick % 6 == 0:
                self.particles.append(Particle(
                    self.player.rect.centerx + random.randint(-4, 4),
                    self.player.rect.bottom,
                    GRASS_GREEN,
                    random.uniform(-0.5, 0.5), random.uniform(-1, -0.2), 12, 2, 0.06))

        # Gift power sparkle trail
        if self.player.alive and self.player.has_gift_power and self.tick % 3 == 0:
            self.particles.append(Particle(
                self.player.rect.centerx + random.randint(-8, 8),
                self.player.rect.centery + random.randint(-10, 10),
                random.choice([HOLY_GOLD, WHITE, SUN_YELLOW]),
                random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.3),
                20, 3, 0.04))

        # Clouds
        for c in self.clouds:
            c.update()

        # Santa warning indicator
        if self.santa and self.santa.alive and not self.santa.appeared:
            if self.tick % 30 == 0:
                self.score_popups.append((
                    self.player.rect.x + 200, self.player.rect.y - 60,
                    "⚠ SANTA INCOMING!", 60, FIRE_ORANGE))

        # Soul death intercept
        if not self.player.alive and self.soul_state is None:
            if self.player.respawn_timer <= 1:
                self.player.respawn_timer = 9999
                self.soul_x = float(self.player.rect.centerx)
                self.soul_y = float(self.player.rect.centery)
                self.soul_target_y = self.player.rect.centery - 160
                self.soul_timer = 0
                self.soul_trail = []
                self.soul_state = "rising"
                self.fire_overlay_alpha = 255
                self.sun_blaze = 0
                self.sfx.play("soul_rise")

        self.level_time += 1

    # ------------------------------------------------------------------
    #  Effects
    # ------------------------------------------------------------------
    def _player_death_fx(self):
        cx, cy = self.player.rect.centerx, self.player.rect.centery
        self.camera.add_shake(16)
        self.flashes.append(FlashOverlay(FIRE_ORANGE, 18, 140))
        for _ in range(14):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(3, 9)
            self.particles.append(Particle(
                cx + random.randint(-6, 6), cy + random.randint(-8, 8),
                random.choice([FIRE_ORANGE, FIRE_RED, FIRE_YELLOW]),
                math.cos(a) * s, math.sin(a) * s - 2,
                random.randint(35, 65), random.randint(4, 8), 0.3))

    def _stomp_fx(self, mush):
        cx, cy = mush.rect.centerx, mush.rect.bottom
        self.camera.add_shake(5)
        self.rings.append(RingEffect(cx, cy, WHITE, 45, 4, 2))
        for _ in range(10):
            a = random.uniform(-math.pi, 0)
            s = random.uniform(1, 4)
            self.particles.append(Particle(
                cx, cy, random.choice([GRASS_GREEN, WHITE, SUN_YELLOW]),
                math.cos(a) * s, math.sin(a) * s - 1, 20, 3, 0.12))
        self.score_popups.append((cx, cy - 25, "+50", 50, WHITE))

    def _arrow_hit_fx(self, x, y, big=False):
        count = 20 if big else 10
        for _ in range(count):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(2, 7 if big else 5)
            self.particles.append(Particle(
                x, y, random.choice([ICE_BLUE, ICE_WHITE, ICE_CORE, WHITE]),
                math.cos(a) * s, math.sin(a) * s,
                random.randint(20, 40), random.randint(2, 5 if big else 3), 0.05))
        self.rings.append(RingEffect(x, y, ICE_BLUE, 60 if big else 35, 4, 2))
        if big:
            self.rings.append(RingEffect(x, y, ICE_WHITE, 90, 5, 3))
            self.freeze_frames = 4
        lbl = "CRITICAL!" if big else "HIT!"
        self.score_popups.append((x, y - 22, lbl, 45, ICE_WHITE if big else ICE_BLUE))

    def _gift_fx(self, x, y):
        self.camera.add_shake(10)
        self.flashes.append(FlashOverlay(HOLY_GOLD, 18, 140))
        for i in range(3):
            self.rings.append(RingEffect(int(x), int(y), HOLY_GOLD, 60 + i * 30, 3 + i, 3))
        for _ in range(30):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(2, 6)
            self.particles.append(Particle(
                x, y, random.choice([HOLY_GOLD, WHITE, SUN_YELLOW, GIFT_RED]),
                math.cos(a) * s, math.sin(a) * s, 40, 4, 0.06))

    # ------------------------------------------------------------------
    #  Soul / resurrection animation
    # ------------------------------------------------------------------
    def _update_soul(self):
        self.soul_timer += 1

        # Fire overlay fades
        if self.fire_overlay_alpha > 0:
            self.fire_overlay_alpha = max(0, self.fire_overlay_alpha - 6)

        # Sun blaze rises then falls
        if self.soul_state in ("rising",):
            self.sun_blaze = min(255, self.sun_blaze + 8)
        else:
            self.sun_blaze = max(0, self.sun_blaze - 4)

        # Sparkle trail
        if self.soul_state != "panning":
            for _ in range(2):
                a = random.uniform(0, math.pi * 2)
                d = random.uniform(6, 18)
                self.particles.append(Particle(
                    self.soul_x + math.cos(a) * d,
                    self.soul_y + math.sin(a) * d,
                    random.choice([HOLY_GOLD, WHITE, SUN_YELLOW]),
                    random.uniform(-0.4, 0.4), random.uniform(-1.0, 0),
                    random.randint(10, 20), 2, 0.02, fade=True))

        if self.soul_state == "rising":
            t = min(1.0, self.soul_timer / 45)
            ease = t * t * (3 - 2 * t)
            self.soul_y = self.player.rect.centery - ease * 160
            self.soul_x = self.player.rect.centerx + math.sin(self.soul_timer * 0.14) * 14
            self.soul_trail.append((self.soul_x, self.soul_y, 255))
            if len(self.soul_trail) > 20:
                self.soul_trail.pop(0)
            self.soul_trail = [(x, y, a - 10) for x, y, a in self.soul_trail if a > 10]
            if self.soul_timer >= 45:
                self.soul_state = "panning"
                self.soul_timer = 0
                self.soul_trail = []
                self.soul_pan_target_x = (self.player.spawn_x + Player.WIDTH // 2
                                          - self.camera.width // 3)
                self.soul_pan_target_y = (self.player.spawn_y + Player.HEIGHT // 2
                                          - self.camera.height // 2)

        elif self.soul_state == "panning":
            dx = self.soul_pan_target_x - self.camera.offset_x
            dy = self.soul_pan_target_y - self.camera.offset_y
            self.camera.offset_x += dx * 0.12
            self.camera.offset_y += dy * 0.08
            close_enough = abs(dx) < 8 and abs(dy) < 8
            if self.soul_timer >= 20 and close_enough:
                self.soul_state = "falling"
                self.soul_timer = 0
                self.soul_x = float(self.player.spawn_x + Player.WIDTH // 2)
                self.soul_y = self.camera.offset_y - 60
                self.soul_target_y = float(self.player.spawn_y + Player.HEIGHT // 2)
                self.soul_trail = []
                self.sfx.play("soul_land")

        elif self.soul_state == "falling":
            t = min(1.0, self.soul_timer / 38)
            ease = t * t * (3 - 2 * t)
            self.soul_y = -50 + (self.soul_target_y + 50) * ease
            self.soul_x = (self.player.spawn_x + Player.WIDTH // 2
                           + math.sin(t * math.pi) * 28)
            self.soul_trail.append((self.soul_x, self.soul_y, 255))
            if len(self.soul_trail) > 20:
                self.soul_trail.pop(0)
            self.soul_trail = [(x, y, a - 10) for x, y, a in self.soul_trail if a > 10]
            if self.soul_timer >= 38:
                self.player.respawn_timer = 0
                self.player.respawn()
                self.sfx.play("respawn")
                self.respawn_fade = 20
                self.flashes.append(FlashOverlay(WHITE, 12, 200))
                for _ in range(22):
                    a = random.uniform(0, math.pi * 2)
                    s = random.uniform(2, 7)
                    self.particles.append(Particle(
                        self.soul_x, self.soul_target_y,
                        random.choice([WHITE, HOLY_GOLD, SUN_YELLOW, ANGEL_BLUE]),
                        math.cos(a) * s, math.sin(a) * s, 30, 4, 0.1))
                self.rings.append(RingEffect(
                    int(self.soul_x), int(self.soul_target_y), HOLY_GOLD, 110, 6, 3))
                self.soul_state = None
                self.soul_trail = []
                self.camera.update(self.player.rect)

        self.particles = [p for p in self.particles if p.update()]
        self.rings = [r for r in self.rings if r.update()]
        self.flashes = [f for f in self.flashes if f.update()]

    def _draw_soul(self):
        if self.soul_state is None:
            return
        # Fire overlay
        if self.fire_overlay_alpha > 0:
            fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for row in range(SCREEN_HEIGHT):
                t = row / SCREEN_HEIGHT
                c = lerp_color(FIRE_YELLOW, FIRE_RED, t)
                a = int(self.fire_overlay_alpha * (0.4 + 0.6 * (1 - t)))
                fs.fill((*c, a), (0, row, SCREEN_WIDTH, 1))
            self.screen.blit(fs, (0, 0))

        # Sun blaze
        if self.sun_blaze > 0:
            ss = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ss.fill((255, 230, 100, int(self.sun_blaze * 0.25)))
            self.screen.blit(ss, (0, 0))

        # Dark dimming overlay
        if self.soul_state == "panning":
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 90))
            self.screen.blit(dim, (0, 0))
            return

        # Soul trail
        for i, (sx, sy, sa) in enumerate(self.soul_trail):
            tp = self.camera.apply(pygame.Rect(int(sx), int(sy), 1, 1))
            frac = (i + 1) / max(1, len(self.soul_trail))
            r = max(2, int(10 * frac))
            al = max(0, min(255, int(sa * 0.4 * frac)))
            ts = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (255, 240, 160, al), (r, r), r)
            self.screen.blit(ts, (tp.x - r, tp.y - r))

        # Soul orb
        sp = self.camera.apply(pygame.Rect(int(self.soul_x), int(self.soul_y), 1, 1))
        for gr, ga in [(42, 35), (28, 70), (16, 160)]:
            gs = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (255, 230, 140, ga), (gr, gr), gr)
            self.screen.blit(gs, (sp.x - gr, sp.y - gr))
        pygame.draw.circle(self.screen, SUN_YELLOW, (sp.x, sp.y), 9)
        pygame.draw.circle(self.screen, WHITE, (sp.x - 1, sp.y - 1), 4)

    # ------------------------------------------------------------------
    #  Drawing
    # ------------------------------------------------------------------
    def _draw(self):
        self.screen.fill(SKY_TOP)
        if self.state == "playing":
            self._draw_game()
        elif self.state == "settings":
            self._draw_game()
            self._draw_settings()
        elif self.state == "win":
            self._draw_win()
        elif self.state in ("dialogue", "ending"):
            self._draw_game()
            if self.dialogue_box:
                self.dialogue_box.draw(self.screen, self.tick)
        elif self.state == "credits":
            self._draw_credits()

        if self.respawn_fade > 0:
            alpha = int(255 * (1.0 - abs(self.respawn_fade - 10) / 10.0))
            if alpha > 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill(BLACK)
                overlay.set_alpha(min(255, alpha))
                self.screen.blit(overlay, (0, 0))

        pygame.display.flip()

    def _draw_background(self):
        # Sky gradient
        for y in range(0, SCREEN_HEIGHT, 2):
            t = y / SCREEN_HEIGHT
            c = lerp_color(SKY_TOP, SKY_BOT, t)
            self.screen.fill(c, (0, y, SCREEN_WIDTH, 2))

        # Sun
        mx, my = SCREEN_WIDTH - 130, 90
        # Outer glow rings
        for r2, a2 in [(80, 18), (60, 35), (45, 60), (32, 100)]:
            gs = pygame.Surface((r2 * 2, r2 * 2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*SUN_GOLD, a2), (r2, r2), r2)
            self.screen.blit(gs, (mx - r2, my - r2))
        pygame.draw.circle(self.screen, SUN_GOLD, (mx, my), 30)
        pygame.draw.circle(self.screen, SUN_YELLOW, (mx, my), 24)
        pygame.draw.circle(self.screen, WHITE, (mx, my), 14)
        # Rays
        for i in range(12):
            a = math.radians(self.tick * 0.4 + i * 30)
            x1 = mx + int(math.cos(a) * 34)
            y1 = my + int(math.sin(a) * 34)
            x2 = mx + int(math.cos(a) * (46 + int(math.sin(self.tick * 0.05 + i) * 5)))
            y2 = my + int(math.sin(a) * (46 + int(math.sin(self.tick * 0.05 + i) * 5)))
            pygame.draw.line(self.screen, SUN_GOLD, (x1, y1), (x2, y2), 2)

        # Clouds (parallax with camera)
        for cloud in self.clouds:
            cloud.draw(self.screen)

        # Distant mountain silhouettes (parallax 0.1x)
        ox = int(self.camera.offset_x * 0.1)
        base_y = SCREEN_HEIGHT - 40
        for mx2 in range(-100 - ox % 350, SCREEN_WIDTH + 400, 350):
            rng = random.Random(mx2 + 9999)
            mh = rng.randint(100, 200)
            mw = rng.randint(120, 220)
            mc = (130, 180, 210)
            pts = [(mx2 - mw // 2, base_y), (mx2, base_y - mh), (mx2 + mw // 2, base_y)]
            pygame.draw.polygon(self.screen, mc, pts)
            # Snow cap
            pygame.draw.polygon(self.screen, (220, 235, 250),
                                [(mx2 - mw // 8, base_y - mh + mh // 4),
                                 (mx2, base_y - mh),
                                 (mx2 + mw // 8, base_y - mh + mh // 4)])

        # Horizon haze
        hz = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        for y in range(60):
            a = int(80 * (1 - y / 60))
            hz.fill((200, 230, 255, a), (0, y, SCREEN_WIDTH, 1))
        self.screen.blit(hz, (0, SCREEN_HEIGHT - 60))

    def _draw_game(self):
        self._draw_background()

        # Platforms
        for plat in self.platforms:
            plat.draw(self.screen, self.camera)

        # Checkpoints
        for cp in self.checkpoints:
            cp.draw(self.screen, self.camera)

        # Exit portal
        self.exit_portal.draw(self.screen, self.camera, self.tick)

        # NPCs
        for npc in self.npcs:
            npc.draw(self.screen, self.camera, self.tick)

        # Mushrooms
        for mush in self.mushrooms:
            mush.draw(self.screen, self.camera, self.tick)

        # Santa
        if self.santa:
            self.santa.draw(self.screen, self.camera, self.tick)

        # Water balloons
        for bal in self.balloons:
            bal.draw(self.screen, self.camera, self.tick)

        # Gift
        if self.gift:
            self.gift.draw(self.screen, self.camera, self.tick)

        # Arrows
        for arrow in self.arrows:
            arrow.draw(self.screen, self.camera, self.tick)

        # Particles & effects
        for p in self.particles:
            p.draw(self.screen, self.camera)
        for r in self.rings:
            r.draw(self.screen, self.camera)
        for f in self.flashes:
            f.draw(self.screen)
        for d in self.damage_flashes:
            d.draw(self.screen)

        # Player
        self.player.draw(self.screen, self.camera, self.tick)

        # Score popups
        for x, y, text, timer, color in self.score_popups:
            a = min(1.0, timer / 30)
            c = tuple(max(0, min(255, int(v * a))) for v in color)
            pos = self.camera.apply(pygame.Rect(int(x), int(y), 1, 1))
            surf = self.small_font.render(text, True, c)
            self.screen.blit(surf, surf.get_rect(center=(pos.x, pos.y)))

        # ── HUD ──
        hud_x, hud_y = 12, 10

        def _hud_text(font, text, color, x, y):
            self.screen.blit(font.render(text, True, BLACK), (x + 1, y + 1))
            self.screen.blit(font.render(text, True, color), (x, y))

        # Hearts
        for i in range(PLAYER_MAX_HEARTS):
            hx = hud_x + i * 26
            c = XMAS_RED if i < self.player.hearts else (50, 50, 50)
            hscale = 0
            if i == 0 and self.player.hearts == 1 and self.player.alive:
                hscale = int(abs(math.sin(self.tick * 0.12)) * 2)
            for dx2, dy2, sc in [(1, 1, BLACK), (0, 0, c)]:
                pygame.draw.circle(self.screen, sc, (hx + 5 + dx2, hud_y + dy2), 5 + hscale)
                pygame.draw.circle(self.screen, sc, (hx + 13 + dx2, hud_y + dy2), 5 + hscale)
                pygame.draw.polygon(self.screen, sc,
                                    [(hx - hscale + dx2, hud_y + 2 + dy2),
                                     (hx + 9 + dx2, hud_y + 11 + hscale + dy2),
                                     (hx + 18 + hscale + dx2, hud_y + 2 + dy2)])
            if i >= self.player.hearts:
                pygame.draw.circle(self.screen, (30, 30, 30), (hx + 5, hud_y), 5, 1)
                pygame.draw.circle(self.screen, (30, 30, 30), (hx + 13, hud_y), 5, 1)

        # Kill count
        if self.player.kill_count > 0:
            _hud_text(self.tiny_font, f"Stomped: {self.player.kill_count}", HOLY_GOLD, hud_x, hud_y + 20)

        # Gift power bar
        if self.player.has_gift_power:
            rem = self.player.gift_power_timer / FPS
            bw, bh = 120, 12
            bx2, by2 = hud_x, hud_y + 36
            ratio = self.player.gift_power_timer / 600
            pygame.draw.rect(self.screen, (40, 40, 40), (bx2 - 2, by2 - 2, bw + 4, bh + 4))
            for px_i in range(int(bw * ratio)):
                t = px_i / bw
                bc = lerp_color(GIFT_RED, HOLY_GOLD, t)
                self.screen.fill(bc, (bx2 + px_i, by2, 1, bh))
            _hud_text(self.tiny_font, f"POWER  {rem:.0f}s", HOLY_GOLD, bx2 + 4, by2)

        # Santa HP (top center, shown only when santa is alive)
        if self.santa and self.santa.alive and not self.santa.dead:
            pass  # Already drawn on Santa sprite

        # Time / right side
        t2 = self.level_time / FPS
        _hud_text(self.tiny_font, f"Time: {t2:.1f}s", HOLY_WHITE, SCREEN_WIDTH - 120, 10)
        _hud_text(self.tiny_font, "Level 3", ANGEL_BLUE, SCREEN_WIDTH - 120, 24)

        # Bottom help
        self.screen.blit(
            self.tiny_font.render(
                "LEFT CLICK to shoot arrow  |  SPACE=Jump  |  SHIFT=Sprint  |  E=Talk  |  ESC=Settings  |  R=Respawn",
                True, (60, 70, 90)),
            (10, SCREEN_HEIGHT - 16))

        # Low health border
        if self.player.hearts == 1 and self.player.alive:
            pulse = abs(math.sin(self.tick * 0.08)) * 0.5
            lh_s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for bi in range(5):
                ia = max(0, int(35 * pulse) - bi * 6)
                if ia > 0:
                    pygame.draw.rect(lh_s, (220, 50, 50, ia),
                                     (bi, bi, SCREEN_WIDTH - 2 * bi, SCREEN_HEIGHT - 2 * bi), 1)
            self.screen.blit(lh_s, (0, 0))

        if not self.player.alive and self.soul_state is None:
            txt = self.font.render("Respawning...", True, FIRE_ORANGE)
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        if self.soul_state is not None:
            self._draw_soul()

    def _draw_settings(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            t = y / SCREEN_HEIGHT
            c = lerp_color((20, 60, 120), (60, 120, 180), t)
            overlay.fill((*c, 220), (0, y, SCREEN_WIDTH, 4))
        self.screen.blit(overlay, (0, 0))

        # Border
        bw = 7
        for x in range(0, SCREEN_WIDTH, 20):
            shift = (self.tick // 4) % 20
            c = HOLY_GOLD if ((x + shift) // 10) % 2 == 0 else ANGEL_BLUE
            pygame.draw.rect(self.screen, c, (x, 0, 10, bw))
            pygame.draw.rect(self.screen, c, (x, SCREEN_HEIGHT - bw, 10, bw))

        title = pygame.font.SysFont("consolas", 36, bold=True).render("SETTINGS", True, HOLY_GOLD)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 70)))

        items = [
            f"Music Volume:  < {int(self.music_volume * 100)}% >",
            f"Mute Music:    {'ON' if self.music_muted else 'OFF'}",
            "Resume Game",
            "Restart Level",
            "Exit to Main Menu",
        ]
        for i, item in enumerate(items):
            y = 130 + i * 52
            sel = (i == self.settings_cursor)
            bar = pygame.Rect(SCREEN_WIDTH // 2 - 220, y - 2, 440, 38)
            if sel:
                pygame.draw.rect(self.screen, (20, 50, 100), bar, border_radius=6)
                pygame.draw.rect(self.screen, HOLY_GOLD, bar, 2, border_radius=6)
                color = HOLY_GOLD
            else:
                pygame.draw.rect(self.screen, (30, 60, 110), bar, border_radius=6)
                color = HOLY_WHITE
            txt = self.small_font.render(item, True, color)
            self.screen.blit(txt, (SCREEN_WIDTH // 2 - 160, y + 6))

        esc = self.small_font.render("ESC to resume", True, (160, 180, 220))
        self.screen.blit(esc, esc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

    def _draw_win(self):
        self._draw_background()
        for c in self.clouds:
            c.update()
            c.draw(self.screen)

        if self.win_timer % 8 == 0:
            for _ in range(4):
                self.particles.append(Particle(
                    random.randint(200, SCREEN_WIDTH - 200),
                    random.randint(50, 200),
                    random.choice([HOLY_GOLD, SUN_YELLOW, WHITE, ANGEL_BLUE]),
                    random.uniform(-2, 2), random.uniform(1, 3), 60, 4, 0.05))
        for p in self.particles:
            p.draw(self.screen, self.camera)
        self.particles = [p for p in self.particles if p.update()]

        txt = self.big_font.render("SKY TRIAL COMPLETE!", True, SUN_YELLOW)
        self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, 110)))
        txt2 = self.font.render("THE THIRD REALM — CONQUERED", True, HOLY_GOLD)
        self.screen.blit(txt2, txt2.get_rect(center=(SCREEN_WIDTH // 2, 170)))

        t2 = self.level_time / FPS
        stats = [
            (f"Time: {t2:.1f}s", HOLY_WHITE),
            (f"Deaths: {self.player.death_count}", FIRE_ORANGE),
            (f"Mushrooms stomped: {self.player.kill_count}", GRASS_GREEN),
            (f"Santa defeated: {'Yes' if self.santa_spawned else 'No'}", SANTA_RED),
        ]
        for i, (s, sc) in enumerate(stats):
            surf = self.font.render(s, True, sc)
            self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, 240 + i * 46)))

        if t2 < 120:
            rank, rc = "S", HOLY_GOLD
        elif t2 < 200:
            rank, rc = "A", GRASS_GREEN
        elif t2 < 320:
            rank, rc = "B", ANGEL_BLUE
        else:
            rank, rc = "C", GRAY
        rs = self.big_font.render(f"Rank: {rank}", True, rc)
        self.screen.blit(rs, rs.get_rect(center=(SCREEN_WIDTH // 2, 460)))

        pulse = abs(math.sin(self.tick * 0.05)) * 0.5 + 0.5
        hint = self.small_font.render("Press ENTER to continue to the ending...", True, HOLY_WHITE)
        hint.set_alpha(int(128 + 127 * pulse))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 530)))
        self.tick += 1

    def _draw_credits(self):
        # Simple scrolling credits
        scroll = self.credits_scroll
        cx = SCREEN_WIDTH // 2

        # Sky background
        for y in range(0, SCREEN_HEIGHT, 2):
            t = y / SCREEN_HEIGHT
            c = lerp_color((60, 130, 220), (180, 230, 255), t)
            self.screen.fill(c, (0, y, SCREEN_WIDTH, 2))
        for cloud in self.clouds:
            cloud.draw(self.screen)

        fonts = {
            "big": pygame.font.SysFont("consolas", 48, bold=True),
            "head": pygame.font.SysFont("consolas", 30, bold=True),
            "body": pygame.font.SysFont("consolas", 20),
            "small": pygame.font.SysFont("consolas", 14),
        }

        DARK_BLUE = (20, 40, 100)
        MID_BLUE = (40, 70, 140)

        credits_lines = [
            ("", "body", DARK_BLUE, 60),
            ("THE ENDLESS DREAM", "big", DARK_BLUE, 10),
            ("The Sky Trial", "body", MID_BLUE, 40),
            ("", "body", DARK_BLUE, 30),
            ("The Team", "head", DARK_BLUE, 12),
            ("Muqeet", "body", HOLY_GOLD, 4),
            ("Omar", "body", HOLY_GOLD, 4),
            ("John", "body", HOLY_GOLD, 4),
            ("Danial", "body", HOLY_GOLD, 30),
            ("Level Design & Programming", "head", DARK_BLUE, 8),
            ("Muqeet  /  Omar  /  John  /  Danial", "body", MID_BLUE, 30),
            ("Art & Visuals", "head", DARK_BLUE, 8),
            ("Muqeet  /  Omar  /  John  /  Danial", "body", MID_BLUE, 30),
            ("Story & Dialogue", "head", DARK_BLUE, 8),
            ("Muqeet  /  Omar  /  John  /  Danial", "body", MID_BLUE, 30),
            ("", "body", DARK_BLUE, 30),
            ("Special Thanks", "head", DARK_BLUE, 12),
            ("Mary Ting — Course Professor", "body", MID_BLUE, 8),
            ("Our classmates, families, and testers", "body", MID_BLUE, 40),
            ("", "body", DARK_BLUE, 40),
            ("Thank You for Playing", "head", DARK_BLUE, 12),
            ("The sky is always waiting.", "body", MID_BLUE, 100),
            ("THE ENDLESS DREAM", "big", DARK_BLUE, 8),
            ("Imaging Assignment  —  2026", "small", MID_BLUE, 80),
        ]

        total_h = SCREEN_HEIGHT + 50
        for _, fk, _, gap in credits_lines:
            f = fonts[fk]
            total_h += f.get_height() + gap
        self.credits_max_scroll = total_h - SCREEN_HEIGHT // 2 - 60

        y = SCREEN_HEIGHT + 50 - scroll
        for text, fk, color, gap in credits_lines:
            f = fonts[fk]
            fh = f.get_height() if text else 0
            if text and -fh < y < SCREEN_HEIGHT + fh:
                alpha = 1.0
                if y < 80:
                    alpha = max(0, y / 80)
                if y > SCREEN_HEIGHT - 80:
                    alpha = max(0, (SCREEN_HEIGHT - y) / 80)
                c2 = tuple(max(0, min(255, int(v * alpha))) for v in color)
                surf = f.render(text, True, c2)
                self.screen.blit(surf, surf.get_rect(center=(cx, int(y))))
            y += fh + gap

        is_stopped = self.credits_scroll >= self.credits_max_scroll
        hint_text = "Press ENTER or ESC to return to menu" if is_stopped else "Press ENTER or ESC to skip"
        hint = fonts["small"].render(hint_text, True, MID_BLUE)
        self.screen.blit(hint, hint.get_rect(center=(cx, SCREEN_HEIGHT - 28)))


# ---------------------------------------------------------------------------
# Entry point (mirrors Level 4 pattern)
# ---------------------------------------------------------------------------
def launch_game():
    # Stop whatever main.py was playing
    pygame.mixer.music.stop()
    pygame.event.clear()
    # Re-init mixer to clear any state issues
    pygame.mixer.quit()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    # Create game and start music before entering the loop
    game = Game()
    game.sfx.start_music(volume=game.music_volume)
    game.run()
    pygame.event.clear()
    pygame.display.set_caption("The Endless Dream")
    # Restore main menu music
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.music.load(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "audio", "BackgroundMusic.mp3"))
        pygame.mixer.music.play(-1)
    except:
        pass


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    game = Game()
    game.run()
    pygame.quit()