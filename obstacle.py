from collisionobject import StaticObject
from random import randint, uniform

from utils import*
from resources import*
from shared import*

class Obstacle(StaticObject):

    def __init__(self, image, x, y, radius, render_group = render_groups["middleground"], collision_group = collision_groups["obstacle"]):
        super(Obstacle, self).__init__(image, x, y, radius, render_group, collision_group)
        
        self.rotation = randint(0, 359)
        rand = uniform(0.8, 1.2)
        self.scale = rand
        self.radius *= rand

        #self.check_collision()

    def on_collision(self, obj):
        if isinstance(obj, Obstacle):
            self.seperate(obj)
            obj.seperate(self)
