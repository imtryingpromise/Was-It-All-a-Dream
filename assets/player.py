import pygame
import sys
import os

# player.py is at: imaging-assignment/assets/sprites/character/player.py
# sprite_animator.py is at: imaging-assignment/sprite_animator.py
# Go up 3 levels: character -> sprites -> assets -> root
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from sprite_animator import SpriteAnimator, load_sprite_sheet

SPRITE_SCALE = (72, 96)
SPRITE_DIR   = os.path.dirname(os.path.abspath(__file__))


def _detect_frame_size(path, fallback_w=24, fallback_h=32):
    if not os.path.exists(path):
        return fallback_w, fallback_h
    surf = pygame.image.load(path)
    h = surf.get_height()
    return h, h


class Player:
    def __init__(self, x, y, gravity, jump_force, player_speed):
        self.rect         = pygame.Rect(x, y, SPRITE_SCALE[0], SPRITE_SCALE[1])
        self.vel_y        = 0
        self.gravity      = gravity
        self.jump_force   = jump_force
        self.player_speed = player_speed

        self.jump_count    = 0
        self.on_fake_block = False
        self.facing_left   = False

        self.coyote_frames    = 0
        self.COYOTE_TIME      = 6
        self.jump_buffer      = 0
        self.JUMP_BUFFER_TIME = 8
        self.squish_timer     = 0

        # ── Animator ─────────────────────────────────────────────────────────
        self.animator = SpriteAnimator(frame_delay=5)

        # Idle — required
        self.animator.add("idle", load_sprite_sheet(
            os.path.join(SPRITE_DIR, "Skeleton Idle.png"),
            24, 32, scale=SPRITE_SCALE
        ))

        # Walk — known: 26x33 per frame
        self._try_add("walk", "Skeleton Walk.png", frame_w=26, frame_h=33)

        # All other sheets — auto-detect frame size
        for name, filename in [
            ("attack", "Skeleton Attack.png"),
            ("dead",   "Skeleton Dead.png"),
            ("hit",    "Skeleton Hit.png"),
            ("react",  "Skeleton React.png"),
        ]:
            fw, fh = _detect_frame_size(os.path.join(SPRITE_DIR, filename))
            self._try_add(name, filename, frame_w=fw, frame_h=fh)

        self.animator.set_state("idle")

    # ── Private ──────────────────────────────────────────────────────────────

    def _try_add(self, name, filename, frame_w, frame_h):
        path = os.path.join(SPRITE_DIR, filename)
        if os.path.exists(path):
            self.animator.add(name, load_sprite_sheet(
                path, frame_w, frame_h, scale=SPRITE_SCALE
            ))

    def _set_anim(self, name):
        if name in self.animator.animations:
            self.animator.set_state(name)
        else:
            self.animator.set_state("idle")

    def _do_jump(self):
        self.vel_y = self.jump_force
        self.jump_count += 1

    # ── Public API ───────────────────────────────────────────────────────────

    def try_jump(self):
        self.jump_buffer = self.JUMP_BUFFER_TIME

    def handle_jump(self):
        max_jumps = 1 if self.on_fake_block else 2
        if self.coyote_frames > 0 and self.jump_count == 0:
            self._do_jump()
            self.coyote_frames = 0
        elif self.jump_count < max_jumps:
            self._do_jump()

    def land(self, block_top, is_fake=False):
        was_airborne       = self.vel_y > 0
        self.rect.bottom   = block_top
        self.vel_y         = 0
        self.on_fake_block = is_fake
        self.coyote_frames = self.COYOTE_TIME
        self.jump_count    = 0
        if self.jump_buffer > 0 and was_airborne:
            self._do_jump()
            self.jump_buffer = 0
        if was_airborne:
            self.squish_timer = 6

    def update(self, keys):
        moving = False

        if keys[pygame.K_a]:
            self.rect.x     -= self.player_speed
            self.facing_left  = True
            moving            = True
        if keys[pygame.K_d]:
            self.rect.x     += self.player_speed
            self.facing_left  = False
            moving            = True

        # Animation state
        if self.vel_y < -1:
            self._set_anim("attack")
        elif moving:
            self._set_anim("walk")
        else:
            self._set_anim("idle")

        self.animator.update()

        # Physics
        self.vel_y  += self.gravity
        self.rect.y += int(self.vel_y)

        # Timers
        if self.coyote_frames > 0: self.coyote_frames -= 1
        if self.jump_buffer   > 0: self.jump_buffer   -= 1
        if self.squish_timer  > 0: self.squish_timer  -= 1

    def reset(self, spawn):
        self.rect.x, self.rect.y = spawn
        self.vel_y         = 0
        self.jump_count    = 0
        self.on_fake_block = False
        self.facing_left   = False
        self.coyote_frames = 0
        self.jump_buffer   = 0
        self.squish_timer  = 0
        self.animator.set_state("idle", reset=True)

    def draw(self, surface):
        frame = self.animator.get_frame(facing_left=self.facing_left)
        if frame:
            if self.squish_timer > 0:
                t      = self.squish_timer / 6
                w      = int(SPRITE_SCALE[0] * (1 + 0.2  * t))
                h      = int(SPRITE_SCALE[1] * (1 - 0.15 * t))
                frame  = pygame.transform.scale(frame, (w, h))
                draw_x = self.rect.centerx - w // 2
                draw_y = self.rect.bottom  - h
            else:
                draw_x = self.rect.x
                draw_y = self.rect.y
            surface.blit(frame, (draw_x, draw_y))
        else:
            pygame.draw.rect(surface, (30, 30, 30), self.rect, border_radius=6)