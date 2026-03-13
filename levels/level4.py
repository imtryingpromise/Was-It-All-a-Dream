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

# Colours
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
BLUE        = (50, 120, 255)
GRAY        = (140, 140, 140)
DARK_GRAY   = (80, 80, 80)
PURPLE      = (160, 50, 200)
RED         = (220, 50, 50)
GREEN       = (50, 200, 80)
YELLOW      = (255, 220, 50)
DARK_BG     = (18, 18, 30)
CYAN        = (0, 220, 255)
GRID_COLOR  = (25, 25, 40)
ORANGE      = (255, 160, 30)
MAGENTA     = (220, 40, 180)
GOLD        = (255, 200, 50)
BROWN       = (139, 90, 43)
DARK_BROWN  = (100, 60, 30)
MUSHROOM_RED = (200, 45, 45)

# Physics
GRAVITY        = 0.6
JUMP_VELOCITY  = -13
MOVE_SPEED     = 5
SPRINT_SPEED   = 8
MAX_FALL_SPEED = 15
DEATH_Y        = 800
STOMP_BOUNCE   = -10  # velocity given to player after stomping a mushroom

# Unreal Mode
UNREAL_DURATION    = 480  # 8 seconds at 60 fps
UNREAL_SPEED_BOOST = 2

# Rainbow colour table
RAINBOW = [
    (255, 60, 60), (255, 160, 40), (255, 240, 50),
    (80, 255, 80), (50, 200, 255), (120, 80, 255), (220, 50, 220),
]


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rainbow_color(tick, speed=0.05):
    idx = (tick * speed) % len(RAINBOW)
    i = int(idx)
    frac = idx - i
    return lerp_color(RAINBOW[i], RAINBOW[(i + 1) % len(RAINBOW)], frac)


# ---------------------------------------------------------------------------
# Sound Manager  –  placeholder paths, loads silently if files are missing
# ---------------------------------------------------------------------------
# Put your audio files in a "sounds" folder next to this script.
# Supported formats: .wav, .ogg, .mp3 (mp3 for music only)
#
# Expected files:
#   sounds/music_bg.ogg        – main background music (loops)
#   sounds/jump.wav            – player jumps
#   sounds/death.wav           – player dies
#   sounds/respawn.wav         – player respawns
#   sounds/stomp.wav           – stomping a mushroom monster
#   sounds/monster_kill.wav    – killing any monster (unreal mode hit)
#   sounds/powerup.wav         – picking up the unreal mode orb
#   sounds/unreal_end.wav      – unreal mode wears off
#   sounds/checkpoint.wav      – checkpoint activated
#   sounds/win.wav             – level complete
#
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

SOUND_FILES = {
    "jump":         "jump.wav",
    "death":        "death.wav",
    "respawn":      "respawn.wav",
    "stomp":        "stomp.wav",
    "monster_kill": "monster_kill.wav",
    "powerup":      "powerup.wav",
    "unreal_end":   "unreal_end.wav",
    "checkpoint":   "checkpoint.wav",
    "win":          "win.wav",
}

MUSIC_FILE = "assets/audio/Level4Music.mp3"


class SoundManager:
    """Loads sounds from SOUND_DIR.  Missing files are silently skipped."""

    def __init__(self):
        self.sounds: dict[str, pygame.mixer.Sound | None] = {}
        self.music_loaded = False

        for name, filename in SOUND_FILES.items():
            path = os.path.join(SOUND_DIR, filename)
            if os.path.isfile(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception:
                    self.sounds[name] = None
            else:
                self.sounds[name] = None

        # Background music
        music_path = MUSIC_FILE
        if os.path.isfile(music_path):
            try:
                pygame.mixer.music.load(music_path)
                self.music_loaded = True
            except Exception:
                pass

    def play(self, name: str):
        snd = self.sounds.get(name)
        if snd:
            snd.play()

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
        self.width = width
        self.height = height
        self.shake_amount = 0.0
        self.shake_x = 0
        self.shake_y = 0

    def update(self, target_rect):
        tx = target_rect.centerx - self.width // 3
        self.offset_x += (tx - self.offset_x) * 0.1
        ty = target_rect.centery - self.height // 2
        self.offset_y += (ty - self.offset_y) * 0.05
        self.offset_y = max(-200, min(self.offset_y, 200))
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
    def __init__(self, x, y, color, vel_x=0, vel_y=0, lifetime=30, size=4,
                 gravity=0.1, fade=True):
        self.x, self.y = float(x), float(y)
        self.color = color
        self.vel_x, self.vel_y = vel_x, vel_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.base_size = size
        self.gravity = gravity
        self.fade = fade

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surface, camera):
        alpha = self.lifetime / self.max_lifetime if self.fade else 1.0
        size = max(1, int(self.base_size * alpha))
        color = tuple(max(0, min(255, int(c * alpha))) for c in self.color)
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
        alpha = 1.0 - (self.radius / self.max_radius)
        color = tuple(max(0, min(255, int(c * alpha))) for c in self.color)
        w = max(1, int(self.width * alpha))
        pos = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        if 0 <= pos.x <= SCREEN_WIDTH and 0 <= pos.y <= SCREEN_HEIGHT:
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
        alpha = int(self.max_alpha * (self.timer / self.duration))
        self.surface.set_alpha(alpha)
        surface.blit(self.surface, (0, 0))


