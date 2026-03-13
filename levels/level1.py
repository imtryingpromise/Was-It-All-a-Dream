import pygame
import os
from settings import *

# ─────────────────────────────────────────────────────────────────────────────
#  All coordinates are pre-calculated for 1280x720.
#  They were pixel-verified by overlaying lines on the actual map image.
# ─────────────────────────────────────────────────────────────────────────────

CHAR_DIR     = os.path.join("assets", "sprites", "character")
SPRITE_SCALE = (48, 48)
COIN_SIZE    = 24
CLIMB_SPEED  = 3
SW, SH       = 1280, 720


# ── helpers ──────────────────────────────────────────────────────────────────
def load_sheet(path, frame_w, frame_h, scale, n):
    sheet  = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(n):
        f = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        f.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
        frames.append(pygame.transform.scale(f, scale))
    return frames


# ── Animator ─────────────────────────────────────────────────────────────────
class Animator:
    def __init__(self, delay=6):
        self.anims = {}; self.flipped = {}
        self.cur = None; self.idx = 0
        self.delay = delay; self._tick = 0

    def add(self, name, frames):
        self.anims[name]   = frames
        self.flipped[name] = [pygame.transform.flip(f, True, False) for f in frames]
        if self.cur is None: self.cur = name

    def set(self, name, force=False):
        if name not in self.anims: return
        if self.cur != name or force:
            self.cur = name; self.idx = 0; self._tick = 0

    def update(self):
        self._tick += 1
        if self._tick >= self.delay:
            self._tick = 0
            self.idx = (self.idx + 1) % len(self.anims[self.cur])

    def frame(self, left=False):
        return (self.flipped if left else self.anims)[self.cur][self.idx]

    @property
    def done(self):
        return self.idx == len(self.anims[self.cur]) - 1





# ── Player ───────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y, anim):
        self.rect     = pygame.Rect(x, y, SPRITE_SCALE[0], SPRITE_SCALE[1])
        self.vel_y    = 0
        self.anim     = anim
        self.left     = False
        self.grounded = False
        self.on_chain = False
        self.dead     = False
        self.jump_buf = 0
        self.coyote   = 0

    def input(self, keys, chains):
        if self.dead: return
        if keys[pygame.K_a]: self.rect.x -= PLAYER_SPEED; self.left = True
        if keys[pygame.K_d]: self.rect.x += PLAYER_SPEED; self.left = False

        self.on_chain = False
        for c in chains:
            if self.rect.colliderect(c.inflate(20, 0)):
                self.on_chain = True
                if keys[pygame.K_w]: self.rect.y -= CLIMB_SPEED; self.vel_y = 0
                if keys[pygame.K_s]: self.rect.y += CLIMB_SPEED; self.vel_y = 0
                break

        if keys[pygame.K_SPACE] or keys[pygame.K_w]:
            self.jump_buf = 8

    def physics(self, platforms):
        prev_bottom = self.rect.bottom

        if not self.on_chain:
            self.vel_y = min(self.vel_y + GRAVITY, 20)
            self.rect.y += int(self.vel_y)

        self.grounded = False
        for p in platforms:
            if self.rect.colliderect(p) and self.vel_y >= 0:
                if prev_bottom <= p.top + 4:
                    self.rect.bottom = p.top
                    self.vel_y       = 0
                    self.grounded    = True
                    self.coyote      = 6

        if self.jump_buf > 0:
            self.jump_buf -= 1
            if self.grounded or self.on_chain or self.coyote > 0:
                self.vel_y    = JUMP_FORCE
                self.on_chain = False
                self.jump_buf = 0
                self.coyote   = 0

        if self.coyote > 0: self.coyote -= 1
        self.rect.x = max(0, min(self.rect.x, SW - self.rect.w))

    def animate(self, keys):
        moving = keys[pygame.K_a] or keys[pygame.K_d]
        if self.dead:
            self.anim.set("death"); self.anim.update()
        elif self.on_chain:
            self.anim.set("climb")
            if keys[pygame.K_w] or keys[pygame.K_s]: self.anim.update()
        elif not self.grounded:
            self.anim.set("jump"); self.anim.update()
        elif moving:
            self.anim.set("walk"); self.anim.update()
        else:
            self.anim.set("idle"); self.anim.update()



    def draw(self, surf):
        surf.blit(self.anim.frame(self.left), self.rect)


# ─────────────────────────────────────────────────────────────────────────────
#  LEVEL DATA — pixel-verified for 1280x720
#  (x, y, w, h)  where y = TOP of the walkable surface
# ─────────────────────────────────────────────────────────────────────────────

