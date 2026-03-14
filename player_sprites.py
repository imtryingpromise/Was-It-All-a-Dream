"""
Shared Owlet Monster sprite rendering for all levels.
Handles loading sprite sheets, animation state, and drawing.
"""
import os
import math
import pygame

SPRITE_SIZE = 32
_sprites_loaded = False
_sprite_frames = {}       # {'idle': [frames], 'walk': [...], ...}
_sprite_frames_flip = {}  # pre-flipped versions

def _load_sprites():
    global _sprites_loaded, _sprite_frames, _sprite_frames_flip
    if _sprites_loaded:
        return
    sprite_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sprites', 'character')
    sheet_info = {
        'idle':  ('Owlet_Monster_Idle_4.png',  4),
        'walk':  ('Owlet_Monster_Walk_6.png',  6),
        'jump':  ('Owlet_Monster_Jump_8.png',  8),
        'death': ('Owlet_Monster_Death_8.png', 8),
        'climb': ('Owlet_Monster_Climb_4.png', 4),
    }
    for anim, (filename, frame_count) in sheet_info.items():
        sheet = pygame.image.load(os.path.join(sprite_dir, filename)).convert_alpha()
        frames = []
        flipped = []
        for i in range(frame_count):
            frame = sheet.subsurface(pygame.Rect(i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))
            frames.append(frame)
            flipped.append(pygame.transform.flip(frame, True, False))
        _sprite_frames[anim] = frames
        _sprite_frames_flip[anim] = flipped
    _sprites_loaded = True


# Animation speeds (ticks per frame) for each state
_ANIM_SPEEDS = {'idle': 10, 'walk': 6, 'jump': 6, 'death': 8, 'climb': 8}


def init_player_sprite(player):
    """Call this in Player.__init__ to set up sprite animation state."""
    _load_sprites()
    player._spr_state = 'idle'
    player._spr_frame = 0
    player._spr_tick = 0
    player._spr_death_done = False


def get_anim_state(player):
    """Determine animation state from player attributes."""
    if not player.alive:
        return 'death'
    wall_sliding = getattr(player, 'wall_sliding', False)
    if wall_sliding:
        return 'climb'
    dashing = getattr(player, 'dashing', False)
    if dashing or (not player.on_ground and player.vel_y < -1):
        return 'jump'
    if not player.on_ground and player.vel_y > 1:
        return 'jump'
    if abs(player.vel_x) > 0.5:
        return 'walk'
    return 'idle'


def advance_animation(player):
    """Advance the animation by one tick. Returns the current frame surface."""
    state = get_anim_state(player)
    frames = _sprite_frames[state]

    # Handle state transitions
    if state != player._spr_state:
        player._spr_state = state
        player._spr_frame = 0
        player._spr_tick = 0

    player._spr_tick += 1
    speed = _ANIM_SPEEDS.get(state, 8)
    if player._spr_tick >= speed:
        player._spr_tick = 0
        if state == 'death':
            if player._spr_frame < len(frames) - 1:
                player._spr_frame += 1
            else:
                player._spr_death_done = True
        else:
            player._spr_frame = (player._spr_frame + 1) % len(frames)

    idx = min(player._spr_frame, len(frames) - 1)
    if not player.facing_right:
        return _sprite_frames_flip[state][idx]
    return frames[idx]


