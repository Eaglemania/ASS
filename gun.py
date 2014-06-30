import pyglet
from collisionobject import CollisionObject,DynamicObject
from math import *
from random import *
from decal import *
import unit, obstacle
 
from utils import*
from resources import*
from shared import*

from drops import explosion
from animatedsprite import add_blood_splash

class BulletType:
    def __init__(self, image, speed, radius, damage, pellets, spread, explosive = False):
        self.image = image
        self.speed = speed
        self.radius = radius
        self.damage = damage
        self.pellets = pellets
        self.spread = spread
        self.explosive = explosive
        
carbine_bullet_image = Resources.Image.bullet
carbine_bullet_type = BulletType(carbine_bullet_image, 2600, 8, 20, 1, 0)
shotgun_bullet_type = BulletType(carbine_bullet_image, 2300, 8, 15, 7, 0.12)
sniper_bullet_type = BulletType(carbine_bullet_image, 2800, 8, 100, 1, 0)
pdw_bullet_type = BulletType(carbine_bullet_image, 2500, 8, 10, 1, 0)
lmg_bullet_type = BulletType(carbine_bullet_image, 2500, 8, 14, 1, 0)
saiga_bullet_type = BulletType(carbine_bullet_image, 2400, 8, 12, 5, 0.07)
rpg_bullet_type = BulletType(carbine_bullet_image, 1800, 8, 150, 1, 0, True)

class GunSounds:
    def __init__(self, shoot, clip_in, clip_out, empty):
        self.shoot = shoot
        self.clip_in = clip_in
        self.clip_out = clip_out
        self.empty = empty

carbine_sounds = GunSounds(Resources.Audio.Gun.Carbine.shoot,
                           Resources.Audio.Gun.Carbine.clip_in,
                           Resources.Audio.Gun.Carbine.clip_out,
                           Resources.Audio.Gun.Carbine.empty)

shotgun_sounds = GunSounds(Resources.Audio.Gun.Shotgun.shoot,
                           Resources.Audio.Gun.Shotgun.clip_in,
                           Resources.Audio.Gun.Shotgun.clip_out,
                           Resources.Audio.Gun.Shotgun.empty)

sniper_sounds = GunSounds(Resources.Audio.Gun.Sniper.shoot,
                          Resources.Audio.Gun.Sniper.clip_in,
                          Resources.Audio.Gun.Sniper.clip_out,
                          Resources.Audio.Gun.Sniper.empty)

pdw_sounds = carbine_sounds
lmg_sounds = carbine_sounds
saiga_sounds = shotgun_sounds
rpg_sounds = sniper_sounds


class GunRecoil:
    def __init__(self, increasing_strength, decreasing_strength, cap):
        self.increasing_strength = increasing_strength
        self.decreasing_strength = decreasing_strength
        self.cap = cap

carbine_recoil = GunRecoil(0.01, 0.9, 30)
shotgun_recoil = GunRecoil(0.17, 0.96, 30)
sniper_recoil = GunRecoil(0.2, 0.97, 30)
pdw_recoil = GunRecoil(0.007, 0.9, 30)
lmg_recoil = pdw_recoil
saiga_recoil = GunRecoil(0.08, 0.91, 30)
rpg_recoil = GunRecoil(0.3, 0.98, 30)

class GunType:
    def __init__(self, rate_of_fire, automatic, mag_size, reload_time, lose_reload_ammo, bullet_type, recoil, accuracy, accuracy_move, sounds):
        self.rate_of_fire = rate_of_fire
        self.automatic = automatic
        self.mag_size = mag_size
        self.reload_time = reload_time
        self.lose_reload_ammo = lose_reload_ammo
        self.bullet_type = bullet_type
        self.recoil = recoil
        self.accuracy = accuracy
        self.accuracy_move = accuracy_move
        self.sounds = sounds

