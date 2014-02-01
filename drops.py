import pyglet
from collisionobject import CollisionObject,StaticObject
import unit
from animatedsprite import add_explosion
from decal import add_blood_decal, add_mine_flash, add_mine_light, add_burned_decal
from random import choice, randint, uniform

from utils import*
from resources import*
from shared import*

def explosion(owner, radius, damage, push, sound):
    radius = float(radius)
    force_per_radius = push / radius
    damage_per_radius = damage / radius
    
    for obj in owner.objects_in_range(radius):
        if isinstance(obj, unit.Unit):
            add_blood_decal(obj.x, obj.y)
            
            angle = angle_between(owner, obj)
            dist = distance_between(owner, obj)

            obj.push(angle, push - (dist * force_per_radius))
            obj.velocity_x = 0
            obj.velocity_y = 0
            obj.damage(damage - (dist * damage_per_radius), owner)

    add_burned_decal(owner.x, owner.y)
    play_sound(sound, owner.x, owner.y)
    add_explosion(owner.x, owner.y)
    add_mine_flash(owner.x, owner.y)
    


class Mine(CollisionObject):
    
    def __init__(self,
                 image = Resources.Image.Drops.mine,
                 x = 0,
                 y = 0,
                 trigger_radius = 8,
                 trigger_sound = Resources.Audio.Drops.Mine.trigger,
                 explode_in = 0.5,
                 explosion_sound = Resources.Audio.Drops.Mine.explosion,
                 damage = 100,
                 effect_radius = 150,
                 push_force = 1500,
                 render_group = middleground,
                 collision_group = collision_objects):
        
        super(Mine, self).__init__(image, x, y, trigger_radius, render_group, collision_group)

        self.trigger_sound = trigger_sound
        self.explode_in = float(explode_in)
        self.explosion_sound = explosion_sound
        self.damage = float(damage)
        self.effect_radius = float(effect_radius)
        self.push_force = float(push_force)
        self.force_per_radius = self.push_force / self.effect_radius
        self.damage_per_radius = self.damage / self.effect_radius
        
        self.rotation = randint(0, 359)
        self.triggered = False

        self.collision_group.append(self)
        self.check_collision()

    def on_kill(self, victim):
        pass
    
    def trigger(self):
        self.triggered = True
        play_sound(self.trigger_sound, self.x, self.y, 1, 300, 1000)
        add_mine_light(self.x, self.y)
        pyglet.clock.schedule_once(self.explode, self.explode_in) 

    def explode(self, dt):
        explosion(self, self.effect_radius, self.damage, self.push_force, self.explosion_sound)
        self.remove()

    def release(self):
        pyglet.clock.unschedule(self.explode)
        super(Mine, self).release()
    
    def on_collision(self, obj):
        if isinstance(obj, unit.Unit):
            if not self.triggered:
                self.trigger()
        elif isinstance(obj, StaticObject):
            self.seperate(obj)

def add_mine(x = None, y = None):
    if x == None:
        x = randint(0, window.width)
    if y == None:
        y = randint(0, window.height)
    return Mine(x=x, y=y)

  
#just a heads up, there is a unit.heal(amount) method already
#####WIP - phyce
class Medkit(CollisionObject):
    
    def __init__(self,
                 image = Resources.Image.Drops.medkit,
                 x = 0,
                 y = 0,
                 pick_up_radius = 8,
                 pick_up_sound = Resources.Audio.Drops.medkit,
                 heal_amount = 200,
                 render_group = foreground,
                 collision_group = collision_objects):
        
        super(Medkit, self).__init__(image, x, y, pick_up_radius, render_group, collision_group)
        
        self.pick_up_sound = pick_up_sound
        self.heal_amount = heal_amount
        self.collision_group.append(self) 
        self.rotation = randint(0, 359)
        
        
    def on_collision(self, obj):
        if isinstance(obj, unit.Unit):
            play_sound(self.pick_up_sound, self.x, self.y)
            #add healing decals, a bunch of +'s.            
            obj.heal(self.heal_amount)
            self.remove()

def add_medkit(x = None, y = None):
    if x == None:
        x = randint(0, window.width)
    if y == None:
        y = randint(0, window.height)
    return Medkit(x=x, y=y)

