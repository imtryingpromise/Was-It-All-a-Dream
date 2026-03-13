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

# Sky / Cloud colour palette
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
SKY_TOP      = (74,  144, 200)   # deep blue at altitude (SVG #4A90C8)
SKY_MID      = (114, 174, 221)   # SVG #72AEDD
SKY_BOT      = (190, 224, 245)   # SVG #BEE0F5
CLOUD_WHITE  = (208, 234, 255)   # SVG #D0EAFF  — cloud platform tint
CLOUD_SHADOW = (128, 184, 224)   # SVG #80B8E0
SUN_YELLOW   = (255, 215,  64)   # SVG #FFD740
SUN_ORANGE   = (255, 153,   0)   # SVG #FF9900
PLAT_CLOUD   = (208, 234, 255)   # standard cloud platform  #D0EAFF
PLAT_MOVE    = (136, 221, 136)   # moving  #88DD88
PLAT_GLITCH  = (200, 168, 255)   # glitch  #C8A8FF
PLAT_FALL    = (255, 152, 152)   # collapsing  #FF9898
PLAT_TELE    = (255, 184,  96)   # teleport  #FFB860
GRAY         = (160, 170, 185)
DARK_GRAY    = ( 70,  80,  95)
RED          = (220,  60,  60)
GREEN        = ( 60, 200,  90)
YELLOW       = (255, 220,  50)
ORANGE       = (255, 160,  30)
CYAN         = ( 80, 220, 255)
GOLD         = (255, 200,  50)
BROWN        = (160, 110,  60)
DARK_BROWN   = (110,  70,  30)
MUSHROOM_RED = (204,  34,  34)   # SVG #CC2222
DARK_BG      = (155, 205, 250)
GRID_COLOR   = (140, 190, 235)

# Physics
GRAVITY        = 0.6
JUMP_VELOCITY  = -15
MOVE_SPEED     = 5
SPRINT_SPEED   = 8
MAX_FALL_SPEED = 15
STOMP_BOUNCE   = -10

# Death Y — below the spawn cloud
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
    "jump": "jump.wav", "death": "death.wav", "respawn": "respawn.wav",
    "stomp": "stomp.wav", "monster_kill": "monster_kill.wav",
    "powerup": "powerup.wav", "unreal_end": "unreal_end.wav",
    "checkpoint": "checkpoint.wav", "win": "win.wav",
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
# Camera  — follows player both X and Y (vertical map)
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
        # Horizontal: keep player ~1/3 from left
        tx = target_rect.centerx - self.width // 3
        self.offset_x += (tx - self.offset_x) * 0.1
        # Vertical: centre player — full Y tracking for vertical map
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
        self.speed = speed; self.width = width

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
        self.color = color; self.duration = duration
        self.timer = duration; self.max_alpha = max_alpha
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface.fill(color)

    def update(self):
        self.timer -= 1; return self.timer > 0

    def draw(self, surface):
        self.surface.set_alpha(int(self.max_alpha * self.timer / self.duration))
        surface.blit(self.surface, (0, 0))


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
        self.prev_unreal = False
        self.kill_count = 0
        self.riding_platform = None

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

        move = 0.0
        speed = SPRINT_SPEED if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else MOVE_SPEED
        if self.is_unreal: speed += UNREAL_SPEED_BOOST
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: move -= speed; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move += speed; self.facing_right = True

        self.vel_x = self.vel_x + (move - self.vel_x) * 0.3 if move else self.vel_x * 0.75
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
        self.on_ground = False; self.riding_platform = None
        vy = int(self.vel_y)
        if self.vel_y > 0 and vy == 0: vy = 1
        self.rect.y += vy
        for plat in platforms:
            if not plat.is_active(): continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.vel_y > 0:
                    self.rect.bottom = pr.top; self.vel_y = 0
                    self.on_ground = True
                    if isinstance(plat, MovingPlatform): self.riding_platform = plat
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
            pygame.draw.rect(surface, gc, sr.inflate(6 + int(4 * pulse), 6 + int(4 * pulse)), 3)
        else:
            pygame.draw.rect(surface, CLOUD_WHITE, sr)
            pygame.draw.rect(surface, SKY_MID, (sr.x + 2, sr.y + 2, sr.width - 4, 4))
        ey = sr.y + 10
        pupil = BLACK if not self.is_unreal else GOLD
        if self.facing_right:
            pygame.draw.rect(surface, WHITE, (sr.x + 16, ey, 7, 7))
            pygame.draw.rect(surface, pupil, (sr.x + 19, ey + 2, 4, 4))
        else:
            pygame.draw.rect(surface, WHITE, (sr.x + 5,  ey, 7, 7))
            pygame.draw.rect(surface, pupil, (sr.x + 5,  ey + 2, 4, 4))


# ---------------------------------------------------------------------------
# Platforms
# ---------------------------------------------------------------------------
class Platform:
    def __init__(self, x, y, w, h, color=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color or PLAT_CLOUD

    def is_active(self): return True
    def get_rect(self):  return self.rect
    def on_player_land(self, player): pass
    def update(self): pass

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pygame.draw.rect(surface, self.color, sr, border_radius=10)
        hi = tuple(min(c + 45, 255) for c in self.color)
        pygame.draw.rect(surface, hi, (sr.x + 5, sr.y, sr.width - 10, 4), border_radius=4)


class MovingPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, w, h, speed=1.5, color=None):
        super().__init__(x1, y1, w, h, color or PLAT_MOVE)
        self.sx, self.sy = x1, y1; self.ex, self.ey = x2, y2
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
        self.dx = self.rect.x - ox; self.dy = self.rect.y - oy


