import pygame
import math
import random
import os

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

# New obstacle colours
COUNTDOWN_COL  = (60,  120, 200)   # blue-ish "waiting" platform
WALL_COL       = (120, 60,  200)   # purple wall-climb platform
WALL_SIDE_COL  = (90,  40,  160)   # the two bouncing walls
MOVING_COL     = (200, 140, 40)    # moving platform (tram)
SANTA_RED      = (200, 30,  30)
SLEIGH_BROWN   = (180, 100, 40)
SLEIGH_GOLD    = (220, 180, 30)

# Physics
GRAVITY        = 0.6
JUMP_VELOCITY  = -13
MOVE_SPEED     = 5
SPRINT_SPEED   = 8
MAX_FALL_SPEED = 15
DEATH_Y        = 900
BASE_Y         = 420

# ---------------------------------------------------------------------------
# Difficulty presets
# ---------------------------------------------------------------------------
DIFFICULTY_PRESETS = {
    "easy": {
        "shrink_speed":   0.5,
        "fall_delay":     50,
        "phantom_frames": 30,
        "balloon_vx":     10,
        "balloon_vy":     -13,
        "player_speed":   5,
        "player_jump":    -14,
        "countdown_sec":  3,   # seconds before next platform appears
        "wall_bounces":   2,   # how many L/R bounces to unlock
        "tram_speed":     2,   # moving platform speed
    },
    "medium": {
        "shrink_speed":   1.2,
        "fall_delay":     25,
        "phantom_frames": 18,
        "balloon_vx":     9,
        "balloon_vy":     -11,
        "player_speed":   5,
        "player_jump":    -13,
        "countdown_sec":  3,
        "wall_bounces":   2,
        "tram_speed":     3,
    },
    "hard": {
        "shrink_speed":   2.5,
        "fall_delay":     8,
        "phantom_frames": 8,
        "balloon_vx":     8,
        "balloon_vy":     -10,
        "player_speed":   5,
        "player_jump":    -13,
        "countdown_sec":  2,
        "wall_bounces":   3,
        "tram_speed":     4,
    },
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
        self.offset_x += (tr.centerx - self.width//3  - self.offset_x) * 0.1
        oy = tr.centery - self.height//2
        self.offset_y += (oy - self.offset_y) * 0.05
        self.offset_y = max(-200, min(self.offset_y, 200))
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
    def update(self):
        self.r+=self.sp; return self.r<self.mr
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
# Section Checkpoint  (one per obstacle SECTION, not per platform)
# ---------------------------------------------------------------------------
# A SectionCheckpoint has a world X trigger line.
# The first time the player's rect.right passes that X while alive, it activates
# and updates the player's spawn point to the given (spawn_x, spawn_y).
#
class SectionCheckpoint:
    def __init__(self, trigger_x, spawn_x, spawn_y, label=""):
        self.trigger_x   = trigger_x   # world X; activates when player crosses it
        self.spawn_x     = spawn_x
        self.spawn_y     = spawn_y
        self.label       = label
        self.activated   = False
        self.toast_timer = 0
        self.glow_tick   = 0

    def check(self, player):
        """Call every frame. Returns True the frame it first activates."""
        if self.activated or not player.alive:
            return False
        if player.rect.right >= self.trigger_x:
            self.activated   = True
            self.toast_timer = 150
            self.glow_tick   = 0
            player.spawn_x   = self.spawn_x
            player.spawn_y   = self.spawn_y
            return True
        return False

    def update(self):
        if self.toast_timer > 0: self.toast_timer -= 1
        if self.activated:       self.glow_tick   += 1

    def draw_flag(self, surface, camera, font):
        """Draw a flag pole at trigger_x on the ground."""
        wx  = self.trigger_x
        wy  = BASE_Y - 2
        pos = camera.apply(pygame.Rect(wx, wy, 1, 1))
        sx, sy = pos.x, pos.y
        if sx < -60 or sx > SCREEN_WIDTH + 60:
            return
        col  = CP_ACTIVE if self.activated else CP_INACTIVE
        # pole
        pygame.draw.line(surface, GRAY, (sx, sy), (sx, sy-50), 3)
        # flag
        pulse = abs(math.sin(self.glow_tick*0.08)) if self.activated else 0
        fc    = lerp_color(col, WHITE, pulse*0.4)
        pts   = [(sx+1, sy-50),(sx+22, sy-43),(sx+1, sy-36)]
        pygame.draw.polygon(surface, fc, pts)
        # ring glow when active
        if self.activated and self.glow_tick < 60:
            rr = min(40, self.glow_tick*2)
            pygame.draw.circle(surface, CP_GLOW, (sx, sy-43), rr, 2)
        # toast
        if self.toast_timer > 0:
            alpha = min(255, self.toast_timer*4)
            rise  = (150-self.toast_timer)//4
            ts    = font.render(f"CHECKPOINT  {self.label}", True, CP_ACTIVE)
            ts.set_alpha(alpha)
            surface.blit(ts, (sx-ts.get_width()//2, sy-80-rise))

# ---------------------------------------------------------------------------
# Base Platform
# ---------------------------------------------------------------------------
class Platform:
    def __init__(self, x, y, w, h, color=GRAY):
        self.rect  = pygame.Rect(x,y,w,h)
        self.color = color
        self.checkpoint = None   # SectionCheckpoint reference (unused at platform level)

    def is_active(self):              return True
    def get_rect(self):               return self.rect
    def on_player_land(self, player): pass
    def update(self):                 pass

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        pygame.draw.rect(surface, self.color, sr)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x,sr.y,sr.width,5))

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
        if self.shrinking and ratio<0.35 and self.flicker%4<2:
            bc=lerp_color(ICE_BLUE,RED,1-ratio)
        else:
            bc=lerp_color(ICE_DARK,ICE_BLUE,ratio)
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
        ar=self.vt/self.VF if self.touched else 0.55+0.25*abs(math.sin(self.tick*0.07))
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
# Player lands → 3-2-1 countdown shown on screen.
# The NEXT platform is hidden until countdown hits 0.
# If the player jumps before "0 / GO", the next platform hasn't appeared yet
# so they fall into the void.
#
class CountdownPlatform(Platform):
    """
    Landing platform that runs a countdown before revealing the target platform.
    `target` must be set after construction to point to the next Platform object.
    """
    def __init__(self, x, y, w, h, countdown_frames=180):
        super().__init__(x, y, w, h, COUNTDOWN_COL)
        self.countdown_frames = countdown_frames   # total frames for full count
        self.countdown        = 0     # current countdown tick (0 = not started)
        self.running          = False
        self.done             = False  # once done, target is visible permanently
        self.target           = None   # Platform to reveal on GO
        self.tick             = 0

    def on_player_land(self, player):
        if not self.running and not self.done:
            self.running   = True
            self.countdown = self.countdown_frames

    def is_active(self): return True

    def update(self):
        self.tick += 1
        if self.running and not self.done:
            self.countdown -= 1
            if self.countdown <= 0:
                self.running = False
                self.done    = True

    def target_visible(self):
        """True when the next platform should collide with the player."""
        return self.done

    def current_number(self):
        """Returns 3/2/1/0 based on countdown progress."""
        if not self.running and not self.done:
            return None
        total = self.countdown_frames
        t     = self.countdown
        if self.done:
            return 0
        segment = total // 3
        if t > segment * 2:   return 3
        elif t > segment:     return 2
        else:                 return 1

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
            return
        # Colour pulses between blue and white while counting
        pulse = abs(math.sin(self.tick * 0.15))
        if self.running:
            col = lerp_color(COUNTDOWN_COL, WHITE, pulse * 0.4)
        elif self.done:
            col = PINE_GREEN
        else:
            col = COUNTDOWN_COL
        pygame.draw.rect(surface, col, sr)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x, sr.y, sr.width, 5))
        # Countdown number above platform
        n = self.current_number()
        if n is not None:
            f    = pygame.font.SysFont("consolas", 48, bold=True)
            txt  = f.render("GO!" if n == 0 else str(n), True,
                            GOLD if n == 0 else lerp_color(RED, YELLOW, pulse))
            surface.blit(txt, (sr.centerx - txt.get_width()//2, sr.y - 60))


class CountdownTargetPlatform(Platform):
    """
    The platform that only becomes solid after the countdown finishes.
    Linked back to its CountdownPlatform via `owner`.
    """
    def __init__(self, x, y, w, h, owner):
        super().__init__(x, y, w, h, PINE_GREEN)
        self.owner = owner

    def is_active(self):
        return self.owner.target_visible()

    def draw(self, surface, camera):
        if not self.is_active():
            # Draw as a faint ghost so player can see it's coming
            sr = camera.apply(self.rect)
            if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
                return
            ghost = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
            ghost.fill((COUNTDOWN_COL[0], COUNTDOWN_COL[1], COUNTDOWN_COL[2], 50))
            surface.blit(ghost, (sr.x, sr.y))
            return
        super().draw(surface, camera)

# ---------------------------------------------------------------------------
# OBSTACLE 2 — Wall-Climb Platform
# ---------------------------------------------------------------------------
# Two walls flank the platform. Player must hit RIGHT wall then LEFT wall
# (or vice-versa based on required_sequence) N times to unlock the exit.
# A prompt on screen shows the required direction. Wrong order resets progress.
#
WALL_SEQUENCE = ["RIGHT", "LEFT"]   # one full cycle = 1 bounce

class WallClimbPlatform(Platform):
    """
    Landing pad between two walls. Hitting walls in the correct L→R sequence
    N times unlocks the exit platform.
    """
    def __init__(self, x, y, w, h, required_bounces=2):
        super().__init__(x, y, w, h, WALL_COL)
        self.required_bounces = required_bounces
        self.step             = 0      # index into WALL_SEQUENCE * required_bounces
        self.total_steps      = required_bounces * len(WALL_SEQUENCE)
        self.unlocked         = False
        self.active_player    = False  # True after player first lands here
        self.flash_tick       = 0

    def on_player_land(self, player):
        self.active_player = True

    def register_wall_hit(self, side):
        """
        Call with side="RIGHT" or side="LEFT" when player touches a wall.
        Returns True if the whole sequence is now complete.
        """
        if self.unlocked or not self.active_player:
            return False
        expected = WALL_SEQUENCE[self.step % len(WALL_SEQUENCE)]
        if side == expected:
            self.step += 1
            self.flash_tick = 10
            if self.step >= self.total_steps:
                self.unlocked = True
                return True
        else:
            # Wrong wall — reset progress
            self.step       = 0
            self.flash_tick = -15   # negative = red flash for wrong hit
        return False

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
            return
        col = PINE_GREEN if self.unlocked else WALL_COL
        if self.flash_tick > 0:
            col = lerp_color(col, WHITE, self.flash_tick / 10)
            self.flash_tick -= 1
        elif self.flash_tick < 0:
            col = lerp_color(col, RED, abs(self.flash_tick) / 15)
            self.flash_tick += 1
        pygame.draw.rect(surface, col, sr)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x, sr.y, sr.width, 5))
        if self.active_player and not self.unlocked:
            # Draw progress dots
            done  = self.step
            total = self.total_steps
            dw    = 10; gap = 5
            ox    = sr.centerx - (total * (dw+gap)) // 2
            for i in range(total):
                dc = GOLD if i < done else DARK_GRAY
                pygame.draw.rect(surface, dc, (ox + i*(dw+gap), sr.y - 16, dw, 8))


