import pyglet

class GameObject(object):
    def __init__(self, sprite, collision, handlers):
        self.sprite = sprite
        self.collision = collision
        self.handlers = handlers
        


#sprite has x, y
#collision the shape like radial etc, needs x, y from somewhere tho

player_sprite = sprite(image, x, y, batch, whatnot)
player_collision = radial(radius, mass, whatnot)
player_handlers = playerhandlers()

player = gameobject(sprite, collision, handlers)
