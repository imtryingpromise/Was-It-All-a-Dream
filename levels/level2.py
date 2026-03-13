import pygame

def run_level2(screen):

    clock = pygame.time.Clock()

    WIDTH = 1200
    HEIGHT = 650
    FPS = 60

    GRAVITY = 0.8
    PLAYER_SPEED = 6
    JUMP_FORCE = -16

    player = pygame.Rect(100,500,40,60)

    vel_y = 0
    vel_x = 0
    on_ground = False

    spawn = (100,500)

    # -----------------
    # PLATFORM CLASSES
    # -----------------

    class ShrinkingPlatform:

        def __init__(self,x,y,w,h):
            self.rect = pygame.Rect(x,y,w,h)
            self.shrinking = False

        def update(self):
            if self.shrinking:
                self.rect.width -= 1
                if self.rect.width < 0:
                    self.rect.width = 0

        def draw(self):
            pygame.draw.rect(screen,(200,60,60),self.rect)


    class FallingPlatform:

        def __init__(self,x,y,w,h):
            self.rect = pygame.Rect(x,y,w,h)
            self.vel = 0
            self.falling = False

        def update(self):
            if self.falling:
                self.vel += 0.2
                self.rect.y += self.vel

        def draw(self):
            pygame.draw.rect(screen,(60,120,220),self.rect)


    class PhantomPlatform:

        def __init__(self,x,y,w,h):
            self.rect = pygame.Rect(x,y,w,h)
            self.timer = 0
            self.active = True

        def update(self):
            if self.timer > 0:
                self.timer += 1
                if self.timer > 10:
                    self.active = False

        def draw(self):
            if self.active:
                pygame.draw.rect(screen,(120,220,120),self.rect,2)


    class Balloon:

        def __init__(self,x,y):
            self.rect = pygame.Rect(x,y,30,40)
            self.used = False

        def draw(self):
            if not self.used:
                pygame.draw.ellipse(screen,(255,80,80),self.rect)

    # -----------------
    # LEVEL OBJECTS
    # -----------------

    shrinking = [
        ShrinkingPlatform(350,520,120,20),
        ShrinkingPlatform(520,480,120,20)
    ]

    falling = [
        FallingPlatform(700,450,120,20),
        FallingPlatform(850,420,120,20)
    ]

    phantom = [
        PhantomPlatform(1050,380,100,20)
    ]

    balloons = [
        Balloon(920,350)
    ]

    spikes = [
        pygame.Rect(880,580,120,20)
    ]

    portal = pygame.Rect(1150,500,40,80)

    running = True

    while running:

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()

        vel_x = 0

        if keys[pygame.K_a]:
            vel_x = -PLAYER_SPEED

        if keys[pygame.K_d]:
            vel_x = PLAYER_SPEED

        if keys[pygame.K_w] and on_ground:
            vel_y = JUMP_FORCE

        player.x += vel_x

        vel_y += GRAVITY
        player.y += vel_y

        on_ground = False

        # -----------------
        # PLATFORM COLLISION
        # -----------------

        for p in shrinking:

            p.update()

            if player.colliderect(p.rect) and vel_y > 0:
                player.bottom = p.rect.top
                vel_y = 0
                on_ground = True
                p.shrinking = True

        for p in falling:

            p.update()

            if player.colliderect(p.rect) and vel_y > 0:
                player.bottom = p.rect.top
                vel_y = 0
                on_ground = True
                p.falling = True

        for p in phantom:

            p.update()

            if p.active and player.colliderect(p.rect) and vel_y > 0:
                player.bottom = p.rect.top
                vel_y = 0
                on_ground = True
                p.timer = 1

        # -----------------
        # BALLOON LAUNCH
        # -----------------

        for b in balloons:

            if player.colliderect(b.rect) and not b.used:
                b.used = True
                vel_y = -18
                vel_x = 10

        # -----------------
        # SPIKES
        # -----------------

        for s in spikes:
            if player.colliderect(s):
                player.x,player.y = spawn
                vel_y = 0

        # -----------------
        # FALL RESET
        # -----------------

        if player.y > HEIGHT:
            player.x,player.y = spawn
            vel_y = 0

        # -----------------
        # PORTAL
        # -----------------

        if player.colliderect(portal):
            running = False

        # -----------------
        # DRAW
        # -----------------

        screen.fill((200,230,255))

        for p in shrinking:
            p.draw()

        for p in falling:
            p.draw()

        for p in phantom:
            p.draw()

        for b in balloons:
            b.draw()

        for s in spikes:
            pygame.draw.rect(screen,(255,255,255),s)

        pygame.draw.rect(screen,(255,255,0),portal)

        pygame.draw.rect(screen,(0,0,0),player)

        pygame.display.update()
        clock.tick(FPS)