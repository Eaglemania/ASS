"""
    info writing for dummies:

    What it does:
        Sets the game up, with all the other classes and whatnot.
        Also starting, re-starting and pausing the game.

    How to use:
        Import game, create it, call run.
        
"""
import pyglet
from resources import *
from shared import *
from collisiongroup import *

class EventSpammer(object):
    def __init__(self, state):
        self.set(state)
        window.push_handlers(self.on_key_press)
        
    def on_key_press(self, symbol, modifiers):
        if symbol == keys["spam_events"]:
            self.toggle()
            
    def set(self, state):
        self.state = state
        if state:
            pyglet.clock.schedule(self.spam)
        else:
            pyglet.clock.unschedule(self.spam)

    def toggle(self):
        self.set(not self.state)
        
    def spam(self, dt):
        pass

class FrameRateCounter(object):
    def __init__(self, state):
        self.display = pyglet.clock.ClockDisplay()
        self.set(state)
        window.push_handlers(self.on_key_press)

    def on_key_press(self, symbol, modifiers):
        if symbol == keys["draw_fps"]:
            self.toggle()

    def set(self, state):
        self.state = state
        if state:
            drawables.append(self.display)
        else:
            drawables.remove(self.display)

    def toggle(self):
        self.set(not self.state)

class Listener(object):
    def __init__(self):
        pyglet.options['audio'] = ('openal', 'silent')
        self.openal = pyglet.media.get_audio_driver().get_listener()
        self.openal.volume = 1
        self.openal.up_orientation = (0, -1, 0)
        self.openal.forward_orientation = (0, 0, 1)
        self.openal.position = (window.width/2, window.height/2,0)
        window.push_handlers(self.on_resize)

    def on_resize(self, width, height):
        self.openal.position = (width/2, height/2, 0)

class MusicPlayer(object):
    def __init__(self):
        self.loop = Resources.Audio.loop.play()
        self.loop.volume = 0.1
        self.loop.eos_action = "loop"

class Game(object):
    def __init__(self, draw_fps=True, spam_events=True):
        self.frame_rate_counter = FrameRateCounter(draw_fps)
        self.event_spammer = EventSpammer(spam_events)
        self.listener = Listener()
        self.music_player = MusicPlayer()
        
        window.push_handlers(self.on_draw)
        window.push_handlers(self.on_close)

        collision_groups.optimize()
        
        pyglet.clock.schedule(self.update)
   
    def update(self, dt):
        collision_groups.check()
    
    def on_draw(self):
        window.clear()
        
        for drawable in drawables:
            drawable.draw()

    def on_close(self):
        self.music_player.loop.pause()
    
    def run(self):
        pyglet.app.run()

