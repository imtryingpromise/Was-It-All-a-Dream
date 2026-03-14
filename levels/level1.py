"""
Level 1 — Section 1: Falling Platform Precision
================================================
Player spawns on a wide solid platform on the far left.
Must cross 6 narrow falling platforms (jump + dash each gap)
on a rising slope to reach the tall landing platform.
Santa on the landing platform activates Checkpoint 1.
"""

import pygame, math, random, os

# ── Constants ────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60

# Physics
GRAVITY        = 0.55
JUMP_VEL       = -14.5
MOVE_SPEED     = 5
SPRINT_SPEED   = 8
MAX_FALL       = 16
DASH_SPEED     = 22
DASH_FRAMES    = 10
DASH_COOLDOWN  = 28
WALL_SLIDE_VEL = 2.0   # max fall speed while wall-sliding

# Death Y — far below all platforms
DEATH_Y = 900

# Colours
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
SKY_TOP     = (160, 210, 255)
SKY_BOT     = (220, 240, 255)
GRAY        = (160, 170, 185)
DARK_GRAY   = ( 60,  70,  85)
RED         = (220,  50,  50)
ORANGE      = (255, 160,  30)
YELLOW      = (255, 220,  50)
GOLD        = (255, 200,  50)
XMAS_RED    = (200,  35,  35)
XMAS_GREEN  = ( 25, 140,  55)
XMAS_GOLD   = (255, 195,  40)
SNOW_WHITE  = (235, 245, 255)
BROWN       = (130,  85,  40)
DARK_BROWN  = ( 90,  55,  20)
CYAN        = ( 70, 210, 255)

# Platform colours
SOLID_COL   = ( 80,  90, 105)   # spawn + landing: dark solid
FALL_COL    = (220,  60,  60)   # falling: red outline, light fill
FALL_FILL   = (255, 220, 215)

# ── Helpers ──────────────────────────────────────────────────────────────────
def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def rainbow_color(tick, speed=0.07):
    cols = [(255,80,80),(255,170,60),(255,240,60),(80,240,100),(60,200,255),(130,100,255),(230,80,230)]
    idx = (tick * speed) % len(cols)
    i = int(idx)
    return lerp_color(cols[i], cols[(i+1) % len(cols)], idx - i)


# ── Sound ────────────────────────────────────────────────────────────────────
SOUND_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
MUSIC_FILE = os.path.join("assets", "audio", "Level1Music.mp3")