class GlitchPlatform(Platform):
    def __init__(self, x, y, w, h, on_time=90, off_time=60, offset=0, color=None):
        super().__init__(x, y, w, h, color or PLAT_GLITCH)
        self.base_color = self.color
        self.on_time = on_time; self.off_time = off_time
        self.timer = offset; self.active = True; self.alpha = 255

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
            self.alpha = 25 if off_e < self.off_time - 20 else min(25 + (off_e - (self.off_time - 20)) * 6, 80)

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
                    pygame.draw.line(surface, lc, (sr.x + ix, sr.y), (sr.x + ix, sr.y + sr.height))


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
        self.base_color = self.color; self.oy = y; self.delay = delay
        self.respawn_time = respawn_time; self.stood = 0
        self.collapsed = False; self.rc = 0; self.shake = 0

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
            pygame.draw.line(surface, BLACK, (sr.centerx - 8, sr.y), (sr.centerx + 4, sr.bottom), 2)


# ---------------------------------------------------------------------------
# Checkpoint
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


# ---------------------------------------------------------------------------
# Exit Door
# ---------------------------------------------------------------------------
class ExitDoor:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 70); self.pulse = 0

    def update(self): self.pulse = (self.pulse + 3) % 360

    def check(self, player): return player.rect.colliderect(self.rect)

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        pygame.draw.rect(surface, DARK_GRAY, sr.inflate(10, 10), border_radius=8)
        p = abs(math.sin(math.radians(self.pulse)))
        pygame.draw.rect(surface, (int(40 + 180 * p), int(200 + 55 * p), int(40 + 80 * p)), sr, border_radius=8)
        pygame.draw.circle(surface, SUN_YELLOW, (sr.right - 14, sr.centery), 5)
        font = pygame.font.SysFont("consolas", 14)
        surface.blit(font.render("EXIT", True, WHITE), (sr.x + 7, sr.y + 6))


# ---------------------------------------------------------------------------
# Monsters
# ---------------------------------------------------------------------------
class Monster:
    WIDTH, HEIGHT = 26, 26
    def __init__(self, x, y, pl, pr, speed=1.5, color=None):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.pl, self.pr = pl, pr; self.speed = speed; self.dir = 1
        self.color = color or (255, 100, 80); self.alive = True
        self.death_timer = 0; self.bob = 0

    def update(self):
        if not self.alive: self.death_timer -= 1; return
        self.rect.x += int(self.speed * self.dir)
        if self.rect.x >= self.pr: self.rect.x = self.pr; self.dir = -1
        elif self.rect.x <= self.pl: self.rect.x = self.pl; self.dir = 1
        self.bob += 0.12

    def kill(self): self.alive = False; self.death_timer = 1

    def check_collision(self, player):
        if not self.alive or not player.alive: return None
        if not self.rect.colliderect(player.rect): return None
        return "kill_monster" if player.is_unreal else "kill_player"

    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        bo = int(math.sin(self.bob) * 2)
        b = pygame.Rect(sr.x, sr.y + bo, sr.w, sr.h)
        pygame.draw.rect(surface, self.color, b, border_radius=4)
        for sx in range(b.x + 2, b.right - 2, 6):
            pygame.draw.polygon(surface, self.color, [(sx, b.y), (sx + 3, b.y - 6), (sx + 6, b.y)])
        ey = b.y + 8
        pygame.draw.rect(surface, WHITE, (b.x + 4,  ey, 6, 5))
        pygame.draw.rect(surface, WHITE, (b.x + 16, ey, 6, 5))
        pygame.draw.rect(surface, BLACK, (b.x + 6,  ey + 2, 3, 3))
        pygame.draw.rect(surface, BLACK, (b.x + 18, ey + 2, 3, 3))
        pygame.draw.line(surface, BLACK, (b.x + 3, ey - 2), (b.x + 10, ey), 2)
        pygame.draw.line(surface, BLACK, (b.right - 3, ey - 2), (b.right - 10, ey), 2)


class FlyingMonster:
    WIDTH, HEIGHT = 30, 22
    def __init__(self, x, y, pl, pr, speed=1.2, amplitude=40, color=None):
        self.bx, self.by = float(x), float(y)
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.pl, self.pr = pl, pr; self.speed = speed
        self.amplitude = amplitude; self.dir = 1
        self.color = color or (85, 119, 238); self.alive = True
        self.death_timer = 0; self.phase = random.uniform(0, math.pi * 2); self.tick = 0

    def update(self):
        if not self.alive: self.death_timer -= 1; return
        self.tick += 1; self.bx += self.speed * self.dir
        if self.bx >= self.pr: self.bx = self.pr; self.dir = -1
        elif self.bx <= self.pl: self.bx = self.pl; self.dir = 1
        self.rect.x = int(self.bx)
        self.rect.y = int(self.by + math.sin(self.tick * 0.04 + self.phase) * self.amplitude)

    def kill(self): self.alive = False; self.death_timer = 1

    def check_collision(self, player):
        if not self.alive or not player.alive: return None
        if not self.rect.colliderect(player.rect): return None
        return "kill_monster" if player.is_unreal else "kill_player"

    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pygame.draw.ellipse(surface, self.color, sr)
        wy = sr.centery - 2 + int(math.sin(tick * 0.3) * 3)
        pygame.draw.polygon(surface, self.color, [(sr.left, wy), (sr.left - 10, wy - 8), (sr.left + 5, wy)])
        pygame.draw.polygon(surface, self.color, [(sr.right, wy), (sr.right + 10, wy - 8), (sr.right - 5, wy)])
        ey = sr.y + 6; ex = sr.x + 16 if self.dir >= 0 else sr.x + 8
        pygame.draw.rect(surface, WHITE, (ex, ey, 6, 5))
        pygame.draw.rect(surface, BLACK, (ex + 2, ey + 1, 3, 3))