# ---------------------------------------------------------------------------
# Player
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
        self.unreal_timer = 0
        self.prev_unreal = False  # to detect when unreal ends
        self.kill_count = 0
        self.riding_platform = None  # the moving platform we're standing on

    @property
    def is_unreal(self):
        return self.unreal_timer > 0

    def activate_unreal(self):
        self.unreal_timer = UNREAL_DURATION

    def set_checkpoint(self, x, y):
        self.spawn_x = x
        self.spawn_y = y

    def die(self):
        if self.is_unreal:
            return
        self.alive = False
        self.respawn_timer = 50

    def respawn(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.vel_x = self.vel_y = 0
        self.alive = True
        self.on_ground = False
        self.unreal_timer = 0

    def update(self, keys, platforms):
        # Track unreal end
        self.prev_unreal = self.is_unreal

        if not self.alive:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawn()
            return

        if self.unreal_timer > 0:
            self.unreal_timer -= 1

        # ── Carry player with the platform BEFORE own movement ──
        if self.riding_platform is not None and hasattr(self.riding_platform, 'dx'):
            self.rect.x += self.riding_platform.dx
            self.rect.y += self.riding_platform.dy

        move = 0.0
        speed = SPRINT_SPEED if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else MOVE_SPEED
        if self.is_unreal:
            speed += UNREAL_SPEED_BOOST
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += speed
            self.facing_right = True

        if move:
            self.vel_x += (move - self.vel_x) * 0.3
        else:
            self.vel_x *= 0.75
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0

        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        jumped = False
        if self.on_ground and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.vel_y = JUMP_VELOCITY + (-2 if self.is_unreal else 0)
            self.on_ground = False
            self.riding_platform = None
            jumped = True

        # Horizontal collision
        self.rect.x += int(self.vel_x)
        for plat in platforms:
            if not plat.is_active():
                continue
            prect = plat.get_rect()
            if self.rect.colliderect(prect):
                # If our feet are near the platform top, we're standing
                # on it, not hitting its wall — skip horizontal push.
                if self.rect.bottom <= prect.top + 6:
                    continue
                if self.vel_x > 0:
                    self.rect.right = prect.left
                elif self.vel_x < 0:
                    self.rect.left = prect.right
                self.vel_x = 0

        # Vertical collision
        self.on_ground = False
        self.riding_platform = None
        vy_move = int(self.vel_y)
        # Guarantee at least 1px downward when gravity is active, so we
        # always re-detect the ground / moving platform beneath us.
        if self.vel_y > 0 and vy_move == 0:
            vy_move = 1
        self.rect.y += vy_move
        for plat in platforms:
            if not plat.is_active():
                continue
            prect = plat.get_rect()
            if self.rect.colliderect(prect):
                if self.vel_y > 0:
                    self.rect.bottom = prect.top
                    self.vel_y = 0
                    self.on_ground = True
                    if isinstance(plat, MovingPlatform):
                        self.riding_platform = plat
                    plat.on_player_land(self)
                elif self.vel_y < 0:
                    self.rect.top = prect.bottom
                    self.vel_y = 0

        if self.rect.top > DEATH_Y:
            self.alive = False
            self.respawn_timer = 50

        return "jump" if jumped else None

    def draw(self, surface, camera, tick):
        if not self.alive:
            return
        sr = camera.apply(self.rect)
        if self.is_unreal:
            body_color = rainbow_color(tick, 0.12)
            pygame.draw.rect(surface, body_color, sr)
            pulse = abs(math.sin(tick * 0.15)) * 0.5 + 0.5
            pygame.draw.rect(surface, lerp_color(GOLD, WHITE, pulse), sr.inflate(4, 4), 2)
            glow_size = 6 + int(4 * pulse)
            glow_c = tuple(max(0, min(255, int(c * 0.3))) for c in body_color)
            pygame.draw.rect(surface, glow_c, sr.inflate(glow_size, glow_size), 3)
        else:
            pygame.draw.rect(surface, BLUE, sr)
            pygame.draw.rect(surface, (90, 160, 255),
                             (sr.x + 2, sr.y + 2, sr.width - 4, 4))

        eye_y = sr.y + 10
        pupil = BLACK if not self.is_unreal else GOLD
        if self.facing_right:
            pygame.draw.rect(surface, WHITE, (sr.x + 16, eye_y, 7, 7))
            pygame.draw.rect(surface, pupil, (sr.x + 19, eye_y + 2, 4, 4))
        else:
            pygame.draw.rect(surface, WHITE, (sr.x + 5, eye_y, 7, 7))
            pygame.draw.rect(surface, pupil, (sr.x + 5, eye_y + 2, 4, 4))


# ---------------------------------------------------------------------------
# Platforms (unchanged from previous version – collapsed for brevity)
# ---------------------------------------------------------------------------
class Platform:
    def __init__(self, x, y, width, height, color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
    def is_active(self): return True
    def get_rect(self): return self.rect
    def on_player_land(self, player): pass
    def update(self): pass
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pygame.draw.rect(surface, self.color, sr)
        pygame.draw.rect(surface, tuple(min(c+35,255) for c in self.color),
                         (sr.x, sr.y, sr.width, 3))


class MovingPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, w, h, speed=1.5, color=None):
        super().__init__(x1, y1, w, h, color or (80, 180, 110))
        self.sx, self.sy = x1, y1
        self.ex, self.ey = x2, y2
        self.speed = speed; self.progress = 0.0; self.dir = 1
        self.dx = 0; self.dy = 0  # per-frame movement delta
    def update(self):
        old_x, old_y = self.rect.x, self.rect.y
        self.progress += self.speed * self.dir * 0.005
        if self.progress >= 1: self.progress = 1.0; self.dir = -1
        elif self.progress <= 0: self.progress = 0.0; self.dir = 1
        t = self.progress; s = t*t*(3-2*t)
        self.rect.x = int(self.sx + (self.ex-self.sx)*s)
        self.rect.y = int(self.sy + (self.ey-self.sy)*s)
        self.dx = self.rect.x - old_x
        self.dy = self.rect.y - old_y


class GlitchPlatform(Platform):
    def __init__(self, x, y, w, h, on_time=90, off_time=60, offset=0, color=None):
        super().__init__(x, y, w, h, color or PURPLE)
        self.base_color = self.color
        self.on_time = on_time; self.off_time = off_time
        self.timer = offset; self.active = True; self.alpha = 255
    def update(self):
        self.timer += 1
        cycle = self.on_time + self.off_time
        phase = self.timer % cycle
        if phase < self.on_time:
            self.active = True
            rem = self.on_time - phase
            if rem < 30:
                self.alpha = 128 + int(127*(rem/30))
                if rem < 15 and self.timer % 4 < 2: self.alpha = 70
            else: self.alpha = 255
        else:
            self.active = False
            off_e = phase - self.on_time
            self.alpha = 25 if off_e < self.off_time-20 else min(25+(off_e-(self.off_time-20))*6, 80)
    def is_active(self): return self.active
    def draw(self, surface, camera):
        if self.alpha <= 0: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH+10: return
        f = self.alpha/255
        c = tuple(max(0,min(255,int(v*f))) for v in self.base_color)
        pygame.draw.rect(surface, c, sr)
        if self.alpha > 80:
            for ix in range(0, sr.width, 8):
                if (self.timer+ix) % 12 < 6:
                    lc = tuple(min(v+40,255) for v in c)
                    pygame.draw.line(surface, lc, (sr.x+ix, sr.y), (sr.x+ix, sr.y+sr.height))


class TeleportPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, w, h, interval=120, color=None):
        super().__init__(x1, y1, w, h, color or (200,110,50))
        self.p1=(x1,y1); self.p2=(x2,y2)
        self.interval=interval; self.timer=0; self.at1=True; self.flash=0
    def update(self):
        self.timer += 1
        if self.flash > 0: self.flash -= 1
        if self.timer >= self.interval:
            self.timer=0; self.at1=not self.at1; self.flash=10
            self.rect.topleft = self.p1 if self.at1 else self.p2
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if not (sr.right<-10 or sr.left>SCREEN_WIDTH+10):
            pygame.draw.rect(surface, WHITE if self.flash>0 else self.color, sr)
            if self.interval-self.timer < 30 and self.timer%6<3:
                pygame.draw.rect(surface, YELLOW, sr, 2)
        gp = self.p2 if self.at1 else self.p1
        gr = camera.apply(pygame.Rect(*gp, self.rect.w, self.rect.h))
        pygame.draw.rect(surface, tuple(c//4 for c in self.color), gr)
        pygame.draw.rect(surface, tuple(c//2 for c in self.color), gr, 1)


class CollapsingPlatform(Platform):
    def __init__(self, x, y, w, h, delay=45, respawn_time=180, color=None):
        super().__init__(x, y, w, h, color or (180,80,80))
        self.base_color=self.color; self.oy=y; self.delay=delay
        self.respawn_time=respawn_time; self.stood=0; self.collapsed=False
        self.rc=0; self.shake=0
    def update(self):
        if self.collapsed:
            self.rc += 1
            if self.rc >= self.respawn_time:
                self.collapsed=False; self.rc=0; self.stood=0; self.rect.y=self.oy
        elif self.stood > 0:
            self.stood += 1; self.shake=(self.stood%4)-2
            if self.stood >= self.delay: self.collapsed=True; self.shake=0
    def is_active(self): return not self.collapsed
    def on_player_land(self, player):
        if not self.collapsed and self.stood==0: self.stood=1
    def draw(self, surface, camera):
        if self.collapsed: return
        dr = self.rect.copy(); dr.x += self.shake
        sr = camera.apply(dr)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        if self.stood > 0:
            r = min(self.stood/self.delay, 1.0)
            col = (min(255,int(self.base_color[0]+(255-self.base_color[0])*r)),
                   max(0,int(self.base_color[1]*(1-r))),
                   max(0,int(self.base_color[2]*(1-r))))
        else: col = self.base_color
        pygame.draw.rect(surface, col, sr)
        if self.stood > self.delay*0.5:
            pygame.draw.line(surface, BLACK, (sr.centerx-8,sr.y),(sr.centerx+4,sr.bottom),2)


# ---------------------------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------------------------
class Checkpoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y-50, 20, 50)
        self.spawn_x = x; self.spawn_y = y-60
        self.activated = False; self.glow = 0
    def update(self):
        if self.activated: self.glow = (self.glow+3) % 360
    def check(self, player):
        if not self.activated and player.rect.colliderect(self.rect):
            self.activated = True
            player.set_checkpoint(self.spawn_x, self.spawn_y)
            return True
        return False
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        c = GREEN if self.activated else DARK_GRAY
        pygame.draw.rect(surface, c, (sr.x+8, sr.y, 4, sr.height))
        pygame.draw.polygon(surface, c, [(sr.x+12,sr.y),(sr.x+12,sr.y+16),(sr.x+28,sr.y+8)])
        if self.activated:
            i = abs(math.sin(math.radians(self.glow)))*0.6+0.4
            pygame.draw.rect(surface, tuple(int(v*i) for v in GREEN), sr.inflate(6,6), 2)


# ---------------------------------------------------------------------------
# Exit door
# ---------------------------------------------------------------------------
class ExitDoor:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 70)
        self.pulse = 0
    def update(self): self.pulse = (self.pulse+3) % 360
    def check(self, player): return player.rect.colliderect(self.rect)
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        pygame.draw.rect(surface, DARK_GRAY, sr.inflate(10,10))
        p = abs(math.sin(math.radians(self.pulse)))
        pygame.draw.rect(surface, (int(40+180*p),int(200+55*p),int(40+80*p)), sr)
        pygame.draw.circle(surface, YELLOW, (sr.right-14, sr.centery), 5)
        font = pygame.font.SysFont("consolas", 14)
        surface.blit(font.render("EXIT", True, WHITE), (sr.x+7, sr.y+6))


# ---------------------------------------------------------------------------
# Monster – spiky patrol enemy (unchanged logic)
# ---------------------------------------------------------------------------
class Monster:
    WIDTH, HEIGHT = 26, 26
    def __init__(self, x, y, pl, pr, speed=1.5, color=None):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.pl, self.pr = pl, pr; self.speed = speed; self.dir = 1
        self.color = color or RED; self.alive = True; self.death_timer = 0
        self.bob = 0
    def update(self):
        if not self.alive: self.death_timer -= 1; return
        self.rect.x += int(self.speed*self.dir)
        if self.rect.x >= self.pr: self.rect.x=self.pr; self.dir=-1
        elif self.rect.x <= self.pl: self.rect.x=self.pl; self.dir=1
        self.bob += 0.12
    def kill(self):
        self.alive = False; self.death_timer = 1
    def check_collision(self, player):
        if not self.alive or not player.alive: return None
        if not self.rect.colliderect(player.rect): return None
        if player.is_unreal: return "kill_monster"
        return "kill_player"
    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr = camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        bo = int(math.sin(self.bob)*2)
        b = pygame.Rect(sr.x, sr.y+bo, sr.w, sr.h)
        pygame.draw.rect(surface, self.color, b)
        for sx in range(b.x+2, b.right-2, 6):
            pygame.draw.polygon(surface, self.color, [(sx,b.y),(sx+3,b.y-5),(sx+6,b.y)])
        ey = b.y+8
        pygame.draw.rect(surface, WHITE, (b.x+4,ey,6,5))
        pygame.draw.rect(surface, WHITE, (b.x+16,ey,6,5))
        pygame.draw.rect(surface, BLACK, (b.x+6,ey+2,3,3))
        pygame.draw.rect(surface, BLACK, (b.x+18,ey+2,3,3))
        pygame.draw.line(surface, BLACK, (b.x+3,ey-2),(b.x+10,ey),2)
        pygame.draw.line(surface, BLACK, (b.right-3,ey-2),(b.right-10,ey),2)


# ---------------------------------------------------------------------------
# Flying Monster
# ---------------------------------------------------------------------------
class FlyingMonster:
    WIDTH, HEIGHT = 30, 22
    def __init__(self, x, y, pl, pr, speed=1.2, amplitude=40, color=None):
        self.bx, self.by = float(x), y
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.pl, self.pr = pl, pr; self.speed = speed
        self.amplitude = amplitude; self.dir = 1
        self.color = color or MAGENTA; self.alive = True; self.death_timer = 0
        self.phase = random.uniform(0, math.pi*2); self.tick = 0
    def update(self):
        if not self.alive: self.death_timer -= 1; return
        self.tick += 1; self.bx += self.speed*self.dir
        if self.bx >= self.pr: self.bx=self.pr; self.dir=-1
        elif self.bx <= self.pl: self.bx=self.pl; self.dir=1
        self.rect.x = int(self.bx)
        self.rect.y = int(self.by + math.sin(self.tick*0.04+self.phase)*self.amplitude)
    def kill(self):
        self.alive = False; self.death_timer = 1
    def check_collision(self, player):
        if not self.alive or not player.alive: return None
        if not self.rect.colliderect(player.rect): return None
        if player.is_unreal: return "kill_monster"
        return "kill_player"
    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr = camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        pygame.draw.ellipse(surface, self.color, sr)
        wy = sr.centery-2+int(math.sin(tick*0.3)*3)
        pygame.draw.polygon(surface, self.color, [(sr.left,wy),(sr.left-10,wy-8),(sr.left+5,wy)])
        pygame.draw.polygon(surface, self.color, [(sr.right,wy),(sr.right+10,wy-8),(sr.right-5,wy)])
        ey = sr.y+6
        ex = sr.x+16 if self.dir>=0 else sr.x+8
        pygame.draw.rect(surface, WHITE, (ex,ey,6,5))
        pygame.draw.rect(surface, BLACK, (ex+2,ey+1,3,3))


# ---------------------------------------------------------------------------
# Mushroom Monster – Mario-style goomba
#   • Walks in a straight line back and forth
#   • Player stomps it from above → mushroom dies, player bounces
#   • Player touches from the side → player dies
#   • In Unreal Mode → always kills the mushroom on contact
# ---------------------------------------------------------------------------
class MushroomMonster:
    WIDTH, HEIGHT = 28, 28

    def __init__(self, x, y, patrol_left, patrol_right, speed=1.3):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.speed = speed
        self.direction = 1
        self.alive = True
        self.death_timer = 0
        self.squish_timer = 0   # brief squish animation before removal
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
            self.rect.x = self.patrol_right; self.direction = -1
        elif self.rect.x <= self.patrol_left:
            self.rect.x = self.patrol_left; self.direction = 1

    def kill(self):
        """Instant kill (Unreal Mode)."""
        self.alive = False
        self.death_timer = 1

    def stomp(self):
        """Squish animation then die."""
        self.squish_timer = 12  # ~0.2s flat animation

    def check_collision(self, player):
        """
        Returns:
          'stomp'        – player landed on top (mario stomp)
          'kill_monster' – player is in Unreal Mode
          'kill_player'  – side/bottom contact, player dies
          None           – no contact
        """
        if not self.alive or self.squish_timer > 0 or not player.alive:
            return None
        if not self.rect.colliderect(player.rect):
            return None

        if player.is_unreal:
            return "kill_monster"

        # Stomp check: player is falling and their feet are above the
        # mushroom's vertical midpoint
        if player.vel_y > 0 and player.rect.bottom <= self.rect.centery + 6:
            return "stomp"

        return "kill_player"

    def draw(self, surface, camera, tick):
        if not self.alive:
            return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
            return

        if self.squish_timer > 0:
            # Squished flat
            flat = pygame.Rect(sr.x - 4, sr.bottom - 8, sr.width + 8, 8)
            pygame.draw.rect(surface, BROWN, flat)
            pygame.draw.ellipse(surface, MUSHROOM_RED,
                                (flat.x, flat.y - 4, flat.width, 8))
            return

        # Walking bob
        bob = int(math.sin(self.tick * 0.2) * 1.5)

        # Stem (body)
        stem = pygame.Rect(sr.x + 4, sr.centery + bob, sr.width - 8, sr.height // 2)
        pygame.draw.rect(surface, BROWN, stem)

        # Cap (dome)
        cap_rect = pygame.Rect(sr.x - 2, sr.y + bob, sr.width + 4, sr.height // 2 + 4)
        pygame.draw.ellipse(surface, MUSHROOM_RED, cap_rect)

        # White spots on cap
        for sx, sy, r in [(cap_rect.x + 6, cap_rect.y + 5, 3),
                          (cap_rect.right - 8, cap_rect.y + 4, 3),
                          (cap_rect.centerx, cap_rect.y + 2, 2)]:
            pygame.draw.circle(surface, WHITE, (sx, sy + bob), r)

        # Feet
        foot_y = sr.bottom + bob
        pygame.draw.ellipse(surface, DARK_BROWN, (sr.x + 2, foot_y - 4, 8, 5))
        pygame.draw.ellipse(surface, DARK_BROWN, (sr.right - 10, foot_y - 4, 8, 5))

        # Eyes
        ey = sr.centery - 2 + bob
        pygame.draw.circle(surface, WHITE, (sr.x + 8, ey), 4)
        pygame.draw.circle(surface, WHITE, (sr.right - 8, ey), 4)
        # Pupils look in walk direction
        px_off = 1 if self.direction > 0 else -1
        pygame.draw.circle(surface, BLACK, (sr.x + 8 + px_off, ey + 1), 2)
        pygame.draw.circle(surface, BLACK, (sr.right - 8 + px_off, ey + 1), 2)


# ---------------------------------------------------------------------------
# Powerup – Unreal Mode orb
# ---------------------------------------------------------------------------
class Powerup:
    RADIUS = 12
    def __init__(self, x, y, respawn_time=600):
        self.x, self.y = x, y
        self.rect = pygame.Rect(x-self.RADIUS, y-self.RADIUS, self.RADIUS*2, self.RADIUS*2)
        self.collected = False; self.respawn_time = respawn_time
        self.rc = 0; self.tick = random.randint(0,360)
    def update(self):
        self.tick += 1
        if self.collected:
            self.rc += 1
            if self.rc >= self.respawn_time: self.collected=False; self.rc=0
    def check(self, player):
        if self.collected or not player.alive: return False
        if self.rect.colliderect(player.rect):
            self.collected=True; self.rc=0; return True
        return False
    def draw(self, surface, camera, tick):
        if self.collected: return
        bob = math.sin(self.tick*0.06)*5
        cx, cy = self.x, self.y+int(bob)
        pos = camera.apply(pygame.Rect(cx-1,cy-1,2,2))
        sx, sy = pos.x, pos.y
        if sx<-30 or sx>SCREEN_WIDTH+30: return
        pulse = abs(math.sin(self.tick*0.08))*0.4+0.6
        pygame.draw.circle(surface, tuple(max(0,min(255,int(c*0.3*pulse))) for c in GOLD),
                           (sx,sy), int(self.RADIUS*2*pulse))
        pygame.draw.circle(surface, lerp_color(GOLD, WHITE, abs(math.sin(self.tick*0.1))),
                           (sx,sy), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (sx-3,sy-3), 4)
        font = pygame.font.SysFont("consolas", 9, bold=True)
        lbl = font.render("U", True, BLACK)
        surface.blit(lbl, (sx-lbl.get_width()//2, sy-lbl.get_height()//2))
        a = self.tick*0.08
        pygame.draw.rect(surface, rainbow_color(self.tick,0.15),
                         (sx+int(math.cos(a)*(self.RADIUS+6))-2,
                          sy+int(math.sin(a)*(self.RADIUS+6))-2, 4, 4))


# ---------------------------------------------------------------------------
# Level builder
# ---------------------------------------------------------------------------
def create_level_1():
    plats, cps, mons, pws = [], [], [], []

    # ── Section 1 : Intro ─────────────────────────────────────────────────
    plats.append(Platform(0, 500, 400, 40))
    plats.append(Platform(500, 500, 160, 40))
    plats.append(Platform(760, 455, 160, 40))
    plats.append(Platform(1020, 410, 160, 40))
    plats.append(Platform(1270, 455, 200, 40))
    plats.append(Platform(1560, 500, 300, 40))

    # Easy mushroom on the intro platform – teaches stomping
    mons.append(MushroomMonster(200, 472, 50, 370, speed=1.0))
    # Spiky monster after the gap
    mons.append(Monster(1580, 474, 1560, 1830, speed=1.2))

    cps.append(Checkpoint(1610, 500))

    # ── Section 2 : Disappearing platforms ────────────────────────────────
    plats.append(Platform(1960, 460, 120, 30))
    plats.append(GlitchPlatform(2170, 420, 120, 30, on_time=100, off_time=70, offset=0))
    plats.append(GlitchPlatform(2390, 375, 120, 30, on_time=90, off_time=70, offset=40))
    plats.append(Platform(2610, 420, 100, 30))
    plats.append(GlitchPlatform(2800, 375, 130, 30, on_time=85, off_time=65, offset=20))
    plats.append(GlitchPlatform(3010, 330, 120, 30, on_time=100, off_time=55, offset=60))
    plats.append(Platform(3220, 375, 160, 30))

    mons.append(MushroomMonster(1970, 432, 1960, 2060, speed=1.1))
    mons.append(Monster(2620, 394, 2610, 2700, speed=1.0))
    mons.append(FlyingMonster(2400, 320, 2200, 2600, speed=0.8, amplitude=30))

    pws.append(Powerup(2000, 430))
    cps.append(Checkpoint(3250, 375))

    # ── Section 3 : Moving platforms ──────────────────────────────────────
    plats.append(MovingPlatform(3500, 400, 3700, 400, 120, 30, speed=1.2))
    plats.append(Platform(3850, 360, 100, 30))
    plats.append(MovingPlatform(4030, 320, 4030, 450, 120, 30, speed=1.0))
    plats.append(MovingPlatform(4250, 380, 4450, 380, 130, 30, speed=1.5))
    plats.append(Platform(4600, 420, 100, 30))
    plats.append(MovingPlatform(4770, 350, 4770, 240, 110, 30, speed=0.8))
    plats.append(MovingPlatform(4950, 290, 5150, 290, 120, 30, speed=1.3))
    plats.append(Platform(5300, 350, 200, 30))

    mons.append(Monster(3860, 334, 3850, 3940, speed=1.3))
    mons.append(MushroomMonster(4610, 392, 4600, 4690, speed=1.4))
    mons.append(FlyingMonster(4400, 300, 4250, 4550, speed=1.0, amplitude=35))

    pws.append(Powerup(4400, 340))
    cps.append(Checkpoint(5320, 350))

    # ── Section 4 : Glitch challenge ──────────────────────────────────────
    plats.append(TeleportPlatform(5550, 350, 5550, 250, 120, 30, interval=150))
    plats.append(CollapsingPlatform(5770, 300, 120, 30, delay=50))
    plats.append(GlitchPlatform(5980, 350, 110, 30, on_time=70, off_time=55, offset=0))
    plats.append(TeleportPlatform(6170, 300, 6260, 400, 120, 30, interval=120))
    plats.append(CollapsingPlatform(6440, 350, 100, 30, delay=42))
    plats.append(CollapsingPlatform(6610, 300, 100, 30, delay=42))
    plats.append(Platform(6790, 350, 120, 30))
    plats.append(TeleportPlatform(6980, 300, 6980, 400, 100, 30, interval=100))
    plats.append(Platform(7160, 350, 200, 40))

    mons.append(FlyingMonster(5800, 250, 5550, 6000, speed=1.3, amplitude=40))
    mons.append(MushroomMonster(6800, 322, 6790, 6900, speed=1.6))
    mons.append(FlyingMonster(6500, 260, 6400, 6700, speed=1.1, amplitude=35))

    pws.append(Powerup(6820, 310))
    cps.append(Checkpoint(7180, 350))

    # ── Section 5 : Final challenge ───────────────────────────────────────
    plats.append(GlitchPlatform(7460, 320, 100, 30, on_time=65, off_time=55, offset=0))
    plats.append(MovingPlatform(7640, 280, 7640, 390, 100, 30, speed=1.4))
    plats.append(CollapsingPlatform(7840, 320, 90, 30, delay=38))
    plats.append(GlitchPlatform(8010, 280, 100, 30, on_time=70, off_time=60, offset=30))
    plats.append(TeleportPlatform(8200, 320, 8280, 240, 110, 30, interval=100))
    plats.append(MovingPlatform(8440, 280, 8600, 280, 100, 30, speed=1.8))
    plats.append(CollapsingPlatform(8730, 320, 100, 30, delay=32))
    plats.append(GlitchPlatform(8900, 280, 110, 30, on_time=80, off_time=45, offset=10))
    plats.append(Platform(9060, 350, 220, 40))

    mons.append(FlyingMonster(7700, 240, 7500, 7900, speed=1.5, amplitude=45))
    mons.append(MushroomMonster(9080, 322, 9060, 9260, speed=1.8))
    mons.append(FlyingMonster(8500, 220, 8300, 8700, speed=1.4, amplitude=40))

    pws.append(Powerup(7500, 280))

    exit_door = ExitDoor(9130, 280)
    return plats, cps, mons, pws, exit_door


LEVELS = [create_level_1]


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        # Don't call pygame.init() – already initialised by main.py
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Glitch Runner")
        self.clock = pygame.time.Clock()

        self.font       = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font   = pygame.font.SysFont("consolas", 48)
        self.tiny_font  = pygame.font.SysFont("consolas", 12, bold=True)

        self.sfx = SoundManager()

        # State: playing | settings | win
        self.state = "playing"
        self.current_level = 0
        self.level_time = 0
        self.tick = 0
        self.win_timer = 0

        # Settings
        self.music_volume = 0.5
        self.music_muted = False
        self.settings_cursor = 0  # 0=volume, 1=mute, 2=resume, 3=exit

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles: list[Particle] = []
        self.rings: list[RingEffect] = []
        self.flashes: list[FlashOverlay] = []
        self.score_popups: list = []

        self.platforms: list[Platform] = []
        self.checkpoints: list[Checkpoint] = []
        self.monsters: list = []
        self.powerups: list[Powerup] = []
        self.exit_door: ExitDoor | None = None
        self.player = Player(100, 400)

        self.load_level(0)
        self.sfx.start_music(volume=self.music_volume)

    def load_level(self, index=0):
        builder = LEVELS[index % len(LEVELS)]
        (self.platforms, self.checkpoints, self.monsters,
         self.powerups, self.exit_door) = builder()
        self.player = Player(100, 400)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles.clear()
        self.rings.clear()
        self.flashes.clear()
        self.score_popups.clear()
        self.level_time = 0
        self.tick = 0
        self.win_timer = 0

    def _exit_to_menu(self):
        """Stop level4 music and return control to main.py's game loop."""
        self.sfx.stop_music()
        self.running = False

    def _apply_volume(self):
        """Push current volume / mute state to mixer."""
        vol = 0.0 if self.music_muted else self.music_volume
        pygame.mixer.music.set_volume(vol)

    # -- main loop -----------------------------------------------------------
    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._exit_to_menu()
                    return
                if event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            if not self.running:
                return

            if self.state == "playing":
                self._update()
            elif self.state == "win":
                self.win_timer += 1

            self._draw()
            self.clock.tick(FPS)

    def _handle_key(self, key):
        # ── Settings screen ──
        if self.state == "settings":
            if key == pygame.K_ESCAPE:
                self.state = "playing"  # resume
            elif key in (pygame.K_UP, pygame.K_w):
                self.settings_cursor = (self.settings_cursor - 1) % 4
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.settings_cursor = (self.settings_cursor + 1) % 4
            elif key in (pygame.K_LEFT, pygame.K_a):
                if self.settings_cursor == 0:  # volume down
                    self.music_volume = max(0.0, round(self.music_volume - 0.1, 1))
                    self._apply_volume()
            elif key in (pygame.K_RIGHT, pygame.K_d):
                if self.settings_cursor == 0:  # volume up
                    self.music_volume = min(1.0, round(self.music_volume + 0.1, 1))
                    self._apply_volume()
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.settings_cursor == 0:
                    pass  # volume – use left/right
                elif self.settings_cursor == 1:  # mute toggle
                    self.music_muted = not self.music_muted
                    self._apply_volume()
                elif self.settings_cursor == 2:  # resume
                    self.state = "playing"
                elif self.settings_cursor == 3:  # exit to menu
                    self._exit_to_menu()
            return

        # ── Win screen ──
        if self.state == "win":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._exit_to_menu()
            return

        # ── Playing ──
        if key == pygame.K_ESCAPE:
            self.state = "settings"
            self.settings_cursor = 2  # default to "Resume"
        elif key == pygame.K_r:
            self.player.unreal_timer = 0
            self.player.die()
            self.sfx.play("death")

    # -- update --------------------------------------------------------------
    def _update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()

        for plat in self.platforms:
            plat.update()

        result = self.player.update(keys, self.platforms)
        if result == "jump":
            self.sfx.play("jump")

        # Detect unreal mode ending
        if self.player.prev_unreal and not self.player.is_unreal:
            self.sfx.play("unreal_end")

        if self.player.alive:
            self.camera.update(self.player.rect)

        for cp in self.checkpoints:
            cp.update()
            if self.player.alive and cp.check(self.player):
                self.sfx.play("checkpoint")

        # Monsters (all types including mushrooms)
        for mon in self.monsters:
            mon.update()
            coll = mon.check_collision(self.player)
            if coll == "kill_player":
                self._player_death_fx()
                self.player.die()
                self.sfx.play("death")
            elif coll == "kill_monster":
                self._monster_kill_fx(mon)
                mon.kill()
                self.player.kill_count += 1
                self.sfx.play("monster_kill")
            elif coll == "stomp":
                self._stomp_fx(mon)
                mon.stomp()
                self.player.vel_y = STOMP_BOUNCE  # bounce up
                self.player.kill_count += 1
                self.sfx.play("stomp")

        self.monsters = [m for m in self.monsters
                         if m.alive or (hasattr(m, 'squish_timer') and m.squish_timer > 0)
                         or m.death_timer > 0]

        # Powerups
        for pw in self.powerups:
            pw.update()
            if pw.check(self.player):
                self._powerup_fx(pw)
                self.player.activate_unreal()
                self.sfx.play("powerup")

        # Exit door
        self.exit_door.update()
        if self.player.alive and self.exit_door.check(self.player):
            self.state = "win"
            self.sfx.play("win")
            self.sfx.stop_music()

        # Effects
        self.particles = [p for p in self.particles if p.update()]
        self.rings = [r for r in self.rings if r.update()]
        self.flashes = [f for f in self.flashes if f.update()]
        self.score_popups = [(x, y-0.8, t, timer-1, c)
                             for x, y, t, timer, c in self.score_popups if timer > 0]

        self._spawn_ambient_particles()

        # Respawn sound
        if not self.player.alive and self.player.respawn_timer == 1:
            self.sfx.play("respawn")

        self.level_time += 1

    # -- effects -------------------------------------------------------------
    def _player_death_fx(self):
        cx, cy = self.player.rect.centerx, self.player.rect.centery
        self.camera.add_shake(14)
        self.flashes.append(FlashOverlay(RED, duration=18, max_alpha=120))
        for _ in range(35):
            a = random.uniform(0, math.pi*2)
            s = random.uniform(2, 7)
            self.particles.append(Particle(
                cx, cy, random.choice([BLUE, CYAN, WHITE]),
                math.cos(a)*s, math.sin(a)*s,
                lifetime=random.randint(25,50), size=random.randint(3,7), gravity=0.15))
        for _ in range(8):
            self.particles.append(Particle(
                cx+random.randint(-10,10), cy+random.randint(-10,10), DARK_GRAY,
                random.uniform(-3,3), random.uniform(-8,-2),
                lifetime=40, size=6, gravity=0.3))

    def _monster_kill_fx(self, mon):
        cx, cy = mon.rect.centerx, mon.rect.centery
        self.camera.add_shake(8)
        self.rings.append(RingEffect(cx, cy, GOLD, max_radius=80, speed=5, width=3))
        self.flashes.append(FlashOverlay(YELLOW, duration=8, max_alpha=80))
        for _ in range(25):
            a = random.uniform(0, math.pi*2)
            s = random.uniform(2, 6)
            self.particles.append(Particle(
                cx, cy, random.choice([RED, ORANGE, YELLOW, WHITE]),
                math.cos(a)*s, math.sin(a)*s,
                lifetime=random.randint(20,40), size=random.randint(3,6), gravity=0.1))
        self.score_popups.append((cx, cy-20, "+100", 60, GOLD))

    def _stomp_fx(self, mon):
        """Satisfying Mario-style stomp effect."""
        cx, cy = mon.rect.centerx, mon.rect.bottom
        self.camera.add_shake(5)
        # Small white ring
        self.rings.append(RingEffect(cx, cy, WHITE, max_radius=40, speed=4, width=2))
        # Brown / mushroom-coloured poof
        for _ in range(12):
            a = random.uniform(-math.pi, 0)  # upward arc
            s = random.uniform(1, 4)
            self.particles.append(Particle(
                cx, cy, random.choice([BROWN, MUSHROOM_RED, WHITE, DARK_BROWN]),
                math.cos(a)*s, math.sin(a)*s - 1,
                lifetime=random.randint(15,30), size=random.randint(2,5), gravity=0.15))
        self.score_popups.append((cx, cy - 25, "+50", 50, WHITE))

    def _powerup_fx(self, pw):
        cx, cy = pw.x, pw.y
        self.camera.add_shake(10)
        self.flashes.append(FlashOverlay(GOLD, duration=20, max_alpha=160))
        for i in range(3):
            self.rings.append(RingEffect(cx, cy, rainbow_color(self.tick+i*30),
                                         max_radius=100+i*40, speed=3+i, width=4-i))
        for _ in range(40):
            a = random.uniform(0, math.pi*2)
            s = random.uniform(1, 5)
            self.particles.append(Particle(
                cx, cy, random.choice([GOLD, YELLOW, WHITE, ORANGE]),
                math.cos(a)*s, math.sin(a)*s,
                lifetime=random.randint(30,60), size=random.randint(2,6), gravity=0.05))
        self.score_popups.append((cx, cy-30, "UNREAL MODE!", 90, GOLD))

    def _spawn_ambient_particles(self):
        for plat in self.platforms:
            if isinstance(plat, GlitchPlatform) and plat.active and plat.alpha < 200:
                if random.random() < 0.25:
                    self.particles.append(Particle(
                        plat.rect.x+random.randint(0,plat.rect.width),
                        plat.rect.y+random.randint(0,plat.rect.height),
                        PURPLE, random.uniform(-1,1), random.uniform(-2,0), 20))
            elif isinstance(plat, TeleportPlatform) and plat.flash > 0:
                for _ in range(4):
                    self.particles.append(Particle(
                        plat.rect.x+random.randint(0,plat.rect.width),
                        plat.rect.y+random.randint(0,plat.rect.height),
                        YELLOW, random.uniform(-3,3), random.uniform(-3,3), 15))

        if not self.player.alive and self.player.respawn_timer == 49:
            self._player_death_fx()

        if self.player.alive and self.player.is_unreal:
            if self.tick % 2 == 0:
                self.particles.append(Particle(
                    self.player.rect.centerx+random.randint(-8,8),
                    self.player.rect.bottom+random.randint(-4,4),
                    rainbow_color(self.tick+random.randint(0,20)),
                    random.uniform(-0.5,0.5), random.uniform(-1.5,-0.3),
                    lifetime=random.randint(15,30), size=random.randint(3,6), gravity=0.02))
            if self.tick % 5 == 0:
                side = 1 if self.player.facing_right else -1
                self.particles.append(Particle(
                    self.player.rect.centerx-side*12,
                    self.player.rect.centery+random.randint(-10,10),
                    WHITE, -side*random.uniform(1,3), random.uniform(-1,1),
                    lifetime=15, size=3, gravity=0))

    # -- drawing -------------------------------------------------------------
    def _draw(self):
        self.screen.fill(DARK_BG)
        if self.state == "playing":
            self._draw_game()
        elif self.state == "settings":
            self._draw_game()  # game visible behind overlay
            self._draw_settings()
        elif self.state == "win":
            self._draw_win()
        pygame.display.flip()

    def _draw_background(self):
        ox = int(self.camera.offset_x*0.3) % 60
        oy = int(self.camera.offset_y*0.3) % 60
        bg = GRID_COLOR
        if self.player.is_unreal:
            p = abs(math.sin(self.tick*0.06))*0.5+0.5
            bg = lerp_color(GRID_COLOR, (40,30,60), p)
        for x in range(0, SCREEN_WIDTH+60, 60):
            pygame.draw.line(self.screen, bg, (x-ox,0), (x-ox,SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT+60, 60):
            pygame.draw.line(self.screen, bg, (0,y-oy), (SCREEN_WIDTH,y-oy))

    def _draw_game(self):
        self._draw_background()
        for plat in self.platforms: plat.draw(self.screen, self.camera)
        for cp in self.checkpoints: cp.draw(self.screen, self.camera)
        for pw in self.powerups: pw.draw(self.screen, self.camera, self.tick)
        self.exit_door.draw(self.screen, self.camera)
        for mon in self.monsters: mon.draw(self.screen, self.camera, self.tick)
        for p in self.particles: p.draw(self.screen, self.camera)
        for r in self.rings: r.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.tick)
        for f in self.flashes: f.draw(self.screen)

        # Score popups
        for x, y, text, timer, color in self.score_popups:
            alpha = min(1.0, timer/30)
            c = tuple(max(0,min(255,int(v*alpha))) for v in color)
            pos = self.camera.apply(pygame.Rect(int(x),int(y),1,1))
            surf = self.small_font.render(text, True, c)
            self.screen.blit(surf, surf.get_rect(center=(pos.x, pos.y)))

        # ── HUD ──
        t = self.level_time / FPS
        self.screen.blit(
            self.small_font.render(f"Time: {t:.1f}s", True, WHITE),
            (SCREEN_WIDTH-150, 10))

        if self.player.kill_count > 0:
            self.screen.blit(
                self.small_font.render(f"Kills: {self.player.kill_count}", True, ORANGE),
                (SCREEN_WIDTH-150, 30))

        if self.player.is_unreal:
            rem = self.player.unreal_timer / FPS
            bw, bh = 160, 14
            bx = SCREEN_WIDTH//2 - bw//2; by = 12
            ratio = self.player.unreal_timer / UNREAL_DURATION
            pygame.draw.rect(self.screen, DARK_GRAY, (bx-2,by-2,bw+4,bh+4))
            fw = int(bw*ratio)
            # Rainbow fill bar
            for px_i in range(fw):
                col = rainbow_color(self.tick+px_i*2, 0.3)
                pygame.draw.line(self.screen, col, (bx+px_i,by), (bx+px_i,by+bh))
            self.screen.blit(
                self.tiny_font.render(f"UNREAL  {rem:.1f}s", True, WHITE), (bx+4, by+1))
            pygame.draw.rect(self.screen, rainbow_color(self.tick,0.15),
                             (bx-2,by-2,bw+4,bh+4), 2)

        self.screen.blit(
            self.small_font.render("R-Respawn  ESC-Settings", True, (80,80,100)),
            (10, SCREEN_HEIGHT-22))

        if not self.player.alive:
            txt = self.font.render("Respawning...", True, RED)
            self.screen.blit(txt, txt.get_rect(
                center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

    def _draw_settings(self):
        """Semi-transparent pause / settings overlay."""
        # Dim overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(160)
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.font.render("SETTINGS", True, CYAN)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 160)))

        # Menu items
        items = [
            f"Music Volume:  < {int(self.music_volume * 100)}% >",
            f"Mute Music:    {'ON' if self.music_muted else 'OFF'}",
            "Resume Game",
            "Exit to Menu",
        ]
        hints = [
            "(Left / Right to adjust)",
            "(Enter to toggle)",
            "(Enter)",
            "(Enter)",
        ]

        for i, (item, hint) in enumerate(zip(items, hints)):
            y = 230 + i * 50
            selected = (i == self.settings_cursor)
            color = GOLD if selected else GRAY
            # Highlight bar
            if selected:
                bar = pygame.Rect(SCREEN_WIDTH//2 - 200, y - 4, 400, 30)
                pygame.draw.rect(self.screen, (40, 40, 60), bar)
                pygame.draw.rect(self.screen, GOLD, bar, 1)
                # Arrow indicator
                arrow = self.small_font.render(">", True, GOLD)
                self.screen.blit(arrow, (SCREEN_WIDTH//2 - 190, y))

            txt = self.small_font.render(item, True, color)
            self.screen.blit(txt, (SCREEN_WIDTH//2 - 160, y))

            if selected:
                ht = self.tiny_font.render(hint, True, (120, 120, 140))
                self.screen.blit(ht, (SCREEN_WIDTH//2 - 160, y + 20))

        # Volume bar visual
        bar_x = SCREEN_WIDTH//2 - 100
        bar_y = 230 + 0 * 50 + 30  # below the volume text when not selected
        # Always show it below the volume item area
        vbar_y = 256
        if self.settings_cursor == 0:
            vbar_y = 258
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, vbar_y, 200, 6))
        fill_w = int(200 * self.music_volume)
        pygame.draw.rect(self.screen, CYAN if not self.music_muted else RED,
                         (bar_x, vbar_y, fill_w, 6))
        pygame.draw.rect(self.screen, WHITE, (bar_x, vbar_y, 200, 6), 1)

        # Footer
        esc_txt = self.tiny_font.render("ESC to resume", True, (100, 100, 120))
        self.screen.blit(esc_txt, esc_txt.get_rect(center=(SCREEN_WIDTH//2, 480)))

    def _draw_win(self):
        self._draw_background()
        txt = self.big_font.render("LEVEL COMPLETE!", True, GREEN)
        self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, 160)))

        t = self.level_time / FPS
        time_s = self.font.render(f"Time: {t:.1f} seconds", True, YELLOW)
        self.screen.blit(time_s, time_s.get_rect(center=(SCREEN_WIDTH//2, 250)))

        kills_s = self.font.render(f"Monsters defeated: {self.player.kill_count}", True, ORANGE)
        self.screen.blit(kills_s, kills_s.get_rect(center=(SCREEN_WIDTH//2, 300)))

        hint_s = self.small_font.render("Press ENTER or ESC to exit", True, WHITE)
        self.screen.blit(hint_s, hint_s.get_rect(center=(SCREEN_WIDTH//2, 400)))


# ---------------------------------------------------------------------------
# Entry point – can be imported and called from an external menu
# ---------------------------------------------------------------------------
def launch_game():
    """Call this from your external menu to start the game."""
    # Stop whatever music main.py was playing
    pygame.mixer.music.stop()

    game = Game()
    game.run()

    # Restore main.py's window and music after level4 ends
    pygame.display.set_caption("Christmas Pixel Adventure")
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
