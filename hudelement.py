import pyglet
from utils import load_image

from utils import*
from resources import*
from shared import*

class AnchoredSprite(pyglet.sprite.Sprite):
    """
    offset_x 20 would be anchored on the left side of the window, 20 pixels right
    offset_y -20 would be anchored on the top side of the window, 20 pixels down
    """
    def __init__(self, image, offset_x, offset_y, render_group = hud):
        super(AnchoredSprite, self).__init__(image, 0, 0, batch=batch, group = render_group)
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        self.right = False
        self.top = False
        
        if offset_x < 0:
            self.right = True
            self.x = window.width+self.offset_x
        else:
            self.x = self.offset_x

        if offset_y < 0:
            self.top = True
            self.y = window.height+self.offset_y
        else:
            self.y = self.offset_y

        window.push_handlers(self.on_resize)
        
    def on_resize(self, width, height):
        if self.right:
            self.x = window.width+self.offset_x
        if self.top:
            self.y = window.height+self.offset_y
            

class Bar(pyglet.sprite.Sprite):
    
    def __init__(self, stat,
                 image_bar = Resources.Image.Hud.bar,
                 image_border = Resources.Image.Hud.border,
                 x = 0,
                 y = 0,
                 render_group = hud):
        
        super(Bar, self).__init__(image_bar, x, y, batch=batch, group = render_group)

        self.border = pyglet.sprite.Sprite(image_border, x, y, batch=batch, group = render_group)
        self.length = float(self.width)
        self.stat = stat
        
    def center_on(self, x, y):
        self.position = (x, y-(self.height/2))
        self.border.position = self.position

    def update(self):
        img = self.image.get_region(0,0,int((self.length/self.stat.max) * self.stat.current),self.height)
        img.anchor_x = self.length/2
        img.anchor_y = self.height/2
        self.image = img

    def clean(self):
        try:
            self.border.delete()
            self.delete()
        except AttributeError:
            #print "why"
            pass

