import pyglet
from pyglet.gl import*
from random import randint, uniform, choice

from utils import*
from resources import*
from shared import*


class FadingSprite(pyglet.sprite.Sprite):
    def __init__(self, image, x, y, fade_in=1, full_for=1, fade_out=1, fps=60 ,full_opacity=255, scale=1, render_group=effects, blend_src = GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA):
        super(FadingSprite, self).__init__(image, x, y, batch=batch, group=render_group, blend_src = blend_src, blend_dest = blend_dest)
        self.rotation = randint(0, 359)
        self.scale = uniform(0.8, 1.2)*scale
        self.full_opacity = full_opacity
        self.full_for = full_for
        self.fps = float(fps)

        if fade_out > 0:
            self.tick_out = self.full_opacity / (self.fps*fade_out)
        else:
            self.tick_out = 0
        
        if fade_in > 0:
            self.tick_in = self.full_opacity / (self.fps*fade_in)
            self.opacity = 0
            pyglet.clock.schedule_interval_soft(self.fade_in, 1/self.fps)
        else:
            self.opacity = self.full_opacity
            pyglet.clock.schedule_once(self.start_fade_out, self.full_for)

    def fade_in(self, dt):
        self.opacity += self.tick_in
        if self.opacity >= self.full_opacity:
            self.opacity = self.full_opacity
            pyglet.clock.unschedule(self.fade_in)
            pyglet.clock.schedule_once(self.start_fade_out, self.full_for)

    def start_fade_out(self, dt):
        pyglet.clock.schedule_interval_soft(self.fade_out, 1/self.fps)
        
    def fade_out(self, dt):
        self.opacity -= self.tick_out
        if self.tick_out == 0 or self.opacity <= 0:
            self.opacity = 0
            pyglet.clock.unschedule(self.fade_out)

class FadingScalingSprite(FadingSprite):
    
    def fade_out(self, dt):
        self.opacity -= self.tick_out
        self.scale += 0.05
        if self.tick_out == 0 or self.opacity <= 0:
            self.opacity = 0
            pyglet.clock.unschedule(self.fade_out)

def add_flash(x, y, fade_in, fade_out, opacity = 255, scale = 1):
    return FadingSprite(Resources.Image.light, x, y, fade_in, 0, fade_out, 20, opacity, scale, effects)

def add_gun_flash(x, y):
    return FadingSprite(Resources.Image.light, x, y, 0.05, 0, 0.1, 20, 100, 1, effects)

def add_mine_flash(x, y):
    return FadingSprite(Resources.Image.light, x, y, 0.05, 0, 0.3, 20, 200, 2, effects)
def add_mine_light(x, y):
    return FadingSprite(Resources.Image.Drops.light, x, y, 0.1, 0.5, 0, 20, 200, 1, decals)

def add_terror(x = None, y = None):
    if x == None:
        x = randint(0, window.width)
    if y == None:
        y = randint(0, window.height)
    fade_in = uniform(0.1,1)
    fade_out = uniform(1,3)
    opacity = randint(30,200)
    return FadingSprite(Resources.Image.terror, x, y, fade_in, 0, fade_out, 5, opacity, 1, hud)

def add_blood_decal(x, y):
    return FadingSprite(choice(Resources.Image.Blood.large), x, y, 0, 30, 30, 3, 200, 1, decals)

def add_burned_decal(x, y):
    return FadingSprite(Resources.Image.burned, x, y, 0, 60, 30, 5, 240, 1, burned)

def add_trail(x, y, angle):
    trail = FadingScalingSprite(choice(Resources.Image.trail), x, y, 0.1, 0, 3, 15, 200, 1, effects)
    trail.rotation = angle + randint(-10,10)
    trail.scale = uniform(0.9, 1.1)
    return trail

def add_muzzle_smoke(x, y):
    trail = FadingScalingSprite(choice(Resources.Image.trail), x, y, 0.1, 0, 1.5, 7, 50, 1, effects)
    trail.scale = uniform(0.5, 1)
    return trail

def add_impact_smoke(x, y):
    trail = FadingScalingSprite(choice(Resources.Image.trail), x, y, 0.05, 0, 1.5, 7, 70, 1, effects)
    trail.scale = uniform(0.5, 1)
    return trail

class Particle(FadingScalingSprite):
    #and also moving

    def __init__(self, image, x, y, angle, velocity, friction, fade_in=1, full_for=1, fade_out=1, fps=60 ,full_opacity=255, scale=1, render_group=effects, blend_src = GL_SRC_ALPHA, blend_dest=GL_ONE_MINUS_SRC_ALPHA):
        super(Particle, self).__init__(image, x, y, fade_in, full_for, fade_out, fps, full_opacity, scale, render_group, blend_src, blend_dest)
        self.angle = angle
        self.velocity = velocity
        self.friction = friction

        pyglet.clock.schedule_interval_soft(self.animate, 1./fps)

    def animate(self, dt):
        self.x -= cos(self.angle)*(self.velocity*dt)
        self.y += sin(self.angle)*(self.velocity*dt)
        self.velocity *= pow(self.friction,dt)

    def fade_out(self, dt):
        self.opacity -= self.tick_out
        self.scale += 0.1
        if self.tick_out == 0 or self.opacity <= 0:
            self.opacity = 0
            pyglet.clock.unschedule(self.fade_out)
            pyglet.clock.unschedule(self.animate)
            
def add_impact_particle(x, y, angle):
    angle += uniform(-0.25, 0.25)
    velocity = randint(1200, 1400)
    friction = uniform(0.6, 0.8)
    fade_in = uniform(0.01, 0.03)
    full_for = uniform(0.03, 0.05)
    fade_out = uniform(0.03, 0.05)
    opacity = randint(155, 255)
    scale = uniform(0.3,0.6)
    return Particle(Resources.Image.particle, x, y, angle, velocity, friction, fade_in, full_for, fade_out, 60, opacity, scale)

def add_impact_particles(x, y, angle, count):
    for i in xrange(randint(count-2, count)):
        add_impact_particle(x, y, angle)
        
if __name__ == "__main__":   
    def test_flash(dt):
        add_gun_flash(randint(0, window.width),randint(0,window.height))
    def test_blood(dt):
        add_blood_decal(randint(0, window.width),randint(0,window.height))

    def stress_test():
        pyglet.clock.schedule_interval_soft(test_flash, 1./480)
        pyglet.clock.schedule_interval_soft(test_blood, 1./60)
    def real_test():   
        pyglet.clock.schedule_interval_soft(test_flash, 1./50)
        pyglet.clock.schedule_interval_soft(test_blood, 1./3)

    stress_test()
    #real_test()

    run_pyglet()
