from collisiongroup import *

class Base(object):
    def __init__(self, x, y, group):
        self.x = x
        self.y = y
        self.group = group
        self.group.append(self)
        ##may not even need the group here, just append it outside... i dunno
        
    def collision(self, other):
        if self.colliding_with(other):
            print "%s colliding with %s" % (self, other)
            self.send_collision(other)
            other.recieve_collision(self)

    def colliding_with(self, other):
        #overwrite for a subclass, with the subclass specific collision method call on other
        pass
    
    def send_collision(self, other):
        #called by the collision check from self
        #in which case other must be from on of the groups in self.group.mask
        #or, depending on the type of group used, self.group.container
        pass
    
    def recieve_collision(self, other):
        #called by the collision check from other
        #in which case other must have self in one of the groups in other.group.mask
        #or, again depending on the group, other.group.container
        pass

    def __repr__(self):
        return "%s, %s, %s" % (self.__class__.__name__, self.x, self.y)


class Radial(Base):
    def __init__(self, x, y, radius, group):
        super(Radial, self).__init__(x, y, group)
        self.radius = radius
        
    def colliding_with(self, other):
        #no type check, because other has to implement radial_collision
        #so if other is a box, the implemented radial_collision should be box vs radial
        #if other is a kitchen sink, the implemented radial_collision should be kitchen sink vs radial
        #etc
        return other.radial_collision(self)

    def radial_collision(self, other):
        #self=radial, other=radial
        return (self.x-other.x)**2 + (other.y-self.y)**2 < (other.radius+self.radius)**2
    
    def box_collision(self, other):
        #self=radial, other=box
        return False

    
class Box(Base):
    def __init__(self, width, height, group):
        super(Radial, self).__init__(x, y, group)
        self.width = width
        self.height = height

    def colliding_with(self, other):
        #other has to implement box_collision
        return other.box_collision(self)

    def radial_collision(self, other):
        #self=box, other=radial
        return False
    
    def box_collision(self, other):
        #self=box, other=box
        return  (abs(other.x - self.x) * 2 < (other.width + self.width) and
                 abs(other.y - self.y) * 2 < (other.height + self.height))



##TEST STUFF

class Bullet(Radial):
    collision_groups["bullet"] = ["unit","obstacle"]
    
    def __init__(self, x, y, radius, group=collision_groups["bullet"]):
        super(Bullet, self).__init__(x, y, radius, group)
        
    def send_collision(self, other):
        #a collision with one of the self.group.mask_objects happened (currently either a unit or an obstacle)
        #so remove the bullet, or maybe pass through a few objects for a special bullet or whatnot
        #also call bullet_collision on other, so other has to implement_bullet collision,
        #but it'll know without a type check, that a bullet hit it
        #so if other is a rock, it might play a clunk sound or add a small bullethole decal
        #oh the possibilitities
        other.bullet_collision(self)

class Unit(Radial):
    collision_groups["unit"] = ["unit", "obstacle", "powerup"]
    
    def __init__(self, x, y, radius, group=collision_groups["unit"]):
        super(Unit, self).__init__(x, y, radius, group)

    def send_collision(self, other):
        #again... other, which is one of the objects possible set by the collision group,
        #so in this case either a unit, because CollisionGroupMe checks the container, obstacle or powerup,
        #have to implement a unit_collision
        other.unit_collision(self)

    def unit_collision(self, unit):
        #seperate the 2 units
        pass
        print "%s was ...touched by %s" % (self, unit)
    
    def bullet_collision(self, bullet):
        #play a hurt sound, remove health etc
        pass
        print "%s was hit by %s" % (self, bullet)


##why no init? reasons!
##still have to explain for what a collision group without a mask is...
class Obstacle(object):
    collision_groups["obstacle"] = []
    
    def unit_collision(self, unit):
        #seperate the unit
        pass
        print "%s was ...touched by %s" % (self, unit)
        
    def bullet_collision(self, bullet):
        #sound, maybe add a decal to the obstacle...
        pass
        print "%s was hit by %s" % (self, bullet)