carbine_gun_type = GunType(700, True, 30, 1.2, True, carbine_bullet_type, carbine_recoil, 0.025, 0.02, carbine_sounds)
shotgun_gun_type = GunType(250, False, 7, 1.4, False, shotgun_bullet_type, shotgun_recoil, 0.13, 0.03, shotgun_sounds)
sniper_gun_type = GunType(100, False, 10, 2, True, sniper_bullet_type, sniper_recoil, 0.003, 0.07, sniper_sounds)
pdw_gun_type = GunType(1100, True, 25, 0.8, True, pdw_bullet_type, pdw_recoil, 0.08, 0.015, pdw_sounds)
lmg_gun_type = GunType(550, True, 100, 2.2, True, lmg_bullet_type, lmg_recoil, 0.01, 0.05, lmg_sounds)
saiga_gun_type = GunType(300, True, 12, 1.2, True, saiga_bullet_type, saiga_recoil, 0.05, 0.03, saiga_sounds)
rpg_gun_type = GunType(50, False, 1, 3, False, rpg_bullet_type, rpg_recoil, 0.05, 0.07, rpg_sounds) 

class Bullet(DynamicObject):
    
    def __init__(self,
                 bullet_type,
                 owner,
                 x,
                 y,
                 angle,
                 render_group = render_groups["foreground"],
                 collision_group = collision_groups["bullet"],
                 physic_ticks = 80):

        super(Bullet, self).__init__(bullet_type.image, x, y, bullet_type.radius, render_group, collision_group, physic_ticks )

        self.friction = 0.99
        
        self.angle = angle + uniform(-bullet_type.spread, bullet_type.spread)
        self.rotation = degrees(self.angle)
        self.speed = uniform(bullet_type.speed*0.99,bullet_type.speed*1.01)
        self.owner = owner
        self.bullet_type = bullet_type
        self.push(-self.rotation, self.speed)
        
        #if not bullet_type.explosive:
        #   self.check_collision()
        
        #will cause strange crash for explosive bullets that kill the owner on this first check)

    def loop(self, dt):
        if self.bullet_type.explosive:
            add_trail(self.x, self.y, self.rotation)
        super(Bullet, self).loop(dt)
                                
    def check_bounds(self):
        remove = False
        if self.x > window.width:
            remove = True
        elif self.x < 0:
            remove = True
        if self.y > window.height:
            remove = True
        elif self.y < 0:
            remove = True
        if remove:
            self.remove()
            
    def on_kill(self, victim):
        self.owner.on_kill(victim)
    
    def send_collision(self, obj):
        if isinstance(obj, unit.Unit):
            if randint(0, 100) < 50:
                add_blood_decal(obj.x, obj.y)
            if self.bullet_type.explosive:
                explosion(self,150,self.bullet_type.damage,1500,Resources.Audio.Drops.Mine.explosion)
            else:
                obj.damage(self.bullet_type.damage, self.owner)
                
                angle = -self.rotation
                ox = cos(angle * (pi/180)) * (obj.radius+self.radius+8)
                oy = sin(angle * (pi/180)) * (obj.radius+self.radius+8)

                add_blood_splash(self.x+ox, self.y+oy, self.rotation)
                
            self.remove()
        elif isinstance(obj, obstacle.Obstacle):
            play_sound(choice(Resources.Audio.Impact.stone), self.x, self.y, 0.1, 300, 1000)
            if self.bullet_type.explosive:
                explosion(self,150,self.bullet_type.damage,1500,Resources.Audio.Drops.Mine.explosion)
            else:
                #add_impact_particles(self.x, self.y, self.angle, 4)
                add_impact_smoke(self.x,self.y)
            self.remove()
            
                            
        
