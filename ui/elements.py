from _collections_abc import dict_values
import pygame
from ..core import *
from typing import Self

class Button(StatedAsset):
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
        def onhover(self: Self, isHovered: bool):
            if isHovered and self.selected_state != 'hover':
                self.construct('hover')

            elif not isHovered and self.selected_state == 'hover':
                self.construct('default')







class ProgressBar(StatedAsset):
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





class Switch(CombinedAsset):
    def __init__(self,
                 rect: pygame.Rect = None,
                 body: Asset | None = None,
                 pointer: Asset | None = None,
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


        super().__init__(rect, body, pointer)

        self.pointer: Asset
        self.body: Asset

        self._value = False


    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = bool(val)


    def switch(self):
        self.value = not self.value

    




class Slider(CombinedAsset):
    """
    A slider with a changable value.
    If no body and pointer assets are set, the default slider style will be used.
    """
    def __init__(self, 
                 rect: pygame.Rect | None = None,
                 body: Asset | None = None,
                 pointer: Asset | None = None,
                 vertical = False):
        """
        A slider with a changable value.
        If no body and pointer assets are set, the default slider style will be used.
        """
         
        #TODO: different slider styles with pre-made assets

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

            body = StatedAsset(_brect,background=(100,100,100), border=(50,50,50), border_radius=1000)


        if pointer is None:
            pointer = Button(pygame.Rect(0,0,rect.size[self._dim-1],rect.size[self._dim-1]), bg=(50,50,50), border=(0,0,0), border_radius=1000)

        @pointer.event()
        def onhover(pointer: Button, isHovered: bool):
            if isHovered and pointer.selected_state != 'hover' and not self._clicked:
                pointer.construct('hover')

            elif not isHovered and pointer.selected_state == 'hover' and not self._clicked:
                pointer.construct('default')



        super().__init__(rect, body=body, pointer=pointer)

        self.pointer: Asset
        self.body: Asset


        self._clicked = False
        self._value = 0
        self._max_val = 100

        @self.pointer.event()
        def onleftclick(pointer: Asset, isClicked: bool):
            if isClicked:
                self._clicked = True

        @self.pointer.event()
        def onleftrelease(pointer: Asset, isReleased: bool):
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








class OldSlider(StatedAsset):
    """
    A slider with a changable value.
    """
    def __init__(self, rect: pygame.Rect = None, pointer: StatedAsset = None, vertical=False, **style):
        # Dimension
        # 0 = horizontal (x); 1 = vertical (y)
        # in pygame, sizes are always saved as (x,y); 0th index is x, 1st index is y
        self._dim = int(not vertical)

        self.pointer: StatedAsset = pointer # TODO: make pointer styles

        @self.pointer.event()
        def onleftclick(pointer: StatedAsset, isClicked: bool):
            if isClicked:
                self.clicked = True

            elif self.clicked:
                self.clicked = False



        self.clicked = False
        self.value = 0
        self.max_val = 100

        super().__init__(rect, **style)
        


            
    def update(self, delta_time: int = 1) -> None:
        super().update(delta_time)
        self.pointer.update(delta_time)

        if self.clicked:
            # relative mouse pos
            rmouse_p = pygame.mouse.get_pos()[self._dim] - self.rect.topleft[self._dim]


            pointer_pos = min(self.rect.size[self._dim], max(0, rmouse_p))

            # Uptade pointer position
            if self._dim == 0:
                self.pointer.rect.left = pointer_pos
            else:
                self.pointer.rect.top = pointer_pos

            self.value = pointer_pos // self.rect.size[self._dim]
            


    
    def _construct(self, reset_image=True, **style):
        super()._construct(reset_image, **style)
        self.pointer.draw(self.image)

    def handle_event(self, event: pygame.Event):
        self.pointer.handle_event(event)
        super().handle_event(event)



            
    


