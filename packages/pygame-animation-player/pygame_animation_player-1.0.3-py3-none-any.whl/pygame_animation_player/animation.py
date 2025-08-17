import pygame
from typing import Dict, Optional, Tuple, List

class Animation:
    def __init__(self, fps:int, *sprites: pygame.Surface, tilesize: Optional[Tuple[int, int]] = None, one_shot:bool = False) -> None:
        """animation for AnimationPlayer. Sprites can be single spritesheet or seperate imgs. No mixing! Set fps to 0 for static img."""
        # argument validation:
        if not sprites:
            raise ValueError("Animation needs at least one frame!!!")
        if fps < 0:
            raise ValueError("fps needs to be positive!!!")

        self.fps = fps
        self.one_shot = one_shot

        # calculates frame time. if fps == 0 (static image) set frame time to infinity
        self.frame_time = 1 / self.fps if self.fps > 0 else float("inf")


        if len(sprites) > 1:
            # sprites is seperate imgs
            if tilesize is None:
                self.sprites = list(sprites)

            else:
                raise ValueError("tilesize only needed if inserting Spritesheet!!!")
        else:
            if tilesize is not None:
                # sprites is Spritesheet
                self.sprites = self._extract_sprites_from_spritesheet(sprites[0], tilesize)
            elif tilesize is None:
                # single frame animation
                self.sprites = list(sprites)


        self.frame_count: int = len(self.sprites)



    def _extract_sprites_from_spritesheet(self, spritesheet:pygame.Surface, tilesize:tuple) -> list:
        """does what the name implies. If the tilesize does not match the spritesheet it will throw TypeError"""
        sprites = []
        # sizing:
        size_x, size_y = tilesize
        spritesheet_size_x, spritesheet_size_y = spritesheet.get_size()
        
        # throws error if tilesize doesnt evenly divide spritesheet
        if spritesheet_size_x % size_x != 0 or spritesheet_size_y % size_y != 0:
            raise ValueError(f"tilesize[{tilesize}] does not match Spritesheet")

        # determines the spritesheet rows and collums
        collums = spritesheet_size_x // size_x
        rows = spritesheet_size_y // size_y

        for y in range(rows):
            for x in range(collums):
                # creates the sprite surface with transparancy enabled
                surf = pygame.Surface((tilesize), pygame.SRCALPHA)
                # draws the desired part of the spritesheet onto sprite surface
                surf.blit(spritesheet , (0,0), area=(x*tilesize[0],y*tilesize[1],tilesize[0],tilesize[1]))
                # adds the sprite surface to the list
                sprites.append(surf)

        return sprites

    def get_frame_img(self, index:int) -> pygame.Surface:
        if index < 0:
            raise ValueError("index < 0 is not permitted")
        if index >= self.frame_count:
            raise ValueError(f"index {index} > length of animation {self.frame_count}")
        return self.sprites[index]