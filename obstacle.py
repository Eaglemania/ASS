from collisionobject import*

collision_groups["obstacle"] = ["unit"]

class ObstacleResponse(Response):

    def unit_response(self, unit):
        unit.seperate_from(self.collision)
        
        
class Crate(object):
    
    def __init__(self, x, y, width, height, group=collision_groups["obstacle"]):
        self.position = Position(x, y)
        self.collision = Box(self.position, width, height, group)
        self.response = ObstacleResponse(self.collision)
        self.sprite = Sprite(self.position, Resources.Image.Drops.ammunition)


if __name__ == "__main__":
    from game import*
    from unit import*
    from player import*
    from enemy import*
    game = Game()

    stuffs = []
    for i in range(20):
        stuffs.append(Unit(randint(0,window.width), randint(0, window.height), 24))           
    for i in range(20):
        stuffs.append(Enemy(randint(0,window.width), randint(0, window.height), 24))
    for i in range(20):
        stuffs.append(Crate(randint(0,window.width), randint(0, window.height), 32, 32))
    p = Player(300,300,24)
    p1 = Player(400,400,24)
    p2 = Player(600,600,24)
    pc = PlayerCrate(150,150,32,32)

    game.run()
"""
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

"""
