import pygame
from typing import Any, Iterable, List, Literal, Union, Sequence, overload, TypedDict, Self, Callable, TypeVar
from os import listdir

from .exceptions import *
from .easing import EASING_FUNCTIONS
pygame.init()


FONTS = {
    'basic': pygame.Font(None, 500)
}


RGBValue = Sequence[int]
ColorValue = Union[int, str, Sequence[int]] # copied from pygame
Coordinate = Sequence[float] # copied from pygame




class Animation:
    """
    Frame by frame animations.

    ### Parameters
    - `file` -> the image where the full animation is stored
    - `files` -> list of paths to files containing frames, in order
    - `_dir` -> directory of all frame images
    - `speed` -> speed of the animation relative to the framerate of the game. higher value = slower animation.
    - `flip` (x,y) -> flip the frames around an axis

    ### Optional Keywords
    - `convert_alpha`: bool -> Use .convert_alpha on frames instead of normal .convert
    - `offsets`: list[Coordinate] -> The offset to the positioning of each frame
    - `offset`: Coordinate -> Default offset for all frames.
    - `end_func`: function -> a function to call when the animation is completed.
    - `end_funcs`: list[function] -> a list of functions to be called on completion.
    - `functions`: dict[int, function] -> functions to be called when the animation reaches a specific frame.
    - `listdir_key`: function -> sorting key function for directory listing. (same as in `min` or `max`)
    """
    @overload
    def __init__(self, files: list[str], speed: int = 1, flip=(False,False), **kwds): ...
    @overload
    def __init__(self, _dir: str, speed: int = 1, flip=(False,False), **kwds): ...
    @overload
    def __init__(self, file: str, size: Coordinate = (32,32), start: Coordinate = (0,0), end: int | None = None, step: Literal['horizontal', 'vertical'] = 'horizontal', speed: int = 1, flip=(False,False), **kwds): ...

    def __init__(self,
                 file: str | None = None,
                 size: Coordinate = (32,32),
                 start: Coordinate = (0,0),
                 end: int | None = None,
                 step: Literal['horizontal', 'vertical'] = 'horizontal',
                 files: list[str] | None = None,
                 _dir: str | None = None,
                 speed: int = 1,
                 flip=(False,False),
                 **kwds):
        
        self.frames = []
        self.frame_index = 0
        self.speed = speed
        self.frame_since_last = 0
        self.loop_frames: Coordinate = (0,-1)

        self.functions: dict[int,function] = kwds.get('functions',{})
        self.end_funcs: list[function] = kwds.get('end_funcs',[])
        if kwds.get('end_func'): self.end_funcs.append(kwds.get('end_func'))


        self.offset = kwds.get('offset',(0,0))
        _offsets = kwds.get('offsets',[])
        self.offsets: list[Coordinate] = _offsets

        if file:
            full_img = pygame.image.load(file).convert_alpha()

            if end is None:
                end = full_img.get_width() if step == 'horizontal' else full_img.get_height()

            _range_step = size[0]  if step == 'horizontal' else size[1]

            for f in range(0,end,_range_step):
                if step == 'horizontal':
                    _s = full_img.subsurface((f,start[1],*size))
                else:
                    _s = full_img.subsurface((start[0],f,*size))
                    
                self.frames.append(pygame.transform.flip(_s,*flip))


        elif files:
            for file in files:
                if kwds.get('convert_alpha',False):
                    _s = pygame.image.load(file).convert_alpha()
                else:
                    _s = pygame.image.load(file).convert()

                self.frames.append(pygame.transform.flip(_s,*flip))


        elif _dir:
            _ld = listdir(_dir)
            _ld.sort(key= kwds.get('listdir_key'))
            for file in _ld:
                if kwds.get('convert_alpha',False):
                    _s = pygame.image.load(_dir+'/'+file).convert_alpha()
                else:
                    _s = pygame.image.load(_dir+'/'+file).convert()

                self.frames.append(pygame.transform.flip(_s,*flip))


        if not _offsets:
            self.offsets = [(0,0) for _ in range(len(self.frames))]



    @property
    def frame(self):
        return self.frames[self.frame_index]



    def tick(self, step=1):
        if self.frame_since_last < self.speed:
            self.frame_since_last += 1      
            return
        
        self.frame_since_last = 0
        self.frame_index += step

        if self.loop_frames[1] != -1 and self.frame_index > self.loop_frames[1]:
            self.frame_index = self.loop_frames[0]
            
        elif self.frame_index >= len(self.frames)-1:
            if self.end_funcs:
                for func in self.end_funcs:
                    func()
            else:
                self.frame_index = 0

        func = self.functions.get(self.frame)
        if func:
            func()


    
    def scale_by(self, factor: Coordinate):
        self.offset = (self.offset[0]*factor[0], self.offset[1]*factor[1])
        for i in range(len(self.frames)):
            self.frames[i] = pygame.transform.scale_by(self.frames[i],factor)
            self.offsets[i] = (self.offsets[i][0]*factor[0], self.offsets[i][1]*factor[1])

    

    def reset(self):
        self.frame_index = 0
        self.frame_since_last = 0


    
    @overload
    def blit_params(self, rect: pygame.FRect) -> tuple[pygame.Surface, Coordinate]: ...
    @overload
    def blit_params(self, pos: Coordinate) -> tuple[pygame.Surface, Coordinate]: ...

    def blit_params(self, rect: pygame.FRect | None = None, pos: Coordinate | None = None) -> tuple[pygame.Surface, Coordinate]:
        """
        Returns the current frame with the position (with offset) of the animation, relative to the given position or Rect.

        As the name suggests, you can directly put this into `Surface.blit`
        """
        if rect:
            return self.frame, (rect.left + self.offsets[self.frame_index][0] + self.offset[0],
                                             rect.top + self.offsets[self.frame_index][1] + self.offset[1])
        else:
            return self.frame, (pos[0] + self.offsets[self.frame_index][0] + self.offset[0],
                                             pos[1] + self.offsets[self.frame_index][1] + self.offset[1])





