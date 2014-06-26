import pyglet
from random import uniform

from utils import*
from resources import*
from shared import*

class AnimatedSprite(pyglet.sprite.Sprite):
    #fire and forget
    #also not really need an extra class.
    def __init__(self, animation, x, y, render_group = render_groups["effects"]):
        super(AnimatedSprite, self).__init__(animation, x, y, batch=batch, group = render_group)
        self.scale = uniform(0.9, 1.1)  

def add_explosion(x, y):
    return AnimatedSprite(Resources.Image.explosion, x, y)

def add_blood_splash(x, y, angle):
    s = AnimatedSprite(Resources.Image.Blood.splash, x, y)
    s.rotation = angle
    return s
