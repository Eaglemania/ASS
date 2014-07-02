from collisiongroup import collision_groups
from shared import*
from resources import*
from random import*
import pyglet

class Position(object):
    def __init__(self, x, y):
        self._x = x
        self._y = y
        self.children = []

    def set_x(self, x):
        self._x = x
        for child in self.children:
            child.x = x

    x = property(lambda self: self._x, set_x)

    def set_y(self, y):
        self._y = y
        for child in self.children:
            child.y = y

    y = property(lambda self: self._y, set_y)

    
class Collision(object):
    def __init__(self, position, group):
        self.position = position
        self.group = group
        self.group.append(self)

    def colliding_with(self, other):
        if other.type_collision(self):
            other.type_response(self)
    
    def type_collision(self, other):
        pass
    
    def type_response(self, other):
        pass

    def seperate_from(self, other):
        other.type_seperate(self)

    def type_seperate(self, other):
        pass


def radials(a, b):
    dx = b.position.x - a.position.x
    dy = b.position.y - a.position.y
    rads = atan2(dy, dx)
    dist = sqrt((dx**2)+(dy**2)) - a.radius-b.radius

    a.position.x += cos(rads)*dist
    a.position.y += sin(rads)*dist

    
def boxes(a, b):
    dx = b.position.x - a.position.x
    dy = b.position.y - a.position.y

    if abs(dx) > abs(dy):
        width = (a.width+b.width)/2
        if dx > 0:
            a.position.x = b.position.x-width
        else:
            a.position.x = b.position.x+width
    else:
        height = (a.height+b.height)/2
        if dy > 0:
            a.position.y = b.position.y-height
        else:
            a.position.y = b.position.y+height


def both(radial, box):
    #yea... not really...
    dy = box.position.y - radial.position.y
    dx = box.position.x - radial.position.x

    if abs(dx) > abs(dy):
        width = (radial.radius+box.width)/2
        if dx > 0:
            radial.position.x = box.position.x-width
        else:
            radial.position.x = box.position.x+width
    else:
        height = (radial.radius+box.height)/2
        if dy > 0:
            radial.position.y = box.position.y-height
        else:
            radial.position.y = box.position.y+height


class Radial(Collision):
    def __init__(self, position, radius, group):
        super(Radial, self).__init__(position, group)
        self.radius = radius

    def type_collision(self, other):
        return other.radial_collision(self)
    
    def radial_collision(self, other):
        #self=radial, other=radial
        return (self.position.x-other.position.x)**2 + (other.position.y-self.position.y)**2 < (other.radius+self.radius)**2

    def box_collision(self, other):
        #self=radial, other=box
        return (abs(other.position.x - self.position.x) * 2 < (other.width + self.radius) and
                abs(other.position.y - self.position.y) * 2 < (other.height + self.radius))

    def type_seperate(self, other):
        other.radial_seperate(self)
            
    def radial_seperate(self, other):
        #self=radial, other=radial
        radials(self, other)

    def box_seperate(self, other):
        #self=radial, other=box
        both(self, other)

            
class Box(Collision):
    def __init__(self, position, width, height, group):
        super(Box, self).__init__(position, group)
        self.width = width
        self.height = height

    def type_collision(self, other):
        return other.box_collision(self)

    def radial_collision(self, other):
        #self=box, other=radial
        return (abs(other.position.x - self.position.x) * 2 < (other.radius + self.width) and
                abs(other.position.y - self.position.y) * 2 < (other.radius + self.height))
    
    def box_collision(self, other):
        #self=box, other=box
        return  (abs(other.position.x - self.position.x) * 2 < (other.width + self.width) and
                 abs(other.position.y - self.position.y) * 2 < (other.height + self.height))

    def type_seperate(self, other):
        other.box_seperate(self)
            
    def radial_seperate(self, other):
        #self=box, other=radial
        both(other, self)

    def box_seperate(self, other):
        #self=box, other=box
        boxes(self, other)