class Style(TypedDict):
    """
    Some sprites may not support all Style keys.
    
    ### Keys
    - `image`: *Surface | str (filepath)* -> Image to be displayed on the sprite.
    - `img_alpha`: *bool* -> If True, the `image` will be converted with `.convert_alpha`, else with `.convert` (only used if `image` is `str`).
    - `img_scale`: *Coordinate | Literal['auto']* -> Scale of the `image`. ('auto' means it will match the size of the sprite)

    - `anim`: *Animation* -> An animation to use instead of an image. Can only be used in `AnimatedSprite` and its subclasses.

    - `bg`: *ColorValue* -> Background color of the sprite.

    - `border`: *ColorValue* -> Border color of the sprite.
    - `border_width`: *int* -> Width of the `border`.
    - `border_radius`: *int | tuple* -> Radius of the rounded corners of the sprite.
        If a tuple with 4 numbers is given, each corner will be rounded accordingly. 
        If the tuple doesn't have 4 numbers, the remaining spaces will be filled with `-1`'s.

    - `text`: *str* -> A text to be displayed on the sprite.
    - `font`: *Font* -> Font of the `text`. (Only used if `text` is set)
    - `text_antialias`: *bool* -> Antialias parameter in `Font.render`. (Default: True)
    - `text_color`: *ColorValue* -> Color of the text.
    - `text_pos`: *Coordinate* -> Position of the text. if not set, automatic centering is used. (Only used if `text` is set)

    - `rect`: *Sequence[int | Literal['auto']]* -> Rectangle of the sprite. If an element is 'auto', the current rectangle will be used for that element.
    - `check_rect_auto`: *bool* -> Whether to check if the rect value contains any 'auto's.

    
    ### Special Keys 

    These are only used in a few types of sprites. If they can be used, it is mentioned in the docstring.

    - `fg`: *ColorValue* -> Foreground color / main color of the sprite.
    - `fg_radius`: *int | tuple* -> Same as `border_radius`, but for the foreground.
    - `fg_rect`: *Rect* -> Rectangle where the foreground is placed. Mostly handled automatically.
    """

    bg: ColorValue

    fg: ColorValue
    fg_radius: int | tuple[int,int,int,int]
    fg_rect: pygame.FRect

    border: ColorValue
    border_width: int
    border_radius: int | tuple[int,int,int,int]

    image: pygame.Surface | str
    img_alpha: bool
    img_scale: Coordinate | Literal['auto']

    text: str
    font: pygame.Font
    text_antialias: bool
    text_color: ColorValue
    text_pos: Coordinate

    anim: Animation

    rect: Sequence[int | Literal['auto']] | pygame.FRect
    check_rect_auto: bool


