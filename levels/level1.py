import pygame
import sys
import math
import random
import os

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS = 60

WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
SKY_TOP      = (74,  144, 200)
SKY_MID      = (114, 174, 221)
SKY_BOT      = (190, 224, 245)
CLOUD_WHITE  = (208, 234, 255)
CLOUD_SHADOW = (128, 184, 224)
SUN_YELLOW   = (255, 215,  64)
SUN_ORANGE   = (255, 153,   0)
PLAT_CLOUD   = (208, 234, 255)
PLAT_MOVE    = (136, 221, 136)
PLAT_GLITCH  = (200, 168, 255)
PLAT_FALL    = (255, 152, 152)
PLAT_TELE    = (255, 184,  96)
PLAT_ICE     = (180, 230, 255)
PLAT_BOUNCE  = (120, 255, 140)
PLAT_SPIKE   = (210, 210, 215)
SPIKE_COLOR  = (200,  50,  50)
WIND_COLOR   = (160, 210, 255)
GRAY         = (160, 170, 185)
DARK_GRAY    = ( 70,  80,  95)
RED          = (220,  60,  60)
GREEN        = ( 60, 200,  90)
YELLOW       = (255, 220,  50)
ORANGE       = (255, 160,  30)
CYAN         = ( 80, 220, 255)
GOLD         = (255, 200,  50)
DARK_BG      = (155, 205, 250)
GRID_COLOR   = (140, 190, 235)

# Physics
GRAVITY         = 0.6
JUMP_VELOCITY   = -15
MOVE_SPEED      = 5
SPRINT_SPEED    = 8
MAX_FALL_SPEED  = 15
BOUNCE_VELOCITY = -22   # spring launcher

# Death Y
DEATH_Y = 980

# Unreal Mode
UNREAL_DURATION    = 480
UNREAL_SPEED_BOOST = 2

RAINBOW = [
    (255, 60, 60), (255, 160, 40), (255, 240, 50),
    (80, 255, 80), (50, 200, 255), (120, 80, 255), (220, 50, 220),
]


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rainbow_color(tick, speed=0.05):
    idx = (tick * speed) % len(RAINBOW)
    i = int(idx)
    return lerp_color(RAINBOW[i], RAINBOW[(i + 1) % len(RAINBOW)], idx - i)


# ---------------------------------------------------------------------------
# Sound Manager
# ---------------------------------------------------------------------------
SOUND_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
MUSIC_FILE = "assets/audio/Level1Music.mp3"

SOUND_FILES = {
    "jump":       "jump.wav",
    "death":      "death.wav",
    "respawn":    "respawn.wav",
    "powerup":    "powerup.wav",
    "unreal_end": "unreal_end.wav",
    "checkpoint": "checkpoint.wav",
    "win":        "win.wav",
    "bounce":     "jump.wav",
}


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_loaded = False
        for name, fn in SOUND_FILES.items():
            path = os.path.join(SOUND_DIR, fn)
            try:
                self.sounds[name] = pygame.mixer.Sound(path) if os.path.isfile(path) else None
            except Exception:
                self.sounds[name] = None
        if os.path.isfile(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                self.music_loaded = True
            except Exception:
                pass

    def play(self, name):
        s = self.sounds.get(name)
        if s: s.play()

    def start_music(self, loops=-1, volume=0.5):
        if self.music_loaded:
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
class Camera:
    def __init__(self, width, height):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.width  = width
        self.height = height
        self.shake_amount = 0.0
        self.shake_x = self.shake_y = 0

    def update(self, target_rect):
        tx = target_rect.centerx - self.width // 3
        self.offset_x += (tx - self.offset_x) * 0.1
        ty = target_rect.centery - self.height // 2
        self.offset_y += (ty - self.offset_y) * 0.08
        if self.shake_amount > 0.5:
            self.shake_x = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_y = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_amount *= 0.85
        else:
            self.shake_amount = 0
            self.shake_x = self.shake_y = 0

    def add_shake(self, amount):
        self.shake_amount = min(self.shake_amount + amount, 20)

    def apply(self, rect):
        return pygame.Rect(
            rect.x - int(self.offset_x) + self.shake_x,
            rect.y - int(self.offset_y) + self.shake_y,
            rect.width, rect.height,
        )


# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color, vel_x=0, vel_y=0, lifetime=30, size=4, gravity=0.1, fade=True):
        self.x, self.y = float(x), float(y)
        self.color = color
        self.vel_x, self.vel_y = vel_x, vel_y
        self.lifetime = self.max_lifetime = lifetime
        self.base_size = size
        self.gravity = gravity
        self.fade = fade

    def update(self):
        self.x += self.vel_x; self.y += self.vel_y
        self.vel_y += self.gravity; self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface, camera):
        a = self.lifetime / self.max_lifetime if self.fade else 1.0
        size = max(1, int(self.base_size * a))
        color = tuple(max(0, min(255, int(c * a))) for c in self.color)
        pos = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        pygame.draw.rect(surface, color, (pos.x, pos.y, size, size))


# ---------------------------------------------------------------------------
# Ring Effect
# ---------------------------------------------------------------------------
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
        a = 1.0 - self.radius / self.max_radius
        color = tuple(max(0, min(255, int(c * a))) for c in self.color)
        w = max(1, int(self.width * a))
        pos = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        if -50 < pos.x < SCREEN_WIDTH + 50 and -50 < pos.y < SCREEN_HEIGHT + 50:
            pygame.draw.circle(surface, color, (pos.x, pos.y), int(self.radius), w)


# ---------------------------------------------------------------------------
# Flash Overlay
# ---------------------------------------------------------------------------
class FlashOverlay:
    def __init__(self, color, duration=15, max_alpha=180):
        self.color = color
        self.duration = duration
        self.timer = duration
        self.max_alpha = max_alpha
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.fill(color)

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def draw(self, surface):
        self.surface.set_alpha(int(self.max_alpha * self.timer / self.duration))
        surface.blit(self.surface, (0, 0))


# ---------------------------------------------------------------------------
# NEW OBSTACLE: Wind Zone
# Invisible horizontal push zone. Draws as animated streaks with arrows.
# ---------------------------------------------------------------------------
class WindZone:
    def __init__(self, x, y, w, h, force=2.5, direction=1):
        self.rect      = pygame.Rect(x, y, w, h)
        self.force     = force
        self.direction = direction   # +1 right, -1 left
        self.tick      = 0
        rng = random.Random(x ^ (y + 1))
        self.streaks = [(rng.randint(0, w), rng.randint(0, h),
                         rng.randint(40, 90)) for _ in range(20)]

    def update(self):
        self.tick += 1

    def apply_to_player(self, player):
        if player.alive and player.rect.colliderect(self.rect):
            player.vel_x += self.force * self.direction * 0.35
            player.vel_x = max(-12, min(12, player.vel_x))

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20: return
        if sr.bottom < -20 or sr.top  > SCREEN_HEIGHT + 20: return

        # Translucent tinted fill
        overlay = pygame.Surface((max(1, sr.width), max(1, sr.height)), pygame.SRCALPHA)
        alpha = int(30 + 14 * abs(math.sin(self.tick * 0.04)))
        col = (100, 180, 255, alpha) if self.direction > 0 else (255, 170, 80, alpha)
        overlay.fill(col)
        surface.blit(overlay, (sr.x, sr.y))

        # Animated streaks
        speed_off = self.tick * 3 * self.direction
        for ox, oy, length in self.streaks:
            sx = sr.x + (ox + speed_off) % max(1, sr.width)
            sy = sr.y + oy % max(1, sr.height)
            ex = sx + length * self.direction
            sx = max(sr.x, min(sr.right, sx))
            ex = max(sr.x, min(sr.right, ex))
            a2 = int(70 + 50 * abs(math.sin(self.tick * 0.06 + ox)))
            c3 = (160, 210, 255) if self.direction > 0 else (255, 200, 130)
            if abs(ex - sx) > 2:
                pygame.draw.line(surface, c3, (int(sx), int(sy)), (int(ex), int(sy)), 1)

        # Arrow indicators every 80 px across the zone
        arrow_step = 80
        start_x = sr.x + 30
        for ax in range(start_x, sr.right - 20, arrow_step):
            ay = sr.centery
            tip = (ax + 14 * self.direction, ay)
            base_l = (ax, ay - 7)
            base_r = (ax, ay + 7)
            pygame.draw.polygon(surface, WIND_COLOR, [base_l, tip, base_r])

        # Label
        font = pygame.font.SysFont("consolas", 11, bold=True)
        lbl = font.render(">> WIND >>" if self.direction > 0 else "<< WIND <<", True, (70, 130, 190))
        surface.blit(lbl, (sr.x + 6, sr.y + 4))


