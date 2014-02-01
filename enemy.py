import pyglet
from unit import Unit
from player import Player
from utils import load_image
from random import randint, uniform, choice
from gun import Gun
from drops import random_drop

from utils import*
from resources import*
from shared import*

from decal import*
from animatedsprite import*

def col_with(x,y,r,obj):
    #circle to circle collision
    return (obj.x-x)**2 + (y-obj.y)**2 < (r+obj.radius)**2


def check_col(x,y,r,checker):
    #put all colliders in self.collisions, run on_collision (for both objects??)
    for obj in collision_objects:
        if obj != checker and col_with(x,y,r,obj):
            return angle_between_xy(x,y,obj), distance_between_xy(x,y,obj)
    return False, False
                
def angle_between_xy(x,y, obj_b):
    delta_x = obj_b.x - x
    delta_y = obj_b.y - y
    return degrees(atan2(delta_y, delta_x))

def distance_between_xy(x,y, obj_b):
    return sqrt( (obj_b.x - x)**2 + (obj_b.y - y)**2 )    

def intersects(x, y):
    for obj in collision_objects:
        if intersect([x,y],obj):
            return angle_between_xy(x,y,obj)
    return False

def intersect(p, obj):
    return (p[0] - obj.x)**2 + (p[1] - obj.y)**2 < obj.radius**2
        
class Enemy(Unit):   
    def __init__(self, image, x, y, radius, health, speed):
        super(Enemy, self).__init__(image, x, y, radius, health, speed)
        self.waypoint_timer = 0
        self.waypoint_x = 0
        self.waypoint_y = 0
        self.shoot_timer = 0
        self.target = None
        self.firing = False
        self.avoid_angle = 0
        #self.avoid_sprite = pyglet.sprite.Sprite(image, x, y, batch = batch, group = hud)
        #self.a_a_sprite = pyglet.sprite.Sprite(image, x, y, batch = batch, group = hud)
        #self.w_sprite = pyglet.sprite.Sprite(image, x, y, batch = batch, group = hud)
        
    def los_points(self, quality):
        ang = angle_between(self, self.target)
        angle = ang*(pi/180)
        c = cos(angle)
        s = sin(angle)
        distance = distance_between(self, self.target)
        
        for point in range(int(distance/quality)):
            yield [ self.x+(c*(point*quality)), self.y+(s*(point*quality)) ]
            
    def los(self, target):
        quality = 32
        for obj in collision_objects:
            if obj != self and not isinstance(obj, Player):
                    for point in self.los_points(quality):
                        if intersect(point, obj):
                            return obj
        return True

    def avoid(self):
        delta_x = self.speed_x()
        delta_y = self.speed_y()
        look_ahead = self.radius
        self.avoid_angle = degrees(atan2(delta_y, delta_x))
        
        ox = cos(self.avoid_angle * (pi/180)) * (look_ahead*2)
        oy = sin(self.avoid_angle * (pi/180)) * (look_ahead*2)
        x = self.x+ox
        y = self.y+oy
        #self.avoid_sprite.position = (x, y)
        col_a, col_d = check_col(x, y, look_ahead, self)
        
        if col_a:
            s = 1
            ox = cos(col_a * (pi/180)) * (s-(s*col_d))
            oy = sin(col_a * (pi/180)) * (s-(s*col_d))
            #self.a_a_sprite.position = (x+ox, y+oy)
            #print "wp", self.waypoint_x, self.waypoint_y, "offset", ox, oy
            self.waypoint_x += ox
            self.waypoint_y += oy
            #print "AVOID"
            return True
        return False
    

        #self.w_sprite.position = (self.waypoint_x, self.waypoint_y)
            
        #print self.avoid_angle, self.speed_x(), self.speed_y()
    
    def controll(self, dt):
        """
        all just tests here, ai and shit
        """
        self.avoid()
        #distance to the waypoint
        dx = abs(self.x - self.waypoint_x)
        dy = abs(self.y - self.waypoint_y)
        
        #go to the waypoint
        if dx > 50:
            if self.x - self.waypoint_x < -50:
                self.move_right()
            elif self.x - self.waypoint_x > 50:
                self.move_left()
        else:
            self.move_right(False)
            self.move_left(False)

        if dy > 50:
            if self.y - self.waypoint_y < -50:
                self.move_up()
            elif self.y - self.waypoint_y > 50:
                self.move_down()
        else:
            self.move_up(False)
            self.move_down(False)

        #get a new waypoint, if enough time has passed
        self.waypoint_timer += dt
        if self.waypoint_timer > 10:
            self.waypoint_timer = uniform(0,5)
            self.random_waypoint()
            self.random_aim()
            
        #if there is a valid target, aim at it
        if self.target != None:
            if self.target.health.current > 0:
                self.aim_x = self.target.x
                self.aim_y = self.target.y


                #and if self is not firing(checkin this for safety), check ammo 
                if not self.firing:
                    
                    self.shoot_timer += dt
                    
                    if self.gun.bullets_left <= 0:
                        self.gun.reload()

                    #and check for line of sight to the target, finally pull the trigger!
                    if self.shoot_timer > 2:
                        #now more like an action timer, checking for los
                        self.shoot_timer = uniform(0,1)
                        los = self.los(self.target)
                        if los == True:
                            self.pull_trigger()
                        else:
                            #print los
                            #can't see shit captain
                            pass
                            
                    
            else:
                self.target = None

    
    def random_waypoint(self):
        self.waypoint_x = randint(0, window.width)
        self.waypoint_y = randint(0, window.height)

    def random_aim(self):
        self.aim_x = randint(0, window.width)
        self.aim_y = randint(0, window.height)
          
    def on_death(self, killer):
        random_drop(self.x, self.y)
    
    def pull_trigger(self):
        super(Enemy, self).pull_trigger()
        self.firing = True
        pyglet.clock.schedule_once(self.release_trigger, uniform(0.5,1))
        
    def release_trigger(self, dt):
        self.firing = False
        super(Enemy, self).release_trigger()

    def release(self):
        pyglet.clock.unschedule(self.release_trigger)
        super(Enemy, self).release()