State = Style # if someone likes this word more
CombinedStyle = dict[str, dict[str, str | Style]] # used for CombinedStatedSprites

    



EventName = Literal['onhover','onclick','onleftclick','onmiddleclick','onrightclick','onrelease','onleftrelease','onmiddlerelease','onrightrelease']
EasingName = Literal[
    "linear",
    "cubic_in",
    "cubic_out",
    "cubic_in_out",
    "quadric_in",
    "quadric_out",
    "quadric_in_out",
    "cubic_in",
    "cubic_out",
    "cubic_in_out",
    "sine_in",
    "sine_out",
    "sine_in_out",
    "exponential_in",
    "exponential_out",
    "exponential_in_out",
    "circular_in",
    "circular_out",
    "circular_in_out",
    "quartic_in",
    "quartic_out",
    "quartic_in_out",
    "quintic_in",
    "quintic_out",
    "quintic_in_out",
]





DEFAULT_EVENT_CHECKS = {
    'onhover': lambda sprite,_: sprite.rect.collidepoint(pygame.mouse.get_pos()),
    'onclick': lambda sprite,event: event.type == pygame.MOUSEBUTTONDOWN and sprite.rect.collidepoint(pygame.mouse.get_pos()),
    'onleftclick': lambda sprite,event: event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and sprite.rect.collidepoint(pygame.mouse.get_pos()),
    'onmiddleclick': lambda sprite,event: event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1] and sprite.rect.collidepoint(pygame.mouse.get_pos()),
    'onrightclick': lambda sprite,event: event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2] and sprite.rect.collidepoint(pygame.mouse.get_pos()),
    'onrelease': lambda _,event: event.type == pygame.MOUSEBUTTONUP,
    'onleftrelease': lambda _,event: event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0],
    'onmiddlerelease': lambda _,event: event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[1],
    'onrightrelease': lambda _,event: event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[2],
}