class WallSide(Platform):
    """
    One of the two bounce walls that flank WallClimbPlatform.
    Reports collisions to its owner platform.
    """
    def __init__(self, x, y, w, h, side, owner):
        super().__init__(x, y, w, h, WALL_SIDE_COL)
        self.side  = side    # "LEFT" or "RIGHT"
        self.owner = owner
        self.flash = 0

    def on_player_land(self, player):
        pass   # walls don't use the land callback

    def register_hit(self, player):
        """Call from Game._update() when player horizontally collides with this wall."""
        just_finished = self.owner.register_wall_hit(self.side)
        self.flash = 12
        return just_finished

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
            return
        col = lerp_color(WALL_SIDE_COL, WHITE, max(0, self.flash)/12) if self.flash>0 else WALL_SIDE_COL
        if self.flash > 0: self.flash -= 1
        pygame.draw.rect(surface, col, sr)
        # Arrow hint on wall
        f   = pygame.font.SysFont("consolas", 14, bold=True)
        arr = f.render("◄" if self.side=="LEFT" else "►", True, WHITE)
        surface.blit(arr, (sr.centerx - arr.get_width()//2, sr.centery - arr.get_height()//2))


class WallExitPlatform(Platform):
    """Next platform after wall-climb — only solid once the WallClimbPlatform is unlocked."""
    def __init__(self, x, y, w, h, owner):
        super().__init__(x, y, w, h, PINE_GREEN)
        self.owner = owner

    def is_active(self):
        return self.owner.unlocked

    def draw(self, surface, camera):
        if not self.is_active():
            sr = camera.apply(self.rect)
            if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
                return
            ghost = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
            ghost.fill((WALL_COL[0], WALL_COL[1], WALL_COL[2], 50))
            surface.blit(ghost, (sr.x, sr.y))
            return
        super().draw(surface, camera)

# ---------------------------------------------------------------------------
# OBSTACLE 3 — Moving Platform (Tram) + Santa Sleigh
# ---------------------------------------------------------------------------
# Player lands on the tram → it moves rightward.
# After a delay, Santa's sleigh sweeps in from the top-right.
# Player must JUMP onto the sleigh. If they miss, the tram carries them off
# the right edge and they die.
# If they land on the sleigh, it carries them directly to the portal area.
#
class TramPlatform(Platform):
    """
    A platform that starts moving right when the player lands on it.
    """
    def __init__(self, x, y, w, h, speed=3):
        super().__init__(x, y, w, h, MOVING_COL)
        self.speed      = speed
        self.moving     = False
        self.origin_x   = x
        self.dx         = 0   # used by player.update() for riding

    def on_player_land(self, player):
        self.moving = True

    def reset(self):
        self.rect.x = self.origin_x
        self.moving = False

    def update(self):
        if self.moving:
            self.rect.x += self.speed

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
            return
        pygame.draw.rect(surface, MOVING_COL, sr)
        # Rail lines
        for i in range(3):
            lx = sr.x + 15 + i * (sr.width // 3 - 5)
            pygame.draw.line(surface, SLEIGH_GOLD, (lx, sr.y+4), (lx, sr.bottom-4), 2)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x, sr.y, sr.width, 5))
        pygame.draw.rect(surface, SLEIGH_GOLD, sr, 2)
        # "JUMP!" warning once it's been moving a while
        if self.moving:
            f   = pygame.font.SysFont("consolas", 14, bold=True)
            t   = f.render("JUMP!", True, RED)
            surface.blit(t, (sr.centerx - t.get_width()//2, sr.y - 22))


class SantaSleigh:
    """
    Santa's sleigh that swoops in when the tram starts moving.
    - Starts off-screen top-right
    - Flies in diagonally to hover above the tram
    - Player must jump onto it
    - If player lands on sleigh: whisked to portal area (spawn override)
    - If tram goes off-screen with player still on it: player dies
    """
    WIDTH  = 120
    HEIGHT = 30

    def __init__(self, portal_spawn_x, portal_spawn_y, tram):
        self.tram           = tram
        self.portal_spawn_x = portal_spawn_x
        self.portal_spawn_y = portal_spawn_y

        # Start position (off-screen top right)
        self.wx   = float(SCREEN_WIDTH + 300)
        self.wy   = float(-200)
        self.rect = pygame.Rect(int(self.wx), int(self.wy), self.WIDTH, self.HEIGHT)

        self.state   = "waiting"   # waiting / flying_in / hovering / carrying / done
        self.tick    = 0
        self.hover_y = 0.0         # set when tram starts
        self.vx      = 0.0
        self.vy      = 0.0
        self.player_aboard = False

    def start(self, tram_rect):
        """Called the frame the tram starts moving."""
        if self.state != "waiting":
            return
        # Target hover position: above the tram, slightly ahead
        self.hover_y = float(tram_rect.top - 120)
        # Start off-screen top-right in world space
        self.wx      = float(tram_rect.right + 600)
        self.wy      = float(tram_rect.top - 400)
        self.state   = "flying_in"

    def update(self, player):
        self.tick += 1
        tr = self.tram.rect

        if self.state == "flying_in":
            # Fly diagonally toward hover position above tram
            target_x = float(tr.centerx - self.WIDTH//2)
            target_y = float(tr.top - 120)
            self.wx += (target_x - self.wx) * 0.06
            self.wy += (target_y - self.wy) * 0.06
            if abs(self.wx - target_x) < 8 and abs(self.wy - target_y) < 8:
                self.state = "hovering"

        elif self.state == "hovering":
            # Drift with the tram horizontally + gentle bob
            target_x = float(tr.centerx - self.WIDTH//2)
            target_y = float(tr.top - 120) + math.sin(self.tick * 0.06) * 6
            self.wx += (target_x - self.wx) * 0.12
            self.wy += (target_y - self.wy) * 0.10

        elif self.state == "carrying":
            # Fly right and upward toward portal
            self.wx += 4
            self.wy -= 1.5

        self.rect.x = int(self.wx)
        self.rect.y = int(self.wy)

        # Check if player jumped onto sleigh
        if self.state in ("flying_in", "hovering"):
            if (player.alive and not self.player_aboard
                    and player.vel_y >= 0
                    and player.rect.colliderect(self.rect)):
                self.player_aboard = True
                self.state         = "carrying"

        if self.player_aboard and self.state == "carrying":
            # Snap player onto top of sleigh
            player.rect.bottom = self.rect.top
            player.rect.centerx = self.rect.centerx
            player.vel_x = 4
            player.vel_y = 0
            player.on_ground = True
            # When close enough to portal spawn, teleport
            if self.wx > self.portal_spawn_x - 200:
                player.spawn_x    = self.portal_spawn_x
                player.spawn_y    = self.portal_spawn_y
                player.rect.x     = self.portal_spawn_x
                player.rect.y     = self.portal_spawn_y
                self.state        = "done"

    def draw(self, surface, camera):
        if self.state == "waiting" or self.state == "done":
            return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10:
            return

        # Sleigh body
        pygame.draw.rect(surface, SLEIGH_BROWN, sr)
        pygame.draw.rect(surface, SLEIGH_GOLD, sr, 2)

        # Runner curves at bottom
        for side in (sr.x+8, sr.right-18):
            pygame.draw.arc(surface, SLEIGH_GOLD,
                            (side, sr.bottom-4, 10, 8), 0, math.pi, 2)

        # Santa pixel art (tiny: red hat, white beard, red coat) above sleigh
        hx = sr.centerx - 12
        hy = sr.y - 28
        # coat
        pygame.draw.rect(surface, SANTA_RED, (hx, hy+10, 24, 18))
        # belt
        pygame.draw.rect(surface, (50,30,10), (hx, hy+18, 24, 4))
        pygame.draw.rect(surface, SLEIGH_GOLD, (hx+9, hy+17, 6, 6))
        # head
        pygame.draw.rect(surface, (240,200,160), (hx+4, hy, 16, 12))
        # hat
        pygame.draw.rect(surface, SANTA_RED, (hx+4, hy-8, 16, 10))
        pygame.draw.rect(surface, WHITE, (hx+2, hy-1, 20, 4))
        pygame.draw.circle(surface, WHITE, (hx+20, hy-8), 3)
        # beard
        pygame.draw.rect(surface, WHITE, (hx+2, hy+6, 20, 8))

        # "HO HO!" text while hovering
        if self.state == "hovering" and self.tick % 80 < 50:
            f = pygame.font.SysFont("consolas", 12, bold=True)
            t = f.render("HO HO!", True, SANTA_RED)
            surface.blit(t, (sr.centerx - t.get_width()//2, sr.y - 48))

# ---------------------------------------------------------------------------
# Spike Trap
# ---------------------------------------------------------------------------
class SpikeTrap:
    SPIKE_W=14; SPIKE_H=22
    def __init__(self, x, y, count):
        self.x=x; self.y=y; self.count=count
        self.rect=pygame.Rect(x, y-self.SPIKE_H, count*self.SPIKE_W, self.SPIKE_H)
    def check_kill(self, player):
        return player.alive and self.rect.colliderect(player.rect)
    def draw(self, surface, camera):
        for i in range(self.count):
            sx=self.x+i*self.SPIKE_W
            pos=camera.apply(pygame.Rect(sx,self.y-self.SPIKE_H,self.SPIKE_W,self.SPIKE_H))
            tip=(pos.x+pos.width//2,pos.y)
            pygame.draw.polygon(surface,SPIKE_GRAY,[tip,(pos.x,pos.bottom),(pos.right,pos.bottom)])
            pygame.draw.polygon(surface,WHITE,     [tip,(pos.x,pos.bottom),(pos.right,pos.bottom)],1)
            pygame.draw.circle(surface,RED,tip,3)

# ---------------------------------------------------------------------------
# Balloon
# ---------------------------------------------------------------------------
class Balloon:
    RADIUS=14; STRING_LEN=30
    def __init__(self, x, y, launch_vx=9, launch_vy=-11):
        self.x=float(x); self.y=float(y)
        self.launch_vx=launch_vx; self.launch_vy=launch_vy
        self.grabbed=False; self.rc=0; self.tick=0
        self.rect=pygame.Rect(int(x)-self.RADIUS, int(y)-self.RADIUS,
                              self.RADIUS*2, self.RADIUS*2)
    def update(self):
        self.tick+=1
        if self.grabbed:
            self.rc+=1
            if self.rc>=360: self.grabbed=False; self.rc=0
        self.rect.centery=int(self.y+math.sin(self.tick*0.06)*8)
        self.rect.centerx=int(self.x)
    def check_grab(self, player):
        if self.grabbed or not player.alive: return False
        if self.rect.colliderect(player.rect):
            self.grabbed=True; self.rc=0
            player.vel_x=self.launch_vx; player.vel_y=self.launch_vy
            player.on_ground=False; return True
        return False
    def draw(self, surface, camera, tick):
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
        pygame.draw.line(surface,GOLD,(sx,sy+r+3),
                         (sx+int(math.sin(self.tick*0.04)*4),sy+r+self.STRING_LEN),1)
        for k in range(4):
            a=self.tick*0.08+k*math.pi/2
            dx=int(math.cos(a)*(r+10)); dy=int(math.sin(a)*(r+10))
            pygame.draw.rect(surface,rainbow_color(tick+k*20,0.2),(sx+dx-2,sy+dy-2,4,4))

# ---------------------------------------------------------------------------
# Portal
# ---------------------------------------------------------------------------
class Portal:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x,y,56,80); self.pulse=0
    def update(self): self.pulse=(self.pulse+3)%360
    def check(self, player): return player.alive and player.rect.colliderect(self.rect)
    def draw(self, surface, camera):
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
    def draw(self, surf):
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

    def die(self): self.alive=False; self.respawn_timer=60

    def respawn(self):
        self.rect.topleft=(self.spawn_x,self.spawn_y)
        self.vel_x=self.vel_y=0; self.alive=True
        self.on_ground=False; self.riding_platform=None

    def update(self, keys, platforms):
        if not self.alive:
            self.respawn_timer-=1
            if self.respawn_timer<=0: self.respawn()
            return None

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

        # Horizontal
        self.rect.x+=int(self.vel_x)
        for plat in platforms:
            if not plat.is_active(): continue
            pr=plat.get_rect()
            if self.rect.colliderect(pr):
                if self.rect.bottom<=pr.top+6: continue
                if self.vel_x>0: self.rect.right=pr.left
                elif self.vel_x<0: self.rect.left=pr.right
                self.vel_x=0

        # Vertical
        self.on_ground=False; self.riding_platform=None
        vy=int(self.vel_y)
        if self.vel_y>0 and vy==0: vy=1
        self.rect.y+=vy
        for plat in platforms:
            if not plat.is_active(): continue
            pr=plat.get_rect()
            if self.rect.colliderect(pr):
                if self.vel_y>0:
                    self.rect.bottom=pr.top; self.vel_y=0
                    self.on_ground=True; plat.on_player_land(self)
                elif self.vel_y<0:
                    self.rect.top=pr.bottom; self.vel_y=0

        if self.rect.top>DEATH_Y: self.alive=False; self.respawn_timer=60
        return "jump" if jumped else None

    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr=camera.apply(self.rect)
        EG=(40,160,70); ER=(200,40,50)
        pygame.draw.rect(surface,EG,sr)
        by=sr.y+sr.height//2-2
        pygame.draw.rect(surface,(80,50,20),(sr.x,by,sr.width,5))
        pygame.draw.rect(surface,GOLD,(sr.centerx-4,by-1,8,7))
        pygame.draw.polygon(surface,ER,[(sr.centerx,sr.y-12),(sr.x+2,sr.y+4),(sr.right-2,sr.y+4)])
        pygame.draw.rect(surface,WHITE,(sr.x,sr.y+1,sr.width,5))
        pygame.draw.circle(surface,WHITE,(sr.centerx,sr.y-12),4)
        ey=sr.y+11
        if self.facing_right:
            pygame.draw.rect(surface,WHITE,(sr.x+16,ey,7,6))
            pygame.draw.rect(surface,(0,0,0),(sr.x+19,ey+2,3,3))
        else:
            pygame.draw.rect(surface,WHITE,(sr.x+5,ey,7,6))
            pygame.draw.rect(surface,(0,0,0),(sr.x+5,ey+2,3,3))

# ---------------------------------------------------------------------------
# Sound Manager
# ---------------------------------------------------------------------------
SOUND_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
SOUND_FILES= {"jump":"jump.wav","death":"death.wav","respawn":"respawn.wav",
              "balloon":"powerup.wav","checkpoint":"checkpoint.wav","win":"win.wav"}
MUSIC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "assets","audio","ChristmasMusic.mp3")

class SoundManager:
    def __init__(self):
        self.sounds={}; self.music_loaded=False
        for name,fn in SOUND_FILES.items():
            p=os.path.join(SOUND_DIR,fn)
            try: self.sounds[name]=pygame.mixer.Sound(p) if os.path.isfile(p) else None
            except: self.sounds[name]=None
        if os.path.isfile(MUSIC_FILE):
            try: pygame.mixer.music.load(MUSIC_FILE); self.music_loaded=True
            except: pass
    def play(self, name):
        s=self.sounds.get(name)
        if s: s.play()
    def start_music(self, loops=-1, volume=0.5):
        if self.music_loaded:
            pygame.mixer.music.set_volume(volume); pygame.mixer.music.play(loops)
    def stop_music(self): pygame.mixer.music.stop()

# ---------------------------------------------------------------------------
# Level layout
# ---------------------------------------------------------------------------
# X positions (left to right):
#
#  0      START (safe)
#  420    ICE shrink 1
#  660    ICE shrink 2
#  910    SAFE 1                          ← section checkpoint A (after ice)
#  1240   FALL 1
#  1460   FALL 2
#  1690   SAFE 2                          ← section checkpoint B (after falls)
#  1880   SPIKE base + BALLOON above
#  2120   BALLOON landing                 ← section checkpoint C (after balloon)
#  2450   PHANTOM 1
#  2640   PHANTOM 2
#  2840   SAFE 3                          ← section checkpoint D (after phantom)
# ----- NEW OBSTACLES -----
#  3200   COUNTDOWN platform (obs 1)
#  3500   countdown target platform       ← section checkpoint E (after countdown)
#  3800   WALL-CLIMB pad + two walls
#  4100   wall-exit platform              ← section checkpoint F (after wall)
#  4400   TRAM platform → SANTA SLEIGH    ← checkpoint G set by sleigh carry
#  4700   Portal (final)
#
PW_SAFE=250; PW_SHRINK=160; PW_FALL=140; PW_PHANTOM=110; PH=28

def create_christmas_level(preset):
    platforms=[]
    shrink_platforms=[]; fall_platforms=[]; phantom_platforms=[]
    wall_sides=[]; tram_platform=None; santa_sleigh=None
    countdown_platforms=[]; spikes=[]; balloon=None
    section_checkpoints=[]

    def add(p): platforms.append(p); return p

    # ── START ────────────────────────────────────────────────────────────
    add(Platform(0, BASE_Y, PW_SAFE, PH, PINE_GREEN))

    # ── ICE shrink ────────────────────────────────────────────────────────
    sp=preset["shrink_speed"]
    for p in [ShrinkingPlatform(420,BASE_Y-30,PW_SHRINK,PH,sp),
              ShrinkingPlatform(660,BASE_Y-60,PW_SHRINK,PH,sp)]:
        add(p); shrink_platforms.append(p)

    # SAFE 1 + checkpoint A (after ice section)
    add(Platform(910, BASE_Y-40, PW_SAFE, PH, PINE_GREEN))
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=910, spawn_x=920, spawn_y=BASE_Y-40-40, label="A  Ice cleared"))

    # ── FALL platforms ────────────────────────────────────────────────────
    fd=preset["fall_delay"]
    for p in [FallingPlatform(1240,BASE_Y-20,PW_FALL,PH,fd),
              FallingPlatform(1460,BASE_Y,   PW_FALL,PH,fd)]:
        add(p); fall_platforms.append(p)

    # SAFE 2 + checkpoint B
    add(Platform(1690, BASE_Y, 100, PH, PINE_GREEN))
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=1690, spawn_x=1700, spawn_y=BASE_Y-40, label="B  Falls cleared"))

    # ── SPIKES + BALLOON ─────────────────────────────────────────────────
    sbx=1880; sby=BASE_Y+10
    add(Platform(sbx, sby, 140, PH, (60,60,70)))
    spikes.append(SpikeTrap(sbx+6, sby, 9))
    balloon=Balloon(sbx+70, sby-90, preset["balloon_vx"], preset["balloon_vy"])

    # BALLOON landing + checkpoint C
    add(Platform(2120, BASE_Y-20, PW_SAFE, PH, PINE_GREEN))
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=2120, spawn_x=2130, spawn_y=BASE_Y-20-40, label="C  Balloon cleared"))

    # ── PHANTOM platforms ────────────────────────────────────────────────
    pf=preset["phantom_frames"]
    for p in [PhantomPlatform(2450,BASE_Y-50,PW_PHANTOM,PH,pf),
              PhantomPlatform(2640,BASE_Y-80,PW_PHANTOM,PH,pf)]:
        add(p); phantom_platforms.append(p)

    # SAFE 3 + checkpoint D
    add(Platform(2840, BASE_Y-60, PW_SAFE+50, PH, PINE_GREEN))
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=2840, spawn_x=2850, spawn_y=BASE_Y-60-40, label="D  Phantom cleared"))

    # ── OBSTACLE 1: COUNTDOWN ────────────────────────────────────────────
    # Approach platform → Countdown pad → Hidden target platform
    add(Platform(3060, BASE_Y-60, 120, PH, PINE_GREEN))  # approach

    cnt_frames = preset["countdown_sec"] * FPS
    cd_pad = CountdownPlatform(3240, BASE_Y-60, 180, PH, countdown_frames=cnt_frames)
    add(cd_pad); countdown_platforms.append(cd_pad)

    cd_target = CountdownTargetPlatform(3490, BASE_Y-60, PW_SAFE, PH, owner=cd_pad)
    cd_pad.target = cd_target
    add(cd_target)
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=3490, spawn_x=3500, spawn_y=BASE_Y-60-40, label="E  Countdown cleared"))

    # ── OBSTACLE 2: WALL CLIMB ───────────────────────────────────────────
    # Approach → Wall-climb pad (flanked by two tall walls) → Exit
    add(Platform(3810, BASE_Y-60, 100, PH, PINE_GREEN))  # approach

    wcp_x=3970; wcp_y=BASE_Y-60
    wc_pad = WallClimbPlatform(wcp_x, wcp_y, 160, PH,
                               required_bounces=preset["wall_bounces"])
    add(wc_pad)

    wall_h = 200
    lw = WallSide(wcp_x-30,   wcp_y-wall_h+PH, 28, wall_h, "LEFT",  wc_pad)
    rw = WallSide(wcp_x+160+2, wcp_y-wall_h+PH, 28, wall_h, "RIGHT", wc_pad)
    add(lw); add(rw); wall_sides+=[lw,rw]

    wc_exit = WallExitPlatform(4210, BASE_Y-60, PW_SAFE, PH, owner=wc_pad)
    add(wc_exit)
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=4210, spawn_x=4220, spawn_y=BASE_Y-60-40, label="F  Wall cleared"))

    # ── OBSTACLE 3: TRAM + SANTA SLEIGH ──────────────────────────────────
    add(Platform(4530, BASE_Y-60, 120, PH, PINE_GREEN))  # approach

    tram_x=4710; tram_y=BASE_Y-60
    tram = TramPlatform(tram_x, tram_y, 160, PH, speed=preset["tram_speed"])
    add(tram); tram_platform=tram

    # Portal sits at end of level
    portal_x=5100; portal_y=BASE_Y-60-80
    # SantaSleigh will teleport player to just left of portal
    santa = SantaSleigh(portal_spawn_x=portal_x-80, portal_spawn_y=portal_y+80, tram=tram)
    santa_sleigh=santa
    # checkpoint G is set dynamically when sleigh carries player (inside SantaSleigh.update)
    section_checkpoints.append(SectionCheckpoint(
        trigger_x=5020, spawn_x=5020, spawn_y=BASE_Y-60-40, label="G  Santa cleared"))

    # Final safe platform + portal
    add(Platform(4990, BASE_Y-60, PW_SAFE+50, PH, PINE_GREEN))
    portal=Portal(portal_x, portal_y)

    return dict(
        platforms=platforms,
        shrink_platforms=shrink_platforms,
        fall_platforms=fall_platforms,
        phantom_platforms=phantom_platforms,
        wall_sides=wall_sides,
        countdown_platforms=countdown_platforms,
        tram_platform=tram_platform,
        santa_sleigh=santa_sleigh,
        spikes=spikes,
        balloon=balloon,
        portal=portal,
        section_checkpoints=section_checkpoints,
    )

# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    DIFF_OPTIONS=["easy","medium","hard"]
    DIFF_COLORS={"easy":(80,200,80),"medium":(255,200,50),"hard":(220,60,60)}

    def __init__(self):
        self.screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pygame.display.set_caption("Glitch Claus - Christmas Level")
        self.clock=pygame.time.Clock()
        self.font       =pygame.font.SysFont("consolas",24)
        self.small_font =pygame.font.SysFont("consolas",16)
        self.big_font   =pygame.font.SysFont("consolas",48)
        self.tiny_font  =pygame.font.SysFont("consolas",12,bold=True)
        self.cp_font    =pygame.font.SysFont("consolas",13,bold=True)
        self.sfx=SoundManager()
        self.diff_index=1; self.difficulty=self.DIFF_OPTIONS[1]
        self.state="playing"; self.settings_cursor=0
        self.music_volume=0.5; self.music_muted=False
        self.tick=0; self.level_time=0; self.win_timer=0
        self.camera=Camera(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.particles=[]; self.rings=[]; self.flashes=[]
        self.snowflakes=[Snowflake() for _ in range(80)]
        self._load_level()
        self.sfx.start_music(volume=self.music_volume)

    def _load_level(self):
        preset=DIFFICULTY_PRESETS[self.difficulty]
        d=create_christmas_level(preset)
        self.platforms          =d["platforms"]
        self.shrink_platforms   =d["shrink_platforms"]
        self.fall_platforms     =d["fall_platforms"]
        self.phantom_platforms  =d["phantom_platforms"]
        self.wall_sides         =d["wall_sides"]
        self.countdown_platforms=d["countdown_platforms"]
        self.tram_platform      =d["tram_platform"]
        self.santa_sleigh       =d["santa_sleigh"]
        self.spikes             =d["spikes"]
        self.balloon            =d["balloon"]
        self.portal             =d["portal"]
        self.section_checkpoints=d["section_checkpoints"]
        self.player=Player(80,BASE_Y-60,
                           move_speed   =preset["player_speed"],
                           jump_velocity=preset["player_jump"])
        self.camera=Camera(SCREEN_WIDTH,SCREEN_HEIGHT)
        self.particles.clear(); self.rings.clear(); self.flashes.clear()
        self.level_time=0; self.tick=0; self.win_timer=0
        self._tram_started=False

    def _apply_volume(self):
        pygame.mixer.music.set_volume(0.0 if self.music_muted else self.music_volume)

    def _exit_to_menu(self):
        self.sfx.stop_music(); self.running=False

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        self.running=True
        while self.running:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: self._exit_to_menu(); return
                if ev.type==pygame.KEYDOWN: self._handle_key(ev.key)
            if not self.running: return
            if self.state=="playing": self._update()
            elif self.state=="win":   self.win_timer+=1
            self._draw()
            self.clock.tick(FPS)

    def _handle_key(self, key):
        if self.state=="settings":
            if key==pygame.K_ESCAPE: self.state="playing"; return
            nr=5
            if key in (pygame.K_UP,pygame.K_w):   self.settings_cursor=(self.settings_cursor-1)%nr
            elif key in (pygame.K_DOWN,pygame.K_s): self.settings_cursor=(self.settings_cursor+1)%nr
            elif self.settings_cursor==0:
                if key in (pygame.K_LEFT,pygame.K_a):
                    self.diff_index=(self.diff_index-1)%3; self.difficulty=self.DIFF_OPTIONS[self.diff_index]
                elif key in (pygame.K_RIGHT,pygame.K_d,pygame.K_RETURN,pygame.K_SPACE):
                    self.diff_index=(self.diff_index+1)%3; self.difficulty=self.DIFF_OPTIONS[self.diff_index]
            elif self.settings_cursor==1:
                if key in (pygame.K_LEFT,pygame.K_a):   self.music_volume=max(0.0,round(self.music_volume-0.1,1)); self._apply_volume()
                elif key in (pygame.K_RIGHT,pygame.K_d): self.music_volume=min(1.0,round(self.music_volume+0.1,1)); self._apply_volume()
            elif self.settings_cursor==2:
                if key in (pygame.K_RETURN,pygame.K_SPACE): self.music_muted=not self.music_muted; self._apply_volume()
            elif self.settings_cursor==3:
                if key in (pygame.K_RETURN,pygame.K_SPACE): self.state="playing"
            elif self.settings_cursor==4:
                if key in (pygame.K_RETURN,pygame.K_SPACE): self._exit_to_menu()
            return
        if self.state=="win":
            if key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_ESCAPE): self._exit_to_menu()
            return
        if key==pygame.K_ESCAPE: self.state="settings"; self.settings_cursor=3
        elif key==pygame.K_r:    self._load_level()

    # ── Update ────────────────────────────────────────────────────────────
    def _update(self):
        self.tick+=1; self.level_time+=1
        keys=pygame.key.get_pressed()

        for p in self.platforms: p.update()

        result=self.player.update(keys, self.platforms)
        if result=="jump": self.sfx.play("jump")

        # ── Wall-side collision detection ─────────────────────────────────
        # We detect horizontal collision with wall sides specifically so we
        # can report LEFT/RIGHT bounce to the WallClimbPlatform
        if self.player.alive:
            for ws in self.wall_sides:
                if ws.rect.colliderect(self.player.rect):
                    ws.register_hit(self.player)
                    # Push player out (simple)
                    if ws.side=="RIGHT":
                        self.player.rect.right=ws.rect.left
                        self.player.vel_x=-abs(self.player.vel_x)*0.5
                    else:
                        self.player.rect.left=ws.rect.right
                        self.player.vel_x=abs(self.player.vel_x)*0.5

        # ── Tram + sleigh ─────────────────────────────────────────────────
        if self.tram_platform and self.tram_platform.moving and not self._tram_started:
            self._tram_started=True
            if self.santa_sleigh: self.santa_sleigh.start(self.tram_platform.rect)

        if self.santa_sleigh and self.santa_sleigh.state!="waiting":
            self.santa_sleigh.update(self.player)
            if self.santa_sleigh.state=="done" and not self._tram_started:
                pass   # already handled inside SantaSleigh.update

        # If tram goes too far right and player is still riding it, kill player
        if self.tram_platform and self.player.alive:
            if (self.tram_platform.moving
                    and self.tram_platform.rect.left > 6000
                    and self.player.on_ground
                    and self.player.riding_platform is self.tram_platform):
                self._death_fx(); self.player.die(); self.sfx.play("death")

        # ── Section checkpoints ───────────────────────────────────────────
        for sc in self.section_checkpoints:
            sc.update()
            if sc.check(self.player):
                self.sfx.play("checkpoint")
                self._checkpoint_fx_at(sc.trigger_x, BASE_Y-30)

        if self.player.alive: self.camera.update(self.player.rect)

        # ── Spikes ───────────────────────────────────────────────────────
        for sp in self.spikes:
            if sp.check_kill(self.player):
                self._death_fx(); self.player.die(); self.sfx.play("death")

        # ── Balloon ──────────────────────────────────────────────────────
        self.balloon.update()
        if self.balloon.check_grab(self.player):
            self._balloon_fx(); self.sfx.play("balloon")

        # ── Portal ───────────────────────────────────────────────────────
        self.portal.update()
        if self.player.alive and self.portal.check(self.player):
            self.state="win"; self.win_timer=0
            self.sfx.play("win"); self.sfx.stop_music()

        if not self.player.alive and self.player.respawn_timer==1:
            self.sfx.play("respawn")

        self.particles=[p for p in self.particles if p.update()]
        self.rings    =[r for r in self.rings     if r.update()]
        self.flashes  =[f for f in self.flashes   if f.update()]
        for sf in self.snowflakes: sf.update()
        self._spawn_ambient()

    # ── Effects ───────────────────────────────────────────────────────────
    def _death_fx(self):
        cx,cy=self.player.rect.centerx,self.player.rect.centery
        self.camera.add_shake(12)
        self.flashes.append(FlashOverlay(RED,18,110))
        for _ in range(30):
            a=random.uniform(0,math.pi*2); s=random.uniform(2,6)
            self.particles.append(Particle(cx,cy,random.choice([SNOW_WHITE,ICE_BLUE,CANDY_RED]),
                                           math.cos(a)*s,math.sin(a)*s,
                                           random.randint(20,45),random.randint(3,6),0.18))
    def _balloon_fx(self):
        cx,cy=self.balloon.rect.centerx,self.balloon.rect.centery
        self.camera.add_shake(8)
        self.flashes.append(FlashOverlay(GOLD,12,90))
        self.rings.append(RingEffect(cx,cy,BALLOON_PINK,70,5,3))
        for _ in range(25):
            a=random.uniform(0,math.pi*2); s=random.uniform(1,5)
            self.particles.append(Particle(cx,cy,random.choice([BALLOON_RED,BALLOON_PINK,GOLD,WHITE]),
                                           math.cos(a)*s,math.sin(a)*s,
                                           random.randint(20,40),random.randint(2,5),0.05))
    def _checkpoint_fx_at(self, wx, wy):
        self.rings.append(RingEffect(wx,wy,CP_GLOW,55,4,3))
        self.flashes.append(FlashOverlay(CP_ACTIVE,10,60))
        for _ in range(18):
            a=random.uniform(0,math.pi*2); s=random.uniform(1,4)
            self.particles.append(Particle(wx,wy,random.choice([CP_ACTIVE,CP_GLOW,WHITE,GOLD]),
                                           math.cos(a)*s,math.sin(a)*s,
                                           random.randint(20,40),random.randint(2,5),0.06))
    def _spawn_ambient(self):
        for p in self.phantom_platforms:
            if not p.gone and random.random()<0.15:
                self.particles.append(Particle(
                    p.rect.x+random.randint(0,p.rect.width),p.rect.y,PHANTOM_TEAL,
                    random.uniform(-0.5,0.5),random.uniform(-1.5,-0.3),20,3,0.0))
        for p in self.shrink_platforms:
            if p.shrinking and not p.gone and random.random()<0.2:
                self.particles.append(Particle(
                    p.rect.x+random.randint(0,max(1,p.rect.width)),
                    p.rect.y+random.randint(0,p.rect.height),ICE_BLUE,
                    random.uniform(-1,1),random.uniform(-1.5,0),15,2,0.0))

    # ── Drawing ───────────────────────────────────────────────────────────
    def _draw(self):
        self.screen.fill(DARK_BG)
        if self.state in ("playing","settings"): self._draw_game()
        if self.state=="settings":               self._draw_settings()
        elif self.state=="win":                  self._draw_win()
        pygame.display.flip()

    def _draw_background(self):
        ox=int(self.camera.offset_x*0.2)%80
        for x in range(0,SCREEN_WIDTH+80,80):
            pygame.draw.line(self.screen,GRID_COLOR,(x-ox,0),(x-ox,SCREEN_HEIGHT))
        for y in range(0,SCREEN_HEIGHT+80,80):
            pygame.draw.line(self.screen,GRID_COLOR,(0,y),(SCREEN_WIDTH,y))
        for i in range(60):
            sx=(i*137+int(self.camera.offset_x*0.05))%SCREEN_WIDTH
            sy=(i*89)%(SCREEN_HEIGHT-60)
            b=80+int(40*math.sin(self.tick*0.05+i))
            pygame.draw.rect(self.screen,(b,b,b+30),(sx,sy,2,2))

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
        self.player.draw(self.screen,self.camera,self.tick)
        for f in self.flashes:     f.draw(self.screen)

        # Wall-climb hint (show while player is on the pad and not yet done)
        for ws in self.wall_sides:
            if ws.owner.active_player and not ws.owner.unlocked:
                wsr=self.camera.apply(ws.owner.rect)
                step=ws.owner.step
                total=ws.owner.total_steps
                needed=WALL_SEQUENCE[step%len(WALL_SEQUENCE)]
                hint=self.small_font.render(
                    f"Bounce {needed}  ({step}/{total})", True, CYAN)
                self.screen.blit(hint,(wsr.centerx-hint.get_width()//2, wsr.y-38))
                break

        # HUD
        self.screen.blit(self.small_font.render(f"Time: {self.level_time/FPS:.1f}s",True,SNOW_WHITE),
                         (SCREEN_WIDTH-160,12))
        total_sc  =len(self.section_checkpoints)
        reached_sc=sum(1 for sc in self.section_checkpoints if sc.activated)
        cp_col    =CP_ACTIVE if reached_sc==total_sc else SNOW_WHITE
        self.screen.blit(self.small_font.render(f"CP  {reached_sc}/{total_sc}",True,cp_col),
                         (SCREEN_WIDTH-160,34))
        dc=self.DIFF_COLORS[self.difficulty]
        ds=self.small_font.render(f"[ {self.difficulty.upper()} ]",True,dc)
        self.screen.blit(ds,(SCREEN_WIDTH//2-ds.get_width()//2,10))

        legend=[
            (ICE_BLUE,     "Ice - shrinks"),
            (FALLING_BROWN,"Wood - falls"),
            (SPIKE_GRAY,   "Spikes - death"),
            (BALLOON_RED,  "Balloon - fly over"),
            (PHANTOM_TEAL, "Teal - phantom"),
            (COUNTDOWN_COL,"Blue - wait for GO"),
            (WALL_COL,     "Purple - bounce walls"),
            (MOVING_COL,   "Gold - ride & jump!"),
            (CP_ACTIVE,    "Flag - checkpoint"),
        ]
        for li,(col,txt) in enumerate(legend):
            pygame.draw.rect(self.screen,col,(12,12+li*17,10,10))
            self.screen.blit(self.tiny_font.render(txt,True,(160,180,200)),(26,10+li*17))

        self.screen.blit(self.tiny_font.render(
            "SPACE/W-Jump  A/D-Move  R-Restart  ESC-Settings",True,(80,100,120)),
            (10,SCREEN_HEIGHT-20))
        if not self.player.alive:
            t=self.font.render("Respawning...",True,RED)
            self.screen.blit(t,t.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)))

    def _draw_settings(self):
        ov=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)); ov.fill(BLACK); ov.set_alpha(170)
        self.screen.blit(ov,(0,0))
        tit=self.font.render("SETTINGS",True,CYAN)
        self.screen.blit(tit,tit.get_rect(center=(SCREEN_WIDTH//2,130)))
        dc=self.DIFF_COLORS[self.difficulty]
        desc={"easy":"Slow shrink  |  long warning  |  generous balloon",
              "medium":"Balanced experience",
              "hard":"Fast shrink  |  instant drop  |  blink phantom"}
        ds=self.tiny_font.render(desc[self.difficulty],True,dc)
        self.screen.blit(ds,ds.get_rect(center=(SCREEN_WIDTH//2,168)))
        items=[(f"Difficulty :  < {self.difficulty.upper()} >","Left/Right to change  |  R to restart"),
               (f"Music Volume :  < {int(self.music_volume*100)}% >","Left/Right"),
               (f"Mute Music :  {'ON' if self.music_muted else 'OFF'}","Enter to toggle"),
               ("Resume","Enter or ESC"),("Exit to Menu","Enter")]
        for i,(label,hint) in enumerate(items):
            y=205+i*58; sel=(i==self.settings_cursor)
            if sel:
                bar=pygame.Rect(SCREEN_WIDTH//2-240,y-4,480,30)
                pygame.draw.rect(self.screen,(30,40,60),bar)
                pygame.draw.rect(self.screen,CYAN,bar,1)
                self.screen.blit(self.small_font.render(">",True,CYAN),(SCREEN_WIDTH//2-228,y))
            rc=(dc if(i==0 and sel) else lerp_color(dc,GRAY,0.5) if i==0 else WHITE if sel else GRAY)
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
        for lbl,col,y in [
            ("MERRY CHRISTMAS!", GOLD, 140),
        ]:
            t=self.big_font.render(lbl,True,col)
            self.screen.blit(t,t.get_rect(center=(SCREEN_WIDTH//2,y)))
        for lbl,col,y in [
            ("You escaped the Glitch Winter!",ICE_BLUE,215),
            (f"Time: {self.level_time/FPS:.1f} seconds",YELLOW,265),
            (f"Checkpoints: {sum(1 for sc in self.section_checkpoints if sc.activated)}/{len(self.section_checkpoints)}",CP_ACTIVE,315),
            (f"Difficulty: {self.difficulty.upper()}",self.DIFF_COLORS[self.difficulty],365),
        ]:
            t=self.font.render(lbl,True,col)
            self.screen.blit(t,t.get_rect(center=(SCREEN_WIDTH//2,y)))
        h=self.small_font.render("Press ENTER or ESC to exit",True,WHITE)
        self.screen.blit(h,h.get_rect(center=(SCREEN_WIDTH//2,430)))

# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------
def launch_game():
    pygame.mixer.music.stop()
    game=Game(); game.run()
    pygame.display.set_caption("Christmas Pixel Adventure")
    try: pygame.mixer.music.load("assets/audio/BackgroundMusic.mp3"); pygame.mixer.music.play(-1)
    except: pass

if __name__=="__main__":
    pygame.init(); pygame.mixer.init()
    game=Game(); game.run()
    pygame.quit()