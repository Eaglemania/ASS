from utils import*

pyglet.options['audio'] = ('openal', 'silent')

class Resources:
    
    class Audio:
        loop = load_audio("resources/audio/loop.wav")
        
        class Drops:
            ammunition = load_audio("resources/audio/drops/ammunition.wav")
            medkit = load_audio("resources/audio/drops/medkit.wav")
            
            class Mine:
                explosion_1 = load_audio("resources/audio/drops/mine/explosion_1.wav")
                explosion_2 = load_audio("resources/audio/drops/mine/explosion_2.wav")
                explosion_3 = load_audio("resources/audio/drops/mine/explosion_3.wav")
                explosion = [explosion_1, explosion_2, explosion_3]
                trigger = load_audio("resources/audio/drops/mine/trigger.wav")
                
        class Gun:
            class Carbine:
                clip_in = load_audio("resources/audio/gun/carbine/clip_in.wav")
                clip_out = load_audio("resources/audio/gun/carbine/clip_out.wav")
                empty = load_audio("resources/audio/gun/carbine/empty.wav")
                shoot = load_audio("resources/audio/gun/carbine/shoot.wav")
            class Shotgun:
                clip_in = load_audio("resources/audio/gun/shotgun/clip_in.wav")
                clip_out = load_audio("resources/audio/gun/shotgun/clip_out.wav")
                empty = load_audio("resources/audio/gun/shotgun/empty.wav")
                shoot = load_audio("resources/audio/gun/shotgun/shoot.wav")
            class Sniper:
                clip_in = load_audio("resources/audio/gun/sniper/clip_in.wav")
                clip_out = load_audio("resources/audio/gun/sniper/clip_out.wav")
                empty = load_audio("resources/audio/gun/sniper/empty.wav")
                shoot = load_audio("resources/audio/gun/sniper/shoot.wav")
    
        class Impact:
            flesh_1 = load_audio("resources/audio/impact/flesh_1.wav")
            flesh_2 = load_audio("resources/audio/impact/flesh_2.wav")
            flesh_3 = load_audio("resources/audio/impact/flesh_3.wav")
            flesh_4 = load_audio("resources/audio/impact/flesh_4.wav")
            flesh_5 = load_audio("resources/audio/impact/flesh_5.wav")
            flesh = [flesh_1, flesh_2, flesh_3, flesh_4, flesh_5]
            stone_1 = load_audio("resources/audio/impact/stone_1.wav")
            stone_2 = load_audio("resources/audio/impact/stone_2.wav")
            stone_3 = load_audio("resources/audio/impact/stone_3.wav")
            stone = [stone_1, stone_2, stone_3]
            
        class Unit:
            death_1 = load_audio("resources/audio/unit/death/death_1.wav")
            death_2 = load_audio("resources/audio/unit/death/death_2.wav")
            death_3 = load_audio("resources/audio/unit/death/death_3.wav")
            death_4 = load_audio("resources/audio/unit/death/death_4.wav")
            death_5 = load_audio("resources/audio/unit/death/death_5.wav")
            death = [death_1, death_2, death_3, death_4, death_5]

            class Step:
                stone_1 = load_audio("resources/audio/unit/step/stone_1.wav")
                stone_2 = load_audio("resources/audio/unit/step/stone_2.wav")
                stone_3 = load_audio("resources/audio/unit/step/stone_3.wav")
                stone = [stone_1, stone_2, stone_3]
   
    class Image:
        background = load_image("resources/image/background.png", False)
        bullet = load_image("resources/image/bullet.png")
        burned = load_image("resources/image/burned.png")
        explosion = load_animation("resources/image/explosion.png", 4, 4, 20)
        light = load_image("resources/image/light.png")
        player = load_image("resources/image/player.png")
        terror = load_image("resources/image/terror.png")
        trail = load_sequence("resources/image/trail.png", 2, 2)
        particle = load_image("resources/image/particle.png")
        class Blood:
            large = load_sequence("resources/image/blood/large.png", 4, 4)
            splash = load_animation("resources/image/blood/splash.png", 1, 8, 30)
            
        class Drops:
            ammunition = load_animation("resources/image/drop/ammunition.png", 2, 3, 12, True, True)
            medkit = load_animation("resources/image/drop/medkit.png", 2, 3, 12, True, True)
            mine = load_image("resources/image/drop/mine.png")
            light = load_image("resources/image/drop/light.png")
            speedboost = load_animation("resources/image/drop/speedboost.png", 2, 3, 12, True, True)
            
        class Enemy:
            shooter = load_image("resources/image/enemy/shooter.png")
            bomber = load_image("resources/image/enemy/bomber.png")

        class Hud:
            bar = load_image("resources/image/hud/bar.png")
            border = load_image("resources/image/hud/border.png")
            cursor = load_cursor("resources/image/hud/cursor.png")
        
        class Obstacle:
            small = load_image("resources/image/obstacle/small.png")
            medium = load_image("resources/image/obstacle/medium.png")
            large = load_image("resources/image/obstacle/large.png")
