"""
Sky Climber — Level 3  (Christmas Morning Edition)
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

_FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
TITLE_FONT_PATH = os.path.join(_FONT_DIR, "title_font.ttf")
BTN_FONT_PATH = os.path.join(_FONT_DIR, "button_font.ttf")
try:
    from player_sprites import init_player_sprite, draw_player_sprite
    _SPRITES_AVAILABLE = True
except ImportError:
    _SPRITES_AVAILABLE = False
from wood_ui import draw_wooden_bar, draw_wooden_panel, draw_wooden_slider

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
PLAT_CLOUD   = (210, 170, 120)
PLAT_MOVE    = (200, 140, 90)
PLAT_FALL    = (220, 130, 100)
PLAT_TELE    = (180, 110, 200)
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
DARK_BG      = (200, 120, 60)

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

# Snowball (mouse-aimed arc)
SNOWBALL_SPEED    = 11
SNOWBALL_GRAVITY  = 0.28
SNOWBALL_LIFETIME = 110
SNOWBALL_COOLDOWN = 22

# Coyote time + jump buffer
COYOTE_FRAMES      = 8
JUMP_BUFFER_FRAMES = 8

# Mini boss hits to kill (scales with difficulty)
BOSS_HITS   = {"easy": 3, "medium": 6, "hard": 9}
# Mini boss shot cooldown in frames
BOSS_SHOT_CD = {"easy": 180, "medium": 120, "hard": 60}

# Combo system
COMBO_EXPIRE = 90

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
        ("Zephyr", "Your body is in bed. Warm, safe. But your mind is locked here in the Third Realm until you break through."),
        ("Zephyr", "Four realms stand between you and waking up. This is the third — you're getting closer."),
        ("Zephyr", "MOVE: Arrow keys or WASD. SPACE to jump. SHIFT to sprint."),
        ("Zephyr", "DASH: Press SHIFT while airborne to dash forward. Great for crossing gaps fast."),
        ("Zephyr", "WALL SLIDE & JUMP: Press into a wall while falling to slow down. Then SPACE to kick off."),
        ("Zephyr", "HEALTH: You have 3 hearts. Hazards take one and give you a moment of safety after."),
        ("Zephyr", "ICE PLATFORMS — slippery. WIND ZONES — sprint against them."),
        ("Zephyr", "STAR RINGS: Collect them for points."),
        ("Zephyr", "Press E near a guide to talk. ESC for settings. R to respawn."),
        ("Zephyr", "The Horizon Gate is at the far right. Run. One more realm is waiting."),
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
        ("Zephyr",  "You cleared the Third Realm. Well done, dreamer."),
        ("Nimbus",  "Horizon Gate is open. The Fourth Realm is already taking shape around you."),
        ("Solara",  "One realm remains. The hardest one. But you proved you can do this."),
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
    "shoot":      "shoot.wav",
    "boss_hit":   "stomp.wav",
    "boss_die":   "win.wav",
}

# Per-sound volume levels — keeps SFX under the music
SFX_VOLUMES = {
    "jump": 0.6, "death": 1.0, "hit": 0.8, "stomp": 0.7,
    "respawn": 0.7, "checkpoint": 1.0, "win": 1.0,
    "star": 0.35, "soul_rise": 0.7, "soul_land": 0.7,
    "crumble": 0.8, "npc_talk": 1.0,
    "shoot": 0.5, "boss_hit": 0.8, "boss_die": 1.0,
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
        self._cached = None
    def _build_cache(self):
        s = self.size
        puffs = [(0,0,s),(s,5,int(s*.8)),(-s,5,int(s*.75)),(int(s*1.8),10,int(s*.6))]
        # Determine bounding box
        min_x = min(ox-r for ox,oy,r in puffs) - 4
        max_x = max(ox+r for ox,oy,r in puffs) + 4
        min_y = min(oy-r for ox,oy,r in puffs) - 4
        max_y = max(oy+r for ox,oy,r in puffs) + 4
        w = max_x - min_x; h = max_y - min_y
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        ox_off = -min_x; oy_off = -min_y
        # Sunset-lit clouds: warm orange/peach tones with dark underbelly
        for ox, oy, r in puffs:
            pygame.draw.circle(surf, (120, 60, 50, 25), (ox+ox_off+2, oy+oy_off+4), r)
        for ox, oy, r in puffs:
            pygame.draw.circle(surf, (255, 190, 130), (ox+ox_off, oy+oy_off), r)
        for ox, oy, r in puffs[:3]:
            if r > 8:
                pygame.draw.circle(surf, (255, 220, 160), (ox+ox_off, oy+oy_off-r//3), max(1, int(r*0.7)))
        self._cached = surf
        self._cache_offset = (min_x, min_y)
    def draw(self, surface, camera):
        if self._cached is None: self._build_cache()
        sx = int(self.x - camera.offset_x * self.speed) + self._cache_offset[0]
        sy = int(self.y - camera.offset_y * 0.05) + self._cache_offset[1]
        if sx > SCREEN_WIDTH + 20 or sx + self._cached.get_width() < -20: return
        surface.blit(self._cached, (sx, sy))


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
            font = pygame.font.Font(TITLE_FONT_PATH,10)
            tag  = font.render(self.name, True, (255, 200, 60))
            surface.blit(tag, (bx+12-tag.get_width()//2, by-14))
            exc_pulse = abs(math.sin(tick * 0.12)) * 0.5 + 0.5
            exc_c = lerp_color((255, 200, 50), (255, 240, 120), exc_pulse)
            ef = pygame.font.Font(TITLE_FONT_PATH,13 + int(exc_pulse * 2))
            exc = ef.render("!", True, exc_c)
            surface.blit(exc, (bx+12-exc.get_width()//2, by-27))
        if self.proximity_shown and not self.talked:
            font2 = pygame.font.Font(TITLE_FONT_PATH,11)
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
        fn = pygame.font.Font(TITLE_FONT_PATH,17)
        ft = pygame.font.Font(TITLE_FONT_PATH,14)
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
        pg_f = pygame.font.Font(TITLE_FONT_PATH,11)
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
        # Rich wooden plank body bathed in sunset warmth
        body_col = lerp_color(self.color, (160, 100, 60), 0.35)
        pygame.draw.rect(surface, body_col, sr, border_radius=10)
        # Plank grain lines
        rng = random.Random(self.rect.x * 31 + self.rect.y * 17)
        grain_col = lerp_color(body_col, (120, 70, 40), 0.25)
        for gi in range(sr.x + 6, sr.right - 6, max(12, sr.width // 5)):
            pygame.draw.line(surface, grain_col, (gi, sr.y+4), (gi, sr.bottom-2), 1)
        # Top snow cap with sunset-pink tint
        snow_pts = [(sr.x-2, sr.y+4)]
        for bx in range(sr.x, sr.right+6, 8):
            bump = rng.randint(3, 7)
            snow_pts.append((bx, sr.y - bump))
        snow_pts.append((sr.right+2, sr.y+4))
        if len(snow_pts) >= 3:
            pygame.draw.polygon(surface, (255, 225, 210), snow_pts)       # sunset-kissed snow
            pygame.draw.polygon(surface, (255, 200, 180), snow_pts, 1)    # warm outline
        # Golden sunset highlight on top
        hi = lerp_color(body_col, (255, 200, 100), 0.5)
        pygame.draw.rect(surface, hi, (sr.x+4, sr.y+3, sr.width-8, 4), border_radius=3)
        # Right edge warm sunlight
        sun_edge = lerp_color(body_col, (255, 180, 80), 0.45)
        pygame.draw.rect(surface, sun_edge, (sr.right-4, sr.y+5, 3, sr.height-10), border_radius=2)
        # Left edge deep shadow
        shadow = lerp_color(body_col, (60, 35, 25), 0.4)
        pygame.draw.rect(surface, shadow, (sr.x+1, sr.y+5, 3, sr.height-10), border_radius=2)
        # Bottom edge
        bot_col = lerp_color(body_col, (70, 40, 25), 0.35)
        pygame.draw.line(surface, bot_col, (sr.x+4, sr.bottom-1), (sr.right-4, sr.bottom-1))
        # Christmas lights — glowing warm in the sunset
        if sr.width >= 80:
            lcs = [(255, 80, 60), (255, 200, 50), (80, 200, 80), (255, 140, 60), (255, 100, 140)]
            for i, lx in enumerate(range(sr.x + 8, sr.right - 8, 16)):
                ly = sr.bottom + 3 + int(math.sin(i * 0.9) * 2)
                if i > 0:
                    px2 = lx - 16; py2 = sr.bottom + 3 + int(math.sin((i-1) * 0.9) * 2)
                    pygame.draw.line(surface, (80, 45, 25), (px2, py2), (lx, ly), 1)
                c = lcs[i % len(lcs)]
                pygame.draw.circle(surface, c, (lx, ly), 3)
                pygame.draw.circle(surface, (255, 255, 220), (lx-1, ly-1), 1)
        # Holly leaf accents on platform edges
        if sr.width >= 50:
            for hx in [sr.x + 8, sr.right - 14]:
                pygame.draw.ellipse(surface, (40, 120, 50), (hx, sr.y+5, 6, 4))
                pygame.draw.circle(surface, (200, 40, 40), (hx+3, sr.y+4), 2)


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
        # Gift-wrapped moving platform — deep red with gold ribbon
        base = (170, 45, 35)
        pygame.draw.rect(surface, base, sr, border_radius=8)
        # Gold ribbon cross
        mid_x = sr.x + sr.width // 2
        mid_y = sr.y + sr.height // 2
        pygame.draw.rect(surface, (220, 180, 50), (mid_x-3, sr.y, 6, sr.height))
        pygame.draw.rect(surface, (220, 180, 50), (sr.x, mid_y-2, sr.width, 4))
        # Ribbon bow on top center
        pygame.draw.ellipse(surface, (240, 200, 60), (mid_x-8, sr.y-5, 8, 6))
        pygame.draw.ellipse(surface, (240, 200, 60), (mid_x+1, sr.y-5, 8, 6))
        pygame.draw.circle(surface, (255, 220, 80), (mid_x, sr.y-2), 3)
        # Sunset highlight on top edge
        hi = lerp_color(base, (255, 180, 80), 0.4)
        pygame.draw.rect(surface, hi, (sr.x+3, sr.y, sr.width-6, 3), border_radius=2)
        # Border glow
        pygame.draw.rect(surface, (200, 70, 50), sr, 2, border_radius=8)
        # Snow puffs on top
        rng = random.Random(self.sx * 17 + self.sy * 31)
        for bx in range(sr.x + 3, sr.right - 3, 10):
            bw = rng.randint(8, 14)
            pygame.draw.ellipse(surface, (255, 220, 200), (bx, sr.y - 4, bw, 6))


class IcePlatform(Platform):
    ICE_FRICTION = 0.96; ICE_ACCEL = 0.12
    def __init__(self, x, y, w, h=22):
        super().__init__(x, y, w, h, PLAT_ICE); self.tick = 0
    def on_player_land(self, player): player.on_ice = True
    def update(self): self.tick += 1
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH+10: return
        # Sunset-tinted ice — amber reflections on frozen surface
        ice_base = (180, 170, 200)
        pygame.draw.rect(surface, ice_base, sr, border_radius=10)
        # Warm sunset reflection on top
        hi = (230, 190, 160)
        pygame.draw.rect(surface, hi, (sr.x+3, sr.y, sr.width-6, 6), border_radius=4)
        # Amber sparkles
        for i in range(5):
            phase = (self.tick*0.09 + i*1.3) % (2*math.pi)
            bri = abs(math.sin(phase))
            sx2 = sr.x + 8 + i*max(1, (sr.width-16)//4)
            sy2 = sr.y + 5 + int(math.sin(i+self.tick*0.05)*3)
            sc = (int(220+35*bri), int(180+40*bri), int(120+60*bri))
            pygame.draw.circle(surface, sc, (sx2, sy2), 2)
        # Icicles with warm tips from sunset light
        rng = random.Random(self.rect.x*13 + self.rect.y*7)
        for ix in range(sr.x+6, sr.right-6, max(1, sr.width//5)):
            ih = rng.randint(5, 12)
            iw = rng.randint(2, 4)
            pts = [(ix-iw, sr.bottom), (ix+iw, sr.bottom), (ix, sr.bottom+ih)]
            pygame.draw.polygon(surface, (200, 190, 220), pts)
            pygame.draw.polygon(surface, (230, 210, 200), pts, 1)
        pygame.draw.rect(surface, (160, 140, 170), sr, 1, border_radius=10)
        font = pygame.font.Font(TITLE_FONT_PATH,9)
        lbl  = font.render("ICE", True, (200, 160, 130))
        surface.blit(lbl, (sr.centerx-lbl.get_width()//2, sr.y+7))


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
            col = lerp_color(self.base_color, (255, 80, 30), r)
        else:
            col = self.base_color
        # Main body — warm gingerbread style
        pygame.draw.rect(surface, col, sr, border_radius=8)
        # Frosting/icing decoration on top
        rng = random.Random(self.rect.x*13 + self.rect.y*7)
        if self.stood == 0:
            frost_col = (255, 220, 190)
            frost_pts = [(sr.x+2, sr.y+3)]
            for fx in range(sr.x+4, sr.right-2, 6):
                drip = rng.randint(0, 4)
                frost_pts.append((fx, sr.y - 2 + drip))
            frost_pts.append((sr.right-2, sr.y+3))
            if len(frost_pts) >= 3:
                pygame.draw.polygon(surface, frost_col, frost_pts)
        # Warm sunset highlight on top
        hi = lerp_color(col, (255, 200, 100), 0.4)
        pygame.draw.rect(surface, hi, (sr.x+4, sr.y+1, sr.width-8, 3), border_radius=2)
        # Decorative dots (candy buttons) when not crumbling
        if self.stood == 0:
            dot_cols = [(255, 80, 60), (255, 200, 50), (80, 180, 80)]
            for i, dx in enumerate(range(sr.x+8, sr.right-8, max(14, sr.width//4))):
                pygame.draw.circle(surface, dot_cols[i % len(dot_cols)], (dx, sr.centery), 3)
                pygame.draw.circle(surface, (255, 240, 220), (dx-1, sr.centery-1), 1)
        # Plank grain
        grain_col = lerp_color(col, (80, 40, 20), 0.2)
        for gi in range(sr.x+8, sr.right-8, max(10, sr.width//4)):
            pygame.draw.line(surface, grain_col, (gi, sr.y+4), (gi, sr.bottom-2), 1)
        # Dark edges
        shadow = lerp_color(col, (50, 25, 10), 0.4)
        pygame.draw.rect(surface, shadow, (sr.x+1, sr.y+4, 2, sr.height-8), border_radius=1)
        bot_col = lerp_color(col, (60, 30, 15), 0.35)
        pygame.draw.line(surface, bot_col, (sr.x+4, sr.bottom-1), (sr.right-4, sr.bottom-1))
        # Crack lines when close to breaking
        if self.stood > self.delay*0.3:
            crack_r = min(1.0, (self.stood - self.delay*0.3) / (self.delay*0.7))
            crack_col = lerp_color(col, (30, 10, 5), crack_r*0.7)
            for ci in range(int(3 + crack_r*5)):
                cx2 = sr.x + rng.randint(6, max(7, sr.width-6))
                cy2 = sr.y + rng.randint(2, max(3, sr.height-2))
                clen = rng.randint(4, int(8 + crack_r*12))
                ca = rng.uniform(-0.6, 0.6)
                ex = cx2 + int(math.cos(ca)*clen)
                ey = cy2 + int(math.sin(ca)*clen)
                pygame.draw.line(surface, crack_col, (cx2,cy2), (ex,ey), max(1, int(1+crack_r*2)))
        # Warning symbol when about to fall (blink on/off)
        if self.stood > self.delay*0.7 and (self.stood // 4) % 2 == 0:
            wx, wy = sr.centerx, sr.y - 10
            pygame.draw.polygon(surface, (255, 200, 40), [(wx, wy-8), (wx-7, wy+5), (wx+7, wy+5)])
            pygame.draw.line(surface, (60, 30, 10), (wx, wy-4), (wx, wy+1), 2)
            pygame.draw.circle(surface, (60, 30, 10), (wx, wy+3), 1)
        # Countdown bar
        if self.stood > 0 and sr.width > 8:
            ratio = max(0.0, 1.0 - (self.stood / self.delay))
            bar_w = int((sr.width - 8) * ratio)
            bar_col = lerp_color((100, 220, 80), (255, 50, 30),
                                 min(1.0, self.stood / self.delay))
            pygame.draw.rect(surface, (30, 15, 10), (sr.x+4, sr.bottom-5, sr.width-8, 4), border_radius=2)
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
        font=pygame.font.Font(TITLE_FONT_PATH,11)
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
        # Color per monster (based on spawn position)
        orn_cols = [(210, 50, 50), (50, 180, 80), (60, 100, 220), (200, 60, 180), (220, 160, 30)]
        orn_idx = int(self.base_y * 7 + self.patrol_x1) % len(orn_cols)
        body_col = orn_cols[orn_idx]
        body_hi = tuple(min(c+80, 255) for c in body_col)
        flap = int(math.sin(self.tick * 0.25) * 5)
        wing_col = lerp_color(body_col, (40,30,50), 0.5)
        # Bat-like wings (direct draw, no SRCALPHA)
        for side in [-1, 1]:
            wx = cx + side * (sr.width//2 + 5)
            pts = [(cx + side*sr.width//2, cy+flap),
                   (wx, cy-6+flap), (wx-side*4, cy+6+flap)]
            pygame.draw.polygon(surface, wing_col, pts)
        # Ornament body — round with shine
        pygame.draw.ellipse(surface, body_col, (sr.x, sr.y, sr.width, sr.height))
        # Decorative stripe
        pygame.draw.ellipse(surface, body_hi, (sr.x+4, cy-3, sr.width-8, 6))
        # Shine highlight (top-left)
        pygame.draw.ellipse(surface, body_hi, (sr.x+5, sr.y+2, sr.width//3, sr.height//3))
        # Gold cap on top
        pygame.draw.rect(surface, (200, 180, 60), (cx-5, sr.y-5, 10, 6), border_radius=2)
        pygame.draw.circle(surface, (220, 200, 80), (cx, sr.y-6), 3)
        # Angry eyes
        if self.alive:
            ex1 = cx - 5 if self.dir >= 0 else cx + 1
            ex2 = ex1 + 6
            pygame.draw.circle(surface, (255, 255, 240), (ex1, cy-1), 4)
            pygame.draw.circle(surface, (255, 255, 240), (ex2, cy-1), 4)
            pd = 1 if self.dir >= 0 else -1
            pygame.draw.circle(surface, (30, 10, 10), (ex1+pd, cy), 2)
            pygame.draw.circle(surface, (30, 10, 10), (ex2+pd, cy), 2)
            brow_col = lerp_color(body_col, (40, 20, 20), 0.6)
            pygame.draw.line(surface, brow_col, (ex1-3, cy-5), (ex1+2, cy-3), 2)
            pygame.draw.line(surface, brow_col, (ex2+3, cy-5), (ex2-2, cy-3), 2)
            pygame.draw.line(surface, (180, 40, 40), (cx-4, cy+5), (cx, cy+7), 1)
            pygame.draw.line(surface, (180, 40, 40), (cx, cy+7), (cx+4, cy+5), 1)
        else:
            for ox, oy in [(-5,-2),(3,-2)]:
                bx2, by2 = cx+ox, cy+oy
                pygame.draw.line(surface, (255,80,80), (bx2-2,by2-2), (bx2+2,by2+2), 2)
                pygame.draw.line(surface, (255,80,80), (bx2+2,by2-2), (bx2-2,by2+2), 2)


# ── Snowball (mouse-aimed arc) ────────────────────────────────────────────
class Snowball:
    RADIUS = 5
    def __init__(self, x, y, vx, vy):
        self.x = float(x); self.y = float(y)
        self.vx = vx; self.vy = vy
        self.lifetime = SNOWBALL_LIFETIME; self.alive = True
        self.trail = []
    def update(self):
        if not self.alive: return False
        self.trail.append((self.x, self.y))
        if len(self.trail) > 7: self.trail.pop(0)
        self.x += self.vx; self.y += self.vy
        self.vy += SNOWBALL_GRAVITY
        self.lifetime -= 1
        if self.lifetime <= 0: self.alive = False
        return self.alive
    def get_rect(self):
        return pygame.Rect(int(self.x)-self.RADIUS, int(self.y)-self.RADIUS,
                           self.RADIUS*2, self.RADIUS*2)
    def draw(self, surface, camera, tick):
        if not self.alive: return
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            tp = camera.apply(pygame.Rect(int(tx), int(ty), 1, 1))
            a = int(120 * (i+1) / len(self.trail))
            ts = pygame.Surface((8,8), pygame.SRCALPHA)
            pygame.draw.circle(ts, (200, 230, 255, a), (4,4), 3)
            surface.blit(ts, (tp.x-4, tp.y-4))
        p = camera.apply(self.get_rect())
        # Glow
        gs = pygame.Surface((22,22), pygame.SRCALPHA)
        pygame.draw.circle(gs, (180, 220, 255, 70), (11,11), 10)
        surface.blit(gs, (p.x-5, p.y-5))
        pygame.draw.circle(surface, SNOW_WHITE, (p.centerx, p.centery), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (p.centerx-1, p.centery-1), 2)


# ── Mini Boss Projectile ──────────────────────────────────────────────────
class MiniBossProjectile:
    RADIUS = 5
    def __init__(self, x, y, vx, vy, color=(140,210,255)):
        self.x=float(x); self.y=float(y)
        self.vx=vx; self.vy=vy
        self.color=color; self.alive=True; self.lifetime=120
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.lifetime-=1
        if self.lifetime<=0: self.alive=False
        return self.alive
    def get_rect(self):
        return pygame.Rect(int(self.x)-self.RADIUS, int(self.y)-self.RADIUS,
                           self.RADIUS*2, self.RADIUS*2)
    def check_hit(self, player):
        return self.alive and player.alive and self.get_rect().colliderect(player.rect)
    def draw(self, surface, camera, tick):
        if not self.alive: return
        p = camera.apply(self.get_rect())
        pulse = abs(math.sin(tick*0.2))*0.4+0.6
        gs = pygame.Surface((18,18), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*self.color, int(80*pulse)), (9,9), 8)
        surface.blit(gs, (p.x-4, p.y-4))
        pygame.draw.circle(surface, self.color, (p.centerx, p.centery), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (p.centerx-1, p.centery-1), 2)


# ── Mini Boss base ────────────────────────────────────────────────────────
class MiniBoss:
    """Flying mini boss that spawns above its checkpoint and follows the player."""
    def __init__(self, spawn_x, spawn_y, hp, shot_cd):
        self.spawn_x = spawn_x
        self.cx = float(spawn_x)
        self.cy = float(spawn_y - 120)   # start 120px above checkpoint
        self.hp = hp; self.max_hp = hp
        self.shot_cd = shot_cd; self.shot_timer = random.randint(0, shot_cd)
        self.alive = True; self.death_timer = 0; self.tick = random.randint(0,120)
        self.hit_flash = 0
        self.projectiles = []
        self.phase = "descend"   # descend → active → retreat → dead
        self.target_y = float(spawn_y - 80)
        self.vel_x = 0.0; self.vel_y = 0.0
        self.W = 48; self.H = 48
        # Zone boundaries — boss only chases within [zone_left, zone_right)
        self.zone_left = -999999
        self.zone_right = 999999

    @property
    def rect(self):
        return pygame.Rect(int(self.cx)-self.W//2, int(self.cy)-self.H//2, self.W, self.H)

    def update(self, player):
        if not self.alive:
            self.death_timer -= 1
            for p in self.projectiles: p.update()
            self.projectiles = [p for p in self.projectiles if p.alive]
            return
        self.tick += 1
        if self.hit_flash > 0: self.hit_flash -= 1

        # Check if player has left this boss's zone → retreat
        player_in_zone = self.zone_left <= player.rect.centerx < self.zone_right

        if self.phase == "descend":
            # Glide down to target_y
            self.cy += (self.target_y - self.cy) * 0.06
            self.cx += (player.rect.centerx - self.cx) * 0.02
            if abs(self.cy - self.target_y) < 5:
                self.phase = "active"
            if not player_in_zone:
                self.phase = "retreat"

        elif self.phase == "active" and player.alive:
            if not player_in_zone:
                self.phase = "retreat"
            else:
                # Smooth follow with slight sine wobble
                dx = player.rect.centerx - self.cx
                dy = (player.rect.centery - 90) - self.cy
                self.cx += dx * 0.025 + math.sin(self.tick * 0.04) * 0.8
                self.cy += dy * 0.025 + math.cos(self.tick * 0.035) * 0.6

                # Shooting
                self.shot_timer -= 1
                if self.shot_timer <= 0:
                    self.shot_timer = self.shot_cd
                    self._shoot(player)

        elif self.phase == "retreat":
            # Fly back to spawn and hover there
            dx = self.spawn_x - self.cx
            dy = self.target_y - self.cy
            self.cx += dx * 0.06
            self.cy += dy * 0.06
            # If player comes back into zone, resume active
            if player_in_zone:
                self.phase = "active"

        for p in self.projectiles: p.update()
        self.projectiles = [p for p in self.projectiles if p.alive]

    def _shoot(self, player):
        """Override per boss type. Default: straight shot at player."""
        dx = player.rect.centerx - self.cx
        dy = player.rect.centery  - self.cy
        dist = max(1, math.sqrt(dx*dx+dy*dy))
        spd = 4.5
        self.projectiles.append(MiniBossProjectile(
            self.cx, self.cy, dx/dist*spd, dy/dist*spd))

    def hit(self):
        """Returns True if boss died."""
        self.hp -= 1; self.hit_flash = 10
        if self.hp <= 0:
            self.alive = False; self.death_timer = 40
            self.phase = "dead"
            return True
        return False

    def check_projectile_hits(self, player):
        for p in self.projectiles:
            if p.check_hit(player):
                p.alive = False
                return True
        return False

    def check_body_hit(self, player):
        return self.alive and self.phase != "retreat" and self.rect.colliderect(player.rect)

    def draw(self, surface, camera, tick):
        # Draw projectiles
        for p in self.projectiles: p.draw(surface, camera, tick)
        # Subclasses implement their own visual
        self._draw_body(surface, camera, tick)
        if not self.alive: return
        # HP bar
        sr = camera.apply(self.rect)
        if sr.right < -60 or sr.left > SCREEN_WIDTH + 60: return
        bar_w = 60; bar_h = 6
        bx = sr.centerx - bar_w//2; by = sr.y - 14
        pygame.draw.rect(surface, (50,20,20), (bx-1, by-1, bar_w+2, bar_h+2), border_radius=3)
        ratio = max(0, self.hp/self.max_hp)
        fc = lerp_color((220,50,50),(50,220,80), ratio)
        if int(bar_w*ratio) > 0:
            pygame.draw.rect(surface, fc, (bx, by, int(bar_w*ratio), bar_h), border_radius=3)
        # Hit flash ring
        if self.hit_flash > 0:
            hs = pygame.Surface((80,80), pygame.SRCALPHA)
            pygame.draw.circle(hs, (255,255,255, int(180*self.hit_flash/10)), (40,40), 36, 3)
            surface.blit(hs, (sr.centerx-40, sr.centery-40))

    def _draw_body(self, surface, camera, tick):
        pass  # override in subclasses


# ── 1. Snowman Boss ───────────────────────────────────────────────────────
class SnowmanBoss(MiniBoss):
    def __init__(self, spawn_x, spawn_y, hp, shot_cd):
        super().__init__(spawn_x, spawn_y, hp, shot_cd)
        self.W = 44; self.H = 56
    def _shoot(self, player):
        # Spread of 3 snowballs in a cone
        dx = player.rect.centerx - self.cx
        dy = player.rect.centery  - self.cy
        dist = max(1, math.sqrt(dx*dx+dy*dy))
        base_angle = math.atan2(dy, dx)
        for spread in [-0.25, 0, 0.25]:
            a = base_angle + spread
            spd = 4.0
            self.projectiles.append(MiniBossProjectile(
                self.cx, self.cy, math.cos(a)*spd, math.sin(a)*spd,
                color=(200, 235, 255)))
    def _draw_body(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -60 or sr.left > SCREEN_WIDTH+60: return
        cx, cy = sr.centerx, sr.centery
        alpha = 255 if self.alive else max(0, int(255*self.death_timer/40))
        bob = int(math.sin(self.tick*0.06)*4)
        # Body (lower ball)
        bs = pygame.Surface((50,50), pygame.SRCALPHA)
        pygame.draw.circle(bs, (230,245,255,alpha), (25,25), 22)
        pygame.draw.circle(bs, (200,225,245,alpha), (25,25), 22, 2)
        # Buttons
        for by2 in [18,25,32]:
            pygame.draw.circle(bs, (60,80,100,alpha), (25,by2), 3)
        surface.blit(bs, (cx-25, cy+bob))
        # Head (upper ball)
        hs = pygame.Surface((40,40), pygame.SRCALPHA)
        pygame.draw.circle(hs, (235,248,255,alpha), (20,20), 17)
        pygame.draw.circle(hs, (200,225,245,alpha), (20,20), 17, 2)
        # Eyes
        pygame.draw.circle(hs, (30,40,60,alpha), (14,16), 3)
        pygame.draw.circle(hs, (30,40,60,alpha), (26,16), 3)
        # Carrot nose
        pygame.draw.polygon(hs, (255,140,30), [(20,20),(16,22),(24,22)])
        surface.blit(hs, (cx-20, cy-32+bob))
        # Hat
        pygame.draw.rect(surface, (30,30,30), (cx-16, cy-56+bob, 32, 6))  # brim
        pygame.draw.rect(surface, (30,30,30), (cx-10, cy-72+bob, 20, 22)) # top
        pygame.draw.rect(surface, XMAS_RED,   (cx-10, cy-58+bob, 20, 5))  # band
        # Scarf
        pygame.draw.rect(surface, XMAS_RED, (cx-18, cy-14+bob, 36, 7), border_radius=3)
        # Arms (twig-like)
        pygame.draw.line(surface, (100,70,40), (cx-22, cy+bob+5), (cx-36, cy-10+bob), 3)
        pygame.draw.line(surface, (100,70,40), (cx+22, cy+bob+5), (cx+36, cy-10+bob), 3)


# ── 2. Evil Elf Boss ──────────────────────────────────────────────────────
class EvilElfBoss(MiniBoss):
    def __init__(self, spawn_x, spawn_y, hp, shot_cd):
        super().__init__(spawn_x, spawn_y, hp, shot_cd)
        self.W = 32; self.H = 44
    def _shoot(self, player):
        # Fast straight shot
        dx = player.rect.centerx - self.cx
        dy = player.rect.centery  - self.cy
        dist = max(1, math.sqrt(dx*dx+dy*dy))
        spd = 6.0
        self.projectiles.append(MiniBossProjectile(
            self.cx, self.cy, dx/dist*spd, dy/dist*spd,
            color=(50, 200, 80)))
    def _draw_body(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -60 or sr.left > SCREEN_WIDTH+60: return
        cx, cy = sr.centerx, sr.centery
        alpha = 255 if self.alive else max(0, int(255*self.death_timer/40))
        bob = int(math.sin(self.tick*0.09)*5)
        # Body
        bs = pygame.Surface((34,44), pygame.SRCALPHA)
        pygame.draw.polygon(bs, (*XMAS_RED,alpha), [(4,44),(30,44),(28,18),(6,18)])
        pygame.draw.polygon(bs, (*XMAS_GREEN,alpha), [(0,44),(34,44),(30,30),(4,30)])
        # Belt
        pygame.draw.rect(bs, (*XMAS_GOLD,alpha), (2,28,30,5))
        pygame.draw.rect(bs, (*DARK_BROWN,alpha), (13,26,8,7), border_radius=1)
        surface.blit(bs, (cx-17, cy-6+bob))
        # Head
        hs = pygame.Surface((28,28), pygame.SRCALPHA)
        pygame.draw.circle(hs, (220,185,155,alpha), (14,14), 12)
        # Evil eyes (narrow red)
        pygame.draw.ellipse(hs, (200,30,30,alpha), (4,9,8,5))
        pygame.draw.ellipse(hs, (200,30,30,alpha), (16,9,8,5))
        pygame.draw.circle(hs, (10,0,0,alpha), (8,11), 2)
        pygame.draw.circle(hs, (10,0,0,alpha), (20,11), 2)
        # Evil grin
        pygame.draw.arc(hs, (80,30,20,alpha), (5,15,18,8), math.pi, 2*math.pi, 2)
        surface.blit(hs, (cx-14, cy-32+bob))
        # Hat (pointed elf hat)
        hat_pts = [(cx-12,cy-32+bob),(cx+12,cy-32+bob),(cx,cy-56+bob)]
        pygame.draw.polygon(surface, XMAS_GREEN, hat_pts)
        pygame.draw.circle(surface, XMAS_GOLD, (cx, cy-56+bob), 4)
        # Wings (sparkly)
        wing_pulse = abs(math.sin(self.tick*0.15))*3
        for side in [-1,1]:
            wx = cx + side*20
            ws = pygame.Surface((28,20),pygame.SRCALPHA)
            pygame.draw.ellipse(ws, (180,255,180,int(160+wing_pulse*10)), (0,0,28,20))
            surface.blit(ws, (wx-14 if side<0 else wx-14, cy-10+bob))


# ── 3. Frost Wraith Boss ──────────────────────────────────────────────────
class FrostWraithBoss(MiniBoss):
    def __init__(self, spawn_x, spawn_y, hp, shot_cd):
        super().__init__(spawn_x, spawn_y, hp, shot_cd)
        self.W = 40; self.H = 56; self.phase_offset = random.uniform(0, math.pi*2)
    def _shoot(self, player):
        # Spread of 5 icicle shards in wide cone
        dx = player.rect.centerx - self.cx
        dy = player.rect.centery  - self.cy
        base_angle = math.atan2(dy, dx)
        for i in range(5):
            spread = -0.5 + i * 0.25
            a = base_angle + spread
            spd = 3.5 + abs(spread)*1.5
            self.projectiles.append(MiniBossProjectile(
                self.cx, self.cy, math.cos(a)*spd, math.sin(a)*spd,
                color=(160, 220, 255)))
    def _draw_body(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -60 or sr.left > SCREEN_WIDTH+60: return
        cx, cy = sr.centerx, sr.centery
        alpha = 255 if self.alive else max(0, int(255*self.death_timer/40))
        float_off = int(math.sin(self.tick*0.05 + self.phase_offset)*8)
        # Ghostly robe (semi-transparent wisp)
        for r2, a2 in [(28,int(60*alpha/255)),(22,int(100*alpha/255)),(16,int(alpha*0.7))]:
            gs2 = pygame.Surface((r2*2,r2*2),pygame.SRCALPHA)
            pygame.draw.ellipse(gs2, (160,220,255,a2), (0,0,r2*2,r2*2))
            surface.blit(gs2, (cx-r2, cy-10+float_off-r2+r2))
        # Robe tail wisps
        for i in range(3):
            wx = cx + (i-1)*12
            wy = cy + 18 + float_off + int(math.sin(tick*0.08+i)*6)
            ws = pygame.Surface((10,20),pygame.SRCALPHA)
            pygame.draw.ellipse(ws, (160,220,255,int(80*alpha/255)), (0,0,10,20))
            surface.blit(ws, (wx-5, wy))
        # Face (hollow dark)
        hs = pygame.Surface((30,30),pygame.SRCALPHA)
        pygame.draw.circle(hs, (180,230,255,alpha), (15,15), 13)
        # Hollow eyes
        pygame.draw.circle(hs, (20,40,80,alpha), (9,12), 4)
        pygame.draw.circle(hs, (20,40,80,alpha), (21,12), 4)
        # Glowing pupils
        pygame.draw.circle(hs, (100,200,255,alpha), (9,12), 2)
        pygame.draw.circle(hs, (100,200,255,alpha), (21,12), 2)
        # Wail mouth
        pygame.draw.ellipse(hs, (10,20,50,alpha), (8,18,14,7))
        surface.blit(hs, (cx-15, cy-28+float_off))
        # Ice crown
        for i in range(5):
            a = math.radians(-90 + i*45)
            px2 = cx + int(math.cos(a)*14)
            py2 = cy - 40 + float_off + int(math.sin(a)*4)
            pygame.draw.polygon(surface, (200,240,255),
                [(px2-3,py2+6),(px2+3,py2+6),(px2,py2-8)])


# ── 4. Gift Golem Boss ────────────────────────────────────────────────────
class GiftGolemBoss(MiniBoss):
    def __init__(self, spawn_x, spawn_y, hp, shot_cd):
        super().__init__(spawn_x, spawn_y, hp, shot_cd)
        self.W = 56; self.H = 56
    def _shoot(self, player):
        # Straight aimed shot + 2 side shots
        dx = player.rect.centerx - self.cx
        dy = player.rect.centery  - self.cy
        dist = max(1, math.sqrt(dx*dx+dy*dy))
        base_angle = math.atan2(dy, dx)
        for spread in [-0.3, 0, 0.3]:
            a = base_angle + spread
            spd = 4.5
            self.projectiles.append(MiniBossProjectile(
                self.cx, self.cy, math.cos(a)*spd, math.sin(a)*spd,
                color=(255, 180, 60)))
    def _draw_body(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -60 or sr.left > SCREEN_WIDTH+60: return
        cx, cy = sr.centerx, sr.centery
        alpha = 255 if self.alive else max(0, int(255*self.death_timer/40))
        bob = int(math.sin(self.tick*0.05)*4)
        # Main box body
        box_cols = [(220,50,50),(50,180,80),(60,100,220),(255,200,50)]
        bc = box_cols[(self.tick//60) % len(box_cols)]
        bs = pygame.Surface((56,50),pygame.SRCALPHA)
        pygame.draw.rect(bs, (*bc,alpha), (0,0,56,50), border_radius=4)
        # Ribbon vertical
        pygame.draw.rect(bs, (255,255,255,alpha), (24,0,8,50))
        # Ribbon horizontal
        pygame.draw.rect(bs, (255,255,255,alpha), (0,20,56,8))
        # Bow at top
        pygame.draw.circle(bs, (255,255,255,alpha), (28,0), 7)
        pygame.draw.circle(bs, (255,255,255,alpha), (18,0), 5)
        pygame.draw.circle(bs, (255,255,255,alpha), (38,0), 5)
        surface.blit(bs, (cx-28, cy-2+bob))
        # Stubby arms (flaps)
        for side in [-1,1]:
            ax = cx + side*34
            pygame.draw.ellipse(surface, (*bc,alpha), (ax-8 if side<0 else ax-8, cy+bob, 16,12))
        # Face on top half of box
        pygame.draw.circle(surface, (240,200,160), (cx, cy-16+bob), 14)
        # Angry brows
        pygame.draw.line(surface, (60,30,20), (cx-12,cy-24+bob),(cx-4,cy-20+bob),3)
        pygame.draw.line(surface, (60,30,20), (cx+4,cy-20+bob),(cx+12,cy-24+bob),3)
        # Eyes
        pygame.draw.circle(surface, BLACK, (cx-6,cy-15+bob), 3)
        pygame.draw.circle(surface, BLACK, (cx+6,cy-15+bob), 3)
        # Mean mouth
        pygame.draw.arc(surface, (140,40,40),
            (cx-8,cy-8+bob,16,8), math.pi, 2*math.pi, 2)
        # Propeller on top (spinning)
        pa = self.tick * 0.12
        for i in range(3):
            a = pa + i*2*math.pi/3
            px2 = cx + int(math.cos(a)*12)
            py2 = cy - 30 + bob + int(math.sin(a)*5)
            pygame.draw.ellipse(surface, (*bc,alpha), (px2-5,py2-3,10,6))
        pygame.draw.circle(surface, (80,60,40), (cx,cy-30+bob), 4)


# ── 5. Huge Bird Boss ─────────────────────────────────────────────────────
class HugeBirdBoss(MiniBoss):
    def __init__(self, spawn_x, spawn_y, hp, shot_cd):
        super().__init__(spawn_x, spawn_y, hp, shot_cd)
        self.W = 64; self.H = 52
        self.wing_phase = 0.0
    def _shoot(self, player):
        # Straight shot + random spread on hard
        dx = player.rect.centerx - self.cx
        dy = player.rect.centery  - self.cy
        dist = max(1, math.sqrt(dx*dx+dy*dy))
        base_angle = math.atan2(dy, dx)
        spreads = [-0.2, 0, 0.2] if self.max_hp >= 9 else [0]
        for spread in spreads:
            a = base_angle + spread
            spd = 5.0
            self.projectiles.append(MiniBossProjectile(
                self.cx, self.cy, math.cos(a)*spd, math.sin(a)*spd,
                color=(255, 220, 100)))
    def update(self, player):
        self.wing_phase += 0.15
        super().update(player)
    def _draw_body(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -60 or sr.left > SCREEN_WIDTH+60: return
        cx, cy = sr.centerx, sr.centery
        alpha = 255 if self.alive else max(0, int(255*self.death_timer/40))
        flap = int(math.sin(self.wing_phase)*18)
        # Wings
        for side in [-1,1]:
            wx = cx + side*20
            wy = cy - 8
            pts = [(cx, wy),(wx+side*30, wy+flap),(wx+side*40, wy+flap+14),(cx, wy+20)]
            ws = pygame.Surface((100,60),pygame.SRCALPHA)
            adjusted = [(p[0]-cx+50, p[1]-wy+10) for p in pts]
            if len(adjusted) >= 3:
                pygame.draw.polygon(ws, (200,160,80,alpha), adjusted)
                pygame.draw.polygon(ws, (170,130,60,alpha), adjusted, 2)
            surface.blit(ws, (cx-50, wy-10))
        # Body
        body_s = pygame.Surface((52,40),pygame.SRCALPHA)
        pygame.draw.ellipse(body_s, (210,170,80,alpha), (0,4,52,36))
        pygame.draw.ellipse(body_s, (230,190,100,alpha), (4,8,44,24))
        # Belly
        pygame.draw.ellipse(body_s, (240,220,180,alpha), (12,14,28,16))
        surface.blit(body_s, (cx-26, cy-8))
        # Head
        hs = pygame.Surface((36,34),pygame.SRCALPHA)
        pygame.draw.circle(hs, (210,170,80,alpha), (18,16), 14)
        # Crown feathers
        for i in range(5):
            fa = math.radians(-110 + i*28)
            fx = 18+int(math.cos(fa)*16); fy = 16+int(math.sin(fa)*14)
            pygame.draw.line(hs, (255,200,50,alpha), (18,16),(fx,fy), 3)
            pygame.draw.circle(hs, (255,230,80,alpha), (fx,fy), 3)
        # Eyes (big angry)
        pygame.draw.circle(hs, (255,255,200,alpha), (11,13), 5)
        pygame.draw.circle(hs, (255,255,200,alpha), (25,13), 5)
        pygame.draw.circle(hs, (200,50,50,alpha), (11,14), 3)
        pygame.draw.circle(hs, (200,50,50,alpha), (25,14), 3)
        pygame.draw.circle(hs, (20,0,0,alpha),   (11,14), 1)
        pygame.draw.circle(hs, (20,0,0,alpha),   (25,14), 1)
        # Beak
        pygame.draw.polygon(hs, (255,160,30,alpha), [(14,21),(22,21),(18,28)])
        surface.blit(hs, (cx-18, cy-32))
        # Talons
        for side in [-1,1]:
            tx = cx + side*12
            ty = cy + 20
            pygame.draw.line(surface, (180,140,50), (tx,ty),(tx+side*8,ty+10), 3)
            pygame.draw.line(surface, (180,140,50), (tx,ty),(tx,ty+12), 3)
            pygame.draw.line(surface, (180,140,50), (tx,ty),(tx-side*6,ty+10), 3)


# ── Boss factory ──────────────────────────────────────────────────────────
BOSS_TYPES = [SnowmanBoss, EvilElfBoss, FrostWraithBoss, GiftGolemBoss, HugeBirdBoss]

def make_boss(cp_index, spawn_x, spawn_y, difficulty, zone_left=-999999, zone_right=999999):
    cls = BOSS_TYPES[cp_index % len(BOSS_TYPES)]
    hp = BOSS_HITS[difficulty]
    shot_cd = BOSS_SHOT_CD[difficulty]
    b = cls(spawn_x, spawn_y, hp, shot_cd)
    b.zone_left = zone_left
    b.zone_right = zone_right
    return b


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
        # Star shape
        gc=lerp_color(STAR_GOLD, WHITE, pulse*0.4)
        r_out,r_in=10,4; pts=[]
        spin = self.tick * 0.02  # slow spin
        for k in range(10):
            angle=-math.pi/2+k*math.pi/5+spin; r=r_out if k%2==0 else r_in
            pts.append((sx+int(math.cos(angle)*r),sy+int(math.sin(angle)*r)))
        pygame.draw.polygon(surface, gc, pts)
        pygame.draw.polygon(surface, lerp_color(SUN_ORANGE, STAR_GOLD, pulse*0.5), pts, 1)
        # Center sparkle
        pygame.draw.circle(surface, (255, 250, 220), (sx, sy), 3)
        pygame.draw.circle(surface, WHITE, (sx-1, sy-1), 1)


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
        # Trunk
        pygame.draw.rect(surface, (110, 70, 35), (cx-4, sr.bottom-14, 8, 14), border_radius=2)
        pygame.draw.rect(surface, (140, 90, 45), (cx-3, sr.bottom-14, 3, 14), border_radius=1)
        # Tree layers with gradient coloring
        tc = (50, 140, 70) if self.activated else (45, 100, 55)
        tc_hi = tuple(min(c+40, 255) for c in tc)
        tc_dk = tuple(max(c-25, 0) for c in tc)
        for w2, h2, yo in [(36, 22, 34), (28, 18, 22), (22, 15, 12)]:
            ty = sr.bottom - 14 - yo
            pts = [(cx, ty-h2), (cx-w2//2, ty), (cx+w2//2, ty)]
            pygame.draw.polygon(surface, tc, pts)
            # Light side highlight
            pygame.draw.polygon(surface, tc_hi, [(cx, ty-h2), (cx-w2//4, ty-h2//2), (cx-w2//2+3, ty-1)])
            # Dark side
            pygame.draw.polygon(surface, tc_dk, [(cx, ty-h2), (cx+w2//4, ty-h2//2), (cx+w2//2-3, ty-1)])
            # Snow on tips — sunset-pink tinted
            pygame.draw.line(surface, (255, 215, 195), (cx-w2//2, ty), (cx-w2//2+8, ty-3), 2)
            pygame.draw.line(surface, (255, 215, 195), (cx+w2//2, ty), (cx+w2//2-8, ty-3), 2)
        # Star on top
        star_y = sr.bottom - 14 - 34 - 22
        sc = (255, 230, 60) if self.activated else (120, 120, 130)
        if self.activated:
            # Bright circle behind star (no SRCALPHA)
            pygame.draw.circle(surface, (255, 240, 140), (cx, star_y), 10)
        # Draw star shape
        star_pts = []
        for k in range(10):
            angle = -math.pi/2 + k*math.pi/5
            r = 7 if k%2==0 else 3
            star_pts.append((cx+int(math.cos(angle)*r), star_y+int(math.sin(angle)*r)))
        pygame.draw.polygon(surface, sc, star_pts)
        if self.activated:
            pygame.draw.polygon(surface, (255, 250, 200), star_pts, 1)
        # Ornament decorations when activated
        if self.activated:
            orn_colors = [(255,80,80),(255,200,50),(100,180,255),(255,140,200),(80,220,130)]
            for j,(ox,oy,_) in enumerate([(-9,-22,0),(7,-18,0),(-6,-32,0),(9,-28,0),(0,-40,0)]):
                pulse = abs(math.sin(math.radians(self.glow+j*72)))
                if pulse > 0.2:
                    oc = orn_colors[j % len(orn_colors)]
                    oy2 = sr.bottom - 14 + oy
                    pygame.draw.circle(surface, oc, (cx+ox, oy2), 3)
                    pygame.draw.circle(surface, (255,255,240), (cx+ox-1, oy2-1), 1)
            # Active glow border
            glow_a = abs(math.sin(math.radians(self.glow)))*0.6+0.4
            glow_c = tuple(int(v*glow_a) for v in (100, 220, 150))
            pygame.draw.rect(surface, glow_c, sr.inflate(10,10), 2, border_radius=4)


class ExitDoor:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x,y,54,72); self.pulse=0
    def update(self): self.pulse=(self.pulse+3)%360
    def check(self, player): return player.rect.colliderect(self.rect)
    def draw(self, surface, camera):
        sr=camera.apply(self.rect); p=abs(math.sin(math.radians(self.pulse)))
        cx2, cy2 = sr.centerx, sr.centery
        # Stone frame
        frame_col = (60, 55, 65)
        frame_hi = (90, 85, 95)
        pygame.draw.rect(surface, frame_col, sr.inflate(12,12), border_radius=10)
        pygame.draw.rect(surface, frame_hi, sr.inflate(10,10), 2, border_radius=10)
        # Rune markings on frame
        rune_col = lerp_color((180, 160, 50), (255, 230, 100), p)
        for i in range(4):
            ry = sr.y + 8 + i*(sr.height-16)//3
            pygame.draw.circle(surface, rune_col, (sr.x-3, ry), 3)
            pygame.draw.circle(surface, rune_col, (sr.right+3, ry), 3)
        # Portal interior — swirling golden light
        portal_col = lerp_color((255, 200, 60), (255, 240, 180), p)
        pygame.draw.rect(surface, portal_col, sr, border_radius=8)
        # Swirl rays (direct draw on main surface)
        for i in range(8):
            angle = math.radians(i * 45 + self.pulse * 0.8)
            ray_len = int(18 + p * 10)
            rx = cx2 + int(math.cos(angle) * ray_len)
            ry = cy2 + int(math.sin(angle) * ray_len)
            ray_col = lerp_color((255, 210, 70), (255, 240, 160), p*0.6)
            pygame.draw.line(surface, ray_col, (cx2, cy2), (rx, ry), 2)
        # Center star
        star_r = int(14 + p*6)
        pygame.draw.circle(surface, (255, 220, 60), (cx2, cy2), star_r)
        pygame.draw.circle(surface, (255, 245, 160), (cx2, cy2), int(star_r*0.6))
        pygame.draw.circle(surface, (255, 255, 240), (cx2, cy2), 5)
        # "HORIZON GATE" label
        font = pygame.font.Font(TITLE_FONT_PATH,10)
        lbl = font.render("HORIZON", True, (100, 70, 20))
        surface.blit(lbl, (sr.centerx - lbl.get_width()//2, sr.bottom - 14))
        lbl2 = font.render("GATE", True, lerp_color((200, 170, 50), (255, 230, 100), p))
        surface.blit(lbl2, (sr.centerx - lbl2.get_width()//2, sr.bottom + 2))
        # Outer glowing border
        border_col = lerp_color((255, 210, 60), WHITE, p*0.4)
        pygame.draw.rect(surface, border_col, sr.inflate(8,8), 2, border_radius=11)


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
        # Coyote time + jump buffer
        self.coyote_timer = 0
        self.jump_buffer  = 0
        # Snowball
        self.snowball_cooldown = 0
        # Combo
        self.combo_count = 0
        self.combo_timer = 0
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
        if self.snowball_cooldown > 0: self.snowball_cooldown -= 1
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0: self.combo_count = 0

        # Jump buffer: count down each frame a jump was requested
        if self.jump_buffer > 0: self.jump_buffer -= 1

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

        # Coyote time: allow jump for a few frames after walking off edge
        was_on_ground_before = self.on_ground
        jumped = False

        # Consume jump buffer: if we just landed and buffer is active, jump immediately
        can_jump = (self.on_ground or self.coyote_timer > 0) and self.jump_count == 0
        if can_jump and self.jump_buffer > 0:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False; self.riding_platform = None
            self.jump_count = 1; jumped = True
            self.jump_buffer = 0; self.coyote_timer = 0

        # Normal jump key
        if not jumped and can_jump and (
                keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False; self.riding_platform = None
            self.jump_count = 1; jumped = True
            self.coyote_timer = 0
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
        prev_on_ground = self.on_ground
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
                    self.coyote_timer = 0
                    if isinstance(plat, MovingPlatform): self.riding_platform = plat
                    if isinstance(plat, IcePlatform):    self.on_ice = True
                    plat.on_player_land(self)
                elif self.vel_y < 0:
                    self.rect.top = pr.bottom; self.vel_y = 0

        # Variable jump height: cut velocity if jump key released early
        if not (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            if self.vel_y < -5: self.vel_y = max(self.vel_y * 0.75, -5)

        # Coyote time: if we just left the ground (not jumped), start coyote window
        if prev_on_ground and not self.on_ground and not jumped:
            self.coyote_timer = COYOTE_FRAMES
        elif self.on_ground:
            self.coyote_timer = 0
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1
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
    for _ in range(25):
        out.append(BGCloud(rng.randint(-200, 1400), rng.randint(-600, 500),
                           rng.randint(30, 65), rng.uniform(0.04, 0.15)))
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

    monster_defs.append(dict(x=6480, y=GROUND-300, x1=6440, x2=6540, spd=0.8, cp=3))
    monster_defs.append(dict(x=6660, y=GROUND-360, x1=6620, x2=6720, spd=0.8, cp=3))
    monster_defs.append(dict(x=6840, y=GROUND-400, x1=6800, x2=6880, spd=0.8, cp=3))

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

    monster_defs.append(dict(x=9460, y=GROUND-360, x1=9420, x2=9500, spd=1.0, cp=4))

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
        _fs = self.screen and (self.screen.get_flags() & pygame.FULLSCREEN)
        if self.screen is None or self.screen.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN if _fs else 0)
        elif _fs:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Sky Climber — Level 3 (Christmas Morning)")
        pygame.mouse.set_visible(False)   # use custom crosshair cursor
        self.clock      = pygame.time.Clock()
        self.font       = pygame.font.Font(TITLE_FONT_PATH, 24)
        self.small_font = pygame.font.Font(TITLE_FONT_PATH, 16)
        self.big_font   = pygame.font.Font(TITLE_FONT_PATH, 48)
        self.tiny_font  = pygame.font.Font(TITLE_FONT_PATH, 12)
        self.title_font = pygame.font.Font(TITLE_FONT_PATH, 36)
        self.sfx        = SoundManager()
        self.state      = "playing"
        self.difficulty = "medium"
        self.level_time = self.tick = self.win_timer = 0
        self.music_volume = 0.25; self.sfx_volume = 0.2; self.music_muted = False
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
        self.snowballs      = []
        self.mini_bosses    = []   # active flying mini bosses
        self.combo_popups   = []   # (x, y, count, timer)
        self.player       = Player(100, 504)
        self.admin_mode   = False
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
        self.snowballs.clear() if hasattr(self,'snowballs') else None
        self.mini_bosses = []
        self.combo_popups = []

    def _rebuild_monsters(self):
        # Determine which checkpoint the player is currently at
        current_cp = -1
        for i, cp in enumerate(self.checkpoints):
            if cp.activated:
                current_cp = i
        # Only rebuild stomp monsters belonging to current checkpoint zone (or untagged)
        self.stomp_monsters = [
            StompMonster(d['x'], d['y'], d['x1'], d['x2'], d['spd'])
            for d in self.monster_defs
            if d.get('cp', current_cp) == current_cp
        ]
        # Only respawn the boss for the current checkpoint, not past ones
        self.mini_bosses = []
        if current_cp >= 0:
            cp = self.checkpoints[current_cp]
            zl = cp.spawn_x - 200
            zr = self.checkpoints[current_cp+1].spawn_x if current_cp+1 < len(self.checkpoints) else 999999
            b = make_boss(current_cp, cp.spawn_x, cp.spawn_y, self.difficulty, zl, zr)
            b._cp_index = current_cp
            self.mini_bosses.append(b)

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
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "playing" and self.player.alive and self.player.snowball_cooldown <= 0:
                        # Aim toward mouse cursor in world space
                        mx, my = event.pos
                        # Convert screen pos to world pos
                        wx2 = mx + self.camera.offset_x - self.camera.shake_x
                        wy2 = my + self.camera.offset_y - self.camera.shake_y
                        dx = wx2 - self.player.rect.centerx
                        dy = wy2 - self.player.rect.centery
                        dist = max(1, math.sqrt(dx*dx + dy*dy))
                        vx = dx/dist * SNOWBALL_SPEED
                        vy = dy/dist * SNOWBALL_SPEED
                        sb = Snowball(self.player.rect.centerx, self.player.rect.centery, vx, vy)
                        self.snowballs.append(sb)
                        self.player.snowball_cooldown = SNOWBALL_COOLDOWN
                        self.sfx.play("shoot")
                        # Muzzle flash particles
                        for _ in range(5):
                            self.particles.append(Particle(
                                self.player.rect.centerx, self.player.rect.centery,
                                random.choice([WHITE, SNOW_WHITE, ICE_BLUE]),
                                vx*0.3+random.uniform(-1,1), vy*0.3+random.uniform(-1,1),
                                12, 3, 0.05))
                    elif self.state == "settings":
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
                                    elif i == 4: pygame.display.toggle_fullscreen()
                                    elif i == 5: self.state = "playing"
                                    elif i == 6: self.load_level(); self.state="playing"; self.sfx.start_music(volume=self.music_volume)
                                    elif i == 7: self._exit_to_menu()
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
            n = 8
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
                elif self.settings_cursor == 4: pygame.display.toggle_fullscreen()
                elif self.settings_cursor == 5: self.state = "playing"
                elif self.settings_cursor == 6:
                    self.load_level(); self.state = "playing"; self.sfx.start_music(volume=self.music_volume)
                elif self.settings_cursor == 7: self._exit_to_menu()
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
        # Admin mode toggle — backslash key
        if key == pygame.K_BACKSLASH:
            self.admin_mode = not self.admin_mode
            return
        if key == pygame.K_ESCAPE:
            self.state = "settings"; self.settings_cursor = 5
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
                else:
                    # Set jump buffer so ground landing within buffer window auto-jumps
                    self.player.jump_buffer = JUMP_BUFFER_FRAMES

    def _update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()
        # Admin mode: free fly, no gravity, no collisions, invincible
        if self.admin_mode:
            spd = 10
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.player.rect.x -= spd
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player.rect.x += spd
            if keys[pygame.K_UP] or keys[pygame.K_w]: self.player.rect.y -= spd
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.player.rect.y += spd
            self.player.vel_y = 0; self.player.vel_x = 0
            self.player.alive = True; self.player.hearts = PLAYER_MAX_HEARTS
            self.player.invincibility = 0
            self.camera.update(self.player.rect)
            for p in self.platforms: p.update()
            for cp in self.checkpoints:
                cp.update()
                if cp.check(self.player):
                    self.sfx.play("checkpoint"); self._cp_fx(cp)
            for st in self.stars_list:
                if st.check(self.player):
                    self.player.star_count += 1; self.sfx.play("star"); self._star_fx(st)
            self.exit_door.update()
            if self.player.alive and self.exit_door.check(self.player):
                self.state = "win"; self.sfx.play("win"); self.sfx.stop_music()
            self.particles = [p for p in self.particles if p.update()]
            self.rings = [r for r in self.rings if r.update()]
            return
        for p in self.platforms:
            p.update()
        for w in self.winds:     w.update()
        for sb in self.saw_blades: sb.update()
        for k in self.kunais:    k.update()
        for fp in self.frost_puffs: fp.update()
        for sm in self.stomp_monsters: sm.update()

        result = self.player.update(keys, self.platforms)
        if result == "jump": self.sfx.play("jump")
        # Play crumble sound immediately when player first lands on a collapsing platform
        for p in self.platforms:
            if isinstance(p, CollapsingPlatform) and p.stood == 1:
                self.sfx.play("crumble")
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
                # Spawn mini boss for this checkpoint if not already active
                cp_idx = self.checkpoints.index(cp)
                already = any(getattr(b, '_cp_index', None) == cp_idx for b in self.mini_bosses)
                if not already:
                    zl = cp.spawn_x - 200
                    zr = self.checkpoints[cp_idx+1].spawn_x if cp_idx+1 < len(self.checkpoints) else 999999
                    b = make_boss(cp_idx, cp.spawn_x, cp.spawn_y, self.difficulty, zl, zr)
                    b._cp_index = cp_idx
                    self.mini_bosses.append(b)
                # Kill/deactivate bosses from previous checkpoints
                for old_b in self.mini_bosses:
                    old_cp = getattr(old_b, '_cp_index', -1)
                    if old_cp < cp_idx and old_b.alive:
                        old_b.alive = False; old_b.death_timer = 0
        for npc in self.npcs:
            npc.proximity_shown = npc.check_proximity(self.player)
        for st in self.stars_list:
            if st.check(self.player):
                self.player.star_count += 1; self.sfx.play("star"); self._star_fx(st)
                self.score_popups.append((st.x, st.y-20, f"+STAR x{self.player.star_count}", 55, STAR_GOLD))

        # ── Snowballs: update + check boss hits ────────────────────────────
        self.snowballs = [sb for sb in self.snowballs if sb.update()]
        for sb in list(self.snowballs):
            if not sb.alive: continue
            # Platform collision (snowball disappears on wall)
            sbr = sb.get_rect()
            for plat in self.platforms:
                if plat.is_active() and sbr.colliderect(plat.get_rect()):
                    sb.alive = False
                    for _ in range(4):
                        self.particles.append(Particle(sb.x, sb.y, SNOW_WHITE,
                            random.uniform(-2,2), random.uniform(-2,0), 10, 2, 0.1))
                    break
            if not sb.alive: continue
            # Boss hit
            for boss in self.mini_bosses:
                if boss.alive and sb.alive and sb.get_rect().colliderect(boss.rect):
                    sb.alive = False
                    died = boss.hit()
                    if died:
                        self.sfx.play("boss_die")
                        self.camera.add_shake(12)
                        self.flashes.append(FlashOverlay(XMAS_GOLD, 12, 140))
                        for _ in range(28):
                            a = random.uniform(0, math.pi*2); s = random.uniform(2,7)
                            self.particles.append(Particle(boss.cx, boss.cy,
                                random.choice([XMAS_GOLD, WHITE, XMAS_RED, XMAS_GREEN]),
                                math.cos(a)*s, math.sin(a)*s, 45, random.randint(3,7), 0.1))
                        self.rings.append(RingEffect(int(boss.cx), int(boss.cy), XMAS_GOLD, 110, 5, 3))
                        # Bonus stars
                        bonus = 8
                        self.player.star_count += bonus
                        self.score_popups.append((boss.cx, boss.cy-35,
                            f"BOSS DOWN! +{bonus} STARS", 90, XMAS_GOLD))
                        # Combo
                        self.player.combo_count += 1
                        self.player.combo_timer  = COMBO_EXPIRE
                        if self.player.combo_count >= 2:
                            self.combo_popups.append((boss.cx, boss.cy-60,
                                self.player.combo_count, 55))
                        self.freeze_frames = 6
                    else:
                        self.sfx.play("boss_hit")
                        self.camera.add_shake(4)
                        for _ in range(8):
                            a = random.uniform(0, math.pi*2); s = random.uniform(1,3)
                            self.particles.append(Particle(boss.cx, boss.cy,
                                ICE_BLUE, math.cos(a)*s, math.sin(a)*s, 18, 3, 0.1))
                        self.score_popups.append((boss.cx, boss.cy-20,
                            f"HIT! {boss.hp}/{boss.max_hp}", 45, ICE_BLUE))
                    break

        # ── Mini bosses: update + damage player ────────────────────────────
        for boss in self.mini_bosses:
            boss.update(self.player)
            if boss.alive:
                # Projectile hits
                if boss.check_projectile_hits(self.player):
                    _do_damage()
                # Body contact
                if boss.check_body_hit(self.player):
                    _do_damage()
        self.mini_bosses = [b for b in self.mini_bosses if b.alive or b.death_timer > 0]
        # Combo popup decay
        self.combo_popups = [(x, y-1.0, cnt, t-1) for x, y, cnt, t in self.combo_popups if t > 0]

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
        # Show system cursor only in settings/pause so mouse clicks are visible
        pygame.mouse.set_visible(self.state in ("settings",))
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

    def _build_sky_cache(self):
        """Pre-render the static sunset sky gradient + sun glow."""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Sunset gradient: deep purple-blue top → coral → warm orange → golden horizon
        sky_cols = [(45, 30, 80), (80, 45, 110), (140, 60, 100),
                    (210, 90, 70), (245, 140, 60), (255, 180, 70),
                    (255, 210, 100), (255, 225, 130)]
        band_h = SCREEN_HEIGHT // (len(sky_cols) - 1)
        for i in range(len(sky_cols)-1):
            for y2 in range(band_h):
                t = y2 / band_h
                c = lerp_color(sky_cols[i], sky_cols[i+1], t)
                yy = i*band_h + y2
                pygame.draw.line(surf, c, (0, yy), (SCREEN_WIDTH, yy))
        for yy in range((len(sky_cols)-1)*band_h, SCREEN_HEIGHT):
            pygame.draw.line(surf, sky_cols[-1], (0, yy), (SCREEN_WIDTH, yy))
        # Warm sun glow baked in
        sun_x = SCREEN_WIDTH // 2 + 100; sun_y = SCREEN_HEIGHT - 160
        for r, col in [(120, (255, 160, 40)), (80, (255, 190, 60)), (50, (255, 210, 90))]:
            gs = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*col, 18), (r+2, r+2), r)
            surf.blit(gs, (sun_x-r-2, sun_y-r-2))
        return surf

    def _build_mountain_layers(self):
        """Pre-render mountain silhouette strips for parallax blitting."""
        layers = []
        mtn_rng = random.Random(42)
        strip_w = SCREEN_WIDTH + 800
        # Warm sunset mountain silhouettes — dark purples and warm grays
        for col, scale in [((60, 35, 70), 1.0), ((80, 50, 75), 0.8), ((110, 70, 80), 0.6)]:
            s = pygame.Surface((strip_w, SCREEN_HEIGHT), pygame.SRCALPHA)
            pts = [(0, SCREEN_HEIGHT)]
            for mx in range(0, strip_w, 40):
                base_h = 280 + mtn_rng.randint(-80, 80)
                my = SCREEN_HEIGHT - int(base_h * scale) + int(math.sin(mx*0.005)*30)
                pts.append((mx, my))
            pts.append((strip_w, SCREEN_HEIGHT))
            pygame.draw.polygon(s, col, pts)
            layers.append(s)
        # Dark pine tree silhouettes
        tree_s = pygame.Surface((strip_w, SCREEN_HEIGHT), pygame.SRCALPHA)
        tree_rng = random.Random(123)
        for i in range(60):
            tx = tree_rng.randint(0, strip_w)
            th = tree_rng.randint(18, 40)
            ty = SCREEN_HEIGHT - 140 + tree_rng.randint(-40, 30)
            tc = (35+tree_rng.randint(0,20), 50+tree_rng.randint(0,20), 35+tree_rng.randint(0,15))
            pygame.draw.polygon(tree_s, tc,
                [(tx, ty), (tx-th//3, ty+th), (tx+th//3, ty+th)])
            pygame.draw.rect(tree_s, (50, 30, 20), (tx-2, ty+th, 4, 6))
        layers.append(tree_s)
        return layers

    def _draw_background(self):
        # Build caches on first call
        if not hasattr(self, '_sky_cache'):
            self._sky_cache = self._build_sky_cache()
            self._mtn_layers = self._build_mountain_layers()

        # Blit cached sky (instant)
        self.screen.blit(self._sky_cache, (0, 0))

        # Sunset sun — large, low, warm orange
        sun_x = SCREEN_WIDTH // 2 + 100; sun_y = SCREEN_HEIGHT - 160
        pulse = abs(math.sin(self.tick*0.015))*4
        pygame.draw.circle(self.screen, (255, 120, 30), (sun_x, sun_y), int(44+pulse))
        pygame.draw.circle(self.screen, (255, 170, 50), (sun_x, sun_y), int(34+pulse*0.6))
        pygame.draw.circle(self.screen, (255, 210, 100), (sun_x, sun_y), int(20+pulse*0.3))
        pygame.draw.circle(self.screen, (255, 240, 180), (sun_x, sun_y), 10)

        # Mountain parallax layers (pre-rendered strips, just offset)
        parallax_rates = [0.06, 0.09, 0.13, 0.1]
        for i, layer_surf in enumerate(self._mtn_layers):
            ox = int(-self.camera.offset_x * parallax_rates[i]) % layer_surf.get_width()
            self.screen.blit(layer_surf, (-ox, 0))
            # Wrap if needed
            if ox > layer_surf.get_width() - SCREEN_WIDTH:
                self.screen.blit(layer_surf, (layer_surf.get_width()-ox, 0))

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
        # Mini bosses (behind player so projectiles visible over boss)
        for boss in self.mini_bosses: boss.draw(self.screen, self.camera, self.tick)
        # Player snowballs
        for sb2 in self.snowballs: sb2.draw(self.screen, self.camera, self.tick)
        self.exit_door.draw(self.screen, self.camera)
        for p in self.particles: p.draw(self.screen, self.camera)
        for r in self.rings:     r.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.tick)
        # Wall-slide particles
        if self.player.wall_sliding and self.player.alive and self.tick % 2 == 0:
            wx2 = self.player.rect.left if self.player.wall_side == -1 else self.player.rect.right
            self.particles.append(Particle(wx2, self.player.rect.centery + random.randint(-5,10),
                random.choice([WHITE, SNOW_WHITE, ICE_BLUE]),
                -self.player.wall_side * random.uniform(0.5,1.5), random.uniform(-1,0.5), 10, 2, 0.05))
        for f in self.flashes:        f.draw(self.screen)
        for d in self.damage_flashes: d.draw(self.screen)
        for x,y,text,timer,color in self.score_popups:
            a=min(1.0,timer/30); c=tuple(max(0,min(255,int(v*a))) for v in color)
            pos=self.camera.apply(pygame.Rect(int(x),int(y),1,1))
            surf=self.small_font.render(text,True,c)
            self.screen.blit(surf,surf.get_rect(center=(pos.x,pos.y)))
        # Combo popups
        for x, y, cnt, timer in self.combo_popups:
            a = min(1.0, timer/20)
            sz = min(30, 16 + cnt*2)
            cf = pygame.font.Font(TITLE_FONT_PATH,sz)
            cc = lerp_color(XMAS_GOLD, WHITE, min(1.0, cnt/6))
            cs = tuple(max(0, min(255, int(v*a))) for v in cc)
            combo_surf = cf.render(f"x{cnt} COMBO!", True, cs)
            pos = self.camera.apply(pygame.Rect(int(x), int(y), 1, 1))
            self.screen.blit(combo_surf, combo_surf.get_rect(center=(pos.x, pos.y)))
        # Snowball crosshair cursor
        if self.player.alive and self.state == "playing":
            mx, my = pygame.mouse.get_pos()
            cd_ratio = self.player.snowball_cooldown / SNOWBALL_COOLDOWN
            r_outer = 14; r_inner = 5
            col = lerp_color((80, 200, 255), (255, 100, 100), cd_ratio)
            pygame.draw.circle(self.screen, col, (mx, my), r_outer, 2)
            pygame.draw.circle(self.screen, col, (mx, my), r_inner, 2)
            gap = 6
            for dx2, dy2 in [(0,-1),(0,1),(-1,0),(1,0)]:
                x1 = mx + dx2*(r_inner+gap); y1 = my + dy2*(r_inner+gap)
                x2 = mx + dx2*(r_outer-2);   y2 = my + dy2*(r_outer-2)
                pygame.draw.line(self.screen, col, (x1,y1), (x2,y2), 2)
            if cd_ratio > 0:
                arc_rect = pygame.Rect(mx-r_outer, my-r_outer, r_outer*2, r_outer*2)
                pygame.draw.arc(self.screen, (255,220,80), arc_rect,
                    math.pi/2, math.pi/2 + (1-cd_ratio)*2*math.pi, 3)
        self._draw_hud()
        if self.soul_state is not None: self._draw_soul()

    def _draw_hud(self):
        def _hud_text(font, text, color, x, y):
            self.screen.blit(font.render(text,True,(0,0,0)),(x+1,y+1))
            self.screen.blit(font.render(text,True,color),(x,y))
        hud_x, hud_y = 12, 10
        # Hearts
        for i in range(PLAYER_MAX_HEARTS):
            hx=hud_x+i*26; hy=hud_y; filled=i<self.player.hearts
            c=XMAS_RED if filled else (50,50,50)
            ps=int(abs(math.sin(self.tick*0.12))*2) if (i==0 and self.player.hearts==1 and self.player.alive) else 0
            for dx,dy,sc in [(1,1,(0,0,0)),(0,0,c)]:
                pygame.draw.circle(self.screen,sc,(hx+5+dx,hy+dy),5+ps)
                pygame.draw.circle(self.screen,sc,(hx+13+dx,hy+dy),5+ps)
                pygame.draw.polygon(self.screen,sc,[(hx-ps+dx,hy+2+dy),(hx+9+dx,hy+11+ps+dy),(hx+18+ps+dx,hy+2+dy)])
        # Low health red border
        if self.player.hearts == 1 and self.player.alive:
            pulse = abs(math.sin(self.tick*0.08))*0.7
            lh_s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for bi in range(8):
                ia = max(0, int(60*pulse - bi*8))
                if ia > 0:
                    pygame.draw.rect(lh_s, (220,30,30,ia),
                        (bi,bi,SCREEN_WIDTH-2*bi,SCREEN_HEIGHT-2*bi), 2)
            self.screen.blit(lh_s, (0,0))
        # Dash bar
        dash_y=hud_y+18; dash_bw=60; dash_bh=5
        if self.player.dash_cooldown > 0:
            ratio=1.0-self.player.dash_cooldown/DASH_COOLDOWN
            pygame.draw.rect(self.screen,(30,30,40),(hud_x,dash_y,dash_bw,dash_bh))
            pygame.draw.rect(self.screen,CYAN,(hud_x,dash_y,int(dash_bw*ratio),dash_bh))
        else:
            pygame.draw.rect(self.screen,CYAN,(hud_x,dash_y,dash_bw,dash_bh))
        _hud_text(pygame.font.Font(TITLE_FONT_PATH,9),"DASH",
                  (160,220,230) if self.player.dash_cooldown<=0 else (80,80,90), hud_x+dash_bw+4, dash_y-2)
        # Snowball cooldown bar
        sb_bw=60; sb_y=dash_y+10
        if self.player.snowball_cooldown > 0:
            ratio2=1.0-self.player.snowball_cooldown/SNOWBALL_COOLDOWN
            pygame.draw.rect(self.screen,(30,30,40),(hud_x,sb_y,sb_bw,sb_bh:=5))
            pygame.draw.rect(self.screen,(80,200,255),(hud_x,sb_y,int(sb_bw*ratio2),5))
        else:
            pygame.draw.rect(self.screen,(80,200,255),(hud_x,sb_y,sb_bw,5))
        _hud_text(pygame.font.Font(TITLE_FONT_PATH,9),"BALL",
                  (160,220,230) if self.player.snowball_cooldown<=0 else (80,80,90), hud_x+sb_bw+4, sb_y-2)
        # Progress bar
        alt=self._altitude(); ab_w,ab_h=160,8; ab_x=SCREEN_WIDTH//2-ab_w//2; ab_y=10
        pygame.draw.rect(self.screen,(40,50,70),(ab_x-1,ab_y-1,ab_w+2,ab_h+2))
        for pi in range(int(ab_w*alt)):
            t=pi/ab_w; fc=lerp_color((255,180,50),(80,150,220),t)
            pygame.draw.line(self.screen,fc,(ab_x+pi,ab_y),(ab_x+pi,ab_y+ab_h))
        _hud_text(pygame.font.Font(TITLE_FONT_PATH,8),"progress",(180,200,220),ab_x+ab_w+4,ab_y)
        # Top-right info
        _hud_text(self.tiny_font,f"Time: {self.level_time/FPS:.1f}s",SNOW_WHITE,SCREEN_WIDTH-145,10)
        _hud_text(self.tiny_font,f"Stars: {self.player.star_count}",STAR_GOLD,SCREEN_WIDTH-145,26)
        dc=((100,220,150) if self.difficulty=="easy" else (255,210,60) if self.difficulty=="medium" else (255,100,100))
        _hud_text(self.tiny_font,self.difficulty.upper(),dc,SCREEN_WIDTH-145,42)
        # Active boss indicator (top-right corner)
        alive_bosses = [b for b in self.mini_bosses if b.alive]
        if alive_bosses:
            boss_names = ["Snowman","Evil Elf","Frost Wraith","Gift Golem","Huge Bird"]
            bx3 = SCREEN_WIDTH - 200; by3 = 62
            for bi2, boss in enumerate(alive_bosses[:3]):
                name = boss_names[getattr(boss,'_cp_index',0) % len(boss_names)]
                pulse2 = abs(math.sin(self.tick*0.1+bi2))*0.4+0.6
                bc2 = tuple(int(v*pulse2) for v in XMAS_RED)
                _hud_text(self.tiny_font, f"⚠ {name} {boss.hp}/{boss.max_hp}", bc2,
                          bx3, by3 + bi2*14)
        if not self.player.alive and self.soul_state is None:
            txt=self.font.render("Respawning...",True,XMAS_RED)
            self.screen.blit(txt,txt.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)))
        # Admin mode indicator
        if self.admin_mode:
            admin_pulse = abs(math.sin(self.tick*0.08))*0.4+0.6
            admin_col = tuple(int(v*admin_pulse) for v in (255,80,80))
            pygame.draw.rect(self.screen, (30,10,10), (SCREEN_WIDTH//2-80, 56, 160, 22), border_radius=6)
            _hud_text(self.small_font, "ADMIN MODE", admin_col, SCREEN_WIDTH//2-50, 58)
        self.screen.blit(self.tiny_font.render(
            "SPACE-Jump  SHIFT-Dash  LEFT CLICK-Snowball  E-Talk  R-Respawn  ESC-Menu",
            True,(80,100,130)),(10,SCREEN_HEIGHT-16))

    def _draw_settings(self):
        panel_w, panel_h = 500, 640
        panel_x = SCREEN_WIDTH // 2 - panel_w // 2
        panel_y = 40
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_wooden_panel(self.screen, panel_rect, "PAUSED", self.title_font)

        # Menu items
        is_fs = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
        items = [
            f"Music:  < {int(self.music_volume*100)}% >",
            f"SFX:    < {int(self.sfx_volume*100)}% >",
            f"Mute:   {'ON' if self.music_muted else 'OFF'}",
            f"Difficulty:  < {self.difficulty.upper()} >",
            f"Fullscreen:  {'ON' if is_fs else 'OFF'}",
            "Resume",
            "Restart Level",
            "Exit to Menu",
        ]

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
            draw_wooden_bar(self.screen, bar, item, self.small_font, sel, self.tick)

        # Volume sliders using wooden style
        slider_x = SCREEN_WIDTH // 2 - 150
        slider_w = 300
        self._settings_vol_slider = draw_wooden_slider(self.screen, slider_x, _item_y[0]+bar_h+4, slider_w, self.music_volume, self.music_muted, self.small_font)
        self._settings_sfx_slider = draw_wooden_slider(self.screen, slider_x, _item_y[1]+bar_h+4, slider_w, self.sfx_volume, self.music_muted, self.small_font)

        # Footer
        footer_text = "UP/DOWN Navigate    LEFT/RIGHT Adjust    ENTER Select    ESC Resume"
        ft = self.small_font.render(footer_text, True, (150, 120, 80))
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
        wt=self.big_font.render("REALM 3 CLEARED!",True,(255,215,60))
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