from .core import *

class Sprite(pygame.sprite.Sprite):
    """
    Base class for all sprites.

    ### Parameters:
    - `image` -> default surface of the sprite
    - `rect` -> rectangle of the sprite
    
    > one of these must have a value if you use 'auto'
    """
        
    def __init__(self, image: pygame.Surface | Literal['auto'] = None, rect: pygame.FRect | Literal['auto'] = None, *groups):
        super().__init__(*groups)
            
        self.image = image
        if rect == 'auto' and image:
            self.rect = image.get_rect()
        else:
            self.rect = rect
        
        if self.rect not in ('auto', None) and image is None:
            self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        
        self.Events = {}


    def update(self, delta_time: float = 1, *args: Any, **kwds: Any) -> None:
        # NOTE: removed because it always reset the StatedSprites' state to default
        # self.handle_event(pygame.Event(0, {}))
        pass


    @property
    def nullrect(self):
        """A copy of the sprite's rect at position (0,0)"""
        return pygame.FRect(0,0,self.rect.w,self.rect.h)

   

    def event(self, check: Callable | EventName | None = None, name: str | None = None, return_self: bool = False):
        """
        An event of the sprite. ALWAYS USE WITH BRACKETS

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
        - `name`: str -> Name of the event. If not given, the function name is used. Only affects its key in the `Sprite.Events` dictionary.
        - `check`: Callable | EventName -> Condition of the event.
            1. You can use a Callable which returns a boolean
            2. Or one of the default event names. This will use thet event's check but register this as a new event with the given name.
                (useful for having multiple events of the same type, e.g. keeping a default event while adding a new one too.)
        - `return_self`: bool -> If true, the function will be called with these parameters: (self, check) istead of (check)
            
        
        
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



            def wrapper(sprite, event, *args, **kwargs):
                if return_self:
                    return func(sprite, check(sprite,event), *args, **kwargs)
            
                return func(check(sprite,event), *args, **kwargs)


            self.Events[name] = wrapper
                                

            return wrapper
        return decorator


    def add_event(self, func: Callable, check: Callable | EventName | None = None, name: str | None = None, return_self: bool = False):
        """Add an event without using the decorator"""
        if name is None:
            name = func.__name__
        if check is None:
            check = DEFAULT_EVENT_CHECKS.get(name, lambda _,__: True)
        if check is None:
            check = DEFAULT_EVENT_CHECKS.get(name, lambda _,__: True)
        elif type(check) is str:
            check = DEFAULT_EVENT_CHECKS.get(check, lambda _,__: True)

        
        def wrapper(sprite, event, *args, **kwargs):
            if return_self:
                return func(sprite, check(sprite,event), *args, **kwargs)
        
            return func(check(sprite,event), *args, **kwargs)

        self.Events[name] = wrapper



    def handle_event(self, event: pygame.Event, *args, **kwds):
        """Call this when looping through events."""
        for spriteEvent in self.Events.values():
            spriteEvent(self, event, *args, **kwds)


    
    def draw(self, surf: pygame.Surface) -> None:
        """Draws the sprite on the surface."""
        surf.blit(self.image, self.rect)





class SpriteGroup(pygame.sprite.Group):
    """
    Group of Sprites.
    """
    def __init__(self, *elements):
        super().__init__(*elements)



    def handle_event(self, event: pygame.Event):
        """Call this when looping through events."""
        for sprite in self.sprites():
            sprite.handle_event(event)
    

    def update(self, delta_time: float, *args, **kwds):
        super().update(delta_time=delta_time, *args, **kwds)


    # Copied from pygame and modified
    def add(self, *sprites: Any | pygame.sprite.AbstractGroup | Iterable):
        for sprite in sprites:
            # It's possible that some sprite is also an iterator.
            # If this is the case, we should add the sprite itself,
            # and not the iterator object.
            if isinstance(sprite, Sprite):
                if not self.has_internal(sprite):
                    self.add_internal(sprite)
                    sprite.add_internal(self)
            # elif isinstance(sprite, GenericCombinedSprite):
            #     raise TypeError('You cannot put CombinedSprites in a group!')
            else:
                try:
                    # See if sprite is an iterator, like a list or sprite
                    # group.
                    self.add(*sprite)
                except (TypeError, AttributeError):
                    # Not iterable. This is probably a sprite that is not an
                    # instance of the Sprite class or is not an instance of a
                    # subclass of the Sprite class. Alternately, it could be an
                    # old-style sprite group.
                    if hasattr(sprite, "_spritegroup"):
                        for spr in sprite.sprites():
                            if not self.has_internal(spr):
                                self.add_internal(spr)
                                spr.add_internal(self)
                    elif not self.has_internal(sprite):
                        self.add_internal(sprite)
                        sprite.add_internal(self)


class StatedSprite(Sprite):
    """
    ### Keywords
    - `Style` keys for the sprite's 'default' state
    """
    def __init__(self, rect: pygame.FRect = None, *groups, **style):
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
            
            self.style = self.states[state].copy()
            if change_selected:
                self.selected_state = state

        elif state is None:
            self.style = {}
            if change_selected:
                self.selected_state = None

        else:
            self.style = state.copy()
            if change_selected:
                self.selected_state = None


    
    def _construct(self, reset_image=True, **style):
        """Do not use this. This does not change the selected state variable."""
        
        rect = style.get('rect')
        if rect:
            _r = check_rect_auto(rect, self.rect, style.get('check_rect_auto', True))
            self.rect.update(_r)
            
            
            

        if reset_image:
            self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        border_width = style.get('border_width', 2)
        border_radius = radius_kwds(style.get('border_radius'))


        # Background
        bg = style.get('bg', (0,0,0,0))
        if bg:
            pygame.draw.rect(self.image, bg, self.nullrect, **border_radius)


        # Foreground
        fg = style.get('fg')
        fg_rect = style.get('fg_rect', pygame.FRect(0,0,0,0))
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

            rect_without_border = pygame.FRect(
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
        # if border_radius:
        #     wh = min((self.rect.h//2,self.rect.w//2))
        #     if border_radius['border_top_left_radius'] > wh:
        #         border_radius['border_top_left_radius'] = wh
        #     if border_radius['border_top_right_radius'] > wh:
        #         border_radius['border_top_right_radius'] = wh
        #     if border_radius['border_bottom_left_radius'] > wh:
        #         border_radius['border_bottom_left_radius'] = wh
        #     if border_radius['border_bottom_right_radius'] > wh:
        #         border_radius['border_bottom_right_radius'] = wh
            

            # dist = round(sqrt(border_radius['border_top_left_radius']**2*2)-border_radius['border_top_left_radius'])
            # dist = round(sqrt(2)*border_radius['border_top_left_radius']-border_radius['border_top_left_radius'])
            # pygame.draw.arc(
            #     self.image,
            #     (0,0,0,0),
            #     pygame.FRect(
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
            #     pygame.FRect(
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
        """Constructs the sprite.
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




    def transition(self, state: str | Style, time: int, *style_keys, _all=False, easing: EasingName | Callable = 'linear', force = False):
        """
        Transitions the sprite to the given state.
        ### parameters:
        - `time:` (seconds or frames) The duration of the transition. Treated as game frames if the `delta_time` parameter is not used in the `update` method.
        - `state:` The state to transition into.
        - `*style_keys:` A list of style keys you want to transition.
        - `_all:` Ignore `style_keys` and transition everything.
        - `easing:` The easing function to use. See `sprites.EASING_FUNCTIONS`
        - `force:` Do the transition even when the selected state is already tha state you are transitioning into.
        """
        if type(state) is str:
            if not force:
                if state == self.selected_state:
                    return
                
            if not self.states.get(state):
                raise KeyError(f'{state} is not a valid state. (not in {self.__class__}.states)')
            
            
            _state = self.states[state]
            self.selected_state = state

        else:
            _state = state
            self.selected_state = None


        rect = _state.get('rect')
        if rect:
            _state['rect'] = check_rect_auto(rect, self.rect, _state.get('check_rect_auto', True))
            _state['check_rect_auto'] = False
            self.style['rect'] = [*self.rect]


        self._transition = None
        self._transition = Transition(time, self.style, _state,style_keys, _all=_all, easing=easing)
            

    


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


