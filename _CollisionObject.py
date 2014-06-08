"""
    info:
    Currently not in use. This is a future proof version of CollisionObject which
    should be used further on.

    Removed collisions[] -- is not used anywhere?
 
"""

import pyglet
from math import sin, cos, pi, radians, sqrt
from utils import*
from shared import*

class CollisionObject(pyglet.sprite.Sprite):
    #base object, never moves, only detects collision, won't do anything with it 
    
    def __init__(self, image, x, y, render_group = middleground, collision_group = collision_objects):
        super(CollisionObject, self).__init__(image, x, y, batch=batch, group = render_group)
    
        self.collision_group = collision_group
    
    def objects_in_range(self, distance):
        for obj in self.collision_group:
            if obj != self and self.distance_to(obj) < distance:
                yield obj

    def check_collision(self):
        for obj in self.collision_group:
            if self.collision(obj) and obj != self:
                self.on_collision(obj)
                obj.on_collision(self)
    
    def distance_to(self, obj):
        return sqrt( (other.x - self.x)**2 + (other.y - self.y)**2 )

    def check_bounds(self):
    	self.x = window.width if self.x > window.width else 0 if self.x < 0
    	self.y = window.height if self.y > window.height else 0 if self.y < 0
            
    def move_to(self, x, y):
    	self.x, self.y = x, y

    	self.check_bounds()
    	self.check_collision()
            
    def move_by(self, x, y):
        x, y = self.x + x, self.y + y
        self.move_to(x, y)
        
    def remove(self):
        self.release()
        self.clean(1)
    
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


class RadialCollisionObject(CollisionObject):

	def __init__(self, image, x=0, y=0, radius, group, collision_group = collision_objects, mass = 1):
		super(RadialCollisionObject, self).__init__(image, x, y, radius, batch=batch, group=group)

		self.type = "radial"
		self.mass = mass
		self.radius = radius
		self.solid = True

	def collision(self, obj): #coliding_with replacement
	if obj.type == "radial":
		return (obj.x-self.x)**2 + (self.y-obj.y)**2 < (self.radius+obj.radius)**2
	elif obj.type == "box":
		return False #temporary

    def push(self, angle, force):
    	angle = radians(angle)
    	self.force_x, self.force_y += force * cos(angle), force * sin(angle)

	def relative_push(self, obj, force=1): #seperate replacement
        angle = angle_between(self, obj)
        dist = distance_between(self, obj)
            
        self.x += force*(cos(angle * (pi/180)) * (dist-self.radius-obj.radius))
        self.y += force*(sin(angle * (pi/180)) * (dist-self.radius-obj.radius))

    def on_collision(self, obj):
        self.relative_push(self, obj, abs(self.mass - abs(self.mass - obj.mass)))

class StaticRadialCollisionObject(RadialCollisionObject):
	def __init__(self, image, x, y, radius, render_group = False, collision_group = False):
   		super(StaticObject, self).__init__(image, x, y, radius, render_group, collision_group)

class DynamicRadialCollisionObject(RadialCollisionObject):
    def __init__(self, image, x, y, radius, render_group = False, collision_group = False, physic_ticks = 60, mass = 1):
        super(DynamicObject, self).__init__(image, x, y, radius, render_group, collision_group, mass)	

      	self.velocity_x, self.velocity_y = 0, 0
      	self.force_x, self.force_y = 0,0

      	self.friction = 0.01

      	pyglet.clock.schedule_interval_soft(self.loop, 1/physic_ticks)

    def loop(self, dt):
    	if self.moving():
    		friction = pow(self.friction, dt)
    		cut = 1

            self.velocity_x = cutoff(self.velocity_x, cut)
            self.velocity_y = cutoff(self.velocity_y, cut)

            self.force_x = cutoff(self.force_x, cut)
            self.force_y = cutoff(self.force_y, cut)
            
            self.velocity_x *= friction
            self.velocity_y *= friction

            self.force_x *= friction
            self.force_y *= friction

            self.move_by((self.velocity_x+self.force_x)*dt, (self.velocity_y+self.force_y)*dt)

    def moving(self):
        if (self.velocity_x  + self.velocity_y + self.force_x + self.force_y) != 0:
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
        #phyce# but mass isn't gonna change the force pushing anyways?
        #phyce# mass should change maths in other functions, like reduce_velocity
        obj.force_x += self.velocity_x * 0.1
        obj.force_y += self.velocity_y * 0.1

    def check_bounds(self):
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