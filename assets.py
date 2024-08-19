import pygame
from typing import overload

from core import *





class ProgressBar(Asset):
    """
    Percentage bar

    ### Parameters
    - `size`: The size of the bar
    - `outer_col` -> color of the outer surface
    - `inner_col` -> color of the inner surface
    
    ### Keywords and Variables:
     - `max_val: float -> maximum value of the bar`
     - `value: float -> current value of the bar`
     - `border_size`: Coordinate -> size of the space between the inner and outer surfaces
    """
    def __init__(self, size: Coordinate = None, outer_col: ColorValue = (50,50,50), inner_col: ColorValue = (255,0,0), *groups, **kwds):
        super().__init__(None, *groups, **kwds)

        self.size = size

        self.max_val: float = kwds.get('max_val', 100)
        self.value: float = kwds.get('value', 0)

        self.outer_col = outer_col
        self.inner_col = inner_col

        self.border_size: Coordinate = kwds.get('border_size', (5,5))

        self.construct()

    def construct(self, value = None, max_value = None, outer_col: ColorValue = None, inner_col: ColorValue = None, border_size: Coordinate = None):
        if outer_col is None:
            outer_col = self.outer_col
        if inner_col is None:
            inner_col = self.inner_col
        if border_size is None:
            border_size = self.border_size

        if value:
            self.value = value
        elif max_value:
            self.max_val = max_value
        
        if self.value <= 0:
            return

        self.image = pygame.Surface(self.size)
        self.image.fill(outer_col)
        
        perc = self.value / self.max_val
        inner = pygame.Surface((self.get_width()*perc - border_size[0]*2,
                                self.get_height()-border_size[1]*2))
        inner.fill(inner_col)
        self.image.blit(inner, self.border_size)




class Slider(Asset):
    def __init__(self, base_size: Coordinate, button_size: Coordinate, *groups, **kwds):
        super().__init__(size=(max((base_size[0],button_size[0])),max((base_size[1],button_size[1]))), *groups, **kwds)

        self.base_col = kwds.get('base_col', (50,50,50))
        self.button_col = kwds.get('button_col', (50,50,150))

        self.base = pygame.Surface(base_size)
        self.button = BaseButton(button_size,None)

        self.value = kwds.get('value',0)
        self.max_value = kwds.get('max_value',100)
        self.clicked = False


        def onleftclick(button: BaseButton, ):
            self.clicked = True
        
        self.button.onleftclick = onleftclick



    def update(self):
        super().update()
        self.button.update()

        if self.clicked and not pygame.mouse.get_pressed():
            self.clicked = False


    
    def construct(self, **kwds):
        self.fill(kwds.get('base_col', self.base_col))
        self.button.fill(kwds.get('button_col', self.base_col))
    

    





class BaseButton(StatedAsset):
    def __init__(self, size: Coordinate, *groups):
        super().__init__(size, *groups)

        self.disabled = False


    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.onhover(True)
        
            pressed = pygame.mouse.get_pressed()
            if any(pressed):
                self._onclick(pressed)


        else:
            self.onhover(False)
    