class GenericCombinedSprite(dict[T1, T2]):
    """Generic class for CombinedSprite"""
    def __init__(self, rect: pygame.FRect = None, **sprites: T2):
        """Generic class for CombinedSprite"""
        super().__init__(**sprites)

        self.rect = rect
        


    def update(self, delta_time: float = 1):
        for sprite in self.values():
            sprite.update(delta_time)


    # TODO: optimize this so it doesn't run multiple times each frame
    def handle_event(self, event: pygame.Event):
        for sprite in self.values():
            rect = sprite.rect.copy()
            sprite.rect = pygame.FRect(self.rect.left + sprite.rect.left,
                               self.rect.top + sprite.rect.top,
                               sprite.rect.width,
                               sprite.rect.height)
            sprite.handle_event(event)
            sprite.rect = rect


    def draw(self, surf: pygame.Surface):
        image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for sprite in self.values():
            sprite.draw(image)

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


    def __setitem__(self, key: T1, value: T2) -> None:
        if super().__getattribute__(key):
            raise KeyError(f"'{key}' is already an attribute of this object! You cannot have items named the same as attributes.")
        super().__setitem__(key, value)


    def __iter__(self):
        # raise TypeError(f'{self.__class__} is not iterable. Did you mean {self.__class__}.values()?')
        return iter(self.values())



