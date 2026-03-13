import pygame
import sys
import math
import random
import os

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS = 60

BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
XMAS_RED    = (200, 30, 30)
XMAS_GREEN  = (30, 160, 50)
XMAS_DARK_GREEN = (20, 100, 35)
XMAS_GOLD   = (255, 200, 50)
ICE_BLUE    = (140, 200, 240)
SNOW_WHITE  = (240, 245, 255)
CANDY_PINK  = (255, 130, 160)
CANDY_WHITE = (255, 240, 240)
DARK_SKY    = (10, 12, 30)
NIGHT_BLUE  = (15, 20, 50)
GRAY        = (140, 140, 140)
DARK_GRAY   = (80, 80, 80)
PURPLE      = (160, 50, 200)
RED         = (220, 50, 50)
GREEN       = (50, 200, 80)
YELLOW      = (255, 220, 50)
CYAN        = (0, 220, 255)
ORANGE      = (255, 160, 30)
MAGENTA     = (220, 40, 180)
GOLD        = (255, 200, 50)
BROWN       = (139, 90, 43)
DARK_BROWN  = (100, 60, 30)
MUSHROOM_RED = (200, 45, 45)
BLUE        = (50, 120, 255)
BOMB_BLACK  = (40, 40, 45)
BOMB_GRAY   = (70, 70, 75)
FUSE_ORANGE = (255, 140, 30)
FUSE_RED    = (255, 60, 20)
NPC_ROBE    = (60, 60, 160)
DIALOG_BG   = (10, 10, 28, 230)

GRAVITY        = 0.6
JUMP_VELOCITY  = -13
MOVE_SPEED     = 5
SPRINT_SPEED   = 8
MAX_FALL_SPEED = 15
DEATH_Y        = 800
STOMP_BOUNCE   = -10
UNREAL_DURATION    = 480
UNREAL_SPEED_BOOST = 2
SNOWBALL_SPEED    = 10
SNOWBALL_LIFETIME = 90
SNOWBALL_COOLDOWN = 18
BOMB_EXPLODE_RADIUS = 120
DASH_SPEED = 18
DASH_DURATION = 8
DASH_COOLDOWN = 45
PLAYER_MAX_HEARTS = 3
INVINCIBILITY_FRAMES = 90  # 1.5 sec at 60fps
BOSS_MAX_HP = 10
ICICLE_SHAKE_TIME = 30
ICICLE_FALL_SPEED = 8

DIFFICULTY = {
    "easy":   {"bomb_fuse": 300, "bomb_detect": 180, "bomb_spd": 0.5, "mon_spd": 0.65, "bomb_hits": 1,
               "plat_spd": 0.6, "glitch_on": 140, "glitch_off": 40, "collapse_delay": 70, "tp_interval": 200},
    "medium": {"bomb_fuse": 220, "bomb_detect": 230, "bomb_spd": 0.8, "mon_spd": 0.85, "bomb_hits": 2,
               "plat_spd": 0.85, "glitch_on": 110, "glitch_off": 55, "collapse_delay": 55, "tp_interval": 150},
    "hard":   {"bomb_fuse": 150, "bomb_detect": 300, "bomb_spd": 1.3, "mon_spd": 1.0,  "bomb_hits": 2,
               "plat_spd": 1.0, "glitch_on": 80, "glitch_off": 65, "collapse_delay": 40, "tp_interval": 110},
}

XMAS_COLORS = [(220,30,30),(255,200,50),(30,180,60),(255,255,255),(220,30,30),(50,180,220),(255,130,160)]

def lerp_color(a, b, t):
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def xmas_cycle_color(tick, speed=0.05):
    idx = (tick*speed) % len(XMAS_COLORS); i = int(idx); frac = idx-i
    return lerp_color(XMAS_COLORS[i], XMAS_COLORS[(i+1)%len(XMAS_COLORS)], frac)

def rainbow_color(tick, speed=0.05):
    return xmas_cycle_color(tick, speed)

# --- Story Dialogues ---
STORY_DIALOGUES = {
    "intro": [
        ("Elder Frost", "Brave dreamer... you have reached the Fourth Realm."),
        ("Elder Frost", "The Frozen Christmas Realm -- the final barrier between you and waking."),
        ("Elder Frost", "Three realms you have conquered in your slumber... but this one will not let you go easily."),
        ("Elder Frost", "Let me teach you what you need to survive here."),
        ("Elder Frost", "MOVEMENT: Arrow keys or WASD to move. SPACE or UP to jump. SHIFT to sprint."),
        ("Elder Frost", "SNOWBALLS: Press F or X to throw snowballs. They fly in the direction you face."),
        ("Elder Frost", "STOMPING: Jump on top of mushroom enemies to squash them -- like the old plumber's trick."),
        ("Elder Frost", "BOMB FIENDS: These black bombs start ticking when you get close. Shoot them with snowballs!"),
        ("Elder Frost", "Hit a Bomb Fiend TWICE before its fuse runs out, or it EXPLODES and takes you with it."),
        ("Elder Frost", "GOLDEN ORNAMENTS: Grab them for Unreal Mode -- you become invincible and faster for a short time."),
        ("Elder Frost", "ICE PLATFORMS: Some platforms fade in and out. Time your jumps. Others crumble when you stand on them."),
        ("Elder Frost", "One more thing -- press ESC for settings, R to respawn, and E to talk to us guides."),
        ("Elder Frost", "Now go, dreamer. The dream ends here, one way or another."),
    ],
    "cp1": [
        ("Holly", "You survived the first stretch! I am Holly, another fragment of your dreaming mind."),
        ("Holly", "Three realms you have already conquered... fire, shadow, and storm."),
        ("Holly", "This frozen realm is the dream's last defense. It knows you are close to waking."),
        ("Holly", "The path ahead grows treacherous. Icy platforms that vanish beneath your feet..."),
        ("Holly", "Stay brave, dreamer. We are all rooting for you."),
    ],
    "cp2": [
        ("Jingle", "Ha! Still standing? Name's Jingle. I guard the middle stretch."),
        ("Jingle", "You know, this realm used to be beautiful before the nightmare corrupted it."),
        ("Jingle", "Christmas lights, warm hearths, children laughing in the snow..."),
        ("Jingle", "Now it is all ice and monsters. But every enemy you defeat weakens the nightmare's grip."),
        ("Jingle", "Keep pushing forward. The dream cannot hold you forever."),
    ],
    "cp3": [
        ("Elder Frost", "I can feel the dream weakening. You are so close now."),
        ("Elder Frost", "When you first fell asleep, the nightmare trapped your mind in four realms."),
        ("Elder Frost", "Each realm was a fear given form. Fire was your anger. Shadow was your doubt."),
        ("Elder Frost", "Storm was your grief. And this... this frozen place is your loneliness."),
        ("Elder Frost", "But you have proven stronger than all of them. The gift box ahead -- it is the doorway to waking."),
    ],
    "cp4": [
        ("Holly", "This is it. The final gauntlet. Everything the dream has, it will throw at you now."),
        ("Holly", "I have watched so many dreamers fall at this last hurdle. Their minds gave up."),
        ("Holly", "But you... you are different. I can see it in the way you fight."),
        ("Holly", "When you reach that gift box, the dream shatters. You wake up. Christmas morning."),
        ("Holly", "We believe in you, dreamer. Now go -- and do not look back!"),
    ],
    "ending": [
        ("Elder Frost", "...You did it."),
        ("Elder Frost", "The Fourth Realm crumbles. The dream releases its hold."),
        ("Elder Frost", "Four realms conquered. Four nightmares shattered."),
        ("Holly", "We were all fragments of your sleeping mind, you know."),
        ("Jingle", "Heh. Gonna miss throwing snowballs at bomb fiends though."),
        ("Elder Frost", "When you open your eyes, you will not remember our faces."),
        ("Elder Frost", "But you will remember the courage. That part is real."),
        ("Elder Frost", "Merry Christmas, dreamer. It is time to wake up."),
        ("", "You feel warmth. Sunlight on your face. The smell of pine and cinnamon."),
        ("", "Your eyes flutter open. Christmas morning."),
        ("", "It was all a dream... wasn't it?"),
        ("", "On your nightstand, a single golden ornament glows faintly, then fades."),
    ],
}

# --- Sound ---
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
SOUND_FILES = {
    "jump":"jump.wav","death":"death.wav","respawn":"respawn.wav",
    "stomp":"stomp.wav","monster_kill":"monster_kill.wav",
    "powerup":"powerup.wav","unreal_end":"unreal_end.wav",
    "checkpoint":"checkpoint.wav","win":"win.wav",
    "shoot":"shoot.wav","bomb_explode":"bomb_explode.wav","bomb_defuse":"bomb_defuse.wav",
}
MUSIC_FILE = "assets/audio/Level4Music.mp3"

class SoundManager:
    def __init__(self):
        self.sounds = {}; self.music_loaded = False
        for name, fn in SOUND_FILES.items():
            path = os.path.join(SOUND_DIR, fn)
            try: self.sounds[name] = pygame.mixer.Sound(path) if os.path.isfile(path) else None
            except: self.sounds[name] = None
        if os.path.isfile(MUSIC_FILE):
            try: pygame.mixer.music.load(MUSIC_FILE); self.music_loaded = True
            except: pass
    def play(self, n):
        s = self.sounds.get(n)
        if s: s.play()
    def start_music(self, loops=-1, volume=0.5):
        if self.music_loaded: pygame.mixer.music.set_volume(volume); pygame.mixer.music.play(loops)
    def stop_music(self): pygame.mixer.music.stop()

# --- Camera ---
class Camera:
    def __init__(self, w, h):
        self.offset_x=0.0; self.offset_y=0.0; self.width=w; self.height=h
        self.shake_amount=0.0; self.shake_x=0; self.shake_y=0
    def update(self, r):
        self.offset_x += (r.centerx - self.width//3 - self.offset_x)*0.1
        ty = r.centery - self.height//2
        self.offset_y += (ty - self.offset_y)*0.05
        self.offset_y = max(-200, min(self.offset_y, 200))
        if self.shake_amount > 0.5:
            self.shake_x = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_y = random.randint(int(-self.shake_amount), int(self.shake_amount))
            self.shake_amount *= 0.85
        else: self.shake_amount=0; self.shake_x=self.shake_y=0
    def add_shake(self, a): self.shake_amount = min(self.shake_amount+a, 20)
    def apply(self, rect):
        return pygame.Rect(rect.x-int(self.offset_x)+self.shake_x,
                           rect.y-int(self.offset_y)+self.shake_y, rect.width, rect.height)

# --- Particle / Effects ---
class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, lifetime=30, size=4, gravity=0.1, fade=True):
        self.x,self.y=float(x),float(y); self.color=color; self.vel_x,self.vel_y=vx,vy
        self.lifetime=lifetime; self.max_lifetime=lifetime; self.base_size=size
        self.gravity=gravity; self.fade=fade
    def update(self):
        self.x+=self.vel_x; self.y+=self.vel_y; self.vel_y+=self.gravity; self.lifetime-=1
        return self.lifetime>0
    def draw(self, surface, camera):
        a = self.lifetime/self.max_lifetime if self.fade else 1.0
        sz = max(1,int(self.base_size*a))
        c = tuple(max(0,min(255,int(v*a))) for v in self.color)
        p = camera.apply(pygame.Rect(int(self.x),int(self.y),1,1))
        pygame.draw.rect(surface, c, (p.x, p.y, sz, sz))

class Snowflake:
    def __init__(self):
        self.reset(False)
    def reset(self, top=True):
        self.x=random.uniform(0,SCREEN_WIDTH)
        self.y=random.uniform(-20,0) if top else random.uniform(0,SCREEN_HEIGHT)
        self.size=random.uniform(1.5,4); self.sy=random.uniform(0.5,2.0)
        self.sx=random.uniform(-0.3,0.3); self.wp=random.uniform(0,math.pi*2)
        self.ws=random.uniform(0.01,0.04); self.wa=random.uniform(0.3,1.2)
        self.alpha=random.uniform(0.4,1.0)
    def update(self):
        self.wp+=self.ws; self.x+=self.sx+math.sin(self.wp)*self.wa; self.y+=self.sy
        if self.y>SCREEN_HEIGHT+10: self.reset(True)
        if self.x<-10: self.x=SCREEN_WIDTH+5
        elif self.x>SCREEN_WIDTH+10: self.x=-5
    def draw(self, surface):
        a=self.alpha
        pygame.draw.circle(surface,(int(240*a),int(245*a),int(255*a)),(int(self.x),int(self.y)),int(self.size))

class BGStar:
    def __init__(self):
        self.x=random.uniform(0,SCREEN_WIDTH); self.y=random.uniform(0,SCREEN_HEIGHT*0.55)
        self.bb=random.uniform(0.3,1.0); self.ts=random.uniform(0.02,0.08)
        self.phase=random.uniform(0,math.pi*2); self.size=random.choice([1,1,1,2])
    def draw(self, surface, tick):
        b=self.bb*(0.5+0.5*math.sin(tick*self.ts+self.phase))
        pygame.draw.circle(surface,(int(255*b),int(255*b),int(200*b)),(int(self.x),int(self.y)),self.size)

class RingEffect:
    def __init__(self, x, y, color, max_radius=120, speed=4, width=4):
        self.x,self.y=x,y; self.color=color; self.radius=0
        self.max_radius=max_radius; self.speed=speed; self.width=width
    def update(self): self.radius+=self.speed; return self.radius<self.max_radius
    def draw(self, surface, camera):
        a=1.0-(self.radius/self.max_radius)
        c=tuple(max(0,min(255,int(v*a))) for v in self.color)
        w=max(1,int(self.width*a))
        p=camera.apply(pygame.Rect(int(self.x),int(self.y),1,1))
        if 0<=p.x<=SCREEN_WIDTH and 0<=p.y<=SCREEN_HEIGHT:
            pygame.draw.circle(surface,c,(p.x,p.y),int(self.radius),w)

class FlashOverlay:
    def __init__(self, color, duration=15, max_alpha=180):
        self.color=color; self.duration=duration; self.timer=duration; self.max_alpha=max_alpha
        self.surface=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)); self.surface.fill(color)
    def update(self): self.timer-=1; return self.timer>0
    def draw(self, surface):
        self.surface.set_alpha(int(self.max_alpha*(self.timer/self.duration)))
        surface.blit(self.surface,(0,0))

class Snowball:
    RADIUS=5
    def __init__(self, x, y, d):
        self.x=float(x); self.y=float(y); self.dir=d
        self.lifetime=SNOWBALL_LIFETIME; self.alive=True; self.trail_timer=0
    def update(self):
        self.x+=SNOWBALL_SPEED*self.dir; self.lifetime-=1; self.trail_timer+=1
        if self.lifetime<=0: self.alive=False
        return self.alive
    def get_rect(self):
        return pygame.Rect(int(self.x)-self.RADIUS,int(self.y)-self.RADIUS,self.RADIUS*2,self.RADIUS*2)
    def draw(self, surface, camera, tick):
        if not self.alive: return
        p=camera.apply(self.get_rect())
        gr=self.RADIUS+4+int(math.sin(tick*0.3)*2)
        pygame.draw.circle(surface,(60,80,120),(p.centerx,p.centery),gr)
        pygame.draw.circle(surface,SNOW_WHITE,(p.centerx,p.centery),self.RADIUS)
        pygame.draw.circle(surface,WHITE,(p.centerx-1,p.centery-1),2)

