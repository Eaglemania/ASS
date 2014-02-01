import pyglet
from pyglet.gl import*
from unit import Unit
from gun import Gun
from math import pi, sin, cos
from utils import load_image
from random import randint

from utils import*
from resources import*
from shared import*

glEnable(GL_BLEND)
 
class PlayerUnitHandlers(object):
    def __init__(self, player):
        self.player = player
        
    def on_key_press(self, symbol, modifiers):
        if symbol == 119:#w
            self.player.up = True
        elif symbol == 115:#s
            self.player.down = True
        elif symbol == 97:#a
            self.player.left = True
        elif symbol == 100:#d
            self.player.right = True
        elif symbol == 114:#r
            self.player.gun.reload()
        #weapon keys 1,2,3,...
        for i in range(len(self.player.guns)):
            if symbol == 49+i:
                self.player.switch_gun(self.player.guns[i])

        if modifiers == 17:#shift
            if not self.player.sprinting:
                self.player.sprint_on()
        elif modifiers == 18:#ctrl
            if not self.player.crouching:
                self.player.crouch_on()
        #print modifiers
    
    def on_key_release(self, symbol, modifiers):
        if symbol == 119:#w
            self.player.up = False
        elif symbol == 115:#s
            self.player.down = False
        elif symbol == 97:#a
            self.player.left = False
        elif symbol == 100:#d
            self.player.right = False

        #print modifiers
        if modifiers != 17:#shift
            #print "yop"
            if self.player.sprinting:
                #print "so richtig"
                self.player.sprint_off()
        if modifiers != 18:#ctrl
            if self.player.crouching:
                self.player.crouch_off()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        current_gun = self.player.guns.index(self.player.gun)
        if scroll_y > 0:
            current_gun += 1
            if current_gun >= len(self.player.guns):
                current_gun = 0
            self.player.switch_gun(self.player.guns[current_gun])
        else:
            current_gun -= 1
            if current_gun < 0:
                current_gun = len(self.player.guns)-1
            self.player.switch_gun(self.player.guns[current_gun])
                                                    
    def on_mouse_motion(self, x, y, dx, dy):
        self.player.aim_x = x
        self.player.aim_y = y
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.player.aim_x = x
        self.player.aim_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        self.player.aim_x = x
        self.player.aim_y = y
        if button == 1:#left
            self.player.pull_trigger()
        elif button == 4:#right
            self.player.gun.reload()
        
    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1:
            self.player.release_trigger()

class Player(Unit):
    def __init__(self,
                 image = Resources.Image.player,
                 x = 0,
                 y = 0,
                 radius = 24,
                 health = 1000,
                 max_speed = 150):
        super(Player, self).__init__(image, x, y, radius, health, max_speed)
        #keyboard & mouse handlers
        self.handlers = PlayerUnitHandlers(self)
        window.push_handlers(self.handlers)
        
        #player specific stuff
        self.crosshair = None
        self.guide = None
        self.ammo_text = pyglet.text.Label(text = str(self.gun.bullets_left) + "/" + str(self.gun.ammo_pool), x = self.x, y = self.y, batch = batch, group = hud, anchor_x='center')
        self.score = 0
        self.score_text = pyglet.text.Label(text = "Kills: " + str(self.score), x = 5, y = 5, batch = batch, group = hud)
        self.reload_bar = None
        self.reloading_time = 0
        
    def loop(self, dt):
        super(Player, self).loop(dt)
        self.update_crosshair()
        #self.update_guide()
        self.update_ammo_text()

    def on_kill(self, victim):
        self.increase_score(1)

    def increase_score(self, amount):
        self.score += amount
        self.score_text.text = "Kills: " + str(self.score)

    def update_ammo_text(self):
        self.ammo_text.x = int(self.x)
        self.ammo_text.y = int(self.y-70)
        self.ammo_text.text = str(self.gun.bullets_left) + "/" + str(self.gun.ammo_pool)

    #circle
    def update_crosshair(self):
        x = self.aim_x
        y = self.aim_y
        dx1 = abs(x - self.x)
        dy1 = abs(y - self.y)

        radius = 4 + ((dx1+dy1)*3) * ((self.accuracy())*0.2)#dunno but looks right
        
        iterations = int(0.15*radius*pi)+8
        s = sin(2*pi / iterations)
        c = cos(2*pi / iterations)
         
        dx, dy = radius, 0
        dx1, dy1 = radius+3, 0
         
        vertices = []
        for i in range(iterations+1):
            vertices.extend([x+dx, y+dy])
            dx, dy = (dx*c - dy*s), (dy*c + dx*s)
            vertices.extend([x+dx1, y+dy1])
            dx1, dy1 = (dx1*c - dy1*s), (dy1*c + dx1*s)
            
        count = len(vertices)/2
        if self.crosshair != None:
            self.crosshair.delete()
            
        p = self.health.current_percentage()
        red = 255-p
        green = p
        self.crosshair = batch.add(count, GL_QUAD_STRIP, hud, ('v2f', vertices), ('c4B', (red, green, 0, 255)*count))