class Gun:
    def __init__(self, gun_type, owner, ammo_pool):
        self.gun_type = gun_type
        self.owner = owner
        self.ammo_pool = ammo_pool
        self.bullets_left = self.gun_type.mag_size
        self.ready_to_fire = True
        self.ready_to_reload = True
        self.help_reload = False

        
    def switch_to(self):
        play_sound(self.gun_type.sounds.clip_in, self.owner.x, self.owner.y, 0.3, 300, 1000)
        self.ready_to_reload = True
        self.ready_to_fire = True
        
    def switch_from(self):
        self.owner.gun = None
        pyglet.clock.unschedule(self.shoot)
        pyglet.clock.unschedule(self.make_ready)
        pyglet.clock.unschedule(self.reloaded)
        
    def make_ready(self, dt):
        self.ready_to_fire = True

    def shoot(self, dt):
        rotation = -self.owner.rotation
        ox = cos(rotation * (pi/180)) * (self.owner.radius+self.gun_type.bullet_type.radius+1)
        oy = sin(rotation * (pi/180)) * (self.owner.radius+self.gun_type.bullet_type.radius+1)
        x = self.owner.x+ox
        y = self.owner.y+oy
        
        play_sound(self.gun_type.sounds.shoot, x, y, 0.7, 300, 1000)
        add_gun_flash(x, y)
        add_muzzle_smoke(x, y)
        
        self.bullets_left -= 1
        angle = radians(self.owner.rotation) + (uniform(-1,1)*self.owner.accuracy())
        for pellet in range(self.gun_type.bullet_type.pellets):     
            Bullet(self.gun_type.bullet_type, self.owner, x, y, angle)
        if self.bullets_left <= 0:
            pyglet.clock.unschedule(self.shoot)
            
        self.owner.increase_recoil() 

    def pull_trigger(self):
        if self.ready_to_fire:
            self.ready_to_fire = False
            pyglet.clock.schedule_once(self.make_ready, 1./(self.gun_type.rate_of_fire/60.))

            if self.bullets_left > 0:
                self.shoot(1)
                if self.gun_type.automatic and self.bullets_left > 0:
                    pyglet.clock.schedule_interval(self.shoot, 1./(self.gun_type.rate_of_fire/60.))
            else:
                play_sound(self.gun_type.sounds.empty, self.owner.x, self.owner.y, 0.5, 300, 1000)
                if self.help_reload:
                    self.reload()
                else:
                    self.help_reload = True


    def release_trigger(self):
        pyglet.clock.unschedule(self.shoot)
    
    def reloaded(self, dt):
        play_sound(self.gun_type.sounds.clip_in, self.owner.x, self.owner.y, 0.5, 300, 1000)
        if self.ammo_pool < self.gun_type.mag_size:
            if self.bullets_left + self.ammo_pool <= self.gun_type.mag_size:
                self.bullets_left += self.ammo_pool
                self.ammo_pool = 0
            else:
                self.ammo_pool -= self.gun_type.mag_size - self.bullets_left
                self.bullets_left = self.gun_type.mag_size                
        else:
            if self.bullets_left + self.ammo_pool <= self.gun_type.mag_size:
                self.ammo_pool -= self.gun_type.mag_size
                self.bullets_left = self.gun_type.mag_size
            else:
                if self.gun_type.lose_reload_ammo == True:
                    self.ammo_pool -= self.gun_type.mag_size
                    self.bullets_left = self.gun_type.mag_size
                else:
                    self.ammo_pool -= self.gun_type.mag_size - self.bullets_left
                    self.bullets_left = self.gun_type.mag_size
        self.ready_to_reload = True
        self.ready_to_fire = True

    def reload(self):
        if self.ready_to_reload and self.ammo_pool > 0 and self.bullets_left < self.gun_type.mag_size:
            #print "reload"
            play_sound(self.gun_type.sounds.clip_out, self.owner.x, self.owner.y, 0.5, 300, 1000)
            self.help_reload = False
            self.ready_to_reload = False
            self.ready_to_fire = False
            pyglet.clock.unschedule(self.shoot)
            pyglet.clock.unschedule(self.make_ready)
            pyglet.clock.schedule_once(self.reloaded, self.gun_type.reload_time)
            self.owner.on_reload(self.gun_type.reload_time)
        

    def release(self):
        pyglet.clock.unschedule(self.shoot)
        pyglet.clock.unschedule(self.make_ready)
        pyglet.clock.unschedule(self.reloaded)

    
