import pygame
from typing import Any, List, Literal, Union, Sequence, overload, TypedDict, Self, Callable, TypeVar
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
    def __init__(self, file: str, size: Coordinate = (32,32), start: Coordinate = (0,0), end: int = None, step: Literal['horizontal', 'vertical'] = 'horizontal', speed: int = 1, flip=(False,False), **kwds): ...

    def __init__(self, file: str = None, size: Coordinate = (32,32), start: Coordinate = (0,0), end: int = None, step: Literal['horizontal', 'vertical'] = 'horizontal', files: list[str] = None, _dir: str = None, speed: int = 1, flip=(False,False), **kwds):
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
    def blit_params(self, rect: pygame.Rect) -> tuple[pygame.Surface, Coordinate]: ...
    @overload
    def blit_params(self, pos: Coordinate) -> tuple[pygame.Surface, Coordinate]: ...

    def blit_params(self, rect: pygame.Rect = None, pos: Coordinate = None) -> tuple[pygame.Surface, Coordinate]:
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
    Some assets may not support all Style keys.
    
    ### Keys
    - `image:` image to be displayed on the asset
    - `img_alpha:` if True, the `image` will be converted with `.convert_alpha`, else with `.convert` (only used if `image` is `str`)
    - `img_scale:` scale of the `image`. ('auto' means it will match the size of the asset)

    - `anim:` An animation to use instead of an image. Can only be used in `AnimatedAsset` and its subclasses.

    - `bg:`  background color of the asset

    - `border:` border color of the asset
    - `border_width:` width of the `border`
    - `border_radius:` radius of the rounded corners of the asset .
        if a tuple with 4 numbers is given, each corner will be rounded accordingly. 
        if the tuple doesn't have 4 numbers, the remaining spaces will be filled with `-1`'s.

    - `text:`  a text to be displayed on the asset
    - `font:` font of the `text`. (Only used if `text` is set)
    - `text_antialias:` antialias parameter in `Font.render`. (Default: True)
    - `text_color:` color of the text
    - `text_pos:` position of the text. if not set, automatic centering is used. (Only used if `text` is set)

    
    ### Special Keys 

    These are only used in a few types of assets. If they can be used, it is mentioned in the docstring.

    - `fg:` foreground color / main color of the asset.
    - `fg_radius`: same as `border_radius`, but for the foreground.
    - `fg_rect:` rectangle where the foreground is placed. Mostly handled automatically.
    """

    bg: ColorValue

    fg: ColorValue
    fg_radius: int | tuple[int,int,int,int]
    fg_rect: pygame.Rect

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



State = Style # if someone likes this word more
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
    'onhover': lambda asset,_: asset.rect.collidepoint(pygame.mouse.get_pos()),
    'onclick': lambda asset,event: event.type == pygame.MOUSEBUTTONDOWN and asset.rect.collidepoint(pygame.mouse.get_pos()),
    'onleftclick': lambda asset,event: event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and asset.rect.collidepoint(pygame.mouse.get_pos()),
    'onmiddleclick': lambda asset,event: event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1] and asset.rect.collidepoint(pygame.mouse.get_pos()),
    'onrightclick': lambda asset,event: event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2] and asset.rect.collidepoint(pygame.mouse.get_pos()),
    'onrelease': lambda asset,event: event.type == pygame.MOUSEBUTTONUP,
    'onleftrelease': lambda asset,event: event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0],
    'onmiddlerelease': lambda asset,event: event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[1],
    'onrightrelease': lambda asset,event: event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[2],
}






class Asset(pygame.sprite.Sprite):
    """
    Base class for all assets.

    ### Parameters:
    - `image` -> default surface of the asset
    - `rect` -> rectangle of the asset
    
    > one of these must have a value if you use 'auto'
    """
        
    def __init__(self, image: pygame.Surface | Literal['auto'] = None, rect: pygame.Rect | Literal['auto'] = None, *groups):
        super().__init__(*groups)
            
        self.image = image
        if rect == 'auto' and image:
            self.rect = image.get_rect()
        else:
            self.rect = rect
        
        if self.rect not in ('auto', None) and image is None:
            self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        
        self.Events = {}


    def update(self, delta_time: float = 1, *args: Any, **kwargs: Any) -> None:
        self.handle_event(pygame.Event(0, {}))


    @property
    def nullrect(self):
        """A copy of the asset's rect at position (0,0)"""
        return pygame.Rect(0,0,self.rect.w,self.rect.h)



    def event(self, check: Callable | EventName = None, name: str = None):
        """
        An event of the asset. ALWAYS USE WITH BRACKETS

        Calls the function with True or False as the second argument, depending on whether the "check" condition is fulfilled or not.

        
        ### Default events
        - onhover
        - onclick
        - onleftclick
        - onmiddleclick
        - onrightclick
        - onrelease
        - onleftrelease
        - onmiddlerelease
        - onrightrelease


        ### Parameters (optional)
        - `name`: str -> Name of the event. If not given, the function name is used. Only affects its key in the `Asset.Events` dictionary.
        - `check`: Callable | EventName -> Condition of the event.
            1. You can use a Callable which returns a boolean
            2. Or one of the default event names. This will use thet event's check but register this as a new event with the given name.
                (useful for having multiple events of the same type, e.g. keeping a default event while adding a new one too.)
            
        
        
        ### Examples
            Open `examples.py` in the base directory of the library.
        """
        def decorator(func):
            nonlocal name
            if name is None:
                name = func.__name__

            nonlocal check
            if check is None:
                check = DEFAULT_EVENT_CHECKS.get(name, lambda _,__: True)
            elif type(check) is str:
                check = DEFAULT_EVENT_CHECKS.get(check, lambda _,__: True)



            def wrapper(asset, event, *args, **kwargs):
                return func(asset, check(asset,event), *args, **kwargs)


            self.Events[name] = wrapper
                                

            return wrapper
        return decorator

    # FIXME: if there are no pygame events, some Assets freeze because their events are not called.
    def handle_event(self, event: pygame.Event):
        """Call this when looping through events."""
        for assetEvent in self.Events.values():
            assetEvent(self, event)

    
    def draw(self, surf: pygame.Surface) -> None:
        """Draws the asset on the surface."""
        surf.blit(self.image, self.rect)





