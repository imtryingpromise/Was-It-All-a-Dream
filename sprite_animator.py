import pygame


def load_sprite_sheet(path, frame_width, frame_height, scale=None):
    """
    Slice a horizontal sprite sheet into a list of surfaces.

    Args:
        path         : path to the image file
        frame_width  : width of ONE frame in the sheet (pixels)
        frame_height : height of ONE frame in the sheet (pixels)
        scale        : optional (w, h) to scale every frame to

    Returns:
        List of pygame.Surface frames with per-pixel alpha.
    """
    sheet = pygame.image.load(path).convert_alpha()
    sheet_w = sheet.get_width()
    num_frames = sheet_w // frame_width

    frames = []
    for i in range(num_frames):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
        if scale:
            frame = pygame.transform.scale(frame, scale)
        frames.append(frame)

    return frames


class SpriteAnimator:
    """
    Manages named animations and advances frames at a fixed tick rate.

    Usage:
        animator = SpriteAnimator(frame_delay=5)
        animator.add("idle", load_sprite_sheet("idle.png", 24, 32, scale=(72, 96)))
        animator.add("walk", load_sprite_sheet("walk.png", 26, 33, scale=(72, 96)))
        animator.set_state("idle")

        # Each game loop tick:
        animator.update()
        surface.blit(animator.get_frame(facing_left=False), (x, y))
    """

    def __init__(self, frame_delay=5):
        self.animations  = {}
        self._flipped    = {}
        self.current     = None
        self.frame_index = 0
        self.frame_delay = frame_delay
        self._tick       = 0

    def add(self, name, frames):
        """Register an animation. Pre-caches horizontally-flipped copies."""
        self.animations[name] = frames
        self._flipped[name]   = [pygame.transform.flip(f, True, False) for f in frames]
        if self.current is None:
            self.current = name

    def set_state(self, name, reset=False):
        """
        Switch to animation name.
        reset=True restarts from frame 0 (use for one-shot anims like death/hit).
        Does nothing if the animation is not registered.
        """
        if name not in self.animations:
            return
        if self.current != name:
            self.current     = name
            self.frame_index = 0
            self._tick       = 0
        elif reset:
            self.frame_index = 0
            self._tick       = 0

    def update(self):
        """Advance the animation by one tick. Call exactly once per game loop."""
        if not self.current:
            return
        self._tick += 1
        if self._tick >= self.frame_delay:
            self._tick = 0
            total = len(self.animations[self.current])
            self.frame_index = (self.frame_index + 1) % total

    def get_frame(self, facing_left=False):
        """Return the current Surface, flipped if facing left."""
        if not self.current:
            return None
        src = self._flipped if facing_left else self.animations
        return src[self.current][self.frame_index]

    @property
    def finished(self):
        """True when on the last frame — useful for one-shot animations."""
        if not self.current:
            return False
        return self.frame_index == len(self.animations[self.current]) - 1