class Bomber(Enemy):

    def __init__(self, image, x, y, radius, health, speed):
        self.explode_in = float(1)
        self.explosion_damage = float(200)
        self.effect_radius = float(150)
        self.push_force = float(1500)
        self.force_per_radius = self.push_force / self.effect_radius
        self.damage_per_radius = self.explosion_damage / self.effect_radius
        self.triggered = False
        super(Bomber, self).__init__(image, x, y, radius, health, speed)
        
    def controll(self, dt):
        """
        ai for a charging unit, and trigger on player collision, detonation in 1 sec
        """

        #mb get new waypoint
        if self.target != None:
            self.waypoint_x = self.target.x
            self.waypoint_y = self.target.y
            self.aim_x = self.target.x
            self.aim_y = self.target.y
        else:
            self.w_counter +=1
            if self.w_counter > 300:
                self.waypoint_x = randint(0, window.width)
                self.waypoint_y = randint(0, window.height)
                self.aim_x = randint(0, window.width)
                self.aim_y = randint(0, window.height)

        #distance
        dx = abs(self.x - self.waypoint_x)
        dy = abs(self.y - self.waypoint_y)
        
        #go to waypoint
        if dx > 25:
            if self.x - self.waypoint_x < -25:
                self.move_right()
            elif self.x - self.waypoint_x > 25:
                self.move_left()
        else:
            self.move_right(False)
            self.move_left(False)

        if dy > 25:
            if self.y - self.waypoint_y < -25:
                self.move_up()
            elif self.y - self.waypoint_y > 25:
                self.move_down()
        else:
            self.move_up(False)
            self.move_down(False)

    def trigger(self):
        self.triggered = True
        play_sound(Resources.Audio.Drops.Mine.trigger, self.x, self.y, 1, 300, 1000)
        pyglet.clock.schedule_once(self.explode, self.explode_in) 

    def explode(self, dt):
        for obj in self.objects_in_range(self.effect_radius):
            if isinstance(obj, Unit):
                angle = angle_between(self, obj)
                dist = distance_between(self, obj)
                
                obj.push(angle, self.push_force - (dist * self.force_per_radius))
                obj.velocity_x = 0
                obj.velocity_y = 0
                add_blood_decal(obj.x, obj.y)
                obj.damage(self.explosion_damage - (dist * self.damage_per_radius), self)

        add_burned_decal(self.x, self.y)
        play_sound(Resources.Audio.Drops.Mine.explosion, self.x, self.y)
        add_explosion(self.x, self.y)
        add_mine_flash(self.x, self.y) 
        self.remove()

    def release(self):
        pyglet.clock.unschedule(self.explode)
        super(Bomber, self).release()
    
    def on_collision(self, obj):
        if not self.triggered:
            if isinstance(obj, Player):
                self.trigger()
        super(Bomber, self).on_collision(obj)

def add_enemy():
    if randint(0, 100) < 30:
        return Bomber(Resources.Image.Enemy.bomber, randint(0, window.width), randint(0, window.height), 24, 150, 100)
    else:
        return Enemy(Resources.Image.Enemy.shooter, randint(0, window.width), randint(0, window.height), 24, 100, 125)