class Button(BaseButton):
    """
    ### Parameters
     - `image` -> image to be displayed on button
     - `text` ->  string to be displayed on button
     - `bg`: ColorValue ->  background color of the button (default is black)
     - `border`: ColorValue ->  border color of the button (default is gray)

     
    ### Optional Keywords
     - `border_width`: int -> width of the `border`
     - `border_radius`: int -> radius of the rounded corners of the button

     - `img_alpha`: bool -> if True, the `image` will be converted with `.convert_alpha`, else with `.convert` (only used if `image` is `str`)
     - `img_scale`: Coordinate -> scale of the `image`. ('auto' means it will match the size of the button)

     - `font`: pygame.Font -> font of the `text`. (Only used if `text` is set.)
     - `font_params`: tuple -> parameters for the `font.render` method. (Only used if `font` is set.)
     - `text_pos`: Coordinate -> position of the text. if not set, center position of the `text`.

     
    ### How to use

    #### Events
     Rewrite the event methods, they all start with `on`.

    #### States
     Add states to the `Button.states` dictionary.
      KEYS (optional): image, text, bg, border, kwds (optional keywords written above)

    #### Construction
     Use the `Button.construct` method with a state or custom parameters.

    #### More customization
     Rewrite the `Button.update` method. Remember to also call it with super(), or the default events won't work.
    """

    def __init__(self,
                 size: Coordinate,
                 image: str|pygame.Surface = None,
                 text: str = None,
                 bg = (0,0,0,0),
                 border = (50,50,50), 
                 *groups,
                 **kwds):
        
        super().__init__(size, *groups)

        self.selected_state = 'default'
        self.states = {
            'default': {
                'image': image,
                'text': text,
                'bg': bg,
                'border': border,
                'kwds': kwds
            },
            'hover': {
                'image': image,
                'text': text,
                'bg': border,
                'border': bg,
                'kwds': kwds
            },
            'disabled': 'auto',
        }
        self._construct(**self.states['default'])



    def _construct(self, image=None, text=None, bg=None, border=None, **kwds):
        """Do not use this. This does not reset the selected state."""

        if bg:
            self.fill(bg)
        

        if type(image) is str:
            if kwds.get('img_alpha'):
                image = pygame.image.load(image).convert_alpha()
            else:
                image = pygame.image.load(image).convert()

        if kwds.get('img_scale') == 'auto':
            image = pygame.transform.scale(image, self.get_size())

        if 'img_scale' in kwds.keys():
            image = pygame.transform.scale(image, kwds.get('img_scale'))
        
        if image:
            print(image)
            self.blit(image,(0,0))
        

        if text:
            font: pygame.Font = kwds.get('font', pygame.Font(None, int(self.get_height()/2)))

            text = font.render(text, *kwds.get('font_params', (True, (255,255,255))))
            
            pos = kwds.get('text_pos', (self.get_width()/2, self.get_height()/2))
            
            text_rect: pygame.Rect = text.get_rect()
            text_rect.center = pos

            self.blit(text, text_rect)
    

        if border:
            pygame.draw.rect(self, border, ((0,0),self.get_size()), width=kwds.get('border_width', 2), border_radius=kwds.get('border_radius', -1))



    @overload
    def construct(self, state: str | dict, **kwds): ...
    @overload
    def construct(self, image, text, bg, border, **kwds): ...

    def construct(self, state: str = None, image=None, text=None, bg=None, border=None, **kwds):
        """Constructs the button.
        ### parameters:
         `state`: str -> constructs the button from the saved states
         `state`: dict -> constructs the button from the given custom state

         OR normal Button parameters

        ### Optional keywords
         `reset_state`: bool -> set the selected state to `None` or not.
            Only works if the provided state is not `str`.
            default: True
        """

        if type(state) is str:
            if not self.states.get(state):
                raise KeyError(f'{state} is not a valid state. (not in self.states)')

            self.selected_state = state
            self._construct(**self.states[state], **kwds)
        

        else:
            if type(state) is dict:
                self._construct(**state, **kwds)

            else:
                self._construct(image, text, bg, border, **kwds)
            

            if kwds.get('reset_state', True):
                self.selected_state = None
            



    def onhover(self, hover):
        if hover and self.selected_state == 'default':
            self.construct(state='hover')
        
        elif not hover and self.selected_state == 'hover':
            self.construct(state='default')
    
    def disable(self, _disable: bool = True, state = None):
        """Disable or enable button functions."""
        self.disabled = _disable

        if not state:
            state = self.states.get('disabled')
            if state == 'auto':
                self.fill((0,0,0,.2))
            else:
                self.construct(state='disabled')
                return
        
        
        self.construct(state=state)

    