class Pillar(Radial, Obstacle):
    def __init__(self, x, y, radius, group=collision_groups["obstacle"]):
        super(Pillar, self).__init__(x, y, radius, group)
        
class Wall(Box, Obstacle):
    def __init__(self, x, y, width, height, group=collision_groups["obstacle"]):
        super(Wall, self).__init__(x, y, width, height, group)


class Powerup(Radial):
    collision_groups["powerup"] = []
    
    def __init__(self, x, y, radius, group=collision_groups["powerup"]):
        super(Powerup, self).__init__(x, y, radius, group)

    def unit_collision(self, unit):
        pass
        print "%s got picked up by %s" % (self, unit)
    
def test():
    Unit(100,100,25)
    Unit(125,125,25)
    Bullet(100,100,5)
    Bullet(100,100,5)
    Pillar(100,100,25)
    Pillar(125,125,25)
    Powerup(100,100,10)
    Powerup(125,125,10)

from shared import*
from resources import*
import pyglet
class Anchor(object):
    def __init__(self, parent, followers):
        self.parent = parent
        self.followers = followers
        
    @property
    def x(self):
        return self.parent.x

    @x.setter
    def x(self, val):
        self.parent.x = val
        for follower in self.followers:
            follower.x = val
        
class UnitTest(object):
    def __init__(self,
                 x,
                 y,
                 radius=36,
                 image=Resources.Image.player,
                 layer=render_groups["foreground"]):
        self.collision = Unit(x, y, radius)
        self.sprite = pyglet.sprite.Sprite(image, x, y, batch = batch, group = layer)
        self.anchor = Anchor(self.collision, [self.sprite])
    
if __name__ == "__main__":
    from game import*
    game = Game()

    test()
    u = UnitTest(500, 111)
    game.update(1)
    print "more tests"
    u.anchor.x = 111
    game.update(1)
    game.run()