class Velocity(object):
    def __init__(self, x, y):
        self.x = 0
        self.y = 0


def Sprite(position, image):
    sprite = pyglet.sprite.Sprite(image, position.x, position.y, batch=batch, group=render_groups["foreground"])        
    position.children.append(sprite)
    return sprite


class Movement(object):
    def __init__(self, position, walk_speed):
        self.position = position
        self.walk_speed = walk_speed
        self.current_speed = Velocity(0, 0)
        
        pyglet.clock.schedule(self.update)

    def update(self, dt):
        self.position.x += self.current_speed.x * dt
        self.position.y += self.current_speed.y * dt
        

class UnitCollision(Radial):
    def type_response(self, other):
        other.unit_response(self)

    def unit_response(self, unit):
        self.seperate_from(unit)


class Unit(object):
    collision_groups["unit"] = ["unit"]
    
    def __init__(self, x, y, radius, group=collision_groups["unit"]):
        self.position = Position(x, y)
        self.collision = UnitCollision(self.position, radius, group)
        self.sprite = Sprite(self.position, Resources.Image.player)
        self.movement = Movement(self.position, 100)


class PlayerController:
    def __init__(self, movement):
        self.movement = movement
        window.push_handlers(self)
        
    def on_key_press(self, symbol, modifiers):
        if symbol == keys["up"]:
            self.movement.current_speed.y = self.movement.walk_speed
        elif symbol == keys["down"]:
            self.movement.current_speed.y = -self.movement.walk_speed
        if symbol == keys["left"]:
            self.movement.current_speed.x = -self.movement.walk_speed
        elif symbol == keys["right"]:
            self.movement.current_speed.x = self.movement.walk_speed
        
    def on_key_release(self, symbol, modifiers):
        if symbol == keys["up"]:
            self.movement.current_speed.y = 0
        elif symbol == keys["down"]:
            self.movement.current_speed.y = 0
        if symbol == keys["left"]:
            self.movement.current_speed.x = 0
        elif symbol == keys["right"]:
            self.movement.current_speed.x = 0


class Player(Unit):
    def __init__(self, x, y, radius, group=collision_groups["unit"]):
        super(Player, self).__init__(x, y, radius, group)
        self.controller = PlayerController(self.movement)

class CrateCollision(Box):
    #what if i wanted to seperate everything regardless of type
    #lol i've been workin on this system for like 2 weeks
    #anyway, because unit is in the mask, (ALSO: collision_group should be set here?)
    #the unit will call unit_response on the crate, which means the crate must implement it...
    #that's bad.......
    #more things that are wrong: what if i want to switch out the responses
    #they are tied with the shape, box/radial
    #have the responses be a class without init?
    
    def unit_response(self, unit):
        unit.seperate_from(self)

class PlayerCrateCollision(Box):
    #this shoudn't be another class, it should use players group, and crates collision, whos responses tho?
    def type_response(self, other):
        other.unit_response(self)

    def unit_response(self, unit):
        unit.seperate_from(self)
        
class Crate(object):
    collision_groups["obstacle"] = ["unit"]
    
    def __init__(self, x, y, width, height, group=collision_groups["obstacle"]):
        self.position = Position(x, y)
        self.collision = CrateCollision(self.position, width, height, group)
        self.sprite = Sprite(self.position, Resources.Image.Drops.ammunition)

class PlayerCrate(Crate):
    def __init__(self, x, y, width, height, group=collision_groups["unit"]):
        #why is group unit and not obstacle, well, it's not an obstacle, but it moves for the player... so it's a unit kinda sorta?
        self.position = Position(x, y)
        self.collision = PlayerCrateCollision(self.position, width, height, group)
        self.sprite = Sprite(self.position, Resources.Image.Drops.ammunition)
        self.movement = Movement(self.position, 100)
        self.controller = PlayerController(self.movement)
        
