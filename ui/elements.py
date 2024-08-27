from _collections_abc import dict_values
import pygame
from typing import Self
from ..sprite import *



class Button(StatedSprite):
    def __init__(self,
                 rect: pygame.Rect = None,
                 text: str = None,
                 bg = (0,0,0,0),
                 border = (50,50,50),
                 image: pygame.Surface = None,
                 **style):
        
        _hover_state = { # created here before the style is updated
            'image': image,
            'text': text,
            'bg': border,
            'border': bg,
            **style
        }

        style.update({
            'image': image,
            'bg': bg,
            'border': border,
            'text': text
            })
        
        super().__init__(rect, **style)


        self.states['hover'] = _hover_state




        # Events
        @self.event()
        def onhover(isHovered: bool):
            if isHovered and self.selected_state != 'hover':
                self.construct('hover')

            elif not isHovered and self.selected_state == 'hover':
                self.construct('default')







class ProgressBar(StatedSprite):
    """
    A progress bar that can be used to show a changing value.
    
    Automatically reconstructs if the value is changed.

    ### Keywords
    - `value`: The value to show on the progress bar.
    - `max_value`: The maximum value that the progress bar can show.
    - +Style keywords


    ### Special Style keys:
    - `fg:` Used as the inner color of the pbar.
    - `fg_radius:` rounding of the inner color
    """
    def __init__(self,
                 rect: pygame.Rect = None, bg = (0,0,0,0),
                 fg = (160,0,0),
                 border = (100,100,100),
                 **style):
        
        
        style.update({'bg': bg,
                      'fg': fg,
                      'border': border,})
        
        # rounding the left side is not needed
        fg_rad = style.pop('fg_radius', None)
        if fg_rad:
            style['fg_radius'] = {
                'border_top_right_radius' : fg_rad,
                'border_bottom_right_radius' : fg_rad,
            }
        

        self.max_val: float = style.get('max_value', 100)
        self.value: float = style.get('value', 0)

        self._old_value = self.value

        super().__init__(rect, **style)


    def update(self, delta_time = 1):
        super().update(delta_time)

        if self.value != self._old_value:
            if self.value > self.max_val:
                self.value = self.max_val
            else:
                self.construct('default')

            self._old_value = self.value


    
    def _construct(self, **kwds):
        
        fg_w = self.rect.w * (self.value/self.max_val)
        super()._construct(fg_rect=pygame.Rect(0, 0, fg_w, self.rect.h), **kwds)





class Switch(CombinedStatedSprite):
    def __init__(self,
                 rect: pygame.Rect = None,
                 body: StatedSprite | None = None,
                 pointer: StatedSprite | None = None,
                 vertical = False):
        
        # Dimension
        # 0 = horizontal (x); 1 = vertical (y)
        self._dim = int(vertical)


        if body is None:
            _brect = pygame.Rect(0,0,rect.w,rect.h)
            body = Button(_brect,background=(100,100,100), border=(50,50,50), border_radius=1000)

        if pointer is None:
            pointer = Button(pygame.Rect(0,0,rect.size[self._dim-1],rect.size[self._dim-1]), bg=(50,50,50), border=(0,0,0), border_radius=1000)

        @body.event
        def onclick(isClicked):
            if isClicked:
                self.switch()
                self.construct(str(self._value))


        super().__init__(rect, body=body, pointer=pointer)

        self.pointer: StatedSprite
        self.body: StatedSprite

        self._value = False


        self.states['0'] = self.states['default'].copy()
        del self.states['default']
        self.states['1'] = {
            'body': ''

        }



    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = bool(val)


    def switch(self):
        self.value = not self.value

    




class Slider(CombinedSprite):
    """
    A slider with a changable value.
    If no body and pointer sprites are set, the default slider style will be used.
    """
    def __init__(self, 
                 rect: pygame.Rect | None = None,
                 body: Sprite | None = None,
                 pointer: Sprite | None = None,
                 vertical = False):
        """
        A slider with a changable value.
        If no body and pointer sprites are set, the default slider style will be used.
        """
         
        #TODO: different slider styles with pre-made sprites

        # Dimension
        # 0 = horizontal (x); 1 = vertical (y)
        self._dim = int(vertical)

        if body is None:
            if self._dim == 0:
                _brect = pygame.Rect(0,0,rect.w,rect.h//2)
                _brect.centery = rect.h//2
            else:
                _brect = pygame.Rect(0,0,rect.w//2,rect.h)
                _brect.centerx = rect.w//2

            body = StatedSprite(_brect,background=(100,100,100), border=(50,50,50), border_radius=1000)


        if pointer is None:
            pointer = Button(pygame.Rect(0,0,rect.size[self._dim-1],rect.size[self._dim-1]), bg=(50,50,50), border=(0,0,0), border_radius=1000)

        @pointer.event()
        def onhover(isHovered: bool):
            if isHovered and pointer.selected_state != 'hover' and not self._clicked:
                pointer.construct('hover')

            elif not isHovered and pointer.selected_state == 'hover' and not self._clicked:
                pointer.construct('default')



        super().__init__(rect, body=body, pointer=pointer)

        self.pointer: Sprite
        self.body: Sprite


        self._clicked = False
        self._value = 0
        self._max_val = 100

        @self.pointer.event()
        def onleftclick(isClicked: bool):
            if isClicked:
                self._clicked = True

        @self.pointer.event()
        def onleftrelease(isReleased: bool):
            if self._clicked and isReleased:
                self._clicked = False
                pointer.construct('default')



    def set_pointer_pos(self, pos: int):
        if self._dim == 0:
            self.pointer.rect.centerx = pos
        else:
            self.pointer.rect.centery = pos



    def callback(value: float):
        """This will be called when the slider is used."""
        pass



    def update(self, delta_time: float = 1):
        super().update(delta_time)

        if self._clicked:
            # relative mouse pos
            rmouse_p = pygame.mouse.get_pos()[self._dim] - self.rect.topleft[self._dim]

            offset = self.pointer.rect.size[self._dim]//2

            pointer_pos = min(self.rect.size[self._dim]-offset, max(offset, rmouse_p))
            self.set_pointer_pos(pointer_pos)


            distance = pointer_pos / (self.rect.size[self._dim] - self.pointer.rect.size[self._dim])
            self._value = distance * self._max_val

            self.callback(self._value)



    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val: float | int):
        size = self.rect.size[self._dim] - self.pointer.rect.size[self._dim] # the distance the center of the pointer can make without going outside the slider borders
        offset = self.pointer.rect.size[self._dim]//2
        progress = val / self._max_val

        self.set_pointer_pos(offset + size*progress)
        self._value = val
        self.callback(val)

    
    # FIXME: the pointer can move a bit past the slider borders.
    def set_value(self, val: float, transition=False):
        size = self.rect.size[self._dim] - self.pointer.rect.size[self._dim] # the distance the center of the pointer can make without going outside the slider borders
        offset = self.pointer.rect.size[self._dim]//2
        progress = val / self._max_val

        self._value = val
        if transition:
            if self._dim == 0:
                style: Style = {'rect': (round(offset + size*progress), 'auto', 'auto', 'auto')}
            else:
                style: Style = {'rect': ('auto', round(offset + size*progress), 'auto', 'auto')}
            
            self.pointer: StatedSprite
            self.pointer.transition(style, .2, 'rect', easing='cubic_in')

        else:
            self.set_pointer_pos(offset + size*progress)

        self.callback(val)