class SoundManager:
    SOUNDS = {
        "jump":       "jump.wav",
        "dash":       "jump.wav",
        "land":       "checkpoint.wav",
        "death":      "death.wav",
        "respawn":    "respawn.wav",
        "checkpoint": "checkpoint.wav",
        "shake":      "death.wav",
    }
    def __init__(self):
        self.sfx = {}
        self.music_loaded = False
        for name, fn in self.SOUNDS.items():
            path = os.path.join(SOUND_DIR, fn)
            try:
                self.sfx[name] = pygame.mixer.Sound(path) if os.path.isfile(path) else None
            except Exception:
                self.sfx[name] = None
        if os.path.isfile(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                self.music_loaded = True
            except Exception:
                pass

    def play(self, name):
        s = self.sfx.get(name)
        if s:
            s.play()

    def start_music(self, vol=0.5):
        if self.music_loaded:
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()


# ── Camera ───────────────────────────────────────────────────────────────────
class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.shake = 0.0
        self.sx = self.sy = 0

    def update(self, target):
        # Follow player horizontally (1/3 from left), gentle vertical follow
        tx = target.rect.centerx - SCREEN_WIDTH // 3
        ty = target.rect.centery - SCREEN_HEIGHT // 2
        self.x += (tx - self.x) * 0.10
        self.y += (ty - self.y) * 0.08
        # Clamp: never scroll left of world origin
        self.x = max(0, self.x)
        # Vertical: keep platforms visible
        self.y = max(-100, min(self.y, 300))
        if self.shake > 0.5:
            self.sx = random.randint(int(-self.shake), int(self.shake))
            self.sy = random.randint(int(-self.shake), int(self.shake))
            self.shake *= 0.82
        else:
            self.shake = 0; self.sx = self.sy = 0

    def apply(self, rect):
        return pygame.Rect(
            rect.x - int(self.x) + self.sx,
            rect.y - int(self.y) + self.sy,
            rect.width, rect.height
        )

    def add_shake(self, amt):
        self.shake = min(self.shake + amt, 18)


# ── Particles ────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color, vx=0.0, vy=0.0, life=30, size=4, grav=0.12):
        self.x, self.y = float(x), float(y)
        self.color = color
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.size = size
        self.grav = grav

    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += self.grav; self.life -= 1
        return self.life > 0

    def draw(self, surf, cam):
        a = self.life / self.max_life
        s = max(1, int(self.size * a))
        c = tuple(max(0, min(255, int(v * a))) for v in self.color)
        p = cam.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        pygame.draw.rect(surf, c, (p.x, p.y, s, s))


class FlashOverlay:
    def __init__(self, color=(255,255,255), dur=14, max_alpha=180):
        self.color = color; self.dur = dur; self.t = dur; self.max_alpha = max_alpha
        self.surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.surf.fill(color)
    def update(self): self.t -= 1; return self.t > 0
    def draw(self, surf):
        self.surf.set_alpha(int(self.max_alpha * self.t / self.dur))
        surf.blit(self.surf, (0, 0))


# ── Platforms ────────────────────────────────────────────────────────────────
class SolidPlatform:
    """Standard immovable solid platform."""
    def __init__(self, x, y, w, h=22):
        self.rect = pygame.Rect(x, y, w, h)

    def update(self): pass
    def is_solid(self): return True

    def draw(self, surf, cam, tick=0):
        sr = cam.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pygame.draw.rect(surf, SOLID_COL, sr, border_radius=4)
        hi = tuple(min(c + 40, 255) for c in SOLID_COL)
        pygame.draw.rect(surf, hi, (sr.x + 4, sr.y, sr.width - 8, 5), border_radius=3)


class FallingPlatform:
    """
    Narrow platform that shakes then falls when the player lands on it.
    States: idle → shaking → falling → gone
    """
    W = 120   # world-pixel width
    H = 18
    SHAKE_DUR   = 26   # frames of shaking (~0.43 s at 60 fps)
    FALL_GRAV   = 0.9  # acceleration while falling

    def __init__(self, x, y):
        self.orig_x = x
        self.orig_y = y
        self.rect   = pygame.Rect(x, y, self.W, self.H)
        self.state  = "idle"   # idle | shaking | falling | gone
        self.shake_t = 0
        self.fall_vy = 0.0
        self.tick    = 0

    def land(self):
        """Called when player first lands on this platform."""
        if self.state == "idle":
            self.state   = "shaking"
            self.shake_t = self.SHAKE_DUR

    def update(self):
        self.tick += 1
        if self.state == "shaking":
            self.shake_t -= 1
            if self.shake_t <= 0:
                self.state   = "falling"
                self.fall_vy = 0.0
        elif self.state == "falling":
            self.fall_vy += self.FALL_GRAV
            self.rect.y  += int(self.fall_vy)
            if self.rect.y > DEATH_Y + 200:
                self.state = "gone"

    def is_solid(self):
        return self.state in ("idle", "shaking")

    def shake_offset(self):
        if self.state != "shaking": return 0
        intensity = max(1, int(4 * self.shake_t / self.SHAKE_DUR))
        return random.randint(-intensity, intensity)

    def draw(self, surf, cam, tick=0):
        if self.state == "gone": return
        ox = self.shake_offset()
        dr = pygame.Rect(self.rect.x + ox, self.rect.y, self.rect.width, self.rect.height)
        sr = cam.apply(dr)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return

        # Fill + red outline
        pygame.draw.rect(surf, FALL_FILL, sr, border_radius=5)
        pygame.draw.rect(surf, FALL_COL,  sr, 3, border_radius=5)

        # Crack lines when shaking hard
        if self.state == "shaking" and self.shake_t < self.SHAKE_DUR * 0.5:
            crack_col = tuple(max(0, c - 60) for c in FALL_COL)
            mid = sr.centerx
            pygame.draw.line(surf, crack_col,
                             (mid - 10 + ox, sr.y + 4),
                             (mid + 6 + ox, sr.bottom - 4), 1)
            pygame.draw.line(surf, crack_col,
                             (mid + 8 + ox, sr.y + 3),
                             (mid - 4 + ox, sr.bottom - 4), 1)

        # Warning pulse glow when about to fall
        if self.state == "shaking":
            alpha = int(120 * (1.0 - self.shake_t / self.SHAKE_DUR) *
                        abs(math.sin(self.tick * 0.4)))
            glow = pygame.Surface((sr.width + 8, sr.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*FALL_COL, alpha),
                             (0, 0, sr.width + 8, sr.height + 8), border_radius=7)
            surf.blit(glow, (sr.x - 4, sr.y - 4))


# ── Santa Checkpoint ─────────────────────────────────────────────────────────
class SantaCheckpoint:
    """
    Santa stands on a platform. Touching the player activates the checkpoint.
    Draws a detailed Santa figure.
    """
    W, H = 36, 60

    def __init__(self, x, y):
        # x, y = bottom-centre of Santa's feet
        self.rect     = pygame.Rect(x - self.W // 2, y - self.H, self.W, self.H)
        self.spawn_x  = x - 14   # player respawn slightly left of Santa
        self.spawn_y  = y - 50
        self.active   = False
        self.glow_t   = 0
        self.bob_t    = random.uniform(0, math.pi * 2)

    def check(self, player):
        if not self.active and player.rect.colliderect(self.rect):
            self.active = True
            return True
        return False

    def update(self):
        if self.active:
            self.glow_t = (self.glow_t + 4) % 360

    def draw(self, surf, cam, tick):
        sr  = cam.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20: return

        bob = int(math.sin(tick * 0.04 + self.bob_t) * 2)
        bx, by = sr.x, sr.y + bob

        # ── Boots ──
        for bx2 in [bx + 4, bx + 20]:
            pygame.draw.rect(surf, DARK_BROWN, (bx2, by + 50, 12, 10), border_radius=3)

        # ── Legs / trousers ──
        pygame.draw.rect(surf, (50, 50, 60), (bx + 6, by + 38, 10, 16), border_radius=2)
        pygame.draw.rect(surf, (50, 50, 60), (bx + 20, by + 38, 10, 16), border_radius=2)

        # ── Coat body ──
        pygame.draw.rect(surf, XMAS_RED, (bx + 2, by + 22, 32, 22), border_radius=5)
        # Coat white trim bottom
        pygame.draw.rect(surf, SNOW_WHITE, (bx + 2, by + 40, 32, 5), border_radius=3)

        # ── Belt ──
        pygame.draw.rect(surf, (30, 30, 30), (bx + 2, by + 33, 32, 5))
        pygame.draw.rect(surf, XMAS_GOLD, (bx + 14, by + 32, 8, 7), border_radius=1)
        pygame.draw.rect(surf, (200, 160, 30), (bx + 15, by + 33, 6, 5), border_radius=1, width=1)

        # ── Arms ──
        pygame.draw.line(surf, XMAS_RED, (bx + 2, by + 26), (bx - 6, by + 36), 7)
        pygame.draw.line(surf, XMAS_RED, (bx + 34, by + 26), (bx + 42, by + 36), 7)
        # Gloved hands
        pygame.draw.circle(surf, (40, 80, 40), (bx - 6, by + 37), 5)
        pygame.draw.circle(surf, (40, 80, 40), (bx + 43, by + 37), 5)

        # ── Head ──
        pygame.draw.circle(surf, (235, 195, 160), (bx + 18, by + 16), 12)

        # ── Beard ──
        pygame.draw.ellipse(surf, SNOW_WHITE, (bx + 6, by + 20, 24, 14))
        pygame.draw.ellipse(surf, SNOW_WHITE, (bx + 8, by + 26, 20, 10))

        # ── Eyes ──
        pygame.draw.circle(surf, (40, 30, 20), (bx + 13, by + 13), 2)
        pygame.draw.circle(surf, (40, 30, 20), (bx + 23, by + 13), 2)
        # Rosy cheeks
        pygame.draw.circle(surf, (220, 130, 120), (bx + 10, by + 18), 3)
        pygame.draw.circle(surf, (220, 130, 120), (bx + 26, by + 18), 3)

        # ── Hat ──
        pygame.draw.rect(surf, XMAS_RED, (bx + 8, by - 4, 20, 18), border_radius=3)
        pygame.draw.rect(surf, SNOW_WHITE, (bx + 6, by + 10, 24, 6), border_radius=3)
        # Pompom
        pygame.draw.circle(surf, SNOW_WHITE, (bx + 18, by - 5), 5)

        # ── CP label + glow ──
        if self.active:
            glow_a = int(80 + 60 * abs(math.sin(math.radians(self.glow_t))))
            gs = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*XMAS_GOLD, glow_a), (30, 30), 30)
            surf.blit(gs, (bx - 12, by - 10))
            font = pygame.font.SysFont("consolas", 13, bold=True)
            lbl  = font.render("CP1 ✓", True, XMAS_GOLD)
            surf.blit(lbl, (bx + 18 - lbl.get_width() // 2, by - 24))
        else:
            font = pygame.font.SysFont("consolas", 11)
            lbl  = font.render("[touch]", True, XMAS_GOLD)
            lbl.set_alpha(int(180 + 60 * abs(math.sin(tick * 0.05))))
            surf.blit(lbl, (bx + 18 - lbl.get_width() // 2, by - 20))


# ── Player ───────────────────────────────────────────────────────────────────
class Player:
    W, H = 28, 38
    INVINCIBLE_FRAMES = 80

    def __init__(self, x, y):
        self.rect        = pygame.Rect(x, y, self.W, self.H)
        self.vx          = 0.0
        self.vy          = 0.0
        self.on_ground   = False
        self.prev_ground = False
        self.facing_r    = True
        self.alive       = True
        self.respawn_t   = 0
        self.invinc      = 0
        self.spawn_x     = x
        self.spawn_y     = y
        # Jump
        self.jump_count  = 0
        self.max_jumps   = 2
        # Dash
        self.dash_t      = 0
        self.dash_cd     = 0
        self.dash_dir    = 1
        self.dashing     = False
        # Wall
        self.wall_side   = 0     # -1 left, 0 none, 1 right
        self.wall_slide  = False
        # Squash/stretch
        self.squash_t    = 0
        # Afterimages
        self.afterimages = []    # [(x,y,alpha)]
        # Riding
        self.riding_plat = None

    def set_spawn(self, x, y):
        self.spawn_x = x
        self.spawn_y = y

    def die(self):
        if self.invinc > 0: return
        self.alive    = False
        self.respawn_t = 55

    def respawn(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.vx = self.vy  = 0
        self.alive         = True
        self.on_ground     = False
        self.jump_count    = 0
        self.dashing       = False
        self.dash_t        = 0
        self.dash_cd       = 0
        self.invinc        = self.INVINCIBLE_FRAMES
        self.afterimages   = []
        self.riding_plat   = None

    def start_dash(self):
        if self.dash_cd <= 0 and not self.dashing:
            self.dashing  = True
            self.dash_t   = DASH_FRAMES
            self.dash_cd  = DASH_COOLDOWN
            self.dash_dir = 1 if self.facing_r else -1
            self.vy       = 0

    def update(self, keys, platforms, sfx):
        if not self.alive:
            self.respawn_t -= 1
            if self.respawn_t <= 0:
                self.respawn()
                sfx.play("respawn")
            return

        if self.invinc  > 0: self.invinc  -= 1
        if self.dash_cd > 0: self.dash_cd -= 1
        if self.squash_t > 0: self.squash_t -= 1

        # ── Dashing ──────────────────────────────────────────────────
        if self.dashing:
            self.dash_t -= 1
            self.afterimages.append((self.rect.x, self.rect.y, 210))
            if len(self.afterimages) > 8: self.afterimages.pop(0)
            self.rect.x += DASH_SPEED * self.dash_dir
            self.vy = 0
            if self.dash_t <= 0:
                self.dashing = False
                self.vx = MOVE_SPEED * self.dash_dir * 0.6
            # Dash collisions (horizontal only)
            for plat in platforms:
                if not plat.is_solid(): continue
                pr = plat.rect
                if self.rect.colliderect(pr):
                    if self.dash_dir > 0: self.rect.right = pr.left
                    else:                 self.rect.left  = pr.right
                    self.dashing = False
            return
        self.afterimages = [(x,y,a-25) for x,y,a in self.afterimages if a > 25]

        # ── Horizontal input ─────────────────────────────────────────
        move = 0
        sprint = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed  = SPRINT_SPEED if sprint else MOVE_SPEED
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: move = -speed; self.facing_r = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move =  speed; self.facing_r = True

        accel = 0.3; fric = 0.75
        self.vx = self.vx + (move - self.vx) * accel if move else self.vx * fric
        if abs(self.vx) < 0.1: self.vx = 0

        # ── Gravity ──────────────────────────────────────────────────
        if self.wall_slide and self.vy > WALL_SLIDE_VEL:
            self.vy = WALL_SLIDE_VEL
        else:
            self.vy = min(self.vy + GRAVITY, MAX_FALL)

        # ── Horizontal movement + collision ──────────────────────────
        self.riding_plat = None
        self.rect.x += int(self.vx)
        touching_wall = 0
        for plat in platforms:
            if not plat.is_solid(): continue
            pr = plat.rect
            if self.rect.colliderect(pr):
                if self.rect.bottom <= pr.top + 6: continue
                if self.vx > 0:  self.rect.right = pr.left;  touching_wall =  1
                elif self.vx < 0: self.rect.left = pr.right; touching_wall = -1
                self.vx = 0

        # ── Vertical movement + collision ────────────────────────────
        self.prev_ground = self.on_ground
        self.on_ground   = False
        vy = int(self.vy) if int(self.vy) else (1 if self.vy > 0 else 0)
        self.rect.y += vy
        for plat in platforms:
            if not plat.is_solid(): continue
            pr = plat.rect
            if self.rect.colliderect(pr):
                if self.vy > 0:
                    self.rect.bottom = pr.top
                    self.vy          = 0
                    self.on_ground   = True
                    self.jump_count  = 0
                    if hasattr(plat, 'land'): plat.land()   # trigger falling plat
                elif self.vy < 0:
                    self.rect.top = pr.bottom
                    self.vy       = 0

        # ── Wall slide ───────────────────────────────────────────────
        pressing_into = ((touching_wall == 1  and (keys[pygame.K_RIGHT] or keys[pygame.K_d])) or
                         (touching_wall == -1 and (keys[pygame.K_LEFT]  or keys[pygame.K_a])))
        if not self.on_ground and self.vy > 0 and pressing_into and touching_wall:
            self.wall_slide = True
            self.wall_side  = touching_wall
            self.jump_count = 1
        else:
            self.wall_slide = False
            self.wall_side  = 0

        # Landing squash
        if self.on_ground and not self.prev_ground:
            self.squash_t = 7

        # Death fall
        if self.rect.top > DEATH_Y:
            self.die()
            sfx.play("death")

    def draw(self, surf, cam, tick):
        if not self.alive: return

        # Invincibility flicker
        if self.invinc > 0 and (self.invinc // 4) % 2 == 0: return

        # Afterimages (dash trail)
        for ax, ay, aa in self.afterimages:
            ar = cam.apply(pygame.Rect(ax, ay, self.W, self.H))
            s  = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            s.fill((80, 180, 255, int(aa * 0.4)))
            surf.blit(s, ar.topleft)

        sr = cam.apply(self.rect)

        # Squash / stretch
        if self.squash_t > 0:
            sq  = int(self.squash_t * 0.7)
            sr  = sr.inflate(sq * 2, -sq * 2)
            sr.bottom += sq
        elif self.vy < -3 and not self.on_ground:
            stretch = 5
            sr = sr.inflate(-4, stretch * 2)
            sr.bottom += stretch

        # Body — warm golden adventurer
        body_c = lerp_color((255, 170, 55), (255, 215, 100),
                            abs(math.sin(tick * 0.03)) * 0.25)
        pygame.draw.rect(surf, body_c, sr, border_radius=5)

        # Sun-lit right edge
        pygame.draw.rect(surf, (255, 235, 160),
                         (sr.right - 4, sr.y + 4, 3, sr.height - 8), border_radius=2)
        # Shadow left edge
        pygame.draw.rect(surf, (200, 125, 35),
                         (sr.x + 1, sr.y + 4, 3, sr.height - 8), border_radius=2)

        # Belt
        belt_y = sr.y + sr.height - 14
        pygame.draw.rect(surf, (70, 45, 15), (sr.x, belt_y, sr.width, 5))
        pygame.draw.rect(surf, XMAS_GOLD, (sr.centerx - 4, belt_y - 1, 8, 7), border_radius=1)

        # Hat
        ht = sr.y - 10
        tip_x = sr.centerx + (6 if self.facing_r else -6)
        hat_c = lerp_color((255, 185, 35), (255, 225, 90),
                           abs(math.sin(tick * 0.04)) * 0.4)
        pygame.draw.polygon(surf, hat_c,
            [(sr.x + 1, sr.y + 3), (sr.x + sr.width - 1, sr.y + 3),
             (sr.centerx + (4 if self.facing_r else -4), sr.y - 4),
             (tip_x, ht)])
        pygame.draw.rect(surf, (255, 248, 205), (sr.x - 1, sr.y, sr.width + 2, 5))
        pygame.draw.circle(surf, YELLOW, (tip_x, ht - 2), 2)

        # Face
        pygame.draw.rect(surf, (228, 192, 155),
                         (sr.x + 2, sr.y + 8, sr.width - 4, 12))
        ey = sr.y + 11
        pupil = BLACK
        if self.facing_r:
            pygame.draw.rect(surf, WHITE, (sr.x + 15, ey, 7, 6))
            pygame.draw.rect(surf, pupil,  (sr.x + 18, ey + 1, 4, 4))
        else:
            pygame.draw.rect(surf, WHITE, (sr.x + 6, ey, 7, 6))
            pygame.draw.rect(surf, pupil,  (sr.x + 6, ey + 1, 4, 4))
        pygame.draw.arc(surf, (170, 75, 55),
                        (sr.centerx - 3, ey + 5, 6, 4), 3.4, 6.0, 1)

        # Wall-slide sparks
        if self.wall_slide:
            wx = sr.left if self.wall_side == -1 else sr.right
            for i in range(4):
                sy2 = sr.y + 5 + i * 8 + random.randint(-1, 1)
                pygame.draw.line(surf, WHITE, (wx, sy2),
                                 (wx + random.randint(-3, 3),
                                  sy2 + random.randint(4, 8)), 1)

        # Dash cooldown pip
        if self.dash_cd > 0:
            ratio = 1.0 - self.dash_cd / DASH_COOLDOWN
            w = int(sr.width * ratio)
            pygame.draw.rect(surf, DARK_GRAY,
                             (sr.x, sr.bottom + 3, sr.width, 4), border_radius=2)
            pygame.draw.rect(surf, CYAN,
                             (sr.x, sr.bottom + 3, w, 4), border_radius=2)


# ── Background clouds ─────────────────────────────────────────────────────────
class BGCloud:
    def __init__(self, x, y, size, speed=0.08):
        self.x = float(x); self.y = y
        self.size = size; self.speed = speed

    def draw(self, surf, cam):
        sx = int(self.x - cam.x * self.speed)
        sy = int(self.y - cam.y * 0.04)
        s  = self.size
        for ox, oy, r in [(0,0,s),(s,6,int(s*.78)),(-s,6,int(s*.72)),(int(s*1.75),12,int(s*.55))]:
            if r < 3: continue
            pygame.draw.circle(surf, (255, 252, 242), (sx + ox, sy + oy), r)
            pygame.draw.circle(surf, (255, 248, 235), (sx + ox + r//3, sy + oy - r//3), max(1, r//5))


def make_bg_clouds():
    rng = random.Random(42)
    return [BGCloud(rng.randint(0, 3500), rng.randint(50, 350),
                    rng.randint(28, 65), rng.uniform(0.04, 0.18))
            for _ in range(60)]


# ── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(surf, player, cp1_active, cp2_active, tick, level_time, font_s, font_t):
    def shadow_text(font, text, color, x, y):
        surf.blit(font.render(text, True, (0,0,0)), (x+1, y+1))
        surf.blit(font.render(text, True, color),   (x,   y))

    t = level_time / FPS
    shadow_text(font_s, f"time: {t:.1f}s", SNOW_WHITE, 14, 12)

    # Dash bar
    if player.dash_cd > 0:
        ratio = 1.0 - player.dash_cd / DASH_COOLDOWN
        bx, by, bw, bh = 14, 34, 100, 8
        pygame.draw.rect(surf, DARK_GRAY, (bx, by, bw, bh), border_radius=3)
        pygame.draw.rect(surf, CYAN, (bx, by, int(bw * ratio), bh), border_radius=3)
        shadow_text(font_t, "DASH", CYAN, bx + bw + 6, by - 1)
    else:
        pygame.draw.rect(surf, CYAN, (14, 34, 100, 8), border_radius=3)
        shadow_text(font_t, "DASH ✓", CYAN, 120, 33)

    # CP indicators top right
    if cp2_active:
        pulse = abs(math.sin(tick * 0.07)) * 0.4 + 0.6
        c = tuple(int(v * pulse) for v in XMAS_GOLD)
        shadow_text(font_s, "CP1 ✓  CP2 ✓", c, SCREEN_WIDTH - 220, 12)
    elif cp1_active:
        pulse = abs(math.sin(tick * 0.07)) * 0.4 + 0.6
        c = tuple(int(v * pulse) for v in XMAS_GOLD)
        shadow_text(font_s, "CP1 ✓", c, SCREEN_WIDTH - 140, 12)

    # Controls hint (fades after 420 frames)
    if level_time < 420:
        a = min(255, int(255 * (1 - max(0, level_time - 300) / 120)))
        ctrl = pygame.font.SysFont("consolas", 12)
        hints = [
            "Arrow / WASD — move",
            "Space / W    — jump (x2 double jump, SPACE on turbine = release)",
            "Shift        — dash (mid-air)",
        ]
        for i, h in enumerate(hints):
            s = ctrl.render(h, True, (220, 235, 255))
            s.set_alpha(a)
            surf.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2,
                          SCREEN_HEIGHT - 80 + i * 18))

    if not player.alive:
        big = pygame.font.SysFont("consolas", 28, bold=True)
        txt = big.render("Respawning...", True, RED)
        txt.set_alpha(int(200 * abs(math.sin(tick * 0.12))))
        surf.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))


# ── Moving Platform (Section 2 purple dash platforms) ────────────────────────
class MovingPlatform:
    """
    Purple platform that starts moving right when the player first lands on it.
    Stops at x_max.
    """
    H = 18

    def __init__(self, x, y, w, speed=3.5, x_max=None):
        self.rect   = pygame.Rect(x, y, w, self.H)
        self.speed  = speed
        self.x_max  = x_max if x_max is not None else x + 600
        self.moving = False
        self.dx     = 0   # movement this frame (for player riding)
        self.orig_x = x
        self.tick   = 0

    def activate(self):
        self.moving = True

    def is_solid(self): return True

    def update(self):
        self.dx = 0
        self.tick += 1
        if self.moving and self.rect.x < self.x_max:
            self.dx = self.speed
            self.rect.x += int(self.dx)

    def draw(self, surf, cam, tick=0):
        sr = cam.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return

        # Purple fill
        col  = (220, 195, 255)
        bord = (130,  70, 220)
        pygame.draw.rect(surf, col,  sr, border_radius=6)
        pygame.draw.rect(surf, bord, sr, 3, border_radius=6)

        # Shimmer highlight on top
        pygame.draw.rect(surf, (240, 225, 255),
                         (sr.x + 6, sr.y + 2, sr.width - 12, 4), border_radius=3)

        # Moving chevrons (shows direction)
        if self.moving:
            chev_c = (160, 90, 240)
            for cx in range(sr.x + 10, sr.right - 8, 18):
                cy = sr.centery
                pygame.draw.polygon(surf, chev_c,
                    [(cx, cy - 4), (cx + 7, cy), (cx, cy + 4)])

        # Pulse glow when idle (waiting for player)
        if not self.moving:
            a = int(40 + 30 * abs(math.sin(tick * 0.06)))
            glow = pygame.Surface((sr.width + 8, sr.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (160, 80, 255, a),
                             (0, 0, sr.width + 8, sr.height + 8), border_radius=8)
            surf.blit(glow, (sr.x - 4, sr.y - 4))


# ── Turbine ───────────────────────────────────────────────────────────────────
class Turbine:
    """
    Rotates clockwise. 4 grab handles at top/right/bottom/left.
    Player jumps onto a handle → rides it → jumps off at top.
    """
    N_HANDLES = 4
    HANDLE_R  = 14    # grab zone radius
    ROT_SPEED = 1.2   # degrees per frame

    def __init__(self, cx, cy, radius=90):
        self.cx     = cx
        self.cy     = cy
        self.radius = radius
        self.angle  = 0.0          # degrees, 0 = top handle at 12 o'clock
        self.rider  = None         # Player if someone is riding
        self.ride_handle = -1      # which handle index player grabbed
        self.tick   = 0

    def handle_positions(self):
        """Returns list of (hx, hy) for each of the 4 handles."""
        positions = []
        for i in range(self.N_HANDLES):
            a = math.radians(self.angle + i * 90 - 90)  # -90 so 0=top
            hx = self.cx + int(math.cos(a) * self.radius)
            hy = self.cy + int(math.sin(a) * self.radius)
            positions.append((hx, hy))
        return positions

    def check_grab(self, player):
        """If player is near any handle and moving downward, grab it."""
        if self.rider: return
        positions = self.handle_positions()
        for i, (hx, hy) in enumerate(positions):
            pr = player.rect
            dist = math.hypot(pr.centerx - hx, pr.centery - hy)
            if dist < self.HANDLE_R + 16 and player.vy >= 0:
                self.rider       = player
                self.ride_handle = i
                player.vy        = 0
                player.vx        = 0
                break

    def release(self):
        """Player jumps off — give an upward velocity boost."""
        if not self.rider: return
        # Launch upward from current handle position
        positions = self.handle_positions()
        hx, hy    = positions[self.ride_handle]
        self.rider.rect.center = (hx, hy - 20)
        self.rider.vy          = JUMP_VEL * 1.1
        self.rider.vx          = 4.0
        self.rider.jump_count  = 1
        self.rider.on_ground   = False
        self.rider       = None
        self.ride_handle = -1

    def update(self):
        self.tick  += 1
        self.angle  = (self.angle + self.ROT_SPEED) % 360

        if self.rider:
            # Move player to ride handle position
            positions = self.handle_positions()
            hx, hy   = positions[self.ride_handle]
            self.rider.rect.centerx = hx
            self.rider.rect.centery = hy

    def draw(self, surf, cam, tick=0):
        # Centre in screen coords
        cp = cam.apply(pygame.Rect(self.cx, self.cy, 1, 1))
        cx, cy = cp.x, cp.y
        r  = self.radius
        if cx + r < -20 or cx - r > SCREEN_WIDTH + 20: return

        # Outer ring
        pygame.draw.circle(surf, (255, 165, 30), (cx, cy), r, 4)
        # Subtle inner fill
        pygame.draw.circle(surf, (255, 240, 200), (cx, cy), r - 4)
        pygame.draw.circle(surf, (255, 210, 120), (cx, cy), r, 2)

        # 4 arms
        positions = self.handle_positions()
        for hx, hy in positions:
            hp = cam.apply(pygame.Rect(hx, hy, 1, 1))
            pygame.draw.line(surf, (220, 140, 20), (cx, cy), (hp.x, hp.y), 5)
            pygame.draw.line(surf, (255, 200, 80), (cx, cy), (hp.x, hp.y), 2)

        # Hub
        pygame.draw.circle(surf, (255, 210, 50), (cx, cy), 12)
        pygame.draw.circle(surf, (200, 150, 10), (cx, cy), 12, 2)
        pygame.draw.circle(surf, (255, 240, 150), (cx, cy), 6)

        # 4 grab handles (purple dots)
        for i, (hx, hy) in enumerate(positions):
            hp = cam.apply(pygame.Rect(hx, hy, 1, 1))
            grabbed = (self.rider is not None and self.ride_handle == i)
            col  = (255, 220, 80)  if grabbed else (160, 60, 240)
            bcol = (200, 160, 20)  if grabbed else (100, 20, 180)
            pygame.draw.circle(surf, col,  (hp.x, hp.y), self.HANDLE_R)
            pygame.draw.circle(surf, bcol, (hp.x, hp.y), self.HANDLE_R, 2)
            # G label
            font = pygame.font.SysFont("consolas", 9, bold=True)
            lbl  = font.render("G", True, WHITE)
            surf.blit(lbl, (hp.x - lbl.get_width() // 2,
                            hp.y - lbl.get_height() // 2))

        # Rotation direction arrow (small arc)
        arrow_a = math.radians(self.angle - 30)
        ax = cx + int(math.cos(arrow_a) * (r + 16))
        ay = cy + int(math.sin(arrow_a) * (r + 16))
        pygame.draw.circle(surf, (255, 165, 30), (ax, ay), 4)


# ── Snowman (Section 2 enemy) ─────────────────────────────────────────────────
class Snowman:
    """
    Stands on left edge of CP2 platform.
    Fires snowballs leftward when activated.
    Defeated by player jumping on top.
    """
    W, H      = 38, 68
    FIRE_RATE = 90    # frames between shots
    SB_SPEED  = 5     # snowball horizontal speed (leftward)

    def __init__(self, x, y):
        # x,y = bottom-left of snowman feet
        self.rect      = pygame.Rect(x, y - self.H, self.W, self.H)
        self.alive     = True
        self.active    = False   # starts inactive; activated when player hits plat1
        self.fire_t    = 45      # offset so first shot comes quickly
        self.snowballs = []      # list of Snowball objects
        self.death_t   = 0
        self.squish_t  = 0
        self.tick      = 0

    def activate(self):
        self.active = True

    def check_stomp(self, player):
        """Returns True if player lands on top of snowman head."""
        if not self.alive or self.squish_t > 0: return False
        if not player.rect.colliderect(self.rect): return False
        # Player must be falling and feet near top of snowman
        if player.vy > 0 and player.rect.bottom <= self.rect.y + 20:
            return True
        return False

    def check_side_hit(self, player):
        """Returns True if player touches snowman from side/below."""
        if not self.alive or self.squish_t > 0: return False
        if not player.rect.colliderect(self.rect): return False
        if not (player.vy > 0 and player.rect.bottom <= self.rect.y + 20):
            return True
        return False

    def stomp(self):
        self.squish_t = 14

    def kill(self):
        self.alive   = False
        self.death_t = 30

    def update(self):
        self.tick += 1
        if not self.alive:
            self.death_t = max(0, self.death_t - 1)
            for sb in self.snowballs: sb.update()
            self.snowballs = [sb for sb in self.snowballs if sb.alive]
            return

        if self.squish_t > 0:
            self.squish_t -= 1
            if self.squish_t == 0:
                self.kill()
            return

        if self.active:
            self.fire_t -= 1
            if self.fire_t <= 0:
                self.fire_t = self.FIRE_RATE
                self._fire()

        for sb in self.snowballs: sb.update()
        self.snowballs = [sb for sb in self.snowballs if sb.alive]

    def _fire(self):
        # Fire leftward from snowman chest height
        sx = self.rect.x
        sy = self.rect.y + self.H // 2
        self.snowballs.append(Snowball(sx, sy, -self.SB_SPEED))

    def draw(self, surf, cam, tick):
        if not self.alive and self.death_t <= 0:
            for sb in self.snowballs: sb.draw(surf, cam)
            return

        # Draw snowballs first (behind snowman)
        for sb in self.snowballs: sb.draw(surf, cam)

        sr = cam.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20: return

        bx, by = sr.x, sr.y

        # Squish effect
        if self.squish_t > 0:
            ratio = self.squish_t / 14
            sh = max(8, int(sr.height * (1 - ratio * 0.7)))
            bx = sr.x - int(sr.width * ratio * 0.3)
            bw = sr.width + int(sr.width * ratio * 0.6)
            by = sr.bottom - sh
            # Flat squished body
            pygame.draw.ellipse(surf, (230, 245, 255), (bx, by, bw, sh))
            pygame.draw.ellipse(surf, (160, 180, 200), (bx, by, bw, sh), 2)
            return

        # ── Normal snowman: 3 spheres ──
        # Lower body
        pygame.draw.circle(surf, (235, 248, 255), (bx + 19, by + 52), 16)
        pygame.draw.circle(surf, (180, 200, 220), (bx + 19, by + 52), 16, 2)
        # Middle body
        pygame.draw.circle(surf, (240, 250, 255), (bx + 19, by + 32), 12)
        pygame.draw.circle(surf, (180, 200, 220), (bx + 19, by + 32), 12, 2)
        # Head
        pygame.draw.circle(surf, (245, 252, 255), (bx + 19, by + 16), 10)
        pygame.draw.circle(surf, (180, 200, 220), (bx + 19, by + 16), 10, 2)

        # Hat
        pygame.draw.rect(surf, (40, 40, 50),  (bx + 11, by + 2,  16, 14), border_radius=2)
        pygame.draw.rect(surf, (40, 40, 50),  (bx +  8, by + 12, 22,  4))
        pygame.draw.rect(surf, XMAS_RED,      (bx + 11, by + 7,  16,  5))   # hat band

        # Carrot nose (pointing LEFT — toward player)
        pygame.draw.polygon(surf, (255, 130, 0),
            [(bx + 9, by + 17), (bx, by + 15), (bx, by + 19)])

        # Coal eyes
        pygame.draw.circle(surf, (40,  40,  50), (bx + 15, by + 12), 2)
        pygame.draw.circle(surf, (40,  40,  50), (bx + 23, by + 12), 2)

        # Coal buttons
        for i in range(3):
            pygame.draw.circle(surf, (50, 50, 60),
                               (bx + 19, by + 26 + i * 7), 2)

        # Stick arms (left arm points toward player)
        pygame.draw.line(surf, BROWN,
            (bx + 7,  by + 32), (bx - 12, by + 25), 3)
        pygame.draw.line(surf, BROWN,
            (bx + 31, by + 32), (bx + 48, by + 25), 3)

        # Scarf
        pygame.draw.rect(surf, XMAS_RED,
            (bx + 8, by + 24, 22, 5), border_radius=2)
        pygame.draw.rect(surf, (180, 20, 20),
            (bx + 8, by + 24, 22, 5), 1, border_radius=2)

        # "Activated" warning pulse (red glow when firing)
        if self.active and self.fire_t < 20:
            a = int(100 * (1 - self.fire_t / 20) * abs(math.sin(tick * 0.5)))
            gs = pygame.Surface((sr.width + 16, sr.height + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (255, 60, 60, a),
                                (0, 0, sr.width + 16, sr.height + 16))
            surf.blit(gs, (sr.x - 8, sr.y - 8))


# ── Snowball ──────────────────────────────────────────────────────────────────
class Snowball:
    R = 10
    def __init__(self, x, y, vx):
        self.x    = float(x)
        self.y    = float(y)
        self.vx   = vx
        self.vy   = 0.0
        self.rect = pygame.Rect(int(x) - self.R, int(y) - self.R,
                                self.R * 2, self.R * 2)
        self.alive = True
        self.tick  = 0

    def update(self):
        self.vy  += 0.12   # slight gravity arc
        self.x   += self.vx
        self.y   += self.vy
        self.rect.center = (int(self.x), int(self.y))
        if self.x < -200 or self.x > 15000 or self.y > DEATH_Y:
            self.alive = False
        self.tick += 1

    def check_hit(self, player):
        if not self.alive or not player.alive: return False
        if self.rect.colliderect(player.rect):
            self.alive = False
            return True
        return False

    def draw(self, surf, cam):
        if not self.alive: return
        sr = cam.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20: return
        pygame.draw.circle(surf, SNOW_WHITE, sr.center, self.R)
        pygame.draw.circle(surf, (180, 210, 240), sr.center, self.R, 2)
        # Shadow dot
        pygame.draw.circle(surf, (160, 195, 225),
                           (sr.centerx + 2, sr.centery + 3), self.R - 4)


# ── Section 1 level data ──────────────────────────────────────────────────────
def build_section1():
    """
    Spawn platform  : x=100,  y=520, w=260
    Falling plat 1  : x=460,  y=508  (gap=100, plain jump from spawn)
    Falling plats 2–6: spaced 290 px apart (jump+dash each)
    Each platform rises 18 px
    Landing platform: x=2730, y=418, w=280 (tall solid block)
    Santa CP1       : centre of landing platform
    """
    SPAWN_Y  = 520
    PLAT_W   = 260
    GAP1     = 100
    DASH_GAP = 290
    RISE     = 18

    plats = []

    spawn_px = 100
    spawn_py = SPAWN_Y
    plats.append(SolidPlatform(spawn_px, spawn_py, PLAT_W, 28))

    fp_start_x = spawn_px + PLAT_W + GAP1
    fp_y       = SPAWN_Y - 12
    falling    = []
    for i in range(6):
        fx = fp_start_x + i * (FallingPlatform.W + DASH_GAP)
        fy = fp_y - i * RISE
        fp = FallingPlatform(fx, fy)
        plats.append(fp)
        falling.append(fp)

    last_fp   = falling[-1]
    land_x    = last_fp.rect.x + FallingPlatform.W + GAP1
    land_y    = last_fp.rect.y
    land_h    = SPAWN_Y - land_y + 200
    land_plat = SolidPlatform(land_x, land_y, 280, land_h)
    plats.append(land_plat)

    santa_x = land_x + 140
    santa_y = land_y
    santa   = SantaCheckpoint(santa_x, santa_y)

    spawn_x = spawn_px + 30
    spawn_y = spawn_py - 50

    return plats, falling, santa, spawn_x, spawn_y


# ── Section 2 level data ──────────────────────────────────────────────────────
def build_section2():
    """
    6 purple moving platforms  : dash+jump gap (290px) apart, slight rise 8px
    Turbine                    : one jump+dash from last platform
    CP2 platform               : right of turbine (wide)
    Snowman                    : left edge of CP2 (faces left, fires on activation)
    Santa CP2                  : right edge of CP2

    World coords (computed from S1 landing at x=2730, y=418):
      Plat 1 : x=3300, y=418
      Plat 6 : x=5300, y=378
      Turbine: cx=5740, cy=298, r=90
      CP2    : x=5890, y=378, w=420
    """
    S2_PLAT_W = 110
    S2_GAP    = 290     # jump + dash
    S2_RISE   = 8
    BASE_Y    = 418     # same as S1 landing platform top

    plats  = []
    movers = []

    start_x = 3300

    for i in range(6):
        px = start_x + i * (S2_PLAT_W + S2_GAP)
        py = BASE_Y - i * S2_RISE
        mp = MovingPlatform(px, py, S2_PLAT_W, speed=3.5,
                            x_max=px + 500)
        plats.append(mp)
        movers.append(mp)

    # Turbine
    turbine = Turbine(cx=5740, cy=298, radius=90)

    # CP2 platform (wide solid — snowman left edge, Santa right edge)
    CP2_X = 5890
    CP2_Y = 378
    CP2_W = 420
    CP2_H = 600
    cp2_plat = SolidPlatform(CP2_X, CP2_Y, CP2_W, CP2_H)
    plats.append(cp2_plat)

    # Snowman — left edge of CP2
    snowman = Snowman(CP2_X + 4, CP2_Y)

    # Santa CP2 — right edge of CP2
    santa2 = SantaCheckpoint(CP2_X + CP2_W - 40, CP2_Y)

    return plats, movers, turbine, snowman, santa2


# ── Game ──────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, screen):
        self.screen   = screen
        self.clock    = pygame.time.Clock()
        self.sfx      = SoundManager()
        self.font_s   = pygame.font.SysFont("consolas", 16)
        self.font_t   = pygame.font.SysFont("consolas", 12, bold=True)

        self.camera    = Camera()
        self.particles = []
        self.flashes   = []
        self.bg_clouds = make_bg_clouds()

        # ── Build both sections ──
        (s1_plats, self.falling_plats,
         self.santa1, spawn_x, spawn_y) = build_section1()

        (s2_plats, self.movers, self.turbine,
         self.snowman, self.santa2) = build_section2()

        # Combined platform list (player collides with all)
        self.platforms = s1_plats + s2_plats

        self.player     = Player(spawn_x, spawn_y)
        self.cp1_active = False
        self.cp2_active = False
        self.s2_triggered = False   # snowman + movers activate on plat1 land

        self.level_time = 0
        self.tick       = 0
        self.state      = "playing"
        self.win_timer  = 0

        self.sfx.start_music(vol=0.45)

    # ─────────────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    running = self._handle_key(event.key)
                    if not running: break

            if self.state == "playing":
                self._update()

            self._draw()
            self.clock.tick(FPS)

        self.sfx.stop_music()

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            return False

        if not self.player.alive:
            return True

        if self.state == "playing":
            if key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                # If riding turbine, release instead of jump
                if self.turbine.rider is self.player:
                    self.turbine.release()
                    self.sfx.play("jump")
                    self._release_fx()
                else:
                    self._do_jump()
            elif key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                if not self.player.on_ground and self.turbine.rider is not self.player:
                    self.player.start_dash()
                    self._dash_fx()
                    self.sfx.play("dash")

        if self.state in ("section_done", "win") and key in (pygame.K_RETURN, pygame.K_SPACE):
            return False

        return True

    def _do_jump(self):
        p = self.player
        if not p.alive: return
        if self.turbine.rider is p: return   # handled by release

        if p.wall_slide:
            # Wall jump
            p.vy        = JUMP_VEL * 0.92
            p.vx        = -p.wall_side * MOVE_SPEED * 2.2
            p.jump_count = 2
            p.wall_slide = False
            p.facing_r   = (p.wall_side < 0)
            self.sfx.play("jump")
            wx = p.rect.left if p.wall_side == -1 else p.rect.right
            for _ in range(6):
                self.particles.append(Particle(
                    wx, p.rect.centery + random.randint(-8, 8),
                    (180, 220, 255), -p.wall_side * random.uniform(1, 3),
                    random.uniform(-2, 1), 15, 3, 0.1))
        elif p.on_ground or p.jump_count < p.max_jumps:
            p.vy = JUMP_VEL
            if not p.on_ground:
                # Double jump puff
                for _ in range(5):
                    self.particles.append(Particle(
                        p.rect.centerx + random.randint(-6, 6),
                        p.rect.bottom,
                        (200, 230, 255), random.uniform(-1, 1),
                        random.uniform(-0.5, 0.5), 12, 2, 0.08))
            p.on_ground  = False
            p.jump_count += 1
            self.sfx.play("jump")

    def _dash_fx(self):
        p = self.player
        self.camera.add_shake(4)
        for _ in range(12):
            a = random.uniform(-math.pi / 4, math.pi / 4)
            s = random.uniform(3, 7)
            self.particles.append(Particle(
                p.rect.centerx, p.rect.centery,
                (80, 200, 255), math.cos(a) * s * p.dash_dir,
                math.sin(a) * s, random.randint(10, 22), random.randint(3, 6), 0.05))

    def _death_fx(self):
        p = self.player
        self.camera.add_shake(16)
        self.flashes.append(FlashOverlay((220, 50, 50), 16, 110))
        for _ in range(30):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(2, 7)
            self.particles.append(Particle(
                p.rect.centerx, p.rect.centery,
                random.choice([(255, 180, 80), (255, 240, 160), WHITE]),
                math.cos(a) * s, math.sin(a) * s,
                random.randint(25, 50), random.randint(3, 7), 0.15))

    def _land_fx(self):
        p = self.player
        for _ in range(8):
            self.particles.append(Particle(
                p.rect.centerx + random.randint(-12, 12), p.rect.bottom,
                (220, 235, 255), random.uniform(-2, 2),
                random.uniform(-1.5, -0.3), 18, random.randint(2, 4), 0.1))

    def _cp_fx(self, cx, cy, label="CP"):
        for _ in range(28):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(1, 4)
            self.particles.append(Particle(
                cx, cy,
                random.choice([XMAS_GOLD, WHITE, (255, 180, 200), SNOW_WHITE]),
                math.cos(a) * s, math.sin(a) * s, 40, 4, 0.04))
        self.flashes.append(FlashOverlay(XMAS_GOLD, 22, 80))

    def _release_fx(self):
        p = self.player
        self.camera.add_shake(5)
        for _ in range(16):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(2, 6)
            self.particles.append(Particle(
                p.rect.centerx, p.rect.centery,
                random.choice([XMAS_GOLD, (255, 200, 80), WHITE]),
                math.cos(a) * s, math.sin(a) * s, 25, 4, 0.08))

    def _stomp_fx(self, x, y):
        self.camera.add_shake(8)
        self.flashes.append(FlashOverlay((255, 220, 80), 12, 90))
        for _ in range(20):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(2, 6)
            self.particles.append(Particle(
                x, y,
                random.choice([SNOW_WHITE, WHITE, (180, 220, 255)]),
                math.cos(a) * s, math.sin(a) * s - 1,
                random.randint(20, 40), random.randint(3, 6), 0.1))

    # ─────────────────────────────────────────────────────────────────
    def _update(self):
        self.tick       += 1
        self.level_time += 1
        keys = pygame.key.get_pressed()

        prev_alive  = self.player.alive
        prev_ground = self.player.on_ground

        # ── S2: check if player landed on first mover to trigger snowman ──
        if not self.s2_triggered and self.movers:
            first_mover = self.movers[0]
            pr = self.player.rect
            if (pr.colliderect(first_mover.rect) and
                    self.player.on_ground and self.player.alive):
                self.s2_triggered = True
                self.snowman.activate()
                # Activate all movers
                for m in self.movers:
                    m.activate()

        # ── Update platforms ──
        for p in self.platforms:
            p.update()

        # ── Turbine ──
        self.turbine.update()
        # Check grab only when player is airborne near turbine
        if self.turbine.rider is None and not self.player.on_ground:
            self.turbine.check_grab(self.player)

        # ── Player ──
        if self.turbine.rider is self.player:
            # While riding: skip normal physics, turbine controls position
            self.player.vx = 0; self.player.vy = 0
        else:
            self.player.update(keys, self.platforms, self.sfx)

        # ── Riding moving platforms: carry player ──
        for m in self.movers:
            if (self.player.alive and self.player.on_ground and
                    self.player.rect.colliderect(m.rect) and
                    self.player.rect.bottom <= m.rect.top + 6):
                self.player.rect.x += m.dx

        # ── Snowman ──
        self.snowman.update()

        # Snowball hits player
        for sb in self.snowman.snowballs:
            if sb.check_hit(self.player) and self.player.alive:
                self.player.die()
                self._death_fx()
                self.sfx.play("death")

        # Snowman stomp
        if self.snowman.check_stomp(self.player):
            self.snowman.stomp()
            self.player.vy = JUMP_VEL * 0.85
            self.player.jump_count = 1
            self.player.on_ground  = False
            self._stomp_fx(self.snowman.rect.centerx,
                           self.snowman.rect.top)
            self.sfx.play("jump")
        elif self.snowman.check_side_hit(self.player):
            self.player.die()
            self._death_fx()
            self.sfx.play("death")

        # ── Death / landing effects ──
        if prev_alive and not self.player.alive:
            self._death_fx()
            self.sfx.play("death")
        if not prev_ground and self.player.on_ground and self.player.alive:
            self._land_fx()

        # Shaking platform sound
        for fp in self.falling_plats:
            if fp.state == "shaking" and fp.shake_t == fp.SHAKE_DUR - 1:
                self.sfx.play("shake")

        # ── Santa CP1 ──
        if not self.cp1_active and self.player.alive:
            self.santa1.update()
            if self.santa1.check(self.player):
                self.cp1_active = True
                self.player.set_spawn(self.santa1.spawn_x, self.santa1.spawn_y)
                self.sfx.play("checkpoint")
                self.camera.add_shake(5)
                self._cp_fx(self.santa1.rect.centerx, self.santa1.rect.centery,
                            label="CP1")

        # ── Santa CP2 ──
        if self.cp1_active and not self.cp2_active and self.player.alive:
            self.santa2.update()
            if self.santa2.check(self.player):
                self.cp2_active = True
                self.player.set_spawn(self.santa2.spawn_x, self.santa2.spawn_y)
                self.sfx.play("checkpoint")
                self.camera.add_shake(5)
                self._cp_fx(self.santa2.rect.centerx, self.santa2.rect.centery,
                            label="CP2")
                self.state     = "section_done"
                self.win_timer = 0

        # Camera
        if self.player.alive:
            self.camera.update(self.player.rect)

        # Particles
        self.particles = [p for p in self.particles if p.update()]
        self.flashes   = [f for f in self.flashes   if f.update()]

    # ─────────────────────────────────────────────────────────────────
    def _draw_background(self):
        # Gradient sky
        for y in range(0, SCREEN_HEIGHT, 2):
            t   = y / SCREEN_HEIGHT
            col = lerp_color(SKY_TOP, SKY_BOT, t)
            pygame.draw.rect(self.screen, col, (0, y, SCREEN_WIDTH, 2))

        # Sun
        sun_x, sun_y = SCREEN_WIDTH - 120, 65
        pulse = abs(math.sin(self.tick * 0.018)) * 7
        pygame.draw.circle(self.screen, (255, 168, 28), (sun_x, sun_y), int(36 + pulse))
        pygame.draw.circle(self.screen, (255, 218, 58), (sun_x, sun_y), int(22 + pulse * 0.5))
        pygame.draw.circle(self.screen, WHITE, (sun_x, sun_y), 9)

        # Parallax clouds
        for cloud in self.bg_clouds:
            cloud.draw(self.screen, self.camera)

    def _draw(self):
        self._draw_background()

        # Platforms
        for plat in self.platforms:
            plat.draw(self.screen, self.camera, self.tick)

        # Turbine
        self.turbine.draw(self.screen, self.camera, self.tick)

        # Particles (behind entities)
        for p in self.particles:
            p.draw(self.screen, self.camera)

        # Santas
        self.santa1.draw(self.screen, self.camera, self.tick)
        if self.cp1_active:
            self.santa2.draw(self.screen, self.camera, self.tick)

        # Snowman (only show once S2 is reachable)
        self.snowman.draw(self.screen, self.camera, self.tick)

        # Player
        self.player.draw(self.screen, self.camera, self.tick)

        # Flash overlays
        for f in self.flashes:
            f.draw(self.screen)

        # HUD
        draw_hud(self.screen, self.player,
                 self.cp1_active, self.cp2_active,
                 self.tick, self.level_time, self.font_s, self.font_t)

        # Section done banner
        if self.state == "section_done":
            self.win_timer += 1
            big = pygame.font.SysFont("consolas", 42, bold=True)
            sub = pygame.font.SysFont("consolas", 20)
            pulse = abs(math.sin(self.win_timer * 0.06)) * 0.4 + 0.6
            c = tuple(int(v * pulse) for v in XMAS_GOLD)
            section = "1" if not self.cp2_active else "2"
            txt = big.render(f"Section {section} Complete!", True, c)
            s2  = sub.render("Press ESC to exit", True, SNOW_WHITE)
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
            self.screen.blit(s2,  s2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

        pygame.display.flip()


# ── Entry point ───────────────────────────────────────────────────────────────
def launch_game():
    pygame.mixer.music.stop()
    pygame.event.clear()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sky Climber — Section 1")
    game = Game(screen)
    game.run()
    pygame.display.set_caption("Sky Climber")
    try:
        pygame.mixer.music.load(os.path.join("assets", "audio", "BackgroundMusic.mp3"))
        pygame.mixer.music.play(-1)
    except Exception:
        pass


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    launch_game()
    pygame.quit()