"""
class Sprite(pyglet.sprite.Sprite):
    def __init__(self, image, render_group):
        super(Sprite, self).__init__(image, 0, 0, batch = batch, group = render_group)
        

class GameObject(object):
    def __init__(self, x, y, sprite, ,shape, handlers):
        self.sprite = sprite(self)
        self.shape = shape(self)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        self.sprite.x = x

        
        
class CollisionObject(pyglet.sprite.Sprite):
    #base object, never moves, only detects collision, won't do anything with it 
    
    def __init__(self,
                 image,
                 x,
                 y,
                 radius,
                 render_group = render_groups["default"],
                 collision_group = collision_groups["default"] ):
        
        super(CollisionObject, self).__init__(image, x, y, batch=batch, group = render_group)
        
        self.radius = radius
        self.collision_group = collision_group
        
        collision_group.container.append(self)

    def objects_in_range(self, distance):
        #returns "all" objects in pixel distance
        for key in self.collision_group:
            if obj != self and self.distance_to(obj) < distance:
                yield obj

    def distance_to(self, other):
        return sqrt( (other.x - self.x)**2 + (other.y - self.y)**2 )
        
    def coliding_with(self, other):
        #circle to circle collision
        return (other.x-self.x)**2 + (self.y-other.y)**2 < (self.radius+other.radius)**2


    def send_collision(self, reciever):
        pass

    def recieve_collision(self, sender):
        pass
    
    def seperate(self, obj):
        #seperate self from obj along the angle between the two, and only for the dinstance they overlap
        angle = angle_between(self, obj)
        dist = distance_between(self, obj)
            
        self.x += cos(angle * (pi/180)) * (dist-self.radius-obj.radius)
        self.y += sin(angle * (pi/180)) * (dist-self.radius-obj.radius)
    
    def check_bounds(self):
        #check if object is outside of the window bounds,
        #if true just snaps it back to the bounds
        if self.x > window.width:
            self.x = window.width
        elif self.x < 0:
            self.x = 0
        if self.y > window.height:
            self.y = window.height
        elif self.y < 0:
            self.y = 0
            
    def move_to(self, x, y):
        self.x = x
        self.y = y

        self.check_bounds()
        self.on_move()
            
    def move_by(self, x, y):
        x = self.x + x
        y = self.y + y
        self.move_to(x, y)
        
    def remove(self):
        self.release()
        self.clean(1)

    def release(self):
        pass
    
    def clean(self,dt):
        #ok so delete all references...
        if self in self.collision_group.container:
            self.collision_group.container.remove(self)
        #lastly delete sprite from the batch
        try:
            self.delete()
        except AttributeError:
            #print "why"
            pass
        
class StaticObject(CollisionObject):

    def __init__(self, image, x, y, radius, render_group, collision_group):
        super(StaticObject, self).__init__(image, x, y, radius, render_group, collision_group)

    
class DynamicObject(CollisionObject):
    #an object that will move on collision and keep others from groing through
    def __init__(self, image, x, y, radius, render_group, collision_group, physic_ticks = 60):
        super(DynamicObject, self).__init__(image, x, y, radius, render_group, collision_group)

        #these are in pixel per second, not per tick, delta time and whatnot
        self.velocity_x = 0
        self.velocity_y = 0
        self.force_x = 0
        self.force_y = 0

        self.friction = 0.01

        pyglet.clock.schedule_interval_soft(self.loop, 1./physic_ticks)

    def loop(self, dt):
        #print "loop", self
        if self.moving():
            #print self.velocity_x, self.velocity_y
            #apply friction and set velocity/force to 0 if close to
            friction = pow(self.friction,dt)
            cut = 1

            self.velocity_x = cutoff(self.velocity_x, cut)
            self.velocity_y = cutoff(self.velocity_y, cut)

            self.force_x = cutoff(self.force_x, cut)
            self.force_y = cutoff(self.force_y, cut)
            
            self.velocity_x *= friction
            self.velocity_y *= friction

            self.force_x *= friction
            self.force_y *= friction
            #print self.friction**dt

            #actually move according to velocity and delta time
            self.move_by((self.velocity_x+self.force_x)*dt, (self.velocity_y+self.force_y)*dt)

    def on_move(self):
        pass
            
    def moving(self):
        if self.velocity_x != 0 or self.velocity_y != 0 or self.force_x != 0 or self.force_y != 0:
            return True
        return False

    def reduce_velocity(self):
        #this is called on collision with another dynamic,
        #reducing self... like drag or friction, need better name
        #also mb introduce mass to objects, for how much drag there is
        #also also, not helping at all cause again no dt
        self.velocity_x = self.velocity_x * 0.9
        self.velocity_y = self.velocity_y * 0.9

    def add_force(self, obj):
        #again, need better name and mb introduce mass, to check who would push who
        obj.force_x += self.velocity_x * 0.1
        obj.force_y += self.velocity_y * 0.1
    
    def push(self, angle, force):
        angle = radians(angle)
        self.force_x += force * cos(angle)
        self.force_y += force * sin(angle)

    def check_bounds(self):
        #check if object is outside of the window bounds,
        #if true just snap back to the bounds
        #and set the velocity on that axis to 0
        if self.x > window.width:
            self.x = window.width
            self.velocity_x = 0
            self.force_x = 0
        elif self.x < 0:
            self.x = 0
            self.velocity_x = 0
            self.force_x = 0
        if self.y > window.height:
            self.y = window.height
            self.velocity_y = 0
            self.force_y = 0
        elif self.y < 0:
            self.y = 0
            self.velocity_y = 0
            self.force_y = 0

    def release(self):
        pyglet.clock.unschedule(self.loop)
        super(DynamicObject, self).release()

if __name__ == "__main__":
    from resources import*
    from game import*
    game = Game()
    a = CollisionObject(Resources.Image.player, 200, 200, 36)
    game.run()
"""
