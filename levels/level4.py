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
ICICLE_SHAKE_TIME = 30
ICICLE_FALL_SPEED = 8

DIFFICULTY = {
    "easy":   {"bomb_fuse": 300, "bomb_detect": 180, "bomb_spd": 0.5, "mon_spd": 0.4, "bomb_hits": 1,
               "plat_spd": 0.6, "glitch_on": 140, "glitch_off": 40, "collapse_delay": 70, "tp_interval": 200,
               "saw_spd": 0.5, "wind_str": 0.5, "crumble_delay": 16, "icicle_spd": 3, "ornament_gate": 0},
    "medium": {"bomb_fuse": 220, "bomb_detect": 230, "bomb_spd": 0.8, "mon_spd": 0.7, "bomb_hits": 2,
               "plat_spd": 0.85, "glitch_on": 110, "glitch_off": 55, "collapse_delay": 55, "tp_interval": 150,
               "saw_spd": 0.75, "wind_str": 0.75, "crumble_delay": 11, "icicle_spd": 5, "ornament_gate": 13},
    "hard":   {"bomb_fuse": 150, "bomb_detect": 300, "bomb_spd": 1.3, "mon_spd": 1.0,  "bomb_hits": 2,
               "plat_spd": 1.0, "glitch_on": 80, "glitch_off": 65, "collapse_delay": 40, "tp_interval": 110,
               "saw_spd": 1.0, "wind_str": 1.0, "crumble_delay": 8, "icicle_spd": 7, "ornament_gate": 15},
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
        ("Elder Frost", "Dreamer... you stand at the threshold of the Fourth Realm."),
        ("Elder Frost", "The Frozen Christmas Realm. The nightmare's final fortress."),
        ("Elder Frost", "You conquered fire. You survived shadow. You endured the storm."),
        ("Elder Frost", "But this place... this place is different. The cold here is not just in the air. It is in your bones."),
        ("Elder Frost", "I am Elder Frost, the last fragment of light your sleeping mind still holds."),
        ("Elder Frost", "Before you go, let me teach you how to survive what lies ahead."),
        ("Elder Frost", "MOVEMENT: Arrow keys or WASD to move. SPACE or UP to jump. SHIFT to sprint."),
        ("Elder Frost", "DOUBLE JUMP: You can jump again in mid-air. Master this -- it will save your life."),
        ("Elder Frost", "SNOWBALLS: Press F or X to throw snowballs at enemies. They fly the way you face."),
        ("Elder Frost", "STOMPING: Land on top of mushroom enemies to squash them. Classic trick, still works."),
        ("Elder Frost", "BOMB FIENDS: Black ticking bombs. Hit them with TWO snowballs before the fuse runs out!"),
        ("Elder Frost", "ORNAMENTS: Collect the golden ornaments scattered across the realm. You will need them to open the portal home."),
        ("Elder Frost", "The path ahead starts gentle... snowy hills, a few wandering monsters."),
        ("Elder Frost", "But do not be fooled. The nightmare is watching. It will throw everything at you."),
        ("Elder Frost", "Press ESC for settings. R to respawn. E to speak with us guides."),
        ("Elder Frost", "Now go, dreamer. Your bed is waiting. Christmas morning is waiting."),
    ],
    "cp1": [
        ("Holly", "Oh! You made it through the snowy hills! I am so glad."),
        ("Holly", "I am Holly -- a piece of your dreaming mind, just like Elder Frost."),
        ("Holly", "I have been watching you since the first realm. Fire, shadow, storm... you never quit."),
        ("Holly", "Listen -- ahead of you the ground turns to ice. The platforms... they are not stable."),
        ("Holly", "Some of them FLICKER in and out of existence. Glitch platforms, we call them."),
        ("Holly", "And the ice... it is slippery. You will slide if you are not careful."),
        ("Holly", "There are flying monsters too. They patrol the skies between the platforms."),
        ("Holly", "Oh, and watch out for the Bomb Fiends. One wrong move near them and... boom."),
        ("Holly", "I know it sounds scary. But you have already conquered three realms."),
        ("Holly", "What is a little ice compared to fire? You have got this, dreamer."),
    ],
    "cp2": [
        ("Jingle", "Well well well. Look who survived the ice fields. Name's Jingle."),
        ("Jingle", "I am the loud one. Holly is the sweet one. Elder Frost is the wise one. I am just... honest."),
        ("Jingle", "And honestly? What is ahead of you is rough."),
        ("Jingle", "Moving platforms. They slide and shift. Some go sideways, some go up and down."),
        ("Jingle", "Then there are the saw blades. Big spinning death circles. Do not touch them."),
        ("Jingle", "And here is the fun part -- there is a WALL you cannot jump over."),
        ("Jingle", "Two tall walls, close together. The only way up is to wall-jump between them."),
        ("Jingle", "Slide against one wall, jump off, hit the other, jump again. Zigzag your way up."),
        ("Jingle", "After that... there is a crumbling bridge. A long one. Over a pit."),
        ("Jingle", "The tiles break under your feet. You stop, you fall. Simple as that."),
        ("Jingle", "This realm used to be beautiful, you know. Christmas lights everywhere. Kids laughing."),
        ("Jingle", "The nightmare turned it all to ice and death. But every step you take cracks its grip."),
        ("Jingle", "Now get moving. Standing still is not an option anymore."),
    ],
    "cp3": [
        ("Elder Frost", "Dreamer... you crossed the crumbling bridge. You climbed those walls."),
        ("Elder Frost", "I felt the nightmare shudder when you made it through. It is afraid of you now."),
        ("Elder Frost", "Let me tell you something. When you first fell asleep, your mind was trapped in four realms."),
        ("Elder Frost", "Each realm was a fear given form. Fire was your anger. Shadow was your doubt."),
        ("Elder Frost", "Storm was your grief. And this frozen place... this is your loneliness."),
        ("Elder Frost", "That is why it is the hardest. Loneliness does not fight fair. It makes everything colder."),
        ("Elder Frost", "But look how far you have come. You are not alone -- Holly, Jingle, and I are here."),
        ("Elder Frost", "Ahead you will find teleporting platforms. They blink between two positions."),
        ("Elder Frost", "Time your jumps carefully. Land where they ARE, not where they WERE."),
        ("Elder Frost", "There are also collapsing platforms that crumble moments after you touch them."),
        ("Elder Frost", "Between the walls ahead, there is a hidden path upward. For the brave, a secret ornament waits at the top."),
        ("Elder Frost", "The portal home is not far now. I can feel its warmth from here."),
        ("Elder Frost", "Keep going. You are so close to waking up."),
    ],
    "cp4": [
        ("Holly", "Dreamer... this is the last checkpoint. There is nothing after this but the portal."),
        ("Holly", "I need you to listen carefully. What comes next is the worst of it."),
        ("Holly", "One long frozen road. The nightmare is throwing EVERYTHING it has left at you."),
        ("Holly", "A blizzard. The wind will push against you with every step. You have to fight through it."),
        ("Holly", "Saw blades patrol the ground. Pendulums swing from above. Ice geysers erupt beneath your feet."),
        ("Holly", "Icicles will fall from the sky when you pass under them. Keep moving. Never stop."),
        ("Holly", "I have watched so many dreamers reach this point and give up. Their minds just... stopped."),
        ("Holly", "The cold got to them. The wind broke them. They sat down and never got back up."),
        ("Holly", "But you are not like them. I have seen you fall a dozen times and get back up every single time."),
        ("Holly", "At the end of that road, there is a portal. A warm, golden light. That is your way home."),
        ("Holly", "Walk through it and the dream shatters. You wake up. Christmas morning. Safe and warm."),
        ("Holly", "Elder Frost, Jingle, and I -- we will all be watching."),
        ("Holly", "Now go, dreamer. Sprint into that blizzard. Do not look back. We believe in you."),
    ],
    "ending": [
        ("Elder Frost", "...You did it."),
        ("Elder Frost", "After everything -- the fire, the shadows, the storm, the ice -- you did it."),
        ("Elder Frost", "I have watched over countless dreamers trapped in these realms."),
        ("Elder Frost", "Most never make it past the second. The shadow breaks them. Their doubt swallows them whole."),
        ("Elder Frost", "But you... you kept going. Through every realm. Through every fear."),
        ("Holly", "I was so scared for you at the ice fields. When you slipped on that glitch platform..."),
        ("Holly", "And when the ground crumbled under you at the bridge. My heart stopped."),
        ("Holly", "But you always found your footing. You always got back up."),
        ("Jingle", "That final stretch though. Walking into that blizzard. Saw blades, pendulums, geysers..."),
        ("Jingle", "I was screaming the whole time. 'RUN, you stubborn little dreamer, RUN!'"),
        ("Jingle", "And you ran. Through all of it. Into the wind. Into the cold."),
        ("Jingle", "You beautiful, stubborn, impossible dreamer."),
        ("Elder Frost", "The four realms are crumbling now. The nightmare cannot survive without your fear."),
        ("Elder Frost", "And you have no fear left. You burned through it all."),
        ("Elder Frost", "We are fragments of your sleeping mind, dreamer. When you wake... we fade away."),
        ("Holly", "But that is okay. We were made for this moment. To help you get here."),
        ("Holly", "Thank you for not giving up. On us. On yourself."),
        ("Jingle", "Hey. When you wake up... eat some cookies for me, will ya? I never got to try any."),
        ("Elder Frost", "Close your eyes now. Let the warmth take you home."),
        ("Elder Frost", "Merry Christmas, dreamer."),
        ("", "..."),
        ("", "The cold fades. The wind dies. Everything goes quiet."),
        ("", "You feel warmth. Sunlight on your face. The smell of pine and cinnamon."),
        ("", "Your eyes flutter open. Christmas morning. Snow falling gently outside your window."),
        ("", "The tree is lit. Presents underneath. Everything exactly as it should be."),
        ("", "Was it all a dream?"),
        ("", "You reach for your nightstand. A single golden ornament sits there, glowing faintly."),
        ("", "It pulses once... twice... then fades to still."),
        ("", "You hold it close. It is warm."),
        ("", "You smile. Some dreams are worth remembering."),
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
    "blizzard":"blizzard.wav",
    "soul_rise":"soul_rise.wav","soul_land":"soul_land.wav",
}
MUSIC_FILE = "assets/audio/Level4Music.mp3"
ENDING_MUSIC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds", "ending.mp3")

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
        # Robe - cleaner layered shape
        robe_c = NPC_ROBE if "Elder" in self.name else XMAS_GREEN if "Holly" in self.name else XMAS_RED
        robe_dark = tuple(max(0,c-30) for c in robe_c)
        # Robe body with slight taper
        pygame.draw.polygon(surface, robe_c, [(bx+4,by+14),(bx+20,by+14),(bx+22,by+40),(bx,by+40)])
        pygame.draw.polygon(surface, robe_dark, [(bx+4,by+14),(bx+20,by+14),(bx+22,by+40),(bx,by+40)], 1)
        # Hood / head
        pygame.draw.circle(surface, (220,190,160), (bx+12, by+10), 8)
        # Hood arc
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
        # Name tag with shadow
        if not self.talked:
            font = pygame.font.SysFont("consolas", 10, bold=True)
            tag = font.render(self.name, True, XMAS_GOLD)
            tag_sh = font.render(self.name, True, (0,0,0))
            surface.blit(tag_sh, (bx + 12 - tag.get_width()//2 + 1, by - 13))
            surface.blit(tag, (bx + 12 - tag.get_width()//2, by - 14))
            # Pulsing/glowing exclamation mark
            exc_pulse = abs(math.sin(tick * 0.1)) * 0.5 + 0.5
            exc_c = lerp_color(XMAS_RED, (255,100,100), exc_pulse)
            exc_scale = int(exc_pulse * 2)
            exc_font = pygame.font.SysFont("consolas", 12 + exc_scale, bold=True)
            exc = exc_font.render("!", True, exc_c)
            exc_sh = exc_font.render("!", True, (0,0,0))
            surface.blit(exc_sh, (bx + 12 - exc.get_width()//2 + 1, by - 25))
            surface.blit(exc, (bx + 12 - exc.get_width()//2, by - 26))
        # Talk prompt with background pill
        if self.proximity_shown and not self.talked:
            font2 = pygame.font.SysFont("consolas", 11)
            prompt = font2.render("[E] Talk", True, SNOW_WHITE)
            pw, ph = prompt.get_width() + 8, prompt.get_height() + 4
            px2 = bx + 12 - pw // 2; py2 = by - 38
            pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pill.fill((0, 0, 0, 140))
            surface.blit(pill, (px2, py2))
            surface.blit(prompt, (px2 + 4, py2 + 2))

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
        # Rounded-feeling background (overlapping rects)
        bg = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        r = 6
        bg.fill((0,0,0,0))
        pygame.draw.rect(bg, (10, 10, 28, 225), (r, 0, box_rect.width - 2*r, box_rect.height))
        pygame.draw.rect(bg, (10, 10, 28, 225), (0, r, box_rect.width, box_rect.height - 2*r))
        for cx2,cy2 in [(r,r),(box_rect.width-r,r),(r,box_rect.height-r),(box_rect.width-r,box_rect.height-r)]:
            pygame.draw.circle(bg, (10, 10, 28, 225), (cx2, cy2), r)
        surface.blit(bg, box_rect.topleft)
        # Border
        pygame.draw.rect(surface, XMAS_GOLD, box_rect, 2, border_radius=6)
        # Corner ornaments
        for cx, cy in [(box_rect.left+3, box_rect.top+3), (box_rect.right-3, box_rect.top+3),
                       (box_rect.left+3, box_rect.bottom-3), (box_rect.right-3, box_rect.bottom-3)]:
            pygame.draw.circle(surface, XMAS_RED, (cx, cy), 5)
            pygame.draw.circle(surface, XMAS_GOLD, (cx, cy), 3)
        # Speaker name - more prominent with underline
        speaker, text = self.dialogues[self.index]
        font_name = pygame.font.SysFont("consolas", 17, bold=True)
        font_text = pygame.font.SysFont("consolas", 14)
        if speaker:
            name_c = XMAS_GOLD if "Elder" in speaker else XMAS_GREEN if "Holly" in speaker else XMAS_RED
            # Shadow
            surface.blit(font_name.render(speaker, True, (0,0,0)), (box_rect.x + 17, box_rect.y + 11))
            name_surf = font_name.render(speaker, True, name_c)
            surface.blit(name_surf, (box_rect.x + 16, box_rect.y + 10))
            # Underline accent
            pygame.draw.line(surface, name_c, (box_rect.x+16, box_rect.y+30), (box_rect.x+16+name_surf.get_width(), box_rect.y+30), 1)
            text_y = box_rect.y + 36
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
        # Page counter - subtle
        pg_font = pygame.font.SysFont("consolas", 11)
        pg = pg_font.render(f"{self.index+1}/{len(self.dialogues)}", True, (60,60,70))
        surface.blit(pg, (box_rect.x + 16, box_rect.bottom - 18))

# --- Player ---
class DamageFlash:
    """Red vignette border that fades over 20 frames on damage."""
    def __init__(self):
        self.timer = 20; self.max_timer = 20
    def update(self): self.timer -= 1; return self.timer > 0
    def draw(self, surface):
        a = int(160 * (self.timer / self.max_timer))
        if a <= 0: return
        w, h = surface.get_size(); t = 60  # border thickness
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(t):
            ia = int(a * (1 - i / t))
            if ia <= 0: continue
            pygame.draw.rect(s, (220, 30, 30, ia), (i, i, w - 2 * i, h - 2 * i), 1)
        surface.blit(s, (0, 0))

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
        # Wall slide / wall jump
        self.wall_sliding=False; self.wall_side=0  # -1=left wall, 1=right wall
        self.was_on_ground=False  # for landing detection
        # Squash & stretch
        self.squash_timer=0
        # Stats
        self.best_combo=0

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
        touching_wall = 0  # 0=none, -1=left wall, 1=right wall
        for plat in platforms:
            if not plat.is_active(): continue
            pr = plat.get_rect()
            if self.rect.colliderect(pr):
                if self.rect.bottom <= pr.top + 6: continue
                if self.vel_x > 0: self.rect.right = pr.left; touching_wall = 1
                elif self.vel_x < 0: self.rect.left = pr.right; touching_wall = -1
                self.vel_x = 0
        self.was_on_ground = self.on_ground
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
        # Wall slide detection
        pressing_into_wall = (touching_wall == 1 and (keys[pygame.K_RIGHT] or keys[pygame.K_d])) or \
                             (touching_wall == -1 and (keys[pygame.K_LEFT] or keys[pygame.K_a]))
        if not self.on_ground and self.vel_y > 0 and pressing_into_wall and touching_wall != 0:
            self.wall_sliding = True; self.wall_side = touching_wall
            self.vel_y = min(self.vel_y, 2)  # slow slide
            self.jump_count = 1  # allow wall jump
        else:
            self.wall_sliding = False; self.wall_side = 0
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
        # Squash timer update
        if self.on_ground and not self.was_on_ground: self.squash_timer=6
        if self.squash_timer>0: self.squash_timer-=1
        # Invincibility flicker
        if self.invincibility > 0 and (self.invincibility // 4) % 2 == 0: return
        # Dash afterimages + speed lines when dashing
        for idx_ai, (ax, ay, aa) in enumerate(self.dash_afterimages):
            ar = camera.apply(pygame.Rect(ax, ay, self.WIDTH, self.HEIGHT))
            s = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            s.fill((*ICE_BLUE, int(aa * 0.5)))
            surface.blit(s, ar.topleft)
        if self.dashing:
            # Blue speed lines behind player
            dsr = camera.apply(self.rect)
            for sl in range(5):
                slx = dsr.centerx + (-self.dash_dir) * (10 + sl * 8) + random.randint(-2, 2)
                sly = dsr.y + random.randint(2, self.HEIGHT - 2)
                sll = random.randint(8, 16)
                pygame.draw.line(surface, (100, 180, 255, 180), (slx, sly), (slx + (-self.dash_dir) * sll, sly), 2)
        # Sprint trail
        if self.sprinting and self.on_ground and abs(self.vel_x) > 3 and tick % 3 == 0:
            pass  # handled in _spawn_ambient
        sr = camera.apply(self.rect)
        # Squash & stretch visual adjustment (only draw rect, not collision)
        if self.vel_y<-3 and not self.on_ground:
            # Stretch: taller and thinner
            stretch=4; sr=sr.inflate(-4,stretch*2); sr.bottom+=stretch
        elif self.squash_timer>0:
            # Squash: wider and shorter
            sq=int(self.squash_timer*0.8); sr=sr.inflate(sq*2,-sq*2); sr.bottom+=sq
        if self.is_unreal:
            bc = xmas_cycle_color(tick, 0.12)
            pygame.draw.rect(surface, bc, sr)
            pulse = abs(math.sin(tick*0.15))*0.5+0.5
            pygame.draw.rect(surface, lerp_color(GOLD,WHITE,pulse), sr.inflate(4,4), 2)
            gs = 6+int(4*pulse)
            pygame.draw.rect(surface, tuple(max(0,min(255,int(c*0.3))) for c in bc), sr.inflate(gs,gs), 3)
        else:
            pygame.draw.rect(surface, XMAS_RED, sr)
            belt_y = sr.y+sr.height-14
            pygame.draw.rect(surface, BLACK, (sr.x,belt_y,sr.width,5))
            # Centered belt buckle
            bw,bh=8,7
            pygame.draw.rect(surface, XMAS_GOLD, (sr.centerx-bw//2, belt_y-1, bw, bh))
            pygame.draw.rect(surface, (180,140,30), (sr.centerx-bw//2+1, belt_y, bw-2, bh-2), 1)
            # White trim at bottom
            pygame.draw.rect(surface, WHITE, (sr.x,sr.bottom-4,sr.width,4))
        # Santa hat - smoother arc shape
        ht = sr.y-10
        hat_tip_x = sr.centerx + (6 if self.facing_right else -6)
        pygame.draw.polygon(surface, XMAS_RED, [
            (sr.x+1,sr.y+3),(sr.x+sr.width-1,sr.y+3),
            (sr.centerx + (4 if self.facing_right else -4), sr.y-4),
            (hat_tip_x, ht)])
        # Hat brim (white band)
        pygame.draw.rect(surface, WHITE, (sr.x-1,sr.y,sr.width+2,5))
        # Pompom
        pygame.draw.circle(surface, WHITE, (hat_tip_x, ht-2), 4)
        pygame.draw.circle(surface, SNOW_WHITE, (hat_tip_x-1, ht-3), 2)
        # Face / skin area
        face_y = sr.y + 8; face_h = 12
        pygame.draw.rect(surface, (230,195,160), (sr.x+2, face_y, sr.width-4, face_h))
        # Eyes
        ey = sr.y+11; pupil = BLACK if not self.is_unreal else GOLD
        if self.facing_right:
            pygame.draw.rect(surface,WHITE,(sr.x+15,ey,7,6)); pygame.draw.rect(surface,pupil,(sr.x+18,ey+1,4,4))
        else:
            pygame.draw.rect(surface,WHITE,(sr.x+6,ey,7,6)); pygame.draw.rect(surface,pupil,(sr.x+6,ey+1,4,4))
        # Small smile
        smile_x = sr.centerx + (2 if self.facing_right else -2)
        pygame.draw.arc(surface, (180,80,60), (smile_x-3, ey+5, 6, 4), 3.4, 6.0, 1)
        # Wall slide scratchy lines
        if self.wall_sliding:
            wx = sr.left if self.wall_side == -1 else sr.right
            for i in range(4):
                sy2 = sr.y + 5 + i * 8 + random.randint(-1, 1)
                pygame.draw.line(surface, WHITE, (wx, sy2), (wx + random.randint(-3, 3), sy2 + random.randint(4, 8)), 1)

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
        # Snow cap
        pygame.draw.rect(surface, SNOW_WHITE, (sr.x-2,sr.y-3,sr.width+4,5))
        rng=random.Random(sr.x*31+sr.y*17)
        for bx in range(sr.x, sr.right, 16):
            bw=random.Random(bx+sr.y).randint(8,12)
            pygame.draw.ellipse(surface, WHITE, (bx, sr.y-5, bw, 6))
        # Icicles
        for ix in range(sr.x+8, sr.right-8, rng.randint(18,28)):
            il=rng.randint(5,10); iw=rng.randint(2,4)
            pygame.draw.polygon(surface,(180,210,240),[(ix,sr.bottom),(ix+iw,sr.bottom),(ix+iw//2,sr.bottom+il)])

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
            pygame.draw.rect(surface,(int(240*f),int(245*f),int(255*f)),(sr.x-1,sr.y-3,sr.width+2,5))
            # Icicles when solid
            if self.alpha>200:
                rng=random.Random(self.rect.x*31+self.rect.y*17)
                for ix in range(sr.x+8, sr.right-8, rng.randint(18,26)):
                    il=rng.randint(4,8); iw=rng.randint(2,3)
                    ic=(int(180*f),int(210*f),int(240*f))
                    pygame.draw.polygon(surface,ic,[(ix,sr.bottom),(ix+iw,sr.bottom),(ix+iw//2,sr.bottom+il)])

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
            # Snow cap
            pygame.draw.rect(surface, SNOW_WHITE, (sr.x-1,sr.y-3,sr.width+2,5))
            # Icicles
            rng=random.Random(self.p1[0]*31+self.p1[1]*17)
            for ix in range(sr.x+10, sr.right-10, rng.randint(16,24)):
                il=rng.randint(4,8); iw=rng.randint(2,3)
                pygame.draw.polygon(surface,(180,210,240),[(ix,sr.bottom),(ix+iw,sr.bottom),(ix+iw//2,sr.bottom+il)])
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
        pygame.draw.rect(surface,SNOW_WHITE,(sr.x-1,sr.y-3,sr.width+2,5))
        # Icicles
        if self.stood==0:
            rng=random.Random(self.oy*31+self.rect.x*17)
            for ix in range(sr.x+8, sr.right-8, rng.randint(16,24)):
                il=rng.randint(5,9); iw=rng.randint(2,3)
                pygame.draw.polygon(surface,(180,210,240),[(ix,sr.bottom),(ix+iw,sr.bottom),(ix+iw//2,sr.bottom+il)])
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
        tc_dark=tuple(max(0,c-25) for c in tc)
        # Layered tree triangles with depth
        for w2,h2,yo in [(30,18,30),(24,16,20),(18,14,10)]:
            ty=sr.bottom-th-yo
            pts=[(cx,ty-h2),(cx-w2//2,ty),(cx+w2//2,ty)]
            pygame.draw.polygon(surface,tc,pts)
            # Darker edge on right side for depth
            pygame.draw.polygon(surface,tc_dark,[(cx,ty-h2),(cx+w2//2,ty),(cx+2,ty)])
            # Snow on top edge
            pygame.draw.line(surface,SNOW_WHITE,(cx-w2//4,ty-h2+3),(cx+w2//4,ty-h2+5),2)
        sy2=sr.bottom-th-10-14-4; sc=XMAS_GOLD if self.activated else DARK_GRAY
        pygame.draw.circle(surface,sc,(cx,sy2),5)
        if self.activated:
            pygame.draw.circle(surface,WHITE,(cx-1,sy2-1),2)
        if self.activated:
            i=abs(math.sin(math.radians(self.glow)))*0.6+0.4
            for j,(ox,oy,oc) in enumerate([(-9,-22,XMAS_RED),(7,-18,XMAS_GOLD),(-6,-32,CYAN),(9,-28,CANDY_PINK),(0,-42,XMAS_GOLD)]):
                if abs(math.sin(math.radians(self.glow+j*60)))>0.3:
                    pygame.draw.circle(surface,oc,(cx+ox,sr.bottom-th+oy),3)
                    pygame.draw.circle(surface,WHITE,(cx+ox-1,sr.bottom-th+oy-1),1)
            pygame.draw.rect(surface,tuple(int(v*i) for v in XMAS_GREEN),sr.inflate(8,8),2)
            # Waving flag
            flag_x = cx + 8; flag_y = sr.bottom - th - 10 - 12 - 8
            pygame.draw.line(surface, BROWN, (flag_x, flag_y), (flag_x, flag_y - 16), 2)
            wave = int(math.sin(self.glow * 0.05) * 3)
            pts = [(flag_x, flag_y - 16), (flag_x + 12 + wave, flag_y - 13),
                   (flag_x + 10 + wave, flag_y - 8), (flag_x, flag_y - 6)]
            pygame.draw.polygon(surface, XMAS_RED, pts)

# --- Exit Door (Magical Portal) ---
class ExitDoor:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x,y-20,60,90); self.pulse=0; self.particles=[]
        self.orbs=[]; self.rune_angle=0
        self.gifts=[((x-25,y+62),(200,40,40)),((x+5,y+67),(40,180,60)),((x+40,y+60),(50,120,255)),((x+65,y+64),(255,200,50)),((x-10,y+72),(180,60,200)),((x+55,y+70),(255,160,50))]
    def update(self):
        self.pulse=(self.pulse+2)%360
        self.rune_angle=(self.rune_angle+0.8)%360
        # Sparkle particles rising from portal
        if random.random()<0.6:
            px=self.rect.x+random.randint(2,self.rect.width-2)
            col=random.choice([(255,220,100),(200,180,255),(150,220,255),(255,200,80)])
            self.particles.append([px,float(self.rect.bottom-5),random.uniform(-0.4,0.4),random.uniform(-1.8,-0.6),random.randint(35,60),col])
        # Floating orbs that circle the portal
        if len(self.orbs)<6 and random.random()<0.03:
            a=random.uniform(0,math.pi*2)
            self.orbs.append([a,random.uniform(45,65),random.uniform(0.02,0.04),random.randint(120,200)])
        self.particles=[[x+vx,y+vy,vx,vy,t-1,c] for x,y,vx,vy,t,c in self.particles if t>1]
        self.orbs=[[a+s,r,s,t-1] for a,r,s,t in self.orbs if t>1]
    def check(self, player): return player.rect.colliderect(self.rect)
    def draw(self, surface, camera, tick=0, has_enough=False):
        sr=camera.apply(self.rect); p=abs(math.sin(math.radians(self.pulse)))
        bright=1.0 if has_enough else 0.35
        cx,cy=sr.centerx,sr.centery
        # Soft background glow (large, warm)
        for gr,ga,gc in [(80,25,(255,200,100)),(60,35,(200,160,255)),(45,50,(150,200,255))]:
            gs=pygame.Surface((gr*2,gr*2),pygame.SRCALPHA)
            al=int(ga*bright*(0.6+0.4*p))
            pygame.draw.circle(gs,(*gc,al),(gr,gr),gr)
            surface.blit(gs,(cx-gr,cy-10-gr))
        # Light rays fanning upward
        rs=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
        for i in range(8):
            ang=math.radians(-90+(-56+i*16)+math.sin(tick*0.015+i*0.7)*6)
            length=80+20*math.sin(tick*0.02+i*1.3)
            ex=cx+int(math.cos(ang)*length); ey=cy-10+int(math.sin(ang)*length)
            al=int((12+8*p)*bright)
            col=(255,220,140,al) if i%2==0 else (180,160,255,al)
            pygame.draw.polygon(rs,col,[(cx-5,cy-5),(cx+5,cy-5),(ex,ey)])
        surface.blit(rs,(0,0))
        # Portal archway — outer stone frame
        stone_col=lerp_color((70,60,90),(120,110,150),0.3+0.2*p*bright)
        # Pillars
        pw,ph=10,sr.height-15
        pygame.draw.rect(surface,stone_col,(sr.x-4,sr.y+18,pw,ph))
        pygame.draw.rect(surface,stone_col,(sr.right-pw+4,sr.y+18,pw,ph))
        # Pillar highlights
        hl=lerp_color(stone_col,(200,190,220),0.3)
        pygame.draw.rect(surface,hl,(sr.x-2,sr.y+18,3,ph))
        pygame.draw.rect(surface,hl,(sr.right-pw+6,sr.y+18,3,ph))
        # Arch top
        pygame.draw.ellipse(surface,stone_col,(sr.x-4,sr.y-2,sr.width+8,44))
        # Inner portal void — shimmering gradient
        inner=pygame.Rect(sr.x+6,sr.y+20,sr.width-12,sr.height-24)
        void=pygame.Surface((inner.width,inner.height),pygame.SRCALPHA)
        # Vertical gradient from deep blue to warm light
        for row in range(inner.height):
            t2=row/max(1,inner.height-1)
            if has_enough:
                rc=lerp_color((20,10,60),(255,220,140),t2*0.8+0.2*p)
                al=200+int(55*p)
            else:
                rc=lerp_color((15,8,40),(60,50,80),t2)
                al=160
            pygame.draw.line(void,(*rc,min(255,al)),  (0,row),(inner.width,row))
        surface.blit(void,inner.topleft)
        # Elliptical top of inner void
        inner_top=pygame.Rect(sr.x+6,sr.y+6,sr.width-12,34)
        et=pygame.Surface((inner_top.width,inner_top.height),pygame.SRCALPHA)
        if has_enough:
            ec=lerp_color((20,10,60),(200,180,255),0.3+0.2*p)
            pygame.draw.ellipse(et,(*ec,200),et.get_rect())
        else:
            pygame.draw.ellipse(et,(15,8,40,160),et.get_rect())
        surface.blit(et,inner_top.topleft)
        # Swirling energy lines inside portal
        if has_enough:
            es=pygame.Surface((inner.width,inner.height),pygame.SRCALPHA)
            for j in range(3):
                pts=[]
                for k in range(8):
                    ky=k*inner.height//7
                    kx=inner.width//2+int(math.sin(tick*0.03+j*2.1+k*0.8)*inner.width*0.3)
                    pts.append((kx,ky))
                if len(pts)>1:
                    col=[(255,220,120),(180,160,255),(130,220,255)][j]
                    pygame.draw.lines(es,(*col,int(60+40*p)),False,pts,2)
            surface.blit(es,inner.topleft)
        # Rune circle around arch
        if has_enough:
            rune_s=pygame.Surface((sr.width+40,sr.height+20),pygame.SRCALPHA)
            rcx,rcy=(sr.width+40)//2,(sr.height+20)//2-5
            rr=max(sr.width,sr.height)//2+12
            for i in range(12):
                a=math.radians(self.rune_angle+i*30)
                rx=rcx+int(math.cos(a)*rr); ry=rcy+int(math.sin(a)*rr)
                al=int((80+60*math.sin(tick*0.05+i))*bright)
                pygame.draw.circle(rune_s,(255,220,160,max(0,min(255,al))),(rx,ry),2)
            surface.blit(rune_s,(sr.x-20,sr.y-10))
        # Ornate arch border
        border_col=lerp_color((160,140,80),(255,220,120),p*bright) if has_enough else lerp_color((80,70,60),(140,130,100),0.3)
        pygame.draw.ellipse(surface,border_col,(sr.x-6,sr.y-4,sr.width+12,48),3)
        pygame.draw.rect(surface,border_col,(sr.x-6,sr.y+18,sr.width+12,sr.height-18),3)
        # Corner decorations
        for dx,dy in [(-6,18),(sr.width+2,18),(-6,sr.height-2),(sr.width+2,sr.height-2)]:
            pygame.draw.circle(surface,lerp_color(border_col,(255,255,200),0.3*p),(sr.x+dx,sr.y+dy),4)
        # Keystone at top of arch
        ks_col=lerp_color((200,180,60),(255,240,120),p*bright) if has_enough else (120,110,80)
        kpts=[(cx,sr.y-8),(cx-7,sr.y+4),(cx+7,sr.y+4)]
        pygame.draw.polygon(surface,ks_col,kpts)
        pygame.draw.polygon(surface,(255,255,200) if has_enough else (160,150,120),kpts,2)
        # Floating orbs
        for a,r,_,t in self.orbs:
            ox=cx+int(math.cos(a)*r); oy=cy-10+int(math.sin(a)*r*0.6)
            al=min(255,int(t*2.5*bright))
            os2=pygame.Surface((10,10),pygame.SRCALPHA)
            pygame.draw.circle(os2,(255,220,160,al),(5,5),4)
            pygame.draw.circle(os2,(255,255,220,al//2),(5,5),2)
            surface.blit(os2,(ox-5,oy-5))
        # Sparkle particles
        for px,py,_,_,pt,pc in self.particles:
            pp=camera.apply(pygame.Rect(int(px),int(py),1,1))
            al=min(255,int(pt*5*bright))
            sz=1+int(pt/20)
            ps=pygame.Surface((sz*2,sz*2),pygame.SRCALPHA)
            pygame.draw.circle(ps,(*pc,al),(sz,sz),sz)
            surface.blit(ps,(pp.x-sz,pp.y-sz))
        # Gift boxes at base (decorative)
        for (gx,gy),gc in self.gifts:
            gr2=camera.apply(pygame.Rect(gx,gy,14,14))
            pygame.draw.rect(surface,gc,gr2,border_radius=2)
            rib=lerp_color(gc,(255,255,255),0.5)
            pygame.draw.rect(surface,rib,(gr2.centerx-1,gr2.y,2,14))
            pygame.draw.rect(surface,rib,(gr2.x,gr2.centery-1,14,2))
            # Tiny bow
            pygame.draw.circle(surface,rib,(gr2.centerx-2,gr2.y),2)
            pygame.draw.circle(surface,rib,(gr2.centerx+2,gr2.y),2)
        # Text above
        font=pygame.font.SysFont("consolas",11,bold=True)
        if has_enough:
            lbl=font.render("The way home...",True,XMAS_GOLD)
        else:
            lbl=font.render("",True,WHITE)
        if lbl.get_width()>0:
            ly=sr.top-22+int(math.sin(tick*0.05)*3)
            surface.blit(lbl,(cx-lbl.get_width()//2,ly))

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
        # Shadow underneath
        pygame.draw.ellipse(surface,(0,0,0,80),(b.x+2,b.bottom+1,b.width-4,6))
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
        # Shadow underneath
        pygame.draw.ellipse(surface,(0,0,0,60),(sr.x+3,sr.bottom+2,sr.width-6,5))
        pygame.draw.ellipse(surface,self.color,sr)
        pygame.draw.arc(surface,GRAY,(sr.centerx-4,sr.y-8,8,10),0,math.pi,2)
        wy=sr.centery-2+int(math.sin(tick*0.3)*3)
        pygame.draw.polygon(surface,self.color,[(sr.left,wy),(sr.left-10,wy-8),(sr.left+5,wy)])
        pygame.draw.polygon(surface,self.color,[(sr.right,wy),(sr.right+10,wy-8),(sr.right-5,wy)])
        ey=sr.y+6; ex=sr.centerx-3 if self.dir>=0 else sr.centerx-3
        lx=sr.centerx+3; rx=sr.centerx-9
        if self.dir>=0: ex=sr.centerx+1
        else: ex=sr.centerx-7
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
        # Shadow underneath
        pygame.draw.ellipse(surface,(0,0,0,60),(sr.x+2,sr.bottom+bob+1,sr.width-4,5))
        pygame.draw.rect(surface,BROWN,(sr.x+4,sr.centery+bob,sr.width-8,sr.height//2))
        cr=pygame.Rect(sr.x-2,sr.y+bob,sr.width+4,sr.height//2+4)
        pygame.draw.ellipse(surface,MUSHROOM_RED,cr)
        for sx2,sy2,r2 in [(cr.x+6,cr.y+5,3),(cr.right-8,cr.y+4,3),(cr.centerx,cr.y+2,2)]:
            pygame.draw.circle(surface,WHITE,(sx2,sy2+bob),r2)
        pygame.draw.ellipse(surface,DARK_BROWN,(sr.x+2,sr.bottom+bob-4,8,5))
        pygame.draw.ellipse(surface,DARK_BROWN,(sr.right-10,sr.bottom+bob-4,8,5))
        ey2=sr.centery-2+bob
        elx=sr.centerx-6; erx=sr.centerx+6
        pygame.draw.circle(surface,WHITE,(elx,ey2),4); pygame.draw.circle(surface,WHITE,(erx,ey2),4)
        po=1 if self.direction>0 else -1
        pygame.draw.circle(surface,BLACK,(elx+po,ey2+1),2); pygame.draw.circle(surface,BLACK,(erx+po,ey2+1),2)

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

        pygame.draw.ellipse(surface, (15, 15, 15), (cx - br, sr.bottom + 2, br * 2, 6))
        pygame.draw.circle(surface, body_c, (cx, cy), br)
        pygame.draw.circle(surface, BOMB_GRAY, (cx - 4, cy - 4), br // 3)

        fuse_base = (cx + 2, cy - br + 2); fuse_tip = (cx + 8, cy - br - 10)
        pygame.draw.line(surface, BROWN, fuse_base, fuse_tip, 2)
        if self.state == "ticking":
            sc = FUSE_ORANGE if (tick // 3) % 2 == 0 else FUSE_RED
            # Larger, more visible spark with glow
            pygame.draw.circle(surface, (255,200,80), fuse_tip, 8)
            pygame.draw.circle(surface, sc, fuse_tip, 6)
            pygame.draw.circle(surface, XMAS_GOLD, fuse_tip, 3)
            pygame.draw.circle(surface, WHITE, fuse_tip, 1)
            # Spark lines
            for si in range(4):
                sa=tick*0.5+si*math.pi/2
                sx2=fuse_tip[0]+int(math.cos(sa)*8); sy2=fuse_tip[1]+int(math.sin(sa)*8)
                pygame.draw.line(surface, FUSE_ORANGE, fuse_tip, (sx2,sy2), 1)
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
        super().__init__(x, y, w, h, color=(170, 215, 245))
    def on_player_land(self, player): player.on_ice = True
    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < -10 or sr.left > SCREEN_WIDTH + 10: return
        # Lighter icy blue body
        pygame.draw.rect(surface, self.color, sr)
        # Shimmer effect - moving highlight
        tick = pygame.time.get_ticks()//30
        shimmer_x = sr.x + (tick * 2) % (sr.width + 40) - 20
        if sr.x <= shimmer_x <= sr.right:
            for dx in range(-6, 7):
                a = max(0, 255 - abs(dx) * 40)
                if a > 0 and sr.x <= shimmer_x + dx <= sr.right:
                    pygame.draw.line(surface, (220, 240, 255), (shimmer_x+dx, sr.y+1), (shimmer_x+dx, sr.bottom-1))
        # Snow cap
        pygame.draw.rect(surface, (220, 235, 255), (sr.x-1, sr.y-3, sr.width+2, 5))
        # Ice streaks
        for ix in range(sr.x + 8, sr.right - 8, 14):
            pygame.draw.line(surface, (210, 235, 255), (ix, sr.y + 4), (ix + 6, sr.bottom - 2), 1)
        # Icicles
        rng=random.Random(self.rect.x*31+self.rect.y*17)
        for ix in range(sr.x+6, sr.right-6, rng.randint(14,22)):
            il=rng.randint(6,12); iw=rng.randint(2,4)
            pygame.draw.polygon(surface,(190,220,250),[(ix,sr.bottom),(ix+iw,sr.bottom),(ix+iw//2,sr.bottom+il)])

# --- Falling Icicle ---
class Icicle:
    WIDTH, HEIGHT = 10, 30
    def __init__(self, x, y, max_fall_speed=None):
        self.x, self.y = x, y
        self.rect = pygame.Rect(x - self.WIDTH // 2, y, self.WIDTH, self.HEIGHT)
        self.state = "idle"  # idle / shaking / falling / done
        self.shake_timer = 0; self.fall_speed = 0
        self.max_fall_speed = max_fall_speed if max_fall_speed is not None else ICICLE_FALL_SPEED
    def update(self):
        if self.state == "shaking":
            self.shake_timer -= 1
            if self.shake_timer <= 0: self.state = "falling"; self.fall_speed = 2
        elif self.state == "falling":
            self.fall_speed = min(self.fall_speed + 0.4, self.max_fall_speed)
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


# --- Saw Blade Obstacle ---
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
    def check_hit(self, player):
        if not player.alive: return False
        return self.rect.colliderect(player.rect)
    def draw(self, surface, camera, tick):
        sr=camera.apply(self.rect)
        if sr.right<-30 or sr.left>SCREEN_WIDTH+30: return
        cx,cy=sr.centerx,sr.centery; r=self.RADIUS
        # Danger glow
        glow_pulse=abs(math.sin(tick*0.1))*0.4+0.3
        gs=pygame.Surface((r*4+8,r*4+8),pygame.SRCALPHA)
        pygame.draw.circle(gs,(255,80,30,int(40*glow_pulse)),(r*2+4,r*2+4),r+8)
        pygame.draw.circle(gs,(255,50,20,int(25*glow_pulse)),(r*2+4,r*2+4),r+14)
        surface.blit(gs,(cx-r*2-4,cy-r*2-4))
        # Main body - red/orange danger colors
        pygame.draw.circle(surface,(180,50,30),(cx,cy),r)
        pygame.draw.circle(surface,(220,80,40),(cx,cy),r-3)
        pygame.draw.circle(surface,(120,30,20),(cx,cy),5)
        # Teeth
        for i in range(8):
            a=self.angle+i*math.pi/4
            tx=cx+int(math.cos(a)*(r+5)); ty=cy+int(math.sin(a)*(r+5))
            bx1=cx+int(math.cos(a-0.3)*r); by1=cy+int(math.sin(a-0.3)*r)
            bx2=cx+int(math.cos(a+0.3)*r); by2=cy+int(math.sin(a+0.3)*r)
            pygame.draw.polygon(surface,(200,200,210),[(tx,ty),(bx1,by1),(bx2,by2)])
            pygame.draw.polygon(surface,(160,160,170),[(tx,ty),(bx1,by1),(bx2,by2)],1)

# --- Crumbling Bridge ---
class CrumblingBridge:
    TILE_W=40; TILE_H=20; SHAKE_FRAMES=24; RESPAWN_FRAMES=120
    def __init__(self, x, y, width=400, tile_delay=8):
        self.x,self.y,self.width=x,y,width
        self.n_tiles=width//self.TILE_W; self.triggered=False; self.trigger_index=0
        self.tile_delay=tile_delay; self.respawn_timer=0
        self.tiles=[]  # list of {rect, state, timer, vel_y}
        for i in range(self.n_tiles):
            self.tiles.append({"rect":pygame.Rect(x+i*self.TILE_W,y,self.TILE_W,self.TILE_H),
                "state":"solid","timer":0,"vel_y":0.0,"delay":i*tile_delay})
    def get_rects(self):
        return [t["rect"] for t in self.tiles if t["state"] in ("solid","shaking")]
    def _reset_tiles(self):
        self.triggered=False; self.respawn_timer=0
        for i,t in enumerate(self.tiles):
            t["rect"].x=self.x+i*self.TILE_W; t["rect"].y=self.y
            t["state"]="solid"; t["timer"]=0; t["vel_y"]=0.0; t["delay"]=i*self.tile_delay
    def update(self):
        if not self.triggered: return
        all_gone=True
        for t in self.tiles:
            if t["state"]=="solid":
                all_gone=False; t["timer"]+=1
                if t["timer"]>=t["delay"]:
                    t["state"]="shaking"; t["timer"]=0
            elif t["state"]=="shaking":
                all_gone=False; t["timer"]+=1
                if t["timer"]>=self.SHAKE_FRAMES: t["state"]="falling"; t["vel_y"]=1.0
            elif t["state"]=="falling":
                all_gone=False; t["vel_y"]+=0.5; t["rect"].y+=int(t["vel_y"])
                if t["rect"].y>DEATH_Y: t["state"]="gone"
        if all_gone:
            self.respawn_timer+=1
            if self.respawn_timer>=self.RESPAWN_FRAMES: self._reset_tiles()
    def trigger(self): self.triggered=True
    def check_standing(self, player):
        if not player.alive or self.triggered: return
        for t in self.tiles:
            if t["state"]=="solid":
                pr=t["rect"]
                if (player.rect.bottom>=pr.top and player.rect.bottom<=pr.top+10
                    and player.rect.right>pr.left and player.rect.left<pr.right):
                    self.trigger(); return
    def draw(self, surface, camera, tick):
        for t in self.tiles:
            if t["state"]=="gone": continue
            r=t["rect"].copy()
            if t["state"]=="shaking": r.x+=random.randint(-2,2)
            sr=camera.apply(r)
            if sr.right<-10 or sr.left>SCREEN_WIDTH+10: continue
            c=BROWN if t["state"]!="falling" else lerp_color(BROWN,(80,40,20),0.5)
            pygame.draw.rect(surface,c,sr)
            # Stone/brick texture: horizontal mortar line + vertical dividers
            mc=(100,65,35) if t["state"]!="falling" else (60,40,20)
            pygame.draw.line(surface,mc,(sr.x,sr.centery),(sr.right,sr.centery),1)
            for bx in range(sr.x+10,sr.right-5,20):
                pygame.draw.line(surface,mc,(bx,sr.y),(bx,sr.centery),1)
            for bx in range(sr.x+20,sr.right-5,20):
                pygame.draw.line(surface,mc,(bx,sr.centery),(bx,sr.bottom),1)
            pygame.draw.rect(surface,SNOW_WHITE,(sr.x-1,sr.y-3,sr.width+2,4))
            if t["state"]=="shaking":
                pygame.draw.line(surface,XMAS_RED,(sr.centerx-5,sr.y),(sr.centerx+3,sr.bottom),1)

# --- Wind Particle (visual streaks) ---
class WindParticle:
    def __init__(self, x, y, strength):
        self.x,self.y=float(x),float(y); self.strength=strength
        self.lifetime=random.randint(10,25); self.length=random.randint(12,30)
        self.alpha=random.uniform(0.3,0.8)
    def update(self):
        self.x+=self.strength*2; self.y+=random.uniform(-0.3,0.3); self.lifetime-=1
        return self.lifetime>0
    def draw(self, surface, camera):
        sr=camera.apply(pygame.Rect(int(self.x),int(self.y),1,1))
        a=int(200*self.alpha*(self.lifetime/25))
        if a>0:
            pygame.draw.line(surface,(255,255,255,min(255,a)),(sr.x,sr.y),(sr.x+self.length,sr.y),1)

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

# --- Pendulum ---
class Pendulum:
    def __init__(self, x, y, length=100, speed=0.03):
        self.ax,self.ay=x,y; self.length=length; self.speed=speed; self.angle=0; self.tick=0; self.radius=12
    def update(self):
        self.tick+=1; self.angle=math.sin(self.tick*self.speed)*math.pi/3
    @property
    def bx(self): return self.ax+int(math.sin(self.angle)*self.length)
    @property
    def by(self): return self.ay+int(math.cos(self.angle)*self.length)
    @property
    def rect(self): return pygame.Rect(self.bx-self.radius,self.by-self.radius,self.radius*2,self.radius*2)
    def check_hit(self, player):
        if not player.alive or player.invincibility>0 or player.is_unreal: return False
        return self.rect.colliderect(player.rect)
    def draw(self, surface, camera, tick):
        ap=camera.apply(pygame.Rect(self.ax,self.ay,1,1)); bp=camera.apply(pygame.Rect(self.bx,self.by,1,1))
        if bp.x<-50 or bp.x>SCREEN_WIDTH+50: return
        pygame.draw.line(surface,DARK_GRAY,(ap.x,ap.y),(bp.x,bp.y),3)
        for i in range(0,self.length,12):
            t=i/self.length; cx=ap.x+int((bp.x-ap.x)*t); cy=ap.y+int((bp.y-ap.y)*t)
            pygame.draw.circle(surface,GRAY,(cx,cy),2)
        pygame.draw.circle(surface,BOMB_BLACK,(bp.x,bp.y),self.radius)
        pygame.draw.circle(surface,(80,80,90),(bp.x,bp.y),self.radius,2)
        for i in range(6):
            sa=i*math.pi/3+tick*0.1; sx=bp.x+int(math.cos(sa)*(self.radius+4)); sy=bp.y+int(math.sin(sa)*(self.radius+4))
            pygame.draw.polygon(surface,DARK_GRAY,[(sx,sy),(sx+3,sy-5),(sx-3,sy-5)])

# --- Ice Geyser ---
class IceGeyser:
    def __init__(self, x, y, interval=100):
        self.x,self.y=x,y; self.interval=interval; self.tick=0; self.state="idle"
        self.warn_time=20; self.erupt_time=30; self.timer=0; self.particles=[]
        self.rect=pygame.Rect(x-12,y-8,24,8)
    def update(self):
        self.tick+=1
        if self.state=="idle":
            self.timer+=1
            if self.timer>=self.interval: self.state="warning"; self.timer=0
        elif self.state=="warning":
            self.timer+=1
            if self.timer>=self.warn_time: self.state="erupting"; self.timer=0
        elif self.state=="erupting":
            self.timer+=1
            for _ in range(3):
                self.particles.append([self.x+random.randint(-6,6),float(self.y),random.uniform(-1,1),random.uniform(-8,-4),random.randint(15,25)])
            if self.timer>=self.erupt_time: self.state="idle"; self.timer=0
        self.particles=[[px+vx,py+vy,vx,vy*0.95,t-1] for px,py,vx,vy,t in self.particles if t>1]
    def check_hit(self, player):
        if not player.alive or player.invincibility>0 or player.is_unreal: return False
        if self.state!="erupting": return False
        erupt_rect=pygame.Rect(self.x-14,self.y-100,28,100)
        return player.rect.colliderect(erupt_rect)
    def draw(self, surface, camera, tick):
        bp=camera.apply(self.rect)
        if bp.x<-50 or bp.x>SCREEN_WIDTH+50: return
        cx=bp.x+bp.width//2
        # Base
        pygame.draw.ellipse(surface,ICE_BLUE,(cx-14,bp.y,28,10))
        pygame.draw.ellipse(surface,(100,160,200),(cx-10,bp.y+2,20,6))
        # Warning glow
        if self.state=="warning":
            al=int(abs(math.sin(self.timer*0.3))*120)
            ws=pygame.Surface((30,12),pygame.SRCALPHA); ws.fill((140,200,240,al))
            surface.blit(ws,(cx-15,bp.y-2))
        # Eruption particles
        for px,py,_,_,pt in self.particles:
            pp=camera.apply(pygame.Rect(int(px),int(py),1,1))
            al=min(255,pt*12); r=max(1,pt//8)
            pygame.draw.circle(surface,(180,220,255),(pp.x,pp.y),r)

# --- Level Builder ---
def create_level(diff_key="hard"):
    diff = DIFFICULTY[diff_key]
    plats, cps, mons, pws, npcs = [], [], [], [], []
    ornaments, icicles, heart_pickups = [], [], []
    saw_blades, crumbling_bridges = [], []
    pendulums, ice_geysers = [], []
    wind_zones = []  # list of (x_start, x_end, wind_strength)
    ms = diff["mon_spd"]
    ps = diff["plat_spd"]
    go = diff["glitch_on"]
    gf = diff["glitch_off"]
    cd = diff["collapse_delay"]
    ti = diff["tp_interval"]
    ss = diff["saw_spd"]
    ws = diff["wind_str"]
    crd = diff["crumble_delay"]
    isp = diff["icicle_spd"]

    # ---- Section 1: Snowy Intro (0-2000) ----
    plats.append(Platform(0, 500, 400, 40))
    npcs.append(NPC(80, 500, "intro", "Elder Frost"))
    plats.append(Platform(550, 500, 180, 40))
    plats.append(Platform(850, 455, 160, 40))
    plats.append(Platform(1150, 410, 160, 40))
    plats.append(Platform(1450, 455, 200, 40))  # rest platform (no enemy)
    plats.append(Platform(1750, 500, 300, 40))
    mons.append(MushroomMonster(250, 474, 50, 370, speed=1.0*ms))
    mons.append(Monster(1770, 474, 1750, 2020, speed=1.2*ms))
    cps.append(Checkpoint(1800, 500))
    npcs.append(NPC(1850, 500, "cp1", "Holly"))
    heart_pickups.append(HeartPickup(1200, 380))

    # ---- Section 2: Icy platforms (2200-4000) ----
    plats.append(Platform(2200, 460, 140, 30))
    plats.append(GlitchPlatform(2480, 420, 130, 30, on_time=go+10, off_time=gf, offset=0))
    plats.append(Platform(2750, 440, 140, 30))  # rest platform
    plats.append(GlitchPlatform(3020, 375, 130, 30, on_time=go, off_time=gf, offset=40))
    plats.append(Platform(3280, 420, 130, 30))
    plats.append(GlitchPlatform(3520, 375, 140, 30, on_time=go-5, off_time=gf-5, offset=20))
    plats.append(Platform(3780, 375, 180, 30))
    mons.append(FlyingMonster(2900, 340, 2600, 3100, speed=0.8*ms, amplitude=30))
    mons.append(BombMonster(3300, 390, 3280, 3400, speed=0.7, diff=diff))
    pws.append(Powerup(2300, 430))
    # Ice overlays
    plats.append(IcePlatform(2750, 440, 140, 30))
    plats.append(IcePlatform(3780, 375, 180, 30))
    cps.append(Checkpoint(3810, 375))
    npcs.append(NPC(3850, 375, "cp2", "Jingle"))
    heart_pickups.append(HeartPickup(3050, 345))

    # ---- Section 3: Moving platforms (4100-6200) ----
    plats.append(MovingPlatform(4100, 400, 4300, 400, 130, 30, speed=1.2*ps))
    plats.append(Platform(4500, 360, 140, 30))  # rest platform
    plats.append(MovingPlatform(4780, 320, 4780, 450, 130, 30, speed=1.0*ps))
    plats.append(MovingPlatform(5050, 380, 5280, 380, 140, 30, speed=1.3*ps))
    plats.append(Platform(5480, 420, 140, 30))
    # Wall-jump MANDATORY climb — two facing walls, the ONLY way forward
    # Player must wall-jump between them to reach the top platform and continue
    plats.append(Platform(5660, 200, 30, 220))  # left wall (tall)
    plats.append(Platform(5760, 200, 30, 220))  # right wall (tall) ~100px gap
    # Ornaments going upward between walls as a visual guide
    ornaments.append(Ornament(5710, 370))
    ornaments.append(Ornament(5710, 300))
    ornaments.append(Ornament(5710, 230))
    plats.append(Platform(5640, 170, 180, 30))  # top platform — main path continues here
    # NO bypass platform — wall jump is the ONLY way forward
    plats.append(Platform(5900, 240, 130, 30))  # step down from wall-jump top
    plats.append(MovingPlatform(6180, 290, 6380, 290, 130, 30, speed=1.3*ps))
    plats.append(Platform(6550, 350, 220, 30))
    mons.append(MushroomMonster(4510, 332, 4500, 4630, speed=1.3*ms))
    mons.append(FlyingMonster(5200, 300, 5050, 5400, speed=1.0*ms, amplitude=35))
    mons.append(BombMonster(6570, 320, 6550, 6750, speed=0.9, diff=diff))
    plats.append(IcePlatform(4500, 360, 140, 30))
    plats.append(IcePlatform(5480, 420, 140, 30))
    pws.append(Powerup(5150, 340))
    cps.append(Checkpoint(6580, 350))
    npcs.append(NPC(6620, 350, "cp3", "Elder Frost"))
    heart_pickups.append(HeartPickup(5500, 390))

    # ---- Section 4: Teleport challenge (7700-8800) ----
    plats.append(TeleportPlatform(7700, 350, 7700, 250, 130, 30, interval=ti+20))
    plats.append(Platform(7970, 320, 140, 30))  # rest
    plats.append(CollapsingPlatform(8130, 300, 130, 30, delay=cd+10))
    plats.append(GlitchPlatform(8390, 350, 120, 30, on_time=go-10, off_time=gf-10, offset=0))
    plats.append(TeleportPlatform(8650, 300, 8750, 400, 130, 30, interval=ti))
    plats.append(Platform(8950, 350, 140, 30))  # rest
    plats.append(CollapsingPlatform(9190, 300, 130, 30, delay=cd))
    # Wall-jump shortcut in section 4 (optional, bonus ornament on top)
    plats.append(Platform(9370, 200, 30, 180))  # tall thin wall (left)
    plats.append(Platform(9470, 200, 30, 180))  # tall thin wall (right)
    plats.append(Platform(9390, 160, 90, 30))   # secret platform on top
    ornaments.append(Ornament(9430, 130))        # bonus ornament
    plats.append(Platform(9370, 350, 140, 30))  # normal path continues here
    plats.append(Platform(9600, 300, 140, 30))  # step to next platform
    plats.append(TeleportPlatform(9850, 300, 9850, 400, 120, 30, interval=ti-10))
    plats.append(Platform(10070, 350, 220, 40))
    mons.append(FlyingMonster(8150, 250, 7950, 8450, speed=1.2*ms, amplitude=40))
    mons.append(MushroomMonster(8960, 322, 8950, 9080, speed=1.4*ms))
    mons.append(BombMonster(9210, 270, 9190, 9310, speed=0.8, diff=diff))
    pws.append(Powerup(9000, 310))
    cps.append(Checkpoint(10090, 350))
    npcs.append(NPC(10130, 350, "cp4", "Holly"))
    heart_pickups.append(HeartPickup(8650, 270))

    # ---- Section 5: Final gauntlet (10350-13400) ----
    plats.append(GlitchPlatform(10350, 320, 120, 30, on_time=go-15, off_time=gf-10, offset=0))
    plats.append(MovingPlatform(10600, 280, 10600, 390, 120, 30, speed=1.4*ps))
    plats.append(Platform(10850, 340, 140, 30))  # brief rest
    plats.append(CollapsingPlatform(11100, 320, 120, 30, delay=cd-5))
    plats.append(GlitchPlatform(11340, 280, 120, 30, on_time=go-10, off_time=gf-5, offset=30))
    plats.append(TeleportPlatform(11580, 320, 11670, 240, 120, 30, interval=ti-10))
    plats.append(MovingPlatform(11850, 280, 12000, 280, 120, 30, speed=1.6*ps))
    plats.append(Platform(12100, 350, 1600, 40))  # Final platform — 1600px dramatic walk to exit
    # Final gauntlet obstacles on final platform
    icicles.append(Icicle(12250, 150, max_fall_speed=isp))
    icicles.append(Icicle(12550, 140, max_fall_speed=isp))
    icicles.append(Icicle(12850, 130, max_fall_speed=isp))
    icicles.append(Icicle(13050, 145, max_fall_speed=isp))
    icicles.append(Icicle(13350, 135, max_fall_speed=isp))
    saw_blades.append(SawBlade(12300, 330, 12700, 330, speed=1.2*ss))
    saw_blades.append(SawBlade(12800, 330, 13100, 330, speed=1.0*ss))
    wind_zones.append((12100, 13700, -2.5*ws))  # headwind pushing player back
    # Pendulums on final platform
    pendulums.append(Pendulum(12500, 200, length=120, speed=0.025))
    pendulums.append(Pendulum(13000, 190, length=130, speed=0.03))
    pendulums.append(Pendulum(13400, 210, length=110, speed=0.035))
    # Ice geysers on final platform
    ice_geysers.append(IceGeyser(12400, 350, interval=100))
    ice_geysers.append(IceGeyser(12900, 350, interval=90))
    ice_geysers.append(IceGeyser(13300, 350, interval=110))
    mons.append(FlyingMonster(10700, 240, 10500, 10900, speed=1.5*ms, amplitude=40))
    mons.append(MushroomMonster(10860, 312, 10850, 10980, speed=1.6*ms))
    mons.append(BombMonster(11120, 290, 11100, 11250, speed=1.0, diff=diff))
    pws.append(Powerup(10400, 280))
    heart_pickups.append(HeartPickup(11400, 260))

    # --- Saw Blades (sections 3-5) ---
    saw_blades.append(SawBlade(4650,330,4650,430,speed=1.2*ss))
    saw_blades.append(SawBlade(5300,350,5300,280,speed=1.0*ss))
    saw_blades.append(SawBlade(8250,280,8250,380,speed=1.4*ss))
    saw_blades.append(SawBlade(9100,260,9200,260,speed=1.1*ss))
    saw_blades.append(SawBlade(11250,260,11250,340,speed=1.3*ss))

    # --- Wind Zones (sections 3-5) ---
    wind_zones.append((4800, 5200, 1.2*ws))    # rightward wind
    wind_zones.append((7650, 8050, -1.0*ws))   # leftward wind
    wind_zones.append((10400, 10800, 1.5*ws))  # strong rightward wind

    # --- Crumbling Bridge --- dramatic set piece between sections 3 and 4
    # Platforms lead up to bridge start, bridge spans a gap, platforms continue on the other side
    plats.append(Platform(6650, 370, 160, 30))   # approach platform before bridge
    crumbling_bridges.append(CrumblingBridge(6850, 370, 600, tile_delay=crd))
    plats.append(Platform(7490, 370, 160, 30))   # landing platform after bridge

    # Ornaments as coin-trail guides along intended path (~28 total)
    orn_positions = [
        # Sec 1: above platforms guiding forward (plats at y=500,500,455,410,455,500)
        (200, 480), (700, 480), (1250, 390), (1550, 435), (1900, 480),
        # Sec 2: above glitch/ice platforms (y=460,420,440,375,420,375,375)
        (2350, 440), (2600, 400), (3150, 355), (3650, 355),
        # Sec 3: moving plats + wall jump (plats at 400,360,320-450,380,420)
        (4250, 380), (4600, 340), (5200, 360),
        # Bridge: ornaments along the bridge at y=370 surface -> 20px above = 350
        (6950, 350), (7100, 350), (7250, 350),
        # Sec 4: teleport section (plats at 350,320,300,350,300,350,300,350)
        (7800, 330), (8500, 280), (9050, 280), (9700, 280),
        # Sec 5: final stretch before final platform
        (10500, 300), (11000, 300), (11500, 260),
        # Final 1200px platform (y=350 surface -> 20px above = 330), spread 4 evenly
        (12250, 330), (12550, 330), (12900, 330), (13200, 330), (13500, 330),
    ]
    for ox, oy in orn_positions:
        ornaments.append(Ornament(ox, oy))

    # Icicles placed over platforms (not random gaps)
    icicle_positions = [
        (600, 300), (1500, 250), (2750, 240), (3300, 200),
        (4500, 160), (5500, 220), (7970, 120), (8950, 150),
        (10850, 140),
    ]
    for ix, iy in icicle_positions:
        icicles.append(Icicle(ix, iy, max_fall_speed=isp))

    exit_door = ExitDoor(13620, 280)
    return plats, cps, mons, pws, exit_door, npcs, ornaments, icicles, heart_pickups, saw_blades, wind_zones, crumbling_bridges, pendulums, ice_geysers


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
        self.state = "playing"  # playing / settings / win / dialogue / ending / stats
        self.current_level = 0; self.level_time = 0; self.tick = 0; self.win_timer = 0
        self.freeze_frames = 0  # hitstop effect
        self.respawn_fade = 0  # respawn screen wipe
        self.best_combo = 0  # track best combo for stats
        self.difficulty = "hard"
        self.music_volume = 0.5; self.music_muted = False; self.settings_cursor = 0
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = []; self.rings = []; self.flashes = []
        self.damage_flashes = []  # DamageFlash instances for red vignette
        self.score_popups = []; self.snowballs = []
        self.snowflakes = [Snowflake() for _ in range(100)]
        # Combo system
        self.combo_count = 0; self.combo_timer = 0; self.combo_popups = []  # (x,y,count,timer)
        self.bg_stars = [BGStar() for _ in range(80)]
        self.platforms = []; self.checkpoints = []; self.monsters = []
        self.powerups = []; self.npcs = []; self.exit_door = None
        self.ornaments = []; self.icicles = []; self.heart_pickups = []
        self.saw_blades = []; self.wind_zones = []; self.crumbling_bridges = []
        self.pendulums = []; self.ice_geysers = []
        self.wind_particles = []
        self._blizzard_playing = False
        self.ORNAMENT_GATE = DIFFICULTY[self.difficulty]["ornament_gate"]
        self.player = Player(100, 400)
        self.dialogue_box = None
        self.pending_state = None  # state to return to after dialogue
        self.ending_shown = False
        # Soul death/respawn animation
        self.soul_state = None  # None, "rising", "panning", "falling"
        self.soul_x = 0; self.soul_y = 0; self.soul_target_y = 0; self.soul_timer = 0
        self.soul_trail = []  # list of (x,y,alpha) for trail effect
        # Ending NPC positions
        self.ending_npc_x = -40; self.ending_npc_target_x = 200
        self.ending_npc_timer = 0; self.ending_holly_x = SCREEN_WIDTH + 40; self.ending_jingle_x = SCREEN_WIDTH + 40
        self.ending_sparkles = []  # golden sparkle particles for ending
        self.load_level()
        self.sfx.start_music(volume=self.music_volume)

    def load_level(self):
        (self.platforms, self.checkpoints, self.monsters,
         self.powerups, self.exit_door, self.npcs,
         self.ornaments, self.icicles, self.heart_pickups,
         self.saw_blades, self.wind_zones, self.crumbling_bridges,
         self.pendulums, self.ice_geysers) = create_level(self.difficulty)
        self.ORNAMENT_GATE = DIFFICULTY[self.difficulty]["ornament_gate"]
        self.player = Player(100, 400)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles.clear(); self.rings.clear(); self.flashes.clear()
        self.damage_flashes.clear()
        self.score_popups.clear(); self.snowballs.clear()
        self.wind_particles = []
        self._blizzard_playing = False
        self.combo_count = 0; self.combo_timer = 0; self.combo_popups = []
        self.level_time = 0; self.tick = 0; self.win_timer = 0
        self.freeze_frames = 0; self.respawn_fade = 0; self.best_combo = 0
        self.dialogue_box = None; self.ending_shown = False
        self.soul_state = None; self.soul_trail = []

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
            # Hitstop: freeze frames — skip update, just draw
            if self.freeze_frames > 0:
                self.freeze_frames -= 1
            elif self.state == "playing" and self.soul_state is not None:
                self._update_soul(); self.tick += 1
                for sf in self.snowflakes: sf.update()
            elif self.state == "playing": self._update()
            elif self.state == "win":
                self.win_timer += 1
                for sf in self.snowflakes: sf.update()
            elif self.state == "stats":
                for sf in self.snowflakes: sf.update()
                self.tick += 1
            elif self.state == "dialogue":
                if self.dialogue_box: self.dialogue_box.update()
                for sf in self.snowflakes: sf.update()
            elif self.state == "ending":
                if self.dialogue_box: self.dialogue_box.update()
                for sf in self.snowflakes: sf.update()
                self.tick += 1; self.ending_npc_timer += 1
                # Slide Elder Frost in from left
                if self.ending_npc_x < self.ending_npc_target_x:
                    self.ending_npc_x += (self.ending_npc_target_x - self.ending_npc_x) * 0.06 + 1
                # Determine current speaker for NPC visibility
                if self.dialogue_box and self.dialogue_box.active:
                    spk = self.dialogue_box.dialogues[self.dialogue_box.index][0]
                    if "Holly" in spk and self.ending_holly_x > SCREEN_WIDTH - 160:
                        self.ending_holly_x -= 4
                    if "Jingle" in spk and self.ending_jingle_x > SCREEN_WIDTH - 100:
                        self.ending_jingle_x -= 4
                    # Narrator lines: NPCs fade out (slide away)
                    if spk == "":
                        self.ending_npc_x -= 1.5
                        self.ending_holly_x += 1.5
                        self.ending_jingle_x += 1.5
                    # Golden sparkles during final narrator lines
                    di = self.dialogue_box.index
                    total = len(self.dialogue_box.dialogues)
                    if spk == "" and di >= total - 6 and self.tick % 4 == 0:
                        self.ending_sparkles.append([
                            random.randint(100, SCREEN_WIDTH - 100),
                            random.randint(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 50),
                            random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.3),
                            random.randint(40, 70)])
                # Update sparkles
                new_sp = []
                for sp in self.ending_sparkles:
                    sp[0] += sp[2]; sp[1] += sp[3]; sp[4] -= 1
                    if sp[4] > 0: new_sp.append(sp)
                self.ending_sparkles = new_sp
            elif self.state == "credits":
                if self.credits_scroll < self.credits_max_scroll:
                    self.credits_scroll += 0.6
                for sf in self.snowflakes: sf.update()
                self.tick += 1
            # Respawn fade
            if self.respawn_fade > 0: self.respawn_fade -= 1
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
        # Stats screen
        if self.state == "stats":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                if not self.ending_shown:
                    self.ending_shown = True
                    self.start_dialogue("ending", "ending_done")
                    self.state = "ending"
                    self.ending_npc_x = -40; self.ending_npc_timer = 0
                    self.ending_holly_x = SCREEN_WIDTH + 40; self.ending_jingle_x = SCREEN_WIDTH + 40
                    self.ending_sparkles = []
                    self._start_ending_music()
                else:
                    self._exit_to_menu()
            return
        # Win
        if self.state == "win":
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.state = "stats"  # go to stats screen first
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
            # Wall jump
            if self.player.alive and self.player.wall_sliding:
                self.player.vel_y = JUMP_VELOCITY * 0.9
                self.player.vel_x = -self.player.wall_side * 10  # kick off wall
                self.player.jump_count = 2; self.player.wall_sliding = False
                self.player.facing_right = (self.player.wall_side < 0)
                self.sfx.play("jump")
                wx = self.player.rect.left if self.player.wall_side == -1 else self.player.rect.right
                for _ in range(6):
                    self.particles.append(Particle(wx, self.player.rect.centery + random.randint(-8, 8),
                        random.choice([WHITE, ICE_BLUE, SNOW_WHITE]),
                        -self.player.wall_side * random.uniform(1, 3), random.uniform(-2, 1), 15, 3, 0.1))
            # Double jump on key press (second jump only via keydown)
            elif self.player.alive and not self.player.on_ground and self.player.jump_count == 1:
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
                        self._add_combo(mon.rect.centerx, mon.rect.top)
                        self.freeze_frames = 3  # hitstop
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
                        self.damage_flashes.append(DamageFlash())
                        # Knockback away from damage source
                        dx = self.player.rect.centerx - mon.rect.centerx
                        self.player.vel_x = 7 * (1 if dx >= 0 else -1)
                        self.player.vel_y = -5
                    else:
                        self._player_death_fx(); self.sfx.play("death")
                if isinstance(mon, BombMonster) and mon.state == "exploding":
                    self.sfx.play("bomb_explode"); self.camera.add_shake(18)
            elif coll == "kill_monster":
                self._monster_kill_fx(mon); mon.kill()
                self.player.kill_count += 1; self.sfx.play("monster_kill")
                self._add_combo(mon.rect.centerx, mon.rect.top)
                self.freeze_frames = 3  # hitstop
            elif coll == "stomp":
                self._stomp_fx(mon); mon.stomp()
                self.player.vel_y = STOMP_BOUNCE
                self.player.kill_count += 1; self.sfx.play("stomp")
                self._add_combo(mon.rect.centerx, mon.rect.top)
                self.freeze_frames = 3  # hitstop

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
                        self.damage_flashes.append(DamageFlash())
                        self.player.vel_y = -4
                    else:
                        self._player_death_fx(); self.sfx.play("death")

        # Heart pickups
        for hp in self.heart_pickups:
            hp.update()
            if hp.check(self.player):
                self.player.hearts = min(PLAYER_MAX_HEARTS, self.player.hearts + 1)
                self.score_popups.append((hp.x, hp.y - 15, "+1 HEART", 50, XMAS_RED))
                self.sfx.play("powerup")

        # Saw blades
        for sb2 in self.saw_blades:
            sb2.update()
            if sb2.check_hit(self.player):
                if self.player.take_damage():
                    if self.player.alive:
                        self.camera.add_shake(8); self.sfx.play("death")
                        self.damage_flashes.append(DamageFlash())
                        dx=self.player.rect.centerx-sb2.rect.centerx
                        self.player.vel_x=7*(1 if dx>=0 else -1); self.player.vel_y=-5
                    else:
                        self._player_death_fx(); self.sfx.play("death")

        # Pendulums
        for pend in self.pendulums:
            pend.update()
            if pend.check_hit(self.player):
                if self.player.take_damage():
                    if self.player.alive:
                        self.camera.add_shake(8); self.sfx.play("death")
                        self.damage_flashes.append(DamageFlash())
                        dx=self.player.rect.centerx-pend.bx
                        self.player.vel_x=8*(1 if dx>=0 else -1); self.player.vel_y=-6
                    else: self._player_death_fx(); self.sfx.play("death")
        # Ice geysers
        for ig in self.ice_geysers:
            ig.update()
            if ig.check_hit(self.player):
                if self.player.take_damage():
                    if self.player.alive:
                        self.camera.add_shake(6); self.sfx.play("death")
                        self.damage_flashes.append(DamageFlash()); self.player.vel_y=-8
                    else: self._player_death_fx(); self.sfx.play("death")

        # Wind zones
        if self.player.alive:
            for wz_start, wz_end, wz_str in self.wind_zones:
                if wz_start<=self.player.rect.centerx<=wz_end:
                    self.player.vel_x+=wz_str*0.15
                    # Spawn wind particles
                    if self.tick%3==0:
                        wy=random.randint(-20,SCREEN_HEIGHT+20)
                        wx=wz_start+random.randint(0,int(wz_end-wz_start))
                        self.wind_particles.append(WindParticle(wx,wy,wz_str))
        self.wind_particles=[wp for wp in self.wind_particles if wp.update()]

        # Crumbling bridges
        for cb in self.crumbling_bridges:
            cb.check_standing(self.player)
            cb.update()
            # Check collision with solid tiles as platforms
            if self.player.alive:
                for t in cb.tiles:
                    if t["state"] in ("solid","shaking"):
                        pr=t["rect"]
                        if self.player.rect.colliderect(pr) and self.player.vel_y>0:
                            if self.player.rect.bottom<=pr.top+10:
                                self.player.rect.bottom=pr.top; self.player.vel_y=0
                                self.player.on_ground=True; self.player.jump_count=0

        self.exit_door.update()
        # Ornament gate: require enough ornaments to open exit (easy=no gate)
        if self.player.alive and self.exit_door.check(self.player):
            if self.ORNAMENT_GATE <= 0 or self.player.ornament_count >= self.ORNAMENT_GATE:
                snd = self.sfx.sounds.get("blizzard")
                if snd: snd.stop()
                self._blizzard_playing = False
                self.state = "win"; self.sfx.play("win"); self.sfx.stop_music()
            else:
                # Push player back gently
                dx = self.player.rect.centerx - self.exit_door.rect.centerx
                self.player.vel_x = 3 * (1 if dx >= 0 else -1)

        self.particles = [p for p in self.particles if p.update()]
        self.rings = [r for r in self.rings if r.update()]
        self.flashes = [f for f in self.flashes if f.update()]
        self.damage_flashes = [d for d in self.damage_flashes if d.update()]
        self.score_popups = [(x,y-0.8,t,ti-1,c) for x,y,t,ti,c in self.score_popups if ti>0]
        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0: self.combo_count = 0
        self.combo_popups = [(x, y - 1.2, cnt, t - 1) for x, y, cnt, t in self.combo_popups if t > 0]
        # Footstep & landing particles
        if self.player.alive:
            if self.player.on_ground and not self.player.was_on_ground:
                # Landing burst
                for _ in range(9):
                    self.particles.append(Particle(
                        self.player.rect.centerx + random.randint(-10, 10), self.player.rect.bottom,
                        SNOW_WHITE, random.uniform(-2.5, 2.5), random.uniform(-1.5, 0), 18, random.randint(2, 4), 0.1))
            if self.player.on_ground and abs(self.player.vel_x) > 1:
                interval = 3 if self.player.sprinting else 5
                sz = 3 if self.player.sprinting else 2
                if self.tick % interval == 0:
                    self.particles.append(Particle(
                        self.player.rect.centerx + random.randint(-4, 4), self.player.rect.bottom,
                        SNOW_WHITE, random.uniform(-0.5, 0.5), random.uniform(-1, -0.2), 14, sz, 0.06))
        # Weather progression based on player x
        px = self.player.rect.x
        in_final = px >= 12100
        if px < 3000: target_count = 100
        elif px < 6000: target_count = 150
        elif not in_final: target_count = 250
        else: target_count = 420  # extreme blizzard on final platform
        cur = len(self.snowflakes)
        if cur < target_count:
            for _ in range(min(8, target_count - cur)):
                sf_new = Snowflake()
                if in_final:
                    sf_new.size = random.uniform(2.5, 6)
                    sf_new.sy = random.uniform(1.5, 4.0)
                self.snowflakes.append(sf_new)
        elif cur > target_count:
            for _ in range(min(3, cur - target_count)):
                if self.snowflakes: self.snowflakes.pop()
        # Blizzard sound on final platform
        if in_final and not getattr(self, '_blizzard_playing', False):
            snd = self.sfx.sounds.get("blizzard")
            if snd:
                snd.play(loops=-1); snd.set_volume(0.4)
            self._blizzard_playing = True
        elif not in_final and getattr(self, '_blizzard_playing', False):
            snd = self.sfx.sounds.get("blizzard")
            if snd: snd.stop()
            self._blizzard_playing = False
        # Wind in heavy weather
        if px >= 6000:
            wind_mult = 3.0 if in_final else 1.0
            wind_x = (math.sin(self.tick * 0.01) * 1.5 + 0.8) * wind_mult
            for sf in self.snowflakes: sf.x += wind_x * 0.3
        for sf in self.snowflakes: sf.update()
        # Blizzard streaks in heavy weather
        if px >= 6000:
            if in_final:
                # Every frame: multiple fast dense streaks
                for _ in range(3):
                    sy = random.randint(0, SCREEN_HEIGHT)
                    self.particles.append(Particle(
                        self.camera.offset_x + random.randint(-50, SCREEN_WIDTH + 50), sy,
                        (220, 225, 240), random.uniform(12, 22), random.uniform(-1, 1), 10, 2, 0, fade=True))
                # Subtle screen-wide white flash (blizzard gust)
                if self.tick % 40 == 0:
                    self.flashes.append(FlashOverlay(WHITE, 6, random.randint(10, 20)))
            else:
                if self.tick % 4 == 0:
                    sy = random.randint(0, SCREEN_HEIGHT)
                    self.particles.append(Particle(
                        self.camera.offset_x + random.randint(-50, SCREEN_WIDTH + 50), sy,
                        (200, 210, 230), random.uniform(6, 12), random.uniform(-0.5, 0.5), 8, 1, 0, fade=True))
        self._spawn_ambient()
        # Soul animation: intercept normal respawn
        if not self.player.alive and self.soul_state is None:
            # Block auto-respawn, start soul rising
            if self.player.respawn_timer <= 1:
                self.player.respawn_timer = 9999  # block auto-respawn
                self.soul_x = self.player.rect.centerx
                self.soul_y = self.player.rect.centery
                self.soul_target_y = self.player.rect.centery - 140
                self.soul_timer = 0; self.soul_trail = []
                self.soul_state = "rising"
                self.sfx.play("soul_rise")
        if not self.player.alive and self.player.respawn_timer == 49: pass  # death fx handled in _spawn_ambient
        self.level_time += 1

    # --- Effects ---
    def _player_death_fx(self):
        cx,cy=self.player.rect.centerx,self.player.rect.centery
        self.camera.add_shake(18); self.flashes.append(FlashOverlay(RED,18,120))
        # Scatter 10 "piece" particles in player colors with strong gravity
        for _ in range(10):
            a=random.uniform(0,math.pi*2); s=random.uniform(3,8)
            self.particles.append(Particle(cx+random.randint(-6,6),cy+random.randint(-8,8),
                random.choice([XMAS_RED,WHITE]),
                math.cos(a)*s,math.sin(a)*s-2,random.randint(40,70),random.randint(5,9),0.35))
        # Additional sparkle particles
        for _ in range(25):
            a=random.uniform(0,math.pi*2); s=random.uniform(2,6)
            self.particles.append(Particle(cx,cy,random.choice([XMAS_RED,WHITE,ICE_BLUE,SNOW_WHITE]),
                math.cos(a)*s,math.sin(a)*s,random.randint(25,50),random.randint(2,5),0.15))

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

    def _add_combo(self, x, y):
        self.combo_count += 1; self.combo_timer = 90
        if self.combo_count > self.best_combo: self.best_combo = self.combo_count
        if self.combo_count > self.player.best_combo: self.player.best_combo = self.combo_count
        if self.combo_count >= 2:
            self.combo_popups.append((x, y - 20, self.combo_count, 50))
            # Pitch-shift simulation: increase volume with combo (pygame lacks native pitch shift)
            for snd in [self.sfx.sounds.get("stomp"), self.sfx.sounds.get("monster_kill")]:
                if snd: snd.set_volume(min(1.0, 0.5 + self.combo_count * 0.1))

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

    def _update_soul(self):
        self.soul_timer += 1
        # Sparkle particles around the soul (skip during panning — soul not visible)
        if self.soul_state != "panning":
            for _ in range(random.randint(2,3)):
                a=random.uniform(0,math.pi*2); d=random.uniform(8,20)
                sx=self.soul_x+math.cos(a)*d; sy=self.soul_y+math.sin(a)*d
                self.particles.append(Particle(sx,sy,(255,210,80),random.uniform(-0.5,0.5),random.uniform(-1,0),random.randint(12,20),random.randint(1,3),0.02,fade=True))
        if self.soul_state == "rising":
            # Smoothstep rising over 40 frames with horizontal wobble
            t = min(1.0, self.soul_timer / 40)
            ease = t * t * (3 - 2 * t)
            self.soul_y = self.player.rect.centery - ease * 140
            self.soul_x = self.player.rect.centerx + math.sin(self.soul_timer * 0.15) * 12
            self.soul_trail.append((self.soul_x, self.soul_y, 255))
            if len(self.soul_trail) > 20: self.soul_trail.pop(0)
            self.soul_trail = [(x, y, a - 10) for x, y, a in self.soul_trail if a > 10]
            if self.soul_timer >= 40:
                # Transition to panning — camera moves to checkpoint before soul falls
                self.soul_state = "panning"; self.soul_timer = 0
                self.soul_trail = []
                self.soul_pan_target_x = self.player.spawn_x + Player.WIDTH // 2 - self.camera.width // 3
                self.soul_pan_target_y = self.player.spawn_y + Player.HEIGHT // 2 - self.camera.height // 2
        elif self.soul_state == "panning":
            # Smoothly pan camera toward checkpoint
            dx = self.soul_pan_target_x - self.camera.offset_x
            dy = self.soul_pan_target_y - self.camera.offset_y
            self.camera.offset_x += dx * 0.12
            self.camera.offset_y += dy * 0.08
            # Wait at least 20 frames AND until camera is close enough
            close_enough = abs(dx) < 8 and abs(dy) < 8
            if self.soul_timer >= 20 and close_enough:
                self.soul_state = "falling"; self.soul_timer = 0
                self.soul_x = self.player.spawn_x + Player.WIDTH // 2
                self.soul_y = self.camera.offset_y - 60  # start above visible area
                self.soul_target_y = self.player.spawn_y + Player.HEIGHT // 2
                self.soul_trail = []; self.sfx.play("soul_land")
        elif self.soul_state == "falling":
            # Smoothstep falling over 35 frames with gentle arc
            t = min(1.0, self.soul_timer / 35)
            ease = t * t * (3 - 2 * t)
            self.soul_y = -50 + (self.soul_target_y + 50) * ease
            self.soul_x = (self.player.spawn_x + Player.WIDTH // 2) + math.sin(t * math.pi) * 30
            self.soul_trail.append((self.soul_x, self.soul_y, 255))
            if len(self.soul_trail) > 20: self.soul_trail.pop(0)
            self.soul_trail = [(x, y, a - 10) for x, y, a in self.soul_trail if a > 10]
            if self.soul_timer >= 35:
                self.player.respawn_timer = 0; self.player.respawn()
                self.sfx.play("soul_land"); self.sfx.play("respawn")
                self.respawn_fade = 20
                self.flashes.append(FlashOverlay(WHITE, 12, 160))
                for _ in range(25):
                    a = random.uniform(0, math.pi * 2); s = random.uniform(2, 7)
                    self.particles.append(Particle(self.soul_x, self.soul_target_y,
                        random.choice([WHITE, SNOW_WHITE, ICE_BLUE, XMAS_GOLD]),
                        math.cos(a) * s, math.sin(a) * s, 30, random.randint(3, 7), 0.1))
                self.rings.append(RingEffect(int(self.soul_x), int(self.soul_target_y), WHITE, 100, 6, 3))
                self.soul_state = None; self.soul_trail = []
                self.camera.update(self.player.rect)
        # Update particles even during soul
        self.particles = [p for p in self.particles if p.update()]
        self.rings = [r for r in self.rings if r.update()]
        self.flashes = [f for f in self.flashes if f.update()]

    def _draw_soul(self):
        if self.soul_state is None: return
        # Pulsing dark overlay (breathe between alpha 60-100)
        dim_alpha = int(80 + 20 * math.sin(self.soul_timer * 0.12))
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, dim_alpha))
        self.screen.blit(dim, (0, 0))
        # During panning, only show the dark overlay — no soul orb
        if self.soul_state == "panning": return
        sp = self.camera.apply(pygame.Rect(int(self.soul_x), int(self.soul_y), 1, 1))
        # Soul trail — 20 positions, decreasing circles with fading alpha
        for i, (sx, sy, sa) in enumerate(self.soul_trail):
            tp = self.camera.apply(pygame.Rect(int(sx), int(sy), 1, 1))
            frac = (i + 1) / max(1, len(self.soul_trail))
            r = max(2, int(10 * frac))
            al = max(0, min(255, int(sa * 0.4 * frac)))
            ts = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (255, 255, 255, al), (r, r), r)
            self.screen.blit(ts, (tp.x - r, tp.y - r))
        # Outer glow (radius 40, alpha 40)
        for gr, ga in [(40, 40), (28, 80), (18, 160)]:
            gs = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (255, 255, 255, ga), (gr, gr), gr)
            self.screen.blit(gs, (sp.x - gr, sp.y - gr))
        # Core white (radius 8)
        pygame.draw.circle(self.screen, WHITE, (sp.x, sp.y), 8)
        pygame.draw.circle(self.screen, (240, 250, 255), (sp.x - 1, sp.y - 1), 4)

    # --- Drawing ---
    def _draw(self):
        self.screen.fill(DARK_SKY)
        if self.state == "playing":
            self._draw_game()
        elif self.state == "settings":
            self._draw_game(); self._draw_settings()
        elif self.state == "win":
            self._draw_win()
        elif self.state == "stats":
            self._draw_stats()
        elif self.state in ("dialogue", "ending"):
            self._draw_game()
            if self.state == "ending": self._draw_ending_npcs()
            if self.dialogue_box: self.dialogue_box.draw(self.screen, self.tick)
        elif self.state == "credits":
            self._draw_credits()
        # Respawn screen wipe
        if self.respawn_fade > 0:
            alpha = int(255 * (1.0 - abs(self.respawn_fade - 10) / 10.0))
            if alpha > 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill(BLACK); overlay.set_alpha(min(255, alpha))
                self.screen.blit(overlay, (0, 0))
        pygame.display.flip()

    def _draw_background(self):
        # Sky gradient - smoother (dark blue at top -> slightly lighter at horizon)
        sky_top = (8, 10, 35)
        sky_mid = (12, 16, 45)
        sky_bot = (18, 22, 40)
        for y in range(0, SCREEN_HEIGHT, 2):
            t = y / SCREEN_HEIGHT
            if t < 0.5:
                c = lerp_color(sky_top, sky_mid, t * 2)
            else:
                c = lerp_color(sky_mid, sky_bot, (t - 0.5) * 2)
            self.screen.fill(c, (0, y, SCREEN_WIDTH, 2))
        for star in self.bg_stars: star.draw(self.screen, self.tick)
        # Moon
        mx, my = SCREEN_WIDTH - 120, 80
        pygame.draw.circle(self.screen, (60, 60, 50), (mx, my), 50)
        pygame.draw.circle(self.screen, (240, 230, 200), (mx, my), 45)
        pygame.draw.circle(self.screen, (60, 60, 50), (mx + 12, my - 8), 35)
        for r in range(80, 40, -5):
            a = int(12 * (80 - r) / 40)
            gs = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (240, 230, 200, a), (r, r), r)
            self.screen.blit(gs, (mx - r, my - r))
        # Aurora - subtle, not overpowering
        for i in range(3):
            pts = []
            for x in range(0, SCREEN_WIDTH + 40, 40):
                y = 50 + int(math.sin(x*0.004+self.tick*0.006+i*2)*25+math.sin(x*0.002+self.tick*0.004)*15)
                pts.append((x, y))
            pts.append((SCREEN_WIDTH, 0)); pts.append((0, 0))
            if len(pts) >= 3:
                acs = [(15,60,30),(20,45,60),(30,20,50)]
                ac = acs[i%3]; p = abs(math.sin(self.tick*0.005+i))*0.35+0.15
                ac = tuple(int(c*p) for c in ac)
                s = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
                pygame.draw.polygon(s, (*ac, 22), pts)
                self.screen.blit(s, (0, 0))
        # === PARALLAX LAYER 1: Far mountains (0.1x scroll) ===
        ox_far = int(self.camera.offset_x * 0.1)
        base_y = SCREEN_HEIGHT - 30
        for mx2 in range(-100 - ox_far % 300, SCREEN_WIDTH + 350, 300):
            rng = random.Random(mx2 + 55555)
            mh = rng.randint(120, 220); mw = rng.randint(140, 250)
            mc = (18, 22 + rng.randint(0, 5), 35)
            pts = [(mx2 - mw // 2, base_y), (mx2, base_y - mh), (mx2 + mw // 2, base_y)]
            pygame.draw.polygon(self.screen, mc, pts)
            # Snow cap
            cap_h = mh // 4
            pygame.draw.polygon(self.screen, (35, 40, 55),
                [(mx2 - mw // 6, base_y - mh + cap_h), (mx2, base_y - mh), (mx2 + mw // 6, base_y - mh + cap_h)])
        # === PARALLAX LAYER 2: Mid pine trees (0.3x scroll) ===
        ox_mid = int(self.camera.offset_x * 0.3)
        for tx in range(-60 - ox_mid % 80, SCREEN_WIDTH + 120, 80):
            rng = random.Random(tx + 88888)
            th = rng.randint(50, 100); tw2 = rng.randint(20, 35)
            tc = (10, 16 + rng.randint(0, 6), 10)
            pygame.draw.polygon(self.screen, tc, [(tx, base_y - th), (tx - tw2, base_y), (tx + tw2, base_y)])
            pygame.draw.polygon(self.screen, tc, [(tx, base_y - th + 15), (tx - tw2 + 6, base_y - 8), (tx + tw2 - 6, base_y - 8)])
        # === PARALLAX LAYER 3: Close pine trees (0.6x scroll) ===
        ox_close = int(self.camera.offset_x * 0.6)
        for tx in range(-80 - ox_close % 150, SCREEN_WIDTH + 200, 150):
            rng = random.Random(tx + 33333)
            th = rng.randint(80, 160); tw2 = rng.randint(35, 55)
            tc = (14, 20 + rng.randint(0, 10), 14)
            pygame.draw.polygon(self.screen, tc, [(tx, base_y - th), (tx - tw2, base_y), (tx + tw2, base_y)])
            pygame.draw.polygon(self.screen, tc, [(tx, base_y - th + 25), (tx - tw2 + 10, base_y - 12), (tx + tw2 - 10, base_y - 12)])
            pygame.draw.circle(self.screen, (25, 32, 40), (tx, base_y - th), 4)
        # Distant village silhouettes
        ox2 = int(self.camera.offset_x * 0.04)
        for hx in range(-80 - ox2 % 250, SCREEN_WIDTH + 250, 250):
            rng2 = random.Random(hx + 77777)
            hw = rng2.randint(40, 60); hh = rng2.randint(30, 55)
            pygame.draw.rect(self.screen, (15, 18, 25), (hx, base_y - hh, hw, hh))
            pygame.draw.polygon(self.screen, (20, 22, 30), [(hx - 5, base_y - hh), (hx + hw + 5, base_y - hh), (hx + hw // 2, base_y - hh - 20)])
            pygame.draw.polygon(self.screen, (35, 38, 48), [(hx - 3, base_y - hh), (hx + hw + 3, base_y - hh), (hx + hw // 2, base_y - hh - 18)])
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
        # Draw crumbling bridges
        for cb in self.crumbling_bridges: cb.draw(self.screen, self.camera, self.tick)
        # Draw saw blades
        for sb2 in self.saw_blades: sb2.draw(self.screen, self.camera, self.tick)
        for pend in self.pendulums: pend.draw(self.screen, self.camera, self.tick)
        for ig in self.ice_geysers: ig.draw(self.screen, self.camera, self.tick)
        # Draw wind particles
        for wp in self.wind_particles: wp.draw(self.screen, self.camera)
        # Wind zone visual indicators
        for wz_start, wz_end, wz_str in self.wind_zones:
            zr = self.camera.apply(pygame.Rect(int(wz_start), 0, int(wz_end - wz_start), SCREEN_HEIGHT))
            if zr.right > 0 and zr.left < SCREEN_WIDTH:
                ws = pygame.Surface((min(zr.width, SCREEN_WIDTH), SCREEN_HEIGHT), pygame.SRCALPHA)
                ws.fill((255, 255, 255, 8))
                self.screen.blit(ws, (max(0, zr.left), 0))
        has_enough = self.ORNAMENT_GATE <= 0 or self.player.ornament_count >= self.ORNAMENT_GATE
        self.exit_door.draw(self.screen, self.camera, self.tick, has_enough)
        # Ornament gate indicator near exit door
        er = self.camera.apply(self.exit_door.rect)
        if self.ORNAMENT_GATE > 0 and self.player.ornament_count < self.ORNAMENT_GATE:
            if 0 < er.centerx < SCREEN_WIDTH:
                gf2 = pygame.font.SysFont("consolas", 13, bold=True)
                gate_txt = f"{self.player.ornament_count}/{self.ORNAMENT_GATE} ornaments needed"
                gt = gf2.render(gate_txt, True, XMAS_RED)
                tbg = pygame.Surface((gt.get_width()+12, gt.get_height()+6), pygame.SRCALPHA)
                tbg.fill((0,0,0,160))
                self.screen.blit(tbg, (er.centerx-gt.get_width()//2-6, er.top-30))
                self.screen.blit(gt, gt.get_rect(center=(er.centerx, er.top - 24)))
        for npc in self.npcs: npc.draw(self.screen, self.camera, self.tick)
        for mon in self.monsters: mon.draw(self.screen, self.camera, self.tick)
        for sb in self.snowballs: sb.draw(self.screen, self.camera, self.tick)
        for p in self.particles: p.draw(self.screen, self.camera)
        for r in self.rings: r.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, self.tick)
        # Wall slide particles on wall
        if self.player.wall_sliding and self.player.alive and self.tick % 2 == 0:
            wx = self.player.rect.left if self.player.wall_side == -1 else self.player.rect.right
            self.particles.append(Particle(wx, self.player.rect.centery + random.randint(-5, 10),
                random.choice([WHITE, SNOW_WHITE, ICE_BLUE]), -self.player.wall_side * random.uniform(0.5, 1.5),
                random.uniform(-1, 0.5), 10, 2, 0.05))
        for f in self.flashes: f.draw(self.screen)
        for d in self.damage_flashes: d.draw(self.screen)
        # Combo popups
        for x, y, cnt, timer in self.combo_popups:
            a = min(1.0, timer / 20)
            sz = min(28, 16 + cnt * 2)
            c = lerp_color(XMAS_GOLD, WHITE, min(1.0, cnt / 8))
            c = tuple(max(0, min(255, int(v * a))) for v in c)
            f = pygame.font.SysFont("consolas", sz, bold=True)
            txt = f.render(f"x{cnt}!", True, c)
            pos = self.camera.apply(pygame.Rect(int(x), int(y), 1, 1))
            self.screen.blit(txt, txt.get_rect(center=(pos.x, pos.y)))
        for x, y, text, timer, color in self.score_popups:
            a = min(1.0, timer / 30)
            c = tuple(max(0, min(255, int(v * a))) for v in color)
            pos = self.camera.apply(pygame.Rect(int(x), int(y), 1, 1))
            surf = self.small_font.render(text, True, c)
            self.screen.blit(surf, surf.get_rect(center=(pos.x, pos.y)))
        # === HUD (compact, top-left cluster) ===
        hud_x, hud_y = 12, 10
        def _hud_text(font, text, color, x, y):
            self.screen.blit(font.render(text, True, (0,0,0)), (x+1, y+1))
            self.screen.blit(font.render(text, True, color), (x, y))
        # Hearts - filled red polygons with shadow, empty outline for missing
        for i in range(PLAYER_MAX_HEARTS):
            hx = hud_x + i * 26; hy = hud_y
            c = XMAS_RED if i < self.player.hearts else (50,50,50)
            hscale = 0
            if i == 0 and self.player.hearts == 1 and self.player.alive:
                hscale = int(abs(math.sin(self.tick * 0.12)) * 2)
            for dx, dy, sc in [(1,1,(0,0,0)), (0,0,c)]:
                pygame.draw.circle(self.screen, sc, (hx+5+dx, hy+dy), 5+hscale)
                pygame.draw.circle(self.screen, sc, (hx+13+dx, hy+dy), 5+hscale)
                pygame.draw.polygon(self.screen, sc, [(hx-hscale+dx, hy+2+dy), (hx+9+dx, hy+11+hscale+dy), (hx+18+hscale+dx, hy+2+dy)])
            if i >= self.player.hearts:
                pygame.draw.circle(self.screen, (30,30,30), (hx+5, hy), 5, 1)
                pygame.draw.circle(self.screen, (30,30,30), (hx+13, hy), 5, 1)
        # Ornament icon + count next to hearts
        orn_total = len(self.ornaments)
        orn_got = self.player.ornament_count
        orn_x = hud_x + PLAYER_MAX_HEARTS * 26 + 8
        pygame.draw.circle(self.screen, (0,0,0), (orn_x+6+1, hud_y+4+1), 5)
        pygame.draw.circle(self.screen, XMAS_GOLD, (orn_x+6, hud_y+4), 5)
        pygame.draw.circle(self.screen, WHITE, (orn_x+4, hud_y+2), 1)
        pygame.draw.line(self.screen, GRAY, (orn_x+6, hud_y-1), (orn_x+6, hud_y-4), 1)
        _hud_text(self.tiny_font, f"{orn_got}/{orn_total}", XMAS_GOLD, orn_x+14, hud_y-2)
        # Dash cooldown bar under hearts
        dash_y = hud_y + 16; dash_bw = 60; dash_bh = 5
        pygame.draw.rect(self.screen, (0,0,0), (hud_x, dash_y+1, dash_bw+2, dash_bh+1))
        if self.player.dash_cooldown > 0:
            ratio = 1.0 - self.player.dash_cooldown / DASH_COOLDOWN
            pygame.draw.rect(self.screen, (30,30,40), (hud_x, dash_y, dash_bw, dash_bh))
            pygame.draw.rect(self.screen, (60,140,200), (hud_x, dash_y, int(dash_bw*ratio), dash_bh))
        else:
            pygame.draw.rect(self.screen, CYAN, (hud_x, dash_y, dash_bw, dash_bh))
        _hud_text(pygame.font.SysFont("consolas",9), "DASH", (160,200,230) if self.player.dash_cooldown<=0 else (80,80,90), hud_x+dash_bw+4, dash_y-2)
        # Low health red border
        if self.player.hearts == 1 and self.player.alive:
            pulse = abs(math.sin(self.tick * 0.08)) * 0.6
            lh_s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            lh_a = int(40 * pulse)
            for bi in range(6):
                ia = max(0, lh_a - bi * 6)
                if ia > 0:
                    pygame.draw.rect(lh_s, (220, 30, 30, ia), (bi, bi, SCREEN_WIDTH - 2 * bi, SCREEN_HEIGHT - 2 * bi), 1)
            self.screen.blit(lh_s, (0, 0))
        # Combo - only show when active (>=2), center-top, bold, fades
        if self.combo_count >= 2:
            combo_a = min(1.0, self.combo_timer / 30)
            csz = min(30, 18 + self.combo_count * 2)
            cc = lerp_color(XMAS_GOLD, WHITE, min(1.0, self.combo_count / 8))
            cc_s = tuple(max(0, min(255, int(v * combo_a))) for v in cc)
            cf = pygame.font.SysFont("consolas", csz, bold=True)
            csh = cf.render(f"COMBO x{self.combo_count}!", True, tuple(max(0,int(v*0.3*combo_a)) for v in cc))
            self.screen.blit(csh, csh.get_rect(center=(SCREEN_WIDTH//2+2, 44)))
            self.screen.blit(cf.render(f"COMBO x{self.combo_count}!", True, cc_s), cf.render(f"COMBO x{self.combo_count}!", True, cc_s).get_rect(center=(SCREEN_WIDTH//2, 42)))
        # Unreal mode bar
        if self.player.is_unreal:
            rem=self.player.unreal_timer/FPS; bw,bh=160,14
            bx=SCREEN_WIDTH//2-bw//2; by=12; ratio=self.player.unreal_timer/UNREAL_DURATION
            pygame.draw.rect(self.screen,(0,0,0),(bx-3,by-3,bw+6,bh+6))
            pygame.draw.rect(self.screen,DARK_GRAY,(bx-2,by-2,bw+4,bh+4))
            for px_i in range(int(bw*ratio)):
                self.screen.fill(xmas_cycle_color(self.tick+px_i*2,0.3),(bx+px_i,by,1,bh))
            _hud_text(self.tiny_font, f"UNREAL  {rem:.1f}s", WHITE, bx+4, by+1)
            pygame.draw.rect(self.screen,xmas_cycle_color(self.tick,0.15),(bx-2,by-2,bw+4,bh+4),2)
        # Top-right compact info
        t = self.level_time / FPS
        _hud_text(self.tiny_font, f"Time: {t:.1f}s", SNOW_WHITE, SCREEN_WIDTH-120, 10)
        if self.player.kill_count > 0:
            _hud_text(self.tiny_font, f"Kills: {self.player.kill_count}", XMAS_GOLD, SCREEN_WIDTH-120, 24)
        diff_label = self.difficulty.upper()
        dc = XMAS_GREEN if self.difficulty == "easy" else XMAS_GOLD if self.difficulty == "medium" else XMAS_RED
        _hud_text(self.tiny_font, diff_label, dc, SCREEN_WIDTH-120, 38)
        # Bottom help
        self.screen.blit(self.tiny_font.render("R-Respawn  ESC-Settings  F/X-Shoot  E-Talk  SHIFT-Dash(air)", True, (50,55,70)), (10, SCREEN_HEIGHT-16))
        if not self.player.alive and self.soul_state is None:
            txt=self.font.render("Respawning...",True,XMAS_RED)
            self.screen.blit(txt,txt.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)))
        if self.soul_state is not None:
            self._draw_soul()

    def _draw_settings(self):
        # Warm Christmas overlay - brighter so text is readable
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            t = y / SCREEN_HEIGHT
            r = int(55 + 20 * t)
            g = int(28 + 25 * t)
            b = int(30 + 15 * t)
            pygame.draw.rect(overlay, (r, g, b, 230), (0, y, SCREEN_WIDTH, 4))
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
                pygame.draw.rect(self.screen, (60, 35, 35), bar, border_radius=6)
                pygame.draw.rect(self.screen, (110, 80, 55), bar, 1, border_radius=6)
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

    def _draw_stats(self):
        self._draw_background()
        # Festive particles
        if self.tick % 10 == 0:
            self.particles.append(Particle(random.randint(100, SCREEN_WIDTH - 100),
                random.randint(50, 150), random.choice([XMAS_RED, XMAS_GREEN, XMAS_GOLD, WHITE]),
                random.uniform(-1, 1), random.uniform(0.5, 2), 50, random.randint(2, 5), 0.05))
        for p in self.particles: p.draw(self.screen, self.camera)
        self.particles = [p for p in self.particles if p.update()]
        # Title
        title = self.big_font.render("LEVEL STATS", True, XMAS_GOLD)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 70)))
        # Stats box
        box = pygame.Rect(SCREEN_WIDTH // 2 - 250, 110, 500, 420)
        bg = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
        bg.fill((10, 10, 28, 200))
        self.screen.blit(bg, box.topleft)
        pygame.draw.rect(self.screen, XMAS_GOLD, box, 2)
        # Stats content
        t = self.level_time / FPS
        orn_total = len(self.ornaments)
        orn_got = self.player.ornament_count
        lines = [
            (f"Ornaments: {orn_got} / {orn_total}", XMAS_GOLD),
            (f"Time: {t:.1f} seconds", SNOW_WHITE),
            (f"Deaths: {self.player.death_count}", XMAS_RED),
            (f"Monsters Defeated: {self.player.kill_count}", XMAS_GREEN),
            (f"Best Combo: x{self.best_combo}", CYAN if self.best_combo >= 3 else SNOW_WHITE),
            (f"Difficulty: {self.difficulty.upper()}",
             XMAS_GREEN if self.difficulty == "easy" else XMAS_GOLD if self.difficulty == "medium" else XMAS_RED),
        ]
        sy = box.y + 30
        for text, color in lines:
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, sy)))
            sy += 45
        # Rank calculation
        score = max(0, 1000 - int(t * 2) - self.player.death_count * 50 + orn_got * 20 + self.best_combo * 30)
        if score >= 800: rank, rank_c = "S", XMAS_GOLD
        elif score >= 600: rank, rank_c = "A", XMAS_GREEN
        elif score >= 350: rank, rank_c = "B", ICE_BLUE
        else: rank, rank_c = "C", GRAY
        sy += 10
        rank_surf = self.big_font.render(f"Rank: {rank}", True, rank_c)
        self.screen.blit(rank_surf, rank_surf.get_rect(center=(SCREEN_WIDTH // 2, sy)))
        # Decorative corners
        for cx2, cy2 in [(box.left, box.top), (box.right, box.top), (box.left, box.bottom), (box.right, box.bottom)]:
            pygame.draw.circle(self.screen, XMAS_RED, (cx2, cy2), 5)
            pygame.draw.circle(self.screen, XMAS_GOLD, (cx2, cy2), 3)
        # Continue prompt
        pulse = abs(math.sin(self.tick * 0.05)) * 0.5 + 0.5
        hint = self.small_font.render("Press ENTER to continue to the ending...", True, SNOW_WHITE)
        hint.set_alpha(int(128 + 127 * pulse))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, box.bottom + 30)))

    def _start_ending_music(self):
        if os.path.isfile(ENDING_MUSIC_FILE):
            try:
                pygame.mixer.music.load(ENDING_MUSIC_FILE)
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
                return
            except: pass
        # Fallback: replay level music at lower volume
        if os.path.isfile(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)
            except: pass

    def _draw_ending_npcs(self):
        """Draw NPCs and sparkles during ending dialogue."""
        bot_y = SCREEN_HEIGHT - 200
        # Elder Frost (left side)
        if self.ending_npc_x > -30:
            nx = int(self.ending_npc_x)
            # Simple robe figure
            pygame.draw.polygon(self.screen, NPC_ROBE, [(nx+4,bot_y+14),(nx+20,bot_y+14),(nx+22,bot_y+40),(nx,bot_y+40)])
            pygame.draw.circle(self.screen, (220,190,160), (nx+12, bot_y+10), 8)
            pygame.draw.arc(self.screen, NPC_ROBE, (nx+2, bot_y, 20, 18), 0.3, 2.8, 3)
            pygame.draw.circle(self.screen, WHITE, (nx+9, bot_y+9), 2)
            pygame.draw.circle(self.screen, WHITE, (nx+15, bot_y+9), 2)
            pygame.draw.circle(self.screen, BLACK, (nx+9, bot_y+10), 1)
            pygame.draw.circle(self.screen, BLACK, (nx+15, bot_y+10), 1)
            pygame.draw.line(self.screen, BROWN, (nx+22, bot_y+5), (nx+22, bot_y+40), 2)
            pygame.draw.circle(self.screen, XMAS_GOLD, (nx+22, bot_y+4), 4)
        # Holly (right side)
        if self.ending_holly_x < SCREEN_WIDTH + 20:
            hx = int(self.ending_holly_x)
            pygame.draw.polygon(self.screen, XMAS_GREEN, [(hx+4,bot_y+14),(hx+20,bot_y+14),(hx+22,bot_y+40),(hx,bot_y+40)])
            pygame.draw.circle(self.screen, (220,190,160), (hx+12, bot_y+10), 8)
            pygame.draw.arc(self.screen, XMAS_GREEN, (hx+2, bot_y, 20, 18), 0.3, 2.8, 3)
            pygame.draw.circle(self.screen, WHITE, (hx+9, bot_y+9), 2)
            pygame.draw.circle(self.screen, WHITE, (hx+15, bot_y+9), 2)
            pygame.draw.circle(self.screen, BLACK, (hx+9, bot_y+10), 1)
            pygame.draw.circle(self.screen, BLACK, (hx+15, bot_y+10), 1)
        # Jingle (right of Holly)
        if self.ending_jingle_x < SCREEN_WIDTH + 20:
            jx = int(self.ending_jingle_x)
            pygame.draw.polygon(self.screen, XMAS_RED, [(jx+4,bot_y+14),(jx+20,bot_y+14),(jx+22,bot_y+40),(jx,bot_y+40)])
            pygame.draw.circle(self.screen, (220,190,160), (jx+12, bot_y+10), 8)
            pygame.draw.arc(self.screen, XMAS_RED, (jx+2, bot_y, 20, 18), 0.3, 2.8, 3)
            pygame.draw.circle(self.screen, WHITE, (jx+9, bot_y+9), 2)
            pygame.draw.circle(self.screen, WHITE, (jx+15, bot_y+9), 2)
            pygame.draw.circle(self.screen, BLACK, (jx+9, bot_y+10), 1)
            pygame.draw.circle(self.screen, BLACK, (jx+15, bot_y+10), 1)
        # Golden sparkles
        for sp in self.ending_sparkles:
            a = max(0, min(255, int(255 * sp[4] / 70)))
            sz = max(1, int(3 * sp[4] / 70))
            c = (255, 200, 50, a)
            gs = pygame.Surface((sz*2+2, sz*2+2), pygame.SRCALPHA)
            pygame.draw.circle(gs, c, (sz+1, sz+1), sz)
            self.screen.blit(gs, (int(sp[0])-sz-1, int(sp[1])-sz-1))

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