# ---------------------------------------------------------------------------
# NEW OBSTACLE: Ice Platform
# Very low friction — player slides and accelerates slowly.
# ---------------------------------------------------------------------------
class IcePlatform:
    ICE_FRICTION = 0.96   # slightly more forgiving — still slippery but not hopeless
    ICE_ACCEL    = 0.14

    def __init__(self, x, y, w, h=26):
        self.rect  = pygame.Rect(x, y, w, h)
        self.color = PLAT_ICE
        self.tick  = 0

    def is_active(self):         return True
    def get_rect(self):          return self.rect
    def on_player_land(self, p): pass
    def update(self):            self.tick += 1

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pygame.draw.rect(surface, self.color, sr, border_radius=10)
        # Glossy highlight
        hi = tuple(min(c + 65, 255) for c in self.color)
        pygame.draw.rect(surface, hi, (sr.x + 4, sr.y, sr.width - 8, 5), border_radius=4)
        # Sparkle dots
        for i in range(5):
            phase = (self.tick * 0.09 + i * 1.3) % (2 * math.pi)
            bri   = int(150 + 105 * abs(math.sin(phase)))
            sp_x  = sr.x + 10 + i * max(1, (sr.width - 20) // 4)
            pygame.draw.circle(surface, (bri, bri, 255), (sp_x, sr.y + 8), 2)
        # Label
        font = pygame.font.SysFont("consolas", 10, bold=True)
        lbl  = font.render("ICE", True, (80, 160, 215))
        surface.blit(lbl, (sr.centerx - lbl.get_width() // 2, sr.y + 9))


# ---------------------------------------------------------------------------
# NEW OBSTACLE: Bouncy Pad
# Small spring that launches the player much higher than a normal jump.
# ---------------------------------------------------------------------------
class BouncyPad:
    PAD_W, PAD_H = 60, 18

    def __init__(self, x, y):
        self.rect   = pygame.Rect(x, y, self.PAD_W, self.PAD_H)
        self.tick   = 0
        self.squish = 0

    def is_active(self):  return True
    def get_rect(self):   return self.rect

    def on_player_land(self, player):
        player.vel_y     = BOUNCE_VELOCITY
        player.on_ground = False
        self.squish      = 10

    def update(self):
        self.tick += 1
        if self.squish > 0: self.squish -= 1

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return

        # Squish animation
        sh = max(4, int(sr.height * (1.0 - 0.45 * self.squish / 10)))
        sy = sr.bottom - sh
        body = pygame.Rect(sr.x, sy, sr.width, sh)

        coil_col = lerp_color(PLAT_BOUNCE, (200, 255, 200),
                              abs(math.sin(self.tick * 0.12)) * 0.4)
        pygame.draw.rect(surface, coil_col, body, border_radius=8)

        # Coil lines
        for i in range(3):
            cy2 = body.y + 3 + i * max(1, sh // 3)
            pygame.draw.line(surface, (50, 170, 70),
                             (sr.x + 6, cy2), (sr.right - 6, cy2), 2)

        # Bouncing arrow above pad
        pulse = abs(math.sin(self.tick * 0.14))
        ay = sr.y - int(7 + 7 * pulse)
        arrow_col = lerp_color((80, 220, 100), WHITE, pulse)
        pygame.draw.polygon(surface, arrow_col,
            [(sr.centerx, ay - 9), (sr.centerx - 8, ay + 3), (sr.centerx + 8, ay + 3)])

        # Label
        font = pygame.font.SysFont("consolas", 10, bold=True)
        lbl  = font.render("SPRING", True, (30, 130, 50))
        surface.blit(lbl, (sr.centerx - lbl.get_width() // 2, body.y + 1))


# ---------------------------------------------------------------------------
# NEW OBSTACLE: Spike Trap
# Platform with spikes that extend/retract on a timer.
# Touching the spikes while they're out = death.
# ---------------------------------------------------------------------------
class SpikeTrap:
    SPIKE_H = 14

    def __init__(self, x, y, w, h=26, up_time=70, down_time=50, offset=0, spike_count=None):
        self.rect        = pygame.Rect(x, y, w, h)
        self.up_time     = up_time
        self.down_time   = down_time
        self.timer       = offset
        self.spikes_up   = False
        self.spike_count = spike_count or max(2, w // 20)
        self.color       = PLAT_SPIKE

    def is_active(self):         return True
    def get_rect(self):          return self.rect
    def on_player_land(self, p): pass

    def update(self):
        self.timer += 1
        phase = self.timer % (self.up_time + self.down_time)
        self.spikes_up = phase < self.up_time

    def kills_player(self, player):
        if not self.spikes_up or not player.alive: return False
        spike_rect = pygame.Rect(self.rect.x, self.rect.y - self.SPIKE_H,
                                 self.rect.width, self.SPIKE_H + 4)
        return player.rect.colliderect(spike_rect)

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return

        # Platform base
        pygame.draw.rect(surface, self.color, sr, border_radius=6)
        hi = tuple(min(c + 30, 255) for c in self.color)
        pygame.draw.rect(surface, hi, (sr.x + 4, sr.y, sr.width - 8, 4), border_radius=3)

        # Spike extension amount
        phase = self.timer % (self.up_time + self.down_time)
        if self.spikes_up:
            ext = self.SPIKE_H
        else:
            retract = min(1.0, (phase - self.up_time) / 12.0)
            ext = int(self.SPIKE_H * (1.0 - retract))

        n   = self.spike_count
        gap = sr.width / max(1, n)
        if ext > 0:
            for i in range(n):
                tip_x  = int(sr.x + gap * i + gap / 2)
                tip_y  = sr.y - ext
                base_l = int(sr.x + gap * i + 3)
                base_r = int(sr.x + gap * (i + 1) - 3)
                pygame.draw.polygon(surface, SPIKE_COLOR,
                    [(tip_x, tip_y), (base_l, sr.y), (base_r, sr.y)])
                pygame.draw.polygon(surface, (255, 110, 110),
                    [(tip_x, tip_y), (base_l, sr.y), (base_r, sr.y)], 1)

        # Warning flash — blinks when spikes are about to rise
        warn = self.down_time - (phase - self.up_time) if not self.spikes_up else 0
        if not self.spikes_up and warn < 20 and (self.timer // 4) % 2 == 0:
            pygame.draw.rect(surface, (255, 80, 80), sr, 2, border_radius=6)

        # Label
        font = pygame.font.SysFont("consolas", 10, bold=True)
        col  = (200, 50, 50) if self.spikes_up else (110, 110, 120)
        lbl  = font.render("SPIKE", True, col)
        surface.blit(lbl, (sr.centerx - lbl.get_width() // 2, sr.y + 7))


# ---------------------------------------------------------------------------
# Standard Platforms
# ---------------------------------------------------------------------------
class Platform:
    def __init__(self, x, y, w, h, color=None):
        self.rect  = pygame.Rect(x, y, w, h)
        self.color = color or PLAT_CLOUD

    def is_active(self):         return True
    def get_rect(self):          return self.rect
    def on_player_land(self, p): pass
    def update(self):            pass

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pygame.draw.rect(surface, self.color, sr, border_radius=10)
        hi = tuple(min(c + 45, 255) for c in self.color)
        pygame.draw.rect(surface, hi, (sr.x + 5, sr.y, sr.width - 10, 4), border_radius=4)


class MovingPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, w, h, speed=1.5, color=None):
        super().__init__(x1, y1, w, h, color or PLAT_MOVE)
        self.sx, self.sy = x1, y1
        self.ex, self.ey = x2, y2
        self.speed = speed; self.progress = 0.0; self.dir = 1
        self.dx = self.dy = 0

    def update(self):
        ox, oy = self.rect.x, self.rect.y
        self.progress += self.speed * self.dir * 0.005
        if self.progress >= 1: self.progress = 1.0; self.dir = -1
        elif self.progress <= 0: self.progress = 0.0; self.dir = 1
        t = self.progress; s = t * t * (3 - 2 * t)
        self.rect.x = int(self.sx + (self.ex - self.sx) * s)
        self.rect.y = int(self.sy + (self.ey - self.sy) * s)
        self.dx = self.rect.x - ox
        self.dy = self.rect.y - oy


class GlitchPlatform(Platform):
    def __init__(self, x, y, w, h, on_time=90, off_time=60, offset=0, color=None):
        super().__init__(x, y, w, h, color or PLAT_GLITCH)
        self.base_color = self.color
        self.on_time  = on_time
        self.off_time = off_time
        self.timer    = offset
        self.active   = True
        self.alpha    = 255

    def update(self):
        self.timer += 1
        phase = self.timer % (self.on_time + self.off_time)
        if phase < self.on_time:
            self.active = True
            rem = self.on_time - phase
            self.alpha = (128 + int(127 * rem / 30)) if rem < 30 else 255
            if rem < 15 and self.timer % 4 < 2: self.alpha = 70
        else:
            self.active = False
            off_e = phase - self.on_time
            self.alpha = 25 if off_e < self.off_time - 20 \
                else min(25 + (off_e - (self.off_time - 20)) * 6, 80)

    def is_active(self): return self.active

    def draw(self, surface, camera):
        if self.alpha <= 0: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        f = self.alpha / 255
        c = tuple(max(0, min(255, int(v * f))) for v in self.base_color)
        pygame.draw.rect(surface, c, sr, border_radius=8)
        if self.alpha > 80:
            for ix in range(0, sr.width, 8):
                if (self.timer + ix) % 12 < 6:
                    lc = tuple(min(v + 40, 255) for v in c)
                    pygame.draw.line(surface, lc,
                                     (sr.x + ix, sr.y), (sr.x + ix, sr.y + sr.height))


class TeleportPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, w, h, interval=120, color=None):
        super().__init__(x1, y1, w, h, color or PLAT_TELE)
        self.p1 = (x1, y1); self.p2 = (x2, y2)
        self.interval = interval; self.timer = 0; self.at1 = True; self.flash = 0

    def update(self):
        self.timer += 1
        if self.flash > 0: self.flash -= 1
        if self.timer >= self.interval:
            self.timer = 0; self.at1 = not self.at1; self.flash = 10
            self.rect.topleft = self.p1 if self.at1 else self.p2

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if not (sr.right < -10 or sr.left > SCREEN_WIDTH + 10):
            pygame.draw.rect(surface, WHITE if self.flash > 0 else self.color, sr, border_radius=8)
            if self.interval - self.timer < 30 and self.timer % 6 < 3:
                pygame.draw.rect(surface, YELLOW, sr, 2, border_radius=8)
        gp = self.p2 if self.at1 else self.p1
        gr = camera.apply(pygame.Rect(*gp, self.rect.w, self.rect.h))
        pygame.draw.rect(surface, tuple(c // 4 for c in self.color), gr, border_radius=8)
        pygame.draw.rect(surface, tuple(c // 2 for c in self.color), gr, 1, border_radius=8)


class CollapsingPlatform(Platform):
    def __init__(self, x, y, w, h, delay=45, respawn_time=180, color=None):
        super().__init__(x, y, w, h, color or PLAT_FALL)
        self.base_color  = self.color
        self.oy          = y
        self.delay       = delay
        self.respawn_time = respawn_time
        self.stood = 0; self.collapsed = False; self.rc = 0; self.shake = 0

    def update(self):
        if self.collapsed:
            self.rc += 1
            if self.rc >= self.respawn_time:
                self.collapsed = False; self.rc = 0; self.stood = 0; self.rect.y = self.oy
        elif self.stood > 0:
            self.stood += 1; self.shake = (self.stood % 4) - 2
            if self.stood >= self.delay: self.collapsed = True; self.shake = 0

    def is_active(self): return not self.collapsed
    def on_player_land(self, player):
        if not self.collapsed and self.stood == 0: self.stood = 1

    def draw(self, surface, camera):
        if self.collapsed: return
        dr = self.rect.copy(); dr.x += self.shake
        sr = camera.apply(dr)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        if self.stood > 0:
            r = min(self.stood / self.delay, 1.0)
            col = (min(255, int(self.base_color[0] + (255 - self.base_color[0]) * r)),
                   max(0, int(self.base_color[1] * (1 - r))),
                   max(0, int(self.base_color[2] * (1 - r))))
        else:
            col = self.base_color
        pygame.draw.rect(surface, col, sr, border_radius=8)
        if self.stood > self.delay * 0.5:
            pygame.draw.line(surface, BLACK,
                             (sr.centerx - 8, sr.y), (sr.centerx + 4, sr.bottom), 2)


# ---------------------------------------------------------------------------
# Checkpoint / Exit
# ---------------------------------------------------------------------------
class Checkpoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y - 50, 20, 50)
        self.spawn_x, self.spawn_y = x, y - 60
        self.activated = False; self.glow = 0

    def update(self):
        if self.activated: self.glow = (self.glow + 3) % 360

    def check(self, player):
        if not self.activated and player.rect.colliderect(self.rect):
            self.activated = True
            player.set_checkpoint(self.spawn_x, self.spawn_y)
            return True
        return False

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        c = SUN_YELLOW if self.activated else DARK_GRAY
        pygame.draw.rect(surface, c, (sr.x + 8, sr.y, 4, sr.height))
        pygame.draw.polygon(surface, c, [(sr.x + 12, sr.y), (sr.x + 12, sr.y + 16), (sr.x + 28, sr.y + 8)])
        if self.activated:
            i = abs(math.sin(math.radians(self.glow))) * 0.6 + 0.4
            pygame.draw.rect(surface, tuple(int(v * i) for v in SUN_YELLOW), sr.inflate(6, 6), 2)


class ExitDoor:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 70); self.pulse = 0

    def update(self): self.pulse = (self.pulse + 3) % 360

    def check(self, player): return player.rect.colliderect(self.rect)

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        pygame.draw.rect(surface, DARK_GRAY, sr.inflate(10, 10), border_radius=8)
        p = abs(math.sin(math.radians(self.pulse)))
        pygame.draw.rect(surface,
            (int(40 + 180 * p), int(200 + 55 * p), int(40 + 80 * p)), sr, border_radius=8)
        pygame.draw.circle(surface, SUN_YELLOW, (sr.right - 14, sr.centery), 5)
        font = pygame.font.SysFont("consolas", 14)
        surface.blit(font.render("EXIT", True, WHITE), (sr.x + 7, sr.y + 6))


# ---------------------------------------------------------------------------
# Powerup
# ---------------------------------------------------------------------------
class Powerup:
    RADIUS = 12
    def __init__(self, x, y, respawn_time=600):
        self.x, self.y = x, y
        self.rect = pygame.Rect(x - self.RADIUS, y - self.RADIUS,
                                self.RADIUS * 2, self.RADIUS * 2)
        self.collected = False; self.respawn_time = respawn_time
        self.rc = 0; self.tick = random.randint(0, 360)

    def update(self):
        self.tick += 1
        if self.collected:
            self.rc += 1
            if self.rc >= self.respawn_time: self.collected = False; self.rc = 0

    def check(self, player):
        if self.collected or not player.alive: return False
        if self.rect.colliderect(player.rect):
            self.collected = True; self.rc = 0; return True
        return False

    def draw(self, surface, camera, tick):
        if self.collected: return
        bob = math.sin(self.tick * 0.06) * 5
        cx, cy = self.x, self.y + int(bob)
        pos = camera.apply(pygame.Rect(cx - 1, cy - 1, 2, 2))
        sx, sy = pos.x, pos.y
        if sx < -30 or sx > SCREEN_WIDTH + 30: return
        pulse = abs(math.sin(self.tick * 0.08)) * 0.4 + 0.6
        pygame.draw.circle(surface,
            tuple(max(0, min(255, int(c * 0.3 * pulse))) for c in SUN_YELLOW),
            (sx, sy), int(self.RADIUS * 2 * pulse))
        pygame.draw.circle(surface,
            lerp_color(SUN_YELLOW, WHITE, abs(math.sin(self.tick * 0.1))),
            (sx, sy), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (sx - 3, sy - 3), 4)
        font = pygame.font.SysFont("consolas", 9, bold=True)
        lbl  = font.render("U", True, BLACK)
        surface.blit(lbl, (sx - lbl.get_width() // 2, sy - lbl.get_height() // 2))
        a = self.tick * 0.08
        pygame.draw.rect(surface, rainbow_color(self.tick, 0.15),
            (sx + int(math.cos(a) * (self.RADIUS + 6)) - 2,
             sy + int(math.sin(a) * (self.RADIUS + 6)) - 2, 4, 4))


# ---------------------------------------------------------------------------
# Background cloud
# ---------------------------------------------------------------------------
class BgCloud:
    def __init__(self, x, y, size, drift=0.15):
        self.x = float(x); self.y = y; self.size = size; self.drift = drift

    def draw(self, surface, camera):
        sx = int(self.x - camera.offset_x * 0.2)
        sy = int(self.y - camera.offset_y * 0.15)
        if sx < -self.size * 4 or sx > SCREEN_WIDTH + self.size * 4: return
        s = self.size
        for ox, oy, r in [(0,0,s),(s,4,int(s*.8)),(-s,4,int(s*.75)),(int(s*1.8),8,int(s*.6))]:
            pygame.draw.circle(surface, CLOUD_WHITE, (sx + ox, sy + oy), r)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player:
    WIDTH, HEIGHT = 28, 36

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vel_x = self.vel_y = 0.0
        self.on_ground = False
        self.spawn_x, self.spawn_y = x, y
        self.alive = True
        self.respawn_timer = 0
        self.facing_right = True
        self.unreal_timer = 0
        self.prev_unreal  = False
        self.riding_platform = None
        self.on_ice = False

    @property
    def is_unreal(self): return self.unreal_timer > 0

    def activate_unreal(self): self.unreal_timer = UNREAL_DURATION

    def set_checkpoint(self, x, y): self.spawn_x, self.spawn_y = x, y

    def die(self):
        if self.is_unreal: return
        self.alive = False; self.respawn_timer = 50

    def respawn(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.vel_x = self.vel_y = 0
        self.alive = True; self.on_ground = False; self.unreal_timer = 0

    def update(self, keys, platforms):
        self.prev_unreal = self.is_unreal
        if not self.alive:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0: self.respawn()
            return

        if self.unreal_timer > 0: self.unreal_timer -= 1

        if self.riding_platform is not None and hasattr(self.riding_platform, 'dx'):
            self.rect.x += self.riding_platform.dx
            self.rect.y += self.riding_platform.dy

        move  = 0.0
        speed = SPRINT_SPEED if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else MOVE_SPEED
        if self.is_unreal: speed += UNREAL_SPEED_BOOST
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: move -= speed; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move += speed; self.facing_right = True

        # Ice changes feel — sluggish acceleration, barely any friction
        accel = IcePlatform.ICE_ACCEL    if self.on_ice else 0.3
        fric  = IcePlatform.ICE_FRICTION if self.on_ice else 0.75

        self.vel_x = (self.vel_x + (move - self.vel_x) * accel) if move else (self.vel_x * fric)
        if abs(self.vel_x) < 0.1: self.vel_x = 0

        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        jumped = False
        if self.on_ground and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.vel_y = JUMP_VELOCITY + (-2 if self.is_unreal else 0)
            self.on_ground = False; self.riding_platform = None; jumped = True

        # Horizontal
        self.rect.x += int(self.vel_x)
        for plat in platforms:
            if not plat.is_active(): continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.rect.bottom <= pr.top + 6: continue
                if self.vel_x > 0:   self.rect.right = pr.left
                elif self.vel_x < 0: self.rect.left  = pr.right
                self.vel_x = 0

        # Vertical
        self.on_ground = False; self.riding_platform = None; self.on_ice = False
        vy = int(self.vel_y)
        if self.vel_y > 0 and vy == 0: vy = 1
        self.rect.y += vy
        for plat in platforms:
            if not plat.is_active(): continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.vel_y > 0:
                    self.rect.bottom = pr.top; self.vel_y = 0
                    self.on_ground   = True
                    if isinstance(plat, MovingPlatform): self.riding_platform = plat
                    if isinstance(plat, IcePlatform):    self.on_ice = True
                    plat.on_player_land(self)
                elif self.vel_y < 0:
                    self.rect.top = pr.bottom; self.vel_y = 0

        if self.rect.top > DEATH_Y:
            self.alive = False; self.respawn_timer = 50

        return "jump" if jumped else None

    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr = camera.apply(self.rect)
        if self.is_unreal:
            bc = rainbow_color(tick, 0.12)
            pygame.draw.rect(surface, bc, sr)
            pulse = abs(math.sin(tick * 0.15)) * 0.5 + 0.5
            pygame.draw.rect(surface, lerp_color(GOLD, WHITE, pulse), sr.inflate(4, 4), 2)
            gc = tuple(max(0, min(255, int(c * 0.3))) for c in bc)
            pygame.draw.rect(surface, gc, sr.inflate(6 + int(4*pulse), 6 + int(4*pulse)), 3)
        elif self.on_ice:
            pygame.draw.rect(surface, (210, 238, 255), sr)
            pygame.draw.rect(surface, PLAT_ICE, (sr.x + 2, sr.y + 2, sr.width - 4, 4))
        else:
            pygame.draw.rect(surface, CLOUD_WHITE, sr)
            pygame.draw.rect(surface, SKY_MID, (sr.x + 2, sr.y + 2, sr.width - 4, 4))
        ey    = sr.y + 10
        pupil = BLACK if not self.is_unreal else GOLD
        if self.facing_right:
            pygame.draw.rect(surface, WHITE, (sr.x + 16, ey, 7, 7))
            pygame.draw.rect(surface, pupil, (sr.x + 19, ey + 2, 4, 4))
        else:
            pygame.draw.rect(surface, WHITE, (sr.x + 5, ey, 7, 7))
            pygame.draw.rect(surface, pupil, (sr.x + 5, ey + 2, 4, 4))


# ---------------------------------------------------------------------------
# SVG → game coordinate helpers
# ---------------------------------------------------------------------------
_SVG_W        = 680
_GAME_W       = 640
_SPAWN_GAME_Y = 860
_SCALE_Y      = 4.17

def _gx(svg_x): return int(svg_x / _SVG_W * _GAME_W)
def _pw(svg_w): return max(80, int(svg_w / _SVG_W * _GAME_W))

_PH = 26


# ---------------------------------------------------------------------------
# Level builder
#
# Physics: JUMP_VELOCITY=-15, GRAVITY=0.6 → max height 187.5 px
# All vertical gaps ≤ 120 px.  Bridge platforms fill tier transitions.
#
# Obstacle theme per tier:
#   Tier 1  Staircase intro      — cloud steps + bouncy pad shortcuts
#   Tier 2  Ice gauntlet         — all ice platforms + rightward wind zone
#   Tier 3  Moving spike maze    — moving platforms + synced spike traps
#   Tier 4  Glitch + wind left   — glitch blink + leftward wind
#   Tier 5  Summit gauntlet      — collapsing + spikes + teleport + bounce exit
# ---------------------------------------------------------------------------
def create_level_1():
    """
    Vibe: chill but tricky — every obstacle feels fair and readable.

    Tier themes:
      T1  Staircase intro         cloud steps + 2 bouncy pad shortcuts
      T2  Ice + gentle wind       ice platforms, mild rightward push
      T3  Moving + spike traps    slow movers, generous spike timings
      T4  Teleport labyrinth      teleporters replace glitch — predictable, fun
      T5  Summit mix              spikes + teleport + bounce exit pad

    NO glitch platforms anywhere.
    Wind force dialled down (force=1.8) so player can fight it comfortably.
    Spike up_time >= down_time so there is always more safe time than danger time.
    Teleport intervals are long (140–180 frames) so the player can see the cycle.
    """
    plats = []
    cps   = []
    pws   = []
    winds = []

    # ══════════════════════════════════════════════════════════════════════
    # TIER 1 — Staircase intro  (y 768 → 193)
    # Plain cloud steps — purely to get the player moving and comfortable.
    # Two optional bouncy pad shortcuts reward exploration.
    # ══════════════════════════════════════════════════════════════════════
    plats.append(Platform(_gx(70),  768, _pw(260), _PH + 2, PLAT_CLOUD))  # spawn cloud
    plats.append(Platform(_gx(100), 648, _pw(100), _PH, PLAT_CLOUD))       # step 1
    plats.append(Platform(_gx(220), 530, _pw(100), _PH, PLAT_CLOUD))       # step 2
    plats.append(Platform(_gx(340), 409, _pw(100), _PH, PLAT_CLOUD))       # step 3
    plats.append(Platform(_gx(460), 301, _pw(110), _PH, PLAT_CLOUD))       # landing + CP1

    # Bouncy pad on step 1 right edge → launches over step 2 entirely (optional skip)
    plats.append(BouncyPad(_gx(163), 648 - 18))
    # Bouncy pad on step 3 right edge → launches toward landing (saves one jump)
    plats.append(BouncyPad(_gx(395), 409 - 18))

    cps.append(Checkpoint(_gx(475), 301))

    # Bridge T1 → T2
    plats.append(Platform(_gx(260), 193, _pw(110), _PH, PLAT_CLOUD))

    # ══════════════════════════════════════════════════════════════════════
    # TIER 2 — Ice + gentle wind  (y 84 → -457)
    # Ice platforms introduce slippery feel — every platform is wide enough
    # to stop on if the player is careful.  One safe cloud mid-tier.
    # Wind is mild (force=1.8) and only covers the gap between columns
    # so it nudges rather than shoves.
    # ══════════════════════════════════════════════════════════════════════
    plats.append(IcePlatform(_gx(140),  84,  _pw(150)))   # entry (widest = most forgiving)
    plats.append(IcePlatform(_gx(420), -24,  _pw(130)))
    plats.append(IcePlatform(_gx(140), -132, _pw(130)))   # CP2 here
    plats.append(Platform(   _gx(420), -240, _pw(130), _PH, PLAT_CLOUD))  # safe breather (no ice)
    plats.append(IcePlatform(_gx(140), -349, _pw(130)))
    plats.append(IcePlatform(_gx(420), -457, _pw(130)))

    # Mild rightward wind — only in the narrow gap, doesn't reach the platforms
    winds.append(WindZone(_gx(240), -420, _pw(180), 340, force=1.8, direction=1))

    cps.append(Checkpoint(_gx(160), -132))
    pws.append(Powerup(_gx(308), -290))

    # Bridge T2 → T3
    plats.append(Platform(_gx(260), -569, _pw(110), _PH, PLAT_CLOUD))

    # ══════════════════════════════════════════════════════════════════════
    # TIER 3 — Moving platforms + spike traps  (y -682 → -1116)
    # Movers are slow-to-medium speed.  Spike timings are generous:
    # down_time > up_time so safe windows are always longer than danger windows.
    # Safe cloud rest islands every other step.
    # ══════════════════════════════════════════════════════════════════════
    plats.append(Platform(_gx(140), -682, _pw(130), _PH, PLAT_CLOUD))   # safe entry + CP3

    # Right slow H-mover  (speed 1.2) — spikes: 50 up / 70 down = more safe
    _m1_y = -791
    plats.append(MovingPlatform(_gx(420), _m1_y, _gx(530), _m1_y, _pw(120), _PH, speed=1.2))
    plats.append(SpikeTrap(_gx(420), _m1_y - 14, _pw(120), 14,
                           up_time=50, down_time=70, offset=0))

    # Left safe rest cloud
    plats.append(Platform(_gx(140), -899, _pw(120), _PH, PLAT_CLOUD))

    # Right slow V-mover — spikes: 45 up / 75 down (very generous)
    _m2_y = -1008
    plats.append(MovingPlatform(_gx(420), _m2_y, _gx(420), _m2_y - 70, _pw(120), _PH, speed=0.9))
    plats.append(SpikeTrap(_gx(420), _m2_y - 14, _pw(120), 14,
                           up_time=45, down_time=75, offset=30))

    # Left slow H-mover, no spikes — relaxed pacing
    plats.append(MovingPlatform(_gx(140), -1116, _gx(310), -1116, _pw(120), _PH, speed=1.1))

    cps.append(Checkpoint(_gx(160), -682))
    pws.append(Powerup(_gx(308), -950))

    # Bridge T3 → T4
    plats.append(Platform(_gx(260), -1203, _pw(110), _PH, PLAT_CLOUD))

    # ══════════════════════════════════════════════════════════════════════
    # TIER 4 — Teleport labyrinth + leftward wind  (y -1291 → -1792)
    # ALL platforms here are teleporters (no glitch).
    # Intervals are long (140–180 frames ≈ 2.3–3 s) so the player can easily
    # read the cycle before jumping.  Ghost position always shows where it
    # will reappear.  One safe cloud mid-tier.
    # Leftward wind is mild (force=1.6) and only in the upper half.
    # ══════════════════════════════════════════════════════════════════════
    plats.append(Platform(_gx(150), -1291, _pw(130), _PH, PLAT_CLOUD))   # safe entry + CP4

    # T4 teleporters — each jumps to a nearby second position
    plats.append(TeleportPlatform(_gx(420), -1391, _gx(300), -1391,
                                  _pw(110), _PH, interval=160))
    plats.append(TeleportPlatform(_gx(140), -1491, _gx(260), -1480,
                                  _pw(110), _PH, interval=180))
    plats.append(Platform(        _gx(420), -1591, _pw(120), _PH, PLAT_CLOUD))   # mid safe
    plats.append(TeleportPlatform(_gx(140), -1692, _gx(270), -1700,
                                  _pw(110), _PH, interval=150))
    plats.append(TeleportPlatform(_gx(430), -1792, _gx(310), -1785,
                                  _pw(110), _PH, interval=140))

    # Mild leftward wind — upper portion only, easy to counter with right movement
    winds.append(WindZone(_gx(120), -1770, _pw(420), 300, force=1.6, direction=-1))

    cps.append(Checkpoint(_gx(165), -1291))
    pws.append(Powerup(_gx(308), -1540))

    # Bridge T4 → T5
    plats.append(Platform(_gx(160), -1889, _pw(110), _PH, PLAT_CLOUD))
    plats.append(Platform(_gx(420), -1986, _pw(110), _PH, PLAT_CLOUD))

    # ══════════════════════════════════════════════════════════════════════
    # TIER 5 — Summit mix  (y -2084 → -2542)
    # Combines teleport + spikes + a collapsing platform with a bouncy pad
    # on top as a skill-skip to the exit.  All spike timings remain generous.
    # ══════════════════════════════════════════════════════════════════════

    # Left teleporter (long interval — easy to read)
    plats.append(TeleportPlatform(_gx(150), -2084, _gx(260), -2075,
                                  _pw(110), _PH, interval=160))

    # Right medium H-mover + fair spike timing (50 up / 80 down)
    _m3_y = -2184
    plats.append(MovingPlatform(_gx(420), _m3_y, _gx(530), _m3_y, _pw(110), _PH, speed=1.4))
    plats.append(SpikeTrap(_gx(420), _m3_y - 14, _pw(110), 14,
                           up_time=50, down_time=80, offset=15))

    # Left collapsing platform — delay 55 frames (just under 1 s) — fair warning
    plats.append(CollapsingPlatform(_gx(160), -2275, _pw(100), _PH, delay=55))
    # Bouncy pad on top: if player hits it before collapse, launches straight to exit platform
    plats.append(BouncyPad(_gx(178), -2275 - 18))

    # Right safe cloud + CP5
    plats.append(Platform(_gx(420), -2367, _pw(110), _PH, PLAT_CLOUD))

    # Bridge T5 → exit
    plats.append(Platform(_gx(255), -2454, _pw(110), _PH, PLAT_CLOUD))
    plats.append(Platform(_gx(255), -2542, _pw(130), _PH + 4, PLAT_CLOUD))

    cps.append(Checkpoint(_gx(435), -2367))
    pws.append(Powerup(_gx(308), -2320))

    exit_door = ExitDoor(_gx(295), -2620)
    return plats, cps, pws, winds, exit_door


LEVELS = [create_level_1]


# ---------------------------------------------------------------------------
# Background clouds
# ---------------------------------------------------------------------------
def make_bg_clouds():
    clouds = []
    rng = random.Random(42)
    for _ in range(80):
        clouds.append(BgCloud(
            rng.randint(-200, 800), rng.randint(-3000, 900),
            rng.randint(28, 65), rng.uniform(0.05, 0.2),
        ))
    return clouds


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sky Climber – Level 1")
        self.clock = pygame.time.Clock()

        self.font       = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font   = pygame.font.SysFont("consolas", 48)
        self.tiny_font  = pygame.font.SysFont("consolas", 12, bold=True)

        self.sfx = SoundManager()
        self.state = "playing"
        self.level_time = self.tick = self.win_timer = 0
        self.music_volume = 0.5; self.music_muted = False
        self.settings_cursor = 0

        self.camera    = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = []; self.rings = []; self.flashes = []
        self.score_popups = []
        self.bg_clouds = make_bg_clouds()

        self.platforms = []; self.checkpoints = []
        self.powerups  = []; self.winds       = []
        self.exit_door = None
        self.player    = Player(100, 400)

        self.load_level(0)
        self.sfx.start_music(volume=self.music_volume)

    def load_level(self, index=0):
        (self.platforms, self.checkpoints,
         self.powerups, self.winds,
         self.exit_door) = LEVELS[index % len(LEVELS)]()
        spawn_x = _gx(100)
        spawn_y = 768 - 40
        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles.clear(); self.rings.clear()
        self.flashes.clear(); self.score_popups.clear()
        self.level_time = self.tick = self.win_timer = 0

    def _exit_to_menu(self):
        self.sfx.stop_music(); self.running = False

    def _apply_volume(self):
        pygame.mixer.music.set_volume(0.0 if self.music_muted else self.music_volume)

    # ── Main loop ────────────────────────────────────────────────────────
    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._exit_to_menu(); return
                if event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)
            if not self.running: return
            if self.state == "playing": self._update()
            elif self.state == "win":   self.win_timer += 1
            self._draw()
            self.clock.tick(FPS)

    def _handle_key(self, key):
        if self.state == "settings":
            if key == pygame.K_ESCAPE: self.state = "playing"
            elif key in (pygame.K_UP,   pygame.K_w): self.settings_cursor = (self.settings_cursor-1)%4
            elif key in (pygame.K_DOWN, pygame.K_s): self.settings_cursor = (self.settings_cursor+1)%4
            elif key in (pygame.K_LEFT, pygame.K_a):
                if self.settings_cursor == 0:
                    self.music_volume = max(0.0, round(self.music_volume-0.1,1)); self._apply_volume()
            elif key in (pygame.K_RIGHT, pygame.K_d):
                if self.settings_cursor == 0:
                    self.music_volume = min(1.0, round(self.music_volume+0.1,1)); self._apply_volume()
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if   self.settings_cursor == 1: self.music_muted = not self.music_muted; self._apply_volume()
                elif self.settings_cursor == 2: self.state = "playing"
                elif self.settings_cursor == 3: self._exit_to_menu()
            return
        if self.state == "win":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE): self._exit_to_menu()
            return
        if key == pygame.K_ESCAPE:
            self.state = "settings"; self.settings_cursor = 2
        elif key == pygame.K_r:
            self.player.unreal_timer = 0; self.player.die(); self.sfx.play("death")

    # ── Update ───────────────────────────────────────────────────────────
    def _update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()

        for p in self.platforms: p.update()
        for w in self.winds:     w.update()

        result = self.player.update(keys, self.platforms)
        if result == "jump": self.sfx.play("jump")

        # Detect BouncyPad launch (first frame of squish = just bounced)
        for p in self.platforms:
            if isinstance(p, BouncyPad) and p.squish == 9:
                self.sfx.play("bounce")
                self._bounce_fx(p)

        if self.player.prev_unreal and not self.player.is_unreal: self.sfx.play("unreal_end")
        if self.player.alive: self.camera.update(self.player.rect)

        # Wind push every frame
        for w in self.winds:
            w.apply_to_player(self.player)

        # Spike trap death
        for p in self.platforms:
            if isinstance(p, SpikeTrap) and p.kills_player(self.player):
                if not self.player.is_unreal:
                    self._player_death_fx(); self.player.die(); self.sfx.play("death")

        for cp in self.checkpoints:
            cp.update()
            if self.player.alive and cp.check(self.player): self.sfx.play("checkpoint")

        for pw in self.powerups:
            pw.update()
            if pw.check(self.player):
                self._powerup_fx(pw); self.player.activate_unreal(); self.sfx.play("powerup")

        self.exit_door.update()
        if self.player.alive and self.exit_door.check(self.player):
            self.state = "win"; self.sfx.play("win"); self.sfx.stop_music()

        self.particles    = [p for p in self.particles if p.update()]
        self.rings        = [r for r in self.rings     if r.update()]
        self.flashes      = [f for f in self.flashes   if f.update()]
        self.score_popups = [(x, y-0.8, t, timer-1, c)
                             for x, y, t, timer, c in self.score_popups if timer > 0]
        self._spawn_ambient()
        if not self.player.alive and self.player.respawn_timer == 1: self.sfx.play("respawn")
        self.level_time += 1

    # ── Effects ──────────────────────────────────────────────────────────
    def _player_death_fx(self):
        cx, cy = self.player.rect.center
        self.camera.add_shake(14)
        self.flashes.append(FlashOverlay(RED, 18, 120))
        for _ in range(35):
            a = random.uniform(0, math.pi*2); s = random.uniform(2, 7)
            self.particles.append(Particle(cx, cy,
                random.choice([SKY_MID, CYAN, WHITE, CLOUD_WHITE]),
                math.cos(a)*s, math.sin(a)*s, random.randint(25,50), random.randint(3,7), 0.15))
        for _ in range(8):
            self.particles.append(Particle(
                cx+random.randint(-10,10), cy+random.randint(-10,10),
                CLOUD_SHADOW, random.uniform(-3,3), random.uniform(-8,-2), 40, 6, 0.3))

    def _bounce_fx(self, pad):
        cx = pad.rect.centerx; cy = pad.rect.top
        self.rings.append(RingEffect(cx, cy, (100, 255, 120), 60, 4, 2))
        for _ in range(14):
            a = random.uniform(-math.pi, 0); s = random.uniform(1, 4)
            self.particles.append(Particle(cx, cy,
                random.choice([PLAT_BOUNCE, WHITE, (180, 255, 180)]),
                math.cos(a)*s, math.sin(a)*s - 1, random.randint(15,30), random.randint(2,5), 0.12))

    def _powerup_fx(self, pw):
        cx, cy = pw.x, pw.y
        self.camera.add_shake(10)
        self.flashes.append(FlashOverlay(SUN_YELLOW, 20, 160))
        for i in range(3):
            self.rings.append(RingEffect(cx, cy, rainbow_color(self.tick+i*30), 100+i*40, 3+i, 4-i))
        for _ in range(40):
            a = random.uniform(0, math.pi*2); s = random.uniform(1, 5)
            self.particles.append(Particle(cx, cy,
                random.choice([SUN_YELLOW, YELLOW, WHITE, ORANGE]),
                math.cos(a)*s, math.sin(a)*s, random.randint(30,60), random.randint(2,6), 0.05))
        self.score_popups.append((cx, cy-30, "UNREAL MODE!", 90, SUN_YELLOW))

    def _spawn_ambient(self):
        for plat in self.platforms:
            if isinstance(plat, IcePlatform) and random.random() < 0.07:
                self.particles.append(Particle(
                    plat.rect.x + random.randint(0, plat.rect.width),
                    plat.rect.y - 2,
                    (205, 238, 255),
                    random.uniform(-0.4,0.4), random.uniform(-1.4,-0.2),
                    random.randint(12,22), 2, 0.0))
            elif isinstance(plat, TeleportPlatform) and plat.flash > 0:
                for _ in range(4):
                    self.particles.append(Particle(
                        plat.rect.x + random.randint(0, plat.rect.width),
                        plat.rect.y + random.randint(0, plat.rect.height),
                        SUN_YELLOW, random.uniform(-3,3), random.uniform(-3,3), 15))
            elif isinstance(plat, TeleportPlatform) and (self.tick % 8 == 0):
                # Gentle idle shimmer on teleporters
                self.particles.append(Particle(
                    plat.rect.x + random.randint(0, plat.rect.width),
                    plat.rect.y,
                    PLAT_TELE, random.uniform(-0.5,0.5), random.uniform(-1.0,-0.2), 18, 2, 0.0))

        if not self.player.alive and self.player.respawn_timer == 49:
            self._player_death_fx()

        if self.player.alive and self.player.is_unreal:
            if self.tick % 2 == 0:
                self.particles.append(Particle(
                    self.player.rect.centerx + random.randint(-8,8),
                    self.player.rect.bottom  + random.randint(-4,4),
                    rainbow_color(self.tick + random.randint(0,20)),
                    random.uniform(-0.5,0.5), random.uniform(-1.5,-0.3),
                    random.randint(15,30), random.randint(3,6), 0.02))
            if self.tick % 5 == 0:
                side = 1 if self.player.facing_right else -1
                self.particles.append(Particle(
                    self.player.rect.centerx - side*12,
                    self.player.rect.centery + random.randint(-10,10),
                    WHITE, -side*random.uniform(1,3), random.uniform(-1,1), 15, 3, 0))

        # Wind particles on player when inside zone
        for w in self.winds:
            if self.player.rect.colliderect(w.rect) and self.tick % 3 == 0:
                self.particles.append(Particle(
                    self.player.rect.centerx + random.randint(-14,14),
                    self.player.rect.centery + random.randint(-14,14),
                    WIND_COLOR,
                    w.force * w.direction * 0.6 + random.uniform(-0.3,0.3),
                    random.uniform(-0.4,0.4), 18, 3, 0.0))

    # ── Drawing ──────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(DARK_BG)
        if   self.state == "playing":  self._draw_game()
        elif self.state == "settings": self._draw_game(); self._draw_settings()
        elif self.state == "win":      self._draw_win()
        pygame.display.flip()

    def _draw_background(self):
        for i, col in enumerate([
            (74,144,200),(114,174,221),(157,203,238),(190,224,245),(216,238,248)
        ]):
            pygame.draw.rect(self.screen, col,
                (0, i*SCREEN_HEIGHT//5, SCREEN_WIDTH, SCREEN_HEIGHT//5+2))

        pulse = abs(math.sin(self.tick * 0.03)) * 6
        pygame.draw.circle(self.screen, SUN_ORANGE, (SCREEN_WIDTH-110, 70), int(34+pulse))
        pygame.draw.circle(self.screen, SUN_YELLOW, (SCREEN_WIDTH-110, 70), 22)
        pygame.draw.circle(self.screen, WHITE,      (SCREEN_WIDTH-122, 58), 9)

        alt_ratio = max(0.0, min(1.0, -self.camera.offset_y / 2000))
        for sx, sy in [(80,20),(160,35),(260,15),(380,28),(450,12)]:
            if alt_ratio > 0.3:
                bri = int((140+115*abs(math.sin(self.tick*0.04+sx*0.1)))
                          * (alt_ratio-0.3)/0.7)
                pygame.draw.circle(self.screen, (bri,bri,bri), (sx,sy), 2)

        for c in self.bg_clouds: c.draw(self.screen, self.camera)

        oy = int(self.camera.offset_y * 0.1) % 90
        for y in range(0, SCREEN_HEIGHT+90, 90):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y-oy), (SCREEN_WIDTH, y-oy))

    def _draw_game(self):
        self._draw_background()

        # Wind zones — behind everything
        for w in self.winds: w.draw(self.screen, self.camera)

        for p  in self.platforms:    p.draw(self.screen, self.camera)
        for cp in self.checkpoints:  cp.draw(self.screen, self.camera)
        for pw in self.powerups:     pw.draw(self.screen, self.camera, self.tick)
        self.exit_door.draw(self.screen, self.camera)
        for p  in self.particles:    p.draw(self.screen, self.camera)
        for r  in self.rings:        r.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.tick)
        for f  in self.flashes:      f.draw(self.screen)

        for x, y, text, timer, color in self.score_popups:
            a = min(1.0, timer/30)
            c = tuple(max(0,min(255,int(v*a))) for v in color)
            pos = self.camera.apply(pygame.Rect(int(x),int(y),1,1))
            surf = self.small_font.render(text, True, c)
            self.screen.blit(surf, surf.get_rect(center=(pos.x, pos.y)))

        # HUD
        t = self.level_time / FPS
        self.screen.blit(self.small_font.render(f"Time: {t:.1f}s", True, DARK_GRAY),
                         (SCREEN_WIDTH-150, 10))

        # Altitude bar
        alt   = max(0, min(3400, 860 - self.player.rect.centery))
        ratio = alt / 3400
        bh=200; bx=12; by=SCREEN_HEIGHT//2-bh//2
        pygame.draw.rect(self.screen, DARK_GRAY, (bx, by, 10, bh), 1)
        fh = int(bh*ratio)
        pygame.draw.rect(self.screen, lerp_color(SKY_BOT, SUN_YELLOW, ratio),
                         (bx, by+bh-fh, 10, fh))
        self.screen.blit(self.tiny_font.render("ALT", True, DARK_GRAY), (bx-2, by-14))

        # Unreal bar
        if self.player.is_unreal:
            rem = self.player.unreal_timer / FPS
            bw=160; bh2=14; bx2=SCREEN_WIDTH//2-80; by2=12
            r2 = self.player.unreal_timer / UNREAL_DURATION
            pygame.draw.rect(self.screen, DARK_GRAY, (bx2-2, by2-2, bw+4, bh2+4))
            for pi in range(int(bw*r2)):
                pygame.draw.line(self.screen, rainbow_color(self.tick+pi*2, 0.3),
                                 (bx2+pi, by2), (bx2+pi, by2+bh2))
            self.screen.blit(self.tiny_font.render(f"UNREAL  {rem:.1f}s", True, WHITE),
                             (bx2+4, by2+1))
            pygame.draw.rect(self.screen, rainbow_color(self.tick, 0.15),
                             (bx2-2, by2-2, bw+4, bh2+4), 2)

        # Obstacle legend — top left
        legend = [
            (PLAT_ICE,    "ICE    — slippery!"),
            (WIND_COLOR,  "WIND   — push zone"),
            (SPIKE_COLOR, "SPIKE  — timed!"),
            (PLAT_BOUNCE, "SPRING — launcher"),
            (PLAT_TELE,   "TELE   — teleports!"),
        ]
        for i, (col, txt) in enumerate(legend):
            pygame.draw.rect(self.screen, col, (34, 10+i*18, 12, 12), border_radius=3)
            self.screen.blit(self.tiny_font.render(txt, True, DARK_GRAY), (52, 10+i*18))

        self.screen.blit(self.small_font.render("R-Respawn  ESC-Settings", True, CLOUD_SHADOW),
                         (10, SCREEN_HEIGHT-22))

        if not self.player.alive:
            txt = self.font.render("Respawning...", True, RED)
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

    def _draw_settings(self):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); ov.fill(BLACK); ov.set_alpha(160)
        self.screen.blit(ov, (0,0))
        hdr = self.font.render("SETTINGS", True, CYAN)
        self.screen.blit(hdr, hdr.get_rect(center=(SCREEN_WIDTH//2, 160)))
        items = [f"Music Volume:  < {int(self.music_volume*100)}% >",
                 f"Mute Music:    {'ON' if self.music_muted else 'OFF'}",
                 "Resume Game", "Exit to Menu"]
        hints = ["(Left / Right)", "(Enter to toggle)", "(Enter)", "(Enter)"]
        for i, (item, hint) in enumerate(zip(items, hints)):
            y = 230+i*50; sel = i == self.settings_cursor
            color = SUN_YELLOW if sel else GRAY
            if sel:
                bar = pygame.Rect(SCREEN_WIDTH//2-200, y-4, 400, 30)
                pygame.draw.rect(self.screen, (30,50,80), bar)
                pygame.draw.rect(self.screen, SUN_YELLOW, bar, 1)
                self.screen.blit(self.small_font.render(">", True, SUN_YELLOW),
                                 (SCREEN_WIDTH//2-190, y))
            self.screen.blit(self.small_font.render(item, True, color), (SCREEN_WIDTH//2-160, y))
            if sel:
                self.screen.blit(self.tiny_font.render(hint, True, (120,140,160)),
                                 (SCREEN_WIDTH//2-160, y+20))
        bx = SCREEN_WIDTH//2-100; vy = 258
        pygame.draw.rect(self.screen, DARK_GRAY, (bx, vy, 200, 6))
        pygame.draw.rect(self.screen, CYAN if not self.music_muted else RED,
                         (bx, vy, int(200*self.music_volume), 6))
        pygame.draw.rect(self.screen, WHITE, (bx, vy, 200, 6), 1)
        esc = self.tiny_font.render("ESC to resume", True, (100,120,140))
        self.screen.blit(esc, esc.get_rect(center=(SCREEN_WIDTH//2, 480)))

    def _draw_win(self):
        for i in range(8):
            pygame.draw.rect(self.screen, lerp_color(SKY_TOP, SKY_BOT, i/7),
                             (0, i*SCREEN_HEIGHT//8, SCREEN_WIDTH, SCREEN_HEIGHT//8+2))
        wt = self.big_font.render("LEVEL COMPLETE!", True, SUN_YELLOW)
        self.screen.blit(wt, wt.get_rect(center=(SCREEN_WIDTH//2, 160)))
        t = self.level_time / FPS
        for surf, cy in [
            (self.font.render(f"Time: {t:.1f} seconds", True, WHITE), 250),
            (self.small_font.render("Press ENTER or ESC to exit", True, WHITE), 360),
        ]:
            self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH//2, cy)))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def launch_game():
    pygame.mixer.music.stop()
    game = Game()
    game.run()
    pygame.display.set_caption("Main Menu")
    try:
        pygame.mixer.music.load("assets/audio/BackgroundMusic.mp3")
        pygame.mixer.music.play(-1)
    except Exception:
        pass


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    game = Game()
    game.run()
    pygame.quit()