def draw_player_sprite(player, surface, camera, tick, unreal_tint_fn=None):
    """
    Draw the player sprite. Replaces pygame.draw-based player rendering.

    player          - the Player instance (must have rect, alive, facing_right, vel_x, vel_y, on_ground)
    surface         - pygame display surface
    camera          - camera with .apply(rect) method
    tick            - game tick counter
    unreal_tint_fn  - optional callable(tick) -> (r,g,b) for unreal mode color cycling.
                      If provided and player.is_unreal is True, the sprite gets tinted.
    """
    is_unreal = getattr(player, 'is_unreal', False)
    invincibility = getattr(player, 'invincibility', 0)
    squash_timer = getattr(player, 'squash_timer', 0)
    was_on_ground = getattr(player, 'was_on_ground', False)
    dashing = getattr(player, 'dashing', False)
    dash_afterimages = getattr(player, 'dash_afterimages', [])

    # Death animation
    if not player.alive:
        if player._spr_death_done:
            return
        sr = camera.apply(player.rect)
        frame = advance_animation(player)
        scale_w, scale_h = int(sr.width * 1.8), int(sr.height * 1.6)
        scaled = pygame.transform.scale(frame, (scale_w, scale_h))
        surface.blit(scaled, (sr.centerx - scale_w // 2, sr.bottom - scale_h))
        return

    # Squash timer update
    if player.on_ground and not was_on_ground:
        player.squash_timer = 6
    if squash_timer > 0:
        player.squash_timer -= 1

    # Invincibility flicker
    if invincibility > 0 and (invincibility // 4) % 2 == 0:
        advance_animation(player)  # keep animation advancing even when flickering
        return

    # Dash afterimages (level4 only)
    if dash_afterimages:
        for ax, ay, aa in dash_afterimages:
            ar = camera.apply(pygame.Rect(ax, ay, player.WIDTH, player.HEIGHT))
            idx = min(player._spr_frame, len(_sprite_frames[player._spr_state]) - 1)
            if not player.facing_right:
                ai_frame = _sprite_frames_flip[player._spr_state][idx]
            else:
                ai_frame = _sprite_frames[player._spr_state][idx]
            ai_w, ai_h = int(ar.width * 1.8), int(ar.height * 1.6)
            ai_scaled = pygame.transform.scale(ai_frame, (ai_w, ai_h))
            ai_surf = ai_scaled.copy()
            ai_surf.set_alpha(int(aa * 0.5))
            surface.blit(ai_surf, (ar.centerx - ai_w // 2, ar.bottom - ai_h))

    sr = camera.apply(player.rect)

    # Squash & stretch visual adjustment
    if player.vel_y < -3 and not player.on_ground:
        stretch = 4
        sr = sr.inflate(-4, stretch * 2)
        sr.bottom += stretch
    elif getattr(player, 'squash_timer', 0) > 0:
        sq = int(player.squash_timer * 0.8)
        sr = sr.inflate(sq * 2, -sq * 2)
        sr.bottom += sq

    # Get current animation frame
    frame = advance_animation(player)
    scale_w, scale_h = int(sr.width * 1.8), int(sr.height * 1.6)
    scaled = pygame.transform.scale(frame, (scale_w, scale_h))

    # Unreal mode tint
    if is_unreal and unreal_tint_fn is not None:
        bc = unreal_tint_fn(tick)
        pulse = abs(math.sin(tick * 0.15)) * 0.5 + 0.5
        tint_surf = scaled.copy()
        tint_strength = int(40 + 30 * pulse)
        tint_surf.fill((tint_strength, tint_strength, tint_strength), special_flags=pygame.BLEND_RGB_ADD)
        tint_surf.fill((*bc, 255), special_flags=pygame.BLEND_RGB_MULT)
        blended = scaled.copy()
        tint_surf.set_alpha(int(100 + 55 * pulse))
        blended.blit(tint_surf, (0, 0))
        scaled = blended

    blit_x = sr.centerx - scale_w // 2
    blit_y = sr.bottom - scale_h
    surface.blit(scaled, (blit_x, blit_y))

    # Wall slide scratchy lines (level4 only)
    wall_sliding = getattr(player, 'wall_sliding', False)
    if wall_sliding:
        import random
        wall_side = getattr(player, 'wall_side', 0)
        wx = sr.left if wall_side == -1 else sr.right
        for i in range(4):
            sy2 = sr.y + 5 + i * 8 + random.randint(-1, 1)
            pygame.draw.line(surface, (255, 255, 255), (wx, sy2),
                             (wx + random.randint(-3, 3), sy2 + random.randint(4, 8)), 1)
