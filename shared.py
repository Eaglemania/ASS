import pyglet
 
window = pyglet.window.Window(width = 1280, height = 720 , resizable = True, vsync = False)
batch = pyglet.graphics.Batch()

background = pyglet.graphics.OrderedGroup(0)
burned = pyglet.graphics.OrderedGroup(1)
middleground = pyglet.graphics.OrderedGroup(2)
decals = pyglet.graphics.OrderedGroup(3)
foreground = pyglet.graphics.OrderedGroup(4)
effects = pyglet.graphics.OrderedGroup(5)
hud = pyglet.graphics.OrderedGroup(6)

collision_objects = []

def run_pyglet(show_fps=True, max_fps=True):
    if max_fps:
        def max_fps(dt):
            pass
        pyglet.clock.schedule(max_fps)
        
    if show_fps:
        
        fps_display = pyglet.clock.ClockDisplay()
        @window.event
        def on_draw():
            window.clear()
            batch.draw()
            fps_display.draw()
    else:
        
        @window.event
        def on_draw():
            window.clear()
            batch.draw()

    pyglet.app.run()
