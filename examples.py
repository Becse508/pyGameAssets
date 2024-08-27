import pygame
import assets
from random import randint

# EVENTS

mysprite = assets.Sprite(rect = '')


# Default Event
@mysprite.event()
def onhover(isHovered: bool): # the parameters are always these
    if isHovered:
        mysprite.image.fill((255,0,0))
    else:
        mysprite.image.fill((255,255,255))



# Custom Event

# checks if the mouse is sitting on top of the sprite and SPACE is pressed (runs once per press).
mycheck = lambda sprite,event: sprite.rect.colliderect(pygame.mouse.get_pos()) and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE

@mysprite.event(check = mycheck, name = 'space_pressed') # name is optional
def pressing_space(pressing_it: bool): # the parameters are always these
    if pressing_it:
        # do some stuff
        mysprite.image.fill((randint(0,255),randint(0,255),randint(0,255)))