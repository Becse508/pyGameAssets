import pygame
import assets
from random import randint

# EVENTS

myasset = assets.Sprite(rect = '')


# Default Event
@myasset.event()
def onhover(asset: assets.Sprite, isHovered: bool): # the parameters are always these
    if isHovered:
        asset.image.fill((255,0,0))
    else:
        asset.image.fill((255,255,255))



# Custom Event

# checks if the mouse is sitting on top of the asset and SPACE is pressed (runs once per press).
mycheck = lambda asset,event: asset.rect.colliderect(pygame.mouse.get_pos()) and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE

@myasset.event(check = mycheck, name = 'space_pressed') # name is optional
def pressing_space(asset: assets.Sprite, pressing_it: bool): # the parameters are always these
    if pressing_it:
        # do some stuff
        myasset.image.fill((randint(0,255),randint(0,255),randint(0,255)))