PLATFORMS = [
    # Main floor above lava
    pygame.Rect(0,   596, 1280,  124),
    # Upper left platform
    pygame.Rect(156, 157,  516,   40),
    # Wide middle row
    pygame.Rect(0,   329, 1280,   40),
    # Mid shelves — left
    pygame.Rect(61,  385,  183,   30),
    # Mid shelves — right
    pygame.Rect(730, 385,  408,   30),
    # Lower shelves
    pygame.Rect(0,   568,  167,   28),
    pygame.Rect(233, 568,  450,   28),
    pygame.Rect(616, 568,  100,   28),
    pygame.Rect(875, 568,  405,   28),
]

BRIDGES = [
    # Upper gold bridge
    pygame.Rect(280, 157,  291,   16),
    # Lower gold bridge
    pygame.Rect(96,  208,  675,   16),
]

SPIKE_ZONES = [
    # Top ceiling spikes (player hits from below — kill on any contact)
    pygame.Rect(290,  27,  750,   28),
    # Upper right spikes
    pygame.Rect(648, 165,  217,   28),
    # Mid left spikes (on top of wide middle)
    pygame.Rect(220, 301,  100,   28),
    # Mid lower spikes
    pygame.Rect(233, 500,  317,   28),
    # Bottom row spikes
    pygame.Rect(408, 597,  517,   28),
]

CHAINS = [
    # (x, y_top, height)
    pygame.Rect(50,   43, 14, 196),
    pygame.Rect(545, 302, 14, 200),
    pygame.Rect(775,  43, 14, 152),
    pygame.Rect(1000, 87, 14, 350),
]

# Coin positions: (screen_x_center, platform_top_y)
# Coin will be placed COIN_SIZE+6 px above the platform top
COIN_POSITIONS = [
    # Upper left platform (y=157)
    (200, 157), (290, 157), (380, 157), (470, 157), (570, 157),
    # Upper gold bridge (y=157)
    (330, 157), (420, 157), (510, 157),
    # Lower gold bridge (y=208)
    (150, 208), (280, 208), (430, 208), (580, 208), (700, 208),
    # Wide middle (y=329)
    (80,  329), (300, 329), (600, 329), (900, 329), (1150, 329),
    # Mid left shelf (y=385)
    (100, 385), (180, 385),
    # Mid right shelf (y=385)
    (800, 385), (900, 385), (1050, 385),
    # Lower shelves (y=568)
    (80,  568), (380, 568), (640, 568), (1000, 568),
    # Main floor (y=596)
    (350, 596), (600, 596), (850, 596), (1100, 596),
]


# ─────────────────────────────────────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────────────────────────────────────
def run_level1(screen):
    clock = pygame.time.Clock()

    # ── Music ────────────────────────────────────────────────────────────────
    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/audio/Level1Music.mp3")
    pygame.mixer.music.play(-1)

    # ── Map ──────────────────────────────────────────────────────────────────
    # Use new background image (Level1Backroung.png)
    map_img = pygame.transform.scale(
        pygame.image.load("assets/backgrounds/Level1Background.png").convert(),
        (SW, SH)
    )



    # ── Animator ─────────────────────────────────────────────────────────────
    anim = Animator(delay=6)
    anim.add("idle",  load_sheet(f"{CHAR_DIR}/Owlet_Monster_Idle_4.png",  32, 32, SPRITE_SCALE, 4))
    anim.add("walk",  load_sheet(f"{CHAR_DIR}/Owlet_Monster_Walk_6.png",  32, 32, SPRITE_SCALE, 6))
    anim.add("jump",  load_sheet(f"{CHAR_DIR}/Owlet_Monster_Jump_8.png",  32, 32, SPRITE_SCALE, 8))
    anim.add("climb", load_sheet(f"{CHAR_DIR}/Owlet_Monster_Climb_4.png", 32, 32, SPRITE_SCALE, 4))
    anim.add("death", load_sheet(f"{CHAR_DIR}/Owlet_Monster_Death_8.png", 32, 32, SPRITE_SCALE, 8))

    # ── Objects ───────────────────────────────────────────────────────────────
    # Player walks on the grass (flat land) in the new background
    GRASS_Y = 650  # Adjust this value to match the grass top in the new image
    GRASS_HEIGHT = 70
    GRASS_PLATFORM = [pygame.Rect(0, GRASS_Y, SW, GRASS_HEIGHT)]
    all_solid = GRASS_PLATFORM

    # Spawn on grass
    SPAWN  = (60, GRASS_Y - SPRITE_SCALE[1])
    player = Player(SPAWN[0], SPAWN[1], anim)



    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        player.input(keys, [])  # No chains
        player.physics(all_solid)
        player.animate(keys)

        # Draw
        screen.blit(map_img, (0, 0))
        player.draw(screen)
        pygame.display.update()
        clock.tick(FPS)