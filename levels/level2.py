import pygame
import math
import random
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from player_sprites import init_player_sprite, draw_player_sprite

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS = 60

BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
GRAY         = (140, 140, 140)
DARK_GRAY    = (80,  80,  80)
RED          = (220, 50,  50)
YELLOW       = (255, 220, 50)
DARK_BG      = (8,   18,  35)
CYAN         = (0,   220, 255)
GRID_COLOR   = (15,  25,  45)
ORANGE       = (255, 160, 30)
GOLD         = (255, 200, 50)
ICE_BLUE     = (120, 200, 255)
ICE_DARK     = (60,  140, 210)
SNOW_WHITE   = (230, 245, 255)
PINE_GREEN   = (30,  100, 60)
CANDY_RED    = (220, 40,  60)
BALLOON_RED  = (255, 60,  80)
BALLOON_PINK = (255, 160, 180)
SPIKE_GRAY   = (160, 160, 175)
PORTAL_CYAN  = (0,   240, 220)
PORTAL_BLUE  = (0,   120, 255)
FALLING_BROWN= (160, 100, 50)
PHANTOM_TEAL = (40,  220, 180)
CP_INACTIVE  = (180, 140, 50)
CP_ACTIVE    = (255, 220, 0)
CP_GLOW      = (255, 255, 150)
COUNTDOWN_COL = (60,  120, 200)

LEDGE_L_COL  = (80,  160, 220)
LEDGE_R_COL  = (200, 160, 40)

MOVING_COL   = (200, 140, 40)
SANTA_RED    = (200, 30,  30)
SLEIGH_BROWN = (180, 100, 40)
SLEIGH_GOLD  = (220, 180, 30)

# Snow Miser colour — icy blue-white, very on-brand
SNOW_MISER_ROBE = (80, 160, 220)
XMAS_GOLD       = (255, 200, 50)
XMAS_RED        = (200, 30,  30)
XMAS_GREEN      = (30,  160, 50)

# Physics
GRAVITY        = 0.6
JUMP_VELOCITY  = -13
MOVE_SPEED     = 5
SPRINT_SPEED   = 8
MAX_FALL_SPEED = 15
DEATH_Y        = 900
BASE_Y         = 420

LEDGE_GAP   = 180
LEDGE_RISE  = 120
WALL_STEPS  = 5
COUNTDOWN_GRACE = 90

# ---------------------------------------------------------------------------
# Difficulty presets  (unchanged from original)
# ---------------------------------------------------------------------------
DIFFICULTY_PRESETS = {
    "easy": {
        "shrink_speed":    0.4,  "shrink_respawn":  400,
        "fall_delay":      55,   "phantom_frames":  30,
        "phantom_w":       110,  "balloon_vx":      10,
        "balloon_vy":      -13,  "balloon_radius":  18,
        "player_speed":    5,    "player_jump":     -14,
        "countdown_sec":   3,    "countdown_grace": 100,
        "tram_speed":      2,    "tram_vanish":     650,
        "santa_timeout":   420,  "rope_len":        160,
        "rope_grab_r":     22,   "zigzag_ledge_w":  80,
        "kidnap_dist":     320,
    },
    "medium": {
        "shrink_speed":    1.2,  "shrink_respawn":  300,
        "fall_delay":      25,   "phantom_frames":  18,
        "phantom_w":       80,   "balloon_vx":      9,
        "balloon_vy":      -11,  "balloon_radius":  14,
        "player_speed":    5,    "player_jump":     -13,
        "countdown_sec":   3,    "countdown_grace": 90,
        "tram_speed":      3,    "tram_vanish":     560,
        "santa_timeout":   300,  "rope_len":        130,
        "rope_grab_r":     14,   "zigzag_ledge_w":  60,
        "kidnap_dist":     250,
    },
    "hard": {
        "shrink_speed":    2.8,  "shrink_respawn":  240,
        "fall_delay":      8,    "phantom_frames":  8,
        "phantom_w":       55,   "balloon_vx":      8,
        "balloon_vy":      -10,  "balloon_radius":  9,
        "player_speed":    5,    "player_jump":     -13,
        "countdown_sec":   2,    "countdown_grace": 60,
        "tram_speed":      4,    "tram_vanish":     555,
        "santa_timeout":   300,  "rope_len":        130,
        "rope_grab_r":     14,   "zigzag_ledge_w":  42,
        "kidnap_dist":     250,
    },
}

# ---------------------------------------------------------------------------
# Story Dialogues  — Snow Miser guides the dreamer through the Second Realm
# ---------------------------------------------------------------------------
STORY_DIALOGUES = {
    # ── Intro: Snow Miser greets the dreamer at the very start ──────────
    "intro": [
        ("Snow Miser", "Oh ho ho ho! Look who wandered into MY realm!"),
        ("Snow Miser", "I'm Snow Miser. I'm too much. The second of the dream's four terrors."),
        ("Snow Miser", "The First Realm is behind you. Fire. Anger. You burned right through it."),
        ("Snow Miser", "But THIS realm? This is the realm of ICE. Of cold truth. Of slipping and falling."),
        ("Snow Miser", "Everything here wants to shrink under you, fall away, or simply... vanish."),
        ("Snow Miser", "I'm not your enemy, dreamer. I'm just the cold, honest voice in your head."),
        ("Snow Miser", "Let me tell you what you're up against. ARROW KEYS or WASD to move. SPACE to jump."),
        ("Snow Miser", "You can JUMP again in mid-air. Double jump. Use it wisely on the ice platforms."),
        ("Snow Miser", "ICE PLATFORMS shrink the moment you land. Don't dawdle. Keep moving."),
        ("Snow Miser", "WOOD PLATFORMS fall after a delay. You'll feel them shake. That's your warning."),
        ("Snow Miser", "SPIKES are instant death. Don't fall into them. There's a balloon nearby... trust it."),
        ("Snow Miser", "TEAL PLATFORMS are phantom. Step on them and they vanish. Fast."),
        ("Snow Miser", "Press SPACE to jump off the ROPE when Santa carries you. Aim for the portal."),
        ("Snow Miser", "Miss the portal and Santa takes you... somewhere you do NOT want to go."),
        ("Snow Miser", "R to restart. ESC for settings. Flags are checkpoints -- reach them."),
        ("Snow Miser", "Oh, and dreamer? The cold doesn't care how determined you are."),
        ("Snow Miser", "It just waits. Patiently. For you to slip."),
        ("Snow Miser", "Try not to slip."),
    ],

    # ── Checkpoint A: After shrinking ice platforms ──────────────────────
    "cp_a": [
        ("Snow Miser", "Ha! You made it past the ice. Barely."),
        ("Snow Miser", "You felt it, didn't you? The platform shrinking under your feet."),
        ("Snow Miser", "That feeling -- the ground disappearing while you're still standing on it."),
        ("Snow Miser", "That's what this realm IS. Everything you rely on just... erodes."),
        ("Snow Miser", "Ahead are the FALLING platforms. Wood. Old. Tired."),
        ("Snow Miser", "They shake for a moment when you land. That shake is a countdown."),
        ("Snow Miser", "Jump before the countdown ends. Every single time."),
        ("Snow Miser", "You've done harder things, dreamer. Keep moving."),
    ],

    # ── Checkpoint B: After falling platforms, approaching spikes ────────
    "cp_b": [
        ("Snow Miser", "Two down. You're learning."),
        ("Snow Miser", "The spikes ahead look like a dead end. They're not."),
        ("Snow Miser", "There's a balloon floating just above them. Red. Festive. Deceptive."),
        ("Snow Miser", "Grab it and you'll fly over the whole mess. It only works once though."),
        ("Snow Miser", "Time your jump carefully. Land too early and the spikes get you."),
        ("Snow Miser", "Land too late and you miss the safe platform entirely."),
        ("Snow Miser", "I'd wish you luck but I don't believe in luck."),
        ("Snow Miser", "I believe in timing. And you've got decent timing... so far."),
    ],

    # ── Checkpoint C: After spikes + balloon, approaching phantoms ───────
    "cp_c": [
        ("Snow Miser", "The balloon trick. Nice. Most dreamers just stare at the spikes until they die."),
        ("Snow Miser", "Not you though. You see the path."),
        ("Snow Miser", "Ahead of you are the PHANTOM platforms. Teal. Glowing. Beautiful, honestly."),
        ("Snow Miser", "Touch them and a timer starts. When the timer runs out -- gone."),
        ("Snow Miser", "No warning shake. No countdown. Just gone."),
        ("Snow Miser", "Move fast. Don't look down. The gap below is not forgiving."),
        ("Snow Miser", "You know what I find interesting about you, dreamer?"),
        ("Snow Miser", "You keep going. Every realm. Every trap. You just... keep going."),
        ("Snow Miser", "I wonder if you even know why."),
    ],

    # ── Checkpoint D: Safe platform after phantoms, before countdown ─────
    "cp_d": [
        ("Snow Miser", "Breathe. You've earned it."),
        ("Snow Miser", "What comes next is my personal favourite. The COUNTDOWN platform."),
        ("Snow Miser", "You step on it. A number appears. 3... 2... 1... GO!"),
        ("Snow Miser", "When it says GO -- you jump. Immediately. To the platform ahead."),
        ("Snow Miser", "If you hesitate, the pad falls away and takes you with it."),
        ("Snow Miser", "The target platform only appears at GO. Not before. Not during the countdown."),
        ("Snow Miser", "Don't try to jump early. There's nothing there yet."),
        ("Snow Miser", "And if you die after reaching the target... it stays solid. You won't be trapped."),
        ("Snow Miser", "I'm cold, dreamer. Not cruel."),
    ],

    # ── Checkpoint E: After countdown, approaching zigzag ───────────────
    "cp_e": [
        ("Snow Miser", "The countdown platform. Down in one try, were you? Or did it take a few?"),
        ("Snow Miser", "Doesn't matter. You're here."),
        ("Snow Miser", "The ZIGZAG climb is next. Floating ledges. No walls. Just the void."),
        ("Snow Miser", "Blue ledges are on the left. Gold ledges are on the right."),
        ("Snow Miser", "Jump right to gold. Then left to blue. Alternate. Rise."),
        ("Snow Miser", "You need to reach the TENTH ledge. The very top one."),
        ("Snow Miser", "Miss a ledge and you fall back down. Start the zigzag again."),
        ("Snow Miser", "This one tests patience more than skill, dreamer."),
        ("Snow Miser", "Which one do you have more of?"),
    ],

    # ── Checkpoint F: After zigzag, before tram + Santa ─────────────────
    "cp_f": [
        ("Snow Miser", "Ten ledges. You climbed all ten. I'm... actually impressed."),
        ("Snow Miser", "Don't let it go to your head."),
        ("Snow Miser", "Ahead is the final obstacle of this realm. The TRAM."),
        ("Snow Miser", "Step on the golden cart. It starts moving. Ride it to the right."),
        ("Snow Miser", "At some point... Santa Claus will appear. In his sleigh. With a rope."),
        ("Snow Miser", "Yes. That Santa. In my realm. I know. Believe me, I know."),
        ("Snow Miser", "Jump and GRAB the rope. Press SPACE to release when you're over the portal."),
        ("Snow Miser", "Release too early and you fall short. Too late and Santa takes you for a ride."),
        ("Snow Miser", "A very long, very unwanted ride."),
        ("Snow Miser", "The portal is your way out of this realm. Through it -- the Third Realm."),
        ("Snow Miser", "Storm. Grief. Someone else's problem to explain."),
        ("Snow Miser", "But first... survive this. Go on, dreamer."),
        ("Snow Miser", "I'll be watching."),
    ],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def rainbow_color(tick, speed=0.05):
    RB = [(255,60,60),(255,160,40),(255,240,50),(80,255,80),(50,200,255),(120,80,255),(220,50,220)]
    idx = (tick*speed) % len(RB)
    i   = int(idx)
    return lerp_color(RB[i], RB[(i+1)%len(RB)], idx-i)

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
class Camera:
    def __init__(self, w, h):
        self.offset_x = self.offset_y = 0.0
        self.width = w; self.height = h
        self.shake_amount = self.shake_x = self.shake_y = 0

    def update(self, tr):
        self.offset_x += (tr.centerx - self.width//3 - self.offset_x) * 0.1
        oy = tr.centery - self.height//2
        self.offset_y += (oy - self.offset_y) * 0.05
        self.offset_y = max(-900, min(self.offset_y, 200))
        if self.shake_amount > 0.5:
            self.shake_x = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_y = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_amount *= 0.85
        else:
            self.shake_amount = self.shake_x = self.shake_y = 0

    def add_shake(self, v): self.shake_amount = min(self.shake_amount+v, 20)

    def apply(self, rect):
        return pygame.Rect(rect.x - int(self.offset_x)+self.shake_x,
                           rect.y - int(self.offset_y)+self.shake_y,
                           rect.width, rect.height)

# ---------------------------------------------------------------------------
# Particle / Ring / Flash
# ---------------------------------------------------------------------------
class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, lifetime=30, size=4, grav=0.1, fade=True):
        self.x=float(x); self.y=float(y); self.color=color
        self.vx=vx; self.vy=vy; self.lt=lifetime; self.mlt=lifetime
        self.size=size; self.grav=grav; self.fade=fade
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=self.grav; self.lt-=1
        return self.lt>0
    def draw(self, surf, cam):
        a = self.lt/self.mlt if self.fade else 1.0
        s = max(1, int(self.size*a))
        c = tuple(max(0,min(255,int(v*a))) for v in self.color)
        p = cam.apply(pygame.Rect(int(self.x),int(self.y),1,1))
        pygame.draw.rect(surf, c, (p.x,p.y,s,s))

class RingEffect:
    def __init__(self, x, y, color, max_r=120, speed=4, w=4):
        self.x=x; self.y=y; self.color=color; self.r=0; self.mr=max_r; self.sp=speed; self.w=w
    def update(self): self.r+=self.sp; return self.r<self.mr
    def draw(self, surf, cam):
        a = 1-(self.r/self.mr)
        c = tuple(max(0,min(255,int(v*a))) for v in self.color)
        w = max(1,int(self.w*a))
        p = cam.apply(pygame.Rect(int(self.x),int(self.y),1,1))
        if -50<p.x<SCREEN_WIDTH+50:
            pygame.draw.circle(surf, c, (p.x,p.y), int(self.r), w)

class FlashOverlay:
    def __init__(self, color, dur=15, max_alpha=180):
        self.dur=dur; self.t=dur; self.ma=max_alpha
        self.surf=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)); self.surf.fill(color)
    def update(self): self.t-=1; return self.t>0
    def draw(self, surf): self.surf.set_alpha(int(self.ma*(self.t/self.dur))); surf.blit(self.surf,(0,0))

