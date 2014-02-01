"""
    info:
 
"""

import pyglet
from math import sin, cos, pi, radians, sqrt
from utils import*
from shared import*

class CollisionObject(pyglet.sprite.Sprite):
    #base object, never moves, only detects collision, won't do anything with it 
    
    def __init__(self, image, x, y, radius, render_group = middleground, collision_group = collision_objects):
        super(CollisionObject, self).__init__(image, x, y, batch=batch, group = render_group)

        self.radius = radius        
        self.collision_group = collision_group
        self.collisions = []
    
    def objects_in_range(self, distance):
        #returns "all" objects in pixel distance
        for obj in self.collision_group:
            if obj != self and self.distance_to(obj) < distance:
                yield obj

    def distance_to(self, other):
        return sqrt( (other.x - self.x)**2 + (other.y - self.y)**2 )
        
    def coliding_with(self, other):
        #circle to circle collision
        return (other.x-self.x)**2 + (self.y-other.y)**2 < (self.radius+other.radius)**2


    def check_collision(self):
        #put all colliders in self.collisions, run on_collision (for both objects??)
        self.collisions = []
        for obj in self.collision_group:
            if self.coliding_with(obj) and obj != self:
                self.collisions.append(obj)
                self.on_collision(obj)
                obj.on_collision(self)
                
    def on_collision(self, obj):
        #to be overwritten/added to it
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
        self.check_collision()
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
        if self in self.collision_group:
            for obj in self.collision_group:
                if self in obj.collisions:
                    #first all reference of self in any other collision_objects collisions list
                    obj.collisions.remove(self)
            #then delete self from collision_objects
            self.collision_group.remove(self)
        #lastly delete sprite from the batch
        try:
            self.delete()
        except AttributeError:
            #print "why"
            pass
        
class StaticObject(CollisionObject):
    #an object that will stay in place, and keep other objects from going through
    """
    well... because it never moves it'll never check for collisions,
    so it's just needed for DynamicObject, which moves and checks collision against this
    """
    def __init__(self, image, x, y, radius, render_group = False, collision_group = False):
        super(StaticObject, self).__init__(image, x, y, radius, render_group, collision_group)

    
class DynamicObject(CollisionObject):
    #an object that will move on collision and keep others from groing through
    def __init__(self, image, x, y, radius, render_group = False, collision_group = False, physic_ticks = 60):
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