class AssetGroup(pygame.sprite.Group):
    """
    Group of Assets.
    """
    def __init__(self, *elements, **kwds):
        super().__init__(elements)



    def handle_event(self, event: pygame.Event):
        """Call this when looping through events."""
        for asset in self.sprites():
            asset.handle_event(event)


    def sprites(self) -> List[Asset]:
        return super().sprites()




class Transition:
    """
    Transition between an asset's states.

    ### Parameters
    - `time:` (seconds or frames) The duration of the transition. Treated as game frames if the `delta_time` parameter is not used in `Transition.tick`.
    - `style1:` The style from which the transition starts.
    - `style2:` The style to transition into.
    - `*style_keys:` A list of style keys you want to transition.
    - `_all:` Ignore `style_keys` and transition everything.
    - `easing:` The easing function to use. See `assets.EASING_FUNCTIONS`
    """
    def __init__(self, time: float, style1: Style, style2: Style, *style_keys, _all=False, easing: EasingName | Callable = 'linear') -> None:
        self.finished = False
        self.time = time
        self.current_time = 0

        if type(easing) is str:
            self.easing_func = EASING_FUNCTIONS.get(easing)
            if self.easing_func is None:
                raise KeyError(f"Invalid easing function: '{easing}'")
        elif type(easing) is Callable:
            self.easing_func = easing
        else:
            raise TypeError("The easing must be either 'str' or 'Callable'")



        self.style_keys = set(*style_keys)
        if _all:
            self.style_keys = set(style1.keys()).union(set(style2.keys()))


        self.style1 = style1.copy()
        self.style2 = style2.copy()


        _to_remove = set()
        # Make all values the same type
        for key in self.style_keys:
            s1_val = self.style1.get(key)
            s2_val = self.style2.get(key)

            # Remove not used keys from self.style_keys
            if s1_val is None and s2_val is None:
                _to_remove.add(key)
                continue
            
            # All colors must be in RGBA format
            if key in ('bg','fg','border','text_color'):
                if type(s1_val) in (str,int):
                    raise IncorrectColorError(f"'{s1_val}' can not be accepted in a Transition. The color value must be a sequence of integers (RGB / RGBA).")
                if type(s2_val) in (str,int):
                    raise IncorrectColorError(f"'{s2_val}' can not be accepted in a Transition. The color value must be a sequence of integers (RGB / RGBA).")
            
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
            
            
            if key in ('bg','fg','border','text_color','border_radius','fg_radius'):
                for i in range(4):
                    diff = s2_val[i] - s1_val[i]
                    if key in ('border_radius', 'fg_radius'):
                        self.style[key][i] = round(s1_val[i] + diff * progress)
                    else:
                        # must be a valid color value
                        self.style[key][i] = min(max(round(s1_val[i] + diff * progress), 0), 255)
                    

        if self.current_time >= self.time:
            self.finished = True


        return self.style