class CombinedSprite(GenericCombinedSprite[str, Sprite]):
    """
    Base class for all sprites that are made up of multiple parts.
    """

    # only needed for docsting
    def __init__(self, rect: pygame.FRect = None, **sprites: Sprite):
        """
        Base class for all sprites that are made up of multiple parts.
        """
        super().__init__(rect, **sprites)



class GenericCombinedStatedSprite(GenericCombinedSprite[T1, T2]):
    """Generic class for CombinedStatedSprite."""
    
    def __init__(self, rect: pygame.FRect = None, **sprites):
        
        super().__init__(rect, **sprites)
        # EXAMPLE:
        # {
        #     'state1': {
        #         'sprite1': 'hover',
        #         'sprite2': 'default'
        #         'sprite3': {'bg': 'red', 'border': 'blue'}
        #     }
        # }
        #
        self.states: CombinedStyle = {
            'default': {key: 'default' for key in self.keys()},
        }

        self.selected_state = 'default'

        self.style = self.states[self.selected_state].copy()

    

    def change_style(self, state: str | CombinedStyle | None, change_selected = True):
        if type(state) is str:
            if not self.states.get(state):
                raise KeyError(f'{state} is not a valid state. (not in {self.__class__}.states)')
            
            self.selected_state = state
            if change_selected:
                self.style = self.states[state].copy()

        elif state is None:
            self.style = {}
            if change_selected:
                self.selected_state = None

        else:
            self.style = state.copy()
            if change_selected:
                self.selected_state = None

        for key, sprite in self.items():
            if key in self.style:
                sprite.change_style(self.style[key])
        
        



    def construct(self, style: str | CombinedStyle | None, force=False):
        """
        Constructs all of its Sprites from the selected style.
        - `force`: reconstruct the sprite even if its selected state is the same as the `style` parameter.
        """
        if type(style) is str:
            if not force and style == self.selected_state:
                return
            
            for key, sprite in self.items():
                try:
                    sprite.construct(self.states[style][key])
                except:
                    raise KeyError(f'{style} is not a valid state. (not in {sprite.__class__}.states)')
        
        elif type(style) is CombinedStyle:
            for key, sprite in self.items():
                sprite.construct(style[key])
            
        


    # TODO: Improve for custom parameters per sprite if possible.
    def transition(self, state: str, time: int, *style_keys, _all=False, easing: EasingName | Callable = 'linear', force = False):
        """
        Transitions the sprite to the given state.
        ### parameters:
        - `time:` (seconds or frames) The duration of the transition. Treated as game frames if the `delta_time` parameter is not used in the `update` method.
        - `state:` The state to transition into.
        - `*style_keys:` A list of style keys you want to transition.
        - `_all:` Ignore `style_keys` and transition everything.
        - `easing:` The easing function to use. See `sprites.EASING_FUNCTIONS`
        - `force:` Do the transition even when the selected state is already the state you are transitioning into.
        """
        # raise Exception('This is not working yet.')
        if type(state) is str:
            if not force:
                if state == self.selected_state:
                    return
                
            if not self.states.get(state):
                raise KeyError(f'{state} is not a valid state. (not in {self.__class__}.states)')
            

            self.change_style(state)
            
            for key, sprite in self.items():
                sprite.transition(state[key], time, style_keys, _all=_all, easing=easing, force=force)



    

    

    



class CombinedStatedSprite(GenericCombinedStatedSprite[str, StatedSprite]):
    """Base class for all sprites that are made up of multiple stated sprites. You can can create general states which include multiple sprites."""

    # only needed for docstring
    def __init__(self, rect: pygame.FRect = None, **sprites):
        """Base class for all sprites that are made up of multiple stated sprites. You can can create general states which include multiple sprites."""
        super().__init__(rect, **sprites)



class AnimatedSprite(StatedSprite):
    """
    A StatedSprite which accepts animations in states.
    
    ### 
    """
    def __init__(self, rect: pygame.FRect = None, *groups, **kwds):
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
