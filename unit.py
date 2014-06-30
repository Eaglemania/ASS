import pyglet
from collisionobject import CollisionObject, DynamicObject
from hudelement import Bar
from gun import *
from math import atan2, pi, degrees, sin, cos, radians
from random import choice
from namegen import generate
from obstacle import Obstacle

from utils import*
from resources import*
from shared import*
 
class Stat(object):
    def __init__(self, current, max):
        self.current = current
        self.max = max

    def current_percentage(self): #well not percentage... dunno
        return int(255 * float(self.current)/float(self.max))

class Unit(DynamicObject):
    #baseclass for units, to controll the unit either by ai or by keyboard sublcass this
    """
    for collision to work the unit must be added to and ONLY to collision_objects,
    there can not be any reference of the object outside of collision_objects or the unit won't get cleaned up properly
    """
    def __init__(self, image, x, y, radius, health, max_speed, render_group = foreground, collision_group = collision_objects): 
        super(Unit, self).__init__(image, x, y, radius, render_group, collision_group)        
        #stats
        self.health = Stat(health, health)
        #movement stuff
        self.sprinting = False
        self.crouching = False
        self.friction = 0.001
        self.max_speed = max_speed
        self.up = False
        self.left = False
        self.down = False
        self.right = False
        self.aim_x = 500
        self.aim_y = 500
        self.target = None
        #gun stuff
        self.accuracy_modifier = 1
        self.recoil = .0
        self.cooldown = 0
        
        self.guns = [Gun(carbine_gun_type, self, carbine_gun_type.mag_size*3),
                     Gun(shotgun_gun_type, self, shotgun_gun_type.mag_size*3),
                     Gun(sniper_gun_type, self, sniper_gun_type.mag_size*3),
                     Gun(pdw_gun_type, self, pdw_gun_type.mag_size*3),
                     Gun(lmg_gun_type, self, lmg_gun_type.mag_size*3),
                     Gun(saiga_gun_type, self, saiga_gun_type.mag_size*3),
                     Gun(rpg_gun_type, self, rpg_gun_type.mag_size*3)]
        
        self.gun = choice(self.guns)

        self.health_bar = Bar(stat = self.health, x = x, y = y-(self.height/2))

        #random name label
        gen = generate()
        self.name = gen.generate_name(7)
        self.label_offset = -50
        self.label = pyglet.text.Label(self.name, x=self.x, y=self.y+self.label_offset, batch=batch, group = hud, anchor_x="center")

        #walksound test
        self.walkcycle = 0

        self.collision_group.append(self)
        self.check_collision()
        self.push(0, 50)

    def sprint_on(self):
        self.accuracy_modifier += 0.3
        self.max_speed += 80
        self.sprinting = True
        
    def sprint_off(self):
        self.accuracy_modifier -= 0.3
        self.max_speed -= 80
        self.sprinting = False

    def crouch_on(self):
        self.accuracy_modifier -= 0.3
        self.max_speed -= 80
        self.crouching = True
        
    def crouch_off(self):
        self.accuracy_modifier += 0.3
        self.max_speed += 80
        self.crouching = False
    
    def loop(self, dt):
        super(Unit, self).loop(dt)
        
        self.controll(dt)

        self.decrease_recoil()

        #check if any of the movement flags are set, if so... add velocity
        if self.up:
            self.velocity_y += (self.max_speed*10) * dt
        elif self.down:
            self.velocity_y -= (self.max_speed*10) * dt
        if self.left:
            self.velocity_x -= (self.max_speed*10) * dt
        elif self.right:
            self.velocity_x += (self.max_speed*10) * dt
        #print self.velocity_x
        #restrict velocity to max_speed
        if self.velocity_x < -self.max_speed:
            self.velocity_x = -self.max_speed
        elif self.velocity_x > self.max_speed:
            self.velocity_x = self.max_speed
        if self.velocity_y < -self.max_speed:
            self.velocity_y = -self.max_speed
        elif self.velocity_y > self.max_speed:
            self.velocity_y = self.max_speed
        
        self.walkcycle += 1
        
        self.health_bar.update()

        self.look_at(self.aim_x, self.aim_y)
        
    def on_reload(self, reload_time):
        pass
    
    def on_move(self):
        #update health bar position
        self.health_bar.center_on(self.x, self.y-25)

        #update name label position
        self.label.x = int(self.x)
        self.label.y = int(self.y+self.label_offset)


        #!!!!!NEEDS DT but how????
        #walk step sounds LOL this works good for first try
        #also sounds like shit with a lot of units, as expected...
        if self.walkcycle >= 50 - max([abs(self.velocity_x),abs(self.velocity_y)])*0.11:
            play_sound(Resources.Audio.Unit.Step.stone, self.x, self.y, 0.15, 300, 1000)
            self.walkcycle = 0

    def on_collision(self, obj):
        super(Unit, self).on_collision(obj)
        if isinstance(obj, Unit):
            self.seperate(obj)
            self.add_force(obj)
            self.reduce_velocity()
        elif isinstance(obj, Obstacle):
            self.reduce_velocity()
            self.seperate(obj)
    
    def controll(self, dt):
        pass
        #to be overwriten with keyboard/ai controll
        #or just a very dumb npc

    def walking(self):
        if self.velocity_x != 0 or self.velocity_y != 0:
            return True
        return False

    def on_kill(self, victim):
        pass
    
    def damage(self, amount, damager = None):
        play_sound(Resources.Audio.Impact.flesh, self.x, self.y, 0.15, 300, 1000)
        self.health.current -= amount
        if self.health.current <= 0:
            damager.on_kill(self)
            self.die(damager)
            
    def heal(self, amount):
        self.health.current += amount
        if self.health.current > self.health.max:
            self.health.current = self.health.max

    def aim_angle(self):
        dx = self.aim_x - self.x
        dy = self.aim_y - self.y
        rads = atan2(-dy,dx)
        rads %= 2*pi
        return degrees(rads)
        
    def look_at(self, x, y):
        dx = x - self.x
        dy = y - self.y
        rads = atan2(-dy,dx)
        rads %= 2*pi
        self.rotation = degrees(rads)

    """
    prolly stupid but mb not ?
    for setting the movement flags in a subclass
    """
    def move_right(self, flag = True):
        if flag:
            self.right = True
            self.left = False
        else:
            self.right = False
    def move_left(self, flag = True):
        if flag:
            self.left = True
            self.right = False
        else:
            self.left = False
    def move_up(self, flag = True):
        if flag:
            self.up = True
            self.down = False
        else:
            self.up = False
    def move_down(self, flag = True):
        if flag:
            self.down = True
            self.up = False
        else:
            self.down = False

    def on_gun_switch(self):
        pass
    
    def switch_gun(self, to):
        self.on_gun_switch()
        self.gun.switch_from()
        self.gun = to
        self.gun.switch_to()

    def speed_x(self):
        return self.velocity_x + self.force_x
    def speed_y(self):
        return self.velocity_y + self.force_y
    
    def accuracy(self):
        return (self.recoil + self.gun.gun_type.accuracy + ((max([abs(self.speed_x()),abs(self.speed_y())]) * 0.015 )*self.gun.gun_type.accuracy_move))*self.accuracy_modifier
    
    def decrease_recoil(self):
        if self.cooldown > 5:
            self.recoil *= self.gun.gun_type.recoil.decreasing_strength
        else:
            self.cooldown += 1

    def increase_recoil(self):
        self.recoil += self.gun.gun_type.recoil.increasing_strength
        if self.recoil > self.gun.gun_type.recoil.cap:
            self.recoil = self.gun.gun_type.recoil.cap
        self.cooldown = 0

    def pull_trigger(self):
        self.gun.pull_trigger()

    def release_trigger(self):
        self.gun.release_trigger()
        
    def die(self, killer=None):
        self.on_death(killer)
        play_sound(Resources.Audio.Unit.death, self.x, self.y, 0.5, 300, 1000)
        self.remove()

    def kill(self, victim):
        victim.die(self)
        
    def on_death(self, killer):
        pass
    
    def release(self):
        self.gun.release()
        super(Unit, self).release()
        
    def clean(self,dt):
        #self.gun = None
        #self.guns = None
        try:
            self.label.delete()
        except AttributeError:
            #print "why"
            pass
        self.health_bar.clean()
        super(Unit, self).clean(dt)
