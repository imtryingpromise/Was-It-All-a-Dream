"""
Sky Climber — Level 1  (Christmas Morning Edition)
===================================================
CHANGES FROM ORIGINAL:
  1. Checkpoints sit ON their platform (y arg = platform_y)
  2. All platforms reduced 20-30px width for more precise jumping
  3. Single jump only (max_jumps=1, double-jump block removed)
  4. Stomp monsters respawn after player dies (stored as defs, rebuilt each respawn)
  5. SpikeTrap removed entirely
  6. Unreal Mode / Powerup removed entirely
  7. Slowdown fix: spatial culling in Player.update() + unified spike floor removed
"""

import pygame, math, random, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from player_sprites import init_player_sprite, draw_player_sprite
    _SPRITES_AVAILABLE = True
except ImportError:
    _SPRITES_AVAILABLE = False

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60

WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
SKY_DAWN     = (255, 200, 130)
SKY_MID      = (255, 230, 180)
SKY_TOP      = (140, 195, 255)
CLOUD_WHITE  = (255, 250, 240)
CLOUD_SHADOW = (220, 200, 180)
SUN_YELLOW   = (255, 230,  60)
SUN_ORANGE   = (255, 160,   0)
XMAS_RED     = (210,  40,  40)
XMAS_GREEN   = ( 30, 155,  60)
XMAS_DARK_GR = ( 20, 100,  35)
XMAS_GOLD    = (255, 200,  50)
CANDY_PINK   = (255, 140, 170)
SNOW_WHITE   = (240, 248, 255)
ICE_BLUE     = (160, 215, 245)
PLAT_CLOUD   = (240, 248, 235)
PLAT_MOVE    = (255, 235, 175)
PLAT_FALL    = (255, 150, 150)
PLAT_TELE    = (200, 140, 255)
PLAT_ICE     = (180, 232, 255)
PLAT_GLITCH  = (185, 145, 255)
RAINBOW_COLS = [(255,80,80),(255,170,60),(255,240,60),(80,240,100),(60,200,255),(130,100,255),(230,80,230)]
GRAY         = (160, 170, 185)
DARK_GRAY    = ( 70,  80,  95)
RED          = (220,  60,  60)
YELLOW       = (255, 220,  50)
ORANGE       = (255, 160,  30)
CYAN         = ( 80, 220, 255)
GOLD         = (255, 205,  50)
STAR_GOLD    = (255, 215,  80)
UPDRAFT_COL  = (180, 240, 255)
BROWN        = (139,  90,  43)
DARK_BROWN   = (100,  60,  30)
DARK_BG      = (255, 225, 150)

GRAVITY         =  0.6
JUMP_VELOCITY   = -14
MOVE_SPEED      =  5
SPRINT_SPEED    =  8
MAX_FALL_SPEED  = 15
DEATH_Y         = 700

PLAYER_MAX_HEARTS     = 3
INVINCIBILITY_FRAMES  = 90
DASH_SPEED            = 18
DASH_DURATION         = 8
DASH_COOLDOWN         = 45

DIFFICULTY = {
    # collapse_delay: frames before a landed-on platform falls
    #   easy=120f (2s), medium=60f (1s), hard=30f (0.5s)
    "easy":   {"plat_spd": 0.6,  "wind_f": 1.3, "collapse_delay": 120, "tp_interval": 190,
               "saw_spd": 0.5, "icicle_spd": 3},
    "medium": {"plat_spd": 0.9,  "wind_f": 1.8, "collapse_delay": 60,  "tp_interval": 150,
               "saw_spd": 0.8, "icicle_spd": 5},
    "hard":   {"plat_spd": 1.25, "wind_f": 2.4, "collapse_delay": 30,  "tp_interval": 110,
               "saw_spd": 1.1, "icicle_spd": 7},
}

STORY_DIALOGUES = {
    "intro": [
        ("Zephyr", "Easy now... you are asleep. Don't panic."),
        ("Zephyr", "I am Zephyr — a guide your sleeping mind created. And yes, it's Christmas morning out there."),
        ("Zephyr", "Your body is in bed. Warm, safe. But your mind is locked here in the First Realm until you break through."),
        ("Zephyr", "Four realms stand between you and waking up. This is the first — and the kindest."),
        ("Zephyr", "MOVE: Arrow keys or WASD. SPACE to jump. SHIFT to sprint."),
        ("Zephyr", "DASH: Press SHIFT while airborne to dash forward. Great for crossing gaps fast."),
        ("Zephyr", "WALL SLIDE & JUMP: Press into a wall while falling to slow down. Then SPACE to kick off."),
        ("Zephyr", "HEALTH: You have 3 hearts. Hazards take one and give you a moment of safety after."),
        ("Zephyr", "ICE PLATFORMS — slippery. WIND ZONES — sprint against them."),
        ("Zephyr", "STAR RINGS: Collect them for points."),
        ("Zephyr", "Press E near a guide to talk. ESC for settings. R to respawn."),
        ("Zephyr", "The Horizon Gate is at the far right. Run. Three more realms are waiting."),
    ],
    "cp1": [
        ("Nimbus", "Made it through the opening stretch! I am Nimbus."),
        ("Nimbus", "Your body is still tucked in bed. Christmas presents under the tree and everything."),
        ("Nimbus", "The ice section is ahead. Slippery platforms, a bit of wind. Sprint to clear the gaps."),
    ],
    "cp2": [
        ("Zephyr", "Two sections down. Moving platforms ahead — ride them, don't fight them."),
        ("Zephyr", "A shuriken patrols the gap. Time your jump to slip past it."),
    ],
    "cp3": [
        ("Zephyr", "Good. Ice tunnel ahead — wind pushes LEFT. Dash right to fight it on the landings."),
        ("Zephyr", "Kunai hang from the ceiling. Walk under them and they fall. Move quickly."),
    ],
    "cp4": [
        ("Solara", "I am Solara. Collapse and teleport chaos ahead."),
        ("Solara", "The collapsing tiles fall fast. Land and jump immediately — never stand still."),
    ],
    "cp5": [
        ("Solara", "One more push. The final zone mixes everything."),
        ("Solara", "The Gate is just ahead. Go."),
    ],
    "ending": [
        ("Zephyr",  "You cleared the First Realm. Well done, dreamer."),
        ("Nimbus",  "Horizon Gate is open. The Second Realm is already taking shape around you."),
        ("Solara",  "Three realms remain. Each one harder than the last. But you proved you can do this."),
        ("Zephyr",  "Go. The dream won't hold itself together much longer. Move."),
    ],
}

_BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUND_DIR  = os.path.join(_BASE_DIR, "assets", "audio")
MUSIC_FILE = os.path.join(_BASE_DIR, "assets", "audio", "Level1Music.mp3")

SOUND_FILES = {
    "jump":       "jump.wav",
    "death":      "death.wav",
    "respawn":    "respawn.wav",
    "hit":        "hit.wav",
    "stomp":      "stomp.wav",
    "checkpoint": "checkpoint.wav",
    "win":        "win.wav",
    "star":       "checkpoint.wav",
    "soul_rise":  "soul_rise.wav",
    "soul_land":  "soul_land.wav",
    "crumble":    "crumble.wav",
    "npc_talk":   "npc_talk.wav",
}

# Per-sound volume levels — keeps SFX under the music
SFX_VOLUMES = {
    "jump": 0.6, "death": 1.0, "hit": 0.8, "stomp": 0.7,
    "respawn": 0.7, "checkpoint": 1.0, "win": 1.0,
    "star": 0.35, "soul_rise": 0.7, "soul_land": 0.7,
    "dble": 0.8, "npc_talk": 1.0,
}

class SoundManager:
    def __init__(self):
        self.sounds = {}; self.music_loaded = False
        self._sfx_multiplier = 1.0
        for name, fn in SOUND_FILES.items():
            path = os.path.join(SOUND_DIR, fn)
            try:
                if os.path.isfile(path):
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(SFX_VOLUMES.get(name, 0.5))
                    self.sounds[name] = snd
                else:
                    self.sounds[name] = None
            except: self.sounds[name] = None
        if os.path.isfile(MUSIC_FILE):
            try: pygame.mixer.music.load(MUSIC_FILE); self.music_loaded = True
            except: pass
    def set_sfx_volume(self, multiplier):
        self._sfx_multiplier = multiplier
        for name, snd in self.sounds.items():
            if snd:
                snd.set_volume(SFX_VOLUMES.get(name, 0.5) * multiplier)
    def play(self, n):
        s = self.sounds.get(n)
        if s: s.play()
    def start_music(self, loops=-1, volume=0.5):
        if self.music_loaded: pygame.mixer.music.set_volume(volume); pygame.mixer.music.play(loops)
    def stop_music(self): pygame.mixer.music.stop()


class Camera:
    def __init__(self, w, h):
        self.offset_x = 0.0; self.offset_y = 0.0
        self.width = w; self.height = h
        self.shake_amount = 0.0; self.shake_x = self.shake_y = 0
    def update(self, r):
        self.offset_x += (r.centerx - self.width // 3 - self.offset_x) * 0.10
        ty = r.centery - self.height // 2
        self.offset_y += (ty - self.offset_y) * 0.07
        self.offset_y = max(-100, min(self.offset_y, 200))
        if self.shake_amount > 0.5:
            self.shake_x = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_y = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_amount *= 0.85
        else: self.shake_amount = 0; self.shake_x = self.shake_y = 0
    def add_shake(self, a): self.shake_amount = min(self.shake_amount + a, 20)
    def apply(self, rect):
        return pygame.Rect(rect.x - int(self.offset_x) + self.shake_x,
                           rect.y - int(self.offset_y) + self.shake_y,
                           rect.width, rect.height)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def rainbow_color(tick, speed=0.05):
    idx = (tick * speed) % len(RAINBOW_COLS); i = int(idx)
    return lerp_color(RAINBOW_COLS[i], RAINBOW_COLS[(i+1) % len(RAINBOW_COLS)], idx - i)

def xmas_cycle(tick, speed=0.05):
    cols = [XMAS_RED, XMAS_GOLD, XMAS_GREEN, WHITE, CANDY_PINK, XMAS_GOLD, XMAS_RED]
    idx = (tick * speed) % len(cols); i = int(idx)
    return lerp_color(cols[i], cols[(i+1) % len(cols)], idx - i)


class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, lifetime=30, size=4, gravity=0.1, fade=True):
        self.x, self.y = float(x), float(y); self.color = color
        self.vel_x, self.vel_y = vx, vy
        self.lifetime = self.max_lifetime = lifetime
        self.base_size = size; self.gravity = gravity; self.fade = fade
    def update(self):
        self.x += self.vel_x; self.y += self.vel_y
        self.vel_y += self.gravity; self.lifetime -= 1
        return self.lifetime > 0
    def draw(self, surface, camera):
        a  = self.lifetime / self.max_lifetime if self.fade else 1.0
        sz = max(1, int(self.base_size * a))
        c  = tuple(max(0, min(255, int(v * a))) for v in self.color)
        p  = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        pygame.draw.rect(surface, c, (p.x, p.y, sz, sz))