##    #squares fuck horrible
##    def update_crosshair(self):
##        x = self.aim_x
##        y = self.aim_y
##        dx = abs(x - self.x)
##        dy = abs(y - self.y)
##
##        radius = 4 + ((dx+dy)*3) * ((self.accuracy())*0.2)#dunno but looks right
##        
##        iterations = 4
##        
##        s = sin(2*pi / iterations)
##        c = cos(2*pi / iterations)
##         
##        dx, dy = radius, 0.0
##         
##        vertices = []
##        for i in range(iterations):
##            x1=x+dx
##            y1=y+dy
##
##            vertices.append([x1,y1])
##            
##            dx, dy = (dx*c - dy*s), (dy*c + dx*s)
##
##        #print vertices
##        t = 2
##        l = 20
##
##        dx, dy = vertices[0]
##        a = [dx,dy+t,
##             dx,dy-t,
##             dx+l,dy-t,
##             dx+l,dy+t]
##
##        dx, dy = vertices[1]
##        b = [dx-t,dy+l,
##             dx-t,dy,
##             dx+t,dy,
##             dx+t,dy+l]
##
##        dx, dy = vertices[2]
##        c = [dx-l,dy+t,
##             dx-l,dy-t,
##             dx,dy-t,
##             dx,dy+t]
##
##        dx, dy = vertices[3]
##        d = [dx-t,dy,
##             dx-t,dy-l,
##             dx+t,dy-l,
##             dx+t,dy]
##        
##        #print vertices
##        vertices = []
##        vertices.extend(a)
##        vertices.extend(b)
##        vertices.extend(c)
##        vertices.extend(d)
##        
##        count = len(vertices)/2
##        if self.crosshair != None:
##            self.crosshair.delete()
##            
##        p = self.health.current_percentage()
##        red = 255-p
##        green = p
##        self.crosshair = batch.add(count, GL_QUADS, hud, ('v2f', vertices), ('c4B', (red, green, 0, 255)*count))

    def update_guide(self):
        vertices = [int(self.x), int(self.y), int(self.aim_x), int(self.aim_y)]
        if self.guide != None:
            self.guide.delete()
        self.guide = batch.add(2, GL_LINES, hud, ('v2i', vertices))

    def update_reload_bar(self, dt, reload_time, iterations):
        #print dt, reload_time
        self.reloading_time += dt
        x = self.aim_x
        y = self.aim_y
        dx1 = abs(x - self.x)
        dy1 = abs(y - self.y)
        radius = 5 + ((dx1+dy1)*3) * ((self.accuracy())*0.2)

        s = sin(2*pi / iterations)
        c = cos(2*pi / iterations)
         
        dx, dy = 0, radius
         
        vertices = [x,y]
        for i in range( int(    (self.reloading_time/reload_time)   *iterations)     +1):
            vertices.extend([x+dx, y+dy])
            dx, dy = (dx*c + dy*s), (dy*c - dx*s)

        count = len(vertices)/2
        if self.reload_bar != None:
            self.reload_bar.delete()
            
        self.reload_bar = batch.add(count, GL_TRIANGLE_FAN, hud, ('v2f', vertices), ('c4B', (255,255,255,80)*count))

        if self.reloading_time > reload_time:
            self.reloading_time = 0
            self.reload_bar.delete()
            self.reload_bar = None
            pyglet.clock.unschedule(self.update_reload_bar)

    def on_reload(self, reload_time):
        reload_time = float(reload_time)
        iterations = 128
        self.reload_bar = None
        pyglet.clock.schedule_interval_soft(self.update_reload_bar, reload_time/iterations, reload_time, iterations)

    def on_gun_switch(self):
        if self.reload_bar != None:
            self.reloading_time = 0
            pyglet.clock.unschedule(self.update_reload_bar)
            self.reload_bar.delete()
            self.reload_bar = None

    def release(self):
        window.remove_handlers(self.handlers)
        super(Player, self).release()

    def clean(self, dt):
        try:
            self.ammo_text.delete()
            self.crosshair.delete()
            self.guide.delete()
        except AttributeError:
            pass
            #print "why"
        except AssertionError:
            print "new why"
            pass
        
        super(Player, self).clean(dt)
