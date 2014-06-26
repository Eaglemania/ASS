import pyglet
from math import atan2, degrees, sqrt, pi, sin, cos, radians
from random import uniform, choice

#lazy functions
def RenderGroup(order, parent = None):
    return pyglet.graphics.OrderedGroup(order, parent)

def cutoff(val, cutoff):
    if -cutoff < val < cutoff:
        val = 0
    return val

def friction(val, friction):
    return val * friction

def calc_speed(val, friction, cutoff):
    val = friction(val, friction)
    val = cutoff(val, cutoff)
    return val

def tiled_sprite(img, cols, rows, batchy, groupy):
    l = []
    for col in range(cols):
        for row in range(rows):
            l.append( pyglet.sprite.Sprite(img, col*img.width, row*img.height, batch = batchy, group = groupy))
    return l

def clamp(minimum, value, maximum):
    return max(minimum, min(value, maximum))

def play_sound(sound, x, y, vol=1, min_dist=300, max_dist=1000):
    #if sound is a list of sounds, it'll choose randomly between them
    #min_dist and max_dist are strange values, default works somewhat tho
    if type(sound) == list:    
        sm = choice(sound).play()
    else:
        sm = sound.play()
    sm.position = (float(x),float(y),0.0)
    sm.volume = uniform(vol-0.1, vol)
    sm.pitch = uniform(0.9,1)
    sm.min_distance = min_dist
    sm.max_distance = max_dist
    return sm

def load_sequence(path, cols, rows, centered = True):
    image = pyglet.resource.image(path)
    grid = pyglet.image.ImageGrid(image, cols, rows)
    sequence = grid.get_texture_sequence()
    if centered:
        for img in sequence:
            img.anchor_x = img.width/2
            img.anchor_y = img.height/2
    return sequence

def load_animation(path, cols, rows, fps, looped = False, reverse = False, centered = True):
    #this should be given to a sprites image,
    #should handly playing from there
    sequence = load_sequence(path, cols, rows, centered)
    animation_frames = []
    for img in sequence:
        if img == sequence[-1] and not looped:
            animation_frame = pyglet.image.AnimationFrame(img, None)
        else:
            animation_frame = pyglet.image.AnimationFrame(img, 1./fps)
        animation_frames.append(animation_frame)
    if reverse:
        for img in reversed(sequence):
            animation_frame = pyglet.image.AnimationFrame(img, 1./fps)
            animation_frames.append(animation_frame)
            
    return pyglet.image.Animation(animation_frames)

def load_image(path, centered = True):
    image = pyglet.resource.image(path)
    if centered:
        image.anchor_x = image.width/2
        image.anchor_y = image.height/2
    return image

def load_cursor(path, centered = True):
    cursor = pyglet.resource.image(path)
    if centered:
        cursor.anchor_x = cursor.width/2
        cursor.anchor_y = -cursor.height/2
    return cursor
    

def load_audio(path, streaming = False):
    return pyglet.resource.media(path, streaming)

def angle_between(obj_a, obj_b):
    delta_x = obj_b.x - obj_a.x
    delta_y = obj_b.y - obj_a.y
    return degrees(atan2(delta_y, delta_x))

def distance_between(obj_a, obj_b):
    return sqrt( (obj_b.x - obj_a.x)**2 + (obj_b.y - obj_a.y)**2 )