class Transition:
    """
    Transition between a sprite's states.

    ### Parameters
    - `time:` (seconds or frames) The duration of the transition. Treated as game frames if the `delta_time` parameter is not used in `Transition.tick`.
    - `style1:` The style from which the transition starts.
    - `style2:` The style to transition into.
    - `*style_keys:` A list of style keys you want to transition.
    - `_all:` Ignore `style_keys` and transition everything.
    - `easing:` The easing function to use. See `sprites.EASING_FUNCTIONS`
    """
    def __init__(self, time: float, style1: Style, style2: Style, *style_keys, _all=False, easing: EasingName | Callable = 'linear') -> None:
        self.finished = False
        self.time = time
        self.current_time = 0

        if type(easing) is str:
            self.easing_func = EASING_FUNCTIONS.get(easing)
            if self.easing_func is None:
                raise KeyError(f"Invalid easing function name: '{easing}'")
            
        elif type(easing) is Callable:
            self.easing_func = easing
        else:
            raise TypeError("The easing must be either 'str' or 'Callable'")



        self.style_keys = set(*style_keys)
        if _all:
            self.style_keys = set(style1.keys()).union(set(style2.keys()))
        elif not style_keys:
            self.style_keys = set(style2.keys())



        self.style1 = style1.copy()
        self.style2 = style2.copy()



        _to_remove = set()
        # Make all values the same type
        for key in self.style_keys:
            s1_val = self.style1.get(key)
            s2_val = self.style2.get(key)

            # Remove not used keys from self.style_keys
            if s2_val is None:
                _to_remove.add(key)
                continue
            
            # All colors must be in RGBA format
            if key in ('bg','fg','border','text_color'):
                if type(s1_val) in (str,int):
                    raise IncorrectColorError(f"'{s1_val}' can not be accepted in a Transition. The color value must be a sequence of integers (RGB or RGBA).")
                if type(s2_val) in (str,int):
                    raise IncorrectColorError(f"'{s2_val}' can not be accepted in a Transition. The color value must be a sequence of integers (RGB or RGBA).")
            
                self.style1[key] = list(to_rgba(s1_val))
                self.style2[key] = list(to_rgba(s2_val))


            elif key in ('border_radius','fg_radius'):
                self.style1[key] = list(radius_kwds(s1_val, True))
                self.style2[key] = list(radius_kwds(s2_val, True))



        self.style_keys = self.style_keys.difference(_to_remove)


        self.style: Style = self.style1.copy()




    
    def tick(self, delta_time: float = 1) -> Style:
        """Calculate next frame of the transition."""
        self.current_time += delta_time
        progress = self.easing_func(self.current_time / self.time)


        for key in self.style_keys:
            s1_val = self.style1[key]
            s2_val = self.style2[key]
            
            
            if key in ('bg','fg','border','text_color','border_radius','fg_radius','rect'):
                for i in range(4):
                    diff = s2_val[i] - s1_val[i]
                    if key in ('bg','fg','border','text_color'):
                        # must be a valid color value
                        self.style[key][i] = min(max(round(s1_val[i] + diff * progress), 0), 255)
                    else:
                        self.style[key][i] = round(s1_val[i] + diff * progress)
                    

        if self.current_time >= self.time:
            self.finished = True

        return self.style






def auto_sized_text(text: str, font: pygame.Font, font_params, border_rect: pygame.FRect):
    if type(font_params) is tuple:
        textSurface = font.render(text, *font_params).convert_alpha()
    elif type(font_params) is dict:
        textSurface = font.render(text, **font_params).convert_alpha()

    
    if border_rect.h > border_rect.w or textSurface.get_height() > textSurface.get_width():
        textSurface = pygame.transform.smoothscale(
            textSurface, (int(border_rect.h / textSurface.get_height() * textSurface.get_width()), border_rect.h))
    else:
        textSurface = pygame.transform.smoothscale(
            textSurface, (border_rect.w, int(border_rect.w / textSurface.get_width() * textSurface.get_height())))


    return textSurface, textSurface.get_rect()






def get_value(d: dict, *keys, default=None):
    """
    Goes through the list of keys and if it finds a value, returns it
    """
    for key in keys:
        val = d.get(key)
        if val:
            return val
    
    return default




def radius_kwds(val: int | tuple[int, int, int, int], only_tuple = False):
    if val is None:
        return {}
    if type(val) is dict:
        return val
    
    
    if type(val) is int:
        val = (val,val,val,val)

    if only_tuple:
        return val
    
     
    if len(val) < 4:
        val = [*val]
        val.extend([-1 for _ in range(4-len(val))])

    return {'border_top_left_radius': val[0], 'border_top_right_radius': val[1],
                'border_bottom_left_radius': val[2], 'border_bottom_right_radius': val[3]}
            



def to_rgba(color: ColorValue | None) -> tuple[int,int,int,int]:
    """
    Formats a color value to RGBA.

    Currently only works with Sequences
    """
    if color is None:
        return (0,0,0,0)

    if type(color) not in (str, int):
        if len(color) < 4:
            color = [*color]
            color.extend([255 for _ in range(4-len(color))])
    
    return tuple(color)


def check_rect_auto(rect, rect2 = None, check: bool = True) -> list[int, int, int, int]:
    if isinstance(rect, pygame.FRect):
        return [*rect]
    
    # FIXME: this does not run at all
    else:
        rect = [*rect]
        if check and rect2 is not None:
            for i in range(4):
                if rect[i] == 'auto':
                    rect[i] = rect2[i]
        
        return rect
    

    