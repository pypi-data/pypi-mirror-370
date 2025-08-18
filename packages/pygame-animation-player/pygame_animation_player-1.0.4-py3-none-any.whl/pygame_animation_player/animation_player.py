import pygame
from .animation import Animation
from typing import Dict, Optional, List

class AnimationPlayer:
    """AnimationPlayer needs to be an Atrribute of an pygame.sprite.Sprite (or have a self.image attr) Object. 
    call update in sprite.update to update sprite.image
    example usage: 
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            # self.image must be declared before AnimationPlayer.__init__()
            self.image = None
            self.animation_player = AnimationPlayer(self, 
                                    run= Animation(10, pygame.image.load('assets/player/run.png').convert_alpha(), tilesize=(8, 16))
                                    idle= Animation(0, pygame.image.load('assets/player/idle.png').convert_alpha()))
                                    attack= Animation(15, pygame.image.load('assets/player/attack_01.png').convert_alpha(),
                                                        pygame.image.load('assets/player/attack_02.png').convert_alpha(), ........ ,
                                                        one_shot = True)
        def update(dt):
            self.animation_player.update()
            if smt:
                self.animation_player.play('attack', restart= True, force_finish= True)"""


    def __init__(self, parent:pygame.sprite.Sprite, **animations:Animation) -> None:
        if not animations:
            raise ValueError("AnimationPlayer needs at least one animation!")

        self.parent = parent
        self.animations: Dict[str, Animation] = animations

        self.current_animation_name: Optional[str] = None
        self.current_animation: Optional[Animation] = None
        self.current_frame_index: int = 0
        self.frame_timer: float = 0.0
        self.is_playing: bool = False
        self.animation_finished: bool = False

        # set first animation
        first_animation = next(iter(self.animations))
        self.play(first_animation)


    def add_animation(self, name: str, new_animation: Animation) -> None:
        """add a new animation as a Animation object"""
        self.animations[name] = new_animation

    def play(self, animation_name: str, restart: bool = False, force_finish: bool = False) -> None:
        """start new animation. 

            args:
                animation_name: str = name of the animation
                restart: bool = if the player should restart the animation
                force_finish: bool = if restart == True. If the animation needs to be finished to restart"""
        # dont restart animation if already playing same animation exept restart is true
        if self.current_animation_name == animation_name and not restart:
            return
        # force the animation to finish if restart and force finnish are true
        if self.current_animation_name == animation_name and force_finish and not self.animation_finished and restart:
            return

        self.current_animation_name = animation_name
        self.current_animation = self.animations[animation_name]
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.is_playing = True
        self.animation_finished = False

        # update sprite img instantly instead of in update()
        self._update_sprite_img()

    def pause(self) -> None:
        """pause current animation"""
        self.is_playing = False

    def resume(self) -> None:
        """resume paused animation"""
        if self.current_animation:
            self.is_playing = True

    def stop(self) -> None:
        """stop current animation and reset it to first frame"""
        self.is_playing = False
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.animation_finished = False
        self._update_sprite_img()

    def update(self, dt:float) -> None:
        """updates the animation. call in sprite.update"""
        if not self.is_playing or not self.current_animation or self.animation_finished:
            return

        # handle static images (fps = 0)
        if self.current_animation.fps == 0:
            return

        # increment frame timer by dt (time elapsed between frames)
        self.frame_timer += dt

        # checks if it is time to go to the next frame
        if self.frame_timer >= self.current_animation.frame_time:
            self.frame_timer = 0.0
            self.current_frame_index += 1

            # handles looping or completion
            if self.current_frame_index >= self.current_animation.frame_count:
                if self.current_animation.one_shot:
                    # one-shot animation: stop at last frame
                    self.current_frame_index = self.current_animation.frame_count -1
                    self.animation_finished = True
                    self.is_playing = False

                else:
                    # looping animation
                    self.current_frame_index = 0

            self._update_sprite_img()

    def _update_sprite_img(self):
        """updates the parent sprite img"""
        if self.current_animation and hasattr(self.parent, "image"):
            self.parent.image = self.current_animation.get_frame_img(self.current_frame_index)

    def get_animation_name(self) -> Optional[str]:
        """returns current animation"""
        return self.current_animation_name

    def is_animation_finished(self) -> bool:
        """returns true if the animation has finished"""
        return self.animation_finished

    def get_all_animations(self) -> List[str]:
        """returns list of all available animations"""
        return list(self.animations.keys())