if __name__ == "__main__":
    from game import*
    game = Game()

    stuffs = []
    for i in range(40):
        stuffs.append(Unit(randint(0,window.width), randint(0, window.height), 24))
    for i in range(20):
        stuffs.append(Crate(randint(0,window.width), randint(0, window.height), 32, 32))
    p = Player(300,300,24)
    p1 = Player(400,400,24)
    p2 = Player(600,600,24)
    pc = PlayerCrate(150,150,32,32)

    game.run()
    

"""
class Obstacle():
    collision_groups["obstacle"] = ["unit"] 

    def type_response(self, other):
        other.obstacle_response(self)

    def unit_response(self, unit):
        print "just standing here, majestic as fuck, but what do i get, some douche walked into me!" 


class Pillar(Obstacle, Radial):
    def __init__(self, x, y, radius, group=collision_groups["obstacle"]):
        super(Pillar, self).__init__(x, y, radius, group)
        
class Wall(Obstacle, Box):
    def __init__(self, x, y, width, height, group=collision_groups["obstacle"]):
        super(Wall, self).__init__(x, y, width, height, group)


#EXPLANATION
#collision_groups["bullet"] = ["unit", "obstacle"]
#"bullet" is the name of the group, ["unit", "obstacle"] is the mask of the group
#the mask is a list of names of other groups, and/or the group itself
#in this case, objects appended to the bullet group will check for collisions against objects in the unit and obstacle groups
#o respond to the specific case, once a bullet hit something, so either bullet hit a unit, or bullet hit an obstacle,
#the bullet will call other.type_response(bullet)
#let's say other is a unit, so the units implemented type_response, will call bullet.unit_response(other)
#or other is an obstacle, so the obstacles type_response will call bullet.obstacle_response(other)
#so now the bullet can implement whatever it wants to do in either case with its unit_response/obstacle_response method

class Bullet(Radial):
    collision_groups["bullet"] = ["unit", "obstacle"]
    #groups mentioned in a mask must have a type_response
    
    def __init__(self, x, y, radius, group=collision_groups["bullet"]):
        super(Bullet, self).__init__(x, y, radius, group)

    def unit_response(self, unit):
        print "bullet hit a unit"

    def obstacle_response(self, obstacle):
        print "sad bullet is sad... got stuck inside an obstacle :("


class Powerup(Radial):
    collision_groups["powerup"] = ["unit"]
    
    def __init__(self, x, y, radius, group=collision_groups["powerup"]):
        super(Powerup, self).__init__(x, y, radius, group)

    def unit_response(self, unit):
        print "%s got picked up by %s" % (self, unit)


#a unit might need more than one collision object... a multipart enemy creature thing
#for example...same for the sprite...
class CollisionObject(object):
    def __init__(self, position, collision_type, collision_group):

class PlayerCollision(object):#this would be a collision type and group
    collision_group["player"] = ["unit", "obstacle", "powerup"]
    def send_collision(self, other):
        #what i should call on their side, when i hit something
        other.on_player_collision(self)
        
    def on_unit_collision(self, unit):
        #what i should do, when i got hit
        
        pass
#massive brainfart    
class Player(object):
    def __init__(self):
        self.collision_object =         

class Anchor(object):
    def __init__(self, parent=False, followers=[]):
        if parent:
            print "yO"
            parent.followers.append(self)
        self.parent = parent
        self.followers = followers
        
    @property
    def x(self):
        return self.parent.x

    @x.setter
    def x(self, val):
        for follower in self.followers:
            follower.x = val
        
class Player(object):
    def __init__(self,
                 x,
                 y,
                 radius=36,
                 image=Resources.Image.player,
                 layer=render_groups["foreground"]):
        self.collision = Unit(x, y, radius)
        self.player_sprite = pyglet.sprite.Sprite(image, x, y, batch = batch, group = layer)
        self.player_anchor = Anchor(False, [self.player_sprite])
        self.gun_sprite = pyglet.sprite.Sprite(image, x, y, batch = batch, group = layer)
        self.gun_anchor = Anchor(self.player_anchor, [self.gun_sprite])
    
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
