from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ...protocols import ScreenProtocol, AsciiQuariumProtocol
    from ...screen_compat import Screen
else:
    from ...screen_compat import Screen

from ...util import draw_sprite, draw_sprite_masked, randomize_colour_mask
from .fish_assets import (
    FISH_RIGHT,
    FISH_LEFT,
    FISH_RIGHT_MASKS,
    FISH_LEFT_MASKS,
)
from .bubble import Bubble
from ...constants import (
    MOVEMENT_MULTIPLIER,
    FISH_DEFAULT_SPEED_MIN,
    FISH_DEFAULT_SPEED_MAX,
    FISH_BUBBLE_DEFAULT_MIN,
    FISH_BUBBLE_DEFAULT_MAX,
    FISH_BUBBLE_INTERVAL_MIN,
    FISH_BUBBLE_INTERVAL_MAX,
    FISH_TURN_SHRINK_DURATION,
    FISH_TURN_EXPAND_DURATION,
    FISH_TURN_COOLDOWN_MIN,
    FISH_TURN_COOLDOWN_MAX,
)


@dataclass
class Fish:
    """Main fish entity representing the core population of the aquarium.

    Fish are the primary animated entities in the simulation, providing visual interest
    through movement, bubble generation, and interactive behaviors. Each fish maintains
    its own state for position, velocity, appearance, and behavioral parameters.

    Key Features:
        **Movement System**: Fish move horizontally across the screen with configurable
        speed ranges and turning animations. Movement includes smooth direction changes
        with shrink/expand animations during turns.

        **Bubble Generation**: Fish periodically generate bubble entities at randomized
        intervals, contributing to the aquatic atmosphere.

        **Interactive Behavior**: Fish can be caught by fishhooks, with collision
        detection and hook-following mechanics.

        **Visual Customization**: Support for different fish sprites, colors, and
        z-depth layering for visual depth.

        **Behavioral Configuration**: Extensive configuration options for movement
        speed, bubble timing, turning behavior, and movement constraints.

    Architecture:
        The Fish class follows a data-oriented design using dataclasses for efficient
        memory layout and serialization. It implements the Actor protocol for consistent
        update/render behavior within the entity system.

    State Management:
        - **Position State**: x, y coordinates with floating-point precision
        - **Movement State**: velocity (vx), speed constraints, and turning phases
        - **Visual State**: sprite frames, color, z-depth, and color masks
        - **Interaction State**: hook attachment and displacement tracking
        - **Timing State**: bubble generation and turn cooldown timers

    Performance:
        Fish entities are designed for high-frequency updates (20-60 FPS) with
        minimal computational overhead. Movement calculations use simple linear
        interpolation, and collision detection is optimized for common cases.

    Attributes:
        frames (List[str]): Sprite frames for fish appearance (typically 2-4 lines)
        x (float): Horizontal position with sub-pixel precision
        y (float): Vertical position with sub-pixel precision
        vx (float): Horizontal velocity (positive = rightward movement)
        colour (int): Color index for terminal/display rendering
        z (int): Z-depth for layering (higher values draw on top). Default: 3-20
        colour_mask (List[str] | None): Optional color mask for advanced rendering

        next_bubble (float): Countdown timer until next bubble generation
        hooked (bool): Whether fish is attached to a fishhook
        hook_dx (int): Horizontal displacement when hooked
        hook_dy (int): Vertical displacement when hooked

        speed_min/max (float): Velocity range constraints for movement
        bubble_min/max (float): Interval range for bubble generation timing

        band_low_frac/high_frac (float): Vertical movement constraints as screen fractions
        waterline_top (int): Top row of water area for positioning
        water_rows (int): Number of water surface rows to avoid

        turning (bool): Whether fish is currently performing turn animation
        turn_phase (str): Current turn state - "idle", "shrink", "flip", or "expand"
        turn_t (float): Timer for current turn phase
        turn_shrink/expand_seconds (float): Duration of turn animation phases
        base_speed (float): Original speed before turn modifications
        next_turn_ok_in (float): Cooldown timer preventing frequent turns

        turn_enabled (bool): Global setting for turn animation system
        turn_chance_per_second (float): Probability of initiating turn per second
        turn_min_interval (float): Minimum time between turn attempts

    Example:
        >>> from asciiquarium_redux.entities.core.fish_assets import random_fish_frames
        >>>
        >>> # Create a basic fish
        >>> frames = random_fish_frames()
        >>> fish = Fish(
        ...     frames=frames,
        ...     x=10.0, y=15.0, vx=1.5,
        ...     colour=Screen.COLOUR_YELLOW
        ... )
        >>>
        >>> # Configure behavior
        >>> fish.speed_min = 0.8
        >>> fish.speed_max = 2.0
        >>> fish.bubble_min = 1.5
        >>> fish.bubble_max = 4.0
        >>>
        >>> # Update in game loop
        >>> fish.update(dt=0.016, screen=screen, app=aquarium)
        >>> fish.draw(screen, mono=False)

    See Also:
        - Bubble: Entities generated by fish bubble system
        - FishHook: Interactive entity that can catch fish
        - random_fish_frames(): Factory function for fish sprite generation
        - Entity System Documentation: docs/ENTITY_SYSTEM.md
    """

    frames: List[str]
    x: float
    y: float
    vx: float
    colour: int
    # Z-depth for layering between fish (higher draws on top)
    z: int = field(default_factory=lambda: random.randint(3, 20))
    colour_mask: List[str] | None = None
    next_bubble: float = field(default_factory=lambda: random.uniform(FISH_BUBBLE_INTERVAL_MIN, FISH_BUBBLE_INTERVAL_MAX))
    # Hook interaction state
    hooked: bool = False
    hook_dx: int = 0
    hook_dy: int = 0
    # Configurable movement and bubble behavior
    speed_min: float = FISH_DEFAULT_SPEED_MIN
    speed_max: float = FISH_DEFAULT_SPEED_MAX
    bubble_min: float = FISH_BUBBLE_DEFAULT_MIN
    bubble_max: float = FISH_BUBBLE_DEFAULT_MAX
    # Y-band as fractions of screen height, plus waterline context
    band_low_frac: float = 0.0
    band_high_frac: float = 1.0
    waterline_top: int = 5
    water_rows: int = 3
    # Turning state
    turning: bool = False
    turn_phase: str = "idle"  # shrink | flip | expand | idle
    turn_t: float = 0.0
    turn_shrink_seconds: float = FISH_TURN_SHRINK_DURATION
    turn_expand_seconds: float = FISH_TURN_EXPAND_DURATION
    base_speed: float = 0.0
    next_turn_ok_in: float = field(default_factory=lambda: random.uniform(FISH_TURN_COOLDOWN_MIN, FISH_TURN_COOLDOWN_MAX))
    # Global fish settings references (populated by app)
    turn_enabled: bool = True
    turn_chance_per_second: float = 0.01
    turn_min_interval: float = 6.0

    @property
    def width(self) -> int:
        return max(len(row) for row in self.frames)

    @property
    def height(self) -> int:
        return len(self.frames)

    def update(self, dt: float, screen: "Screen", app: "AsciiQuariumProtocol") -> None:
        """Update fish behavior including movement, turning, and bubble generation.

        Args:
            dt: Delta time since last update (seconds)
            screen: Screen interface for boundary checking
            app: Main application instance for spawning bubbles
        """
        # Handle turn timer/chance
        if not self.hooked and self.turn_enabled:
            self.next_turn_ok_in = max(0.0, self.next_turn_ok_in - dt)
            if not self.turning and self.next_turn_ok_in <= 0.0:
                # Poisson process: chance per second scaled by dt
                if random.random() < max(0.0, self.turn_chance_per_second) * dt:
                    self.start_turn()

        # Movement with speed ramp depending on turning phase
        speed_scale = 1.0
        if self.turning:
            if self.turn_phase == "shrink":
                # slow down towards stop
                speed_scale = max(0.0, 1.0 - (self.turn_t / max(0.001, self.turn_shrink_seconds)))
            elif self.turn_phase == "expand":
                # speed up from stop
                speed_scale = min(1.0, (self.turn_t / max(0.001, self.turn_expand_seconds)))
            else:
                speed_scale = 0.0
        self.x += self.vx * dt * MOVEMENT_MULTIPLIER * speed_scale
        self.next_bubble -= dt
        if self.next_bubble <= 0:
            bubble_y = int(self.y + self.height // 2)
            bubble_x = int(self.x + (self.width if self.vx > 0 else -1))
            app.bubbles.append(Bubble(x=bubble_x, y=bubble_y))
            self.next_bubble = random.uniform(self.bubble_min, self.bubble_max)
        if self.vx > 0 and self.x > screen.width:
            self.respawn(screen, direction=1)
        elif self.vx < 0 and self.x + self.width < 0:
            self.respawn(screen, direction=-1)
        # Advance turn animation
        if self.turning:
            self.turn_t += dt
            if self.turn_phase == "shrink" and self.turn_t >= self.turn_shrink_seconds:
                # Reached middle: flip frames and direction, stop movement
                self.finish_shrink_and_flip()
            elif self.turn_phase == "expand" and self.turn_t >= self.turn_expand_seconds:
                # Done expanding
                self.turning = False
                self.turn_phase = "idle"
                self.turn_t = 0.0
                self.next_turn_ok_in = max(self.turn_min_interval, random.uniform(self.turn_min_interval, self.turn_min_interval + (FISH_TURN_COOLDOWN_MAX - FISH_TURN_COOLDOWN_MIN)))

    def respawn(self, screen: Screen, direction: int):
        # choose new frames and matching mask
        if direction > 0:
            frame_choices = list(zip(FISH_RIGHT, FISH_RIGHT_MASKS))
        else:
            frame_choices = list(zip(FISH_LEFT, FISH_LEFT_MASKS))
        frames, colour_mask = random.choice(frame_choices)
        self.frames = frames
        self.colour_mask = randomize_colour_mask(colour_mask)
        self.vx = random.uniform(self.speed_min, self.speed_max) * direction
        # compute y-band respecting waterline and screen size
        default_low_y = max(self.waterline_top + self.water_rows + 1, 1)
        min_y = max(default_low_y, int(screen.height * self.band_low_frac))
        max_y = min(screen.height - self.height - 2, int(screen.height * self.band_high_frac) - 1)
        if max_y < min_y:
            min_y = max(1, default_low_y)
            max_y = max(min_y, screen.height - self.height - 2)

        # Ensure bounds are valid to prevent infinite loops or crashes
        if max_y < min_y or screen.height < self.height + 4:
            # Fallback for very small screens: place fish in middle
            self.y = max(1, min(screen.height - self.height - 1, screen.height // 2))
        else:
            self.y = random.randint(min_y, max(min_y, max_y))
        self.x = -self.width if direction > 0 else screen.width
        # Reset turning animation state on respawn, but keep cooldown timer so turns still happen across respawns
        self.turning = False
        self.turn_phase = "idle"
        self.turn_t = 0.0

    def draw(self, screen: Screen):
        lines = self.frames
        mask = self.colour_mask
        x_off = 0
        # During turning, render a sliced/narrowed view to simulate columns disappearing/appearing
        if self.turning:
            w = self.width
            # Compute current visible width based on phase
            if self.turn_phase == "shrink":
                frac = max(0.0, 1.0 - (self.turn_t / max(0.001, self.turn_shrink_seconds)))
                vis = max(1, int(round(w * frac)))
                if vis % 2 == 0 and vis > 1:
                    vis -= 1
            elif self.turn_phase == "expand":
                frac = min(1.0, (self.turn_t / max(0.001, self.turn_expand_seconds)))
                vis = max(1, int(round(w * frac)))
                if vis % 2 == 0 and vis > 1:
                    vis -= 1
            else:
                vis = 1
            # Centered slice: remove inside columns one from each side means converge to center
            left = (w - vis) // 2
            right = left + vis
            def slice_cols(rows: List[str], l: int, r: int) -> List[str]:
                out: List[str] = []
                for row in rows:
                    seg = row[l:r] if 0 <= l < len(row) else row
                    # Ensure at least 1 char width; pad if empty
                    if seg == "":
                        seg = " "
                    out.append(seg)
                return out
            lines = slice_cols(lines, left, right)
            if mask is not None:
                mask = slice_cols(mask, left, right)
            # Shift draw position so the center stays stable during shrink/expand
            x_off = left
        if mask is not None:
            draw_sprite_masked(screen, lines, mask, int(self.x) + x_off, int(self.y), self.colour)
        else:
            draw_sprite(screen, lines, int(self.x) + x_off, int(self.y), self.colour)

    # Hook API used by FishHook special
    def attach_to_hook(self, hook_x: int, hook_y: int):
        self.hooked = True
        self.hook_dx = int(self.x) - hook_x
        self.hook_dy = int(self.y) - hook_y
        self.vx = 0.0

    def follow_hook(self, hook_x: int, hook_y: int):
        if self.hooked:
            self.x = hook_x + self.hook_dx
            self.y = hook_y + self.hook_dy

    # Turning control
    def start_turn(self):
        if self.turning or self.hooked:
            return
        self.turning = True
        self.turn_phase = "shrink"
        self.turn_t = 0.0
        self.base_speed = self.vx

    def finish_shrink_and_flip(self):
        # At the narrowest point: flip direction and frames, stop, then expand and ramp speed
        direction = -1 if self.vx > 0 else 1
        # Swap to opposite direction frames but choose the same size index if possible
        from .fish_assets import FISH_RIGHT, FISH_LEFT, FISH_RIGHT_MASKS, FISH_LEFT_MASKS
        src = FISH_RIGHT if direction > 0 else FISH_LEFT
        src_masks = FISH_RIGHT_MASKS if direction > 0 else FISH_LEFT_MASKS
        # Try to match width to current lines
        curr_w = self.width
        candidate = list(zip(src, src_masks))
        frames, mask = min(candidate, key=lambda fm: abs(max(len(r) for r in fm[0]) - curr_w))
        self.frames = frames
        self.colour_mask = randomize_colour_mask(mask) if self.colour_mask is not None else None
        # Reverse velocity sign, magnitude picked from base_speed magnitude
        speed_mag = abs(self.base_speed) if self.base_speed != 0 else random.uniform(self.speed_min, self.speed_max)
        self.vx = speed_mag * direction
        # Continue to expand phase
        self.turn_phase = "expand"
        self.turn_t = 0.0