class Ammunition(CollisionObject):
    
    def __init__(self,
                 image = Resources.Image.Drops.ammunition,
                 x = 0,
                 y = 0,
                 pick_up_radius = 8,
                 pick_up_sound = Resources.Audio.Drops.ammunition,
                 render_group = foreground,
                 collision_group = collision_objects):
        
        super(Ammunition, self).__init__(image, x, y, pick_up_radius, render_group, collision_group)
        
        self.pick_up_sound = pick_up_sound
        self.collision_group.append(self) 
        self.rotation = randint(0, 359)
        
    def on_collision(self, obj):
        if isinstance(obj, unit.Unit):
            play_sound(self.pick_up_sound, self.x, self.y)
            #add healing decals, a bunch of +'s.
            #Dunno if that thing below is supposed to work that way
            #eaglemia: adding ammo to the pool? yup
            #should be obj.gun.ammo_pool tho, obj beign the object the ammo is colliding with
            obj.gun.ammo_pool += obj.gun.gun_type.mag_size*2
            self.remove()

def add_ammunition(x = None, y = None):
    if x == None:
        x = randint(0, window.width)
    if y == None:
        y = randint(0, window.height)
    return Ammunition(x=x, y=y)

class SpeedBoost(CollisionObject):
    
    def __init__(self,
                 image = Resources.Image.Drops.speedboost,
                 x = 0,
                 y = 0,
                 pick_up_radius = 8,
                 pick_up_sound = Resources.Audio.Drops.medkit,
                 amount = 100,
                 duration = 10,
                 end_sound = Resources.Audio.Drops.medkit,
                 render_group = foreground,
                 collision_group = collision_objects):
        
        super(SpeedBoost, self).__init__(image, x, y, pick_up_radius, render_group, collision_group)
        
        self.pick_up_sound = pick_up_sound
        self.amount = amount
        self.duration = duration
        self.end_sound = end_sound
        self.collision_group.append(self) 
        self.rotation = randint(0, 359)

    def boost(self, obj):
        obj.max_speed += self.amount
        pyglet.clock.schedule_once(self.end, self.duration, obj)
        
    def end(self, dt, obj):
        obj.max_speed -= self.amount
        play_sound(self.end_sound, self.x, self.y)
        
    def on_collision(self, obj):
        if isinstance(obj, unit.Unit):
            play_sound(self.pick_up_sound, self.x, self.y)
            self.boost(obj)
            self.remove()
            
def add_speedboost(x = None, y = None):
    if x == None:
        x = randint(0, window.width)
    if y == None:
        y = randint(0, window.height)
    return SpeedBoost(x=x, y=y)

def random_drop(x=randint(0, window.width), y=randint(0, window.height), chance=50):
    if randint(0, 100) < chance:
        r = randint(0, 100)
        if r > 70:
            add_ammunition(x, y)
        elif r < 10:
            add_speedboost(x, y)
        else:
            add_medkit(x, y)

if __name__ == "__main__":
    def test_mine(dt):
        add_mine()
    def test_medkit(dt):
        add_medkit()
    def test_ammunition(dt):
        add_ammunition()

    from enemy import add_enemy
    def test_enemy(dt):
        e = add_enemy()
        e.health.max = 1000
        e.health.current = 1000

    def stress_test():
        pyglet.clock.schedule_interval_soft(test_mine, 1./10)
        pyglet.clock.schedule_interval_soft(test_medkit, 1./1)
        pyglet.clock.schedule_interval_soft(test_ammunition, 1./1)
        pyglet.clock.schedule_interval_soft(test_enemy, 10)
        add_enemy()
    def real_test():   
        pyglet.clock.schedule_interval_soft(test_mine, 3)
        pyglet.clock.schedule_interval_soft(test_medkit, 5)
        pyglet.clock.schedule_interval_soft(test_ammunition, 5)
        pyglet.clock.schedule_interval_soft(test_enemy, 60)
        add_enemy()
    def medkit_test():
        pyglet.clock.schedule_interval_soft(test_medkit, 1)
        pyglet.clock.schedule_once(test_enemy, 10)

    #medkit_test()
    stress_test()
    #real_test()

    run_pyglet()

