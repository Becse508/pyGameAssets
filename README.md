# PyGame Assets

A pygame addon library which hopes to make coding in pygame more efficient by introducing a hierarchy of asset classes with different functionalities.
This library is still in an early stage of development.



## What does it include

### Animations
A basic frame-by-frame animation class with:
- offsets for each frame
- functions to call when the animation reaches a specific frame
- speed control
- 3 different ways to import animations



### Sprites
A hierarchy of sprite classes:


- #### Sprite
    Base class for all sprites. Includes:
    - Predefined and custom `Events` useable with a simple decorator


- #### SpriteGroup
    No functionality yet.


- #### StatedSprite
    A sprite with different states. Includes:
    - States can be edited, added or removed at any time.
    - A state acts as a 'blueprint' for the sprite. When you select a new state, the sprite gets 'constructed' from the given style with a method.
    - **Transitioning:** A basic transition system to smoothly transition between states.


- #### Style
    An easy to use style dictionary. Currently available:
    - `image:` image to be displayed on the sprite
    - `img_alpha:` if True, the `image` will be converted with `.convert_alpha`, else with `.convert` (only used if `image` is `str`)
    - `img_scale:` scale of the `image`. ('auto' means it will match the size of the sprite)

    - `anim:` An animation to use instead of an image. Can only be used in `AnimatedSprite` and its subclasses.

    - `bg:`  background color of the sprite

    - `border:` border color of the sprite
    - `border_width:` width of the `border`
    - `border_radius:` radius of the rounded corners of the sprite .
        if a tuple with 4 numbers is given, each corner will be rounded accordingly. 
        if the tuple doesn't have 4 numbers, the remaining spaces will be filled with `-1`'s.

    - `text:`  a text to be displayed on the sprite
    - `font:` font of the `text`. (Only used if `text` is set)
    - `text_antialias:` antialias parameter in `Font.render`. (Default: True)
    - `text_color:` color of the text
    - `text_pos:` position of the text. if not set, automatic centering is used. (Only used if `text` is set)


    **These are only used in a few types of sprites. If they can be used, it is mentioned in the docstring.**

    - `fg:` foreground color / main color of the sprite.
    - `fg_radius`: same as `border_radius`, but for the foreground.
    - `fg_rect:` rectangle where the foreground is placed. Mostly handled automatically.


### Transition
Smooth transitions between two states of a `sprite` or a `CombinedSprite`.
- DOES NOT WORK WITH `CombinedSprite`s YET.
- 25 predifined easing functions
- works with custom ones as well


### CombinedSprite
Sprites that are made up of multiple other sprites. (e.g. sliders)


### CombinedStatedSprite
Sprites that are made up of multiple stated sprites. You can can create general states which include multiple sprites.
- Not fully implemented yet



## UI elements
Currently only a few basic ones are available.

- **Button**
- **ProgressBar**
- **Switch** - NOT WORKING YET
- **Slider**




This is only a superficial presentation of the library, I will improve it later.