# ---------------------------------------------------------------------------
# NPC — Snow Miser  (styled like Level 4 NPCs)
# ---------------------------------------------------------------------------
class NPC:
    """
    Snow Miser NPC.  Drawn as a robed figure with an icy blue robe and
    snowflake-tipped staff, matching the Level 4 NPC visual style.
    """
    WIDTH, HEIGHT = 24, 40

    def __init__(self, x, y, dialogue_key, name="Snow Miser"):
        self.rect = pygame.Rect(x, y - self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.dialogue_key = dialogue_key
        self.name = name
        self.talked = False
        self.bob = random.uniform(0, math.pi*2)
        self.proximity_shown = False

    def check_proximity(self, player):
        dx = abs(player.rect.centerx - self.rect.centerx)
        dy = abs(player.rect.centery - self.rect.centery)
        return dx < 80 and dy < 80

    def draw(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20:
            return
        bob = int(math.sin(tick * 0.04 + self.bob) * 2)
        bx, by = sr.x, sr.y + bob

        # Robe — icy blue for Snow Miser
        robe_c    = SNOW_MISER_ROBE
        robe_dark = tuple(max(0, c - 35) for c in robe_c)
        pygame.draw.polygon(surface, robe_c,
            [(bx+4, by+14), (bx+20, by+14), (bx+22, by+40), (bx, by+40)])
        pygame.draw.polygon(surface, robe_dark,
            [(bx+4, by+14), (bx+20, by+14), (bx+22, by+40), (bx, by+40)], 1)

        # Head
        pygame.draw.circle(surface, (220, 190, 160), (bx+12, by+10), 8)
        # Icy hood arc
        pygame.draw.arc(surface, robe_c, (bx+2, by, 20, 18), 0.3, 2.8, 3)

        # Eyes — slightly mischievous
        pygame.draw.circle(surface, WHITE, (bx+9,  by+9), 2)
        pygame.draw.circle(surface, WHITE, (bx+15, by+9), 2)
        pygame.draw.circle(surface, BLACK, (bx+9,  by+10), 1)
        pygame.draw.circle(surface, BLACK, (bx+15, by+10), 1)

        # Staff with snowflake tip
        pygame.draw.line(surface, (160, 200, 230), (bx+22, by+5), (bx+22, by+40), 2)
        # Snowflake star at tip
        sf_cx, sf_cy = bx+22, by+3
        for si in range(6):
            sa = si * math.pi / 3
            ex2 = sf_cx + int(math.cos(sa) * 5)
            ey2 = sf_cy + int(math.sin(sa) * 5)
            pygame.draw.line(surface, ICE_BLUE, (sf_cx, sf_cy), (ex2, ey2), 1)
        snowflake_pulse = abs(math.sin(tick * 0.06)) * 0.5 + 0.5
        pygame.draw.circle(surface,
            lerp_color(ICE_BLUE, WHITE, snowflake_pulse), (sf_cx, sf_cy), 3)

        # Name tag (only before talked)
        if not self.talked:
            font = pygame.font.SysFont("consolas", 10, bold=True)
            tag    = font.render(self.name, True, ICE_BLUE)
            tag_sh = font.render(self.name, True, (0, 0, 0))
            surface.blit(tag_sh, (bx + 12 - tag.get_width()//2 + 1, by - 13))
            surface.blit(tag,    (bx + 12 - tag.get_width()//2,     by - 14))
            # Pulsing exclamation mark
            exc_pulse = abs(math.sin(tick * 0.1)) * 0.5 + 0.5
            exc_c     = lerp_color(CYAN, WHITE, exc_pulse)
            exc_scale = int(exc_pulse * 2)
            exc_font  = pygame.font.SysFont("consolas", 12 + exc_scale, bold=True)
            exc    = exc_font.render("!", True, exc_c)
            exc_sh = exc_font.render("!", True, (0, 0, 0))
            surface.blit(exc_sh, (bx + 12 - exc.get_width()//2 + 1, by - 25))
            surface.blit(exc,    (bx + 12 - exc.get_width()//2,     by - 26))

        # Talk prompt pill
        if self.proximity_shown and not self.talked:
            font2  = pygame.font.SysFont("consolas", 11)
            prompt = font2.render("[E] Talk", True, SNOW_WHITE)
            pw, ph = prompt.get_width() + 8, prompt.get_height() + 4
            px2 = bx + 12 - pw // 2
            py2 = by - 38
            pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pill.fill((0, 0, 0, 140))
            surface.blit(pill,   (px2, py2))
            surface.blit(prompt, (px2 + 4, py2 + 2))

# ---------------------------------------------------------------------------
# Dialogue Box  — exact match to Level 4 style
# ---------------------------------------------------------------------------
class DialogueBox:
    def __init__(self, dialogues):
        self.dialogues    = dialogues
        self.index        = 0
        self.active       = True
        self.char_index   = 0
        self.char_speed   = 1.5
        self.char_timer   = 0
        self.done_typing  = False

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
        full_text = self.dialogues[self.index][1]
        self.char_index = min(int(self.char_timer), len(full_text))
        if self.char_index >= len(full_text):
            self.done_typing = True

    def draw(self, surface, tick):
        if not self.active:
            return

        # Box background
        box_h   = 130
        box_y   = SCREEN_HEIGHT - box_h - 20
        box_rect = pygame.Rect(40, box_y, SCREEN_WIDTH - 80, box_h)

        bg = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        r  = 6
        bg.fill((0, 0, 0, 0))
        pygame.draw.rect(bg, (8, 12, 30, 225), (r, 0, box_rect.width - 2*r, box_rect.height))
        pygame.draw.rect(bg, (8, 12, 30, 225), (0, r, box_rect.width, box_rect.height - 2*r))
        for cx2, cy2 in [(r, r), (box_rect.width-r, r),
                         (r, box_rect.height-r), (box_rect.width-r, box_rect.height-r)]:
            pygame.draw.circle(bg, (8, 12, 30, 225), (cx2, cy2), r)
        surface.blit(bg, box_rect.topleft)

        # Border — icy cyan instead of gold
        pygame.draw.rect(surface, ICE_BLUE, box_rect, 2, border_radius=6)

        # Corner snowflake ornaments
        for cx3, cy3 in [(box_rect.left+3, box_rect.top+3),
                         (box_rect.right-3, box_rect.top+3),
                         (box_rect.left+3, box_rect.bottom-3),
                         (box_rect.right-3, box_rect.bottom-3)]:
            pygame.draw.circle(surface, ICE_DARK, (cx3, cy3), 5)
            pygame.draw.circle(surface, ICE_BLUE, (cx3, cy3), 3)

        # Speaker name
        speaker, text = self.dialogues[self.index]
        font_name = pygame.font.SysFont("consolas", 17, bold=True)
        font_text = pygame.font.SysFont("consolas", 14)

        if speaker:
            # Snow Miser gets icy cyan; narrator lines have no speaker
            name_c = ICE_BLUE
            surface.blit(font_name.render(speaker, True, (0,0,0)),
                         (box_rect.x + 17, box_rect.y + 11))
            name_surf = font_name.render(speaker, True, name_c)
            surface.blit(name_surf, (box_rect.x + 16, box_rect.y + 10))
            pygame.draw.line(surface, name_c,
                             (box_rect.x+16, box_rect.y+30),
                             (box_rect.x+16+name_surf.get_width(), box_rect.y+30), 1)
            text_y = box_rect.y + 36
        else:
            text_y = box_rect.y + 14

        # Typewriter text
        shown = text[:self.char_index]
        words = shown.split(" ")
        line  = ""
        ly    = text_y
        max_w = box_rect.width - 32
        for word in words:
            test = line + (" " if line else "") + word
            if font_text.size(test)[0] > max_w:
                ts = font_text.render(line, True, SNOW_WHITE)
                surface.blit(ts, (box_rect.x + 16, ly))
                ly += 20; line = word
            else:
                line = test
        if line:
            ts = font_text.render(line, True, SNOW_WHITE)
            surface.blit(ts, (box_rect.x + 16, ly))

        # Continue prompt
        if self.done_typing:
            blink = (tick // 20) % 2 == 0
            if blink:
                if self.index < len(self.dialogues) - 1:
                    prompt = font_text.render("[ENTER] Continue...", True, GRAY)
                else:
                    prompt = font_text.render("[ENTER] Close", True, GRAY)
                surface.blit(prompt,
                             (box_rect.right - prompt.get_width() - 16, box_rect.bottom - 22))

        # Page counter
        pg_font = pygame.font.SysFont("consolas", 11)
        pg = pg_font.render(f"{self.index+1}/{len(self.dialogues)}", True, (60, 60, 70))
        surface.blit(pg, (box_rect.x + 16, box_rect.bottom - 18))

# ---------------------------------------------------------------------------
# Section Checkpoint — floating flag  (unchanged from original)
# ---------------------------------------------------------------------------
class SectionCheckpoint:
    FLAG_W = 22; FLAG_H = 14

    def __init__(self, trigger_x, spawn_x, spawn_y, float_y, label=""):
        self.trigger_x   = trigger_x
        self.spawn_x     = spawn_x
        self.spawn_y     = spawn_y
        self.float_y     = float_y
        self.label       = label
        self.activated   = False
        self.toast_timer = 0
        self.glow_tick   = 0
        self.bob_tick    = random.randint(0, 60)

    def check(self, player):
        if self.activated or not player.alive: return False
        if player.rect.right >= self.trigger_x:
            self._activate(player); return True
        return False

    def activate_direct(self, player):
        if not self.activated:
            self._activate(player); return True
        return False

    def _activate(self, player):
        self.activated   = True
        self.toast_timer = 150
        self.glow_tick   = 0
        player.spawn_x   = self.spawn_x
        player.spawn_y   = self.spawn_y

    def update(self):
        self.bob_tick += 1
        if self.toast_timer > 0: self.toast_timer -= 1
        if self.activated:       self.glow_tick   += 1

    def draw_flag(self, surface, camera, font):
        if self.trigger_x > 100000:
            if self.toast_timer > 0:
                pos = camera.apply(pygame.Rect(int(self.spawn_x), int(self.float_y), 1, 1))
                sx, sy = pos.x, pos.y
                alpha  = min(255, self.toast_timer * 4)
                rise   = (150 - self.toast_timer) // 4
                ts = font.render(f"CHECKPOINT  {self.label}", True, CP_ACTIVE)
                ts.set_alpha(alpha)
                surface.blit(ts, (sx - ts.get_width()//2, sy - rise))
            return

        bob  = math.sin(self.bob_tick * 0.06) * 5
        wx   = self.trigger_x
        wy   = self.float_y + bob
        pos  = camera.apply(pygame.Rect(int(wx), int(wy), 1, 1))
        sx, sy = pos.x, pos.y
        if sx < -80 or sx > SCREEN_WIDTH + 80: return

        col   = CP_ACTIVE if self.activated else CP_INACTIVE
        pulse = abs(math.sin(self.glow_tick * 0.08)) if self.activated else 0.0

        if self.activated:
            glow_r = 18 + int(6 * pulse)
            gc     = lerp_color(CP_GLOW, (0,0,0), 1 - pulse * 0.6)
            pygame.draw.circle(surface, gc, (sx, sy), glow_r, 2)

        pole_top = sy - 18; pole_bot = sy + 18
        pygame.draw.line(surface, GRAY, (sx, pole_top), (sx, pole_bot), 3)
        fc  = lerp_color(col, WHITE, pulse * 0.45)
        pts = [(sx+1, pole_top),
               (sx+1+self.FLAG_W, pole_top+self.FLAG_H//2),
               (sx+1, pole_top+self.FLAG_H)]
        pygame.draw.polygon(surface, fc, pts)
        pygame.draw.polygon(surface, WHITE, pts, 1)
        lbl = font.render(self.label, True, col)
        surface.blit(lbl, (sx - lbl.get_width()//2, sy + 22))

        if self.toast_timer > 0:
            alpha = min(255, self.toast_timer * 4)
            rise  = (150 - self.toast_timer) // 4
            ts    = font.render(f"CHECKPOINT  {self.label}", True, CP_ACTIVE)
            ts.set_alpha(alpha)
            surface.blit(ts, (sx - ts.get_width()//2, sy - 50 - rise))

# ---------------------------------------------------------------------------
# Base Platform
# ---------------------------------------------------------------------------
class Platform:
    def __init__(self, x, y, w, h, color=GRAY):
        self.rect  = pygame.Rect(x,y,w,h)
        self.color = color

    def is_active(self):              return True
    def get_rect(self):               return self.rect
    def on_player_land(self, player): pass
    def update(self):                 pass

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pygame.draw.rect(surface, self.color, sr)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x, sr.y, sr.width, 5))

# ---------------------------------------------------------------------------
# Shrinking Platform
# ---------------------------------------------------------------------------
class ShrinkingPlatform(Platform):
    def __init__(self, x, y, w, h, shrink_speed=1.2, respawn_time=300):
        super().__init__(x,y,w,h,ICE_BLUE)
        self.SHRINK_SPEED=shrink_speed; self.respawn_time=respawn_time
        self.ox=x; self.oy=y; self.ow=w; self.oh=h
        self.shrinking=self.gone=False; self.rc=0; self.flicker=0

    def on_player_land(self, player):
        if not self.gone: self.shrinking=True

    def is_active(self): return not self.gone

    def update(self):
        if self.gone:
            self.rc+=1
            if self.rc>=self.respawn_time:
                self.rect=pygame.Rect(self.ox,self.oy,self.ow,self.oh)
                self.gone=self.shrinking=False; self.rc=0
            return
        if self.shrinking:
            self.flicker+=1
            nw=self.rect.width-self.SHRINK_SPEED*2
            if nw<=0: self.gone=True; self.rc=0; return
            cx=self.rect.centerx
            self.rect.width=int(nw); self.rect.centerx=cx

    def draw(self, surface, camera):
        if self.gone: return
        sr=camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        ratio=self.rect.width/self.ow
        bc=(lerp_color(ICE_BLUE,RED,1-ratio) if self.shrinking and ratio<0.35 and self.flicker%4<2
            else lerp_color(ICE_DARK,ICE_BLUE,ratio))
        pygame.draw.rect(surface,bc,sr)
        for ix in range(0,sr.width,10):
            pygame.draw.line(surface,SNOW_WHITE,(sr.x+ix,sr.y+2),(sr.x+ix+4,sr.y+6),1)
        pygame.draw.rect(surface,SNOW_WHITE,(sr.x,sr.y,sr.width,4))
        if self.shrinking and ratio<0.5:
            pygame.draw.rect(surface,RED if self.flicker%6<3 else YELLOW,sr,2)

# ---------------------------------------------------------------------------
# Falling Platform
# ---------------------------------------------------------------------------
class FallingPlatform(Platform):
    FALL_ACCEL=0.15; MAX_FALL=8.0
    def __init__(self, x, y, w, h, delay=25, respawn_time=300):
        super().__init__(x,y,w,h,FALLING_BROWN)
        self.delay=delay; self.respawn_time=respawn_time
        self.ox=x; self.oy=y
        self.dt=0; self.falling=False; self.fs=0.0; self.gone=False; self.rc=0; self.st=0

    def on_player_land(self, player):
        if not self.falling and not self.gone:
            self.dt=self.delay; self.st=0

    def is_active(self): return not self.gone

    def update(self):
        if self.gone:
            self.rc+=1
            if self.rc>=self.respawn_time:
                self.rect.x=self.ox; self.rect.y=self.oy
                self.gone=self.falling=False; self.fs=0.0; self.dt=0; self.rc=0
            return
        if self.dt>0:
            self.dt-=1; self.st+=1
            if self.dt==0: self.falling=True
        if self.falling:
            self.fs=min(self.fs+self.FALL_ACCEL,self.MAX_FALL)
            self.rect.y+=int(self.fs)
            if self.rect.top>DEATH_Y+100: self.gone=True; self.rc=0

    def draw(self, surface, camera):
        if self.gone: return
        shake=int(math.sin(self.st*1.2)*3) if self.dt>0 else 0
        dr=self.rect.copy(); dr.x+=shake
        sr=camera.apply(dr)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        pygame.draw.rect(surface,FALLING_BROWN,sr)
        for i in range(3):
            ly=sr.y+6+i*8
            if ly<sr.bottom:
                pygame.draw.line(surface,(120,70,30),(sr.x+2,ly),(sr.right-2,ly),1)
        pygame.draw.rect(surface,SNOW_WHITE,(sr.x,sr.y,sr.width,5))
        if self.falling: pygame.draw.rect(surface,ORANGE,sr,2)

# ---------------------------------------------------------------------------
# Phantom Platform
# ---------------------------------------------------------------------------
class PhantomPlatform(Platform):
    def __init__(self, x, y, w, h, visible_frames=18, respawn_time=240):
        super().__init__(x,y,w,h,PHANTOM_TEAL)
        self.VF=visible_frames; self.respawn_time=respawn_time
        self.touched=self.gone=False; self.vt=0; self.rc=0
        self.tick=random.randint(0,60)

    def on_player_land(self, player):
        if not self.gone and not self.touched:
            self.touched=True; self.vt=self.VF

    def is_active(self): return not self.gone

    def update(self):
        self.tick+=1
        if self.gone:
            self.rc+=1
            if self.rc>=self.respawn_time:
                self.gone=self.touched=False; self.vt=0; self.rc=0
            return
        if self.touched:
            self.vt-=1
            if self.vt<=0: self.gone=True; self.rc=0

    def draw(self, surface, camera):
        sr=camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        if self.gone:
            pygame.draw.rect(surface,(20,60,55),sr,1); return
        ar=(self.vt/self.VF if self.touched
            else 0.55+0.25*abs(math.sin(self.tick*0.07)))
        col=tuple(max(0,min(255,int(c*ar))) for c in PHANTOM_TEAL)
        pygame.draw.rect(surface,col,sr)
        for ix in range(0,sr.width,7):
            if (self.tick+ix)%10<5:
                lc=tuple(min(c+60,255) for c in col)
                pygame.draw.line(surface,lc,(sr.x+ix,sr.y),(sr.x+ix,sr.bottom))
        pygame.draw.rect(surface,CYAN,sr,1)
        if self.touched and self.vt%4<2:
            pygame.draw.rect(surface,RED,sr,2)

# ---------------------------------------------------------------------------
# OBSTACLE 1 — Countdown Platform
# ---------------------------------------------------------------------------
class CountdownPlatform(Platform):
    IDLE     = "idle"
    COUNTING = "counting"
    GO       = "go"
    FALLING  = "falling"

    def __init__(self, x, y, w, h, countdown_frames=180, grace_frames=COUNTDOWN_GRACE):
        super().__init__(x,y,w,h,COUNTDOWN_COL)
        self.countdown_frames = countdown_frames
        self.grace_frames     = grace_frames
        self.ox = x; self.oy = y
        self.state     = self.IDLE
        self.countdown = 0
        self.grace     = 0
        self.fall_vy   = 0.0
        self.tick      = 0
        self.target    = None

    def reset(self):
        self.rect.x  = self.ox
        self.rect.y  = self.oy
        self.state   = self.IDLE
        self.countdown = 0
        self.grace   = 0
        self.fall_vy = 0.0
        if self.target:
            self.target.on_countdown_reset()

    def on_player_land(self, player):
        if self.state == self.IDLE:
            self.state     = self.COUNTING
            self.countdown = self.countdown_frames

    def is_active(self):
        return self.state != self.FALLING or self.rect.y < DEATH_Y + 200

    def target_visible(self):
        return self.state in (self.GO, self.FALLING)

    def update(self):
        self.tick += 1
        if self.state == self.COUNTING:
            self.countdown -= 1
            if self.countdown <= 0:
                self.state = self.GO
                self.grace = self.grace_frames
        elif self.state == self.GO:
            self.grace -= 1
            if self.grace <= 0:
                self.state   = self.FALLING
                self.fall_vy = 0.0
        elif self.state == self.FALLING:
            self.fall_vy = min(self.fall_vy + 0.4, 12)
            self.rect.y += int(self.fall_vy)
            if self.rect.top > DEATH_Y + 300:
                self.reset()

    def current_display(self):
        if self.state == self.IDLE:     return None
        if self.state == self.COUNTING:
            seg = self.countdown_frames // 3
            if self.countdown > seg*2: return "3"
            elif self.countdown > seg: return "2"
            else:                      return "1"
        if self.state == self.GO:       return "GO!"
        return None

    def draw(self, surface, camera):
        if self.state == self.FALLING and self.rect.top > DEATH_Y: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return

        pulse = abs(math.sin(self.tick * 0.15))
        if self.state == self.COUNTING:
            col = lerp_color(COUNTDOWN_COL, WHITE, pulse * 0.4)
        elif self.state == self.GO:
            col = lerp_color((30,180,80), GOLD, pulse)
        elif self.state == self.FALLING:
            col = lerp_color(RED, (80,20,20), pulse)
        else:
            col = COUNTDOWN_COL

        pygame.draw.rect(surface, col, sr)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x, sr.y, sr.width, 5))

        txt = self.current_display()
        if txt:
            f  = pygame.font.SysFont("consolas", 52, bold=True)
            tc = lerp_color(GOLD, WHITE, pulse) if txt=="GO!" else lerp_color(RED, YELLOW, pulse)
            t  = f.render(txt, True, tc)
            surface.blit(t, (sr.centerx - t.get_width()//2, sr.y - 70))

        if self.state == self.GO and self.grace > 0:
            bar_w = int(sr.width * self.grace / self.grace_frames)
            bar_y = sr.y - 12
            pygame.draw.rect(surface, DARK_GRAY, (sr.x, bar_y, sr.width, 6))
            pygame.draw.rect(surface,
                             lerp_color(RED, (50,220,80), self.grace/self.grace_frames),
                             (sr.x, bar_y, bar_w, 6))


class CountdownTargetPlatform(Platform):
    def __init__(self, x, y, w, h, owner):
        super().__init__(x, y, w, h, PINE_GREEN)
        self.owner      = owner
        self.section_cp = None
        self.landed     = False

    def is_active(self):
        if self.landed: return True
        return self.owner.target_visible()

    def on_countdown_reset(self):
        pass  # landing flag keeps it solid

    def on_player_land(self, player):
        self.landed = True
        if self.section_cp is not None:
            self.section_cp.activate_direct(player)

    def draw(self, surface, camera):
        if not self.is_active():
            sr = camera.apply(self.rect)
            if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
            s = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
            s.fill((COUNTDOWN_COL[0], COUNTDOWN_COL[1], COUNTDOWN_COL[2], 40))
            surface.blit(s, (sr.x, sr.y))
            return
        if self.landed:
            sr = camera.apply(self.rect)
            if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
            pygame.draw.rect(surface, lerp_color(PINE_GREEN, GOLD, 0.25), sr)
            pygame.draw.rect(surface, SNOW_WHITE, (sr.x, sr.y, sr.width, 5))
        else:
            super().draw(surface, camera)

# ---------------------------------------------------------------------------
# OBSTACLE 2 — Zigzag Floating Ledges
# ---------------------------------------------------------------------------
PH = 28   # platform height constant used throughout

class ZigzagLedge(Platform):
    LEDGE_W = 70
    LEDGE_H = 14

    def __init__(self, x, y, side, owner_climb, step_index, ledge_w=None):
        col = LEDGE_L_COL if side == "LEFT" else LEDGE_R_COL
        w = ledge_w if ledge_w is not None else self.LEDGE_W
        super().__init__(x, y, w, self.LEDGE_H, col)
        self.side        = side
        self.owner_climb = owner_climb
        self.step_index  = step_index
        self.flash       = 0
        self.done        = False

    def on_player_land(self, player):
        result = self.owner_climb.register_landing(self.step_index)
        self.flash = 12
        self.done  = True

    def update(self):
        if self.flash > 0:   self.flash -= 1
        elif self.flash < 0: self.flash += 1

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return

        base_col = lerp_color(self.color, PINE_GREEN, 0.55) if self.done else self.color
        if self.flash > 0:
            col = lerp_color(base_col, WHITE, self.flash/12)
        elif self.flash < 0:
            col = lerp_color(base_col, RED, abs(self.flash)/20)
        else:
            col = base_col

        pygame.draw.rect(surface, col, sr)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x, sr.y, sr.width, 4))

        f = pygame.font.SysFont("consolas", 10, bold=True)
        n = f.render(str(self.step_index+1), True, WHITE)
        surface.blit(n, (sr.centerx - n.get_width()//2, sr.y - 14))


class ZigzagClimbSection:
    def __init__(self):
        self.total_steps  = WALL_STEPS * 2
        self.top_index    = self.total_steps - 1
        self.highest_hit  = -1
        self.unlocked     = False
        self.started      = False

    def register_landing(self, step_index):
        if self.unlocked: return "already_done"
        self.started = True
        if step_index > self.highest_hit:
            self.highest_hit = step_index
        if step_index == self.top_index:
            self.unlocked = True
        return "hit"

    def progress_text(self):
        if self.unlocked:    return "CLIMB COMPLETE!  Jump to exit →"
        if not self.started: return "Zigzag up! Reach the TOP ledge (10)"
        remaining = self.top_index - self.highest_hit
        return f"Reached {self.highest_hit+1}/10 — {remaining} more to go!"


class ZigzagExitPlatform(Platform):
    def __init__(self, x, y, w, h, owner):
        super().__init__(x, y, w, h, PINE_GREEN)
        self.owner = owner

    def is_active(self): return self.owner.unlocked

    def draw(self, surface, camera):
        if not self.is_active():
            sr = camera.apply(self.rect)
            if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
            s = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
            s.fill((LEDGE_R_COL[0], LEDGE_R_COL[1], LEDGE_R_COL[2], 60))
            surface.blit(s, (sr.x, sr.y))
            return
        super().draw(surface, camera)


def build_zigzag_section(base_x, base_y, ledge_w=70):
    climb = ZigzagClimbSection()
    plats = []

    right_x = base_x + LEDGE_GAP
    left_x  = base_x

    step = 0
    for i in range(WALL_STEPS):
        r_y = base_y - i * LEDGE_RISE
        r_ledge = ZigzagLedge(right_x, r_y, "RIGHT", climb, step, ledge_w)
        plats.append(r_ledge)
        step += 1

        l_y = base_y - i * LEDGE_RISE - LEDGE_RISE // 2
        l_ledge = ZigzagLedge(left_x, l_y, "LEFT", climb, step, ledge_w)
        plats.append(l_ledge)
        step += 1

    highest_left_y = base_y - (WALL_STEPS - 1) * LEDGE_RISE - LEDGE_RISE // 2
    exit_y   = highest_left_y - 70 - PH
    exit_x   = right_x - 20
    exit_plat = ZigzagExitPlatform(exit_x, exit_y, 220, PH, owner=climb)
    plats.append(exit_plat)

    return plats, climb, exit_plat

# ---------------------------------------------------------------------------
# OBSTACLE 3 — Tram + Santa Sleigh
# ---------------------------------------------------------------------------
class TramPlatform(Platform):
    FALL_SPEED = 0.5
    MAX_FALL   = 14

    def __init__(self, x, y, w, h, speed=3, vanish_x=None):
        super().__init__(x,y,w,h,MOVING_COL)
        self.speed      = speed
        self.moving     = False
        self.origin_x   = x
        self.origin_y   = y
        self.vanish_x   = vanish_x
        self.dx         = 0
        self.falling    = False
        self.fall_vy    = 0.0
        self.gone       = False
        self.warn_flash = 0

    def on_player_land(self, player):
        if not self.falling and not self.gone:
            self.moving = True

    def is_active(self):
        return not self.gone

    def reset(self):
        self.rect.x   = self.origin_x
        self.rect.y   = self.origin_y
        self.moving   = False
        self.falling  = False
        self.gone     = False
        self.fall_vy  = 0.0
        self.dx       = 0
        self.warn_flash = 0

    def update(self):
        if self.gone:
            self.dx = 0; return
        if self.falling:
            self.dx       = 0
            self.fall_vy  = min(self.fall_vy + self.FALL_SPEED, self.MAX_FALL)
            self.rect.y  += int(self.fall_vy)
            if self.rect.top > DEATH_Y + 200:
                self.gone = True
            return
        if self.moving:
            if self.vanish_x is not None and self.rect.x >= self.vanish_x:
                self.falling  = True
                self.fall_vy  = 0.0
                self.dx       = 0
            else:
                self.rect.x  += self.speed
                self.dx       = self.speed
                if self.vanish_x is not None:
                    dist = self.vanish_x - self.rect.x
                    if dist < 120:
                        self.warn_flash = (self.warn_flash + 1) % 12
        else:
            self.dx = 0

    def draw(self, surface, camera):
        if self.gone: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        if self.vanish_x is not None and self.moving and not self.falling:
            dist = self.vanish_x - self.rect.x
            if dist < 120:
                warn_t = 1.0 - dist / 120
                col = lerp_color(MOVING_COL, RED, warn_t)
            else:
                col = MOVING_COL
        else:
            col = MOVING_COL
        pygame.draw.rect(surface, col, sr)
        for i in range(3):
            lx = sr.x + 15 + i * (sr.width // 3 - 5)
            pygame.draw.line(surface, SLEIGH_GOLD, (lx, sr.y+4), (lx, sr.bottom-4), 2)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x, sr.y, sr.width, 5))
        pygame.draw.rect(surface, SLEIGH_GOLD, sr, 2)
        if self.moving and not self.falling:
            f = pygame.font.SysFont("consolas", 14, bold=True)
            if self.vanish_x is not None and self.vanish_x - self.rect.x < 200:
                t = f.render("JUMP TO SLEIGH!", True, RED)
            else:
                t = f.render("RIDE THE TRAM", True, GOLD)
            surface.blit(t, (sr.centerx - t.get_width()//2, sr.y - 22))


class SantaSleigh:
    WIDTH  = 160
    HEIGHT = 30

    def __init__(self, portal_x, portal_y, tram,
                 rope_len=130, rope_grab_r=14,
                 hover_timeout=300, kidnap_dist=250):
        self.tram          = tram
        self.portal_x      = portal_x
        self.portal_y      = portal_y
        self.ROPE_LEN      = rope_len
        self.ROPE_W        = rope_grab_r
        self.HOVER_TIMEOUT = hover_timeout
        self.KIDNAP_DIST   = kidnap_dist
        self.wx            = float(SCREEN_WIDTH + 400)
        self.wy            = float(-200)
        self.rect          = pygame.Rect(int(self.wx), int(self.wy), self.WIDTH, self.HEIGHT)
        self.state         = "waiting"
        self.tick          = 0
        self.hover_tick    = 0
        self.player_grabbed= False
        self.carry_tick    = 0

    def rope_tip_world(self):
        cx = int(self.wx + self.WIDTH // 2)
        cy = int(self.wy + self.HEIGHT + self.ROPE_LEN)
        return cx, cy

    def rope_grab_rect(self):
        rope_top_x = int(self.wx + self.WIDTH // 2)
        rope_top_y = int(self.wy + self.HEIGHT)
        w = max(30, self.ROPE_W * 2)
        return pygame.Rect(rope_top_x - w // 2, rope_top_y, w, self.ROPE_LEN)

    def reset(self):
        self.wx             = float(SCREEN_WIDTH + 400)
        self.wy             = float(-200)
        self.rect.x         = int(self.wx)
        self.rect.y         = int(self.wy)
        self.state          = "waiting"
        self.tick           = 0
        self.hover_tick     = 0
        self.player_grabbed = False
        self.carry_tick     = 0

    def start(self, tram_rect):
        self.wx    = float(tram_rect.centerx + 500)
        self.wy    = float(tram_rect.top - 380)
        self.state = "flying_in"

    def update(self, player):
        self.tick += 1
        tr = self.tram.rect

        if self.state == "flying_in":
            tx = float(tr.centerx - self.WIDTH // 2)
            ty = float(tr.top - 260)
            self.wx += (tx - self.wx) * 0.06
            self.wy += (ty - self.wy) * 0.06
            if abs(self.wx - tx) < 10 and abs(self.wy - ty) < 10:
                self.state      = "hovering"
                self.hover_tick = 0

        elif self.state == "hovering":
            if not self.tram.falling and not self.tram.gone:
                tx = float(tr.centerx - self.WIDTH // 2)
                ty = float(tr.top - 260) + math.sin(self.tick * 0.07) * 8
                self.wx += (tx - self.wx) * 0.12
                self.wy += (ty - self.wy) * 0.10
            else:
                self.wy += math.sin(self.tick * 0.09) * 0.6

            self.hover_tick += 1

            if player.alive and not self.player_grabbed:
                grip = self.rope_grab_rect()
                if player.rect.colliderect(grip):
                    self.player_grabbed = True
                    self.state          = "carrying"
                    self.carry_tick     = 0
                    player.riding_platform = None

            if self.hover_tick >= self.HOVER_TIMEOUT:
                self.state = "kidnapping"

        elif self.state == "carrying":
            self.carry_tick += 1
            self.wx += 5
            self.wy += math.sin(self.tick * 0.05) * 0.4

            if player.alive:
                cx, cy = self.rope_tip_world()
                player.rect.centerx = cx
                player.rect.bottom  = cy + player.HEIGHT // 2
                player.vel_x        = 0
                player.vel_y        = 0
                player.on_ground    = False

                keys = pygame.key.get_pressed()
                if self.carry_tick > 10 and (
                        keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
                    self.player_grabbed = False
                    self.state          = "done"
                    player.vel_x = 7
                    player.vel_y = -10

            if self.state == "carrying" and self.wx > self.portal_x + self.KIDNAP_DIST:
                self.state = "kidnapping"

        elif self.state == "kidnapping":
            self.wx += 16
            self.wy -= 6
            if player.alive and self.player_grabbed:
                cx, cy = self.rope_tip_world()
                player.rect.centerx = cx
                player.rect.bottom  = cy + player.HEIGHT // 2
                player.vel_x = 0; player.vel_y = 0
            if self.wx > self.portal_x + 900:
                result = "kill_player" if self.player_grabbed else None
                self.player_grabbed = False
                self.state = "done"
                return result

        self.rect.x = int(self.wx)
        self.rect.y = int(self.wy)
        return None

    def draw(self, surface, camera):
        if self.state in ("waiting", "done"): return

        sr = camera.apply(self.rect)
        if -200 < sr.x < SCREEN_WIDTH + 200:
            pygame.draw.rect(surface, SLEIGH_BROWN, sr)
            pygame.draw.rect(surface, SLEIGH_GOLD, sr, 2)
            for side in (sr.x + 8, sr.right - 18):
                pygame.draw.arc(surface, SLEIGH_GOLD,
                                (side, sr.bottom-4, 10, 8), 0, math.pi, 2)
            hx = sr.centerx - 12; hy = sr.y - 28
            pygame.draw.rect(surface, SANTA_RED,       (hx,    hy+10, 24, 18))
            pygame.draw.rect(surface, (50, 30, 10),    (hx,    hy+18, 24,  4))
            pygame.draw.rect(surface, SLEIGH_GOLD,     (hx+9,  hy+17,  6,  6))
            pygame.draw.rect(surface, (240, 200, 160), (hx+4,  hy,    16, 12))
            pygame.draw.rect(surface, SANTA_RED,       (hx+4,  hy-8,  16, 10))
            pygame.draw.rect(surface, WHITE,           (hx+2,  hy-1,  20,  4))
            pygame.draw.circle(surface, WHITE, (hx+20, hy-8), 3)
            pygame.draw.rect(surface, WHITE,   (hx+2,  hy+6,  20,  8))

        cx_w, cy_w = self.rope_tip_world()
        rp_top = camera.apply(pygame.Rect(int(self.wx + self.WIDTH//2), int(self.wy + self.HEIGHT), 1, 1))
        rp_bot = camera.apply(pygame.Rect(cx_w, cy_w, 1, 1))

        pygame.draw.line(surface, (180, 120, 60),
                         (rp_top.x, rp_top.y), (rp_bot.x, rp_bot.y), 3)
        pulse = int(4 + abs(math.sin(self.tick * 0.15)) * 4)
        ring_col = (GOLD if self.state == "hovering" else
                    (100, 220, 100) if self.state == "carrying" else RED)
        pygame.draw.circle(surface, ring_col, (rp_bot.x, rp_bot.y), pulse + 4)
        pygame.draw.circle(surface, WHITE,    (rp_bot.x, rp_bot.y), pulse + 4, 2)

        if self.state == "hovering" and not self.player_grabbed:
            f = pygame.font.SysFont("consolas", 13, bold=True)
            t = f.render("JUMP TO GRAB ROPE!", True, GOLD)
            surface.blit(t, (rp_bot.x - t.get_width()//2, rp_bot.y - 28))
            if self.hover_tick > self.HOVER_TIMEOUT // 2:
                ratio = 1 - self.hover_tick / self.HOVER_TIMEOUT
                bx, by = sr.x, sr.y - 12
                pygame.draw.rect(surface, DARK_GRAY, (bx, by, sr.width, 6))
                pygame.draw.rect(surface, RED,       (bx, by, int(sr.width * ratio), 6))
        elif self.state == "carrying":
            f = pygame.font.SysFont("consolas", 13, bold=True)
            t = f.render("JUMP to release at portal!", True, (100, 255, 100))
            surface.blit(t, (rp_bot.x - t.get_width()//2, rp_bot.y - 28))
        elif self.state == "kidnapping":
            f = pygame.font.SysFont("consolas", 14, bold=True)
            t = f.render("HO HO HO! BYE BYE!", True, RED)
            surface.blit(t, (sr.centerx - t.get_width()//2, sr.y - 50))

# ---------------------------------------------------------------------------
# Spike Trap
# ---------------------------------------------------------------------------
class SpikeTrap:
    SPIKE_W=14; SPIKE_H=22
    def __init__(self,x,y,count):
        self.x=x; self.y=y; self.count=count
        self.rect=pygame.Rect(x,y-self.SPIKE_H,count*self.SPIKE_W,self.SPIKE_H)
    def check_kill(self,player): return player.alive and self.rect.colliderect(player.rect)
    def draw(self,surface,camera):
        for i in range(self.count):
            sx=self.x+i*self.SPIKE_W
            pos=camera.apply(pygame.Rect(sx,self.y-self.SPIKE_H,self.SPIKE_W,self.SPIKE_H))
            tip=(pos.x+pos.width//2,pos.y)
            pygame.draw.polygon(surface,SPIKE_GRAY,[tip,(pos.x,pos.bottom),(pos.right,pos.bottom)])
            pygame.draw.polygon(surface,WHITE,[tip,(pos.x,pos.bottom),(pos.right,pos.bottom)],1)
            pygame.draw.circle(surface,RED,tip,3)

# ---------------------------------------------------------------------------
# Balloon
# ---------------------------------------------------------------------------
class Balloon:
    RADIUS=14; STRING_LEN=30
    def __init__(self,x,y,launch_vx=9,launch_vy=-11,radius=14):
        self.x=float(x); self.y=float(y)
        self.RADIUS=radius
        self.launch_vx=launch_vx; self.launch_vy=launch_vy
        self.grabbed=False; self.rc=0; self.tick=0
        self.rect=pygame.Rect(int(x)-self.RADIUS,int(y)-self.RADIUS,self.RADIUS*2,self.RADIUS*2)
    def update(self):
        self.tick+=1
        if self.grabbed:
            self.rc+=1
            if self.rc>=360: self.grabbed=False; self.rc=0
        self.rect.centery=int(self.y+math.sin(self.tick*0.06)*8)
        self.rect.centerx=int(self.x)
    def check_grab(self,player):
        if self.grabbed or not player.alive: return False
        if self.rect.colliderect(player.rect):
            self.grabbed=True; self.rc=0
            player.vel_x=self.launch_vx; player.vel_y=self.launch_vy
            player.on_ground=False; return True
        return False
    def draw(self,surface,camera,tick):
        if self.grabbed: return
        bob=int(math.sin(self.tick*0.06)*8)
        cx,cy=int(self.x),int(self.y)+bob
        pos=camera.apply(pygame.Rect(cx,cy,1,1)); sx,sy=pos.x,pos.y
        if sx<-40 or sx>SCREEN_WIDTH+40: return
        r=self.RADIUS; pulse=abs(math.sin(self.tick*0.08))*0.5+0.5
        pygame.draw.circle(surface,(80,10,20),(sx,sy),r+int(8*pulse),3)
        pygame.draw.circle(surface,BALLOON_RED,(sx,sy),r)
        pygame.draw.circle(surface,BALLOON_PINK,(sx-r//3,sy-r//3),r//3)
        pygame.draw.circle(surface,CANDY_RED,(sx,sy+r),3)
        pygame.draw.line(surface,GOLD,(sx,sy+r+3),(sx+int(math.sin(self.tick*0.04)*4),sy+r+self.STRING_LEN),1)
        for k in range(4):
            a=self.tick*0.08+k*math.pi/2
            dx=int(math.cos(a)*(r+10)); dy=int(math.sin(a)*(r+10))
            pygame.draw.rect(surface,rainbow_color(tick+k*20,0.2),(sx+dx-2,sy+dy-2,4,4))

# ---------------------------------------------------------------------------
# Portal
# ---------------------------------------------------------------------------
class Portal:
    def __init__(self,x,y):
        self.rect=pygame.Rect(x,y,56,80); self.pulse=0
    def update(self): self.pulse=(self.pulse+3)%360
    def check(self,player): return player.alive and player.rect.colliderect(self.rect)
    def draw(self,surface,camera):
        sr=camera.apply(self.rect)
        p=abs(math.sin(math.radians(self.pulse)))
        pygame.draw.ellipse(surface,lerp_color(PORTAL_BLUE,PORTAL_CYAN,p),sr.inflate(14,14),5)
        pygame.draw.ellipse(surface,lerp_color((0,20,40),(0,60,80),p),sr.inflate(-8,-8))
        for k in range(6):
            ang=math.radians(self.pulse+k*60)
            x1=sr.centerx+int(math.cos(ang)*10); y1=sr.centery+int(math.sin(ang)*10)
            x2=sr.centerx+int(math.cos(ang)*24); y2=sr.centery+int(math.sin(ang)*24)
            pygame.draw.line(surface,lerp_color(PORTAL_CYAN,WHITE,p),(x1,y1),(x2,y2),2)
        f=pygame.font.SysFont("consolas",12,bold=True); lbl=f.render("PORTAL",True,WHITE)
        surface.blit(lbl,(sr.x+sr.width//2-lbl.get_width()//2,sr.y-18))

# ---------------------------------------------------------------------------
# Snowflake
# ---------------------------------------------------------------------------
class Snowflake:
    def __init__(self): self.reset()
    def reset(self):
        self.x=random.randint(0,SCREEN_WIDTH); self.y=random.randint(-20,SCREEN_HEIGHT)
        self.speed=random.uniform(0.5,2); self.drift=random.uniform(-0.3,0.3)
        self.size=random.randint(2,5); self.alpha=random.randint(120,220)
    def update(self):
        self.y+=self.speed; self.x+=self.drift
        if self.y>SCREEN_HEIGHT+10: self.reset(); self.y=-10
    def draw(self,surf):
        c=tuple(min(255,int(SNOW_WHITE[i]*self.alpha/255)) for i in range(3))
        pygame.draw.circle(surf,c,(int(self.x),int(self.y)),self.size)

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player:
    WIDTH, HEIGHT = 28, 36

    def __init__(self, x, y, move_speed=MOVE_SPEED, jump_velocity=JUMP_VELOCITY):
        self.rect=pygame.Rect(x,y,self.WIDTH,self.HEIGHT)
        self.vel_x=self.vel_y=0.0; self.on_ground=False
        self.spawn_x=x; self.spawn_y=y
        self.alive=True; self.respawn_timer=0
        self.facing_right=True; self.riding_platform=None
        self.move_speed=move_speed; self.jump_velocity=jump_velocity
        self.squash_timer=0; self.was_on_ground=False
        init_player_sprite(self)

    def die(self):
        self.alive=False; self.respawn_timer=9999
        self._spr_state='death'; self._spr_frame=0; self._spr_tick=0; self._spr_death_done=False

    def respawn(self):
        self.rect.topleft=(self.spawn_x,self.spawn_y)
        self.vel_x=self.vel_y=0; self.alive=True
        self.on_ground=False; self.riding_platform=None

    def update(self, keys, platforms):
        if not self.alive:
            # Soul system handles respawn — just wait
            return None

        if self.riding_platform is not None and hasattr(self.riding_platform, 'dx'):
            self.rect.x += self.riding_platform.dx

        move=0.0
        speed=SPRINT_SPEED if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else self.move_speed
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: move-=speed; self.facing_right=False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move+=speed; self.facing_right=True
        self.vel_x = self.vel_x+(move-self.vel_x)*0.3 if move else self.vel_x*0.75
        if abs(self.vel_x)<0.1: self.vel_x=0

        self.vel_y=min(self.vel_y+GRAVITY,MAX_FALL_SPEED)
        jumped=False
        if self.on_ground and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.vel_y=self.jump_velocity; self.on_ground=False
            self.riding_platform=None; jumped=True

        self.rect.x+=int(self.vel_x)
        for plat in platforms:
            if not plat.is_active(): continue
            pr=plat.get_rect()
            if self.rect.colliderect(pr):
                if self.rect.bottom<=pr.top+6: continue
                if self.vel_x>0: self.rect.right=pr.left
                elif self.vel_x<0: self.rect.left=pr.right
                self.vel_x=0

        self.was_on_ground=self.on_ground
        self.on_ground=False; self.riding_platform=None
        vy=int(self.vel_y)
        if self.vel_y>0 and vy==0: vy=1
        self.rect.y+=vy
        for plat in platforms:
            if not plat.is_active(): continue
            pr=plat.get_rect()
            if self.rect.colliderect(pr):
                if self.vel_y>0:
                    self.rect.bottom=pr.top; self.vel_y=0; self.on_ground=True
                    self.riding_platform=plat
                    plat.on_player_land(self)
                elif self.vel_y<0:
                    self.rect.top=pr.bottom; self.vel_y=0

        if self.rect.top > SCREEN_HEIGHT - SCREEN_HEIGHT // 10 and self.alive: self.die()
        return "jump" if jumped else None

    def draw(self,surface,camera,tick):
        draw_player_sprite(self, surface, camera, tick)

# ---------------------------------------------------------------------------
# Sound Manager
# ---------------------------------------------------------------------------
SOUND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
SOUND_FILES= {"jump":"jump.wav","death":"death.wav","respawn":"respawn.wav",
              "balloon":"powerup.wav","balloon_pop":"balloon_pop.wav",
              "checkpoint":"checkpoint.wav","win":"win.wav",
              "npc_talk":"npc_talk.wav",
              "soul_rise":"soul_rise.wav","soul_land":"soul_land.wav"}

MUSIC_FILE = r"C:\Users\ilham\Documents\APU WORKS\YEAR 2 SEM 2\IMAGING & SE\GameAssignment\imaging-assignment\assets\audio\backgroundlevel2.mp3"

class SoundManager:
    def __init__(self):
        self.sounds={}; self.music_loaded=False
        for name,fn in SOUND_FILES.items():
            p=os.path.join(SOUND_DIR,fn)
            if os.path.isfile(p):
                try: self.sounds[name]=pygame.mixer.Sound(p)
                except: self.sounds[name]=None
            else:
                self.sounds[name]=None
        if os.path.isfile(MUSIC_FILE):
            try: pygame.mixer.music.load(MUSIC_FILE); self.music_loaded=True
            except: pass
    def play(self,name):
        s=self.sounds.get(name)
        if s: s.play()
    def start_music(self,loops=-1,volume=0.5):
        if self.music_loaded:
            pygame.mixer.music.set_volume(volume); pygame.mixer.music.play(loops)
    def stop_music(self): pygame.mixer.music.stop()

# ---------------------------------------------------------------------------
# Level layout  (unchanged, but NPCs injected at checkpoint positions)
# ---------------------------------------------------------------------------
PW_SAFE=250; PW_SHRINK=160; PW_FALL=140; PW_PHANTOM=110

def create_christmas_level(preset):
    platforms=[]; section_checkpoints=[]
    shrink_platforms=[]; fall_platforms=[]; phantom_platforms=[]
    countdown_platforms=[]; spikes=[]
    tram_platform=None; santa_sleigh=None; balloon=None
    zigzag_section=None; countdown_platform_ref=None
    npcs = []   # ← NEW: NPC list

    def add(p): platforms.append(p); return p

    # ── START — Snow Miser intro NPC ─────────────────────────────────────
    add(Platform(0, BASE_Y, PW_SAFE, PH, PINE_GREEN))
    npcs.append(NPC(80, BASE_Y, "intro", "Snow Miser"))   # intro dialogue

    # ── ICE shrink ───────────────────────────────────────────────────────
    sp=preset["shrink_speed"]; sr_t=preset["shrink_respawn"]
    for p in [ShrinkingPlatform(420,BASE_Y-30,PW_SHRINK,PH,sp,sr_t),
              ShrinkingPlatform(660,BASE_Y-60,PW_SHRINK,PH,sp,sr_t)]:
        add(p); shrink_platforms.append(p)

    add(Platform(910,BASE_Y-40,PW_SAFE,PH,PINE_GREEN))
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=960, spawn_x=920, spawn_y=BASE_Y-80,
        float_y=BASE_Y-120, label="A"))
    npcs.append(NPC(950, BASE_Y-40, "cp_a", "Snow Miser"))   # CP-A dialogue

    # ── FALL platforms ───────────────────────────────────────────────────
    fd=preset["fall_delay"]
    for p in [FallingPlatform(1240,BASE_Y-20,PW_FALL,PH,fd),
              FallingPlatform(1460,BASE_Y,PW_FALL,PH,fd)]:
        add(p); fall_platforms.append(p)

    add(Platform(1690,BASE_Y,100,PH,PINE_GREEN))
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=1740, spawn_x=1700, spawn_y=BASE_Y-40,
        float_y=BASE_Y-130, label="B"))
    npcs.append(NPC(1730, BASE_Y, "cp_b", "Snow Miser"))     # CP-B dialogue

    # ── SPIKES + BALLOON ─────────────────────────────────────────────────
    sbx=1880; sby=BASE_Y+10
    add(Platform(sbx,sby,140,PH,(60,60,70)))
    spikes.append(SpikeTrap(sbx+6,sby,9))
    balloon=Balloon(sbx+70,sby-90,preset["balloon_vx"],preset["balloon_vy"],preset["balloon_radius"])

    add(Platform(2120,BASE_Y-20,PW_SAFE,PH,PINE_GREEN))
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=2170, spawn_x=2130, spawn_y=BASE_Y-60,
        float_y=BASE_Y-140, label="C"))
    npcs.append(NPC(2160, BASE_Y-20, "cp_c", "Snow Miser")) # CP-C dialogue

    # ── PHANTOM ──────────────────────────────────────────────────────────
    pf=preset["phantom_frames"]; pw=preset["phantom_w"]
    for p in [PhantomPlatform(2450,BASE_Y-50,pw,PH,pf),
              PhantomPlatform(2640,BASE_Y-80,pw,PH,pf)]:
        add(p); phantom_platforms.append(p)

    add(Platform(2840,BASE_Y-60,PW_SAFE+50,PH,PINE_GREEN))
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=2900, spawn_x=2850, spawn_y=BASE_Y-100,
        float_y=BASE_Y-150, label="D"))
    npcs.append(NPC(2890, BASE_Y-60, "cp_d", "Snow Miser")) # CP-D dialogue

    # ── OBSTACLE 1: COUNTDOWN ────────────────────────────────────────────
    add(Platform(3060,BASE_Y-60,120,PH,PINE_GREEN))

    cnt_frames=preset["countdown_sec"]*FPS
    cd_pad=CountdownPlatform(3240,BASE_Y-60,180,PH,
                             countdown_frames=cnt_frames,
                             grace_frames=preset["countdown_grace"])
    add(cd_pad); countdown_platforms.append(cd_pad)
    countdown_platform_ref=cd_pad

    cd_target=CountdownTargetPlatform(3490,BASE_Y-60,PW_SAFE,PH,owner=cd_pad)
    cd_pad.target=cd_target; add(cd_target)

    cp_e=SectionCheckpoint(
        trigger_x=9999999, spawn_x=3500, spawn_y=BASE_Y-100,
        float_y=BASE_Y-150, label="E")
    cd_target.section_cp=cp_e
    section_checkpoints.append(cp_e)
    npcs.append(NPC(3510, BASE_Y-60, "cp_e", "Snow Miser")) # CP-E dialogue

    # ── OBSTACLE 2: ZIGZAG FLOATING LEDGES ───────────────────────────────
    zz_base_x = 3820
    zz_base_y = BASE_Y - 60

    add(Platform(3720, zz_base_y, 90, PH, PINE_GREEN))

    zz_plats, zz_climb, zz_exit = build_zigzag_section(zz_base_x, zz_base_y,
                                                         preset["zigzag_ledge_w"])
    for p in zz_plats: add(p)
    zigzag_section = zz_climb

    section_checkpoints.append(SectionCheckpoint(
        trigger_x = zz_exit.rect.right,
        spawn_x   = zz_exit.rect.x + 10,
        spawn_y   = zz_exit.rect.y - 50,
        float_y   = zz_exit.rect.y - 90,
        label     = "F"))
    # CP-F NPC placed just after the zigzag exit
    npcs.append(NPC(zz_exit.rect.right + 30, zz_exit.rect.y, "cp_f", "Snow Miser"))

    # ── OBSTACLE 3: TRAM + SANTA SLEIGH ──────────────────────────────────
    bridge_x = zz_exit.rect.right + 60
    bridge_y = zz_exit.rect.y
    add(Platform(bridge_x, bridge_y, 160, PH, PINE_GREEN))

    tram_x = bridge_x + 200
    tram_y = bridge_y

    SANTA_TRIGGER_DIST = 400
    TRAM_VANISH_DIST   = preset["tram_vanish"]
    PORTAL_DIST        = 1300

    portal_x = tram_x + PORTAL_DIST
    portal_y = tram_y - 80

    vanish_x = tram_x + TRAM_VANISH_DIST

    tram = TramPlatform(tram_x, tram_y, 180, PH,
                        speed=preset["tram_speed"], vanish_x=vanish_x)
    add(tram); tram_platform=tram

    santa = SantaSleigh(
        portal_x      = portal_x,
        portal_y      = portal_y,
        tram          = tram,
        rope_len      = preset["rope_len"],
        rope_grab_r   = preset["rope_grab_r"],
        hover_timeout = preset["santa_timeout"],
        kidnap_dist   = preset["kidnap_dist"],
    )
    santa_sleigh=santa
    tram.santa_trigger_dist = SANTA_TRIGGER_DIST

    portal_plat_x = portal_x - 220
    add(Platform(portal_plat_x, tram_y, PW_SAFE + 200, PH, PINE_GREEN))
    portal=Portal(portal_x, portal_y)

    return dict(
        platforms=platforms,
        shrink_platforms=shrink_platforms,
        fall_platforms=fall_platforms,
        phantom_platforms=phantom_platforms,
        countdown_platforms=countdown_platforms,
        countdown_platform_ref=countdown_platform_ref,
        zigzag_section=zigzag_section,
        tram_platform=tram_platform,
        santa_sleigh=santa_sleigh,
        spikes=spikes, balloon=balloon,
        portal=portal,
        section_checkpoints=section_checkpoints,
        npcs=npcs,          # ← returned
    )

# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    DIFF_OPTIONS=["easy","medium","hard"]
    DIFF_COLORS={"easy":(80,200,80),"medium":(255,200,50),"hard":(220,60,60)}

    def __init__(self):
        self.screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption("Glitch Claus - The Second Realm")
        self.clock=pygame.time.Clock()
        self.font      =pygame.font.SysFont("consolas",24)
        self.small_font=pygame.font.SysFont("consolas",16)
        self.big_font  =pygame.font.SysFont("consolas",48)
        self.tiny_font =pygame.font.SysFont("consolas",12,bold=True)
        self.cp_font   =pygame.font.SysFont("consolas",11,bold=True)
        self.sfx=SoundManager()
        self.diff_index=1; self.difficulty=self.DIFF_OPTIONS[1]
        self.state="playing"; self.settings_cursor=0
        self.music_volume=0.5; self.music_muted=False
        self.tick=0; self.level_time=0; self.win_timer=0
        self.camera=Camera(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.particles=[]; self.rings=[]; self.flashes=[]
        self.snowflakes=[Snowflake() for _ in range(80)]
        # Story
        self.dialogue_box  = None
        self.pending_state = None
        # Soul death/respawn animation
        self.soul_state=None; self.soul_x=0; self.soul_y=0
        self.soul_target_y=0; self.soul_timer=0; self.soul_trail=[]
        self.soul_pan_target_x=0; self.soul_pan_target_y=0
        self.respawn_fade=0
        self._load_level()
        self.sfx.start_music(volume=self.music_volume)

    def _load_level(self):
        preset=DIFFICULTY_PRESETS[self.difficulty]
        d=create_christmas_level(preset)
        self.platforms              =d["platforms"]
        self.shrink_platforms       =d["shrink_platforms"]
        self.fall_platforms         =d["fall_platforms"]
        self.phantom_platforms      =d["phantom_platforms"]
        self.countdown_platforms    =d["countdown_platforms"]
        self.countdown_platform_ref =d["countdown_platform_ref"]
        self.zigzag_section         =d["zigzag_section"]
        self.tram_platform          =d["tram_platform"]
        self.santa_sleigh           =d["santa_sleigh"]
        self.spikes                 =d["spikes"]
        self.balloon                =d["balloon"]
        self.portal                 =d["portal"]
        self.section_checkpoints    =d["section_checkpoints"]
        self.npcs                   =d["npcs"]          # ← NEW
        self.player=Player(80,BASE_Y-60,
                           move_speed=preset["player_speed"],
                           jump_velocity=preset["player_jump"])
        self.camera=Camera(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.particles.clear(); self.rings.clear(); self.flashes.clear()
        self.level_time=0; self.tick=0; self.win_timer=0
        self._tram_started=False
        self.dialogue_box  = None
        self.pending_state = None
        self.soul_state=None; self.soul_trail=[]
        self.respawn_fade=0

    def _apply_volume(self):
        pygame.mixer.music.set_volume(0.0 if self.music_muted else self.music_volume)

    def _exit_to_menu(self):
        self.sfx.stop_music(); self.running=False

    def start_dialogue(self, key, return_state="playing"):
        """Start a story dialogue by key, pausing the game."""
        if key in STORY_DIALOGUES:
            self.dialogue_box  = DialogueBox(STORY_DIALOGUES[key])
            self.pending_state = return_state
            self.state         = "dialogue"
            self.sfx.play("npc_talk")

    def run(self):
        self.running=True
        while self.running:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: self._exit_to_menu(); return
                if ev.type==pygame.KEYDOWN: self._handle_key(ev.key)
            if not self.running: return
            if self.state=="playing" and self.soul_state is not None:
                self._update_soul(); self.tick += 1
            elif self.state=="playing":   self._update()
            elif self.state=="dialogue":
                if self.dialogue_box: self.dialogue_box.update()
                for sf in self.snowflakes: sf.update()
                self.tick += 1
            elif self.state=="win":     self.win_timer+=1
            self._draw()
            self.clock.tick(FPS)

    def _handle_key(self, key):
        # ── Dialogue state ────────────────────────────────────────────────
        if self.state == "dialogue":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                if self.dialogue_box:
                    self.dialogue_box.advance()
                    if not self.dialogue_box.active:
                        self.dialogue_box = None
                        self.state = self.pending_state or "playing"
            return

        # ── Settings state ────────────────────────────────────────────────
        if self.state=="settings":
            if key==pygame.K_ESCAPE: self.state="playing"; return
            nr=5
            if key in (pygame.K_UP,pygame.K_w):    self.settings_cursor=(self.settings_cursor-1)%nr
            elif key in (pygame.K_DOWN,pygame.K_s): self.settings_cursor=(self.settings_cursor+1)%nr
            elif self.settings_cursor==0:
                changed = False
                if key in (pygame.K_LEFT,pygame.K_a):
                    self.diff_index=(self.diff_index-1)%3
                    self.difficulty=self.DIFF_OPTIONS[self.diff_index]; changed=True
                elif key in (pygame.K_RIGHT,pygame.K_d,pygame.K_RETURN,pygame.K_SPACE):
                    self.diff_index=(self.diff_index+1)%3
                    self.difficulty=self.DIFF_OPTIONS[self.diff_index]; changed=True
                if changed: self._load_level()
            elif self.settings_cursor==1:
                if key in (pygame.K_LEFT,pygame.K_a):    self.music_volume=max(0.0,round(self.music_volume-0.1,1)); self._apply_volume()
                elif key in (pygame.K_RIGHT,pygame.K_d): self.music_volume=min(1.0,round(self.music_volume+0.1,1)); self._apply_volume()
            elif self.settings_cursor==2:
                if key in (pygame.K_RETURN,pygame.K_SPACE): self.music_muted=not self.music_muted; self._apply_volume()
            elif self.settings_cursor==3:
                if key in (pygame.K_RETURN,pygame.K_SPACE): self.state="playing"
            elif self.settings_cursor==4:
                if key in (pygame.K_RETURN,pygame.K_SPACE): self._exit_to_menu()
            return

        # ── Win state ─────────────────────────────────────────────────────
        if self.state=="win":
            if key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_ESCAPE): self._exit_to_menu()
            return

        # ── Playing state ─────────────────────────────────────────────────
        if key==pygame.K_ESCAPE:
            self.state="settings"; self.settings_cursor=3
        elif key==pygame.K_r:
            self._load_level()
        elif key==pygame.K_e:
            # Talk to nearest untouched NPC
            for npc in self.npcs:
                if npc.check_proximity(self.player) and not npc.talked:
                    npc.talked = True
                    self.start_dialogue(npc.dialogue_key)
                    break

    def _update(self):
        self.tick+=1; self.level_time+=1
        keys=pygame.key.get_pressed()

        for p in self.platforms: p.update()

        # NPC proximity display
        for npc in self.npcs:
            npc.proximity_shown = npc.check_proximity(self.player)

        was_alive=self.player.alive
        result=self.player.update(keys,self.platforms)
        if result=="jump": self.sfx.play("jump")

        # On death: reset countdown/tram/sleigh
        if was_alive and not self.player.alive:
            if self.countdown_platform_ref:
                self.countdown_platform_ref.reset()
            if self.tram_platform:
                self.tram_platform.reset()
            if self.santa_sleigh:
                self.santa_sleigh.reset()
            self._tram_started = False

        # Tram + sleigh
        if self.tram_platform and self.tram_platform.moving and not self._tram_started:
            tram_travelled = self.tram_platform.rect.x - self.tram_platform.origin_x
            trigger = getattr(self.tram_platform, "santa_trigger_dist", 200)
            if tram_travelled >= trigger:
                self._tram_started = True
                if self.santa_sleigh:
                    self.santa_sleigh.start(self.tram_platform.rect)
        if self.santa_sleigh and self.santa_sleigh.state != "waiting":
            sleigh_result = self.santa_sleigh.update(self.player)
            if sleigh_result == "kill_player" and self.player.alive:
                self._death_fx(); self.player.die(); self.sfx.play("death")
        if (self.tram_platform and self.tram_platform.gone
                and self.player.alive
                and self.santa_sleigh
                and not self.santa_sleigh.player_grabbed
                and self.player.riding_platform is self.tram_platform):
            self._death_fx(); self.player.die(); self.sfx.play("death")

        # Section checkpoints
        for sc in self.section_checkpoints:
            was_active=sc.activated
            sc.update()
            just_activated=sc.check(self.player) or (sc.activated and not was_active)
            if just_activated:
                self.sfx.play("checkpoint")
                fx_x=(self.player.rect.centerx if sc.trigger_x>100000 else sc.trigger_x)
                self._checkpoint_fx_at(fx_x, sc.float_y)

        if self.player.alive: self.camera.update(self.player.rect)

        for sp in self.spikes:
            if sp.check_kill(self.player):
                self._death_fx(); self.player.die(); self.sfx.play("death")

        self.balloon.update()
        if self.balloon.check_grab(self.player):
            self._balloon_fx()
            self.sfx.play("balloon"); self.sfx.play("balloon_pop")

        self.portal.update()
        if self.player.alive and self.portal.check(self.player):
            self.state="win"; self.win_timer=0
            self.sfx.play("win"); self.sfx.stop_music()

        # Trigger soul rise when death animation finishes (or immediately if fell off screen)
        if not self.player.alive and self.soul_state is None:
            death_ready = getattr(self.player, '_spr_death_done', False)
            fell_off = self.player.rect.top > SCREEN_HEIGHT
            if death_ready or fell_off:
                self.player.respawn_timer = 9999
                self.soul_x = float(self.player.rect.centerx)
                self.soul_y = float(min(self.player.rect.centery, SCREEN_HEIGHT - 50))
                self.soul_target_y = self.soul_y - 140
                self.soul_timer = 0; self.soul_trail = []
                self.soul_state = "rising"; self.sfx.play("soul_rise")

        self.particles=[p for p in self.particles if p.update()]
        self.rings    =[r for r in self.rings     if r.update()]
        self.flashes  =[f for f in self.flashes   if f.update()]
        for sf in self.snowflakes: sf.update()
        self._spawn_ambient()

    def _death_fx(self):
        cx,cy=self.player.rect.centerx,self.player.rect.centery
        self.camera.add_shake(12); self.flashes.append(FlashOverlay(RED,18,110))
        for _ in range(30):
            a=random.uniform(0,math.pi*2); s=random.uniform(2,6)
            self.particles.append(Particle(cx,cy,random.choice([SNOW_WHITE,ICE_BLUE,CANDY_RED]),
                                           math.cos(a)*s,math.sin(a)*s,random.randint(20,45),random.randint(3,6),0.18))

    def _balloon_fx(self):
        cx,cy=self.balloon.rect.centerx,self.balloon.rect.centery
        self.camera.add_shake(8); self.flashes.append(FlashOverlay(GOLD,12,90))
        self.rings.append(RingEffect(cx,cy,BALLOON_PINK,70,5,3))
        for _ in range(25):
            a=random.uniform(0,math.pi*2); s=random.uniform(1,5)
            self.particles.append(Particle(cx,cy,random.choice([BALLOON_RED,BALLOON_PINK,GOLD,WHITE]),
                                           math.cos(a)*s,math.sin(a)*s,random.randint(20,40),random.randint(2,5),0.05))

    def _checkpoint_fx_at(self,wx,wy):
        self.rings.append(RingEffect(wx,wy,CP_GLOW,55,4,3))
        self.flashes.append(FlashOverlay(CP_ACTIVE,10,60))
        for _ in range(18):
            a=random.uniform(0,math.pi*2); s=random.uniform(1,4)
            self.particles.append(Particle(wx,wy,random.choice([CP_ACTIVE,CP_GLOW,WHITE,GOLD]),
                                           math.cos(a)*s,math.sin(a)*s,random.randint(20,40),random.randint(2,5),0.06))

    def _spawn_ambient(self):
        for p in self.phantom_platforms:
            if not p.gone and random.random()<0.15:
                self.particles.append(Particle(p.rect.x+random.randint(0,p.rect.width),
                    p.rect.y,PHANTOM_TEAL,random.uniform(-0.5,0.5),random.uniform(-1.5,-0.3),20,3,0.0))
        for p in self.shrink_platforms:
            if p.shrinking and not p.gone and random.random()<0.2:
                self.particles.append(Particle(
                    p.rect.x+random.randint(0,max(1,p.rect.width)),
                    p.rect.y+random.randint(0,p.rect.height),
                    ICE_BLUE,random.uniform(-1,1),random.uniform(-1.5,0),15,2,0.0))

    # ── Drawing ───────────────────────────────────────────────────────────
    def _update_soul(self):
        self.soul_timer += 1
        # Sparkle particles around the soul (skip during panning)
        if self.soul_state != "panning":
            for _ in range(random.randint(2, 3)):
                a = random.uniform(0, math.pi*2); d = random.uniform(8, 20)
                sx = self.soul_x + math.cos(a)*d; sy = self.soul_y + math.sin(a)*d
                self.particles.append(Particle(sx, sy, (255, 210, 80),
                    random.uniform(-0.5, 0.5), random.uniform(-1, 0),
                    random.randint(12, 20), random.randint(1, 3), 0.02, fade=True))
        if self.soul_state == "rising":
            t = min(1.0, self.soul_timer / 40)
            ease = t * t * (3 - 2 * t)
            self.soul_y = self.player.rect.centery - ease * 140
            self.soul_x = self.player.rect.centerx + math.sin(self.soul_timer * 0.15) * 12
            self.soul_trail.append((self.soul_x, self.soul_y, 255))
            if len(self.soul_trail) > 20: self.soul_trail.pop(0)
            self.soul_trail = [(x, y, a-10) for x, y, a in self.soul_trail if a > 10]
            if self.soul_timer >= 40:
                self.soul_state = "panning"; self.soul_timer = 0; self.soul_trail = []
                self.soul_pan_target_x = self.player.spawn_x + Player.WIDTH // 2 - self.camera.width // 3
                self.soul_pan_target_y = self.player.spawn_y + Player.HEIGHT // 2 - self.camera.height // 2
        elif self.soul_state == "panning":
            dx = self.soul_pan_target_x - self.camera.offset_x
            dy = self.soul_pan_target_y - self.camera.offset_y
            self.camera.offset_x += dx * 0.12
            self.camera.offset_y += dy * 0.08
            if self.soul_timer >= 20 and abs(dx) < 8 and abs(dy) < 8:
                self.soul_state = "falling"; self.soul_timer = 0
                self.soul_x = float(self.player.spawn_x + Player.WIDTH // 2)
                self.soul_y = self.camera.offset_y - 60
                self.soul_target_y = float(self.player.spawn_y + Player.HEIGHT // 2)
                self.soul_trail = []; self.sfx.play("soul_land")
        elif self.soul_state == "falling":
            t = min(1.0, self.soul_timer / 35)
            ease = t * t * (3 - 2 * t)
            self.soul_y = -50 + (self.soul_target_y + 50) * ease
            self.soul_x = (self.player.spawn_x + Player.WIDTH // 2) + math.sin(t * math.pi) * 30
            self.soul_trail.append((self.soul_x, self.soul_y, 255))
            if len(self.soul_trail) > 20: self.soul_trail.pop(0)
            self.soul_trail = [(x, y, a-10) for x, y, a in self.soul_trail if a > 10]
            if self.soul_timer >= 35:
                self.player.respawn_timer = 0; self.player.respawn()
                self.sfx.play("soul_land"); self.sfx.play("respawn")
                self.respawn_fade = 20
                self.flashes.append(FlashOverlay(WHITE, 12, 160))
                for _ in range(25):
                    a = random.uniform(0, math.pi*2); s = random.uniform(2, 7)
                    self.particles.append(Particle(self.soul_x, self.soul_target_y,
                        random.choice([WHITE, SNOW_WHITE, ICE_BLUE, XMAS_GOLD]),
                        math.cos(a)*s, math.sin(a)*s, 30, random.randint(3, 7), 0.1))
                self.rings.append(RingEffect(int(self.soul_x), int(self.soul_target_y), WHITE, 100, 6, 3))
                self.soul_state = None; self.soul_trail = []
                self.camera.update(self.player.rect)
        self.particles = [p for p in self.particles if p.update()]
        self.rings = [r for r in self.rings if r.update()]
        self.flashes = [f for f in self.flashes if f.update()]

    def _draw_soul(self):
        if self.soul_state is None: return
        # Pulsing dark overlay (same as level4)
        dim_alpha = int(80 + 20 * math.sin(self.soul_timer * 0.12))
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, dim_alpha))
        self.screen.blit(dim, (0, 0))
        # During panning, only show the dark overlay — no soul orb
        if self.soul_state == "panning": return
        sp = self.camera.apply(pygame.Rect(int(self.soul_x), int(self.soul_y), 1, 1))
        # Soul trail — fading circles
        for i, (sx, sy, sa) in enumerate(self.soul_trail):
            tp = self.camera.apply(pygame.Rect(int(sx), int(sy), 1, 1))
            frac = (i + 1) / max(1, len(self.soul_trail))
            r = max(2, int(10 * frac))
            al = max(0, min(255, int(sa * 0.4 * frac)))
            ts = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (255, 255, 255, al), (r, r), r)
            self.screen.blit(ts, (tp.x - r, tp.y - r))
        # Outer glow
        for gr, ga in [(40, 40), (28, 80), (18, 160)]:
            gs = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (255, 255, 255, ga), (gr, gr), gr)
            self.screen.blit(gs, (sp.x - gr, sp.y - gr))
        # Core white orb
        pygame.draw.circle(self.screen, WHITE, (sp.x, sp.y), 8)
        pygame.draw.circle(self.screen, (240, 250, 255), (sp.x - 1, sp.y - 1), 4)

    def _draw(self):
        self.screen.fill(DARK_BG)
        if self.state in ("playing","settings","dialogue"):
            self._draw_game()
        if self.state=="settings":
            self._draw_settings()
        elif self.state=="dialogue":
            # Dim the game world during dialogue
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 80))
            self.screen.blit(dim, (0, 0))
            if self.dialogue_box:
                self.dialogue_box.draw(self.screen, self.tick)
        elif self.state=="win":
            self._draw_win()
        if self.respawn_fade > 0:
            a = int(255*(1.0-abs(self.respawn_fade-10)/10.0))
            if a > 0:
                ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)); ov.fill(BLACK)
                ov.set_alpha(min(255,a)); self.screen.blit(ov,(0,0))
            self.respawn_fade -= 1
        pygame.display.flip()

    def _draw_background(self):
        sky_top    = (8,  20,  55)
        sky_mid    = (20, 45,  90)
        sky_horz   = (50, 70, 110)
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            if t < 0.6:
                c = lerp_color(sky_top, sky_mid, t / 0.6)
            else:
                c = lerp_color(sky_mid, sky_horz, (t - 0.6) / 0.4)
            pygame.draw.line(self.screen, c, (0, y), (SCREEN_WIDTH, y))

        ox_slow = int(self.camera.offset_x * 0.05) % SCREEN_WIDTH
        for i in range(80):
            sx = (i * 173 + ox_slow) % SCREEN_WIDTH
            sy = (i * 97)  % int(SCREEN_HEIGHT * 0.65)
            brightness = 160 + int(50 * math.sin(self.tick * 0.03 + i))
            r = 1 if i % 3 else 2
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (sx, sy), r)

        ox_far = int(self.camera.offset_x * 0.08) % SCREEN_WIDTH
        far_col = (30, 50, 80)
        far_pts = [(0, SCREEN_HEIGHT)]
        for i in range(9):
            px = int(SCREEN_WIDTH * i / 8)
            heights = [380, 280, 340, 220, 300, 260, 360, 310, 380]
            py = heights[i]
            far_pts.append(((px - ox_far) % SCREEN_WIDTH, py))
        far_pts.append((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.draw.polygon(self.screen, far_col, far_pts)
        for i in range(1, len(far_pts) - 1):
            px, py = far_pts[i]
            if py < 310:
                cap = [(px-18, py+20), (px, py-5), (px+18, py+20)]
                pygame.draw.polygon(self.screen, (200, 215, 235), cap)

        ox_near = int(self.camera.offset_x * 0.18) % SCREEN_WIDTH
        near_col = (15, 28, 52)
        near_pts = [(0, SCREEN_HEIGHT)]
        for i in range(7):
            px = int(SCREEN_WIDTH * i / 6)
            heights = [SCREEN_HEIGHT, 360, 250, 420, 180, 310, SCREEN_HEIGHT]
            py = heights[i]
            near_pts.append(((px - ox_near) % SCREEN_WIDTH, py))
        near_pts.append((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.draw.polygon(self.screen, near_col, near_pts)
        for i in range(1, len(near_pts) - 1):
            px, py = near_pts[i]
            if py < 300:
                cap = [(px-25, py+30), (px, py-10), (px+25, py+30)]
                pygame.draw.polygon(self.screen, (225, 235, 255), cap)

        pygame.draw.rect(self.screen, (200, 215, 235),
                         (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 30))

    def _draw_game(self):
        self._draw_background()
        for sf in self.snowflakes: sf.draw(self.screen)
        for p in self.platforms:   p.draw(self.screen,self.camera)
        for sc in self.section_checkpoints: sc.draw_flag(self.screen,self.camera,self.cp_font)
        for sp in self.spikes:     sp.draw(self.screen,self.camera)
        self.balloon.draw(self.screen,self.camera,self.tick)
        self.portal.draw(self.screen,self.camera)
        if self.santa_sleigh:      self.santa_sleigh.draw(self.screen,self.camera)
        for p in self.particles:   p.draw(self.screen,self.camera)
        for r in self.rings:       r.draw(self.screen,self.camera)
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(self.screen, self.camera, self.tick)
        self.player.draw(self.screen,self.camera,self.tick)
        for f in self.flashes:     f.draw(self.screen)

        # Zigzag progress hint
        if self.zigzag_section and not self.zigzag_section.unlocked:
            if self.zigzag_section.started:
                hs=self.small_font.render(self.zigzag_section.progress_text(),True,CYAN)
                self.screen.blit(hs,(SCREEN_WIDTH//2-hs.get_width()//2,SCREEN_HEIGHT-50))

        # HUD
        self.screen.blit(self.small_font.render(f"Time: {self.level_time/FPS:.1f}s",True,SNOW_WHITE),
                         (SCREEN_WIDTH-165,12))
        total_sc=len(self.section_checkpoints)
        reached_sc=sum(1 for sc in self.section_checkpoints if sc.activated)
        cp_col=CP_ACTIVE if reached_sc==total_sc else SNOW_WHITE
        self.screen.blit(self.small_font.render(f"CP  {reached_sc}/{total_sc}",True,cp_col),
                         (SCREEN_WIDTH-165,34))
        dc=self.DIFF_COLORS[self.difficulty]
        ds=self.small_font.render(f"[ {self.difficulty.upper()} ]",True,dc)
        self.screen.blit(ds,(SCREEN_WIDTH//2-ds.get_width()//2,10))
        legend=[
            (ICE_BLUE,     "Ice - shrinks"),
            (FALLING_BROWN,"Wood - falls"),
            (SPIKE_GRAY,   "Spikes - death"),
            (BALLOON_RED,  "Balloon - fly"),
            (PHANTOM_TEAL, "Teal - phantom"),
            (COUNTDOWN_COL,"Blue - wait GO"),
            (LEDGE_L_COL,  "Blue ledge - left"),
            (LEDGE_R_COL,  "Gold ledge - right"),
            (MOVING_COL,   "Gold tram - jump!"),
            (CP_ACTIVE,    "Flag - checkpoint"),
        ]
        for li,(col,txt) in enumerate(legend):
            pygame.draw.rect(self.screen,col,(12,12+li*17,10,10))
            self.screen.blit(self.tiny_font.render(txt,True,(160,180,200)),(26,10+li*17))
        self.screen.blit(self.tiny_font.render(
            "SPACE/W-Jump  A/D-Move  E-Talk  R-Restart  ESC-Settings",True,(80,100,120)),
            (10,SCREEN_HEIGHT-20))
        if self.soul_state is not None:
            self._draw_soul()
        elif not self.player.alive:
            t=self.font.render("Respawning...",True,RED)
            self.screen.blit(t,t.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)))

    def _draw_settings(self):
        ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)); ov.fill(BLACK); ov.set_alpha(170)
        self.screen.blit(ov,(0,0))
        tit=self.font.render("SETTINGS",True,CYAN)
        self.screen.blit(tit,tit.get_rect(center=(SCREEN_WIDTH//2,130)))
        dc=self.DIFF_COLORS[self.difficulty]
        desc={"easy":"Slow shrink | long warning | generous balloon",
              "medium":"Balanced experience",
              "hard":"Fast shrink | instant drop | blink phantom"}
        ds=self.tiny_font.render(desc[self.difficulty],True,dc)
        self.screen.blit(ds,ds.get_rect(center=(SCREEN_WIDTH//2,168)))
        items=[(f"Difficulty :  < {self.difficulty.upper()} >","Left/Right — restarts level instantly"),
               (f"Music Volume :  < {int(self.music_volume*100)}% >","Left/Right"),
               (f"Mute Music :  {'OFF' if self.music_muted else 'ON'}","Enter to toggle"),
               ("Resume","Enter or ESC"),("Exit to Menu","Enter")]
        for i,(label,hint) in enumerate(items):
            y=205+i*58; sel=(i==self.settings_cursor)
            if sel:
                bar=pygame.Rect(SCREEN_WIDTH//2-240,y-4,480,30)
                pygame.draw.rect(self.screen,(30,40,60),bar)
                pygame.draw.rect(self.screen,CYAN,bar,1)
                self.screen.blit(self.small_font.render(">",True,CYAN),(SCREEN_WIDTH//2-228,y))
            rc=(dc if(i==0 and sel) else lerp_color(dc,GRAY,0.5) if i==0
                else WHITE if sel else GRAY)
            self.screen.blit(self.small_font.render(label,True,rc),(SCREEN_WIDTH//2-200,y))
            if sel: self.screen.blit(self.tiny_font.render(hint,True,(100,120,140)),(SCREEN_WIDTH//2-200,y+22))
        bx=SCREEN_WIDTH//2-100; by=205+58+33
        pygame.draw.rect(self.screen,DARK_GRAY,(bx,by,200,6))
        pygame.draw.rect(self.screen,RED if self.music_muted else CYAN,(bx,by,int(200*self.music_volume),6))
        pygame.draw.rect(self.screen,WHITE,(bx,by,200,6),1)
        ft=self.tiny_font.render("ESC to resume",True,(80,80,100))
        self.screen.blit(ft,(SCREEN_WIDTH//2-ft.get_width()//2,SCREEN_HEIGHT-30))

    def _draw_win(self):
        self._draw_background()
        for sf in self.snowflakes: sf.draw(self.screen)
        t=self.big_font.render("SECOND REALM CLEARED!",True,GOLD)
        self.screen.blit(t,t.get_rect(center=(SCREEN_WIDTH//2,140)))
        sm=self.font.render("Snow Miser tips his hat... reluctantly.",True,ICE_BLUE)
        self.screen.blit(sm,sm.get_rect(center=(SCREEN_WIDTH//2,205)))
        for lbl,col,y in [
            ("You escaped the Second Realm!",ICE_BLUE,265),
            (f"Time: {self.level_time/FPS:.1f} seconds",YELLOW,315),
            (f"Checkpoints: {sum(1 for sc in self.section_checkpoints if sc.activated)}/{len(self.section_checkpoints)}",CP_ACTIVE,365),
            (f"Difficulty: {self.difficulty.upper()}",self.DIFF_COLORS[self.difficulty],415),
        ]:
            t2=self.font.render(lbl,True,col)
            self.screen.blit(t2,t2.get_rect(center=(SCREEN_WIDTH//2,y)))
        h=self.small_font.render("Press ENTER or ESC to exit",True,WHITE)
        self.screen.blit(h,h.get_rect(center=(SCREEN_WIDTH//2,480)))

    # expose zigzag_section for HUD
    @property
    def zigzag_section(self):
        return self._zigzag_section if hasattr(self, '_zigzag_section') else None

    def _load_level(self):
        preset=DIFFICULTY_PRESETS[self.difficulty]
        d=create_christmas_level(preset)
        self.platforms              =d["platforms"]
        self.shrink_platforms       =d["shrink_platforms"]
        self.fall_platforms         =d["fall_platforms"]
        self.phantom_platforms      =d["phantom_platforms"]
        self.countdown_platforms    =d["countdown_platforms"]
        self.countdown_platform_ref =d["countdown_platform_ref"]
        self._zigzag_section        =d["zigzag_section"]
        self.tram_platform          =d["tram_platform"]
        self.santa_sleigh           =d["santa_sleigh"]
        self.spikes                 =d["spikes"]
        self.balloon                =d["balloon"]
        self.portal                 =d["portal"]
        self.section_checkpoints    =d["section_checkpoints"]
        self.npcs                   =d["npcs"]
        self.player=Player(80,BASE_Y-60,
                           move_speed=preset["player_speed"],
                           jump_velocity=preset["player_jump"])
        self.camera=Camera(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.particles.clear(); self.rings.clear(); self.flashes.clear()
        self.level_time=0; self.tick=0; self.win_timer=0
        self._tram_started=False
        self.dialogue_box  = None
        self.pending_state = None


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------
def launch_game():
    pygame.mixer.music.stop()
    game=Game(); game.run()
    pygame.display.set_caption("Christmas Pixel Adventure")
    try: pygame.mixer.music.load("assets/audio/backgroundlevel2.mp3"); pygame.mixer.music.play(-1)
    except: pass

if __name__=="__main__":
    pygame.init(); pygame.mixer.init()
    game=Game(); game.run()
    pygame.quit()