class MushroomMonster:
    WIDTH, HEIGHT = 28, 28
    def __init__(self, x, y, patrol_left, patrol_right, speed=1.3):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.patrol_left = patrol_left; self.patrol_right = patrol_right
        self.speed = speed; self.direction = 1; self.alive = True
        self.death_timer = 0; self.squish_timer = 0; self.tick = 0

    def update(self):
        if not self.alive: self.death_timer -= 1; return
        if self.squish_timer > 0:
            self.squish_timer -= 1
            if self.squish_timer <= 0: self.alive = False; self.death_timer = 1
            return
        self.tick += 1; self.rect.x += int(self.speed * self.direction)
        if self.rect.x >= self.patrol_right: self.rect.x = self.patrol_right; self.direction = -1
        elif self.rect.x <= self.patrol_left: self.rect.x = self.patrol_left; self.direction = 1

    def kill(self): self.alive = False; self.death_timer = 1
    def stomp(self): self.squish_timer = 12

    def check_collision(self, player):
        if not self.alive or self.squish_timer > 0 or not player.alive: return None
        if not self.rect.colliderect(player.rect): return None
        if player.is_unreal: return "kill_monster"
        if player.vel_y > 0 and player.rect.bottom <= self.rect.centery + 6: return "stomp"
        return "kill_player"

    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        if self.squish_timer > 0:
            flat = pygame.Rect(sr.x - 4, sr.bottom - 8, sr.width + 8, 8)
            pygame.draw.rect(surface, BROWN, flat)
            pygame.draw.ellipse(surface, MUSHROOM_RED, (flat.x, flat.y - 4, flat.width, 8))
            return
        bob = int(math.sin(self.tick * 0.2) * 1.5)
        stem = pygame.Rect(sr.x + 4, sr.centery + bob, sr.width - 8, sr.height // 2)
        pygame.draw.rect(surface, BROWN, stem)
        cap = pygame.Rect(sr.x - 2, sr.y + bob, sr.width + 4, sr.height // 2 + 4)
        pygame.draw.ellipse(surface, MUSHROOM_RED, cap)
        for sx, sy, r in [(cap.x + 6, cap.y + 5, 3), (cap.right - 8, cap.y + 4, 3), (cap.centerx, cap.y + 2, 2)]:
            pygame.draw.circle(surface, WHITE, (sx, sy + bob), r)
        fy = sr.bottom + bob
        pygame.draw.ellipse(surface, DARK_BROWN, (sr.x + 2, fy - 4, 8, 5))
        pygame.draw.ellipse(surface, DARK_BROWN, (sr.right - 10, fy - 4, 8, 5))
        ey = sr.centery - 2 + bob
        pygame.draw.circle(surface, WHITE, (sr.x + 8, ey), 4)
        pygame.draw.circle(surface, WHITE, (sr.right - 8, ey), 4)
        px = 1 if self.direction > 0 else -1
        pygame.draw.circle(surface, BLACK, (sr.x + 8 + px, ey + 1), 2)
        pygame.draw.circle(surface, BLACK, (sr.right - 8 + px, ey + 1), 2)


# ---------------------------------------------------------------------------
# Powerup
# ---------------------------------------------------------------------------
class Powerup:
    RADIUS = 12
    def __init__(self, x, y, respawn_time=600):
        self.x, self.y = x, y
        self.rect = pygame.Rect(x - self.RADIUS, y - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)
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
        pygame.draw.circle(surface, tuple(max(0, min(255, int(c * 0.3 * pulse))) for c in SUN_YELLOW), (sx, sy), int(self.RADIUS * 2 * pulse))
        pygame.draw.circle(surface, lerp_color(SUN_YELLOW, WHITE, abs(math.sin(self.tick * 0.1))), (sx, sy), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (sx - 3, sy - 3), 4)
        font = pygame.font.SysFont("consolas", 9, bold=True)
        lbl = font.render("U", True, BLACK)
        surface.blit(lbl, (sx - lbl.get_width() // 2, sy - lbl.get_height() // 2))
        a = self.tick * 0.08
        pygame.draw.rect(surface, rainbow_color(self.tick, 0.15),
            (sx + int(math.cos(a) * (self.RADIUS + 6)) - 2, sy + int(math.sin(a) * (self.RADIUS + 6)) - 2, 4, 4))


# ---------------------------------------------------------------------------
# Background decoration cloud
# ---------------------------------------------------------------------------
class BgCloud:
    def __init__(self, x, y, size, drift=0.15):
        self.x = float(x); self.y = y; self.size = size; self.drift = drift

    def draw(self, surface, camera):
        sx = int(self.x - camera.offset_x * 0.2)
        sy = int(self.y - camera.offset_y * 0.15)
        if sx < -self.size * 4 or sx > SCREEN_WIDTH + self.size * 4: return
        s = self.size
        for ox, oy, r in [(0, 0, s), (s, 4, int(s * 0.8)), (-s, 4, int(s * 0.75)), (int(s * 1.8), 8, int(s * 0.6))]:
            pygame.draw.circle(surface, CLOUD_WHITE, (sx + ox, sy + oy), r)


# ---------------------------------------------------------------------------
# Level builder — redesigned to match level1_climb_map_v2.svg
#
# SVG coordinate space: 680 wide × 980 tall.
#   SVG y=900  → spawn (bottom)        → game world y ≈ 860
#   SVG y=84   → exit platform (top)   → game world y ≈ -2540
#
# The SVG uses two columns (left ≈ x140–160, right ≈ x420–460).
# In the game world we map those proportionally:
#   SVG x / 680 * game_width  where game_width ≈ 640 (0–640 visible range)
#
# Vertical scale: (900 - 84) = 816 SVG units → (860 - (-2540)) = 3400 game units
#   scale_y ≈ 3400 / 816 ≈ 4.17
#
# Conversion helpers (origin at SVG y=900 → game y=860):
#   game_x = svg_x / 680 * 640
#   game_y = 860 - (900 - svg_y) * 4.17
#
# Tier boundaries (game world y, approx):
#   Tier 1  staircase intro      y  860 →  140
#   Tier 2  glitch islands       y  140 → -740
#   Tier 3  moving platforms     y -740 →-1490
#   Tier 4  teleport + collapse  y-1490 →-2160
#   Tier 5  summit gauntlet      y-2160 →-2620
#   Exit door                    y      ≈-2640
# ---------------------------------------------------------------------------

# SVG → game coordinate helpers
_SVG_W  = 680
_SVG_H  = 980
_GAME_W = 640        # usable horizontal game space (x 0..640)
_SPAWN_SVG_Y = 900   # SVG y of spawn
_SPAWN_GAME_Y = 860  # game y of spawn
_SCALE_Y = 4.17      # vertical stretch factor

def _gx(svg_x):
    """Map SVG x to game x."""
    return int(svg_x / _SVG_W * _GAME_W)

def _gy(svg_y):
    """Map SVG y to game y (higher SVG y = lower in game = larger y)."""
    return int(_SPAWN_GAME_Y - (_SPAWN_SVG_Y - svg_y) * _SCALE_Y)

def _pw(svg_w):
    """Map SVG platform width to game width."""
    return max(80, int(svg_w / _SVG_W * _GAME_W))

# Standard platform height in game units
_PH = 26


def create_level_1():
    """
    Platform layout verified against physics:
      JUMP_VELOCITY = -15, GRAVITY = 0.6
      Max jump height = 187.5 px
      All vertical gaps capped at 120 px (well within safe margin).
      Bridge platforms inserted at every tier transition to fill gaps.
    """
    plats, cps, mons, pws = [], [], [], []

    # ══════════════════════════════════════════════════════════════════════
    # TIER 1 — Staircase intro
    # Stairs ascend left→right.  Each step is ~120 px above the last.
    # step1 y lowered from _gy(844)=626 to 648 so gap from spawn (768) = 120.
    # ══════════════════════════════════════════════════════════════════════

    # Wide spawn cloud
    plats.append(Platform(_gx(70),  768,        _pw(260), _PH + 2, PLAT_CLOUD))
    # Step 1 — lowered to y=648 (gap from spawn = 120 ✓)
    plats.append(Platform(_gx(100), 648,        _pw(100), _PH, PLAT_CLOUD))
    # Step 2 — y=530  (gap 118 ✓)
    plats.append(Platform(_gx(220), 530,        _pw(100), _PH, PLAT_CLOUD))
    # Step 3 — y=409  (gap 121 ✓)
    plats.append(Platform(_gx(340), 409,        _pw(100), _PH, PLAT_CLOUD))
    # Wide landing + CP1 — y=301  (gap 108 ✓)
    plats.append(Platform(_gx(460), 301,        _pw(110), _PH, PLAT_CLOUD))

    # Intro mushroom on spawn cloud
    mons.append(MushroomMonster(_gx(145), 768 - 28, _gx(90),  _gx(280), speed=1.0))

    # CP1 on top-right landing
    cps.append(Checkpoint(_gx(475), 301))

    # ── Bridge T1 → T2 ────────────────────────────────────────────────
    # landing y=301 → T2 safe_L y=84  gap=217 → 1 bridge at y=193 (gaps 108+109 ✓)
    plats.append(Platform(_gx(260), 193, _pw(110), _PH, PLAT_CLOUD))

    # ══════════════════════════════════════════════════════════════════════
    # TIER 2 — Glitch islands (alternating left / right, 108 px apart)
    # Path (bottom→top): safe_L(84)→gR2(-24)→gL2(-132)→safe_R(-240)→gL1(-349)→gR1(-457)
    # CP2 on glitch_L2, powerup centre
    # ══════════════════════════════════════════════════════════════════════

    # Left safe rest — y=84   (gap from bridge 193 = 109 ✓)
    plats.append(Platform(      _gx(140),  84,  _pw(140), _PH, PLAT_CLOUD))
    # Right glitch — y=-24  (gap 108 ✓)
    plats.append(GlitchPlatform(_gx(420), -24,  _pw(120), _PH, on_time=95,  off_time=60, offset=55))
    # Left glitch (CP2) — y=-132  (gap 108 ✓)
    plats.append(GlitchPlatform(_gx(140), -132, _pw(120), _PH, on_time=85,  off_time=65, offset=20))
    # Right safe rest — y=-240  (gap 108 ✓)
    plats.append(Platform(      _gx(420), -240, _pw(120), _PH, PLAT_CLOUD))
    # Left glitch — y=-349  (gap 109 ✓)
    plats.append(GlitchPlatform(_gx(140), -349, _pw(120), _PH, on_time=90,  off_time=70, offset=35))
    # Right glitch — y=-457  (gap 108 ✓)
    plats.append(GlitchPlatform(_gx(420), -457, _pw(120), _PH, on_time=100, off_time=65, offset=0))

    # Flying monster mid-tier
    mons.append(FlyingMonster(_gx(310), -200, _gx(100), _gx(560), speed=1.1, amplitude=35, color=(85, 119, 238)))
    # Mushroom on right safe rest
    mons.append(MushroomMonster(_gx(435), -240 - 28, _gx(420), _gx(520), speed=1.2))

    # CP2 on left glitch at y=-132
    cps.append(Checkpoint(_gx(160), -132))
    # Powerup centre between columns
    pws.append(Powerup(_gx(308), -290))

    # ── Bridge T2 → T3 ────────────────────────────────────────────────
    # gR1 y=-457 → T3 safe_L2 y=-682  gap=225 → 1 bridge at y=-569 (gaps 112+113 ✓)
    plats.append(Platform(_gx(260), -569, _pw(110), _PH, PLAT_CLOUD))

    # ══════════════════════════════════════════════════════════════════════
    # TIER 3 — Moving platform maze
    # Path: safe_L2(-682)→mRH(-791)→safe_L(-899)→mRV(-1008)→mLH(-1116)
    # CP3 on right fast H-mover, powerup centre
    # ══════════════════════════════════════════════════════════════════════

    # Left safe rest 2 — y=-682  (gap from bridge -569 = 113 ✓)
    plats.append(Platform(_gx(140), -682, _pw(130), _PH, PLAT_CLOUD))
    # Right H-mover — y=-791  (gap 109 ✓) — CP3 here
    plats.append(MovingPlatform(_gx(420), -791, _gx(560), -791, _pw(120), _PH, speed=1.6))
    # Left safe rest — y=-899  (gap 108 ✓)
    plats.append(Platform(      _gx(140), -899, _pw(110), _PH, PLAT_CLOUD))
    # Right V-mover — y=-1008  (gap 109 ✓)
    plats.append(MovingPlatform(_gx(420), -1008, _gx(420), -1086, _pw(120), _PH, speed=1.0))
    # Left H-mover — y=-1116  (gap 108 ✓)
    plats.append(MovingPlatform(_gx(140), -1116, _gx(320), -1116, _pw(120), _PH, speed=1.3))

    # Mushroom on left safe rest
    mons.append(MushroomMonster(_gx(148), -899 - 28, _gx(140), _gx(240), speed=1.4))
    # Spiky patrol near right mover
    mons.append(Monster(_gx(432), -791 - 26, _gx(420), _gx(530), speed=1.4, color=(255, 68, 51)))

    # CP3 on right H-mover
    cps.append(Checkpoint(_gx(440), -791))
    # Powerup centre
    pws.append(Powerup(_gx(308), -950))

    # ── Bridge T3 → T4 ────────────────────────────────────────────────
    # mLH y=-1116 → T4 safe_L y=-1291  gap=175 → 1 bridge at y=-1203 (gaps 87+88 ✓)
    plats.append(Platform(_gx(260), -1203, _pw(110), _PH, PLAT_CLOUD))

    # ══════════════════════════════════════════════════════════════════════
    # TIER 4 — Teleport + collapse chaos
    # Path: safe_L(-1291)→collR(-1391)→teleL(-1491)→gR(-1591)→collL(-1692)→teleR(-1792)
    # CP4 on left safe rest, powerup centre
    # ══════════════════════════════════════════════════════════════════════

    # Left safe rest — y=-1291  (gap from bridge -1203 = 88 ✓)  CP4 here
    plats.append(Platform(         _gx(150), -1291, _pw(130), _PH, PLAT_CLOUD))
    # Right collapse — y=-1391  (gap 100 ✓)
    plats.append(CollapsingPlatform(_gx(420), -1391, _pw(110), _PH, delay=40))
    # Left teleport — y=-1491  (gap 100 ✓)
    plats.append(TeleportPlatform(  _gx(140), -1491, _gx(240), -1400, _pw(110), _PH, interval=120))
    # Right glitch — y=-1591  (gap 100 ✓)
    plats.append(GlitchPlatform(    _gx(420), -1591, _pw(110), _PH, on_time=75, off_time=55, offset=0))
    # Left collapse — y=-1692  (gap 101 ✓)
    plats.append(CollapsingPlatform(_gx(140), -1692, _pw(110), _PH, delay=48))
    # Right teleport — y=-1792  (gap 100 ✓)
    plats.append(TeleportPlatform(  _gx(430), -1792, _gx(530), -1700, _pw(110), _PH, interval=140))

    # Flying monster mid-tier
    mons.append(FlyingMonster(_gx(308), -1540, _gx(80), _gx(560), speed=1.4, amplitude=45, color=(85, 119, 238)))
    # Spiky patrol on right collapse
    mons.append(Monster(_gx(432), -1391 - 26, _gx(420), _gx(520), speed=1.5, color=(255, 68, 51)))

    # CP4 on left safe rest
    cps.append(Checkpoint(_gx(165), -1291))
    # Powerup centre
    pws.append(Powerup(_gx(308), -1540))

    # ── Bridge T4 → T5 ────────────────────────────────────────────────
    # teleR y=-1792 → T5 teleL y=-2084  gap=292 → 2 bridges (gaps 97+97+98 ✓)
    plats.append(Platform(_gx(160), -1889, _pw(110), _PH, PLAT_CLOUD))
    plats.append(Platform(_gx(420), -1986, _pw(110), _PH, PLAT_CLOUD))

    # ══════════════════════════════════════════════════════════════════════
    # TIER 5 — Summit gauntlet (tight zigzag)
    # Path: teleL(-2084)→mR(-2184)→collL(-2275)→gR(-2367)→bridge(-2454)→exit(-2542)
    # CP5 on right glitch, powerup between platforms
    # ══════════════════════════════════════════════════════════════════════

    # Left teleport — y=-2084  (gap from bridge2 -1986 = 98 ✓)
    plats.append(TeleportPlatform(  _gx(150), -2084, _gx(250), -2010, _pw(110), _PH, interval=100))
    # Right fast mover — y=-2184  (gap 100 ✓)
    plats.append(MovingPlatform(    _gx(420), -2184, _gx(540), -2184, _pw(110), _PH, speed=1.9))
    # Left collapse — y=-2275  (gap 91 ✓)
    plats.append(CollapsingPlatform(_gx(160), -2275, _pw(100), _PH, delay=38))
    # Right glitch (CP5) — y=-2367  (gap 92 ✓)
    plats.append(GlitchPlatform(    _gx(420), -2367, _pw(100), _PH, on_time=70, off_time=55, offset=0))

    # ── Bridge T5 → exit ─────────────────────────────────────────────
    # gR y=-2367 → exit y=-2542  gap=175 → 1 bridge at y=-2454 (gaps 87+88 ✓)
    plats.append(Platform(_gx(255), -2454, _pw(110), _PH, PLAT_CLOUD))

    # Exit-approach platform — y=-2542  (gap 88 ✓)
    plats.append(Platform(_gx(255), -2542, _pw(130), _PH + 4, PLAT_CLOUD))

    # Flying monster pair
    mons.append(FlyingMonster(_gx(295), -2230, _gx(80), _gx(560), speed=1.6, amplitude=50, color=(85, 119, 238)))
    mons.append(MushroomMonster(_gx(268), -2542 - 28, _gx(255), _gx(370), speed=1.9))

    # CP5 on right glitch
    cps.append(Checkpoint(_gx(435), -2367))
    # Powerup between T5 platforms
    pws.append(Powerup(_gx(308), -2320))

    # ══════════════════════════════════════════════════════════════════════
    # EXIT DOOR — above exit platform
    # ══════════════════════════════════════════════════════════════════════
    exit_door = ExitDoor(_gx(295), -2620)

    return plats, cps, mons, pws, exit_door


LEVELS = [create_level_1]


# ---------------------------------------------------------------------------
# Background cloud decorations
# ---------------------------------------------------------------------------
def make_bg_clouds():
    clouds = []
    rng = random.Random(42)
    for _ in range(80):
        clouds.append(BgCloud(
            rng.randint(-200, 800),
            rng.randint(-3000, 900),
            rng.randint(28, 65),
            rng.uniform(0.05, 0.2),
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
        self.monsters  = []; self.powerups    = []
        self.exit_door = None
        self.player    = Player(100, 400)

        self.load_level(0)
        self.sfx.start_music(volume=self.music_volume)

    def load_level(self, index=0):
        (self.platforms, self.checkpoints, self.monsters,
         self.powerups, self.exit_door) = LEVELS[index % len(LEVELS)]()
        # Spawn player on the wide spawn cloud (left side, bottom)
        spawn_x = _gx(100)
        spawn_y = 768 - 40   # spawn platform top is y=768
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
            elif key in (pygame.K_UP,   pygame.K_w): self.settings_cursor = (self.settings_cursor - 1) % 4
            elif key in (pygame.K_DOWN, pygame.K_s): self.settings_cursor = (self.settings_cursor + 1) % 4
            elif key in (pygame.K_LEFT, pygame.K_a):
                if self.settings_cursor == 0:
                    self.music_volume = max(0.0, round(self.music_volume - 0.1, 1)); self._apply_volume()
            elif key in (pygame.K_RIGHT, pygame.K_d):
                if self.settings_cursor == 0:
                    self.music_volume = min(1.0, round(self.music_volume + 0.1, 1)); self._apply_volume()
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

        result = self.player.update(keys, self.platforms)
        if result == "jump": self.sfx.play("jump")
        if self.player.prev_unreal and not self.player.is_unreal: self.sfx.play("unreal_end")
        if self.player.alive: self.camera.update(self.player.rect)

        for cp in self.checkpoints:
            cp.update()
            if self.player.alive and cp.check(self.player): self.sfx.play("checkpoint")

        for mon in self.monsters:
            mon.update()
            coll = mon.check_collision(self.player)
            if coll == "kill_player":
                self._player_death_fx(); self.player.die(); self.sfx.play("death")
            elif coll == "kill_monster":
                self._monster_kill_fx(mon); mon.kill()
                self.player.kill_count += 1; self.sfx.play("monster_kill")
            elif coll == "stomp":
                self._stomp_fx(mon); mon.stomp()
                self.player.vel_y = STOMP_BOUNCE
                self.player.kill_count += 1; self.sfx.play("stomp")

        self.monsters = [m for m in self.monsters
                         if m.alive or (hasattr(m, 'squish_timer') and m.squish_timer > 0) or m.death_timer > 0]

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
        self.score_popups = [(x, y - 0.8, t, timer - 1, c)
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
            a = random.uniform(0, math.pi * 2); s = random.uniform(2, 7)
            self.particles.append(Particle(cx, cy, random.choice([SKY_MID, CYAN, WHITE, CLOUD_WHITE]),
                math.cos(a)*s, math.sin(a)*s, random.randint(25, 50), random.randint(3, 7), 0.15))
        for _ in range(8):
            self.particles.append(Particle(cx+random.randint(-10,10), cy+random.randint(-10,10),
                CLOUD_SHADOW, random.uniform(-3,3), random.uniform(-8,-2), 40, 6, 0.3))

    def _monster_kill_fx(self, mon):
        cx, cy = mon.rect.center
        self.camera.add_shake(8)
        self.rings.append(RingEffect(cx, cy, SUN_YELLOW, 80, 5, 3))
        self.flashes.append(FlashOverlay(YELLOW, 8, 80))
        for _ in range(25):
            a = random.uniform(0, math.pi*2); s = random.uniform(2, 6)
            self.particles.append(Particle(cx, cy, random.choice([RED, ORANGE, SUN_YELLOW, WHITE]),
                math.cos(a)*s, math.sin(a)*s, random.randint(20,40), random.randint(3,6), 0.1))
        self.score_popups.append((cx, cy - 20, "+100", 60, SUN_YELLOW))

    def _stomp_fx(self, mon):
        cx, cy = mon.rect.centerx, mon.rect.bottom
        self.camera.add_shake(5)
        self.rings.append(RingEffect(cx, cy, WHITE, 40, 4, 2))
        for _ in range(12):
            a = random.uniform(-math.pi, 0); s = random.uniform(1, 4)
            self.particles.append(Particle(cx, cy, random.choice([BROWN, MUSHROOM_RED, WHITE, DARK_BROWN]),
                math.cos(a)*s, math.sin(a)*s - 1, random.randint(15,30), random.randint(2,5), 0.15))
        self.score_popups.append((cx, cy - 25, "+50", 50, WHITE))

    def _powerup_fx(self, pw):
        cx, cy = pw.x, pw.y
        self.camera.add_shake(10)
        self.flashes.append(FlashOverlay(SUN_YELLOW, 20, 160))
        for i in range(3):
            self.rings.append(RingEffect(cx, cy, rainbow_color(self.tick + i*30), 100+i*40, 3+i, 4-i))
        for _ in range(40):
            a = random.uniform(0, math.pi*2); s = random.uniform(1, 5)
            self.particles.append(Particle(cx, cy, random.choice([SUN_YELLOW, YELLOW, WHITE, ORANGE]),
                math.cos(a)*s, math.sin(a)*s, random.randint(30,60), random.randint(2,6), 0.05))
        self.score_popups.append((cx, cy - 30, "UNREAL MODE!", 90, SUN_YELLOW))

    def _spawn_ambient(self):
        for plat in self.platforms:
            if isinstance(plat, GlitchPlatform) and plat.active and plat.alpha < 200:
                if random.random() < 0.25:
                    self.particles.append(Particle(
                        plat.rect.x + random.randint(0, plat.rect.width),
                        plat.rect.y + random.randint(0, plat.rect.height),
                        PLAT_GLITCH, random.uniform(-1,1), random.uniform(-2,0), 20))
            elif isinstance(plat, TeleportPlatform) and plat.flash > 0:
                for _ in range(4):
                    self.particles.append(Particle(
                        plat.rect.x + random.randint(0, plat.rect.width),
                        plat.rect.y + random.randint(0, plat.rect.height),
                        SUN_YELLOW, random.uniform(-3,3), random.uniform(-3,3), 15))

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

    # ── Drawing ──────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(DARK_BG)
        if   self.state == "playing":  self._draw_game()
        elif self.state == "settings": self._draw_game(); self._draw_settings()
        elif self.state == "win":      self._draw_win()
        pygame.display.flip()

    def _draw_background(self):
        # Sky gradient — deep blue at top (high altitude), light blue at bottom (low)
        # Match SVG palette: top #4A90C8 → bottom #D8EEF8
        band_colors = [
            (74,  144, 200),   # SVG #4A90C8  highest altitude
            (114, 174, 221),   # SVG #72AEDD
            (157, 203, 238),   # SVG #9DCBEE
            (190, 224, 245),   # SVG #BEE0F5
            (216, 238, 248),   # SVG #D8EEF8  lowest visible
        ]
        bands = len(band_colors)
        for i, col in enumerate(band_colors):
            pygame.draw.rect(self.screen, col,
                             (0, i * SCREEN_HEIGHT // bands, SCREEN_WIDTH, SCREEN_HEIGHT // bands + 2))

        # Sun fixed top-right (near exit — matches SVG)
        pulse = abs(math.sin(self.tick * 0.03)) * 6
        pygame.draw.circle(self.screen, SUN_ORANGE, (SCREEN_WIDTH - 110, 70), int(34 + pulse))
        pygame.draw.circle(self.screen, SUN_YELLOW, (SCREEN_WIDTH - 110, 70), 22)
        pygame.draw.circle(self.screen, WHITE,      (SCREEN_WIDTH - 122, 58), 9)

        # Stars (visible at high altitude — twinkle)
        stars = [(80, 20), (160, 35), (260, 15), (380, 28), (450, 12)]
        for sx, sy in stars:
            brightness = int(140 + 115 * abs(math.sin(self.tick * 0.04 + sx * 0.1)))
            # Only show when camera is high up (low offset_y means high altitude)
            alt_ratio = max(0.0, min(1.0, -self.camera.offset_y / 2000))
            if alt_ratio > 0.3:
                alpha = int(brightness * (alt_ratio - 0.3) / 0.7)
                star_col = (alpha, alpha, alpha)
                pygame.draw.circle(self.screen, star_col, (sx, sy), 2)

        # Parallax background clouds
        for c in self.bg_clouds:
            c.draw(self.screen, self.camera)

        # Altitude guide lines (subtle horizontal)
        oy = int(self.camera.offset_y * 0.1) % 90
        for y in range(0, SCREEN_HEIGHT + 90, 90):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y - oy), (SCREEN_WIDTH, y - oy))

    def _draw_game(self):
        self._draw_background()
        for p in self.platforms:    p.draw(self.screen, self.camera)
        for cp in self.checkpoints: cp.draw(self.screen, self.camera)
        for pw in self.powerups:    pw.draw(self.screen, self.camera, self.tick)
        self.exit_door.draw(self.screen, self.camera)
        for m in self.monsters:     m.draw(self.screen, self.camera, self.tick)
        for p in self.particles:    p.draw(self.screen, self.camera)
        for r in self.rings:        r.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.tick)
        for f in self.flashes:      f.draw(self.screen)

        for x, y, text, timer, color in self.score_popups:
            a = min(1.0, timer / 30)
            c = tuple(max(0, min(255, int(v * a))) for v in color)
            pos = self.camera.apply(pygame.Rect(int(x), int(y), 1, 1))
            surf = self.small_font.render(text, True, c)
            self.screen.blit(surf, surf.get_rect(center=(pos.x, pos.y)))

        # HUD
        t = self.level_time / FPS
        self.screen.blit(self.small_font.render(f"Time: {t:.1f}s", True, DARK_GRAY), (SCREEN_WIDTH - 150, 10))
        if self.player.kill_count > 0:
            self.screen.blit(self.small_font.render(f"Kills: {self.player.kill_count}", True, ORANGE), (SCREEN_WIDTH - 150, 30))

        # Altitude bar (left side)
        max_alt = 3400
        alt = max(0, min(max_alt, _gy(900) - self.player.rect.centery))
        ratio = alt / max_alt
        bh = 200; bx = 12; by = SCREEN_HEIGHT // 2 - bh // 2
        pygame.draw.rect(self.screen, DARK_GRAY, (bx, by, 10, bh), 1)
        fill_h = int(bh * ratio)
        pygame.draw.rect(self.screen, lerp_color(SKY_BOT, SUN_YELLOW, ratio),
                         (bx, by + bh - fill_h, 10, fill_h))
        self.screen.blit(self.tiny_font.render("ALT", True, DARK_GRAY), (bx - 2, by - 14))

        if self.player.is_unreal:
            rem = self.player.unreal_timer / FPS
            bw, bh2 = 160, 14; bx2 = SCREEN_WIDTH // 2 - 80; by2 = 12
            ratio2 = self.player.unreal_timer / UNREAL_DURATION
            pygame.draw.rect(self.screen, DARK_GRAY, (bx2 - 2, by2 - 2, bw + 4, bh2 + 4))
            for px_i in range(int(bw * ratio2)):
                pygame.draw.line(self.screen, rainbow_color(self.tick + px_i * 2, 0.3),
                                 (bx2 + px_i, by2), (bx2 + px_i, by2 + bh2))
            self.screen.blit(self.tiny_font.render(f"UNREAL  {rem:.1f}s", True, WHITE), (bx2 + 4, by2 + 1))
            pygame.draw.rect(self.screen, rainbow_color(self.tick, 0.15), (bx2 - 2, by2 - 2, bw + 4, bh2 + 4), 2)

        self.screen.blit(self.small_font.render("R-Respawn  ESC-Settings", True, CLOUD_SHADOW),
                         (10, SCREEN_HEIGHT - 22))

        if not self.player.alive:
            txt = self.font.render("Respawning...", True, RED)
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

    def _draw_settings(self):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); ov.fill(BLACK); ov.set_alpha(160)
        self.screen.blit(ov, (0, 0))
        self.screen.blit(self.font.render("SETTINGS", True, CYAN),
                         self.font.render("SETTINGS", True, CYAN).get_rect(center=(SCREEN_WIDTH//2, 160)))
        items = [f"Music Volume:  < {int(self.music_volume*100)}% >",
                 f"Mute Music:    {'ON' if self.music_muted else 'OFF'}",
                 "Resume Game", "Exit to Menu"]
        hints = ["(Left / Right to adjust)", "(Enter to toggle)", "(Enter)", "(Enter)"]
        for i, (item, hint) in enumerate(zip(items, hints)):
            y = 230 + i * 50; sel = i == self.settings_cursor
            color = SUN_YELLOW if sel else GRAY
            if sel:
                bar = pygame.Rect(SCREEN_WIDTH//2 - 200, y - 4, 400, 30)
                pygame.draw.rect(self.screen, (30, 50, 80), bar)
                pygame.draw.rect(self.screen, SUN_YELLOW, bar, 1)
                self.screen.blit(self.small_font.render(">", True, SUN_YELLOW), (SCREEN_WIDTH//2 - 190, y))
            self.screen.blit(self.small_font.render(item, True, color), (SCREEN_WIDTH//2 - 160, y))
            if sel:
                self.screen.blit(self.tiny_font.render(hint, True, (120, 140, 160)), (SCREEN_WIDTH//2 - 160, y + 20))
        bx = SCREEN_WIDTH//2 - 100; vy = 258
        pygame.draw.rect(self.screen, DARK_GRAY, (bx, vy, 200, 6))
        pygame.draw.rect(self.screen, CYAN if not self.music_muted else RED,
                         (bx, vy, int(200 * self.music_volume), 6))
        pygame.draw.rect(self.screen, WHITE, (bx, vy, 200, 6), 1)
        self.screen.blit(self.tiny_font.render("ESC to resume", True, (100,120,140)),
                         self.tiny_font.render("ESC to resume", True, (100,120,140)).get_rect(
                             center=(SCREEN_WIDTH//2, 480)))

    def _draw_win(self):
        for i in range(8):
            pygame.draw.rect(self.screen, lerp_color(SKY_TOP, SKY_BOT, i/7),
                             (0, i * SCREEN_HEIGHT//8, SCREEN_WIDTH, SCREEN_HEIGHT//8 + 2))
        wt = self.big_font.render("LEVEL COMPLETE!", True, SUN_YELLOW)
        self.screen.blit(wt, wt.get_rect(center=(SCREEN_WIDTH//2, 160)))
        t = self.level_time / FPS
        for surf, cy in [
            (self.font.render(f"Time: {t:.1f} seconds", True, WHITE), 250),
            (self.font.render(f"Monsters defeated: {self.player.kill_count}", True, ORANGE), 300),
            (self.small_font.render("Press ENTER or ESC to exit", True, WHITE), 400),
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