# --- NPC ---
class NPC:
    WIDTH, HEIGHT = 24, 40
    def __init__(self, x, y, dialogue_key, name="Elder Frost"):
        self.rect = pygame.Rect(x, y - self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.dialogue_key = dialogue_key
        self.name = name
        self.talked = False
        self.bob = random.uniform(0, math.pi*2)
        self.proximity_shown = False

    def check_proximity(self, player):
        dx = abs(player.rect.centerx - self.rect.centerx)
        dy = abs(player.rect.centery - self.rect.centery)
        return dx < 60 and dy < 60

    def draw(self, surface, camera, tick):
        sr = camera.apply(self.rect)
        if sr.right < -20 or sr.left > SCREEN_WIDTH + 20: return
        bob = int(math.sin(tick * 0.04 + self.bob) * 2)
        bx, by = sr.x, sr.y + bob
        # Robe
        robe_c = NPC_ROBE if "Elder" in self.name else XMAS_GREEN if "Holly" in self.name else XMAS_RED
        pygame.draw.rect(surface, robe_c, (bx+2, by+14, 20, 26))
        # Hood / head
        pygame.draw.circle(surface, (220,190,160), (bx+12, by+10), 8)
        # Hood
        pygame.draw.arc(surface, robe_c, (bx+2, by, 20, 18), 0.3, 2.8, 3)
        # Eyes
        pygame.draw.circle(surface, WHITE, (bx+9, by+9), 2)
        pygame.draw.circle(surface, WHITE, (bx+15, by+9), 2)
        pygame.draw.circle(surface, BLACK, (bx+9, by+10), 1)
        pygame.draw.circle(surface, BLACK, (bx+15, by+10), 1)
        # Staff
        pygame.draw.line(surface, BROWN, (bx+22, by+5), (bx+22, by+40), 2)
        pygame.draw.circle(surface, XMAS_GOLD, (bx+22, by+4), 4)
        star_pulse = abs(math.sin(tick*0.06))*0.5+0.5
        pygame.draw.circle(surface, lerp_color(XMAS_GOLD, WHITE, star_pulse), (bx+22, by+4), 2)
        # Name tag
        if not self.talked:
            font = pygame.font.SysFont("consolas", 10, bold=True)
            tag = font.render(self.name, True, XMAS_GOLD)
            surface.blit(tag, (bx + 12 - tag.get_width()//2, by - 14))
            # Exclamation mark
            if (tick // 30) % 2 == 0:
                exc = font.render("!", True, XMAS_RED)
                surface.blit(exc, (bx + 12 - exc.get_width()//2, by - 24))
        # Talk prompt
        if self.proximity_shown and not self.talked:
            font2 = pygame.font.SysFont("consolas", 11)
            prompt = font2.render("[E] Talk", True, SNOW_WHITE)
            surface.blit(prompt, (bx + 12 - prompt.get_width()//2, by - 34))

# --- Dialogue Box ---
class DialogueBox:
    def __init__(self, dialogues):
        self.dialogues = dialogues  # list of (speaker, text)
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
        if not self.active or self.done_typing: return
        self.char_timer += self.char_speed
        full_text = self.dialogues[self.index][1]
        self.char_index = min(int(self.char_timer), len(full_text))
        if self.char_index >= len(full_text):
            self.done_typing = True

    def draw(self, surface, tick):
        if not self.active: return
        # Box
        box_h = 130
        box_y = SCREEN_HEIGHT - box_h - 20
        box_rect = pygame.Rect(40, box_y, SCREEN_WIDTH - 80, box_h)
        # Background
        bg = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        bg.fill((10, 10, 28, 220))
        surface.blit(bg, box_rect.topleft)
        # Border with Christmas pattern
        pygame.draw.rect(surface, XMAS_GOLD, box_rect, 2)
        # Corner ornaments
        for cx, cy in [(box_rect.left, box_rect.top), (box_rect.right, box_rect.top),
                       (box_rect.left, box_rect.bottom), (box_rect.right, box_rect.bottom)]:
            pygame.draw.circle(surface, XMAS_RED, (cx, cy), 5)
            pygame.draw.circle(surface, XMAS_GOLD, (cx, cy), 3)
        # Speaker name
        speaker, text = self.dialogues[self.index]
        font_name = pygame.font.SysFont("consolas", 16, bold=True)
        font_text = pygame.font.SysFont("consolas", 14)
        if speaker:
            name_c = XMAS_GOLD if "Elder" in speaker else XMAS_GREEN if "Holly" in speaker else XMAS_RED
            name_surf = font_name.render(speaker, True, name_c)
            surface.blit(name_surf, (box_rect.x + 16, box_rect.y + 10))
            text_y = box_rect.y + 34
        else:
            text_y = box_rect.y + 14
        # Text with typewriter
        shown = text[:self.char_index]
        words = shown.split(" ")
        line = ""
        ly = text_y
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
                surface.blit(prompt, (box_rect.right - prompt.get_width() - 16, box_rect.bottom - 22))
        # Page counter
        pg = font_text.render(f"{self.index+1}/{len(self.dialogues)}", True, DARK_GRAY)
        surface.blit(pg, (box_rect.x + 16, box_rect.bottom - 22))

# --- Player ---
class Player:
    WIDTH, HEIGHT = 28, 36
    def __init__(self, x, y):
        self.rect=pygame.Rect(x,y,self.WIDTH,self.HEIGHT)
        self.vel_x=0.0; self.vel_y=0.0; self.on_ground=False
        self.spawn_x=x; self.spawn_y=y; self.alive=True; self.respawn_timer=0
        self.facing_right=True; self.unreal_timer=0; self.prev_unreal=False
        self.kill_count=0; self.riding_platform=None; self.shoot_cooldown=0
        # Double jump
        self.jump_count=0; self.max_jumps=2
        # Dash
        self.dash_timer=0; self.dash_cooldown=0; self.dash_dir=0; self.dashing=False
        self.dash_afterimages=[]  # list of (x,y,alpha)
        # Health
        self.hearts=PLAYER_MAX_HEARTS; self.invincibility=0; self.death_count=0
        # Ice
        self.on_ice=False
        # Ornaments
        self.ornament_count=0
        # Sprint trail
        self.sprinting=False

    @property
    def is_unreal(self): return self.unreal_timer > 0
    def activate_unreal(self): self.unreal_timer = UNREAL_DURATION
    def set_checkpoint(self, x, y): self.spawn_x=x; self.spawn_y=y
    def take_damage(self):
        if self.is_unreal or self.invincibility > 0: return False
        self.hearts -= 1; self.invincibility = INVINCIBILITY_FRAMES
        if self.hearts <= 0: self.die(); return True
        return True
    def die(self):
        if self.is_unreal: return
        self.alive=False; self.respawn_timer=50; self.death_count+=1
    def respawn(self):
        self.rect.topleft=(self.spawn_x,self.spawn_y)
        self.vel_x=self.vel_y=0; self.alive=True; self.on_ground=False; self.unreal_timer=0
        self.hearts=PLAYER_MAX_HEARTS; self.invincibility=0; self.jump_count=0
        self.dash_timer=0; self.dash_cooldown=0; self.dashing=False
    def start_dash(self):
        if self.dash_cooldown <= 0 and not self.on_ground and not self.dashing and self.alive:
            self.dashing=True; self.dash_timer=DASH_DURATION; self.dash_cooldown=DASH_COOLDOWN
            self.dash_dir=1 if self.facing_right else -1; self.vel_y=0

    def update(self, keys, platforms):
        self.prev_unreal = self.is_unreal
        if not self.alive:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0: self.respawn()
            return None
        if self.unreal_timer > 0: self.unreal_timer -= 1
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.invincibility > 0: self.invincibility -= 1
        if self.dash_cooldown > 0: self.dash_cooldown -= 1
        # Dash logic
        if self.dashing:
            self.dash_timer -= 1
            self.dash_afterimages.append((self.rect.x, self.rect.y, 200))
            if len(self.dash_afterimages) > 8: self.dash_afterimages.pop(0)
            self.rect.x += DASH_SPEED * self.dash_dir; self.vel_y = 0
            if self.dash_timer <= 0: self.dashing = False
            # Collide with platforms horizontally during dash
            for plat in platforms:
                if not plat.is_active(): continue
                pr = plat.get_rect()
                if self.rect.colliderect(pr):
                    if self.dash_dir > 0: self.rect.right = pr.left
                    else: self.rect.left = pr.right
                    self.dashing = False
            return None
        # Fade afterimages
        self.dash_afterimages = [(x, y, a - 30) for x, y, a in self.dash_afterimages if a > 30]
        if self.riding_platform is not None and hasattr(self.riding_platform, 'dx'):
            self.rect.x += self.riding_platform.dx; self.rect.y += self.riding_platform.dy
        move = 0.0
        self.sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed = SPRINT_SPEED if self.sprinting else MOVE_SPEED
        if self.is_unreal: speed += UNREAL_SPEED_BOOST
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move -= speed; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move += speed; self.facing_right = True
        # Ice friction
        friction = 0.12 if self.on_ice else 0.3
        if move: self.vel_x += (move - self.vel_x) * friction
        else: self.vel_x *= (0.96 if self.on_ice else 0.75)
        if abs(self.vel_x) < 0.1: self.vel_x = 0
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        jumped = False
        if self.on_ground and self.jump_count == 0 and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            self.vel_y = JUMP_VELOCITY + (-2 if self.is_unreal else 0)
            self.on_ground = False; self.riding_platform = None; jumped = True
            self.jump_count = 1
        self.on_ice = False  # reset each frame
        self.rect.x += int(self.vel_x)
        for plat in platforms:
            if not plat.is_active(): continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.rect.bottom <= pr.top + 6: continue
                if self.vel_x > 0: self.rect.right = pr.left
                elif self.vel_x < 0: self.rect.left = pr.right
                self.vel_x = 0
        self.on_ground = False; self.riding_platform = None
        vy = int(self.vel_y)
        if self.vel_y > 0 and vy == 0: vy = 1
        self.rect.y += vy
        for plat in platforms:
            if not plat.is_active(): continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.vel_y > 0:
                    self.rect.bottom = pr.top; self.vel_y = 0; self.on_ground = True
                    self.jump_count = 0  # reset jumps on landing
                    if isinstance(plat, MovingPlatform): self.riding_platform = plat
                    plat.on_player_land(self)
                elif self.vel_y < 0: self.rect.top = pr.bottom; self.vel_y = 0
        if self.rect.top > DEATH_Y: self.alive=False; self.respawn_timer=50; self.death_count+=1
        return "jump" if jumped else None

    def try_shoot(self):
        if self.shoot_cooldown <= 0 and self.alive:
            self.shoot_cooldown = SNOWBALL_COOLDOWN
            d = 1 if self.facing_right else -1
            sx = self.rect.right+4 if self.facing_right else self.rect.left-4
            return Snowball(sx, self.rect.centery-2, d)
        return None

    def draw(self, surface, camera, tick):
        if not self.alive: return
        # Invincibility flicker
        if self.invincibility > 0 and (self.invincibility // 4) % 2 == 0: return
        # Dash afterimages
        for ax, ay, aa in self.dash_afterimages:
            ar = camera.apply(pygame.Rect(ax, ay, self.WIDTH, self.HEIGHT))
            s = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            s.fill((*ICE_BLUE, int(aa * 0.5)))
            surface.blit(s, ar.topleft)
        # Sprint trail
        if self.sprinting and self.on_ground and abs(self.vel_x) > 3 and tick % 3 == 0:
            pass  # handled in _spawn_ambient
        sr = camera.apply(self.rect)
        if self.is_unreal:
            bc = xmas_cycle_color(tick, 0.12)
            pygame.draw.rect(surface, bc, sr)
            pulse = abs(math.sin(tick*0.15))*0.5+0.5
            pygame.draw.rect(surface, lerp_color(GOLD,WHITE,pulse), sr.inflate(4,4), 2)
            gs = 6+int(4*pulse)
            pygame.draw.rect(surface, tuple(max(0,min(255,int(c*0.3))) for c in bc), sr.inflate(gs,gs), 3)
        else:
            pygame.draw.rect(surface, XMAS_RED, sr)
            belt_y = sr.y+sr.height-12
            pygame.draw.rect(surface, BLACK, (sr.x,belt_y,sr.width,4))
            pygame.draw.rect(surface, XMAS_GOLD, (sr.centerx-3,belt_y-1,6,6))
            pygame.draw.rect(surface, WHITE, (sr.x,sr.bottom-3,sr.width,3))
        # Santa hat
        ht = sr.y-12
        pygame.draw.polygon(surface, XMAS_RED, [(sr.x+2,sr.y+2),(sr.x+sr.width-2,sr.y+2),(sr.centerx+8,ht)])
        pygame.draw.rect(surface, WHITE, (sr.x,sr.y,sr.width,4))
        pygame.draw.circle(surface, WHITE, (sr.centerx+8, ht-2), 4)
        # Eyes
        ey = sr.y+14; pupil = BLACK if not self.is_unreal else GOLD
        if self.facing_right:
            pygame.draw.rect(surface,WHITE,(sr.x+16,ey,7,7)); pygame.draw.rect(surface,pupil,(sr.x+19,ey+2,4,4))
        else:
            pygame.draw.rect(surface,WHITE,(sr.x+5,ey,7,7)); pygame.draw.rect(surface,pupil,(sr.x+5,ey+2,4,4))

# --- Platforms ---
class Platform:
    def __init__(self, x, y, w, h, color=None):
        self.rect=pygame.Rect(x,y,w,h); self.color=color or (60,90,60)
    def is_active(self): return True
    def get_rect(self): return self.rect
    def on_player_land(self, player): pass
    def update(self): pass
    def draw(self, surface, camera):
        sr=camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        pygame.draw.rect(surface, self.color, sr)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x-2,sr.y-3,sr.width+4,6))
        rng=random.Random(sr.x*31+sr.y*17)
        for bx in range(sr.x, sr.right, 18):
            bw=random.Random(bx+sr.y).randint(8,14)
            pygame.draw.ellipse(surface, WHITE, (bx, sr.y-5, bw, 6))
        for ix in range(sr.x+4, sr.right-4, rng.randint(12,20)):
            il=rng.randint(5,12); iw=rng.randint(2,4)
            pygame.draw.polygon(surface,(180,210,240),[(ix,sr.bottom),(ix+iw,sr.bottom),(ix+iw//2,sr.bottom+il)])

class MovingPlatform(Platform):
    def __init__(self, x1,y1,x2,y2,w,h,speed=1.5,color=None):
        super().__init__(x1,y1,w,h,color or (80,120,80))
        self.sx,self.sy=x1,y1; self.ex,self.ey=x2,y2; self.speed=speed
        self.progress=0.0; self.dir=1; self.dx=0; self.dy=0
    def update(self):
        ox,oy=self.rect.x,self.rect.y
        self.progress+=self.speed*self.dir*0.005
        if self.progress>=1: self.progress=1.0; self.dir=-1
        elif self.progress<=0: self.progress=0.0; self.dir=1
        t=self.progress; s=t*t*(3-2*t)
        self.rect.x=int(self.sx+(self.ex-self.sx)*s)
        self.rect.y=int(self.sy+(self.ey-self.sy)*s)
        self.dx=self.rect.x-ox; self.dy=self.rect.y-oy
    def draw(self, surface, camera):
        sr=camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        pygame.draw.rect(surface, CANDY_WHITE, sr)
        for sx_i in range(0, sr.width, 16):
            x0=sr.x+sx_i
            stripe=pygame.Rect(x0, sr.y, 8, sr.height)
            stripe=stripe.clip(sr)
            if stripe.width>0: pygame.draw.rect(surface, XMAS_RED, stripe)
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x-1,sr.y-2,sr.width+2,4))

class GlitchPlatform(Platform):
    def __init__(self, x,y,w,h,on_time=90,off_time=60,offset=0,color=None):
        super().__init__(x,y,w,h,color or ICE_BLUE)
        self.base_color=self.color; self.on_time=on_time; self.off_time=off_time
        self.timer=offset; self.active=True; self.alpha=255
    def update(self):
        self.timer+=1; cycle=self.on_time+self.off_time; phase=self.timer%cycle
        if phase<self.on_time:
            self.active=True; rem=self.on_time-phase
            if rem<30:
                    self.alpha=128+int(127*(rem/30))
                    if rem<15 and self.timer%4<2: self.alpha=70
            else: self.alpha=255
        else:
            self.active=False; off_e=phase-self.on_time
            self.alpha=25 if off_e<self.off_time-20 else min(25+(off_e-(self.off_time-20))*6,80)
    def is_active(self): return self.active
    def draw(self, surface, camera):
        if self.alpha<=0: return
        sr=camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        f=self.alpha/255; c=tuple(max(0,min(255,int(v*f))) for v in self.base_color)
        pygame.draw.rect(surface,c,sr)
        if self.alpha>80:
            for ix in range(0,sr.width,6):
                if (self.timer+ix)%10<5:
                    pygame.draw.line(surface,tuple(min(v+60,255) for v in c),(sr.x+ix,sr.y),(sr.x+ix,sr.bottom))
        if self.active and self.alpha>150:
            pygame.draw.rect(surface,(int(240*f),int(245*f),int(255*f)),(sr.x,sr.y-2,sr.width,3))

class TeleportPlatform(Platform):
    def __init__(self, x1,y1,x2,y2,w,h,interval=120,color=None):
        super().__init__(x1,y1,w,h,color or (100,60,140))
        self.p1=(x1,y1); self.p2=(x2,y2); self.interval=interval; self.timer=0; self.at1=True; self.flash=0
    def update(self):
        self.timer+=1
        if self.flash>0: self.flash-=1
        if self.timer>=self.interval:
            self.timer=0; self.at1=not self.at1; self.flash=10
            self.rect.topleft=self.p1 if self.at1 else self.p2
    def draw(self, surface, camera):
        sr=camera.apply(self.rect)
        if not (sr.right<-10 or sr.left>SCREEN_WIDTH+10):
            pygame.draw.rect(surface, WHITE if self.flash>0 else self.color, sr)
            if self.interval-self.timer<30 and self.timer%6<3: pygame.draw.rect(surface,XMAS_GOLD,sr,2)
            pygame.draw.rect(surface, SNOW_WHITE, (sr.x,sr.y-2,sr.width,3))
        gp=self.p2 if self.at1 else self.p1
        gr=camera.apply(pygame.Rect(*gp,self.rect.w,self.rect.h))
        pygame.draw.rect(surface,tuple(c//4 for c in self.color),gr)
        pygame.draw.rect(surface,tuple(c//2 for c in self.color),gr,1)

class CollapsingPlatform(Platform):
    def __init__(self, x,y,w,h,delay=45,respawn_time=180,color=None):
        super().__init__(x,y,w,h,color or (150,70,70))
        self.base_color=self.color; self.oy=y; self.delay=delay
        self.respawn_time=respawn_time; self.stood=0; self.collapsed=False; self.rc=0; self.shake=0
    def update(self):
        if self.collapsed:
            self.rc+=1
            if self.rc>=self.respawn_time: self.collapsed=False; self.rc=0; self.stood=0; self.rect.y=self.oy
        elif self.stood>0:
            self.stood+=1; self.shake=(self.stood%4)-2
            if self.stood>=self.delay: self.collapsed=True; self.shake=0
    def is_active(self): return not self.collapsed
    def on_player_land(self, player):
        if not self.collapsed and self.stood==0: self.stood=1
    def draw(self, surface, camera):
        if self.collapsed: return
        dr=self.rect.copy(); dr.x+=self.shake; sr=camera.apply(dr)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        if self.stood>0:
            r=min(self.stood/self.delay,1.0)
            col=(min(255,int(self.base_color[0]+(255-self.base_color[0])*r)),
                 max(0,int(self.base_color[1]*(1-r))), max(0,int(self.base_color[2]*(1-r))))
        else: col=self.base_color
        pygame.draw.rect(surface,col,sr)
        pygame.draw.rect(surface,SNOW_WHITE,(sr.x,sr.y-2,sr.width,3))
        if self.stood>self.delay*0.5:
            pygame.draw.line(surface,BLACK,(sr.centerx-8,sr.y),(sr.centerx+4,sr.bottom),2)

# --- Checkpoint (Christmas Tree) ---
class Checkpoint:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x,y-50,20,50); self.spawn_x=x; self.spawn_y=y-60
        self.activated=False; self.glow=0; self.base_y=y
    def update(self):
        if self.activated: self.glow=(self.glow+3)%360
    def check(self, player):
        if not self.activated and player.rect.colliderect(self.rect):
            self.activated=True; player.set_checkpoint(self.spawn_x,self.spawn_y); return True
        return False
    def draw(self, surface, camera):
        sr=camera.apply(self.rect); cx=sr.centerx; tw,th=6,12
        pygame.draw.rect(surface,BROWN,(cx-tw//2,sr.bottom-th,tw,th))
        tc=XMAS_GREEN if self.activated else XMAS_DARK_GREEN
        for w2,h2,yo in [(28,16,30),(22,14,20),(16,12,10)]:
            ty=sr.bottom-th-yo
            pygame.draw.polygon(surface,tc,[(cx,ty-h2),(cx-w2//2,ty),(cx+w2//2,ty)])
        sy2=sr.bottom-th-10-12-4; sc=XMAS_GOLD if self.activated else DARK_GRAY
        pygame.draw.circle(surface,sc,(cx,sy2),4)
        if self.activated:
            i=abs(math.sin(math.radians(self.glow)))*0.6+0.4
            for j,(ox,oy,oc) in enumerate([(-8,-22,XMAS_RED),(6,-18,XMAS_GOLD),(-5,-32,CYAN),(8,-28,CANDY_PINK),(0,-40,XMAS_GOLD)]):
                if abs(math.sin(math.radians(self.glow+j*60)))>0.3:
                    pygame.draw.circle(surface,oc,(cx+ox,sr.bottom-th+oy),2)
            pygame.draw.rect(surface,tuple(int(v*i) for v in XMAS_GREEN),sr.inflate(8,8),2)
            # Waving flag
            flag_x = cx + 8; flag_y = sr.bottom - th - 10 - 12 - 8
            pygame.draw.line(surface, BROWN, (flag_x, flag_y), (flag_x, flag_y - 16), 2)
            wave = int(math.sin(self.glow * 0.05) * 3)
            pts = [(flag_x, flag_y - 16), (flag_x + 12 + wave, flag_y - 13),
                   (flag_x + 10 + wave, flag_y - 8), (flag_x, flag_y - 6)]
            pygame.draw.polygon(surface, XMAS_RED, pts)

# --- Exit Door (Gift Box) ---
class ExitDoor:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x,y,50,70); self.pulse=0
    def update(self): self.pulse=(self.pulse+3)%360
    def check(self, player): return player.rect.colliderect(self.rect)
    def draw(self, surface, camera):
        sr=camera.apply(self.rect); p=abs(math.sin(math.radians(self.pulse)))
        bc=lerp_color(XMAS_RED,(255,60,60),p*0.3)
        pygame.draw.rect(surface,bc,sr)
        pygame.draw.rect(surface,XMAS_GOLD,(sr.centerx-4,sr.y,8,sr.height))
        pygame.draw.rect(surface,XMAS_GOLD,(sr.x,sr.centery-4,sr.width,8))
        pygame.draw.ellipse(surface,XMAS_GOLD,(sr.centerx-12,sr.y-14,12,10))
        pygame.draw.ellipse(surface,XMAS_GOLD,(sr.centerx,sr.y-14,12,10))
        pygame.draw.circle(surface,(200,160,30),(sr.centerx,sr.y-6),4)
        if int(self.pulse/30)%2==0:
            pygame.draw.circle(surface,WHITE,(sr.x+int(p*sr.width),sr.y+10),2)
        font=pygame.font.SysFont("consolas",11,bold=True)
        lbl=font.render("GIFT",True,WHITE)
        surface.blit(lbl,(sr.centerx-lbl.get_width()//2,sr.bottom-16))
        pygame.draw.rect(surface,lerp_color((80,30,30),(120,50,50),p),sr.inflate(6,6),2)

# --- Monsters ---
class Monster:
    WIDTH, HEIGHT = 26, 26
    def __init__(self, x,y,pl,pr,speed=1.5,color=None):
        self.rect=pygame.Rect(x,y,self.WIDTH,self.HEIGHT)
        self.pl,self.pr=pl,pr; self.speed=speed; self.dir=1
        self.color=color or SNOW_WHITE; self.alive=True; self.death_timer=0; self.bob=0
    def update(self):
        if not self.alive: self.death_timer-=1; return
        self.rect.x+=int(self.speed*self.dir)
        if self.rect.x>=self.pr: self.rect.x=self.pr; self.dir=-1
        elif self.rect.x<=self.pl: self.rect.x=self.pl; self.dir=1
        self.bob+=0.12
    def kill(self): self.alive=False; self.death_timer=1
    def check_collision(self, player):
        if not self.alive or not player.alive: return None
        if not self.rect.colliderect(player.rect): return None
        return "kill_monster" if player.is_unreal else "kill_player"
    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr=camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        bo=int(math.sin(self.bob)*2); b=pygame.Rect(sr.x,sr.y+bo,sr.w,sr.h)
        pygame.draw.rect(surface,SNOW_WHITE,b)
        pygame.draw.rect(surface,XMAS_RED,(b.x,b.y+b.height//2,b.width,4))
        for sx in range(b.x+2,b.right-2,6):
            pygame.draw.polygon(surface,ICE_BLUE,[(sx,b.y),(sx+3,b.y-6),(sx+6,b.y)])
        ey=b.y+8
        pygame.draw.rect(surface,BLACK,(b.x+4,ey,6,5)); pygame.draw.rect(surface,BLACK,(b.x+16,ey,6,5))
        pygame.draw.rect(surface,RED,(b.x+6,ey+2,3,3)); pygame.draw.rect(surface,RED,(b.x+18,ey+2,3,3))
        pygame.draw.line(surface,BLACK,(b.x+3,ey-2),(b.x+10,ey),2)
        pygame.draw.line(surface,BLACK,(b.right-3,ey-2),(b.right-10,ey),2)

class FlyingMonster:
    WIDTH, HEIGHT = 30, 22
    def __init__(self, x,y,pl,pr,speed=1.2,amplitude=40,color=None):
        self.bx,self.by=float(x),y; self.rect=pygame.Rect(x,y,self.WIDTH,self.HEIGHT)
        self.pl,self.pr=pl,pr; self.speed=speed; self.amplitude=amplitude; self.dir=1
        self.color=color or CANDY_PINK; self.alive=True; self.death_timer=0
        self.phase=random.uniform(0,math.pi*2); self.tick=0
    def update(self):
        if not self.alive: self.death_timer-=1; return
        self.tick+=1; self.bx+=self.speed*self.dir
        if self.bx>=self.pr: self.bx=self.pr; self.dir=-1
        elif self.bx<=self.pl: self.bx=self.pl; self.dir=1
        self.rect.x=int(self.bx)
        self.rect.y=int(self.by+math.sin(self.tick*0.04+self.phase)*self.amplitude)
    def kill(self): self.alive=False; self.death_timer=1
    def check_collision(self, player):
        if not self.alive or not player.alive: return None
        if not self.rect.colliderect(player.rect): return None
        return "kill_monster" if player.is_unreal else "kill_player"
    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr=camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        pygame.draw.ellipse(surface,self.color,sr)
        pygame.draw.arc(surface,GRAY,(sr.centerx-4,sr.y-8,8,10),0,math.pi,2)
        wy=sr.centery-2+int(math.sin(tick*0.3)*3)
        pygame.draw.polygon(surface,self.color,[(sr.left,wy),(sr.left-10,wy-8),(sr.left+5,wy)])
        pygame.draw.polygon(surface,self.color,[(sr.right,wy),(sr.right+10,wy-8),(sr.right-5,wy)])
        ey=sr.y+6; ex=sr.x+16 if self.dir>=0 else sr.x+8
        pygame.draw.rect(surface,WHITE,(ex,ey,6,5)); pygame.draw.rect(surface,BLACK,(ex+2,ey+1,3,3))

class MushroomMonster:
    WIDTH, HEIGHT = 28, 28
    def __init__(self, x,y,pl,pr,speed=1.3):
        self.rect=pygame.Rect(x,y,self.WIDTH,self.HEIGHT)
        self.patrol_left=pl; self.patrol_right=pr; self.speed=speed; self.direction=1
        self.alive=True; self.death_timer=0; self.squish_timer=0; self.tick=0
    def update(self):
        if not self.alive: self.death_timer-=1; return
        if self.squish_timer>0:
            self.squish_timer-=1
            if self.squish_timer<=0: self.alive=False; self.death_timer=1
            return
        self.tick+=1; self.rect.x+=int(self.speed*self.direction)
        if self.rect.x>=self.patrol_right: self.rect.x=self.patrol_right; self.direction=-1
        elif self.rect.x<=self.patrol_left: self.rect.x=self.patrol_left; self.direction=1
    def kill(self): self.alive=False; self.death_timer=1
    def stomp(self): self.squish_timer=12
    def check_collision(self, player):
        if not self.alive or self.squish_timer>0 or not player.alive: return None
        if not self.rect.colliderect(player.rect): return None
        if player.is_unreal: return "kill_monster"
        if player.vel_y>0 and player.rect.bottom<=self.rect.centery+6: return "stomp"
        return "kill_player"
    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr=camera.apply(self.rect)
        if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
        if self.squish_timer>0:
            flat=pygame.Rect(sr.x-4,sr.bottom-8,sr.width+8,8)
            pygame.draw.rect(surface,BROWN,flat)
            pygame.draw.ellipse(surface,MUSHROOM_RED,(flat.x,flat.y-4,flat.width,8)); return
        bob=int(math.sin(self.tick*0.2)*1.5)
        pygame.draw.rect(surface,BROWN,(sr.x+4,sr.centery+bob,sr.width-8,sr.height//2))
        cr=pygame.Rect(sr.x-2,sr.y+bob,sr.width+4,sr.height//2+4)
        pygame.draw.ellipse(surface,MUSHROOM_RED,cr)
        for sx2,sy2,r2 in [(cr.x+6,cr.y+5,3),(cr.right-8,cr.y+4,3),(cr.centerx,cr.y+2,2)]:
            pygame.draw.circle(surface,WHITE,(sx2,sy2+bob),r2)
        pygame.draw.ellipse(surface,DARK_BROWN,(sr.x+2,sr.bottom+bob-4,8,5))
        pygame.draw.ellipse(surface,DARK_BROWN,(sr.right-10,sr.bottom+bob-4,8,5))
        ey2=sr.centery-2+bob
        pygame.draw.circle(surface,WHITE,(sr.x+8,ey2),4); pygame.draw.circle(surface,WHITE,(sr.right-8,ey2),4)
        po=1 if self.direction>0 else -1
        pygame.draw.circle(surface,BLACK,(sr.x+8+po,ey2+1),2); pygame.draw.circle(surface,BLACK,(sr.right-8+po,ey2+1),2)

# --- Bomb Monster ---
class BombMonster:
    WIDTH, HEIGHT = 30, 30
    def __init__(self, x, y, pl, pr, speed=1.0, diff=None):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.patrol_left = pl; self.patrol_right = pr
        diff = diff or DIFFICULTY["hard"]
        self.base_speed = speed * diff["bomb_spd"]
        self.speed = self.base_speed
        self.direction = 1; self.alive = True; self.death_timer = 0; self.tick = 0
        self.state = "patrol"  # patrol / ticking / exploding / defused
        self.fuse_timer = 0; self.fuse_max = diff["bomb_fuse"]
        self.hits = 0; self.hits_to_kill = diff["bomb_hits"]
        self.detect_range = diff["bomb_detect"]
        self.explode_timer = 0; self.flash_rate = 10
        self.charge_dir = 0  # direction to charge toward player when ticking
        self.dodge_timer = 0; self.dodge_dir = 0

    def update(self):
        if not self.alive: self.death_timer -= 1; return
        self.tick += 1
        if self.state == "defused":
            self.death_timer -= 1
            if self.death_timer <= 0: self.alive = False
            return
        if self.state == "exploding":
            self.explode_timer -= 1
            if self.explode_timer <= 0: self.alive = False; self.death_timer = 1
            return
        if self.state == "ticking":
            self.fuse_timer += 1
            progress = self.fuse_timer / self.fuse_max
            self.flash_rate = max(2, int(10 * (1 - progress)))
            # Aggressive movement: charge toward player, dodge sideways
            charge_spd = self.base_speed * (1.5 + progress * 1.5)  # gets faster as fuse runs out
            if self.hits >= 1:
                charge_spd *= 0.6  # slow a bit if hit once
            # Dodge sideways randomly
            if self.dodge_timer > 0:
                self.dodge_timer -= 1
                self.rect.x += int(self.dodge_dir * charge_spd * 0.5)
            else:
                self.rect.x += int(charge_spd * self.charge_dir)
            # Keep in bounds
            if self.rect.x > self.patrol_right + 80: self.rect.x = self.patrol_right + 80
            elif self.rect.x < self.patrol_left - 80: self.rect.x = self.patrol_left - 80
            # Random dodge
            if random.random() < 0.02 and self.dodge_timer <= 0:
                self.dodge_timer = 15
                self.dodge_dir = random.choice([-1, 1])
            if self.fuse_timer >= self.fuse_max:
                self.state = "exploding"; self.explode_timer = 30
            return
        # Patrol - normal movement
        self.rect.x += int(self.speed * self.direction)
        if self.rect.x >= self.patrol_right: self.rect.x = self.patrol_right; self.direction = -1
        elif self.rect.x <= self.patrol_left: self.rect.x = self.patrol_left; self.direction = 1

    def start_ticking(self, player_x):
        if self.state == "patrol":
            self.state = "ticking"; self.fuse_timer = 0
            self.charge_dir = 1 if player_x > self.rect.centerx else -1

    def hit_by_snowball(self):
        if self.state not in ("patrol", "ticking"): return None
        if self.state == "patrol": self.state = "ticking"; self.fuse_timer = 0
        self.hits += 1
        # Random dodge on hit
        self.dodge_timer = 20; self.dodge_dir = random.choice([-1, 1])
        if self.hits >= self.hits_to_kill:
            self.state = "defused"; self.death_timer = 20; return "defused"
        return "hit"

    def kill(self): self.alive = False; self.death_timer = 1

    def check_collision(self, player):
        if not self.alive or not player.alive or self.state == "defused": return None
        if self.state == "exploding":
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            if math.sqrt(dx*dx+dy*dy) < BOMB_EXPLODE_RADIUS:
                return None if player.is_unreal else "kill_player"
            return None
        if not self.rect.colliderect(player.rect): return None
        return "kill_monster" if player.is_unreal else "kill_player"

    def check_proximity(self, player):
        if self.state != "patrol" or not self.alive: return
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        if math.sqrt(dx*dx+dy*dy) < self.detect_range:
            self.start_ticking(player.rect.centerx)

    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        cx, cy = sr.centerx, sr.centery; br = sr.width // 2

        if self.state == "defused":
            a = max(0.2, self.death_timer / 20)
            pygame.draw.circle(surface, tuple(int(v*a) for v in BOMB_GRAY), (cx, cy), br)
            for dx2,s2 in [(-5,-1),(5,-1),(-5,1),(5,1)]:
                pygame.draw.line(surface, WHITE, (cx+dx2-2, cy+s2-2), (cx+dx2+2, cy+s2+2), 2)
            return

        if self.state == "exploding":
            prog = 1 - (self.explode_timer / 30); r = int(BOMB_EXPLODE_RADIUS * prog)
            for i in range(3):
                er = max(1, r - i * 20)
                ec = lerp_color(FUSE_RED, XMAS_GOLD, prog * 0.5 + i * 0.15)
                ea = max(30, int(255 * (1 - prog)))
                pygame.draw.circle(surface, tuple(max(0, min(255, int(c*ea/255))) for c in ec), (cx, cy), er)
            if self.explode_timer > 15:
                pygame.draw.circle(surface, WHITE, (cx, cy), int(r * 0.3))
            return

        bob = int(math.sin(self.tick * 0.15) * 2)
        cy += bob
        body_c = BOMB_BLACK
        if self.state == "ticking" and (self.tick // self.flash_rate) % 2 == 0:
            body_c = lerp_color(BOMB_BLACK, FUSE_RED, (self.fuse_timer / self.fuse_max) * 0.8)

        pygame.draw.ellipse(surface, (20, 20, 20), (cx - br, sr.bottom + 2, br * 2, 6))
        pygame.draw.circle(surface, body_c, (cx, cy), br)
        pygame.draw.circle(surface, BOMB_GRAY, (cx - 4, cy - 4), br // 3)

        fuse_base = (cx + 2, cy - br + 2); fuse_tip = (cx + 8, cy - br - 10)
        pygame.draw.line(surface, BROWN, fuse_base, fuse_tip, 2)
        if self.state == "ticking":
            sc = FUSE_ORANGE if (tick // 3) % 2 == 0 else FUSE_RED
            pygame.draw.circle(surface, sc, fuse_tip, 4)
            pygame.draw.circle(surface, XMAS_GOLD, fuse_tip, 2)
        else:
            pygame.draw.circle(surface, DARK_GRAY, fuse_tip, 2)

        ey = cy - 2
        if self.state == "ticking":
            pygame.draw.rect(surface, FUSE_RED, (cx-8,ey,5,4))
            pygame.draw.rect(surface, FUSE_RED, (cx+3,ey,5,4))
            pygame.draw.line(surface, FUSE_RED, (cx-9,ey-3), (cx-3,ey-1), 2)
            pygame.draw.line(surface, FUSE_RED, (cx+9,ey-3), (cx+3,ey-1), 2)
        else:
            pygame.draw.rect(surface, WHITE, (cx-8,ey,5,5))
            pygame.draw.rect(surface, WHITE, (cx+3,ey,5,5))
            pygame.draw.rect(surface, BLACK, (cx-7,ey+1,3,3))
            pygame.draw.rect(surface, BLACK, (cx+4,ey+1,3,3))

        if self.hits >= 1:
            pygame.draw.line(surface, DARK_GRAY, (cx-3,cy-br+5), (cx+2,cy-2), 2)
            pygame.draw.line(surface, DARK_GRAY, (cx+2,cy-2), (cx-1,cy+5), 2)

        if self.state == "ticking" and self.fuse_timer < 60 and (tick//20)%2==0:
            font = pygame.font.SysFont("consolas", 9, bold=True)
            hint = font.render(f"SHOOT x{self.hits_to_kill - self.hits}!", True, FUSE_RED)
            surface.blit(hint, (cx - hint.get_width()//2, cy - br - 22))

# --- Powerup (Christmas Ornament) ---
class Powerup:
    RADIUS = 12
    def __init__(self, x, y, respawn_time=600):
        self.x,self.y=x,y
        self.rect=pygame.Rect(x-self.RADIUS,y-self.RADIUS,self.RADIUS*2,self.RADIUS*2)
        self.collected=False; self.respawn_time=respawn_time; self.rc=0; self.tick=random.randint(0,360)
    def update(self):
        self.tick+=1
        if self.collected:
            self.rc+=1
            if self.rc>=self.respawn_time: self.collected=False; self.rc=0
    def check(self, player):
        if self.collected or not player.alive: return False
        if self.rect.colliderect(player.rect): self.collected=True; self.rc=0; return True
        return False
    def draw(self, surface, camera, tick):
        if self.collected: return
        bob=math.sin(self.tick*0.06)*5; cx2,cy2=self.x,self.y+int(bob)
        pos=camera.apply(pygame.Rect(cx2-1,cy2-1,2,2)); sx,sy=pos.x,pos.y
        if sx<-30 or sx>SCREEN_WIDTH+30: return
        pulse=abs(math.sin(self.tick*0.08))*0.4+0.6
        pygame.draw.circle(surface,tuple(max(0,min(255,int(c*0.3*pulse))) for c in XMAS_GOLD),(sx,sy),int(self.RADIUS*2*pulse))
        pygame.draw.circle(surface,xmas_cycle_color(self.tick,0.03),(sx,sy),self.RADIUS)
        pygame.draw.line(surface,GRAY,(sx,sy-self.RADIUS),(sx,sy-self.RADIUS-6),2)
        pygame.draw.arc(surface,GRAY,(sx-4,sy-self.RADIUS-10,8,8),0,math.pi,2)
        pygame.draw.circle(surface,WHITE,(sx-3,sy-3),3)
        a2=self.tick*0.08
        pygame.draw.rect(surface,xmas_cycle_color(self.tick,0.15),
            (sx+int(math.cos(a2)*(self.RADIUS+6))-2,sy+int(math.sin(a2)*(self.RADIUS+6))-2,4,4))

# --- Collectible Ornament ---
class Ornament:
    RADIUS = 7
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rect = pygame.Rect(x - self.RADIUS, y - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)
        self.collected = False; self.tick = random.randint(0, 360)
        self.color = random.choice([XMAS_RED, XMAS_GREEN, XMAS_GOLD, CYAN, CANDY_PINK])
    def update(self): self.tick += 1
    def check(self, player):
        if self.collected or not player.alive: return False
        if self.rect.colliderect(player.rect): self.collected = True; return True
        return False
    def draw(self, surface, camera, tick):
        if self.collected: return
        bob = math.sin(self.tick * 0.07) * 4
        pos = camera.apply(pygame.Rect(self.x - 1, int(self.y + bob) - 1, 2, 2))
        sx, sy = pos.x, pos.y
        if sx < -20 or sx > SCREEN_WIDTH + 20: return
        pygame.draw.line(surface, GRAY, (sx, sy - self.RADIUS), (sx, sy - self.RADIUS - 4), 1)
        pygame.draw.circle(surface, self.color, (sx, sy), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (sx - 2, sy - 2), 2)

# --- Heart Pickup ---
class HeartPickup:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
        self.collected = False; self.tick = random.randint(0, 360)
    def update(self): self.tick += 1
    def check(self, player):
        if self.collected or not player.alive: return False
        if self.rect.colliderect(player.rect) and player.hearts < PLAYER_MAX_HEARTS:
            self.collected = True; return True
        return False
    def draw(self, surface, camera, tick):
        if self.collected: return
        bob = math.sin(self.tick * 0.06) * 3
        pos = camera.apply(pygame.Rect(self.x - 1, int(self.y + bob) - 1, 2, 2))
        sx, sy = pos.x, pos.y
        if sx < -20 or sx > SCREEN_WIDTH + 20: return
        # Draw heart shape
        pygame.draw.circle(surface, XMAS_RED, (sx - 4, sy - 2), 5)
        pygame.draw.circle(surface, XMAS_RED, (sx + 4, sy - 2), 5)
        pygame.draw.polygon(surface, XMAS_RED, [(sx - 9, sy), (sx, sy + 8), (sx + 9, sy)])
        pygame.draw.circle(surface, WHITE, (sx - 3, sy - 3), 2)

# --- Ice Platform ---
class IcePlatform(Platform):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, color=(160, 210, 240))
    def on_player_land(self, player): player.on_ice = True
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pygame.draw.rect(surface, self.color, sr)
        pygame.draw.rect(surface, (200, 230, 255), (sr.x, sr.y, sr.width, 3))
        # Ice streaks
        for ix in range(sr.x + 8, sr.right - 8, 14):
            pygame.draw.line(surface, (200, 230, 255), (ix, sr.y + 4), (ix + 6, sr.bottom - 2), 1)

# --- Falling Icicle ---
class Icicle:
    WIDTH, HEIGHT = 10, 30
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rect = pygame.Rect(x - self.WIDTH // 2, y, self.WIDTH, self.HEIGHT)
        self.state = "idle"  # idle / shaking / falling / done
        self.shake_timer = 0; self.fall_speed = 0
    def update(self):
        if self.state == "shaking":
            self.shake_timer -= 1
            if self.shake_timer <= 0: self.state = "falling"; self.fall_speed = 2
        elif self.state == "falling":
            self.fall_speed = min(self.fall_speed + 0.4, ICICLE_FALL_SPEED)
            self.rect.y += int(self.fall_speed)
            if self.rect.y > DEATH_Y: self.state = "done"
    def trigger(self):
        if self.state == "idle": self.state = "shaking"; self.shake_timer = ICICLE_SHAKE_TIME
    def check_player_below(self, player):
        if self.state != "idle" or not player.alive: return
        if abs(player.rect.centerx - self.rect.centerx) < 50 and player.rect.top > self.rect.bottom:
            self.trigger()
    def check_hit(self, player):
        if self.state != "falling" or not player.alive: return False
        return self.rect.colliderect(player.rect)
    def draw(self, surface, camera, tick):
        if self.state == "done": return
        sx = self.rect.x + (random.randint(-2, 2) if self.state == "shaking" else 0)
        r = pygame.Rect(sx, self.rect.y, self.WIDTH, self.HEIGHT)
        sr = camera.apply(r)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        pts = [(sr.x, sr.y), (sr.right, sr.y), (sr.centerx, sr.bottom)]
        pygame.draw.polygon(surface, (180, 220, 250), pts)
        pygame.draw.polygon(surface, (210, 240, 255), pts, 1)

# --- Boss Icicle Projectile ---
class BossIcicle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 4, y, 8, 20)
        self.alive = True; self.speed = 4 + random.uniform(0, 2)
    def update(self):
        self.rect.y += int(self.speed)
        if self.rect.y > DEATH_Y: self.alive = False
        return self.alive
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        pygame.draw.polygon(surface, (180, 220, 250), [(sr.x, sr.y), (sr.right, sr.y), (sr.centerx, sr.bottom)])

# --- Boss Monster ---
class BossMonster:
    WIDTH, HEIGHT = 80, 100
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y - self.HEIGHT, self.WIDTH, self.HEIGHT)
        self.hp = BOSS_MAX_HP; self.alive = True; self.tick = 0
        self.attack_timer = 0; self.attack_interval = 80
        self.projectiles = []; self.flash_timer = 0
        self.phase = 1  # gets harder at low hp
    def update(self):
        if not self.alive: return
        self.tick += 1
        if self.flash_timer > 0: self.flash_timer -= 1
        if self.hp <= BOSS_MAX_HP // 2: self.phase = 2; self.attack_interval = 50
        self.attack_timer += 1
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            n = 3 if self.phase == 1 else 5
            for i in range(n):
                ox = self.rect.x + random.randint(0, self.WIDTH)
                self.projectiles.append(BossIcicle(ox, self.rect.top - 10))
        self.projectiles = [p for p in self.projectiles if p.update()]
    def hit(self):
        if not self.alive: return False
        self.hp -= 1; self.flash_timer = 10
        if self.hp <= 0: self.alive = False
        return True
    def check_projectile_hit(self, player):
        if not player.alive: return False
        for p in self.projectiles:
            if p.alive and p.rect.colliderect(player.rect):
                p.alive = False; return True
        return False
    def draw(self, surface, camera, tick):
        if not self.alive: return
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        # Body - ice golem
        bc = WHITE if self.flash_timer > 0 and self.flash_timer % 4 < 2 else (200, 220, 240)
        pygame.draw.ellipse(surface, bc, (sr.x, sr.y + 30, sr.width, sr.height - 30))
        pygame.draw.ellipse(surface, bc, (sr.x + 10, sr.y + 10, sr.width - 20, 50))
        pygame.draw.circle(surface, bc, (sr.centerx, sr.y + 15), 22)
        # Eyes
        pygame.draw.circle(surface, CYAN, (sr.centerx - 8, sr.y + 12), 5)
        pygame.draw.circle(surface, CYAN, (sr.centerx + 8, sr.y + 12), 5)
        pygame.draw.circle(surface, DARK_SKY, (sr.centerx - 8, sr.y + 13), 3)
        pygame.draw.circle(surface, DARK_SKY, (sr.centerx + 8, sr.y + 13), 3)
        # Icicle crown
        for i in range(-2, 3):
            bx = sr.centerx + i * 10
            pygame.draw.polygon(surface, ICE_BLUE, [(bx - 3, sr.y + 5), (bx + 3, sr.y + 5), (bx, sr.y - 10 - abs(i) * 3)])
        # Health bar
        bar_w = sr.width + 20; bar_x = sr.centerx - bar_w // 2; bar_y = sr.y - 25
        pygame.draw.rect(surface, DARK_GRAY, (bar_x - 1, bar_y - 1, bar_w + 2, 12))
        ratio = max(0, self.hp / BOSS_MAX_HP)
        hc = XMAS_GREEN if ratio > 0.5 else XMAS_GOLD if ratio > 0.25 else XMAS_RED
        pygame.draw.rect(surface, hc, (bar_x, bar_y, int(bar_w * ratio), 10))
        pygame.draw.rect(surface, WHITE, (bar_x - 1, bar_y - 1, bar_w + 2, 12), 1)
        font = pygame.font.SysFont("consolas", 10, bold=True)
        label = font.render(f"ICE GOLEM  {self.hp}/{BOSS_MAX_HP}", True, WHITE)
        surface.blit(label, (bar_x + bar_w // 2 - label.get_width() // 2, bar_y - 1))
        # Projectiles
        for p in self.projectiles: p.draw(surface, camera)

def draw_christmas_lights(surface, camera, rect, tick):
    sr=camera.apply(rect)
    if sr.right<-10 or sr.left>SCREEN_WIDTH+10: return
    lcs=[XMAS_RED,XMAS_GREEN,XMAS_GOLD,CYAN,CANDY_PINK]; sp=16; sag=4
    for i,lx in enumerate(range(sr.x+6,sr.right-6,sp)):
        ly=sr.bottom+sag+int(math.sin(i*0.8)*2)
        if i>0:
            px=lx-sp; py=sr.bottom+sag+int(math.sin((i-1)*0.8)*2)
            pygame.draw.line(surface,(40,60,40),(px,py),(lx,ly),1)
        c=lcs[i%len(lcs)]
        if abs(math.sin(tick*0.05+i*1.2))>0.2:
            pygame.draw.circle(surface,c,(lx,ly),3)
            pygame.draw.circle(surface,tuple(max(0,min(255,int(v*0.4))) for v in c),(lx,ly),6)

# --- Level Builder ---
def create_level(diff_key="hard"):
    diff = DIFFICULTY[diff_key]
    plats, cps, mons, pws, npcs = [], [], [], [], []
    ornaments, icicles, heart_pickups = [], [], []
    ms = diff["mon_spd"]
    ps = diff["plat_spd"]
    go = diff["glitch_on"]
    gf = diff["glitch_off"]
    cd = diff["collapse_delay"]
    ti = diff["tp_interval"]

    # Section 1: Snowy Intro
    plats.append(Platform(0, 500, 400, 40))
    npcs.append(NPC(80, 500, "intro", "Elder Frost"))
    plats.append(Platform(500, 500, 160, 40))
    plats.append(Platform(760, 455, 160, 40))
    plats.append(Platform(1020, 410, 160, 40))
    plats.append(Platform(1270, 455, 200, 40))
    plats.append(Platform(1560, 500, 300, 40))
    mons.append(MushroomMonster(200, 472, 50, 370, speed=1.0*ms))
    mons.append(Monster(1580, 474, 1560, 1830, speed=1.2*ms))
    mons.append(BombMonster(700, 470, 500, 650, speed=0.8, diff=diff))
    cps.append(Checkpoint(1610, 500))
    npcs.append(NPC(1650, 500, "cp1", "Holly"))

    # Section 2: Icy platforms
    plats.append(Platform(1960, 460, 120, 30))
    plats.append(GlitchPlatform(2170, 420, 120, 30, on_time=go+10, off_time=gf, offset=0))
    plats.append(GlitchPlatform(2390, 375, 120, 30, on_time=go, off_time=gf, offset=40))
    plats.append(Platform(2610, 420, 100, 30))
    plats.append(GlitchPlatform(2800, 375, 130, 30, on_time=go-5, off_time=gf-5, offset=20))
    plats.append(GlitchPlatform(3010, 330, 120, 30, on_time=go+10, off_time=gf-10, offset=60))
    plats.append(Platform(3220, 375, 160, 30))
    mons.append(MushroomMonster(1970, 432, 1960, 2060, speed=1.1*ms))
    mons.append(Monster(2620, 394, 2610, 2700, speed=1.0*ms))
    mons.append(FlyingMonster(2400, 320, 2200, 2600, speed=0.8*ms, amplitude=30))
    mons.append(BombMonster(2830, 345, 2800, 2920, speed=0.7, diff=diff))
    pws.append(Powerup(2000, 430))
    cps.append(Checkpoint(3250, 375))
    npcs.append(NPC(3280, 375, "cp2", "Jingle"))

    # Section 3: Moving platforms
    plats.append(MovingPlatform(3500, 400, 3700, 400, 120, 30, speed=1.2*ps))
    plats.append(Platform(3850, 360, 100, 30))
    plats.append(MovingPlatform(4030, 320, 4030, 450, 120, 30, speed=1.0*ps))
    plats.append(MovingPlatform(4250, 380, 4450, 380, 130, 30, speed=1.5*ps))
    plats.append(Platform(4600, 420, 100, 30))
    plats.append(MovingPlatform(4770, 350, 4770, 240, 110, 30, speed=0.8*ps))
    plats.append(MovingPlatform(4950, 290, 5150, 290, 120, 30, speed=1.3*ps))
    plats.append(Platform(5300, 350, 200, 30))
    mons.append(Monster(3860, 334, 3850, 3940, speed=1.3*ms))
    mons.append(MushroomMonster(4610, 392, 4600, 4690, speed=1.4*ms))
    mons.append(FlyingMonster(4400, 300, 4250, 4550, speed=1.0*ms, amplitude=35))
    mons.append(BombMonster(5320, 320, 5300, 5480, speed=0.9, diff=diff))
    pws.append(Powerup(4400, 340))
    cps.append(Checkpoint(5320, 350))
    npcs.append(NPC(5360, 350, "cp3", "Elder Frost"))

    # Section 4: Teleport challenge
    plats.append(TeleportPlatform(5550, 350, 5550, 250, 120, 30, interval=ti+20))
    plats.append(CollapsingPlatform(5770, 300, 120, 30, delay=cd+10))
    plats.append(GlitchPlatform(5980, 350, 110, 30, on_time=go-10, off_time=gf-10, offset=0))
    plats.append(TeleportPlatform(6170, 300, 6260, 400, 120, 30, interval=ti))
    plats.append(CollapsingPlatform(6440, 350, 100, 30, delay=cd))
    plats.append(CollapsingPlatform(6610, 300, 100, 30, delay=cd))
    plats.append(Platform(6790, 350, 120, 30))
    plats.append(TeleportPlatform(6980, 300, 6980, 400, 100, 30, interval=ti-10))
    plats.append(Platform(7160, 350, 200, 40))
    mons.append(FlyingMonster(5800, 250, 5550, 6000, speed=1.3*ms, amplitude=40))
    mons.append(MushroomMonster(6800, 322, 6790, 6900, speed=1.6*ms))
    mons.append(FlyingMonster(6500, 260, 6400, 6700, speed=1.1*ms, amplitude=35))
    mons.append(BombMonster(6450, 320, 6440, 6600, speed=0.8, diff=diff))
    pws.append(Powerup(6820, 310))
    cps.append(Checkpoint(7180, 350))
    npcs.append(NPC(7200, 350, "cp4", "Holly"))

    # Section 5: Final gauntlet
    plats.append(GlitchPlatform(7460, 320, 100, 30, on_time=go-15, off_time=gf-10, offset=0))
    plats.append(MovingPlatform(7640, 280, 7640, 390, 100, 30, speed=1.4*ps))
    plats.append(CollapsingPlatform(7840, 320, 90, 30, delay=cd-5))
    plats.append(GlitchPlatform(8010, 280, 100, 30, on_time=go-10, off_time=gf-5, offset=30))
    plats.append(TeleportPlatform(8200, 320, 8280, 240, 110, 30, interval=ti-10))
    plats.append(MovingPlatform(8440, 280, 8600, 280, 100, 30, speed=1.8*ps))
    plats.append(CollapsingPlatform(8730, 320, 100, 30, delay=cd-8))
    plats.append(GlitchPlatform(8900, 280, 110, 30, on_time=go, off_time=gf-20, offset=10))
    plats.append(Platform(9060, 350, 220, 40))
    mons.append(FlyingMonster(7700, 240, 7500, 7900, speed=1.5*ms, amplitude=45))
    mons.append(MushroomMonster(9080, 322, 9060, 9260, speed=1.8*ms))
    mons.append(FlyingMonster(8500, 220, 8300, 8700, speed=1.4*ms, amplitude=40))
    mons.append(BombMonster(8750, 290, 8730, 8900, speed=1.0, diff=diff))
    mons.append(BombMonster(9100, 320, 9060, 9260, speed=0.6, diff=diff))
    pws.append(Powerup(7500, 280))

    # Ice Platforms (Sections 2-3)
    plats.append(IcePlatform(2610, 420, 100, 30))  # replace or add alongside
    plats.append(IcePlatform(3220, 375, 160, 30))
    plats.append(IcePlatform(3850, 360, 100, 30))
    plats.append(IcePlatform(4600, 420, 100, 30))

    # Ornaments (~18 scattered throughout)
    orn_positions = [
        (250, 470), (550, 470), (800, 420), (1100, 380), (1350, 420),  # Sec 1
        (2000, 430), (2250, 390), (2500, 340), (2700, 390), (3100, 300),  # Sec 2
        (3600, 370), (3900, 330), (4300, 350), (4700, 390), (5100, 260),  # Sec 3
        (5650, 320), (6500, 320), (6900, 310),  # Sec 4
    ]
    for ox, oy in orn_positions:
        ornaments.append(Ornament(ox, oy))

    # Icicles (~10 placed at ceilings)
    icicle_xs = [600, 1200, 2300, 2900, 3700, 4500, 5800, 6300, 7000, 8100]
    for ix in icicle_xs:
        icicles.append(Icicle(ix, 80))

    # Heart pickups (3-4 placed in level)
    heart_pickups.append(HeartPickup(1800, 440))
    heart_pickups.append(HeartPickup(4100, 300))
    heart_pickups.append(HeartPickup(6100, 280))
    heart_pickups.append(HeartPickup(8500, 260))

    # Boss Monster near exit in Section 5
    boss = BossMonster(9000, 350)

    # Boss arena platform (wider)
    plats.append(Platform(8900, 350, 350, 40))

    exit_door = ExitDoor(9180, 280)
    return plats, cps, mons, pws, exit_door, npcs, ornaments, icicles, heart_pickups, boss


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        if self.screen is None or self.screen.get_size() != (SCREEN_WIDTH, SCREEN_HEIGHT):
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Endless Dream - The Final Realm")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 48)
        self.tiny_font = pygame.font.SysFont("consolas", 12, bold=True)
        self.title_font = pygame.font.SysFont("consolas", 36, bold=True)
        self.sfx = SoundManager()
        self.state = "playing"  # playing / settings / win / dialogue / ending
        self.current_level = 0; self.level_time = 0; self.tick = 0; self.win_timer = 0
        self.difficulty = "hard"
        self.music_volume = 0.5; self.music_muted = False; self.settings_cursor = 0
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = []; self.rings = []; self.flashes = []
        self.score_popups = []; self.snowballs = []
        self.snowflakes = [Snowflake() for _ in range(150)]
        self.bg_stars = [BGStar() for _ in range(80)]
        self.platforms = []; self.checkpoints = []; self.monsters = []
        self.powerups = []; self.npcs = []; self.exit_door = None
        self.ornaments = []; self.icicles = []; self.heart_pickups = []; self.boss = None
        self.boss_defeated = False
        self.player = Player(100, 400)
        self.dialogue_box = None
        self.pending_state = None  # state to return to after dialogue
        self.ending_shown = False
        self.load_level()
        self.sfx.start_music(volume=self.music_volume)

    def load_level(self):
        (self.platforms, self.checkpoints, self.monsters,
         self.powerups, self.exit_door, self.npcs,
         self.ornaments, self.icicles, self.heart_pickups, self.boss) = create_level(self.difficulty)
        self.boss_defeated = False
        self.player = Player(100, 400)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles.clear(); self.rings.clear(); self.flashes.clear()
        self.score_popups.clear(); self.snowballs.clear()
        self.level_time = 0; self.tick = 0; self.win_timer = 0
        self.dialogue_box = None; self.ending_shown = False

    def _exit_to_menu(self):
        self.sfx.stop_music(); self.running = False
        pygame.event.clear()  # flush events so main.py doesn't pick up stale ESC

    def _apply_volume(self):
        pygame.mixer.music.set_volume(0.0 if self.music_muted else self.music_volume)

    def start_dialogue(self, key, return_state="playing"):
        if key in STORY_DIALOGUES:
            self.dialogue_box = DialogueBox(STORY_DIALOGUES[key])
            self.pending_state = return_state
            self.state = "dialogue"

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self._exit_to_menu(); return
                if event.type == pygame.KEYDOWN: self._handle_key(event.key)
            if not self.running: return
            if self.state == "playing": self._update()
            elif self.state == "win":
                self.win_timer += 1
                for sf in self.snowflakes: sf.update()
            elif self.state == "dialogue":
                if self.dialogue_box: self.dialogue_box.update()
                for sf in self.snowflakes: sf.update()
            elif self.state == "ending":
                if self.dialogue_box: self.dialogue_box.update()
                for sf in self.snowflakes: sf.update()
            elif self.state == "credits":
                if self.credits_scroll < self.credits_max_scroll:
                    self.credits_scroll += 0.6
                for sf in self.snowflakes: sf.update()
                self.tick += 1
            self._draw()
            self.clock.tick(FPS)

    def _handle_key(self, key):
        # Credits
        if self.state == "credits":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._exit_to_menu()
            return
        # Dialogue
        if self.state in ("dialogue", "ending"):
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                if self.dialogue_box:
                    self.dialogue_box.advance()
                    if not self.dialogue_box.active:
                        self.dialogue_box = None
                        if self.state == "ending":
                            self.state = "credits"
                            self.credits_scroll = 0.0
                            self.credits_max_scroll = 4200
                            self._start_credits_music()
                        else:
                            self.state = self.pending_state or "playing"
            return
        # Settings
        if self.state == "settings":
            n_items = 6
            if key == pygame.K_ESCAPE: self.state = "playing"
            elif key in (pygame.K_UP, pygame.K_w): self.settings_cursor = (self.settings_cursor - 1) % n_items
            elif key in (pygame.K_DOWN, pygame.K_s): self.settings_cursor = (self.settings_cursor + 1) % n_items
            elif key in (pygame.K_LEFT, pygame.K_a):
                if self.settings_cursor == 0:
                    self.music_volume = max(0.0, round(self.music_volume - 0.1, 1)); self._apply_volume()
                elif self.settings_cursor == 2:
                    diffs = ["easy","medium","hard"]
                    idx = diffs.index(self.difficulty)
                    self.difficulty = diffs[(idx - 1) % 3]
            elif key in (pygame.K_RIGHT, pygame.K_d):
                if self.settings_cursor == 0:
                    self.music_volume = min(1.0, round(self.music_volume + 0.1, 1)); self._apply_volume()
                elif self.settings_cursor == 2:
                    diffs = ["easy","medium","hard"]
                    idx = diffs.index(self.difficulty)
                    self.difficulty = diffs[(idx + 1) % 3]
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.settings_cursor == 1:
                    self.music_muted = not self.music_muted; self._apply_volume()
                elif self.settings_cursor == 2:
                    pass  # use arrows
                elif self.settings_cursor == 3: self.state = "playing"
                elif self.settings_cursor == 4:
                    self.load_level(); self.state = "playing"
                    self.sfx.start_music(volume=self.music_volume)
                elif self.settings_cursor == 5:
                    self._exit_to_menu()
            return
        # Win
        if self.state == "win":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                if not self.ending_shown:
                    self.ending_shown = True
                    self.start_dialogue("ending", "ending_done")
                    self.state = "ending"
                else:
                    self._exit_to_menu()
            return
        # Admin mode toggle — backslash key
        if key == pygame.K_BACKSLASH:
            self.admin_mode = not getattr(self, 'admin_mode', False)
            if self.admin_mode:
                self.player.gravity = 0
            else:
                self.player.gravity = GRAVITY
            return
        # Admin: skip to credits
        if key == pygame.K_BACKQUOTE and getattr(self, 'admin_mode', False):
            self.state = "credits"
            self.credits_scroll = 0.0
            self.credits_max_scroll = 4200
            self._start_credits_music()
            return
        # Admin: skip to win
        if key == pygame.K_1 and getattr(self, 'admin_mode', False):
            self.state = "win"; self.win_timer = 0; self.ending_shown = False
            return
        # Playing
        if key == pygame.K_ESCAPE:
            self.state = "settings"; self.settings_cursor = 3
        elif key == pygame.K_r:
            self.player.unreal_timer = 0; self.player.hearts = 0; self.player.die(); self.sfx.play("death")
        elif key in (pygame.K_f, pygame.K_x):
            sb = self.player.try_shoot()
            if sb:
                self.snowballs.append(sb); self.sfx.play("shoot")
                for _ in range(5):
                    self.particles.append(Particle(sb.x, sb.y,
                        random.choice([WHITE,SNOW_WHITE,ICE_BLUE]),
                        random.uniform(-1,1)-sb.dir*2, random.uniform(-1,1), 12, 2, 0.05))
        elif key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            if not self.player.on_ground and self.player.alive:
                self.player.start_dash()
        elif key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            # Double jump on key press (second jump only via keydown)
            if self.player.alive and not self.player.on_ground and self.player.jump_count == 1:
                self.player.vel_y = JUMP_VELOCITY * 0.85
                self.player.jump_count = 2
                self.sfx.play("jump")
                for _ in range(4):
                    self.particles.append(Particle(
                        self.player.rect.centerx + random.randint(-6, 6), self.player.rect.bottom,
                        random.choice([WHITE, ICE_BLUE]), random.uniform(-1, 1),
                        random.uniform(-0.5, 0.5), 12, 2, 0.08))
        elif key == pygame.K_e:
            # Talk to NPC
            for npc in self.npcs:
                if npc.check_proximity(self.player) and not npc.talked:
                    npc.talked = True
                    self.start_dialogue(npc.dialogue_key)
                    break

    def _update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f] or keys[pygame.K_x]:
            sb = self.player.try_shoot()
            if sb: self.snowballs.append(sb); self.sfx.play("shoot")

        # Admin mode: free fly with arrow/WASD, ignore gravity and collisions
        if getattr(self, 'admin_mode', False):
            spd = 10
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.player.rect.x -= spd
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player.rect.x += spd
            if keys[pygame.K_UP] or keys[pygame.K_w]: self.player.rect.y -= spd
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.player.rect.y += spd
            self.player.vel_y = 0
            self.camera.update(self.player.rect)
            for plat in self.platforms: plat.update()
            for sf in self.snowflakes: sf.update()
            return

        for plat in self.platforms: plat.update()
        result = self.player.update(keys, self.platforms)
        if result == "jump":
            self.sfx.play("jump")
            if self.player.alive:
                for _ in range(6):
                    self.particles.append(Particle(
                        self.player.rect.centerx+random.randint(-8,8), self.player.rect.bottom,
                        random.choice([WHITE,SNOW_WHITE]), random.uniform(-1.5,1.5),
                        random.uniform(-0.5,0.5), 15, random.randint(2,4), 0.08))

        if self.player.prev_unreal and not self.player.is_unreal: self.sfx.play("unreal_end")
        if self.player.alive: self.camera.update(self.player.rect)

        # NPC proximity
        for npc in self.npcs:
            npc.proximity_shown = npc.check_proximity(self.player)

        for cp in self.checkpoints:
            cp.update()
            if self.player.alive and cp.check(self.player):
                self.sfx.play("checkpoint")
                for _ in range(20):
                    a=random.uniform(0,math.pi*2); s=random.uniform(1,4)
                    self.particles.append(Particle(cp.rect.centerx,cp.rect.top,
                        random.choice([XMAS_GREEN,XMAS_GOLD,WHITE,XMAS_RED]),
                        math.cos(a)*s,math.sin(a)*s, 30, 3, 0.05))

        # Snowball collisions
        for sb in self.snowballs:
            if not sb.alive: continue
            sbr = sb.get_rect()
            for plat in self.platforms:
                if plat.is_active() and sbr.colliderect(plat.get_rect()):
                    sb.alive = False
                    for _ in range(4):
                        self.particles.append(Particle(sb.x,sb.y,WHITE,
                            random.uniform(-2,2),random.uniform(-2,0),10,2,0.1))
                    break
            if not sb.alive: continue
            for mon in self.monsters:
                if not isinstance(mon, BombMonster) or not mon.alive: continue
                if mon.state in ("defused","exploding"): continue
                if sbr.colliderect(mon.rect):
                    sb.alive = False
                    res = mon.hit_by_snowball()
                    if res == "defused":
                        self._bomb_defuse_fx(mon); self.sfx.play("bomb_defuse")
                        self.player.kill_count += 1
                        self.score_popups.append((mon.rect.centerx,mon.rect.top-20,"DEFUSED! +200",70,XMAS_GREEN))
                    elif res == "hit":
                        self._bomb_hit_fx(mon); self.sfx.play("stomp")
                        self.score_popups.append((mon.rect.centerx,mon.rect.top-20,
                            f"HIT! {mon.hits_to_kill-mon.hits} more",50,FUSE_ORANGE))
                    break

        self.snowballs = [s for s in self.snowballs if s.update()]
        for sb in self.snowballs:
            if sb.trail_timer % 3 == 0:
                self.particles.append(Particle(sb.x+random.uniform(-3,3),sb.y+random.uniform(-3,3),
                    random.choice([WHITE,SNOW_WHITE,ICE_BLUE]),random.uniform(-0.3,0.3),
                    random.uniform(-0.3,0.3),10,2,0.02))

        for mon in self.monsters:
            mon.update()
            if isinstance(mon, BombMonster) and self.player.alive:
                mon.check_proximity(self.player)
                if mon.state == "ticking" and mon.alive and self.tick % max(2,mon.flash_rate)==0:
                    fx=mon.rect.centerx+8; fy=mon.rect.top-8
                    for _ in range(3):
                        self.particles.append(Particle(fx+random.randint(-3,3),fy+random.randint(-3,3),
                            random.choice([FUSE_ORANGE,FUSE_RED,XMAS_GOLD]),
                            random.uniform(-1,1),random.uniform(-2,-0.5),15,random.randint(2,4),-0.05))
            coll = mon.check_collision(self.player)
            if coll == "kill_player":
                if self.player.take_damage():
                    if self.player.alive:
                        self.camera.add_shake(8); self.sfx.play("death")
                        self.flashes.append(FlashOverlay(RED, 10, 80))
                    else:
                        self._player_death_fx(); self.sfx.play("death")
                if isinstance(mon, BombMonster) and mon.state == "exploding":
                    self.sfx.play("bomb_explode"); self.camera.add_shake(18)
            elif coll == "kill_monster":
                self._monster_kill_fx(mon); mon.kill()
                self.player.kill_count += 1; self.sfx.play("monster_kill")
            elif coll == "stomp":
                self._stomp_fx(mon); mon.stomp()
                self.player.vel_y = STOMP_BOUNCE
                self.player.kill_count += 1; self.sfx.play("stomp")

        self.monsters = [m for m in self.monsters
            if m.alive or (hasattr(m,'squish_timer') and m.squish_timer>0)
            or m.death_timer>0
            or (isinstance(m,BombMonster) and m.state in ("exploding","defused"))]

        for pw in self.powerups:
            pw.update()
            if pw.check(self.player):
                self._powerup_fx(pw); self.player.activate_unreal(); self.sfx.play("powerup")

        # Ornaments
        for orn in self.ornaments:
            orn.update()
            if orn.check(self.player):
                self.player.ornament_count += 1
                cx, cy = orn.x, orn.y
                for _ in range(12):
                    a = random.uniform(0, math.pi * 2); s = random.uniform(1, 3)
                    self.particles.append(Particle(cx, cy, random.choice([orn.color, WHITE, XMAS_GOLD]),
                        math.cos(a) * s, math.sin(a) * s, 20, 2, 0.08))
                self.score_popups.append((cx, cy - 15, "+25", 40, orn.color))

        # Icicles
        for ic in self.icicles:
            ic.check_player_below(self.player)
            ic.update()
            if ic.check_hit(self.player):
                ic.state = "done"
                if self.player.take_damage():
                    if self.player.alive:
                        self.camera.add_shake(6); self.sfx.play("death")
                        self.flashes.append(FlashOverlay(ICE_BLUE, 8, 60))
                    else:
                        self._player_death_fx(); self.sfx.play("death")

        # Heart pickups
        for hp in self.heart_pickups:
            hp.update()
            if hp.check(self.player):
                self.player.hearts = min(PLAYER_MAX_HEARTS, self.player.hearts + 1)
                self.score_popups.append((hp.x, hp.y - 15, "+1 HEART", 50, XMAS_RED))
                self.sfx.play("powerup")

        # Boss
        if self.boss and self.boss.alive:
            self.boss.update()
            # Snowball hits on boss
            for sb in self.snowballs:
                if not sb.alive: continue
                if sb.get_rect().colliderect(self.boss.rect):
                    sb.alive = False
                    if self.boss.hit():
                        self.camera.add_shake(6)
                        for _ in range(8):
                            a = random.uniform(0, math.pi * 2); s = random.uniform(1, 4)
                            self.particles.append(Particle(self.boss.rect.centerx, self.boss.rect.centery,
                                random.choice([ICE_BLUE, WHITE, CYAN]),
                                math.cos(a) * s, math.sin(a) * s, 20, 3, 0.1))
                        if not self.boss.alive:
                            self.boss_defeated = True
                            self.camera.add_shake(15)
                            self.flashes.append(FlashOverlay(ICE_BLUE, 20, 140))
                            for _ in range(40):
                                a = random.uniform(0, math.pi * 2); s = random.uniform(2, 6)
                                self.particles.append(Particle(self.boss.rect.centerx, self.boss.rect.centery,
                                    random.choice([ICE_BLUE, WHITE, CYAN, XMAS_GOLD]),
                                    math.cos(a) * s, math.sin(a) * s, 50, 4, 0.05))
                            self.score_popups.append((self.boss.rect.centerx, self.boss.rect.top - 30, "BOSS DEFEATED!", 90, XMAS_GOLD))
                            self.sfx.play("monster_kill")
            # Boss projectile hits on player
            if self.boss.alive and self.boss.check_projectile_hit(self.player):
                if self.player.take_damage():
                    if self.player.alive:
                        self.camera.add_shake(6); self.sfx.play("death")
                    else:
                        self._player_death_fx(); self.sfx.play("death")
            # Boss body collision
            if self.boss.alive and self.player.alive and self.boss.rect.colliderect(self.player.rect):
                if self.player.take_damage():
                    if self.player.alive:
                        self.camera.add_shake(8); self.sfx.play("death")
                        self.player.vel_x = -8 if self.player.rect.centerx < self.boss.rect.centerx else 8
                        self.player.vel_y = -6
                    else:
                        self._player_death_fx(); self.sfx.play("death")

        self.exit_door.update()
        # Exit door only accessible after boss is defeated
        if self.player.alive and self.exit_door.check(self.player) and self.boss_defeated:
            self.state = "win"; self.sfx.play("win"); self.sfx.stop_music()

        self.particles = [p for p in self.particles if p.update()]
        self.rings = [r for r in self.rings if r.update()]
        self.flashes = [f for f in self.flashes if f.update()]
        self.score_popups = [(x,y-0.8,t,ti-1,c) for x,y,t,ti,c in self.score_popups if ti>0]
        for sf in self.snowflakes: sf.update()
        self._spawn_ambient()
        if not self.player.alive and self.player.respawn_timer == 1: self.sfx.play("respawn")
        self.level_time += 1

    # --- Effects ---
    def _player_death_fx(self):
        cx,cy=self.player.rect.centerx,self.player.rect.centery
        self.camera.add_shake(14); self.flashes.append(FlashOverlay(RED,18,120))
        for _ in range(35):
            a=random.uniform(0,math.pi*2); s=random.uniform(2,7)
            self.particles.append(Particle(cx,cy,random.choice([XMAS_RED,WHITE,ICE_BLUE,SNOW_WHITE]),
                math.cos(a)*s,math.sin(a)*s,random.randint(25,50),random.randint(3,7),0.15))

    def _monster_kill_fx(self, mon):
        cx,cy=mon.rect.centerx,mon.rect.centery
        self.camera.add_shake(8); self.rings.append(RingEffect(cx,cy,XMAS_GOLD,80,5,3))
        self.flashes.append(FlashOverlay(XMAS_GOLD,8,80))
        for _ in range(25):
            a=random.uniform(0,math.pi*2); s=random.uniform(2,6)
            self.particles.append(Particle(cx,cy,random.choice([XMAS_RED,XMAS_GREEN,XMAS_GOLD,WHITE]),
                math.cos(a)*s,math.sin(a)*s,random.randint(20,40),random.randint(3,6),0.1))
        self.score_popups.append((cx,cy-20,"+100",60,XMAS_GOLD))

    def _stomp_fx(self, mon):
        cx,cy=mon.rect.centerx,mon.rect.bottom
        self.camera.add_shake(5); self.rings.append(RingEffect(cx,cy,WHITE,40,4,2))
        for _ in range(12):
            a=random.uniform(-math.pi,0); s=random.uniform(1,4)
            self.particles.append(Particle(cx,cy,random.choice([SNOW_WHITE,WHITE,ICE_BLUE]),
                math.cos(a)*s,math.sin(a)*s-1,random.randint(15,30),random.randint(2,5),0.15))
        self.score_popups.append((cx,cy-25,"+50",50,WHITE))

    def _bomb_hit_fx(self, mon):
        cx,cy=mon.rect.centerx,mon.rect.centery
        self.camera.add_shake(6); self.rings.append(RingEffect(cx,cy,FUSE_ORANGE,50,4,2))
        for _ in range(15):
            a=random.uniform(0,math.pi*2); s=random.uniform(2,5)
            self.particles.append(Particle(cx,cy,random.choice([FUSE_ORANGE,FUSE_RED,WHITE]),
                math.cos(a)*s,math.sin(a)*s,random.randint(15,30),random.randint(2,5),0.1))

    def _bomb_defuse_fx(self, mon):
        cx,cy=mon.rect.centerx,mon.rect.centery
        self.camera.add_shake(10); self.flashes.append(FlashOverlay(XMAS_GREEN,12,100))
        for i in range(3):
            self.rings.append(RingEffect(cx,cy,XMAS_GREEN,60+i*30,3+i,3))
        for _ in range(30):
            a=random.uniform(0,math.pi*2); s=random.uniform(1,5)
            self.particles.append(Particle(cx,cy,random.choice([XMAS_GREEN,WHITE,SNOW_WHITE,ICE_BLUE]),
                math.cos(a)*s,math.sin(a)*s,random.randint(20,40),random.randint(2,6),0.08))

    def _powerup_fx(self, pw):
        cx,cy=pw.x,pw.y
        self.camera.add_shake(10); self.flashes.append(FlashOverlay(XMAS_GOLD,20,160))
        for i in range(3):
            self.rings.append(RingEffect(cx,cy,xmas_cycle_color(self.tick+i*30),100+i*40,3+i,4-i))
        for _ in range(40):
            a=random.uniform(0,math.pi*2); s=random.uniform(1,5)
            self.particles.append(Particle(cx,cy,random.choice([XMAS_GOLD,XMAS_RED,XMAS_GREEN,WHITE]),
                math.cos(a)*s,math.sin(a)*s,random.randint(30,60),random.randint(2,6),0.05))
        self.score_popups.append((cx,cy-30,"UNREAL MODE!",90,XMAS_GOLD))

    def _spawn_ambient(self):
        for plat in self.platforms:
            if isinstance(plat, GlitchPlatform) and plat.active and plat.alpha < 200:
                if random.random() < 0.25:
                    self.particles.append(Particle(plat.rect.x+random.randint(0,plat.rect.width),
                        plat.rect.y+random.randint(0,plat.rect.height),ICE_BLUE,
                        random.uniform(-1,1),random.uniform(-2,0),20))
            elif isinstance(plat, TeleportPlatform) and plat.flash > 0:
                for _ in range(4):
                    self.particles.append(Particle(plat.rect.x+random.randint(0,plat.rect.width),
                        plat.rect.y+random.randint(0,plat.rect.height),XMAS_GOLD,
                        random.uniform(-3,3),random.uniform(-3,3),15))
        if not self.player.alive and self.player.respawn_timer == 49: self._player_death_fx()
        if self.player.alive and self.player.is_unreal:
            if self.tick%2==0:
                self.particles.append(Particle(self.player.rect.centerx+random.randint(-8,8),
                    self.player.rect.bottom+random.randint(-4,4),
                    xmas_cycle_color(self.tick+random.randint(0,20)),
                    random.uniform(-0.5,0.5),random.uniform(-1.5,-0.3),random.randint(15,30),random.randint(3,6),0.02))
            if self.tick%5==0:
                side=1 if self.player.facing_right else -1
                self.particles.append(Particle(self.player.rect.centerx-side*12,
                    self.player.rect.centery+random.randint(-10,10),WHITE,
                    -side*random.uniform(1,3),random.uniform(-1,1),15,3,0))
        if self.player.alive and self.player.on_ground and abs(self.player.vel_x)>1 and self.tick%6==0:
            self.particles.append(Particle(self.player.rect.centerx+random.randint(-4,4),
                self.player.rect.bottom,SNOW_WHITE,random.uniform(-0.5,0.5),random.uniform(-0.8,-0.2),12,2,0.05))
        # Sprint trail afterimages
        if self.player.alive and self.player.sprinting and self.player.on_ground and abs(self.player.vel_x)>3 and self.tick%2==0:
            side = -1 if self.player.facing_right else 1
            self.particles.append(Particle(self.player.rect.centerx+side*10, self.player.rect.centery,
                (200,60,60), side*random.uniform(0.5,1.5), random.uniform(-0.5,0.5), 10, 4, 0.01, fade=True))

    # --- Drawing ---
    def _draw(self):
        self.screen.fill(DARK_SKY)
        if self.state == "playing":
            self._draw_game()
        elif self.state == "settings":
            self._draw_game(); self._draw_settings()
        elif self.state == "win":
            self._draw_win()
        elif self.state in ("dialogue", "ending"):
            self._draw_game()
            if self.dialogue_box: self.dialogue_box.draw(self.screen, self.tick)
        elif self.state == "credits":
            self._draw_credits()
        pygame.display.flip()

    def _draw_background(self):
        for y in range(0, SCREEN_HEIGHT, 4):
            t = y / SCREEN_HEIGHT
            self.screen.fill(lerp_color(NIGHT_BLUE, DARK_SKY, t), (0, y, SCREEN_WIDTH, 4))
        for star in self.bg_stars: star.draw(self.screen, self.tick)
        # Moon
        mx, my = SCREEN_WIDTH - 120, 80
        pygame.draw.circle(self.screen, (60, 60, 50), (mx, my), 50)
        pygame.draw.circle(self.screen, (240, 230, 200), (mx, my), 45)
        pygame.draw.circle(self.screen, (60, 60, 50), (mx + 12, my - 8), 35)  # crescent shadow
        # Glow
        for r in range(80, 40, -5):
            a = int(12 * (80 - r) / 40)
            gs = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (240, 230, 200, a), (r, r), r)
            self.screen.blit(gs, (mx - r, my - r))
        # Aurora
        for i in range(3):
            pts = []
            for x in range(0, SCREEN_WIDTH + 40, 40):
                y = 50 + int(math.sin(x*0.005+self.tick*0.01+i*2)*30+math.sin(x*0.003+self.tick*0.007)*20)
                pts.append((x, y))
            pts.append((SCREEN_WIDTH, 0)); pts.append((0, 0))
            if len(pts) >= 3:
                acs = [(20,80,40),(30,60,80),(40,30,70)]
                ac = acs[i%3]; p = abs(math.sin(self.tick*0.008+i))*0.5+0.3
                ac = tuple(int(c*p) for c in ac)
                s = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
                pygame.draw.polygon(s, (*ac, 35), pts)
                self.screen.blit(s, (0, 0))
        # Pine tree silhouettes
        ox = int(self.camera.offset_x * 0.08)
        base_y = SCREEN_HEIGHT - 30
        for tx in range(-50 - ox % 120, SCREEN_WIDTH + 150, 120):
            rng = random.Random(tx + 99999)
            th = rng.randint(60, 130)
            tw = rng.randint(30, 50)
            tc = (12, 18 + rng.randint(0, 8), 12)
            cx2 = tx
            # Triangle tree
            pygame.draw.polygon(self.screen, tc, [
                (cx2, base_y - th), (cx2 - tw, base_y), (cx2 + tw, base_y)])
            # Second layer
            pygame.draw.polygon(self.screen, tc, [
                (cx2, base_y - th + 20), (cx2 - tw + 8, base_y - 10), (cx2 + tw - 8, base_y - 10)])
            # Snow on tips
            pygame.draw.circle(self.screen, (30, 35, 45), (cx2, base_y - th), 4)
        # Distant village silhouettes
        ox2 = int(self.camera.offset_x * 0.04)
        for hx in range(-80 - ox2 % 250, SCREEN_WIDTH + 250, 250):
            rng2 = random.Random(hx + 77777)
            hw = rng2.randint(40, 60); hh = rng2.randint(30, 55)
            pygame.draw.rect(self.screen, (15, 18, 25),
                             (hx, base_y - hh, hw, hh))
            # Roof
            pygame.draw.polygon(self.screen, (20, 22, 30), [
                (hx - 5, base_y - hh), (hx + hw + 5, base_y - hh),
                (hx + hw // 2, base_y - hh - 20)])
            # Snow on roof
            pygame.draw.polygon(self.screen, (35, 38, 48), [
                (hx - 3, base_y - hh), (hx + hw + 3, base_y - hh),
                (hx + hw // 2, base_y - hh - 18)])
            # Window (warm glow)
            if rng2.random() > 0.3:
                wy = base_y - hh + 12; wx = hx + hw // 2 - 4
                wc = (60, 50, 20) if (self.tick // 60 + hx) % 3 != 0 else (40, 35, 15)
                pygame.draw.rect(self.screen, wc, (wx, wy, 8, 8))
        # Ground
        pygame.draw.rect(self.screen, (18, 22, 35), (0, base_y, SCREEN_WIDTH, 50))
        pygame.draw.rect(self.screen, (40, 45, 55), (0, base_y, SCREEN_WIDTH, 3))
        # Snowflakes
        for sf in self.snowflakes: sf.draw(self.screen)

    def _draw_game(self):
        self._draw_background()
        for i, plat in enumerate(self.platforms):
            plat.draw(self.screen, self.camera)
            if isinstance(plat, Platform) and not isinstance(plat, (GlitchPlatform, CollapsingPlatform)):
                if plat.rect.width >= 100 and i % 2 == 0:
                    draw_christmas_lights(self.screen, self.camera, plat.rect, self.tick)
        for cp in self.checkpoints: cp.draw(self.screen, self.camera)
        for pw in self.powerups: pw.draw(self.screen, self.camera, self.tick)
        for orn in self.ornaments: orn.draw(self.screen, self.camera, self.tick)
        for hp in self.heart_pickups: hp.draw(self.screen, self.camera, self.tick)
        for ic in self.icicles: ic.draw(self.screen, self.camera, self.tick)
        if self.boss and self.boss.alive: self.boss.draw(self.screen, self.camera, self.tick)
        # Draw exit door with lock indicator if boss not defeated
        self.exit_door.draw(self.screen, self.camera)
        if not self.boss_defeated:
            dr = self.camera.apply(self.exit_door.rect)
            font = pygame.font.SysFont("consolas", 10, bold=True)
            lock = font.render("LOCKED", True, XMAS_RED)
            self.screen.blit(lock, (dr.centerx - lock.get_width() // 2, dr.y - 14))
        for npc in self.npcs: npc.draw(self.screen, self.camera, self.tick)
        for mon in self.monsters: mon.draw(self.screen, self.camera, self.tick)
        for sb in self.snowballs: sb.draw(self.screen, self.camera, self.tick)
        for p in self.particles: p.draw(self.screen, self.camera)
        for r in self.rings: r.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.tick)
        for f in self.flashes: f.draw(self.screen)
        for x, y, text, timer, color in self.score_popups:
            a = min(1.0, timer / 30)
            c = tuple(max(0, min(255, int(v * a))) for v in color)
            pos = self.camera.apply(pygame.Rect(int(x), int(y), 1, 1))
            surf = self.small_font.render(text, True, c)
            self.screen.blit(surf, surf.get_rect(center=(pos.x, pos.y)))
        # HUD
        t = self.level_time / FPS
        self.screen.blit(self.small_font.render(f"Time: {t:.1f}s", True, SNOW_WHITE), (SCREEN_WIDTH-150, 10))
        if self.player.kill_count > 0:
            self.screen.blit(self.small_font.render(f"Kills: {self.player.kill_count}", True, XMAS_GOLD), (SCREEN_WIDTH-150, 30))
        diff_label = self.difficulty.upper()
        dc = XMAS_GREEN if self.difficulty == "easy" else XMAS_GOLD if self.difficulty == "medium" else XMAS_RED
        self.screen.blit(self.tiny_font.render(f"Difficulty: {diff_label}", True, dc), (SCREEN_WIDTH - 150, 50))
        # Hearts display
        for i in range(PLAYER_MAX_HEARTS):
            hx = 10 + i * 28; hy = 30
            c = XMAS_RED if i < self.player.hearts else DARK_GRAY
            pygame.draw.circle(self.screen, c, (hx + 5, hy), 6)
            pygame.draw.circle(self.screen, c, (hx + 15, hy), 6)
            pygame.draw.polygon(self.screen, c, [(hx - 1, hy + 2), (hx + 10, hy + 12), (hx + 21, hy + 2)])
        # Ornament count
        orn_total = len(self.ornaments)
        orn_got = self.player.ornament_count
        self.screen.blit(self.tiny_font.render(f"Ornaments: {orn_got}/{orn_total}", True, XMAS_GOLD), (10, 50))
        # Dash cooldown
        if self.player.dash_cooldown > 0:
            self.screen.blit(self.tiny_font.render(f"Dash: {self.player.dash_cooldown//6+1}", True, GRAY), (10, 65))
        else:
            self.screen.blit(self.tiny_font.render("Dash: READY [SHIFT]", True, CYAN), (10, 65))
        if self.player.is_unreal:
            rem=self.player.unreal_timer/FPS; bw,bh=160,14
            bx=SCREEN_WIDTH//2-bw//2; by=12; ratio=self.player.unreal_timer/UNREAL_DURATION
            pygame.draw.rect(self.screen,DARK_GRAY,(bx-2,by-2,bw+4,bh+4))
            for px_i in range(int(bw*ratio)):
                self.screen.fill(xmas_cycle_color(self.tick+px_i*2,0.3),(bx+px_i,by,1,bh))
            self.screen.blit(self.tiny_font.render(f"UNREAL  {rem:.1f}s",True,WHITE),(bx+4,by+1))
            pygame.draw.rect(self.screen,xmas_cycle_color(self.tick,0.15),(bx-2,by-2,bw+4,bh+4),2)
        cd="READY" if self.player.shoot_cooldown<=0 else f"{self.player.shoot_cooldown}"
        self.screen.blit(self.tiny_font.render(f"Snowball [F/X]: {cd}",True,
            SNOW_WHITE if self.player.shoot_cooldown<=0 else GRAY),(10,10))
        self.screen.blit(self.small_font.render("R-Respawn  ESC-Settings  F/X-Shoot  E-Talk  SHIFT-Dash(air)",True,(60,70,90)),
            (10,SCREEN_HEIGHT-22))
        # Realm title
        self.screen.blit(self.tiny_font.render("The Fourth Realm: Frozen Christmas",True,(50,55,75)),
            (SCREEN_WIDTH//2-110,SCREEN_HEIGHT-18))
        if not self.player.alive:
            txt=self.font.render("Respawning...",True,XMAS_RED)
            self.screen.blit(txt,txt.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)))

    def _draw_settings(self):
        # Bright warm Christmas overlay - gradient from deep red-brown to dark green
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            t = y / SCREEN_HEIGHT
            r = int(45 + 15 * t)
            g = int(20 + 20 * t)
            b = int(25 + 10 * t)
            pygame.draw.rect(overlay, (r, g, b, 225), (0, y, SCREEN_WIDTH, 4))
        self.screen.blit(overlay, (0, 0))

        # Animated candy-cane border (thick, colorful)
        bw = 8
        for x in range(0, SCREEN_WIDTH, 24):
            shift = (self.tick // 4) % 24
            c = XMAS_RED if ((x + shift) // 12) % 2 == 0 else XMAS_GREEN
            pygame.draw.rect(self.screen, c, (x, 0, 12, bw))
            pygame.draw.rect(self.screen, c, (x, SCREEN_HEIGHT - bw, 12, bw))
        for y in range(0, SCREEN_HEIGHT, 24):
            shift = (self.tick // 4) % 24
            c = XMAS_RED if ((y + shift) // 12) % 2 == 0 else XMAS_GREEN
            pygame.draw.rect(self.screen, c, (0, y, bw, 12))
            pygame.draw.rect(self.screen, c, (SCREEN_WIDTH - bw, y, bw, 12))
        # Golden corners
        for cx2, cy2 in [(bw, bw), (SCREEN_WIDTH - bw, bw), (bw, SCREEN_HEIGHT - bw), (SCREEN_WIDTH - bw, SCREEN_HEIGHT - bw)]:
            pygame.draw.circle(self.screen, XMAS_GOLD, (cx2, cy2), 10)
            pygame.draw.circle(self.screen, WHITE, (cx2, cy2), 6)
            pygame.draw.circle(self.screen, XMAS_RED, (cx2, cy2), 3)

        # Floating snowflakes in settings
        for i in range(12):
            sx2 = (100 + i * 105 + int(math.sin(self.tick * 0.02 + i * 1.3) * 30)) % SCREEN_WIDTH
            sy2 = (60 + int(math.sin(self.tick * 0.015 + i * 0.7) * 20))
            sz = 2 + int(abs(math.sin(self.tick * 0.03 + i)) * 3)
            pygame.draw.circle(self.screen, WHITE, (sx2, sy2), sz)

        # Title panel
        panel_w, panel_h = 360, 50
        panel_r = pygame.Rect(SCREEN_WIDTH // 2 - panel_w // 2, 55, panel_w, panel_h)
        pygame.draw.rect(self.screen, (70, 25, 25), panel_r, border_radius=8)
        pygame.draw.rect(self.screen, XMAS_GOLD, panel_r, 3, border_radius=8)
        title = self.title_font.render("SETTINGS", True, XMAS_GOLD)
        self.screen.blit(title, title.get_rect(center=panel_r.center))
        # Ornaments on title
        for ox2, oc in [(-panel_w // 2 - 20, XMAS_RED), (panel_w // 2 + 20, XMAS_GREEN)]:
            px2 = SCREEN_WIDTH // 2 + ox2
            pygame.draw.line(self.screen, GRAY, (px2, panel_r.top), (px2, panel_r.top - 8), 1)
            pygame.draw.circle(self.screen, oc, (px2, panel_r.top - 12), 7)
            pygame.draw.circle(self.screen, WHITE, (px2 - 2, panel_r.top - 14), 2)

        # Christmas tree on left side
        tree_x, tree_base = 80, 500
        for layer, (tw2, th2, yo2) in enumerate([(50, 28, 70), (40, 24, 45), (28, 20, 22)]):
            pygame.draw.polygon(self.screen, XMAS_GREEN,
                [(tree_x, tree_base - yo2 - th2), (tree_x - tw2 // 2, tree_base - yo2), (tree_x + tw2 // 2, tree_base - yo2)])
        pygame.draw.rect(self.screen, BROWN, (tree_x - 5, tree_base - 10, 10, 20))
        pygame.draw.circle(self.screen, XMAS_GOLD, (tree_x, tree_base - 95), 5)
        # Tree lights
        for j, (tlx, tly, tlc) in enumerate([(-12, -35, XMAS_RED), (10, -30, CYAN), (-8, -55, XMAS_GOLD), (14, -50, CANDY_PINK), (0, -75, XMAS_RED)]):
            if abs(math.sin(self.tick * 0.06 + j * 1.1)) > 0.3:
                pygame.draw.circle(self.screen, tlc, (tree_x + tlx, tree_base + tly), 3)

        # Christmas tree on right side
        tree_x2 = SCREEN_WIDTH - 80
        for layer, (tw2, th2, yo2) in enumerate([(50, 28, 70), (40, 24, 45), (28, 20, 22)]):
            pygame.draw.polygon(self.screen, XMAS_GREEN,
                [(tree_x2, tree_base - yo2 - th2), (tree_x2 - tw2 // 2, tree_base - yo2), (tree_x2 + tw2 // 2, tree_base - yo2)])
        pygame.draw.rect(self.screen, BROWN, (tree_x2 - 5, tree_base - 10, 10, 20))
        pygame.draw.circle(self.screen, XMAS_GOLD, (tree_x2, tree_base - 95), 5)
        for j, (tlx, tly, tlc) in enumerate([(12, -35, XMAS_GREEN), (-10, -30, XMAS_GOLD), (8, -55, CYAN), (-14, -50, XMAS_RED), (0, -75, CANDY_PINK)]):
            if abs(math.sin(self.tick * 0.06 + j * 1.1 + 2)) > 0.3:
                pygame.draw.circle(self.screen, tlc, (tree_x2 + tlx, tree_base + tly), 3)

        # Menu items
        items = [
            f"Music Volume:  < {int(self.music_volume * 100)}% >",
            f"Mute Music:    {'ON' if self.music_muted else 'OFF'}",
            f"Difficulty:    < {self.difficulty.upper()} >",
            "Resume Game",
            "Restart Level",
            "Exit to Main Menu",
        ]
        hints = ["(Left / Right)", "(Enter to toggle)", "(Left / Right)", "(Enter)", "(Enter - applies difficulty)", "(Enter)"]
        item_colors = [SNOW_WHITE, SNOW_WHITE, SNOW_WHITE, XMAS_GREEN, XMAS_GOLD, XMAS_RED]

        start_y = 130
        spacing = 48
        for i, (item, hint) in enumerate(zip(items, hints)):
            y = start_y + i * spacing
            sel = (i == self.settings_cursor)
            # Background bar for each item
            bar = pygame.Rect(SCREEN_WIDTH // 2 - 240, y - 2, 480, 36)
            if sel:
                # Bright selected bar - warm red-brown
                pygame.draw.rect(self.screen, (80, 30, 30), bar, border_radius=6)
                pygame.draw.rect(self.screen, XMAS_GOLD, bar, 2, border_radius=6)
                # Holly decoration left
                pygame.draw.circle(self.screen, XMAS_GREEN, (bar.left + 10, bar.centery - 3), 5)
                pygame.draw.circle(self.screen, XMAS_GREEN, (bar.left + 18, bar.centery + 1), 4)
                pygame.draw.circle(self.screen, XMAS_RED, (bar.left + 14, bar.centery - 1), 2)
                # Holly decoration right
                pygame.draw.circle(self.screen, XMAS_GREEN, (bar.right - 10, bar.centery - 3), 5)
                pygame.draw.circle(self.screen, XMAS_GREEN, (bar.right - 18, bar.centery + 1), 4)
                pygame.draw.circle(self.screen, XMAS_RED, (bar.right - 14, bar.centery - 1), 2)
                # Arrow
                arr = self.small_font.render(">", True, XMAS_GOLD)
                self.screen.blit(arr, (bar.left + 26, y + 4))
                color = item_colors[i]
            else:
                pygame.draw.rect(self.screen, (55, 30, 30), bar, border_radius=6)
                pygame.draw.rect(self.screen, (100, 70, 50), bar, 1, border_radius=6)
                color = SNOW_WHITE

            txt = self.small_font.render(item, True, color)
            self.screen.blit(txt, (SCREEN_WIDTH // 2 - 160, y + 4))

            if sel:
                ht = self.tiny_font.render(hint, True, (150, 140, 120))
                self.screen.blit(ht, (SCREEN_WIDTH // 2 - 160, y + 24))

        # Volume bar visual (below volume item)
        vbar_x = SCREEN_WIDTH // 2 - 100
        vbar_y = start_y + 0 * spacing + 34
        pygame.draw.rect(self.screen, (40, 40, 50), (vbar_x - 2, vbar_y - 2, 204, 10), border_radius=3)
        vol_w = int(200 * self.music_volume)
        # Gradient fill
        for px in range(vol_w):
            t = px / 200
            vc = lerp_color(XMAS_GREEN, XMAS_RED, t) if not self.music_muted else (80, 30, 30)
            pygame.draw.line(self.screen, vc, (vbar_x + px, vbar_y), (vbar_x + px, vbar_y + 5))
        pygame.draw.rect(self.screen, WHITE, (vbar_x, vbar_y, 200, 6), 1, border_radius=2)
        # Volume knob
        knob_x = vbar_x + vol_w
        pygame.draw.circle(self.screen, WHITE, (knob_x, vbar_y + 3), 5)
        pygame.draw.circle(self.screen, XMAS_GOLD, (knob_x, vbar_y + 3), 3)

        # Difficulty description
        desc = {"easy": "Relaxed: Slower enemies, bombs need 1 hit, longer fuse",
                "medium": "Balanced: Moderate speed, bombs need 2 hits",
                "hard": "Intense: Fast aggressive enemies, bombs need 2 hits, short fuse"}
        dc = XMAS_GREEN if self.difficulty == "easy" else XMAS_GOLD if self.difficulty == "medium" else XMAS_RED
        dt = self.tiny_font.render(desc[self.difficulty], True, dc)
        self.screen.blit(dt, dt.get_rect(center=(SCREEN_WIDTH // 2, start_y + 2 * spacing + 36)))

        # Footer with string of lights
        footer_y = SCREEN_HEIGHT - 50
        light_colors = [XMAS_RED, XMAS_GREEN, XMAS_GOLD, CYAN, CANDY_PINK]
        wire_y = footer_y
        for lx in range(40, SCREEN_WIDTH - 40, 20):
            li = (lx - 40) // 20
            sag = int(math.sin(lx * 0.05) * 4)
            if lx > 40:
                pygame.draw.line(self.screen, (40, 60, 40), (lx - 20, wire_y + int(math.sin((lx - 20) * 0.05) * 4)),
                                 (lx, wire_y + sag), 1)
            lc = light_colors[li % len(light_colors)]
            if abs(math.sin(self.tick * 0.06 + li * 0.8)) > 0.25:
                pygame.draw.circle(self.screen, lc, (lx, wire_y + sag), 4)
                pygame.draw.circle(self.screen, tuple(min(255, c + 60) for c in lc), (lx, wire_y + sag), 2)

        # ESC hint
        esc = self.small_font.render("ESC to resume", True, (120, 120, 140))
        self.screen.blit(esc, esc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25)))

    def _start_credits_music(self):
        # Template: put your credits music file here
        credits_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "audio", "credits.mp3")
        if not os.path.isfile(credits_path):
            credits_path = MUSIC_FILE  # fallback to level music
        try:
            pygame.mixer.music.load(credits_path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except: pass

    def _draw_credits(self):
        scroll = self.credits_scroll
        cx = SCREEN_WIDTH // 2

        # ── Background: night → sunrise transition based on scroll progress ──
        # progress goes 0.0 (start/night) → 1.0 (end/sunrise)
        if not hasattr(self, '_cr_max_est'):
            self._cr_max_est = 3500  # rough estimate, updated below
        progress = min(1.0, scroll / max(1, self._cr_max_est))

        # Sky colors: dark night → deep blue → purple dawn → orange sunrise
        night_top = (5, 5, 20)
        night_bot = (10, 10, 35)
        dawn_top = (40, 20, 60)
        dawn_bot = (80, 40, 70)
        sunrise_top = (255, 140, 50)
        sunrise_bot = (255, 200, 100)

        def lerp_c(c1, c2, t):
            return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

        if progress < 0.5:
            t = progress * 2  # 0→1 over first half
            top_c = lerp_c(night_top, dawn_top, t)
            bot_c = lerp_c(night_bot, dawn_bot, t)
        else:
            t = (progress - 0.5) * 2  # 0→1 over second half
            top_c = lerp_c(dawn_top, sunrise_top, t)
            bot_c = lerp_c(dawn_bot, sunrise_bot, t)

        # Draw gradient sky
        for row in range(SCREEN_HEIGHT):
            rt = row / SCREEN_HEIGHT
            c = lerp_c(top_c, bot_c, rt)
            pygame.draw.line(self.screen, c, (0, row), (SCREEN_WIDTH, row))

        # Sun rising at bottom-right as we approach sunrise
        if progress > 0.4:
            sun_t = min(1.0, (progress - 0.4) / 0.6)
            sun_y = int(SCREEN_HEIGHT - sun_t * 200)
            sun_x = SCREEN_WIDTH - 200
            sun_r = int(40 + sun_t * 40)
            # Glow
            for gr in range(sun_r + 60, sun_r, -4):
                ga = int(30 * sun_t * (1 - (gr - sun_r) / 60))
                glow_c = (min(255, 255), min(255, 180 + ga), min(255, 50 + ga))
                pygame.draw.circle(self.screen, glow_c, (sun_x, sun_y), gr)
            pygame.draw.circle(self.screen, (255, 230, 120), (sun_x, sun_y), sun_r)

        # Stars fade out as sunrise comes
        star_alpha = max(0, 1.0 - progress * 1.5)
        if star_alpha > 0.05:
            for star in self.bg_stars: star.draw(self.screen, self.tick)

        # Snow keeps falling always
        for sf in self.snowflakes: sf.draw(self.screen)

        # Colors — dark/night tones for headers so they read well over sunrise
        HEADER = (30, 30, 80)         # deep indigo for section headers
        SUBHEADER = (50, 40, 90)      # slightly lighter indigo
        NAME_WHITE = (255, 255, 255)
        BODY = (200, 200, 210)
        DIM = (100, 100, 120)
        WARM_RED = (180, 50, 50)
        WARM_GREEN = (40, 160, 90)
        ICE_BLUE = (60, 120, 180)
        SOFT_PINK = (180, 100, 150)
        GOLD = (180, 140, 30)
        DARK_GOLD = (120, 90, 20)

        # Build bold fonts for credits (cached)
        if not hasattr(self, '_cr_fonts'):
            self._cr_fonts = {
                "heading": pygame.font.SysFont("consolas", 42, bold=True),
                "subheading": pygame.font.SysFont("consolas", 30, bold=True),
                "name": pygame.font.SysFont("consolas", 36, bold=True),
                "role": pygame.font.SysFont("consolas", 16),
                "body": pygame.font.SysFont("consolas", 20),
                "small": pygame.font.SysFont("consolas", 14),
                "big_title": pygame.font.SysFont("consolas", 56, bold=True),
                "subtitle": pygame.font.SysFont("consolas", 18),
            }
        fonts = self._cr_fonts

        # (text, font_key, color, gap_after)
        credits = [
            ("", "body", NAME_WHITE, 80),

            # ── Game Title - BIG ──
            ("THE ENDLESS DREAM", "big_title", HEADER, 14),
            ("Imaging Assignment", "subtitle", DIM, 40),
            ("A Frozen Realm  -  The Final Chapter", "body", ICE_BLUE, 10),
            ("A Christmas-themed platformer adventure", "small", DIM, 40),

            ("", "body", NAME_WHITE, 40),

            # ── The Team ──
            ("The Team", "heading", HEADER, 15),

            ("Muqeet", "name", WARM_RED, 4),
            ("Developer", "role", DIM, 20),

            ("Omar", "name", WARM_GREEN, 4),
            ("Developer", "role", DIM, 20),

            ("John", "name", ICE_BLUE, 4),
            ("Developer", "role", DIM, 20),

            ("Danial", "name", SOFT_PINK, 4),
            ("Developer", "role", DIM, 20),

            ("", "body", NAME_WHITE, 30),

            # ── Roles ──
            ("Game Design", "subheading", SUBHEADER, 4),
            ("Muqeet  /  Omar  /  John  /  Danial", "role", BODY, 20),

            ("Art & Visuals", "subheading", SUBHEADER, 4),
            ("Muqeet  /  Omar  /  John  /  Danial", "role", BODY, 20),

            ("Music & Sound", "subheading", SUBHEADER, 4),
            ("Muqeet  /  Omar  /  John  /  Danial", "role", BODY, 20),

            ("Level Design", "subheading", SUBHEADER, 4),
            ("Muqeet  /  Omar  /  John  /  Danial", "role", BODY, 20),

            ("Story & Narrative", "subheading", SUBHEADER, 4),
            ("Muqeet  /  Omar  /  John  /  Danial", "role", BODY, 20),

            ("QA & Playtesting", "subheading", SUBHEADER, 4),
            ("Muqeet  /  Omar  /  John  /  Danial", "role", BODY, 20),

            ("", "body", NAME_WHITE, 30),

            # ── Built With ──
            ("Built With", "subheading", SUBHEADER, 6),
            ("Python 3  /  Pygame", "role", BODY, 4),
            ("Pixel Art  /  Retro Sound Design", "role", BODY, 4),
            ("Passion  /  Sleepless Nights  /  Coffee", "role", BODY, 30),

            ("", "body", NAME_WHITE, 30),

            # ── Instructor ──
            ("Instructor", "heading", HEADER, 15),
            ("Mary Ting", "name", NAME_WHITE, 4),
            ("Course Professor", "role", DIM, 20),

            ("", "body", NAME_WHITE, 30),

            # ── Special Thanks ──
            ("Special Thanks", "heading", HEADER, 15),

            ("Mary Ting", "body", NAME_WHITE, 4),
            ("For the guidance and inspiration", "role", DIM, 18),

            ("Our Classmates", "body", NAME_WHITE, 4),
            ("For the feedback, support, and laughs", "role", DIM, 18),

            ("The Pygame Community", "body", NAME_WHITE, 4),
            ("For the tools that made this possible", "role", DIM, 18),

            ("Every Playtester", "body", NAME_WHITE, 4),
            ("Who found the bugs we missed", "role", DIM, 18),

            ("Open-Source Creators", "body", NAME_WHITE, 4),
            ("Whose sprites, fonts, and sounds", "role", DIM, 2),
            ("brought this world to life", "role", DIM, 18),

            ("Our Families", "body", NAME_WHITE, 4),
            ("For putting up with us during crunch", "role", DIM, 25),

            ("", "body", NAME_WHITE, 40),

            # ── A Note to the Player ──
            ("A Note to the Player", "heading", HEADER, 15),

            ("You braved the four realms.", "body", ICE_BLUE, 6),
            ("You faced every monster, every trap,", "role", BODY, 2),
            ("every impossible jump.", "role", BODY, 14),

            ("You refused to give up.", "body", WARM_GREEN, 14),

            ("The dream is over now.", "role", BODY, 2),
            ("You can finally wake up.", "role", BODY, 14),

            ("But we hope a little piece", "role", DIM, 2),
            ("of this adventure stays with you.", "role", DIM, 30),

            ("", "body", NAME_WHITE, 40),

            # ── Final ──
            ("Thank You for Playing", "heading", HEADER, 15),

            ("This game was made with heart.", "body", BODY, 6),
            ("We hope it made you smile.", "body", BODY, 30),

            ("", "body", NAME_WHITE, 20),

            ("Every snowflake, every light, every pixel", "role", ICE_BLUE, 2),
            ("was crafted in the spirit of Christmas.", "role", ICE_BLUE, 30),

            ("", "body", NAME_WHITE, 150),

            # ── End Title — scrolls in and stops centered ──
            ("THE ENDLESS DREAM", "big_title", HEADER, 8),
            ("Imaging Assignment  -  2026", "subtitle", DIM, 40),
        ]

        # Calculate total height including font heights
        total_h = SCREEN_HEIGHT + 50
        for text, fkey, _, gap in credits:
            f = fonts.get(fkey, fonts["role"])
            fh = f.get_height() if text else 0
            total_h += fh + gap
        # Stop scroll so the end title ("THE ENDLESS DREAM") is centered on screen
        # The last two entries are the end title + subtitle
        end_title_fh = fonts["big_title"].get_height()
        end_sub_fh = fonts["subtitle"].get_height()
        end_block = end_title_fh + 8 + end_sub_fh + 40  # gaps from credits list
        self.credits_max_scroll = total_h - SCREEN_HEIGHT // 2 - end_block // 2
        self._cr_max_est = self.credits_max_scroll

        # ── Draw scrolling credits ──
        # Gap = space AFTER the line (font height is added automatically)
        y = SCREEN_HEIGHT + 50 - scroll
        for text, fkey, color, gap in credits:
            f = fonts.get(fkey, fonts["role"])
            fh = f.get_height() if text else 0
            if text and -fh < y < SCREEN_HEIGHT + fh:
                alpha = 1.0
                if y < 90: alpha = max(0, y / 90)
                if y > SCREEN_HEIGHT - 90: alpha = max(0, (SCREEN_HEIGHT - y) / 90)
                if alpha > 0:
                    c = tuple(max(0, min(255, int(v * alpha))) for v in color)
                    surf = f.render(text, True, c)
                    rect = surf.get_rect(center=(cx, int(y)))
                    shadow_c = tuple(max(0, int(v * 0.25 * alpha)) for v in color)
                    shadow = f.render(text, True, shadow_c)
                    self.screen.blit(shadow, shadow.get_rect(center=(cx + 2, int(y) + 2)))
                    self.screen.blit(surf, rect)
            y += fh + gap

        # Christmas lights at top
        wire_y = 12
        for lx in range(20, SCREEN_WIDTH - 20, 20):
            li = lx // 20
            lcs = [WARM_RED, WARM_GREEN, GOLD, ICE_BLUE, SOFT_PINK]
            lc = lcs[li % len(lcs)]
            pulse = abs(math.sin(self.tick * 0.04 + li * 0.7))
            if pulse > 0.2:
                br = 0.5 + 0.5 * pulse
                bc = tuple(min(255, int(c * br)) for c in lc)
                pygame.draw.circle(self.screen, bc, (lx, wire_y), 4)
                pygame.draw.circle(self.screen, tuple(min(255, c + 60) for c in bc), (lx, wire_y), 2)
            if lx > 20:
                sag = int(2 * math.sin((lx - 20) * 0.15))
                pygame.draw.line(self.screen, (40, 55, 40), (lx - 20, wire_y + sag), (lx, wire_y), 1)

        # Christmas lights at bottom
        bot_y = SCREEN_HEIGHT - 12
        for lx in range(20, SCREEN_WIDTH - 20, 20):
            li = lx // 20 + 3
            lcs = [WARM_RED, WARM_GREEN, GOLD, ICE_BLUE, SOFT_PINK]
            lc = lcs[li % len(lcs)]
            pulse = abs(math.sin(self.tick * 0.04 + li * 0.7 + 1.5))
            if pulse > 0.2:
                br = 0.5 + 0.5 * pulse
                bc = tuple(min(255, int(c * br)) for c in lc)
                pygame.draw.circle(self.screen, bc, (lx, bot_y), 4)
                pygame.draw.circle(self.screen, tuple(min(255, c + 60) for c in bc), (lx, bot_y), 2)
            if lx > 20:
                sag = int(2 * math.sin((lx - 20) * 0.15))
                pygame.draw.line(self.screen, (40, 55, 40), (lx - 20, bot_y - sag), (lx, bot_y), 1)

        # Exit hint
        is_stopped = self.credits_scroll >= self.credits_max_scroll
        if is_stopped:
            pulse = abs(math.sin(self.tick * 0.05)) * 0.5 + 0.5
            hint_c = tuple(int(v * (0.6 + 0.4 * pulse)) for v in HEADER)
            hint = fonts["body"].render("Press ENTER or ESC to return to menu", True, hint_c)
            self.screen.blit(hint, hint.get_rect(center=(cx, SCREEN_HEIGHT - 32)))
        else:
            skip_alpha = abs(math.sin(self.tick * 0.04)) * 0.3 + 0.2
            skip_c = tuple(int(v * skip_alpha) for v in (80, 80, 100))
            skip = fonts["small"].render("Press ENTER or ESC to skip", True, skip_c)
            self.screen.blit(skip, skip.get_rect(center=(cx, SCREEN_HEIGHT - 32)))

    def _draw_win(self):
        self._draw_background()
        if self.win_timer%8==0:
            for _ in range(3):
                self.particles.append(Particle(random.randint(200,SCREEN_WIDTH-200),
                    random.randint(50,200),random.choice([XMAS_RED,XMAS_GREEN,XMAS_GOLD,WHITE]),
                    random.uniform(-2,2),random.uniform(1,3),60,random.randint(3,6),0.05))
        for p in self.particles: p.draw(self.screen, self.camera)
        self.particles = [p for p in self.particles if p.update()]
        txt=self.big_font.render("REALM CONQUERED!",True,XMAS_GREEN)
        self.screen.blit(txt,txt.get_rect(center=(SCREEN_WIDTH//2,120)))
        txt2=self.font.render("THE FOURTH REALM - COMPLETE!",True,XMAS_GOLD)
        self.screen.blit(txt2,txt2.get_rect(center=(SCREEN_WIDTH//2,180)))
        t=self.level_time/FPS
        self.screen.blit(self.font.render(f"Time: {t:.1f} seconds",True,SNOW_WHITE),
            self.font.render(f"Time: {t:.1f} seconds",True,SNOW_WHITE).get_rect(center=(SCREEN_WIDTH//2,250)))
        self.screen.blit(self.font.render(f"Monsters defeated: {self.player.kill_count}",True,XMAS_GOLD),
            self.font.render(f"Monsters defeated: {self.player.kill_count}",True,XMAS_GOLD).get_rect(center=(SCREEN_WIDTH//2,300)))
        diff_c = XMAS_GREEN if self.difficulty=="easy" else XMAS_GOLD if self.difficulty=="medium" else XMAS_RED
        self.screen.blit(self.font.render(f"Difficulty: {self.difficulty.upper()}",True,diff_c),
            self.font.render(f"Difficulty: {self.difficulty.upper()}",True,diff_c).get_rect(center=(SCREEN_WIDTH//2,340)))
        # Ornaments collected
        self.screen.blit(self.font.render(f"Ornaments: {self.player.ornament_count}/{len(self.ornaments)}",True,XMAS_GOLD),
            self.font.render(f"Ornaments: {self.player.ornament_count}/{len(self.ornaments)}",True,XMAS_GOLD).get_rect(center=(SCREEN_WIDTH//2,380)))
        # Death counter
        self.screen.blit(self.font.render(f"Deaths: {self.player.death_count}",True,XMAS_RED),
            self.font.render(f"Deaths: {self.player.death_count}",True,XMAS_RED).get_rect(center=(SCREEN_WIDTH//2,420)))
        # Timer-based rank
        if t < 90: rank, rank_c = "S", XMAS_GOLD
        elif t < 150: rank, rank_c = "A", XMAS_GREEN
        elif t < 240: rank, rank_c = "B", ICE_BLUE
        else: rank, rank_c = "C", GRAY
        rank_txt = self.big_font.render(f"Rank: {rank}", True, rank_c)
        self.screen.blit(rank_txt, rank_txt.get_rect(center=(SCREEN_WIDTH//2,470)))
        hint=self.small_font.render("Press ENTER to see the ending...",True,SNOW_WHITE)
        pulse=abs(math.sin(self.tick*0.05))*0.5+0.5
        hint.set_alpha(int(128+127*pulse))
        self.screen.blit(hint,hint.get_rect(center=(SCREEN_WIDTH//2,540)))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def launch_game():
    pygame.mixer.music.stop()
    pygame.event.clear()
    game = Game()
    game.run()
    pygame.event.clear()  # prevent stale keys leaking to main.py
    pygame.display.set_caption("The Endless Dream")
    try:
        pygame.mixer.music.load("assets/audio/BackgroundMusic.mp3")
        pygame.mixer.music.play(-1)
    except: pass


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    game = Game()
    game.run()
    pygame.quit()