# TODO: make this
class ListedTransition:
    """
    Transition between multiple styles.

    ### Parameters
    - `time:` (seconds or frames) The duration of the transition. Treated as game frames if the `delta_time` parameter is not used in `Transition.tick`.

    - `style1list:` The list of styles from which the transition starts.
    - `style2list:` The list of styles to transition into.

    - `*style_keys:` A list of style keys you want to transition.
    - `_all:` Ignore `style_keys` and transition everything.
    - `easing:` The easing function to use. See `assets.EASING_FUNCTIONS`
    """
    def __init__(self, time: float, style1: Style, style2: Style, *style_keys, _all=False, easing: EasingName | Callable = 'linear') -> None:
        self.finished = False
        self.time = time
        self.current_time = 0

        if type(easing) is str:
            self.easing_func = EASING_FUNCTIONS.get(easing)
            if self.easing_func is None:
                raise KeyError(f"Invalid easing function: '{easing}'")
        elif type(easing) is Callable:
            self.easing_func = easing
        else:
            raise TypeError("The easing must be either 'str' or 'Callable'")



        self.style_keys = set(*style_keys)
        if _all:
            self.style_keys = set(style1.keys()).union(set(style2.keys()))


        self.style1 = style1.copy()
        self.style2 = style2.copy()


        _to_remove = set()
        # Make all values the same type
        for key in self.style_keys:
            s1_val = self.style1.get(key)
            s2_val = self.style2.get(key)

            # Remove not used keys from self.style_keys
            if s1_val is None and s2_val is None:
                _to_remove.add(key)
                continue
            
            # All colors must be in RGBA format
            if key in ('bg','fg','border','text_color'):
                if type(s1_val) in (str,int):
                    raise IncorrectColorError(f"'{s1_val}' can not be accepted in a Transition. The color value must be a sequence of integers (RGB / RGBA).")
                if type(s2_val) in (str,int):
                    raise IncorrectColorError(f"'{s2_val}' can not be accepted in a Transition. The color value must be a sequence of integers (RGB / RGBA).")
            
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
            
            
            if key in ('bg','fg','border','text_color','border_radius','fg_radius'):
                for i in range(4):
                    diff = s2_val[i] - s1_val[i]
                    if key in ('border_radius', 'fg_radius'):
                        self.style[key][i] = round(s1_val[i] + diff * progress)
                    else:
                        # must be a valid color value
                        self.style[key][i] = min(max(round(s1_val[i] + diff * progress), 0), 255)
                    

        if self.current_time >= self.time:
            self.finished = True


        return self.style






