# Pygame Animation Player

A simple and animation player for pygame sprites that supports:

- Multiple animation types (sprite sheets and individual frames)
- One-shot and looping animations  
- Frame-rate independent timing
- Easy integration with pygame sprites

## Installation

```bash
pip install pygame-animation-player
```


### Implementation

```python
import pygame
from pygame_animation_player import Animation, AnimationPlayer

# Create animations
idle_anim = Animation(fps=0, frame1)
walk_anim = Animation(fps=12, *walk_frames)
attack_anim = Animation(fps=20, attack_spritesheet, tilesize=(16,16), one_shot=True)
# Add to your sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.image before AnimationPlayer.__init__()
        self.image = None
        self.animation_player = AnimationPlayer(
            self, 
            idle=idle_anim,
            walk=walk_anim,
            attack=attack_anim
        )
    
    def update(self, dt):
        self.animation_player.update(dt)

        if walking:
            self.animation_player.play("walk")
        else:
            self.animation_player.play("idle")

        if attack:
            self.animation_player.play("attack", 
                                        restart= True, 
                                        force_finish= True)
```