"""
    info writing for dummies:

    What it does:
        Stores stuff other stuff might need, like window, batch, groups.

    How to use:
        Import shared, get stuff!
        
"""
import pyglet
from pyglet.graphics import OrderedGroup
from pyglet.window.key import *

window = pyglet.window.Window(width = 1280, height = 720 , resizable = True, vsync = False)
batch = pyglet.graphics.Batch()

drawables = [batch]

render_groups = {}
render_groups["default"] = OrderedGroup(0)
render_groups["background"] = OrderedGroup(1)
render_groups["burned"] = OrderedGroup(2)
render_groups["middleground"] = OrderedGroup(3)
render_groups["decals"] = OrderedGroup(4)
render_groups["foreground"] = OrderedGroup(5)
render_groups["effects"] = OrderedGroup(6)
render_groups["hud"] = OrderedGroup(7)

keys = {}
keys["draw_fps"] = F
keys["spam_events"] = E
keys["up"] = W
keys["down"] = S
keys["left"] = A
keys["right"] = D