class StatedAsset(Asset):
    """
    ### Keywords
    - `Style` keys for the asset's 'default' state
    """
    def __init__(self, rect: pygame.Rect = None, *groups, **style):
        super().__init__(None, rect, *groups)

        self.states: dict[str, Style] = {
            'default': style
        }
        self.selected_state = 'default'


        self.construct('default')

        self._transition = None
        self.style = self.states['default'].copy()
    


    def change_style(self, state: str | Style | None, change_selected = True):
        if type(state) is str:
            if not self.states.get(state):
                raise KeyError(f'{state} is not a valid state. (not in {self.__class__}.states)')
            
            self.selected_state = state
            if change_selected:
                self.style = self.states[state]

        elif state is None:
            self.style = {}
            if change_selected:
                self.selected_state = None

        else:
            self.style = state
            if change_selected:
                self.selected_state = None


    
    def _construct(self, reset_image=True, **style):
        """Do not use this. This does not change the selected state variable."""
        
        if reset_image:
            self.image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        
        border_width = style.get('border_width', 2)
        border_radius = radius_kwds(style.get('border_radius'))


        # Background
        bg = style.get('bg', (0,0,0,0))
        if bg:
            pygame.draw.rect(self.image, bg, self.nullrect, **border_radius)


        # Foreground
        fg = style.get('fg')
        fg_rect = style.get('fg_rect', pygame.Rect(0,0,0,0))
        fg_radius = radius_kwds(style.get('fg_radius'))

        if fg:
            pygame.draw.rect(self.image, fg, fg_rect,**fg_radius)
        
        # Load image if the path is given
        image = style.get('image')
        if type(image) is str:
            if style.get('img_alpha'):
                image = pygame.image.load(image).convert_alpha()
            else:
                image = pygame.image.load(image).convert()


        # Scale the image
        scale = style.get('img_scale')
        if scale == 'auto':
            image = pygame.transform.scale(image, self.rect.size)

        elif scale:
            image = pygame.transform.scale(image, scale)
        
        # Blit the image
        if image:
            self.image.blit(image,(0,0))
        

        # Handle text
        text = style.get('text')
        if text:
            font: pygame.Font = style.get('font', FONTS['basic'])
            
            # Font.render parameters
            font_params = style.get('text_antialias', True ), style.get('text_color', (255,255,255))

            rect_without_border = pygame.Rect(
                self.rect.left+border_width-10,
                self.rect.top+border_width-10,
                self.rect.w-border_width-10,
                self.rect.h-border_width-10,
            )
            text_surf, text_rect = auto_sized_text(text, font, font_params, rect_without_border)
            
            # Automatic centering
            pos = style.get('text_pos', (self.rect.w/2, self.rect.h/2))
            text_rect.center = pos

            self.image.blit(text_surf, text_rect)
    


        # FIXME: removing stuff outside the border radius
        if border_radius:
            wh = min((self.rect.h//2,self.rect.w//2))
            if border_radius['border_top_left_radius'] > wh:
                border_radius['border_top_left_radius'] = wh
            if border_radius['border_top_right_radius'] > wh:
                border_radius['border_top_right_radius'] = wh
            if border_radius['border_bottom_left_radius'] > wh:
                border_radius['border_bottom_left_radius'] = wh
            if border_radius['border_bottom_right_radius'] > wh:
                border_radius['border_bottom_right_radius'] = wh
            

            # dist = round(sqrt(border_radius['border_top_left_radius']**2*2)-border_radius['border_top_left_radius'])
            # dist = round(sqrt(2)*border_radius['border_top_left_radius']-border_radius['border_top_left_radius'])
            # pygame.draw.arc(
            #     self.image,
            #     (0,0,0,0),
            #     pygame.Rect(
            #         -dist,
            #         -dist,
            #         border_radius['border_top_left_radius']*2+dist,
            #         border_radius['border_top_left_radius']*2+dist),
            #     radians(90), radians(180),
            #     dist
            # )



            # dist = int(sqrt(border_radius['border_top_right_radius']**2*2)-border_radius['border_top_right_radius'])
            # pygame.draw.arc(
            #     self.image,
            #     (0,0,0,0),
            #     pygame.Rect(
            #         self.rect.w-border_radius['border_top_right_radius']*2,
            #         -dist,
            #         border_radius['border_top_left_radius']*2+dist,
            #         border_radius['border_top_right_radius']*2+dist),
            #     radians(0), radians(90),
            #     dist
            # )



        # Border
        border = style.get('border')
        if border:
            pygame.draw.rect(
                self.image,
                border,
                self.nullrect,
                width=border_width,
                **border_radius
            )


    

    @overload
    def construct(self, state: str): ...
    @overload
    def construct(self, **style): ...

    def construct(self, state: str = None, **style):
        """Constructs the asset.
        ### parameters:
         `state`: str -> constructs from the saved states
         `**style`: dict -> constructs from the given style

         OR normal Style keys

        ### Optional keywords
         `reset_state`: bool -> set the selected state to `None` or not.
            Only works if the provided state is not a string.
            default: True
        """
        self.change_style(state)

        if type(state) is str:
            self._construct(**self.style)
        
        else:
            self._construct(**style)




    def transition(self, state: str, time: int, *style_keys, _all=False, easing: EasingName | Callable = 'linear', ignore_scheck = False):
        """
        Transitions the asset to the given state.
        ### parameters:
        - `time:` (seconds or frames) The duration of the transition. Treated as game frames if the `delta_time` parameter is not used in the `update` method.
        - `state:` The state to transition into.
        - `*style_keys:` A list of style keys you want to transition.
        - `_all:` Ignore `style_keys` and transition everything.
        - `easing:` The easing function to use. See `assets.EASING_FUNCTIONS`
        - `ignore_scheck:` Do the transition even when the selected state is already tha state you are transitioning into.
        """
        if type(state) is str:
            if not ignore_scheck:
                if state == self.selected_state:
                    return
                
            if not self.states.get(state):
                raise KeyError(f'{state} is not a valid state. (not in {self.__class__}.states)')
            

            # NOTE: removed so you can smoothly change the selected state's values.
            
            _state = self.states[state]
            self._transition = None
            self._transition = Transition(time, self.style, _state,style_keys, _all=_all, easing=easing)
            self.selected_state = state
            

    


    def update(self, delta_time: float = 1) -> None:
        super().update(delta_time)

        if self._transition:
            if self._transition.finished: # remove if finished
                self._transition = None
                self._construct(**self.style) # Fix possibly not perfect ending of transition
            else:
                self._transition.tick(delta_time)
                self.change_style(self._transition.style, False)
                self._construct(**self._transition.style)






T1 = TypeVar('T1')
T2 = TypeVar('T2')


class GenericCombinedAsset(dict[T1, T2]):
    """Generic class for CombinedAsset"""
    def __init__(self, rect: pygame.Rect = None, **assets: T2):
        """Generic class for CombinedAsset"""
        super().__init__(**assets)

        self.rect = rect
        


    def update(self, delta_time: float = 1):
        for asset in self.values():
            asset.update(delta_time)


    def handle_event(self, event: pygame.Event):
        for asset in self.values():
            rect = asset.rect.copy()
            asset.rect = pygame.Rect(self.rect.left + asset.rect.left,
                               self.rect.top + asset.rect.top,
                               asset.rect.width,
                               asset.rect.height)
            asset.handle_event(event)
            asset.rect = rect


    def draw(self, surf: pygame.Surface):
        image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for asset in self.values():
            asset.draw(image)

        surf.blit(image, self.rect)


    def __getattribute__(self, name: T1) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self.__getitem__(name)
            except KeyError:
                raise AttributeError(f"No attribute or key named '{name}'.")
        

    def __setattr__(self, name: T1, value: T2) -> None:
        if self.get(name):
            self.__setitem__(name, value)
        else:
            super().__setattr__(name, value)

        print(name, value)

    def __setitem__(self, key: T1, value: T2) -> None:
        if super().__getattribute__(key):
            raise KeyError(f"'{key}' is already an attribute of this object! You cannot have items named the same as attributes.")
        super().__setitem__(key, value)




class CombinedAsset(GenericCombinedAsset[str, Asset]):
    """
    Base class for all assets that are made up of multiple parts.
    """

    # only needed for docsting
    def __init__(self, rect: pygame.Rect = None, **assets: Asset):
        """
        Base class for all assets that are made up of multiple parts.
        """
        super().__init__(rect, **assets)




class GenericCombinedStatedAsset(GenericCombinedAsset[T1, StatedAsset]):
    """Generic class for CombinedStatedAsset."""
    
    def __init__(self, rect: pygame.Rect = None, **assets):
        
        super().__init__(rect, **assets)
        # EXAMPLE:
        # {
        #     'state1': {
        #         'asset1': 'hover',
        #         'asset2': 'default'
        #     }
        # }
        self.states: dict[str, dict[str, str]] = {
            'default': {key: value.states['default'] for key, value in self.items()},
        }

        self.selected_state = 'default'

        self._transition = None
        self.style = self.states[self.selected_state].copy()

    

    def change_style(self, state: str | dict[str, dict[str, str]] | None, change_selected = True):
        if type(state) is str:
            if not self.states.get(state):
                raise KeyError(f'{state} is not a valid state. (not in {self.__class__}.states)')
            
            self.selected_state = state
            if change_selected:
                self.style = self.states[state]

        elif state is None:
            self.style = {}
            if change_selected:
                self.selected_state = None

        else:
            self.style = state
            if change_selected:
                self.selected_state = None


    # FIXME: not working due to ListedTransition not being made yet
    def transition(self, state: str, time: int, *style_keys, _all=False, easing: EasingName | Callable = 'linear', ignore_scheck = False):
        """
        Transitions the asset to the given state.
        ### parameters:
        - `time:` (seconds or frames) The duration of the transition. Treated as game frames if the `delta_time` parameter is not used in the `update` method.
        - `state:` The state to transition into.
        - `*style_keys:` A list of style keys you want to transition.
        - `_all:` Ignore `style_keys` and transition everything.
        - `easing:` The easing function to use. See `assets.EASING_FUNCTIONS`
        - `ignore_scheck:` Do the transition even when the selected state is already tha state you are transitioning into.
        """
        raise Exception('This is not working yet.')
        if type(state) is str:
            if not ignore_scheck:
                if state == self.selected_state:
                    return
                
            if not self.states.get(state):
                raise KeyError(f'{state} is not a valid state. (not in {self.__class__}.states)')
            

            # NOTE: removed so you can smoothly change the selected state's values.
            
            _state = self.states[state]
            self._transition = None
            self._transition = Transition(time, self.style, _state,style_keys, _all=_all, easing=easing)
            self.selected_state = state


    

    

    



class CombinedStatedAsset(GenericCombinedStatedAsset[str, StatedAsset]):
    """Base class for all assets that are made up of multiple stated assets. You can can create general states which include multiple assets."""

    # only needed for docstring
    def __init__(self, rect: pygame.Rect = None, **assets):
        """Base class for all assets that are made up of multiple stated assets. You can can create general states which include multiple assets."""
        super().__init__(rect, **assets)



class AnimatedAsset(StatedAsset):
    """
    A StatedAsset which accepts animations in states.
    
    ### 
    """
    def __init__(self, rect: pygame.Rect = None, *groups, **kwds):
        super().__init__(None, rect, *groups, **kwds)


        self.frozen = False
    

    
    @property
    def current_anim(self) -> Animation:
        return self.states[self.selected_state].get('anim', None)



    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs) 
        
        if not self.frozen:
            anim = self.current_anim
            anim.tick()
            self.image = anim.frames[anim.frame]


    
    def select_anim(self, anim: str):
        self.current_anim.reset()
        self.anim_index = anim



    def freeze(self):
        self.frozen = True

    def unfreeze(self):
        self.frozen = False








def auto_sized_text(text: str, font: pygame.Font, font_params, border_rect: pygame.Rect):
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