class BGCloud:
    def __init__(self, x, y, size, speed=0.1):
        self.x = float(x); self.y = y; self.size = size; self.speed = speed
    def draw(self, surface, camera):
        sx = int(self.x - camera.offset_x * self.speed)
        sy = int(self.y - camera.offset_y * 0.05)
        s  = self.size
        for ox, oy, r in [(0,0,s),(s,5,int(s*.8)),(-s,5,int(s*.75)),(int(s*1.8),10,int(s*.6))]:
            pygame.draw.circle(surface, (255, 252, 242), (sx+ox, sy+oy), r)
            if r > 8:
                pygame.draw.circle(surface, (255, 248, 235), (sx+ox+r//3, sy+oy-r//3), max(1, r//5))


class RingEffect:
    def __init__(self, x, y, color, max_radius=120, speed=4, width=4):
        self.x, self.y = x, y; self.color = color; self.radius = 0
        self.max_radius = max_radius; self.speed = speed; self.width = width
    def update(self): self.radius += self.speed; return self.radius < self.max_radius
    def draw(self, surface, camera):
        a = 1.0 - self.radius / self.max_radius
        c = tuple(max(0, min(255, int(v*a))) for v in self.color)
        w = max(1, int(self.width * a))
        p = camera.apply(pygame.Rect(int(self.x), int(self.y), 1, 1))
        if -50 < p.x < SCREEN_WIDTH+50 and -50 < p.y < SCREEN_HEIGHT+50:
            pygame.draw.circle(surface, c, (p.x, p.y), int(self.radius), w)


class FlashOverlay:
    def __init__(self, color, duration=15, max_alpha=180):
        self.color = color; self.duration = duration; self.timer = duration
        self.max_alpha = max_alpha
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.surface.fill(color)
    def update(self): self.timer -= 1; return self.timer > 0
    def draw(self, surface):
        self.surface.set_alpha(int(self.max_alpha * self.timer / self.duration))
        surface.blit(self.surface, (0, 0))


class DamageFlash:
    def __init__(self): self.timer = 20; self.max_timer = 20
    def update(self): self.timer -= 1; return self.timer > 0
    def draw(self, surface):
        a = int(150 * self.timer / self.max_timer)
        if a <= 0: return
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        t = 55
        for i in range(t):
            ia = max(0, int(a * (1 - i/t)))
            if ia > 0:
                pygame.draw.rect(s, (220, 30, 30, ia), (i, i, SCREEN_WIDTH-2*i, SCREEN_HEIGHT-2*i), 1)
        surface.blit(s, (0, 0))


class NPC:
    WIDTH, HEIGHT = 24, 40
    def __init__(self, x, y, dialogue_key, name="Zephyr"):
        self.rect = pygame.Rect(x, y - self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.dialogue_key = dialogue_key; self.name = name
        self.talked = False; self.bob = random.uniform(0, math.pi*2)
        self.proximity_shown = False
    def check_proximity(self, player):
        return (abs(player.rect.centerx - self.rect.centerx) < 70 and
                abs(player.rect.centery - self.rect.centery) < 70)
    def draw(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20: return
        bob = int(math.sin(tick * 0.04 + self.bob) * 2)
        bx, by = sr.x, sr.y + bob
        robe_c = ((120, 210, 170) if "Nimbus" in self.name else
                  (255, 200, 100) if "Solara" in self.name else
                  (140, 185, 235))
        robe_hi = tuple(min(c+35, 255) for c in robe_c)
        pygame.draw.polygon(surface, robe_c, [(bx+4,by+14),(bx+20,by+14),(bx+22,by+40),(bx,by+40)])
        pygame.draw.polygon(surface, robe_hi, [(bx+4,by+14),(bx+10,by+14),(bx+8,by+40),(bx,by+40)])
        pygame.draw.circle(surface, (235, 205, 175), (bx+12, by+10), 8)
        pygame.draw.arc(surface, robe_hi, (bx+2, by, 20, 18), 0.3, 2.8, 3)
        pygame.draw.circle(surface, WHITE, (bx+9, by+9), 2)
        pygame.draw.circle(surface, WHITE, (bx+15, by+9), 2)
        pygame.draw.circle(surface, (60, 40, 20), (bx+9, by+10), 1)
        pygame.draw.circle(surface, (60, 40, 20), (bx+15, by+10), 1)
        pygame.draw.arc(surface, (180, 80, 60), (bx+7, by+13, 10, 5), 3.5, 6.0, 1)
        pygame.draw.line(surface, (210, 185, 120), (bx+22, by+6), (bx+22, by+40), 2)
        pulse = abs(math.sin(tick * 0.06)) * 0.5 + 0.5
        orb_c = lerp_color((255, 220, 80), WHITE, pulse * 0.6)
        pygame.draw.circle(surface, orb_c, (bx+22, by+4), 5)
        pygame.draw.circle(surface, WHITE, (bx+21, by+3), 2)
        if not self.talked:
            font = pygame.font.SysFont("consolas", 10, bold=True)
            tag  = font.render(self.name, True, (255, 200, 60))
            surface.blit(tag, (bx+12-tag.get_width()//2, by-14))
            exc_pulse = abs(math.sin(tick * 0.12)) * 0.5 + 0.5
            exc_c = lerp_color((255, 200, 50), (255, 240, 120), exc_pulse)
            ef = pygame.font.SysFont("consolas", 13 + int(exc_pulse * 2), bold=True)
            exc = ef.render("!", True, exc_c)
            surface.blit(exc, (bx+12-exc.get_width()//2, by-27))
        if self.proximity_shown and not self.talked:
            font2 = pygame.font.SysFont("consolas", 11)
            prompt = font2.render("[E] Talk", True, (255, 240, 180))
            pw, ph = prompt.get_width() + 8, prompt.get_height() + 4
            px2, py2 = bx + 12 - pw // 2, by - 40
            pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pill.fill((255, 200, 50, 160))
            surface.blit(pill, (px2, py2))
            surface.blit(prompt, (px2+4, py2+2))


class DialogueBox:
    def __init__(self, dialogues):
        self.dialogues = dialogues; self.index = 0; self.active = True
        self.char_index = 0; self.char_speed = 1.5; self.char_timer = 0
        self.done_typing = False
    def advance(self):
        if not self.done_typing:
            self.char_index = len(self.dialogues[self.index][1]); self.done_typing = True
        else:
            self.index += 1; self.char_index = 0; self.char_timer = 0; self.done_typing = False
            if self.index >= len(self.dialogues): self.active = False
    def update(self):
        if not self.active or self.done_typing: return
        self.char_timer += self.char_speed
        full = self.dialogues[self.index][1]
        self.char_index = min(int(self.char_timer), len(full))
        if self.char_index >= len(full): self.done_typing = True
    def draw(self, surface, tick):
        if not self.active: return
        box_h = 130; box_y = SCREEN_HEIGHT - box_h - 20
        box = pygame.Rect(40, box_y, SCREEN_WIDTH - 80, box_h)
        bg = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
        r = 8; warm_bg = (60, 40, 15, 210)
        pygame.draw.rect(bg, warm_bg, (r, 0, box.width-2*r, box.height))
        pygame.draw.rect(bg, warm_bg, (0, r, box.width, box.height-2*r))
        for cx2, cy2 in [(r,r),(box.width-r,r),(r,box.height-r),(box.width-r,box.height-r)]:
            pygame.draw.circle(bg, warm_bg, (cx2, cy2), r)
        surface.blit(bg, box.topleft)
        pygame.draw.rect(surface, (255, 210, 80), box, 2, border_radius=8)
        for cx2, cy2 in [(box.left+4,box.top+4),(box.right-4,box.top+4),
                         (box.left+4,box.bottom-4),(box.right-4,box.bottom-4)]:
            pygame.draw.circle(surface, (255, 220, 80), (cx2, cy2), 5)
            pygame.draw.circle(surface, WHITE, (cx2-1, cy2-1), 1)
        speaker, text = self.dialogues[self.index]
        fn = pygame.font.SysFont("consolas", 17, bold=True)
        ft = pygame.font.SysFont("consolas", 14)
        if speaker:
            sc = (XMAS_GOLD if "Zephyr" in speaker else
                  XMAS_GREEN if "Nimbus" in speaker else
                  SUN_ORANGE if "Solara" in speaker else WHITE)
            ns = fn.render(speaker, True, sc)
            surface.blit(ns, (box.x+16, box.y+10))
            pygame.draw.line(surface, sc, (box.x+16,box.y+30), (box.x+16+ns.get_width(),box.y+30), 1)
            ty = box.y + 36
        else: ty = box.y + 14
        shown = text[:self.char_index]; words = shown.split(" ")
        line = ""; ly = ty; mw = box.width - 32
        for word in words:
            test = line + (" " if line else "") + word
            if ft.size(test)[0] > mw:
                surface.blit(ft.render(line, True, (255, 245, 210)), (box.x+16, ly)); ly += 20; line = word
            else: line = test
        if line: surface.blit(ft.render(line, True, (255, 245, 210)), (box.x+16, ly))
        if self.done_typing and (tick//20)%2==0:
            label = "[ENTER] Continue..." if self.index < len(self.dialogues)-1 else "[ENTER] Close"
            surface.blit(ft.render(label, True, GRAY), (box.right-ft.size(label)[0]-16, box.bottom-22))
        pg_f = pygame.font.SysFont("consolas", 11)
        surface.blit(pg_f.render(f"{self.index+1}/{len(self.dialogues)}", True, (60,60,70)), (box.x+16, box.bottom-18))


# ── Platforms ──────────────────────────────────────────────────────────────
class Platform:
    def __init__(self, x, y, w, h, color=None):
        self.rect = pygame.Rect(x, y, w, h); self.color = color or PLAT_CLOUD
    def is_active(self):         return True
    def get_rect(self):          return self.rect
    def on_player_land(self, p): pass
    def update(self):            pass
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH+10: return
        pygame.draw.rect(surface, self.color, sr, border_radius=10)
        hi = tuple(min(c+50, 255) for c in self.color)
        pygame.draw.rect(surface, hi, (sr.x+4, sr.y, sr.width-8, 5), border_radius=4)
        sun_edge = lerp_color(self.color, (255, 230, 120), 0.35)
        pygame.draw.rect(surface, sun_edge, (sr.right-5, sr.y+4, 4, sr.height-8), border_radius=3)
        shadow = lerp_color(self.color, (150, 170, 200), 0.3)
        pygame.draw.rect(surface, shadow, (sr.x+1, sr.y+4, 4, sr.height-8), border_radius=3)
        rng = random.Random(sr.x * 31 + sr.y * 17)
        for bx in range(sr.x + 4, sr.right - 4, 14):
            bw = rng.randint(10, 18)
            puff_c = lerp_color(CLOUD_WHITE, (255, 248, 235), 0.4)
            pygame.draw.ellipse(surface, puff_c, (bx, sr.y - 5, bw, 8))
        if sr.width >= 100:
            lcs = [(255, 120, 140), (255, 200, 60), (255, 160, 80), (120, 210, 255), (255, 180, 220)]
            for i, lx in enumerate(range(sr.x + 8, sr.right - 8, 18)):
                ly = sr.bottom + 4 + int(math.sin(i * 0.9) * 2)
                if i > 0:
                    px2 = lx - 18; py2 = sr.bottom + 4 + int(math.sin((i-1) * 0.9) * 2)
                    pygame.draw.line(surface, (200, 190, 170), (px2, py2), (lx, ly), 1)
                c = lcs[i % len(lcs)]
                pygame.draw.circle(surface, c, (lx, ly), 3)
                pygame.draw.circle(surface, WHITE, (lx - 1, ly - 1), 1)


class MovingPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, w, h, speed=1.5, color=None):
        super().__init__(x1, y1, w, h, color or PLAT_MOVE)
        self.sx, self.sy = x1, y1; self.ex, self.ey = x2, y2
        self.speed = speed; self.progress = 0.0; self.dir = 1; self.dx = self.dy = 0
    def update(self):
        ox, oy = self.rect.x, self.rect.y
        self.progress += self.speed * self.dir * 0.005
        if self.progress >= 1: self.progress = 1.0; self.dir = -1
        elif self.progress <= 0: self.progress = 0.0; self.dir = 1
        t = self.progress; s = t*t*(3-2*t)
        self.rect.x = int(self.sx + (self.ex-self.sx)*s)
        self.rect.y = int(self.sy + (self.ey-self.sy)*s)
        self.dx = self.rect.x - ox; self.dy = self.rect.y - oy
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH+10: return
        pygame.draw.rect(surface, (255, 235, 180), sr, border_radius=8)
        stripe_c = (255, 195, 90)
        for si in range(-sr.height, sr.width + sr.height, 14):
            x0 = sr.x + si; x1 = x0 + 8
            pts = [(max(sr.x, x0), sr.y), (min(sr.right, x1), sr.y),
                   (min(sr.right, x1 + sr.height), sr.bottom), (max(sr.x, x0 + sr.height), sr.bottom)]
            if len(set(pts)) >= 3:
                pygame.draw.polygon(surface, stripe_c, pts)
        pygame.draw.rect(surface, (255, 235, 180), sr, border_radius=8, width=2)
        rng = random.Random(sr.x * 17 + sr.y * 31)
        for bx in range(sr.x + 4, sr.right - 4, 12):
            bw = rng.randint(8, 14)
            pygame.draw.ellipse(surface, (255, 252, 240), (bx, sr.y - 4, bw, 7))


class IcePlatform(Platform):
    ICE_FRICTION = 0.96; ICE_ACCEL = 0.12
    def __init__(self, x, y, w, h=22):
        super().__init__(x, y, w, h, PLAT_ICE); self.tick = 0
    def on_player_land(self, player): player.on_ice = True
    def update(self): self.tick += 1
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH+10: return
        pygame.draw.rect(surface, self.color, sr, border_radius=10)
        hi = tuple(min(c+65, 255) for c in self.color)
        pygame.draw.rect(surface, hi, (sr.x+4, sr.y, sr.width-8, 5), border_radius=4)
        for i in range(5):
            phase = (self.tick*0.09 + i*1.3) % (2*math.pi)
            bri = int(150 + 105*abs(math.sin(phase)))
            sx2 = sr.x + 10 + i*max(1, (sr.width-20)//4)
            pygame.draw.circle(surface, (bri, bri, 255), (sx2, sr.y+8), 2)
        font = pygame.font.SysFont("consolas", 10, bold=True)
        lbl  = font.render("ICE", True, (80, 160, 215))
        surface.blit(lbl, (sr.centerx-lbl.get_width()//2, sr.y+8))


class GlitchPlatform(Platform):
    def __init__(self, x, y, w, h=22, on_time=90, off_time=60, offset=0):
        super().__init__(x, y, w, h, PLAT_GLITCH)
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
        if sr.right < -10 or sr.left > SCREEN_WIDTH+10: return
        f = self.alpha / 255
        c = tuple(max(0, min(255, int(v * f))) for v in self.base_color)
        pygame.draw.rect(surface, c, sr, border_radius=8)
        if self.alpha > 80:
            for ix in range(0, sr.width, 8):
                if (self.timer + ix) % 12 < 6:
                    lc = tuple(min(v + 40, 255) for v in c)
                    pygame.draw.line(surface, lc, (sr.x + ix, sr.y), (sr.x + ix, sr.y + sr.height))


class TeleportPlatform(Platform):
    def __init__(self, x1, y1, x2, y2, w, h, interval=150, color=None):
        super().__init__(x1, y1, w, h, color or PLAT_TELE)
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
            pygame.draw.rect(surface, WHITE if self.flash>0 else self.color, sr, border_radius=8)
            if self.interval-self.timer<30 and self.timer%6<3:
                pygame.draw.rect(surface, XMAS_GOLD, sr, 2, border_radius=8)
            pygame.draw.rect(surface, SNOW_WHITE, (sr.x,sr.y-2,sr.width,3))
        gp = self.p2 if self.at1 else self.p1
        gr = camera.apply(pygame.Rect(*gp, self.rect.w, self.rect.h))
        pygame.draw.rect(surface, tuple(c//4 for c in self.color), gr, border_radius=8)
        pygame.draw.rect(surface, tuple(c//2 for c in self.color), gr, 1, border_radius=8)


class CollapsingPlatform(Platform):
    def __init__(self, x, y, w, h, delay=55, respawn_time=180, color=None):
        super().__init__(x, y, w, h, color or PLAT_FALL)
        self.base_color=self.color; self.oy=y; self.delay=delay
        self.respawn_time=respawn_time; self.stood=0; self.collapsed=False; self.rc=0; self.shake=0
    def update(self):
        if self.collapsed:
            self.rc += 1
            if self.rc >= self.respawn_time:
                self.collapsed=False; self.rc=0; self.stood=0; self.rect.y=self.oy
        elif self.stood > 0:
            self.stood += 1; self.shake=(self.stood%4)-2
            if self.stood >= self.delay: self.collapsed=True; self.shake=0
    def is_active(self): return not self.collapsed
    def on_player_land(self, p):
        if not self.collapsed and self.stood==0: self.stood=1
    def draw(self, surface, camera):
        if self.collapsed: return
        dr = self.rect.copy(); dr.x += self.shake
        sr = camera.apply(dr)
        if sr.right < -10 or sr.left > SCREEN_WIDTH+10: return
        if self.stood > 0:
            r = min(self.stood/self.delay, 1.0)
            col = (min(255,int(self.base_color[0]+(255-self.base_color[0])*r)),
                   max(0,int(self.base_color[1]*(1-r))), max(0,int(self.base_color[2]*(1-r))))
        else: col = self.base_color
        pygame.draw.rect(surface, col, sr, border_radius=8)
        pygame.draw.rect(surface, tuple(min(c+30,255) for c in col), (sr.x+4,sr.y,sr.width-8,4), border_radius=3)
        if self.stood > self.delay*0.5:
            pygame.draw.line(surface, BLACK, (sr.centerx-8,sr.y), (sr.centerx+4,sr.bottom), 2)
        # ── countdown bar: full-width at stood=0, shrinks to 0 at stood=delay
        if self.stood > 0 and sr.width > 8:
            ratio = max(0.0, 1.0 - (self.stood / self.delay))
            bar_w = int((sr.width - 8) * ratio)
            bar_col = lerp_color((80, 220, 80), (255, 60, 60),
                                 min(1.0, self.stood / self.delay))
            pygame.draw.rect(surface, (30, 30, 30), (sr.x+4, sr.bottom-5, sr.width-8, 4), border_radius=2)
            if bar_w > 0:
                pygame.draw.rect(surface, bar_col, (sr.x+4, sr.bottom-5, bar_w, 4), border_radius=2)


class WindZone:
    def __init__(self, x, y, w, h, force=1.8, direction=1):
        self.rect=pygame.Rect(x,y,w,h); self.force=force; self.direction=direction; self.tick=0
        rng=random.Random(x^(y+1))
        self.streaks=[(rng.randint(0,w),rng.randint(0,h),rng.randint(40,90)) for _ in range(20)]
    def update(self): self.tick += 1
    def apply_to_player(self, player):
        if player.alive and player.rect.colliderect(self.rect):
            player.vel_x += self.force * self.direction * 0.35
            player.vel_x  = max(-12, min(12, player.vel_x))
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right<-20 or sr.left>SCREEN_WIDTH+20: return
        ov = pygame.Surface((max(1,sr.width),max(1,sr.height)), pygame.SRCALPHA)
        al = int(28+12*abs(math.sin(self.tick*0.04)))
        ov.fill((100,180,255,al) if self.direction>0 else (255,180,100,al))
        surface.blit(ov, (sr.x,sr.y))
        sp = self.tick*3*self.direction
        for ox2,oy2,length in self.streaks:
            sx2=sr.x+(ox2+sp)%max(1,sr.width); sy2=sr.y+oy2%max(1,sr.height)
            ex2=sx2+length*self.direction
            sx2=max(sr.x,min(sr.right,sx2)); ex2=max(sr.x,min(sr.right,ex2))
            if abs(ex2-sx2)>2: pygame.draw.line(surface, (165,215,255), (int(sx2),int(sy2)), (int(ex2),int(sy2)), 1)
        for ax2 in range(sr.x+30, sr.right-20, 80):
            ay2 = sr.centery
            pygame.draw.polygon(surface, (165,215,255), [(ax2,ay2-6),(ax2+14*self.direction,ay2),(ax2,ay2+6)])
        font=pygame.font.SysFont("consolas",11,bold=True)
        lbl=font.render(">> WIND >>" if self.direction>0 else "<< WIND <<",True,(70,130,190))
        surface.blit(lbl, (sr.x+6, sr.y+4))


class SawBlade:
    RADIUS = 18
    def __init__(self, x1, y1, x2, y2, speed=1.5):
        self.x1,self.y1,self.x2,self.y2=x1,y1,x2,y2
        self.speed=speed; self.progress=0.0; self.dir=1; self.angle=0.0
        self.rect=pygame.Rect(x1-self.RADIUS,y1-self.RADIUS,self.RADIUS*2,self.RADIUS*2)
    def update(self):
        self.progress+=self.speed*self.dir*0.005; self.angle+=0.15
        if self.progress>=1: self.progress=1.0; self.dir=-1
        elif self.progress<=0: self.progress=0.0; self.dir=1
        t=self.progress; s=t*t*(3-2*t)
        cx=int(self.x1+(self.x2-self.x1)*s); cy=int(self.y1+(self.y2-self.y1)*s)
        self.rect.center=(cx,cy)
    def check_hit(self, player): return player.alive and self.rect.colliderect(player.rect)
    def draw(self, surface, camera, tick):
        sr=camera.apply(self.rect)
        if sr.right<-30 or sr.left>SCREEN_WIDTH+30: return
        cx,cy=sr.centerx,sr.centery; r=self.RADIUS
        blade_col_dark=(55,55,75); blade_col_mid=(100,100,130)
        blade_col_hi=(180,180,220); blade_col_gold=(200,175,50)
        for i in range(4):
            base_angle = self.angle + i * (math.pi / 2)
            tx=cx+int(math.cos(base_angle)*(r+4)); ty=cy+int(math.sin(base_angle)*(r+4))
            lx=cx+int(math.cos(base_angle+math.pi/2)*(r*0.55)); ly=cy+int(math.sin(base_angle+math.pi/2)*(r*0.55))
            rx=cx+int(math.cos(base_angle-math.pi/2)*(r*0.55)); ry=cy+int(math.sin(base_angle-math.pi/2)*(r*0.55))
            bx=cx+int(math.cos(base_angle+math.pi)*(r*0.30)); by_=cy+int(math.sin(base_angle+math.pi)*(r*0.30))
            pygame.draw.polygon(surface, blade_col_dark, [(tx,ty),(lx,ly),(bx,by_),(rx,ry)])
            pygame.draw.polygon(surface, blade_col_hi,   [(tx,ty),(lx,ly),(bx,by_)])
            pygame.draw.polygon(surface, blade_col_mid,  [(tx,ty),(rx,ry),(bx,by_)])
            pygame.draw.polygon(surface, (200,200,240), [(tx,ty),(lx,ly),(bx,by_),(rx,ry)], 1)
        for rr, rc in [(7, blade_col_gold), (5, blade_col_dark), (3, blade_col_hi)]:
            pygame.draw.circle(surface, rc, (cx, cy), rr)
        pygame.draw.circle(surface, (230, 210, 80), (cx, cy), 2)


class Kunai:
    WIDTH, HEIGHT = 10, 42
    def __init__(self, x, y_ceiling, max_fall_speed=6):
        self.cx = x; self.y_top = y_ceiling
        self.rect = pygame.Rect(x - self.WIDTH//2, y_ceiling, self.WIDTH, self.HEIGHT)
        self.state = "idle"; self.shake_timer = 0; self.angle_deg = 0.0
        self.fall_speed = 0.0; self.max_fall_speed = max_fall_speed; self.orig_y = y_ceiling
    def update(self):
        if self.state == "idle": self.angle_deg = 0.0
        elif self.state == "shaking":
            self.shake_timer -= 1
            self.angle_deg = math.sin(self.shake_timer * 0.8) * 6.0
            if self.shake_timer <= 0:
                self.state = "falling"; self.fall_speed = 2.0; self.angle_deg = 0.0
        elif self.state == "falling":
            self.fall_speed = min(self.fall_speed + 0.5, self.max_fall_speed)
            self.rect.y += int(self.fall_speed); self.y_top = self.rect.y
            if self.rect.y > DEATH_Y: self.state = "done"
    def trigger(self):
        if self.state == "idle": self.state = "shaking"; self.shake_timer = 35
    def check_player_below(self, player):
        if self.state != "idle" or not player.alive: return
        if (abs(player.rect.centerx - self.cx) < 55 and player.rect.top > self.rect.bottom):
            self.trigger()
    def check_hit(self, player):
        if self.state != "falling" or not player.alive: return False
        return self.rect.colliderect(player.rect)
    def draw(self, surface, camera, tick):
        if self.state == "done": return
        world_rect = pygame.Rect(self.rect.x, self.y_top, self.WIDTH, self.HEIGHT)
        sr = camera.apply(world_rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20: return
        sx = sr.centerx; sy_top = sr.y
        RING_R=5; RING_CY=sy_top+RING_R; HANDLE_H=18; HANDLE_W=7; BLADE_H=22; BLADE_W=6; TIP_H=6
        RING_COL=(110,135,155); HANDLE_COL=(75,55,40); WRAP_COL=(140,160,180)
        BLADE_COL=(180,215,245); BLADE_HI=(220,240,255); TIP_COL=(145,185,215)
        pygame.draw.circle(surface, RING_COL, (sx, RING_CY), RING_R, 2)
        cord_top=RING_CY+RING_R; cord_bot=cord_top+5
        pygame.draw.line(surface, WRAP_COL, (sx, cord_top), (sx, cord_bot), 1)
        hx=sx-HANDLE_W//2; hy=cord_bot
        pygame.draw.rect(surface, HANDLE_COL, (hx, hy, HANDLE_W, HANDLE_H), border_radius=2)
        for wi in range(3):
            wy=hy+3+wi*5
            pygame.draw.line(surface, WRAP_COL, (hx, wy), (hx+HANDLE_W, wy+2), 1)
        collar_y=hy+HANDLE_H
        pygame.draw.rect(surface, RING_COL, (sx-4, collar_y, 8, 3), border_radius=1)
        blade_y=collar_y+3
        for bi in range(BLADE_H):
            t_blade=bi/BLADE_H; w_at=max(1, int(BLADE_W*(1.0-t_blade*0.55)))
            col_b=lerp_color(BLADE_COL, TIP_COL, t_blade)
            pygame.draw.line(surface, col_b, (sx-w_at, blade_y+bi), (sx+w_at, blade_y+bi), 1)
            pygame.draw.line(surface, BLADE_HI, (sx-w_at, blade_y+bi), (sx-w_at+1, blade_y+bi), 1)
        tip_y=blade_y+BLADE_H
        pygame.draw.polygon(surface, TIP_COL, [(sx-2, tip_y),(sx+2, tip_y),(sx, tip_y+TIP_H)])


class FrostPuff:
    BURST_INTERVAL = 120
    W, H = 48, 36
    def __init__(self, x, y, drift_speed=0.5, x_min=80, x_max=1200):
        self.x=float(x); self.y=float(y)
        self.rect=pygame.Rect(int(x)-self.W//2, int(y)-self.H//2, self.W, self.H)
        self.drift_speed=drift_speed; self.drift_dir=1; self.x_min=x_min; self.x_max=x_max
        self.burst_timer=random.randint(30, self.BURST_INTERVAL)
        self.tick=random.randint(0, 200); self.droplets=[]
    def update(self):
        self.tick+=1; self.x+=self.drift_speed*self.drift_dir
        if self.x<self.x_min: self.x=self.x_min; self.drift_dir=1
        elif self.x>self.x_max: self.x=self.x_max; self.drift_dir=-1
        self.rect.x=int(self.x)-self.W//2; self.rect.y=int(self.y)-self.H//2
        self.burst_timer-=1
        if self.burst_timer<=0:
            self.burst_timer=self.BURST_INTERVAL
            for _ in range(8):
                self.droplets.append((self.x+random.uniform(-16,16), self.y+self.H//2,
                                      random.uniform(1.5,4.0), random.randint(20,45)))
        self.droplets=[(dx, dy+dvy, dvy+0.3, lt-1) for dx,dy,dvy,lt in self.droplets if lt>0]
    def check_hit(self, player):
        if not player.alive: return False
        pr=player.rect
        for dx,dy,dvy,lt in self.droplets:
            dr=pygame.Rect(int(dx)-4, int(dy)-4, 8, 8)
            if dr.colliderect(pr):
                self.droplets=[(x,y,v,l) for x,y,v,l in self.droplets if not (abs(x-dx)<1 and abs(y-dy)<1)]
                return True
        return False
    def draw(self, surface, camera, tick):
        sr=camera.apply(self.rect)
        if sr.right<-60 or sr.left>SCREEN_WIDTH+60: return
        cx,cy=sr.centerx,sr.centery
        for ox,oy,r in [(0,0,24),(-18,8,18),(18,10,16)]:
            pygame.draw.circle(surface, (210,235,255), (cx+ox,cy+oy), r)
        for ox,oy,r in [(0,0,16),(-16,9,11),(16,11,10)]:
            pygame.draw.circle(surface, (235,248,255), (cx+ox,cy+oy), r)
        pygame.draw.circle(surface, (60,100,160), (cx-8,cy-4), 3)
        pygame.draw.circle(surface, (60,100,160), (cx+8,cy-4), 3)
        pygame.draw.line(surface, (60,100,160), (cx-11,cy-10), (cx-5,cy-8), 2)
        pygame.draw.line(surface, (60,100,160), (cx+5,cy-8), (cx+11,cy-10), 2)
        for dx,dy,dvy,lt in self.droplets:
            ds=camera.apply(pygame.Rect(int(dx)-3,int(dy)-3,6,6))
            alpha=max(0,min(255,int(255*lt/45)))
            fs=pygame.Surface((8,8),pygame.SRCALPHA)
            pygame.draw.circle(fs, (170,215,255,alpha), (4,4), 3)
            surface.blit(fs, (ds.x-4,ds.y-4))


class StompMonster:
    W, H = 32, 24
    BOUNCE_VEL = -16
    def __init__(self, x, y, patrol_x1=None, patrol_x2=None, speed=1.2):
        self.rect  = pygame.Rect(int(x) - self.W//2, int(y) - self.H//2, self.W, self.H)
        self.cx    = float(x); self.cy = float(y)
        self.patrol_x1 = patrol_x1 if patrol_x1 is not None else x - 60
        self.patrol_x2 = patrol_x2 if patrol_x2 is not None else x + 60
        self.speed = speed; self.dir = 1; self.alive = True
        self.death_timer = 0; self.tick = random.randint(0, 120); self.base_y = float(y)
    def update(self):
        if not self.alive:
            self.death_timer -= 1; return
        self.tick += 1
        self.cx += self.speed * self.dir
        if self.cx > self.patrol_x2: self.cx = self.patrol_x2; self.dir = -1
        elif self.cx < self.patrol_x1: self.cx = self.patrol_x1; self.dir = 1
        self.cy = self.base_y + math.sin(self.tick * 0.05) * 12
        self.rect.x = int(self.cx) - self.W // 2
        self.rect.y = int(self.cy) - self.H // 2
    def check_stomp(self, player):
        if not self.alive or not player.alive: return False
        if not self.rect.colliderect(player.rect): return False
        return player.vel_y > 0 and player.rect.bottom <= self.rect.centery + 10
    def check_side_hit(self, player):
        if not self.alive or not player.alive: return False
        if not self.rect.colliderect(player.rect): return False
        return not (player.vel_y > 0 and player.rect.bottom <= self.rect.centery + 10)
    def kill(self):
        self.alive = False; self.death_timer = 20
    def draw(self, surface, camera, tick):
        if not self.alive and self.death_timer <= 0: return
        sr = camera.apply(self.rect)
        if sr.right < -40 or sr.left > SCREEN_WIDTH + 40: return
        cx, cy = sr.centerx, sr.centery
        alpha = 255 if self.alive else max(0, int(255 * self.death_timer / 20))
        body_col = (100, 140, 255); wing_col = (160, 190, 255)
        flap = int(math.sin(self.tick * 0.25) * 5)
        wing_surf = pygame.Surface((sr.width + 20, sr.height + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(wing_surf, (*wing_col, alpha), (0, sr.height//2-4+flap, 14, 10))
        pygame.draw.ellipse(wing_surf, (*wing_col, alpha), (sr.width+6, sr.height//2-4+flap, 14, 10))
        surface.blit(wing_surf, (sr.x - 10, sr.y - 10))
        body_surf = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
        pygame.draw.ellipse(body_surf, (*body_col, alpha), (0, 0, sr.width, sr.height))
        pygame.draw.ellipse(body_surf, (*(min(c+50,255) for c in body_col), alpha),
            (4, 2, sr.width-8, sr.height//2))
        surface.blit(body_surf, sr.topleft)
        ex = cx - 6 if self.dir >= 0 else cx + 2
        pygame.draw.circle(surface, (255,255,255), (ex, cy-2), 4)
        pygame.draw.circle(surface, (30,30,80), (ex+self.dir, cy-1), 2)
        if not self.alive:
            for ox, oy in [(-6,-4),(2,-4)]:
                bx2, by2 = cx+ox, cy+oy
                pygame.draw.line(surface, (255,80,80), (bx2-2,by2-2), (bx2+2,by2+2), 2)
                pygame.draw.line(surface, (255,80,80), (bx2+2,by2-2), (bx2-2,by2+2), 2)


class StarRing:
    def __init__(self, x, y):
        self.x,self.y=x,y; self.rect=pygame.Rect(x-10,y-10,20,20)
        self.collected=False; self.tick=random.randint(0,360)
    def check(self, player):
        if self.collected or not player.alive: return False
        if self.rect.colliderect(player.rect): self.collected=True; return True
        return False
    def draw(self, surface, camera, tick):
        if self.collected: return
        bob=int(math.sin(self.tick*0.08)*3)
        pos=camera.apply(pygame.Rect(self.x,self.y+bob,1,1)); sx,sy=pos.x,pos.y
        if sx<-20 or sx>SCREEN_WIDTH+20: return
        self.tick+=1; pulse=abs(math.sin(self.tick*0.1))*0.4+0.6
        gc=lerp_color(STAR_GOLD, WHITE, pulse*0.4)
        r_out,r_in=10,4; pts=[]
        for k in range(10):
            angle=-math.pi/2+k*math.pi/5; r=r_out if k%2==0 else r_in
            pts.append((sx+int(math.cos(angle)*r),sy+int(math.sin(angle)*r)))
        pygame.draw.polygon(surface, gc, pts)
        pygame.draw.polygon(surface, SUN_ORANGE, pts, 1)


class Checkpoint:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x, y-50, 20, 50)
        self.spawn_x=x; self.spawn_y=y-60
        self.activated=False; self.glow=0
    def update(self):
        if self.activated: self.glow=(self.glow+3)%360
    def check(self, player):
        if not self.activated and player.rect.colliderect(self.rect):
            self.activated=True; player.set_checkpoint(self.spawn_x,self.spawn_y); return True
        return False
    def draw(self, surface, camera):
        sr=camera.apply(self.rect); cx=sr.centerx
        pygame.draw.rect(surface, BROWN, (cx-3,sr.bottom-12,6,12))
        tc = (100, 200, 160) if self.activated else (80, 150, 120)
        tc_hi = tuple(min(c+35, 255) for c in tc)
        for w2, h2, yo in [(34, 20, 32), (26, 17, 20), (20, 14, 10)]:
            ty = sr.bottom - 12 - yo
            pts = [(cx, ty-h2), (cx-w2//2, ty), (cx+w2//2, ty)]
            pygame.draw.polygon(surface, tc, pts)
            pygame.draw.polygon(surface, tc_hi, [(cx, ty-h2), (cx-w2//2+2, ty-2), (cx-4, ty-h2+4)])
        sc = (255, 220, 60) if self.activated else DARK_GRAY
        if self.activated:
            for gr2, ga2 in [(10, 50), (7, 100)]:
                gs2 = pygame.Surface((gr2*2, gr2*2), pygame.SRCALPHA)
                pygame.draw.circle(gs2, (255, 230, 80, ga2), (gr2, gr2), gr2)
                surface.blit(gs2, (cx-gr2, sr.bottom-12-10-14-4-gr2))
        pygame.draw.circle(surface, sc, (cx, sr.bottom-12-10-14-4), 5)
        pygame.draw.circle(surface, WHITE, (cx-1, sr.bottom-12-10-14-5), 2)
        if self.activated:
            for j,(ox,oy,oc) in enumerate([(-9,-22,(255,140,160)),(7,-18,(255,210,60)),(-6,-32,(120,210,255)),(9,-28,(255,180,220)),(0,-42,(255,230,100))]):
                if abs(math.sin(math.radians(self.glow+j*60)))>0.3:
                    pygame.draw.circle(surface,oc,(cx+ox,sr.bottom-12+oy),3)
            i=abs(math.sin(math.radians(self.glow)))*0.6+0.4
            pygame.draw.rect(surface,tuple(int(v*i) for v in XMAS_GREEN),sr.inflate(8,8),2)


class ExitDoor:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x,y,54,72); self.pulse=0
    def update(self): self.pulse=(self.pulse+3)%360
    def check(self, player): return player.rect.colliderect(self.rect)
    def draw(self, surface, camera):
        sr=camera.apply(self.rect); p=abs(math.sin(math.radians(self.pulse)))
        pygame.draw.rect(surface, DARK_GRAY, sr.inflate(10,10), border_radius=10)
        portal_col = lerp_color((255, 220, 80), (255, 255, 200), p)
        pygame.draw.rect(surface, portal_col, sr, border_radius=8)
        cx2, cy2 = sr.centerx, sr.centery
        for i in range(12):
            angle = math.radians(i * 30 + self.pulse * 0.3)
            ray_len = int(22 + p * 12)
            ex2 = cx2 + int(math.cos(angle) * ray_len)
            ey2 = cy2 + int(math.sin(angle) * ray_len)
            pygame.draw.line(surface, lerp_color((255,200,50),WHITE,p*0.6), (cx2,cy2), (ex2,ey2), 2)
        pygame.draw.circle(surface, (255,200,40), (cx2,cy2), int(12+p*5))
        pygame.draw.circle(surface, (255,240,150), (cx2,cy2), int(7+p*3))
        pygame.draw.circle(surface, WHITE, (cx2,cy2), 4)
        font = pygame.font.SysFont("consolas", 11, bold=True)
        surface.blit(font.render("GATE", True, (80,50,10)),
            (sr.centerx-font.size("GATE")[0]//2, sr.bottom-16))
        pygame.draw.rect(surface, lerp_color((255,210,60),WHITE,p), sr.inflate(6,6), 2, border_radius=10)


class Player:
    WIDTH, HEIGHT = 28, 36
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vel_x = 0.0; self.vel_y = 0.0
        self.on_ground = False; self.was_on_ground = False
        self.spawn_x, self.spawn_y = x, y
        self.alive = True; self.respawn_timer = 0
        self.facing_right = True
        self.riding_platform = None; self.on_ice = False
        self.hearts = PLAYER_MAX_HEARTS
        self.invincibility = 0; self.death_count = 0
        self.kill_count = 0
        self.jump_count = 0
        self.max_jumps = 1
        self.dash_timer = 0; self.dash_cooldown = 0
        self.dash_dir = 0; self.dashing = False
        self.dash_afterimages = []
        self.wall_sliding = False; self.wall_side = 0
        self.squash_timer = 0; self.sprinting = False
        self.star_count = 0
        # Sprite animation state (mirrors level4 fields so player_sprites.py works)
        if _SPRITES_AVAILABLE:
            init_player_sprite(self)

    def set_checkpoint(self, x, y): self.spawn_x, self.spawn_y = x, y
    def take_damage(self):
        if self.invincibility > 0: return False
        self.hearts -= 1; self.invincibility = INVINCIBILITY_FRAMES
        if self.hearts <= 0: self.die()
        return True
    def die(self):
        self.alive = False; self.respawn_timer = 9999; self.death_count += 1
        # Trigger death animation if sprites available
        if _SPRITES_AVAILABLE:
            self._spr_state = 'death'; self._spr_frame = 0
            self._spr_tick = 0; self._spr_death_done = False
    def respawn(self):
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.vel_x = self.vel_y = 0; self.alive = True; self.on_ground = False
        self.hearts = PLAYER_MAX_HEARTS; self.invincibility = 0
        self.jump_count = 0; self.dash_timer = 0; self.dash_cooldown = 0; self.dashing = False
    def start_dash(self):
        if self.dash_cooldown <= 0 and not self.on_ground and not self.dashing and self.alive:
            self.dashing = True; self.dash_timer = DASH_DURATION; self.dash_cooldown = DASH_COOLDOWN
            self.dash_dir = 1 if self.facing_right else -1; self.vel_y = 0
    def update(self, keys, platforms):
        if not self.alive:
            # With sprites: wait for death animation before respawning
            if _SPRITES_AVAILABLE:
                if getattr(self, '_spr_death_done', False) and self.respawn_timer > 0:
                    self.respawn_timer -= 1
                    if self.respawn_timer <= 0: self.respawn()
            else:
                self.respawn_timer -= 1
                if self.respawn_timer <= 0: self.respawn()
            return None
        if self.invincibility > 0: self.invincibility -= 1
        if self.dash_cooldown > 0: self.dash_cooldown -= 1

        # ── Spatial culling: only check platforms near the player ──────────
        nearby = [p for p in platforms
                  if abs(p.get_rect().centerx - self.rect.centerx) < 420
                  and abs(p.get_rect().centery - self.rect.centery) < 300]

        if self.dashing:
            self.dash_timer -= 1
            self.dash_afterimages.append((self.rect.x, self.rect.y, 200))
            if len(self.dash_afterimages) > 8: self.dash_afterimages.pop(0)
            self.rect.x += DASH_SPEED * self.dash_dir; self.vel_y = 0
            if self.dash_timer <= 0: self.dashing = False
            for plat in nearby:
                if not plat.is_active(): continue
                pr = plat.get_rect()
                if self.rect.colliderect(pr):
                    if self.dash_dir > 0: self.rect.right = pr.left
                    else: self.rect.left = pr.right
                    self.dashing = False
            return None
        self.dash_afterimages = [(x,y,a-30) for x,y,a in self.dash_afterimages if a>30]
        if self.riding_platform is not None and hasattr(self.riding_platform,'dx'):
            self.rect.x += self.riding_platform.dx; self.rect.y += self.riding_platform.dy
        move = 0.0
        self.sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed = SPRINT_SPEED if self.sprinting else MOVE_SPEED
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: move -= speed; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move += speed; self.facing_right = True
        accel = IcePlatform.ICE_ACCEL if self.on_ice else 0.3
        fric  = IcePlatform.ICE_FRICTION if self.on_ice else 0.75
        self.vel_x = (self.vel_x+(move-self.vel_x)*accel) if move else (self.vel_x*fric)
        if abs(self.vel_x) < 0.1: self.vel_x = 0
        self.vel_y = min(self.vel_y+GRAVITY, MAX_FALL_SPEED)
        jumped = False
        if self.on_ground and self.jump_count == 0 and (
                keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False; self.riding_platform = None
            self.jump_count = 1; jumped = True
        self.on_ice = False
        self.rect.x += int(self.vel_x)
        touching_wall = 0
        for plat in nearby:
            if not plat.is_active(): continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.rect.bottom <= pr.top+6: continue
                if self.vel_x > 0:   self.rect.right = pr.left;  touching_wall = 1
                elif self.vel_x < 0: self.rect.left  = pr.right; touching_wall = -1
                self.vel_x = 0
        self.was_on_ground = self.on_ground
        self.on_ground = False; self.riding_platform = None
        vy = int(self.vel_y)
        if self.vel_y > 0 and vy == 0: vy = 1
        self.rect.y += vy
        for plat in nearby:
            if not plat.is_active(): continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.vel_y > 0:
                    self.rect.bottom = pr.top; self.vel_y = 0
                    self.on_ground = True; self.jump_count = 0
                    if isinstance(plat, MovingPlatform): self.riding_platform = plat
                    if isinstance(plat, IcePlatform):    self.on_ice = True
                    plat.on_player_land(self)
                elif self.vel_y < 0:
                    self.rect.top = pr.bottom; self.vel_y = 0
        pressing_into = ((touching_wall==1  and (keys[pygame.K_RIGHT] or keys[pygame.K_d])) or
                         (touching_wall==-1 and (keys[pygame.K_LEFT]  or keys[pygame.K_a])))
        if not self.on_ground and self.vel_y > 0 and pressing_into and touching_wall != 0:
            self.wall_sliding = True; self.wall_side = touching_wall
            self.vel_y = min(self.vel_y, 2); self.jump_count = 1
        else:
            self.wall_sliding = False; self.wall_side = 0
        if self.rect.top > DEATH_Y:
            self.alive = False; self.respawn_timer = 9999; self.death_count += 1
            if _SPRITES_AVAILABLE:
                self._spr_state = 'death'; self._spr_frame = 0
                self._spr_tick = 0; self._spr_death_done = False
        return "jump" if jumped else None

    def draw(self, surface, camera, tick):
        if not self.alive:
            # Still draw death animation if sprites available
            if _SPRITES_AVAILABLE:
                draw_player_sprite(self, surface, camera, tick,
                                   unreal_tint_fn=lambda t: xmas_cycle(t, 0.12))
            return
        if self.on_ground and not self.was_on_ground: self.squash_timer = 6
        if self.squash_timer > 0: self.squash_timer -= 1
        if self.invincibility > 0 and (self.invincibility//4)%2==0: return
        # Dash afterimages
        for ax, ay, aa in self.dash_afterimages:
            ar = camera.apply(pygame.Rect(ax, ay, self.WIDTH, self.HEIGHT))
            s  = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            s.fill((*ICE_BLUE, int(aa*0.5))); surface.blit(s, ar.topleft)
        # Dash speed lines
        if self.dashing:
            dsr = camera.apply(self.rect)
            for sl in range(5):
                slx = dsr.centerx + (-self.dash_dir)*(10+sl*8) + random.randint(-2,2)
                sly = dsr.y + random.randint(2, self.HEIGHT-2)
                sll = random.randint(8,16)
                pygame.draw.line(surface, (100,180,255), (slx,sly),
                                 (slx+(-self.dash_dir)*sll, sly), 2)
        # Use sprite sheet if available, otherwise fall back to drawn character
        if _SPRITES_AVAILABLE:
            draw_player_sprite(self, surface, camera, tick,
                               unreal_tint_fn=lambda t: xmas_cycle(t, 0.12))
            return
        # ── Fallback: drawn character ──────────────────────────────────────
        sr = camera.apply(self.rect)
        if self.vel_y < -3 and not self.on_ground:
            stretch = 4; sr = sr.inflate(-4, stretch*2); sr.bottom += stretch
        elif self.squash_timer > 0:
            sq = int(self.squash_timer*0.8); sr = sr.inflate(sq*2, -sq*2); sr.bottom += sq
        if self.on_ice:
            pygame.draw.rect(surface, (210,238,255), sr)
            pygame.draw.rect(surface, PLAT_ICE, (sr.x+2,sr.y+2,sr.width-4,4))
        else:
            body_col = lerp_color((255,170,60),(255,210,100), abs(math.sin(tick*0.03))*0.2)
            pygame.draw.rect(surface, body_col, sr, border_radius=4)
            pygame.draw.rect(surface, (255,235,160), (sr.right-4,sr.y+4,3,sr.height-8), border_radius=2)
            pygame.draw.rect(surface, (200,130,40), (sr.x+1,sr.y+4,3,sr.height-8), border_radius=2)
            belt_y = sr.y + sr.height - 14
            pygame.draw.rect(surface, (80,55,20), (sr.x,belt_y,sr.width,5))
            bw, bh = 8, 7
            pygame.draw.rect(surface, (255,220,60), (sr.centerx-bw//2,belt_y-1,bw,bh))
        ht = sr.y - 10
        hat_tip_x = sr.centerx + (6 if self.facing_right else -6)
        hat_col = lerp_color((255,190,40),(255,230,100), abs(math.sin(tick*0.04))*0.4)
        pygame.draw.polygon(surface, hat_col, [(sr.x+1,sr.y+3),(sr.x+sr.width-1,sr.y+3),
            (sr.centerx+(4 if self.facing_right else -4),sr.y-4),(hat_tip_x,ht)])
        pygame.draw.rect(surface, (255,250,210), (sr.x-1,sr.y,sr.width+2,5))
        pygame.draw.circle(surface, SUN_YELLOW, (hat_tip_x, ht-2), 2)
        pygame.draw.rect(surface, (230,195,160), (sr.x+2,sr.y+8,sr.width-4,12))
        ey = sr.y+11; pupil = BLACK
        if self.facing_right:
            pygame.draw.rect(surface,WHITE,(sr.x+15,ey,7,6)); pygame.draw.rect(surface,pupil,(sr.x+18,ey+1,4,4))
        else:
            pygame.draw.rect(surface,WHITE,(sr.x+6,ey,7,6));  pygame.draw.rect(surface,pupil,(sr.x+6,ey+1,4,4))
        if self.wall_sliding:
            wx = sr.left if self.wall_side==-1 else sr.right
            for i in range(4):
                sy2=sr.y+5+i*8+random.randint(-1,1)
                pygame.draw.line(surface,WHITE,(wx,sy2),(wx+random.randint(-3,3),sy2+random.randint(4,8)),1)


def make_bg_clouds():
    rng = random.Random(77); out = []
    for _ in range(100):
        out.append(BGCloud(rng.randint(-200, 1400), rng.randint(-900, 900),
                           rng.randint(28, 70), rng.uniform(0.04, 0.18)))
    return out


def create_level(diff_key="medium"):
    diff = DIFFICULTY[diff_key]
    cd  = diff["collapse_delay"]   # frames: easy=120, medium=60, hard=30

    plats        = []
    updrafts     = []
    winds        = []
    cps          = []
    stars        = []
    npcs         = []
    saw_blades   = []
    kunais       = []
    frost_puffs  = []
    monster_defs = []

    GROUND = 560

    # ── Checkpoint x positions — platforms that hold a checkpoint stay stable.
    # We collect these upfront so the helper below can check against them.
    # Format: set of platform x coords that own a checkpoint.
    CP_PLAT_XS = {680, 1960, 4090, 6050, 7760}

    # ── Helper: returns CollapsingPlatform for jumping platforms,
    #            plain Platform for spawn/checkpoint/exit platforms.
    def P(x, y, w, h=20, force_stable=False):
        if force_stable or x in CP_PLAT_XS:
            return Platform(x, y, w, h)
        return CollapsingPlatform(x, y, w, h, delay=cd, respawn_time=300)

    # ── S1 — START (spawn platform always stable) ──────────────────────────
    plats.append(Platform(0, GROUND, 220, 22))          # spawn — stable
    npcs.append(NPC(100, GROUND, "intro", "Zephyr"))
    stars.append(StarRing(50,  GROUND - 60))
    stars.append(StarRing(130, GROUND - 90))
    stars.append(StarRing(200, GROUND - 60))

    plats.append(P(360, GROUND,       70, 20))
    stars.append(StarRing(395, GROUND - 50))

    plats.append(P(510, GROUND - 40,  70, 20))
    stars.append(StarRing(545, GROUND - 90))

    plats.append(P(680, GROUND - 80,  90, 20))          # CP1 platform — stable
    cps.append(Checkpoint(730, GROUND - 80))
    npcs.append(NPC(750, GROUND - 80, "cp1", "Nimbus"))

    # ── S2 — BASIC PARKOUR ─────────────────────────────────────────────────
    bases = [
        (960,  GROUND - 40,  65),
        (1210, GROUND - 90,  60),
        (1460, GROUND - 140, 60),
        (1710, GROUND - 180, 65),
        (1960, GROUND - 220, 80),                       # CP2 platform — stable
    ]
    for bx, by, bw in bases:
        plats.append(P(bx, by, bw, 20))
        stars.append(StarRing(bx + bw//2, by - 50))

    cps.append(Checkpoint(1970, GROUND - 220))

    # ── S3 — COIN GUIDANCE ─────────────────────────────────────────────────
    plats.append(P(2160, GROUND - 220, 70, 20))
    plats.append(P(2590, GROUND - 220, 70, 20))

    for i in range(6):
        t  = (i + 0.5) / 6
        ax = 2230 + int(t * 360)
        ay = (GROUND - 220) - int(math.sin(math.pi * t) * 120)
        stars.append(StarRing(ax, ay))

    # ── S4 — ZIG-ZAG ───────────────────────────────────────────────────────
    zz = [
        (2820, GROUND - 200, 60),
        (3080, GROUND - 100, 55),
        (3330, GROUND - 240, 55),
        (3580, GROUND - 120, 55),
        (3830, GROUND - 280, 60),
        (4090, GROUND - 180, 70),                       # CP3 platform — stable
    ]
    for bx, by, bw in zz:
        plats.append(P(bx, by, bw, 20))

    cps.append(Checkpoint(4100, GROUND - 180))

    # ── S5 — LONG JUMP ─────────────────────────────────────────────────────
    plats.append(P(4360, GROUND - 200, 70, 20))
    stars.append(StarRing(4395, GROUND - 260))
    stars.append(StarRing(4540, GROUND - 320))
    stars.append(StarRing(4690, GROUND - 260))
    plats.append(P(4850, GROUND - 200, 75, 20))

    # ── S6 — CLEAN PLATFORMS ───────────────────────────────────────────────
    clean_plats = [
        (5050, GROUND - 200, 60),
        (5300, GROUND - 240, 55),
        (5550, GROUND - 200, 55),
        (5800, GROUND - 260, 60),
        (6050, GROUND - 220, 75),                       # CP4 platform — stable
    ]
    for bx, by, bw in clean_plats:
        plats.append(P(bx, by, bw, 20))
        stars.append(StarRing(bx + bw//2, by - 50))

    cps.append(Checkpoint(6060, GROUND - 220))

    # ── S7 — MONSTER BOUNCE ────────────────────────────────────────────────
    plats.append(P(6300, GROUND - 220, 80, 20))
    plats.append(P(6980, GROUND - 420, 90, 20))

    monster_defs.append(dict(x=6480, y=GROUND-300, x1=6440, x2=6540, spd=0.8))
    monster_defs.append(dict(x=6660, y=GROUND-360, x1=6620, x2=6720, spd=0.8))
    monster_defs.append(dict(x=6840, y=GROUND-400, x1=6800, x2=6880, spd=0.8))

    # ── S8 — TRAP ──────────────────────────────────────────────────────────
    plats.append(P(7260, GROUND - 380, 70, 20))
    stars.append(StarRing(7400, GROUND - 430))
    stars.append(StarRing(7460, GROUND - 450))
    stars.append(StarRing(7520, GROUND - 430))

    # This one keeps its original instant-collapse behaviour (delay=8)
    plats.append(CollapsingPlatform(7490, GROUND-380, 70, 20, delay=8, respawn_time=400))

    plats.append(P(7760, GROUND - 380, 75, 20))         # CP5 platform — stable
    cps.append(Checkpoint(7770, GROUND - 380))

    # ── S9 — PRECISION ─────────────────────────────────────────────────────
    tiny = [
        (7990, GROUND - 200, 45),
        (8220, GROUND - 260, 40),
        (8450, GROUND - 320, 40),
        (8220, GROUND - 380, 40),
        (8450, GROUND - 440, 45),
        (8680, GROUND - 400, 45),
        (8910, GROUND - 360, 45),
    ]
    for bx, by, bw in tiny:
        plats.append(P(bx, by, bw, 20))

    # ── S10 — FINAL CHALLENGE + EXIT ───────────────────────────────────────
    final = [
        (9100, GROUND - 360, 55),
        (9330, GROUND - 300, 50),
        (9560, GROUND - 380, 50),
    ]
    for bx, by, bw in final:
        plats.append(P(bx, by, bw, 20))

    monster_defs.append(dict(x=9460, y=GROUND-360, x1=9420, x2=9500, spd=1.0))

    plats.append(Platform(9780, GROUND-360, 180, 22))   # exit rest — stable
    stars.append(StarRing(9820, GROUND - 410))
    stars.append(StarRing(9900, GROUND - 410))

    exit_door = ExitDoor(9950, GROUND - 440)

    stomp_monsters = [StompMonster(d['x'], d['y'], d['x1'], d['x2'], d['spd'])
                      for d in monster_defs]

    return (plats, updrafts, winds, cps, stars, npcs,
            saw_blades, kunais, frost_puffs, stomp_monsters, monster_defs, exit_door)


# ── Game ─────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None or self.screen.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sky Climber — Level 1 (Christmas Morning)")
        self.clock      = pygame.time.Clock()
        self.font       = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font   = pygame.font.SysFont("consolas", 48)
        self.tiny_font  = pygame.font.SysFont("consolas", 12, bold=True)
        self.title_font = pygame.font.SysFont("consolas", 36, bold=True)
        self.sfx        = SoundManager()
        self.state      = "playing"
        self.difficulty = "medium"
        self.level_time = self.tick = self.win_timer = 0
        self.music_volume = 0.5; self.sfx_volume = 0.5; self.music_muted = False
        self.settings_cursor = 0
        self._settings_boxes = []; self._settings_vol_slider = pygame.Rect(0,0,0,0)
        self._settings_sfx_slider = pygame.Rect(0,0,0,0); self._last_mouse_pos = (0,0)
        self.freeze_frames = 0; self.respawn_fade = 0; self.ending_shown = False
        self.camera     = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles  = []; self.rings = []; self.flashes = []
        self.damage_flashes = []; self.score_popups = []
        self.bg_clouds  = make_bg_clouds()
        self.platforms   = []; self.updrafts  = []; self.winds = []
        self.checkpoints = []
        self.stars_list  = []; self.npcs      = []; self.exit_door = None
        self.saw_blades  = []; self.kunais    = []
        self.frost_puffs = []
        self.stomp_monsters = []
        self.monster_defs   = []
        self.player       = Player(100, 504)
        self.dialogue_box = None; self.pending_state = None
        self.soul_state = None; self.soul_x = 0; self.soul_y = 0
        self.soul_target_y = 0; self.soul_timer = 0; self.soul_trail = []
        self.soul_pan_target_x = 0; self.soul_pan_target_y = 0
        self.load_level()
        self.sfx.start_music(volume=self.music_volume)
        self.sfx.set_sfx_volume(self.sfx_volume)

    def load_level(self):
        result = create_level(self.difficulty)
        (self.platforms, self.updrafts, self.winds,
         self.checkpoints,
         self.stars_list, self.npcs, self.saw_blades,
         self.kunais, self.frost_puffs,
         self.stomp_monsters, self.monster_defs,
         self.exit_door) = result
        self.player = Player(100, 504)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles.clear(); self.rings.clear()
        self.flashes.clear(); self.damage_flashes.clear(); self.score_popups.clear()
        self.level_time = self.tick = self.win_timer = 0
        self.freeze_frames = 0; self.respawn_fade = 0
        self.ending_shown = False; self.dialogue_box = None
        self.soul_state = None; self.soul_trail = []

    def _rebuild_monsters(self):
        self.stomp_monsters = [
            StompMonster(d['x'], d['y'], d['x1'], d['x2'], d['spd'])
            for d in self.monster_defs
        ]

    def _exit_to_menu(self):
        self.sfx.stop_music(); self.running = False; pygame.event.clear()

    def _apply_volume(self):
        pygame.mixer.music.set_volume(0.0 if self.music_muted else self.music_volume)
        self.sfx.set_sfx_volume(0.0 if self.music_muted else self.sfx_volume)

    def _apply_difficulty(self):
        """Update collapse delay on all live CollapsingPlatforms to match the
        current difficulty setting — no restart needed, takes effect instantly."""
        new_delay = DIFFICULTY[self.difficulty]["collapse_delay"]
        for p in self.platforms:
            if isinstance(p, CollapsingPlatform) and p.delay > 8:
                p.delay = new_delay
                # If already mid-countdown, clamp so it doesn't instantly vanish
                if p.stood > 0:
                    p.stood = min(p.stood, new_delay - 1)

    def start_dialogue(self, key, return_state="playing"):
        if key in STORY_DIALOGUES:
            self.dialogue_box  = DialogueBox(STORY_DIALOGUES[key])
            self.pending_state = return_state
            self.state         = "dialogue"

    def _altitude(self):
        return max(0.0, min(1.0, (self.player.rect.centerx - 100) / 9900))

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self._exit_to_menu(); return
                if event.type == pygame.KEYDOWN: self._handle_key(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == "settings":
                    mpos = event.pos
                    if self._settings_vol_slider.collidepoint(mpos):
                        self.music_volume = max(0.0, min(1.0, round((mpos[0]-self._settings_vol_slider.x)/max(1,self._settings_vol_slider.width),2)))
                        self._apply_volume(); self.settings_cursor = 0
                    elif self._settings_sfx_slider.collidepoint(mpos):
                        self.sfx_volume = max(0.0, min(1.0, round((mpos[0]-self._settings_sfx_slider.x)/max(1,self._settings_sfx_slider.width),2)))
                        self._apply_volume(); self.settings_cursor = 1
                    else:
                        for i, rect in enumerate(self._settings_boxes):
                            if rect.collidepoint(mpos):
                                self.settings_cursor = i
                                if i == 2: self.music_muted = not self.music_muted; self._apply_volume()
                                elif i == 3:
                                    dl=["easy","medium","hard"]; self.difficulty=dl[(dl.index(self.difficulty)+1)%3]
                                    self._apply_difficulty()
                                elif i == 4: self.state = "playing"
                                elif i == 5: self.load_level(); self.state="playing"; self.sfx.start_music(volume=self.music_volume)
            if not self.running: return
            # Settings mouse clicks
            if self.state == "settings":
                pass  # handled inline via _settings_boxes in _draw_settings
            if self.freeze_frames > 0:
                self.freeze_frames -= 1
            elif self.state == "playing" and self.soul_state is not None:
                self._update_soul(); self.tick += 1
            elif self.state == "playing":
                self._update()
            elif self.state == "win":
                self.win_timer += 1
            elif self.state in ("dialogue", "ending"):
                if self.dialogue_box: self.dialogue_box.update()
            if self.respawn_fade > 0: self.respawn_fade -= 1
            self._draw()
            self.clock.tick(FPS)

    def _handle_key(self, key):
        if self.state in ("dialogue", "ending"):
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                if self.dialogue_box:
                    self.dialogue_box.advance()
                    if not self.dialogue_box.active:
                        self.dialogue_box = None
                        if self.state == "ending": self._exit_to_menu()
                        else: self.state = self.pending_state or "playing"
            return
        if self.state == "settings":
            n = 6
            if key == pygame.K_ESCAPE: self.state = "playing"
            elif key in (pygame.K_UP,   pygame.K_w): self.settings_cursor = (self.settings_cursor-1)%n
            elif key in (pygame.K_DOWN, pygame.K_s): self.settings_cursor = (self.settings_cursor+1)%n
            elif key in (pygame.K_LEFT, pygame.K_a):
                if self.settings_cursor == 0:
                    self.music_volume = max(0.0, round(self.music_volume-0.1,1)); self._apply_volume()
                elif self.settings_cursor == 1:
                    self.sfx_volume = max(0.0, round(self.sfx_volume-0.1,1)); self._apply_volume()
                elif self.settings_cursor == 3:
                    dl=["easy","medium","hard"]; self.difficulty=dl[(dl.index(self.difficulty)-1)%3]
                    self._apply_difficulty()
            elif key in (pygame.K_RIGHT, pygame.K_d):
                if self.settings_cursor == 0:
                    self.music_volume = min(1.0, round(self.music_volume+0.1,1)); self._apply_volume()
                elif self.settings_cursor == 1:
                    self.sfx_volume = min(1.0, round(self.sfx_volume+0.1,1)); self._apply_volume()
                elif self.settings_cursor == 3:
                    dl=["easy","medium","hard"]; self.difficulty=dl[(dl.index(self.difficulty)+1)%3]
                    self._apply_difficulty()
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if   self.settings_cursor == 2: self.music_muted = not self.music_muted; self._apply_volume()
                elif self.settings_cursor == 4: self.state = "playing"
                elif self.settings_cursor == 5:
                    self.load_level(); self.state = "playing"; self.sfx.start_music(volume=self.music_volume)
            return
        if self.state == "win":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                if not self.ending_shown:
                    self.ending_shown = True
                    self.start_dialogue("ending", "ending_done")
                    self.state = "ending"
                else: self._exit_to_menu()
            return
        # Playing
        if key == pygame.K_ESCAPE:
            self.state = "settings"; self.settings_cursor = 3
        elif key == pygame.K_r:
            self.player.hearts = 0
            self.player.die(); self.sfx.play("death")
        elif key == pygame.K_e:
            for npc in self.npcs:
                if npc.check_proximity(self.player) and not npc.talked:
                    npc.talked = True; self.sfx.play("npc_talk")
                    self.start_dialogue(npc.dialogue_key); break
        elif key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            if not self.player.on_ground and self.player.alive:
                self.player.start_dash()
        elif key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            if self.player.alive:
                if self.player.wall_sliding:
                    self.player.vel_y = JUMP_VELOCITY * 0.9
                    self.player.vel_x = -self.player.wall_side * 10
                    self.player.jump_count = 1; self.player.wall_sliding = False
                    self.player.facing_right = (self.player.wall_side < 0)
                    self.sfx.play("jump")
                    wx = self.player.rect.left if self.player.wall_side == -1 else self.player.rect.right
                    for _ in range(6):
                        self.particles.append(Particle(
                            wx, self.player.rect.centery + random.randint(-8, 8),
                            random.choice([WHITE, ICE_BLUE, SNOW_WHITE]),
                            -self.player.wall_side * random.uniform(1, 3),
                            random.uniform(-2, 1), 15, 3, 0.1))

    def _update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()
        for p in self.platforms:
            was_solid = isinstance(p, CollapsingPlatform) and not p.collapsed and p.stood > 0
            p.update()
            if was_solid and isinstance(p, CollapsingPlatform) and p.collapsed:
                self.sfx.play("crumble")
        for w in self.winds:     w.update()
        for sb in self.saw_blades: sb.update()
        for k in self.kunais:    k.update()
        for fp in self.frost_puffs: fp.update()
        for sm in self.stomp_monsters: sm.update()

        result = self.player.update(keys, self.platforms)
        if result == "jump": self.sfx.play("jump")
        if self.player.alive:
            self.camera.update(self.player.rect)
        for w in self.winds: w.apply_to_player(self.player)

        def _do_damage():
            if self.player.take_damage():
                if self.player.alive:
                    self.camera.add_shake(10); self.damage_flashes.append(DamageFlash())
                    self.sfx.play("hit"); self.player.vel_y = -5
                else:
                    self._player_death_fx(); self.sfx.play("death")

        for sb in self.saw_blades:
            if sb.check_hit(self.player) and self.player.alive:
                self.player.vel_x = 8*(1 if self.player.rect.centerx>sb.rect.centerx else -1)
                _do_damage()
        for kn in self.kunais:
            kn.check_player_below(self.player)
            if kn.check_hit(self.player):
                kn.state = "done"
                _do_damage()
        for fp in self.frost_puffs:
            if fp.check_hit(self.player):
                _do_damage()

        for sm in self.stomp_monsters:
            if not sm.alive: continue
            if sm.check_stomp(self.player):
                sm.kill()
                self.player.vel_y = StompMonster.BOUNCE_VEL
                self.player.jump_count = 1
                self.player.on_ground = False
                self.camera.add_shake(5)
                self.rings.append(RingEffect(sm.rect.centerx, sm.rect.centery, STAR_GOLD, 60, 4, 2))
                for _ in range(14):
                    a = random.uniform(0, math.pi*2); s = random.uniform(2, 5)
                    self.particles.append(Particle(sm.rect.centerx, sm.rect.centery,
                        random.choice([STAR_GOLD, WHITE, (160,200,255)]),
                        math.cos(a)*s, math.sin(a)*s, 25, random.randint(3,6), 0.1))
                self.score_popups.append((sm.rect.centerx, sm.rect.top-20, "STOMP!", 55, STAR_GOLD))
                self.sfx.play("stomp")
            elif sm.check_side_hit(self.player):
                _do_damage()

        self.stomp_monsters = [sm for sm in self.stomp_monsters
                               if sm.alive or sm.death_timer > 0]

        for cp in self.checkpoints:
            cp.update()
            if self.player.alive and cp.check(self.player):
                self.sfx.play("checkpoint"); self._cp_fx(cp)
        for npc in self.npcs:
            npc.proximity_shown = npc.check_proximity(self.player)
        for st in self.stars_list:
            if st.check(self.player):
                self.player.star_count += 1; self.sfx.play("star"); self._star_fx(st)
                self.score_popups.append((st.x, st.y-20, f"+STAR x{self.player.star_count}", 55, STAR_GOLD))

        self.exit_door.update()
        if self.player.alive and self.exit_door.check(self.player):
            self.state = "win"; self.sfx.play("win"); self.sfx.stop_music()

        self.particles      = [p for p in self.particles if p.update()]
        self.rings          = [r for r in self.rings     if r.update()]
        self.flashes        = [f for f in self.flashes   if f.update()]
        self.damage_flashes = [d for d in self.damage_flashes if d.update()]
        self.score_popups   = [(x,y-0.8,t,ti-1,c) for x,y,t,ti,c in self.score_popups if ti>0]

        # Landing burst + footstep particles
        if self.player.alive:
            if self.player.on_ground and not self.player.was_on_ground:
                for _ in range(8):
                    self.particles.append(Particle(
                        self.player.rect.centerx+random.randint(-10,10), self.player.rect.bottom,
                        SNOW_WHITE, random.uniform(-2.5,2.5), random.uniform(-1.5,0),
                        18, random.randint(2,4), 0.1))
            if self.player.on_ground and abs(self.player.vel_x) > 1 and self.tick % 5 == 0:
                self.particles.append(Particle(
                    self.player.rect.centerx+random.randint(-4,4), self.player.rect.bottom,
                    SNOW_WHITE, random.uniform(-0.5,0.5), random.uniform(-1,-0.2),
                    14, 2, 0.06))

        if self.player.alive and self.player.on_ground and not self.player.was_on_ground:
            for _ in range(6):
                self.particles.append(Particle(
                    self.player.rect.centerx+random.randint(-10,10), self.player.rect.bottom,
                    SNOW_WHITE, random.uniform(-2,2), random.uniform(-1,0.5), 16, random.randint(2,4), 0.1))

        self._spawn_ambient()

        if not self.player.alive and self.soul_state is None:
            # With sprites: wait for death animation done flag before rising
            death_ready = (not _SPRITES_AVAILABLE) or getattr(self.player, '_spr_death_done', False)
            if death_ready and self.player.respawn_timer > 0:
                self.player.respawn_timer = 9999
                self.soul_x = float(self.player.rect.centerx)
                self.soul_y = float(self.player.rect.centery)
                self.soul_target_y = self.player.rect.centery - 140
                self.soul_timer = 0; self.soul_trail = []
                self.soul_state = "rising"; self.sfx.play("soul_rise")
        self.level_time += 1

    def _player_death_fx(self):
        cx, cy = self.player.rect.center
        self.camera.add_shake(18); self.flashes.append(FlashOverlay(RED, 18, 120))
        for _ in range(35):
            a = random.uniform(0, math.pi*2); s = random.uniform(2, 7)
            self.particles.append(Particle(cx, cy,
                random.choice([(255,180,80),(255,240,160),(255,140,100),WHITE]),
                math.cos(a)*s, math.sin(a)*s, random.randint(25,50), random.randint(3,7), 0.15))

    def _star_fx(self, st):
        self.rings.append(RingEffect(st.x, st.y, STAR_GOLD, 50, 4, 2))
        for _ in range(12):
            a = random.uniform(0, math.pi*2); s = random.uniform(1, 3)
            self.particles.append(Particle(st.x, st.y, STAR_GOLD, math.cos(a)*s, math.sin(a)*s, 20, 3, 0.05))

    def _cp_fx(self, cp):
        cx, cy = cp.rect.centerx, cp.rect.top
        self.rings.append(RingEffect(cx, cy, XMAS_GOLD, 60, 3, 2))
        for _ in range(20):
            a = random.uniform(0, math.pi*2); s = random.uniform(1, 3)
            self.particles.append(Particle(cx, cy,
                random.choice([XMAS_GOLD, WHITE, (120,210,170), (255,180,220)]),
                math.cos(a)*s, math.sin(a)*s, 28, 3, 0.05))

    def _spawn_ambient(self):
        for plat in self.platforms:
            if isinstance(plat, IcePlatform) and random.random() < 0.06:
                self.particles.append(Particle(
                    plat.rect.x+random.randint(0,plat.rect.width), plat.rect.y-2,
                    (205,238,255), random.uniform(-0.4,0.4), random.uniform(-1.2,-0.2),
                    random.randint(12,22), 2, 0.0))
            elif isinstance(plat, TeleportPlatform) and plat.flash > 0:
                for _ in range(3):
                    self.particles.append(Particle(
                        plat.rect.x+random.randint(0,plat.rect.width),
                        plat.rect.y+random.randint(0,plat.rect.height),
                        XMAS_GOLD, random.uniform(-3,3), random.uniform(-3,3), 15))

    def _update_soul(self):
        self.soul_timer += 1
        if self.soul_state != "panning":
            for _ in range(2):
                a = random.uniform(0, math.pi*2); d = random.uniform(8, 20)
                self.particles.append(Particle(
                    self.soul_x+math.cos(a)*d, self.soul_y+math.sin(a)*d,
                    (255,210,80), random.uniform(-0.5,0.5), random.uniform(-1,0),
                    random.randint(12,20), random.randint(1,3), 0.02))
        if self.soul_state == "rising":
            t = min(1.0, self.soul_timer/40); ease = t*t*(3-2*t)
            self.soul_y = self.player.rect.centery - ease*140
            self.soul_x = self.player.rect.centerx + math.sin(self.soul_timer*0.15)*12
            self.soul_trail.append((self.soul_x, self.soul_y, 255))
            if len(self.soul_trail)>20: self.soul_trail.pop(0)
            self.soul_trail = [(x,y,a-10) for x,y,a in self.soul_trail if a>10]
            if self.soul_timer >= 40:
                self.soul_state="panning"; self.soul_timer=0; self.soul_trail=[]
                self.soul_pan_target_x = self.player.spawn_x+Player.WIDTH//2-self.camera.width//2
                self.soul_pan_target_y = self.player.spawn_y+Player.HEIGHT//2-self.camera.height//2
        elif self.soul_state == "panning":
            dx = self.soul_pan_target_x - self.camera.offset_x
            dy = self.soul_pan_target_y - self.camera.offset_y
            self.camera.offset_x += dx*0.12; self.camera.offset_y += dy*0.08
            if self.soul_timer >= 20 and abs(dx)<8 and abs(dy)<8:
                self.soul_state="falling"; self.soul_timer=0
                self.soul_x = float(self.player.spawn_x+Player.WIDTH//2)
                self.soul_y = self.camera.offset_y - 60
                self.soul_target_y = float(self.player.spawn_y+Player.HEIGHT//2)
                self.soul_trail=[]; self.sfx.play("soul_land")
        elif self.soul_state == "falling":
            t = min(1.0, self.soul_timer/35); ease = t*t*(3-2*t)
            self.soul_y = -50 + (self.soul_target_y+50)*ease
            self.soul_x = (self.player.spawn_x+Player.WIDTH//2) + math.sin(t*math.pi)*30
            self.soul_trail.append((self.soul_x, self.soul_y, 255))
            if len(self.soul_trail)>20: self.soul_trail.pop(0)
            self.soul_trail = [(x,y,a-10) for x,y,a in self.soul_trail if a>10]
            if self.soul_timer >= 35:
                self.player.respawn_timer=0; self.player.respawn()
                self.sfx.play("respawn"); self.respawn_fade=20
                self.flashes.append(FlashOverlay(WHITE, 12, 160))
                self._rebuild_monsters()
                for _ in range(25):
                    a = random.uniform(0, math.pi*2); s = random.uniform(2,7)
                    self.particles.append(Particle(self.soul_x, self.soul_target_y,
                        random.choice([WHITE,SNOW_WHITE,ICE_BLUE,XMAS_GOLD]),
                        math.cos(a)*s, math.sin(a)*s, 30, random.randint(3,7), 0.1))
                self.rings.append(RingEffect(int(self.soul_x), int(self.soul_target_y), WHITE, 100, 6, 3))
                self.soul_state=None; self.soul_trail=[]
                self.camera.update(self.player.rect)
        self.particles = [p for p in self.particles if p.update()]
        self.rings     = [r for r in self.rings     if r.update()]
        self.flashes   = [f for f in self.flashes   if f.update()]

    def _draw_soul(self):
        if self.soul_state is None: return
        dim_a = int(80+20*math.sin(self.soul_timer*0.12))
        dim = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
        dim.fill((0,0,0,dim_a)); self.screen.blit(dim,(0,0))
        if self.soul_state == "panning": return
        sp = self.camera.apply(pygame.Rect(int(self.soul_x),int(self.soul_y),1,1))
        for i,(sx,sy,sa) in enumerate(self.soul_trail):
            tp = self.camera.apply(pygame.Rect(int(sx),int(sy),1,1))
            frac=(i+1)/max(1,len(self.soul_trail)); r=max(2,int(10*frac))
            al=max(0,min(255,int(sa*0.4*frac)))
            ts=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(ts,(255,255,255,al),(r,r),r)
            self.screen.blit(ts,(tp.x-r,tp.y-r))
        for gr,ga in [(40,40),(28,80),(18,160)]:
            gs=pygame.Surface((gr*2,gr*2),pygame.SRCALPHA)
            pygame.draw.circle(gs,(255,255,255,ga),(gr,gr),gr)
            self.screen.blit(gs,(sp.x-gr,sp.y-gr))
        pygame.draw.circle(self.screen, WHITE, (sp.x,sp.y), 8)
        pygame.draw.circle(self.screen, (240,250,255), (sp.x-1,sp.y-1), 4)

    def _draw(self):
        self.screen.fill(DARK_BG)
        if self.state in ("playing","settings","dialogue","ending"):
            self._draw_game()
        if self.state == "settings": self._draw_settings()
        elif self.state == "win":    self._draw_win()
        elif self.state in ("dialogue","ending"):
            if self.dialogue_box: self.dialogue_box.draw(self.screen, self.tick)
        if self.respawn_fade > 0:
            a = int(255*(1.0-abs(self.respawn_fade-10)/10.0))
            if a > 0:
                ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)); ov.fill(BLACK)
                ov.set_alpha(min(255,a)); self.screen.blit(ov,(0,0))
        pygame.display.flip()

    def _draw_background(self):
        top_col = (200, 230, 255); bot_col = (255, 220, 140)
        for y in range(0, SCREEN_HEIGHT, 2):
            col = lerp_color(top_col, bot_col, y/SCREEN_HEIGHT)
            pygame.draw.rect(self.screen, col, (0, y, SCREEN_WIDTH, 2))
        sun_x = SCREEN_WIDTH - 110; sun_y = 70
        pulse = abs(math.sin(self.tick*0.018))*6
        pygame.draw.circle(self.screen, (255,170,30), (sun_x,sun_y), int(38+pulse))
        pygame.draw.circle(self.screen, (255,220,60), (sun_x,sun_y), int(24+pulse*0.5))
        pygame.draw.circle(self.screen, WHITE, (sun_x,sun_y), 10)
        for cloud in self.bg_clouds: cloud.draw(self.screen, self.camera)

    def _draw_game(self):
        self._draw_background()
        for w in self.winds:     w.draw(self.screen, self.camera)
        for p in self.platforms: p.draw(self.screen, self.camera)
        for cp in self.checkpoints: cp.draw(self.screen, self.camera)
        for npc in self.npcs:    npc.draw(self.screen, self.camera, self.tick)
        for st in self.stars_list: st.draw(self.screen, self.camera, self.tick)
        for sb in self.saw_blades: sb.draw(self.screen, self.camera, self.tick)
        for kn in self.kunais:   kn.draw(self.screen, self.camera, self.tick)
        for fp in self.frost_puffs: fp.draw(self.screen, self.camera, self.tick)
        for sm in self.stomp_monsters: sm.draw(self.screen, self.camera, self.tick)
        self.exit_door.draw(self.screen, self.camera)
        for p in self.particles: p.draw(self.screen, self.camera)
        for r in self.rings:     r.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.tick)
        for f in self.flashes:        f.draw(self.screen)
        for d in self.damage_flashes: d.draw(self.screen)
        for x,y,text,timer,color in self.score_popups:
            a=min(1.0,timer/30); c=tuple(max(0,min(255,int(v*a))) for v in color)
            pos=self.camera.apply(pygame.Rect(int(x),int(y),1,1))
            surf=self.small_font.render(text,True,c)
            self.screen.blit(surf,surf.get_rect(center=(pos.x,pos.y)))
        self._draw_hud()
        if self.soul_state is not None: self._draw_soul()

    def _draw_hud(self):
        def _hud_text(font, text, color, x, y):
            self.screen.blit(font.render(text,True,(0,0,0)),(x+1,y+1))
            self.screen.blit(font.render(text,True,color),(x,y))
        hud_x, hud_y = 12, 10
        for i in range(PLAYER_MAX_HEARTS):
            hx=hud_x+i*26; hy=hud_y; filled=i<self.player.hearts
            c=XMAS_RED if filled else (50,50,50)
            ps=int(abs(math.sin(self.tick*0.12))*2) if (i==0 and self.player.hearts==1 and self.player.alive) else 0
            for dx,dy,sc in [(1,1,(0,0,0)),(0,0,c)]:
                pygame.draw.circle(self.screen,sc,(hx+5+dx,hy+dy),5+ps)
                pygame.draw.circle(self.screen,sc,(hx+13+dx,hy+dy),5+ps)
                pygame.draw.polygon(self.screen,sc,[(hx-ps+dx,hy+2+dy),(hx+9+dx,hy+11+ps+dy),(hx+18+ps+dx,hy+2+dy)])
        dash_y=hud_y+18; dash_bw=60; dash_bh=5
        if self.player.dash_cooldown > 0:
            ratio=1.0-self.player.dash_cooldown/DASH_COOLDOWN
            pygame.draw.rect(self.screen,(30,30,40),(hud_x,dash_y,dash_bw,dash_bh))
            pygame.draw.rect(self.screen,CYAN,(hud_x,dash_y,int(dash_bw*ratio),dash_bh))
        else:
            pygame.draw.rect(self.screen,CYAN,(hud_x,dash_y,dash_bw,dash_bh))
        _hud_text(pygame.font.SysFont("consolas",9),"DASH",
                  (160,220,230) if self.player.dash_cooldown<=0 else (80,80,90), hud_x+dash_bw+4, dash_y-2)
        alt=self._altitude(); ab_w,ab_h=160,8; ab_x=SCREEN_WIDTH//2-ab_w//2; ab_y=10
        pygame.draw.rect(self.screen,(40,50,70),(ab_x-1,ab_y-1,ab_w+2,ab_h+2))
        for pi in range(int(ab_w*alt)):
            t=pi/ab_w; fc=lerp_color((255,180,50),(80,150,220),t)
            pygame.draw.line(self.screen,fc,(ab_x+pi,ab_y),(ab_x+pi,ab_y+ab_h))
        _hud_text(pygame.font.SysFont("consolas",8),"progress",(180,200,220),ab_x+ab_w+4,ab_y)
        _hud_text(self.tiny_font,f"Time: {self.level_time/FPS:.1f}s",SNOW_WHITE,SCREEN_WIDTH-145,10)
        _hud_text(self.tiny_font,f"Stars: {self.player.star_count}",STAR_GOLD,SCREEN_WIDTH-145,26)
        dc=((100,220,150) if self.difficulty=="easy" else (255,210,60) if self.difficulty=="medium" else (255,100,100))
        _hud_text(self.tiny_font,self.difficulty.upper(),dc,SCREEN_WIDTH-145,42)
        if not self.player.alive and self.soul_state is None:
            txt=self.font.render("Respawning...",True,XMAS_RED)
            self.screen.blit(txt,txt.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)))
        self.screen.blit(self.tiny_font.render(
            "R-Respawn  ESC-Settings  E-Talk  SHIFT-Dash(air)  SPACE-Jump  Wall:slide+jump",
            True,(80,100,130)),(10,SCREEN_HEIGHT-16))

    def _draw_settings(self):
        # Frosted glass overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 8, 5, 215))
        self.screen.blit(overlay, (0, 0))

        # Floating snowflake hints
        for i in range(12):
            sx2 = (80 + i * 110 + int(math.sin(self.tick * 0.02 + i * 1.3) * 25)) % SCREEN_WIDTH
            sy2 = (50 + i * 55 + int(math.sin(self.tick * 0.015 + i * 0.7) * 18)) % SCREEN_HEIGHT
            sz = 2 + int(abs(math.sin(self.tick * 0.03 + i)) * 2)
            sf_s = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
            pygame.draw.circle(sf_s, (255, 240, 220, 35), (sz+1, sz+1), sz)
            self.screen.blit(sf_s, (sx2 - sz, sy2 - sz))

        # Main panel
        panel_w, panel_h = 500, 550
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = 55
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (30, 15, 10, 210), (0, 0, panel_w, panel_h), border_radius=16)
        pygame.draw.rect(panel_surf, (255, 200, 50, 80), (0, 0, panel_w, panel_h), 2, border_radius=16)
        self.screen.blit(panel_surf, (panel_x, panel_y))

        # Corner ornament decorations
        for cx2, cy2 in [(panel_x+12, panel_y+12), (panel_x+panel_w-12, panel_y+12),
                          (panel_x+12, panel_y+panel_h-12), (panel_x+panel_w-12, panel_y+panel_h-12)]:
            pygame.draw.circle(self.screen, XMAS_RED,  (cx2, cy2), 6)
            pygame.draw.circle(self.screen, XMAS_GOLD, (cx2, cy2), 3)
            pygame.draw.circle(self.screen, WHITE,     (cx2, cy2), 1)

        # Title "PAUSED" with Christmas gold glow
        title_text = "PAUSED"
        title_surf = self.title_font.render(title_text, True, XMAS_GOLD)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 42))
        glow_a = int(abs(math.sin(self.tick * 0.04)) * 30) + 20
        glow_s = pygame.Surface((title_rect.width + 40, title_rect.height + 18), pygame.SRCALPHA)
        pygame.draw.rect(glow_s, (255, 200, 50, glow_a), (0, 0, glow_s.get_width(), glow_s.get_height()), border_radius=10)
        self.screen.blit(glow_s, (title_rect.x - 20, title_rect.y - 9))
        title_sh = self.title_font.render(title_text, True, (0, 0, 0))
        self.screen.blit(title_sh, title_sh.get_rect(center=(SCREEN_WIDTH//2+2, panel_y+44)))
        self.screen.blit(title_surf, title_rect)

        # Menu items
        items = [
            f"Music:  < {int(self.music_volume*100)}% >",
            f"SFX:    < {int(self.sfx_volume*100)}% >",
            f"Mute:   {'ON' if self.music_muted else 'OFF'}",
            f"Difficulty:  < {self.difficulty.upper()} >",
            "Resume",
            "Restart Level",
        ]
        item_colors = [SNOW_WHITE, SNOW_WHITE, SNOW_WHITE, SNOW_WHITE, XMAS_GREEN, XMAS_RED]

        start_y = panel_y + 80
        bar_w = 420; bar_h = 36
        slider_gap = 14

        mouse_pos = pygame.mouse.get_pos()
        mouse_moved = mouse_pos != self._last_mouse_pos
        self._last_mouse_pos = mouse_pos
        self._settings_boxes = []
        _item_y = []

        for i, item in enumerate(items):
            # Items 0 and 1 have a slider below them
            if i <= 1:
                y = start_y + i * (bar_h + slider_gap + 6)
            else:
                y = start_y + 2 * (bar_h + slider_gap + 6) + (i - 2) * (bar_h + 8)
            _item_y.append(y)
            bar_x = SCREEN_WIDTH // 2 - bar_w // 2
            bar = pygame.Rect(bar_x, y, bar_w, bar_h)
            self._settings_boxes.append(bar)
            if mouse_moved and bar.collidepoint(mouse_pos):
                self.settings_cursor = i
            sel = (i == self.settings_cursor)

            bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            if sel:
                pygame.draw.rect(bar_surf, (60, 30, 10, 190), (0, 0, bar_w, bar_h), border_radius=8)
                self.screen.blit(bar_surf, bar.topleft)
                pygame.draw.rect(self.screen, XMAS_GOLD, bar, 2, border_radius=8)
                color = item_colors[i]
            else:
                pygame.draw.rect(bar_surf, (40, 20, 10, 150), (0, 0, bar_w, bar_h), border_radius=8)
                self.screen.blit(bar_surf, bar.topleft)
                pygame.draw.rect(self.screen, (120, 70, 30, 80), bar, 1, border_radius=8)
                color = (200, 175, 130)

            # Icon per row
            icon_x = bar_x + 18; icon_cy = y + bar_h // 2
            if i == 0:
                # Music note
                pygame.draw.circle(self.screen, color, (icon_x+4, icon_cy+3), 4)
                pygame.draw.line(self.screen, color, (icon_x+8, icon_cy+3), (icon_x+8, icon_cy-8), 2)
                pygame.draw.line(self.screen, color, (icon_x+8, icon_cy-8), (icon_x+14, icon_cy-6), 2)
            elif i == 1:
                # Speaker
                pygame.draw.rect(self.screen, color, (icon_x, icon_cy-4, 6, 8))
                pygame.draw.polygon(self.screen, color, [(icon_x+6,icon_cy-4),(icon_x+12,icon_cy-8),(icon_x+12,icon_cy+8),(icon_x+6,icon_cy+4)])
                for sw in range(2):
                    ar = 5 + sw * 4
                    pygame.draw.arc(self.screen, color, (icon_x+13, icon_cy-ar, ar*2, ar*2), -0.6, 0.6, 1)
            elif i == 2:
                # Speaker + X for mute
                pygame.draw.rect(self.screen, color, (icon_x, icon_cy-4, 6, 8))
                pygame.draw.polygon(self.screen, color, [(icon_x+6,icon_cy-4),(icon_x+12,icon_cy-8),(icon_x+12,icon_cy+8),(icon_x+6,icon_cy+4)])
                if self.music_muted:
                    pygame.draw.line(self.screen, XMAS_RED, (icon_x+15,icon_cy-5),(icon_x+22,icon_cy+5), 2)
                    pygame.draw.line(self.screen, XMAS_RED, (icon_x+22,icon_cy-5),(icon_x+15,icon_cy+5), 2)
            elif i == 3:
                # Gear (difficulty)
                pygame.draw.circle(self.screen, color, (icon_x+8, icon_cy), 7, 2)
                pygame.draw.circle(self.screen, color, (icon_x+8, icon_cy), 3)
                for gi in range(6):
                    ga = gi * math.pi / 3 + self.tick * 0.02
                    gx = icon_x + 8 + int(9 * math.cos(ga))
                    gy = icon_cy + int(9 * math.sin(ga))
                    pygame.draw.circle(self.screen, color, (gx, gy), 2)
            elif i == 4:
                # Play triangle (resume)
                pygame.draw.polygon(self.screen, color, [(icon_x+3,icon_cy-7),(icon_x+3,icon_cy+7),(icon_x+15,icon_cy)])
            elif i == 5:
                # Restart arrow
                pygame.draw.arc(self.screen, color, (icon_x+2,icon_cy-7,14,14), 0.5, 5.5, 2)
                pygame.draw.polygon(self.screen, color, [(icon_x+14,icon_cy-7),(icon_x+14,icon_cy+1),(icon_x+19,icon_cy-3)])

            txt = self.small_font.render(item, True, color)
            self.screen.blit(txt, (bar_x+42, y+(bar_h-txt.get_height())//2))

        # Volume slider helper
        def _draw_slider(sy, volume, muted):
            sx = SCREEN_WIDTH // 2 - 150
            sw = 300; sh = 8
            pygame.draw.rect(self.screen, (40, 20, 10), (sx-2, sy-2, sw+4, sh+4), border_radius=5)
            fill_w = int(sw * volume)
            for px_i in range(fill_w):
                t2 = px_i / max(1, sw)
                vc = lerp_color(XMAS_GREEN, XMAS_RED, t2) if not muted else (60, 25, 10)
                pygame.draw.line(self.screen, vc, (sx+px_i, sy), (sx+px_i, sy+sh-1))
            pygame.draw.rect(self.screen, (100, 60, 30), (sx, sy, sw, sh), 1, border_radius=4)
            kx = sx + fill_w
            pygame.draw.circle(self.screen, WHITE,    (kx, sy+sh//2), 7)
            pygame.draw.circle(self.screen, XMAS_GOLD,(kx, sy+sh//2), 4)
            pct = self.small_font.render(f"{int(volume*100)}%", True, (180, 150, 110))
            self.screen.blit(pct, (sx+sw+14, sy-2))
            return pygame.Rect(sx, sy-4, sw, sh+8)

        self._settings_vol_slider = _draw_slider(_item_y[0]+bar_h+2, self.music_volume, self.music_muted)
        self._settings_sfx_slider = _draw_slider(_item_y[1]+bar_h+2, self.sfx_volume,   self.music_muted)

        # Difficulty description
        desc = {
            "easy":   "Easy: 2s before platforms fall. Relax and explore.",
            "medium": "Medium: 1s before platforms fall. Keep moving.",
            "hard":   "Hard: 0.5s before platforms fall. No hesitation.",
        }
        dc = (100,220,150) if self.difficulty=="easy" else (255,210,60) if self.difficulty=="medium" else (255,100,100)
        dt = self.tiny_font.render(desc[self.difficulty], True, dc)
        self.screen.blit(dt, dt.get_rect(center=(SCREEN_WIDTH//2, _item_y[3]+bar_h+5)))

        # Footer
        footer_text = "\u2191\u2193 Navigate    \u2190\u2192 Adjust    ENTER Select    ESC Resume"
        ft = self.small_font.render(footer_text, True, (130, 100, 70))
        ft_rect = ft.get_rect(center=(SCREEN_WIDTH//2, panel_y+panel_h-14))
        fb = pygame.Surface((ft_rect.width+30, ft_rect.height+10), pygame.SRCALPHA)
        pygame.draw.rect(fb, (0,0,0,80), (0,0,fb.get_width(),fb.get_height()), border_radius=10)
        self.screen.blit(fb, (ft_rect.x-15, ft_rect.y-5))
        self.screen.blit(ft, ft_rect)

    def _draw_win(self):
        self._draw_background()
        if self.win_timer%6==0:
            for _ in range(3):
                self.particles.append(Particle(
                    random.randint(200,SCREEN_WIDTH-200),random.randint(50,200),
                    random.choice([(255,220,60),(255,170,60),(255,250,180),WHITE,(120,210,255)]),
                    random.uniform(-2,2),random.uniform(1,3),60,random.randint(3,6),0.05))
        for p in self.particles: p.draw(self.screen,self.camera)
        self.particles=[p for p in self.particles if p.update()]
        wt=self.big_font.render("REALM 1 CLEARED!",True,(255,215,60))
        self.screen.blit(wt,wt.get_rect(center=(SCREEN_WIDTH//2,110)))
        t=self.level_time/FPS
        for surf,cy2 in [
            (self.font.render(f"Time:   {t:.1f} seconds",True,WHITE),220),
            (self.font.render(f"Stars:  {self.player.star_count}",True,STAR_GOLD),265),
            (self.font.render(f"Deaths: {self.player.death_count}",True,XMAS_RED),310),
        ]:
            self.screen.blit(surf,surf.get_rect(center=(SCREEN_WIDTH//2,cy2)))
        if t<90 and self.player.death_count==0: rank,rc="S",(255,215,60)
        elif t<150 and self.player.death_count<3: rank,rc="A",(100,220,100)
        elif t<240: rank,rc="B",ICE_BLUE
        else: rank,rc="C",GRAY
        rk=self.big_font.render(f"Rank: {rank}",True,rc)
        self.screen.blit(rk,rk.get_rect(center=(SCREEN_WIDTH//2,370)))
        hint=self.small_font.render("Press ENTER to continue...",True,SNOW_WHITE)
        hint.set_alpha(int(128+127*abs(math.sin(self.tick*0.05))))
        self.screen.blit(hint,hint.get_rect(center=(SCREEN_WIDTH//2,440)))


def launch_game():
    pygame.mixer.music.stop(); pygame.event.clear()
    game = Game(); game.run()
    pygame.event.clear()
    pygame.display.set_caption("Sky Climber")
    try:
        pygame.mixer.music.load("assets/audio/BackgroundMusic.mp3")
        pygame.mixer.music.play(-1)
    except Exception: pass


if __name__ == "__main__":
    pygame.init(); pygame.mixer.init()
    game = Game(); game.run(); pygame.quit()