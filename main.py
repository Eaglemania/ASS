import pyglet, math
from pyglet.window import key
from pyglet.gl import *
 
from random import random,randint,uniform,choice
from math import atan2, degrees, pi, sin, cos, sqrt

from utils import*
from resources import*
from shared import *



window.set_mouse_cursor(pyglet.window.ImageMouseCursor(Resources.Image.Hud.cursor, 0,8))
bg = tiled_sprite(Resources.Image.background, 4, 3, batch, render_groups["background"])

from collisionobject import*
from decal import*
from unit import*
from enemy import*
from player import*
from gun import*
from animatedsprite import*
from hudelement import*
from drops import*
from obstacle import*
from game import*

    

game = Game()

###create some stuff for testing
player = Player(x=300, y=300)

def create_enemy():
    x = randint(0, window.width)
    y = randint(0, window.height)

    wx = randint(0, window.width)
    wy = randint(0, window.height)

    enemy = random_enemy()
    enemy.waypoint_x = wx
    enemy.waypoint_y = wy
    enemy.target = player
    enemy.push(0,1)
    return enemy

def spawn_enemy(dt):
    create_enemy()

def spawn_mine(dt):
    add_mine()

def spawner(dt):
    if len(collision_objects) < 100:
        if randint(0, 100) < 30:
            add_mine()
        else:
            create_enemy()
            
def terror(dt):
    add_terror()
            
terror_mode = False
def toggle_terror_mode():
    global terror_mode
    if terror_mode:
        terror_mode = False
        pyglet.clock.unschedule(spawner)
        pyglet.clock.unschedule(terror)
    else:
        terror_mode = True
        pyglet.clock.schedule_interval_soft(spawner, 1)
        pyglet.clock.schedule_interval_soft(terror, 1./10)


def on_key_press(symbol, modifiers):
    if symbol == 101:#e
        create_enemy()
    elif symbol == 109:#m
        add_mine()
    elif symbol == 104:#h
        player.heal(5000)
    elif symbol == 98:#b
        player.gun.ammo_pool += player.gun.gun_type.mag_size
    elif symbol == 32:#space
        wave_generator = WaveGenerator(2, 1, 6, 8)
    elif symbol == 113:#q
        player.move_to(randint(0, window.width),randint(0, window.height))
    #print symbol

window.push_handlers(on_key_press)

        
def random_level(enemies, mines, lms=[0,0,0]):
    for n in range(mines):
        add_mine()

    """
    size = 8
    for n in range(lms):
        size =* 2
        for i in n:
            Obstacle(Resources.Image.Obstacle.large, randint(0, window.width), randint(0, window.height), size)

    """

    for n in range(lms[0]):
        Obstacle(Resources.Image.Obstacle.large, randint(0, window.width), randint(0, window.height), 64)

    for n in range(lms[1]):
        Obstacle(Resources.Image.Obstacle.medium, randint(0, window.width), randint(0, window.height), 32)

    for n in range(lms[2]):
        Obstacle(Resources.Image.Obstacle.small, randint(0, window.width), randint(0, window.height), 16)

    for n in range(enemies):
        create_enemy()

def level():
    Obstacle(Resources.Image.Obstacle.large, 200, 200, 64)
    
    Obstacle(Resources.Image.Obstacle.medium, 270, 200, 32)
    Obstacle(Resources.Image.Obstacle.medium, 300, 200, 32)
    
    Obstacle(Resources.Image.Obstacle.medium, 200, 270, 32)
    Obstacle(Resources.Image.Obstacle.medium, 200, 300, 32)
    
    Obstacle(Resources.Image.Obstacle.large, 650, 150, 64)
    Obstacle(Resources.Image.Obstacle.large, 650, 200, 64)
    Obstacle(Resources.Image.Obstacle.large, 650, 100, 64)

#level()
random_level(0, 0, [5, 7, 9])

def reposition_listener(dt):
    listener.position=(player.x, player.y, 0)

EVENT_TEXTS = []

class EventText(pyglet.text.Label):
    def __init__(self, text, x, y, time=0, font_size=16, anchor_x='center', group=render_groups["hud"], batch=batch):
        super(EventText, self).__init__(text=text, x=x, y=y, font_size=font_size, anchor_x=anchor_x, group=group, batch=batch)
        self.time = time

        if time > 0:
            pyglet.clock.schedule_once(self.remove, time)

        EVENT_TEXTS.append(self)

    def remove(self, dt):
        self.delete()
        EVENT_TEXTS.remove(self)

EventText("Press SPACE to start waves", window.width/2, window.height/2, 5)

        
WAVE = 1

class WaveGenerator(object):
    def __init__(self, units, mines, spawn_time, wait_time):
        self.units = units
        self.mines = mines
        self.spawn_time = spawn_time
        self.wait_time = wait_time

        for n in xrange(int(units)):
            pyglet.clock.schedule_once(spawn_enemy, uniform(0,spawn_time))

        for n in xrange(int(mines)):
            pyglet.clock.schedule_once(spawn_mine, uniform(0,spawn_time))

        pyglet.clock.schedule_once(self.spawn_stop, int(spawn_time))
        pyglet.clock.schedule_once(self.wave_end, int(spawn_time+wait_time))
        pyglet.clock.schedule_interval_soft(terror, 1./10)

        EventText("Wave "+str(WAVE), window.width/2, int(window.height*0.8),3)
        #print "wave start"
        #print "units : "+str(int(units))
        #print "mines : "+str(int(mines))
        #print "spawn_time : "+str(int(spawn_time))
        #print "wait_time : "+str(int(wait_time))
    
    def spawn_stop(self, dt):
        pyglet.clock.unschedule(terror)
        #print "spawn stop"

    def wave_end(self, dt):
        global WAVE
        WAVE+=1
        #print "wave end"
        #start a new wave, very shitty balanced
        units = self.units*1.3
        mines = self.mines*1.1
        spawn_time = self.spawn_time*1.2
        wait_time = self.wait_time*1.1
        self = WaveGenerator(units,mines,spawn_time,wait_time)


class LevelGenerator(WaveGenerator): #lol sucks
    def __init__(self, units, mines, large, medium, small, spawn_time, clear_time):
        super(LevelGenerator, self).__init__(units, mines, spawn_time, clear_time)
        self.large = large
        self.medium = medium
        self.small = small
        self.obstacles = []
        
        for n in range(int(large)):
            self.obstacles.append(obstacle(Image.Obstacle.large, randint(0, window.width), randint(0, window.height), 64))

        for n in range(int(medium)):
            self.obstacles.append(obstacle(Image.Obstacle.medium, randint(0, window.width), randint(0, window.height), 32))

        for n in range(int(small)):
            self.obstacles.append(obstacle(Image.Obstacle.small, randint(0, window.width), randint(0, window.height), 16))

    def spawn_stop(self, dt):
        super(LevelGenerator, self).spawn_stop(dt)
        for obstacle in self.obstacles:
            obstacle.remove()

    def wave_end(self, dt):
        #redo meh
        units = self.units*1.3
        mines = self.mines*1.1
        large = self.large*1.1
        medium = self.medium*1.2
        small = self.small*1.3
        spawn_time = self.spawn_time*1.2
        wait_time = self.wait_time*1.1
        self = LevelGenerator(units,mines,large,medium,small,spawn_time,wait_time)

        
#level_generator = LevelGenerator(2, 1, 5, 4, 3, 6, 8)
#run stuf...
#pyglet.clock.schedule_interval_soft(reposition_listener, 1./60)
#^ sounds very bad
    
game.run()

