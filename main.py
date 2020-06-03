#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Servaas & Lennart
"""

import pygame as pg
import physics_engine as pe
from physics_engine import Physics_Manager, Physics_Object, Rigid_Body, Vector2, Render_Image, Render_Circle, Image_Manager, draw_text, Ray, Sound_Manager, resource_path,  blit_rotate
import random as rd
import math
import os
import inspect
import sys

class Game_State():
    """Manages and updates game, root source of all calls"""
    def __init__(self):
        
        Game_Object.game_state = self

        self.game_objects = []
        self.fps = 60

        self.high_score = 0
        self.asteroid_index = 1
        self.running = True

        self.init_pygame()
        self.main_menu()

    def main_menu(self):
        """Spawns main menu, starts music etc."""
        self.image_manager = Image_Manager(image_folder= "images", asteroid_path = "images/asteroids")
        self.sound_manager = Sound_Manager(sound_folder= "sounds")
        pg.mixer.music.load(resource_path("music/battletheme.mp3"))
        start_image = self.image_manager.images["Pytroid"]
        start_image = pg.transform.scale(start_image, (self.widthscreen, self.heightscreen))
        pg.mixer.music.play(loops = -1)
        while True:
            for event in pg.event.get():
                self.handle_event(event)
                if event.type == pg.KEYDOWN:
                    self.start_game()

            self.screen.blit(start_image, [0, 0])
            pg.display.flip()

    def start_game(self):    
        """Starts the game after player initiates from start screen"""
        self.clock = pg.time.Clock()           
        self.physics_manager = Physics_Manager(self.screen)
        self.level_manager = Level_Manager()
        self.asteroid_manager = Asteroid_Manager() #TODO: Move to level_manager
        self.enemy_manager = Enemy_Manager() #TODO: Move to level_manager
        
        high_score_doc = open(resource_path("high_score.txt"), 'r+')
        self.high_score = int(float(high_score_doc.read()))
        high_score_doc.close()
        
        self.health_bar = Bar((self.widthscreen/3,20), (self.widthscreen/2, self.heightscreen*0.95), True, 100)
        self.missile_bar = Bar((self.widthscreen/8,10), (self.widthscreen/5, self.heightscreen*0.95), True, background_color=(169,169,169), bar_color=(0,0,0))
        self.railgun_bar = Bar((self.widthscreen/8,10), (self.widthscreen - self.widthscreen/5, self.heightscreen*0.95), True, background_color=(100,100,255), bar_color=(0,0,255))
        
        self.player = SpaceShip()

        self.points_total = 0
        
        self.stats = Text_Stats()

        self.background_image = self.image_manager.images["Andromeda"]
        self.the_image = pg.transform.scale(self.background_image, (self.widthscreen,self.heightscreen))

        self.update()

    def init_pygame(self):
        pg.init()
        size = pg.display.list_modes()[0]
        self.screen = pg.display.set_mode(size, pg.FULLSCREEN)
        self.widthscreen, self.heightscreen = pg.display.get_surface().get_size()

    def remove_children(self, game_object):
        members = inspect.getmembers(game_object)
        for member in members:
            if not member[0].startswith('_'):
                typ = type(member[1])
                is_subclass = issubclass(type(member[1]), Game_Object)
                if member[1] != game_object and is_subclass:
                    #self.remove_children(member[1]) #Leads to recursion, if added back solution is to add an expetion for parent attribute because currently: parent --> healthmanager --> parent --> healthmanager --> ...
                    try:
                        if member[1].parent == game_object:
                            self.game_objects.remove(member[1])
                    except:
                        pass

    def remove_game_object(self, game_object):
        #Clean up special lists
        if hasattr(game_object, 'physics_object'):
            self.physics_manager.physics_objects.remove(game_object.physics_object)
        if hasattr(game_object, 'rigid_body'):
            self.physics_manager.rigid_bodies.remove(game_object.rigid_body)
        if hasattr(game_object, 'render_image'):
            self.physics_manager.render_images.remove(game_object.render_image)
        if hasattr(game_object, 'render_circle'):
            self.physics_manager.render_circles.remove(game_object.render_circle)

        #Clean up gameobjects
        self.remove_children(game_object)
        self.game_objects.remove(game_object)

    def handle_event(self, event):
        """Quits the game"""
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()   

    def local_update_game_objects(self):
        """Calls all local update functions to update all game_objects"""
        for game_object in self.game_objects:
            if hasattr(game_object, "local_update"):
                game_object.local_update()
        return

    def game_over(self):
        """Spawns game over screen, handles end of the game and gives player the option to stop/continue"""
        game_over_image = self.image_manager.images["game over"]
        game_over_image = pg.transform.scale(game_over_image, (self.widthscreen, self.heightscreen))
        
        if self.points_total >= self.high_score:
            with open(resource_path("high_score.txt"), 'w') as filetowrite:
                filetowrite.write(str(self.points_total))
            self.high_score = self.points_total
        while True:
            self.screen.blit(game_over_image, [0, 0])
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_n:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_y:
                    for asteroid in self.asteroid_manager.asteroids:
                        asteroid.zero_hp()
                    for enemy in self.enemy_manager.enemies:
                        enemy.zero_hp()
                    self.remove_game_object(self.player)
                    self.player = SpaceShip()
                    self.points_total = 0
                    self.level_manager.level_number = 0
                    self.level_manager.time = 0
                    return
     
    def update(self):
        while self.running:
            self.dt = self.clock.tick(self.fps)
            self.screen.blit(self.the_image, [0, 0])
            for event in pg.event.get():
                self.handle_event(event)

            pg.event.pump()

            self.local_update_game_objects()

            self.physics_manager.update_all(self.dt)

            pg.display.flip()
    
class Game_Object():
    """Game_Objects puts all object in the game state in order to have good oversight,
    makes sure game objects are removed if needed."""
    game_state = None

    def __init__(self):
        if self.game_state != None:
            self.game_state.game_objects.append(self)
            self.removed = False

    def remove_self(self, lists_references = None):
        if not self.removed:
            self.removed = True
            self.game_state.remove_game_object(self)

            if lists_references != None:
                for lists_reference in lists_references:
                    lists_reference.remove(self)

class Level_Manager(Game_Object):
    """Sets properties of the different levels, makes sure there are no limits"""
    def __init__(self, frequency = 200, level_number = 0, level_time = 15000, level_prop = 1, asteroids = 20):
        Game_Object.__init__(self)

        self.level_number = level_number
        self.level_prop = level_prop
        
        self.level_time = level_time

        self.time = level_time

        self.current_level = Level()

    def update_level(self):
        #set level time of 
        if self.time >= self.level_time:
            self.level_number += 1
            self.time = 0
            asteroid_side = 1
            asteroid_number = 20

            #set amount of asteroids
            if self.level_number <= 3:
                asteroid_number = 20
                enemy_number = 0
            elif (3 < self.level_number <= 5):
                asteroid_number = 30
                enemy_number = 1 
            else:
                asteroid_number = 30 + (self.level_number*5-5)
                enemy_number = 1 + int((self.level_number-5)/2)

            #set direction of asteroids
            if self.level_number < 3:
                random = False
            elif (3 <= self.level_number < 5):
                random = True
            else:
                random  = rd.choice([True, False])

            #set sides at which asteroid appears
            if (self.level_number%1 == 0) or (self.level_number == 0):
                asteroid_side = 1
            if self.level_number%2 == 0:
                asteroid_side = 2
            if self.level_number%3 == 0:
                asteroid_side = 4
                
            #asteroid_frequency
            if asteroid_number != 0:
                self.frequency = int(self.level_time)/int(asteroid_number)*0.9

            self.current_level = Level(asteroid_side = asteroid_side, random = random, asteroid_number = asteroid_number, frequency=self.frequency, enemy_number=enemy_number)

        else:
            self.time += self.game_state.dt

    def local_update(self):
        self.update_level()
        self.game_state.asteroid_manager.manage_asteroid_spawn()
        self.game_state.enemy_manager.manage_enemy_spawn()

class Level():
    """Made to make it easy to store and call level properties"""
    def __init__(self, asteroid_number = 0, random = False, asteroid_side = 1, frequency = 0, enemy_number = 0):
        self.asteroid_number = asteroid_number
        self.frequency = frequency
        self.random = random
        self.asteroid_side = asteroid_side
        self.enemy_number = enemy_number

class Enemy_Manager(Game_Object):
    """Manages spawn and maximum amount of enemies, communicates with level and level manager
    to determine the amount of enemies, spawn time etc."""
    def __init__(self):
        Game_Object.__init__(self)
        self.enemies = []
        self.enemy_time = 0
        self.enemy_frequency = 0
    
    def enemy_generator(self):
        enemy = Enemy()
        return enemy
    
    def manage_enemy_spawn(self):
        current_level = self.game_state.level_manager.current_level        
        if current_level.enemy_number > len(self.enemies) and self.enemy_time > self.enemy_frequency:
            enemy = self.enemy_generator()
            self.enemies.append(enemy)
            self.enemy_frequency = rd.randint(3000,15000)
            self.enemy_time = 0
        else:
            self.enemy_time += self.game_state.dt

class Asteroid_Manager(Game_Object):
    """Manages spawn and removal of asteroids, creates asteroids of different size, different aesthetic,
    speed etc. Communicates with level_manager to regulate the amount of asteroids"""
    def __init__(self):
        Game_Object.__init__(self)
        self.astroid_time = 0
        self.asteroids = []
        self.asteroid_index = 1

    def asteroidGenerator(self, number_ast, waveprop, random): #set constant initially, increase if wave functionality added
        #generates the asteroids
        if random == True:
            angle = math.radians(rd.randint(-40, 40)) #angle between x and y component velocity
        else:
            angle = 0   

        rand = rd.randint(0,100)/100
        mass = 70 + (330)*rand**3
        radius = int(mass/4) #with average mass 80, radius average asteroid 20 pixels
        vel_int = rd.randint(15,30)/mass #standard total momentum of 400 , avg 50 velocity in pixel/second,

        widthscreen = self.game_state.widthscreen
        heightscreen = self.game_state.heightscreen

        lin_size = int(radius * 2 *1.4)
        size = (lin_size, lin_size)
        margin = 0
        #spawns asteroids at different sides of the screen for different levels (waveprop)
        if number_ast%waveprop == 0:
            pos = Vector2(widthscreen + lin_size/2 - margin, rd.randint(0,heightscreen)) #right screen border
            coord = Vector2.unpack(pos)
            if coord[1] < 0.5*heightscreen:
                vel = Vector2(-vel_int*math.cos(angle), vel_int*math.sin(abs(angle)))
            else:
                vel = Vector2(-vel_int*math.cos(angle), -vel_int*math.sin(abs(angle)))
        elif number_ast%waveprop == 1:
            pos = Vector2(0 - lin_size/2 + margin, rd.randint(0,heightscreen)) #left screen border #right screen border
            coord = Vector2.unpack(pos)
            if coord[1] < 0.5*heightscreen:
                vel = Vector2(vel_int*math.cos(angle), vel_int*math.sin(abs(angle)))
            else:
                vel = Vector2(vel_int*math.cos(angle), -vel_int*math.sin(abs(angle)))
        elif number_ast%waveprop == 2:
            pos = Vector2(rd.randint(0,widthscreen), 0 - lin_size/2 + margin) #left handed coordinate system, [x,y], top_screen border
            coord = Vector2.unpack(pos)
            if coord[0] < 0.5*widthscreen:
                vel = Vector2(vel_int*math.sin(abs(angle)), vel_int*math.cos(angle)) #downward, positive y
            else:
                vel = Vector2(-vel_int*math.sin(abs(angle)), vel_int*math.cos(angle))
        elif number_ast%waveprop == 3:
            pos = Vector2(rd.randint(0,widthscreen), heightscreen + lin_size/2 - margin) #bottom screen border
            coord = Vector2.unpack(pos)
            if coord[0] < 0.5*widthscreen:
                vel = Vector2(vel_int*math.sin(abs(angle)), -vel_int*math.cos(angle)) #downward, positive y
            else:
                vel = Vector2(-vel_int*math.sin(abs(angle)), -vel_int*math.cos(angle))

        image = rd.choice(list(self.game_state.image_manager.asteroids.values()))
        current_asteroid = Asteroid(
        physics_object = Physics_Object(mass = mass, pos = pos, vel = vel), 
        rigid_body =  Rigid_Body(radius=radius), 
        render_image = Render_Image(image, size = size), 
        health_manager =  Health_Manager(max_hp=mass**2/3000)
        )
        
        return current_asteroid

    def remove_asteroid(self, asteroid):
        self.asteroids.remove(asteroid)

    def manage_asteroid_spawn(self): #from level manager
        current_level = self.game_state.level_manager.current_level        
        if (current_level.asteroid_number > len(self.asteroids)) and (self.astroid_time > current_level.frequency):
            current_asteroid = self.asteroidGenerator(self.asteroid_index, current_level.asteroid_side, current_level.random)
            self.asteroid_index += 1 
            self.asteroids.append(current_asteroid)
            self.astroid_time = 0
        else:
            self.astroid_time += self.game_state.dt

class Health_Manager(Game_Object):
    """"Manages health of all objects with health (player, asteroids, enemy). Calls remove function 
    of parent if health is less than or equal to 0"""
    def __init__(self, max_hp = 3, parent = None):
        Game_Object.__init__(self)

        self.max_hp = max_hp
        self.hp = max_hp
        self.parent = parent

    def change_hp(self, delta):
        self.hp += int(delta)

        if self.hp > self.max_hp:
            self.hp = self.max_hp

        if hasattr(self.parent, "health_update"):
            self.parent.health_update()

        if self.hp <= 0:
            if hasattr(self.parent, "zero_hp"):
                self.parent.zero_hp()
        
class Asteroid(Game_Object):
    """A class for all asteroids"""
    def __init__(self, asteroid_damage = None, physics_object = None, rigid_body = None, health_manager = None, render_image = None):
        Game_Object.__init__(self)

        if physics_object == None:
            self.physics_object = Physics_Object()
            self.physics_object.parent = self
        else:
            self.physics_object = physics_object
            self.physics_object.parent = self

        if rigid_body == None:
            self.rigid_body = Rigid_Body()
            self.rigid_body.parent = self
        else:
            self.rigid_body = rigid_body
            self.rigid_body.parent = self
        
        if health_manager == None:
            self.health_manager = Health_Manager()
            self.health_manager.parent = self
        else:
            self.health_manager = health_manager
            self.health_manager.parent = self
        
        if render_image == None:
            self.render_image = Render_Image()
            self.render_image.parent = self
        else:
            self.render_image = render_image
            self.render_image.parent = self

        if asteroid_damage == None: #Obsolete
            self.asteroid_damage = self.physics_object.mass / 5
        else:
            self.asteroid_damage = asteroid_damage
            
    def local_update(self):
        self.out_of_bounds()

    def out_of_bounds(self):
        #checks whether or not asteroids is out of screen bounds
        coord = Vector2.unpack(self.physics_object.pos)
        radius = self.rigid_body.radius + 200
        if  coord[0] < 0 - radius or coord[0] > self.game_state.widthscreen + radius or coord[1] < 0 - radius or coord[1] > self.game_state.heightscreen + radius:
            self.zero_hp()
    
    def on_collision(self, other):
        #manages what happens if the asteroid collides with another game object
        if isinstance(other, SpaceShip):
            if hasattr(other, "health_manager"):
                damage = ((self.physics_object.vel - other.physics_object.vel).mag() ** 0.5) * self.physics_object.mass / 5
                other.health_manager.change_hp(-damage) 
                self.game_state.sound_manager.play_sound("bangLarge")
        if isinstance(other, Bullet):
            self.game_state.points_total += 1

    def zero_hp(self):
        self.remove_self([self.game_state.asteroid_manager.asteroids])

class Weapon_Manager(Game_Object):
    """Manages all weapons, shooting of (missiles and bullets) and even controls the flight of missiles"""
    def __init__(self, gun_cooldown = 100, bullet_damage = 1.5, bullet_speed = 0.75, bullet_radius = 2, missile_cooldown = 10000, missile_shot = 6, missile_launch_speed = 0.7, max_missile_speed = 0.7, missile_ripple_speed = 100, railgun_cooldown = 5000):
        Game_Object.__init__(self)
        self.parent = None

        self.gun_cooldown = gun_cooldown #in ms
        self.bullet_damage = bullet_damage
        self.bullet_speed = bullet_speed
        self.last_gunfire_time = 0
        self.bullet_radius = bullet_radius

        self.missiles = []
        self.missile_cooldown = missile_cooldown
        self.missile_shot = missile_shot
        self.last_missile_ripple_time = 0
        self.missile_launch_speed = missile_launch_speed
        self.max_missile_speed = max_missile_speed

        self.missile_ripple_speed = missile_ripple_speed
        self.missile_ripple = False

        self.last_railgun_fire_time = 0
        self.railgun_cooldown = railgun_cooldown

    def shoot_gun(self):
        #shoots a bullet if called
        current_time = pg.time.get_ticks()
        shooter = self.parent
        shooter_radius = shooter.rigid_body.radius

        if current_time - self.last_gunfire_time > self.gun_cooldown:
            player_forward =  self.parent.point_gun()
            '''Refer to angle in radians of shooter here to fix angle of shooting!!!!!!!! ''' 
            bullet = Bullet(
            shooter = shooter, 
            bullet_damage = self.bullet_damage, 
            rigid_body = Rigid_Body(radius = self.bullet_radius), 
            render_circle=  Render_Circle(radius= self.bullet_radius)
            )

            bullet.physics_object.pos = shooter.physics_object.pos + player_forward * (shooter_radius + self.bullet_radius + 5) 
            bullet.physics_object.vel = player_forward * self.bullet_speed + shooter.physics_object.vel
            self.game_state.sound_manager.play_sound("fire")

            self.last_gunfire_time = pg.time.get_ticks()
            
    def shoot_missiles(self, target = None):
        #shoots the missile
        self.current_time = pg.time.get_ticks()
        if self.current_time - self.last_missile_ripple_time > self.missile_cooldown:
            if target == None:
                self.targets = self.get_distanced_targets(self.max_missile_speed)
            else:
                self.targets = [[0, target]]
            self.last_missile_time = self.missile_ripple_speed
            self.last_missile_ripple_time = pg.time.get_ticks()
            self.missile_ripple = True
            self.index = 0     
            
    def shoot_railgun(self):
        #function for shooting railgun
        current_time = pg.time.get_ticks()
        if current_time - self.last_railgun_fire_time > self.railgun_cooldown:
            shooter = self.parent
            shooter_pos = self.parent.physics_object.pos
            shooter_dir = Vector2().vector_from_angle(self.parent.physics_object.ang)
            hits = Ray().cast_ray(shooter_pos, shooter_dir, self.game_state.widthscreen, self.game_state.heightscreen) 
            
            for hit in hits:
                hit_parent = hit.parent
                if isinstance(hit_parent, Asteroid) or isinstance(hit_parent, Enemy):
                    self.game_state.points_total += 50
                    hit_parent.zero_hp()
                    self.game_state.sound_manager.play_sound("bangLarge") 

            self.game_state.sound_manager.play_sound("railgun")
            railgun = Railgun(shooter_pos,shooter_dir)
            #pg.draw.line(self.game_state.screen, (0,0,255), (int(shooter_pos.x), int(shooter_pos.y)), (int(shooter_pos.x + shooter_dir.x *1000), int(shooter_pos.y + shooter_dir.y *1000)), 5)

            self.last_railgun_fire_time = current_time

    def get_distanced_targets(self, missile_speed):
        #determines targets of the missiles, selects on which asteroids will be closest when
        #missile is expected to hit the target
        distance_list = []
        minimum_values = []
        shooter_pos = self.parent.physics_object.pos
        targets = []
        
        for asteroid in self.game_state.asteroid_manager.asteroids:
            targets.append(asteroid)
        for enemie in self.game_state.enemy_manager.enemies:
            targets.append(enemie)
        
        for target in targets:
            target_pos = target.physics_object.pos
            distance_to_target = shooter_pos - target_pos
            time_to_impact = distance_to_target.mag() / missile_speed
            target_vel = target.physics_object.vel
            predicted_target_pos = target_pos + target_vel*time_to_impact
            
            distance = Vector2.mag(shooter_pos - predicted_target_pos)
            #pg.draw.circle(self.game_state.screen, (0,0,0), (int(predicted_target_pos.x), int(predicted_target_pos.y)), 10)
            #draw_text(distance, 20, (255,255,255), (int(predicted_target_pos.x), int(predicted_target_pos.y)), True, self.game_state.screen)
            distance_list.append([distance, target])
        
        distance_list.sort(key=lambda x: x[0])
        #print(distance_list)
        return distance_list

    def missile_update(self):
        #checks whether or not a missile may be fired and fires missile
        if self.missile_ripple:
            if self.index <= self.missile_shot and self.index < len(self.targets) and self.last_missile_time >= self.missile_ripple_speed:
                shooter = self.parent
                shooter_radius = shooter.rigid_body.radius

                player_forward =  Vector2(math.cos(self.game_state.player.physics_object.ang),math.sin(self.game_state.player.physics_object.ang))
                missile = Missile(self.targets[self.index][1], self.parent, max_speed = self.max_missile_speed)
                self.missiles.append(missile)

                missile.physics_object.pos = shooter.physics_object.pos + player_forward * (shooter_radius + 5) 
                missile.physics_object.vel = player_forward * self.missile_launch_speed + shooter.physics_object.vel
                self.game_state.sound_manager.play_sound("missile2")
                self.last_missile_time = 0                
                self.index += 1
            else:
                if self.index > self.missile_shot or self.index >= len(self.targets):
                    self.missile_ripple = False
                    self.index = 0

                if self.missile_ripple_speed > self.last_missile_time:
                    self.last_missile_time += self.game_state.dt
                    
    def charge_bars_update(self):
        #updates the missile charge bar, only when full, a set of missiles can be fired
        current_time = pg.time.get_ticks()
        delta = current_time-self.last_missile_ripple_time 
        per = delta / self.missile_cooldown
        percentage = min(per, 1)
        self.game_state.missile_bar.update_bar(percentage)
        
        delta_railgun = current_time-self.last_railgun_fire_time
        per_railgun = delta_railgun/self.railgun_cooldown
        railgun_percentage = min(per_railgun, 1)
        self.game_state.railgun_bar.update_bar(railgun_percentage)

    def local_update(self):
        if self.parent == self.game_state.player:
            self.charge_bars_update()
            self.missile_update()
      
class Bullet(Game_Object):
    """A class for all bullet objects, both for enemy and for player"""
    def __init__(self, physics_object=None, rigid_body=None, bullet_damage = 1, shooter = None, render_circle = None):
        Game_Object.__init__(self)

        if physics_object == None:
            self.physics_object = Physics_Object(mass=2)
            self.physics_object.parent = self
        else:
            self.physics_object = physics_object
            self.physics_object.parent = self

        if rigid_body == None:
            self.rigid_body = Rigid_Body(radius = 2)
            self.rigid_body.parent = self
        else:
            self.rigid_body = rigid_body
            self.rigid_body.parent = self
        
        if render_circle == None:
            self.render_circle = Render_Circle()
            self.render_circle.parent = self
        else:
            self.render_circle = render_circle
            self.render_circle.parent = self

        self.bullet_damage = bullet_damage
        self.shooter = shooter  
    
    def out_of_bounds(self):
        #makes sure bullets are removed when they go out of bounds
        coord = Vector2.unpack(self.physics_object.pos)
        radius = self.rigid_body.radius
        if  coord[0] < 0 - radius or coord[0] > self.game_state.widthscreen + radius or coord[1] < 0 - radius or coord[1] > self.game_state.heightscreen + radius:
            self.zero_hp()

    def zero_hp(self):
        self.remove_self()

    def on_collision(self, other):
        #determines the amount of points the player get when a bullet hits the enemy or an asteroid
        if hasattr(other, "health_manager"):
            other.health_manager.change_hp(-self.bullet_damage) 
            if isinstance(other, Enemy):
                self.game_state.points_total += 50
        self.zero_hp()

    def local_update(self):
        self.out_of_bounds()

class Railgun(Game_Object):
    def __init__(self, start_pos, direction, color = (0,0,255), duration = 150, fadeout = 1):
        Game_Object.__init__(self)
        self.start_pos = start_pos
        self.direction = direction
        self.color = color
        self.duration = duration
        self.fadeout = fadeout
        self.start_time = pg.time.get_ticks()

        self.surface = pg.Surface((2000,4), pg.SRCALPHA)
        self.rect = pg.Rect(0,0,2000,4)
        pg.draw.rect(self.surface, (0,0,255), self.rect)
        
    def local_update(self):
        current_time = pg.time.get_ticks()
        existance_time = current_time - self.start_time
        if existance_time < self.duration:
            alpha = (self.duration - existance_time*self.fadeout)/self.duration*255
            self.surface.set_alpha(alpha)
            blit_rotate(self.game_state.screen, self.surface, (int(self.start_pos.x),int(self.start_pos.y)), (0,2), math.degrees(-self.direction.get_angle()))
        else:
            self.zero_hp()
    
    def zero_hp(self):
        self.remove_self

class Player_Controller(Game_Object):
    """Sets all controls and fly-by-wire for the player, before intiating the game,
    the player can choose to get assisted (fly-by-wire) or not."""
    def __init__(self, reference_frame = "global", control_mode = "coupled", rotation_mode = "second", thrust_force = 0.08, rotation_moment = 1, rotation_speed = 0.05, correction_boost = 2): 
         #control modes: coupled: speed and rotation compensated, assist: rotation compensated, 
         #decoupled: nothing compensated
         Game_Object.__init__(self)

         self.reference_frame = reference_frame
         self.control_mode = control_mode
         self.thrust_force = thrust_force
         self.rotation_moment = rotation_moment
         self.rotation_speed = rotation_speed
         self.rotation_mode = rotation_mode
         self.correction_boost = correction_boost
         
    def control(self):
        keys = pg.key.get_pressed()
        player = self.parent
        player_physics = self.parent.physics_object

        self.forward = False
        self.back = False
        self.right = False
        self.left = False

        self.rot_right = False
        self.rot_left = False

        #next three give commands to shoot weapons
        if keys[pg.K_SPACE]:
            player.weapon_manager.shoot_gun()
        if keys[pg.K_1]:
            player.weapon_manager.shoot_missiles()
        if keys[pg.K_2]:
            player.weapon_manager.shoot_railgun()
            
        if keys[pg.K_LEFT]: #rotate
            self.rot_left = True
        
        if keys[pg.K_RIGHT]: #rotate
            self.rot_right = True

        if keys[pg.K_w]: #go forward
            self.forward = True
        
        if keys[pg.K_s]: #go backward
            self.back = True

        if keys[pg.K_a]: #go left
            self.left = True

        if keys[pg.K_d]: #go right
            self.right = True

        #sets controls if the player chooses a local reference frame
        if self.reference_frame == "local":
            player_forward = Vector2().vector_from_angle(player_physics.ang)
            if self.forward: #go forward
                force_to_add = player_forward*self.thrust_force 
                player_physics.add_force(force_to_add)
                #play_sound("thrust.wav")
            if self.back: #go backward
                force_to_add = player_forward*-self.thrust_force 
                player_physics.add_force(force_to_add)
                #play_sound("thrust.wav")
            if self.left: #go left
                player_left = Vector2().vector_from_angle(player_physics.ang-0.5*math.pi)
                force_to_add = player_left*self.thrust_force 
                player_physics.add_force(force_to_add)
                #play_sound("thrust.wav")
            if self.right: #go right
                player_right = Vector2().vector_from_angle(player_physics.ang+0.5*math.pi)
                force_to_add = player_right*self.thrust_force 
                player_physics.add_force(force_to_add)
                #play_sound("thrust.wav")

        #sets controls if the player chooses a global reference frame
        if self.reference_frame == "global":
            if self.forward: #go forward = up
                force_to_add = Vector2(0, -1)*self.thrust_force 
                player_physics.add_force(force_to_add)
                #play_sound("thrust.wav")
            if self.back: #go backward
                force_to_add = Vector2(0, 1)*self.thrust_force 
                player_physics.add_force(force_to_add)
                #play_sound("thrust.wav")
            if self.left: #go left
                force_to_add = Vector2(-1,0)*self.thrust_force 
                player_physics.add_force(force_to_add)
                #play_sound("thrust.wav")
            if self.right: #go right
                force_to_add = Vector2(1,0)*self.thrust_force 
                player_physics.add_force(force_to_add)
                #play_sound("thrust.wav")

        if self.rotation_mode == "first":
            if self.rot_left:
                player_physics.ang += -1*self.rotation_speed
            if self.rot_right:
                player_physics.ang += self.rotation_speed

        if self.rotation_mode == "second":
            if self.rot_left:
                player_physics.add_moment(-1*self.rotation_moment)
            if self.rot_right:
                player_physics.add_moment(self.rotation_moment)

    #regulates speed for the player
    def fly_by_wire_speed(self):
        player = self.parent
        player_physics = self.parent.physics_object
        
        #Currently only works for global!!!!
        if not self.forward and player_physics.vel.y > 0: #go forward = up
            force_to_add = Vector2(0, 1)*min(abs(self.thrust_force*self.correction_boost*player_physics.vel.y), self.thrust_force*self.correction_boost)*-1 
            player_physics.add_force(force_to_add)
        if not self.back and player_physics.vel.y < 0: #go backward
            force_to_add = Vector2(0, -1)*min(abs(self.thrust_force*self.correction_boost*player_physics.vel.y), self.thrust_force*self.correction_boost)*-1 
            player_physics.add_force(force_to_add)
        if not self.left and player_physics.vel.x < 0: #go left
            force_to_add = Vector2(-1,0)*min(abs(self.thrust_force*self.correction_boost*player_physics.vel.x), self.thrust_force*self.correction_boost)*-1 
            player_physics.add_force(force_to_add)
        if not self.right and player_physics.vel.x > 0: #go right
            force_to_add = Vector2(1,0)*min(abs(self.thrust_force*self.correction_boost*player_physics.vel.x), self.thrust_force*self.correction_boost)*-1 
            player_physics.add_force(force_to_add)

    #regulates rotation for the player
    def fly_by_wire_rotation(self):

        player = self.parent
        player_physics = self.parent.physics_object 

        if not self.rot_left and player_physics.ang_vel < 0:
            moment_to_add = min(abs(self.rotation_moment*self.correction_boost*player_physics.ang_vel), self.rotation_moment*self.correction_boost)*500
            player_physics.add_moment(moment_to_add)
        
        if not self.rot_right and player_physics.ang_vel > 0:
            moment_to_add = min(abs(self.rotation_moment*self.correction_boost*player_physics.ang_vel), self.rotation_moment*self.correction_boost)*-500
            player_physics.add_moment(moment_to_add)

    def local_update(self):
        self.control()
        #self explanatory
        if self.control_mode == "coupled":
            self.fly_by_wire_speed()
            self.fly_by_wire_rotation()
        if self.control_mode == "assist":
            self.fly_by_wire_rotation()

class SpaceShip(Game_Object):
    """Defines a class for all player (spaceship) objects"""
    def __init__(self, physics_object = None, rigid_body = None, weapon_manager = None, health_manager = None, render_image = None, player_controller = None):
        Game_Object.__init__(self)

        if physics_object == None:

            self.physics_object = Physics_Object(mass = 100, pos = Vector2(self.game_state.widthscreen/2,self.game_state.heightscreen/2), ang = -math.pi/2, moi = 100000)
            self.physics_object.parent = self
        else:
            self.physics_object = physics_object
            self.physics_object.parent = self

        if rigid_body == None:
            self.rigid_body = Rigid_Body(radius = 25)
            self.rigid_body.parent = self
        else:
            self.rigid_body = rigid_body
            self.rigid_body.parent = self
        
        if health_manager == None:
            self.health_manager = Health_Manager(max_hp=100)
            self.health_manager.parent = self
        else:
            self.health_manager = health_manager
            self.health_manager.parent = self

        if weapon_manager == None:
            self.weapon_manager = Weapon_Manager()
            self.weapon_manager.parent = self
        else:
            self.weapon_manager = weapon_manager
            self.weapon_manager.parent = self

        if render_image == None:
            self.render_image = Render_Image(self.game_state.image_manager.images["Spaceship"], scalar_size = 0.1, ang = math.pi/2)
            self.render_image.parent = self
        else:
            self.render_image = render_image
            self.render_image.parent = self

        if player_controller == None:
            self.player_controller = Player_Controller()
            self.player_controller.parent = self
        else:
            self.player_controller = render_image
            self.player_controller.parent = self

        self.health_update()
    
    def health_update(self):
        #updates player health bar
        percentage = self.health_manager.hp / self.health_manager.max_hp
        self.game_state.health_bar.update_bar(percentage, self.health_manager.hp)

    def out_of_bounds(self):
        #makes sure the player can't go out of bounds by bouncing the player off imaginary walls
        radius = self.rigid_body.radius
        widthscreen = self.game_state.widthscreen
        heightscreen = self.game_state.heightscreen

        inverse_x = Vector2(-1, 1)
        inverse_y = Vector2(1, -1)
        test = self.physics_object.vel * inverse_x
        coord = self.physics_object.pos.unpack()
        if coord[0] < 0 + radius:
            self.physics_object.pos = Vector2(0 + radius, coord[1])
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_x)
        if coord[0] > widthscreen - radius:
            self.physics_object.pos = Vector2(widthscreen - radius, coord[1])
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_x)
        if coord[1] < 0 + radius:
            self.physics_object.pos = Vector2(coord[0], 0 + radius)
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_y)
        if coord[1] > heightscreen - radius:
            self.physics_object.pos = Vector2(coord[0], heightscreen - radius)
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_y)

    def zero_hp(self):
        self.game_state.game_over()

    def on_collision(self, other):
        #manages collision of spaceship with asteroids
        if isinstance(other, Asteroid):
            if hasattr(other, "health_manager"):
                other.zero_hp()
                self.game_state.sound_manager.play_sound("bangLarge")

    def point_gun(self):
        #points spaceship bullet gun
        gun_vector = Vector2(math.cos(self.physics_object.ang), math.sin(self.physics_object.ang))
        return gun_vector

    def local_update(self):
        self.out_of_bounds()

class Text_Stats(Game_Object):
    """Manages the level and points total text"""
    def __init__(self, x=10, y=10):
        Game_Object.__init__(self)

        self.x = x
        self.y = y
    
    def update_text(self):
        WHITE = (255,255,255)

        draw_text("Level "+str(self.game_state.level_manager.level_number), 50, WHITE, (4, 0), False, self.game_state.screen)
        draw_text("Points "+str(self.game_state.points_total), 50, WHITE, (4, 50), False, self.game_state.screen)
        draw_text("High Score "+str(self.game_state.high_score), 50, WHITE, (4, 100), False, self.game_state.screen)

    def local_update(self):
        self.update_text()

class Enemy(Game_Object):
    """Class generating properties of enemy object"""
    def __init__(self, physics_object = None, rigid_body = None, weapon_manager = None, health_manager = None, render_image = None):
        Game_Object.__init__(self)

        if physics_object == None:
            self.physics_object = Physics_Object(mass = 100, pos = Vector2(0,self.game_state.heightscreen/(rd.randint(1,6))))
            self.physics_object.parent = self
        else:
            self.physics_object = physics_object
            self.physics_object.parent = self

        if rigid_body == None:
            self.rigid_body = Rigid_Body(radius = 25)
            self.rigid_body.parent = self
        else:
            self.rigid_body = rigid_body
            self.rigid_body.parent = self
        
        if health_manager == None:
            self.health_manager = Health_Manager(max_hp=3)
            self.health_manager.parent = self
        else:
            self.health_manager = health_manager
            self.health_manager.parent = self
        
        if render_image == None:
            self.render_image=Render_Image(self.game_state.image_manager.images["enemy"], scalar_size = 0.1, ang = math.pi/2) 
            self.render_image.parent = self
        else:
            self.render_image = render_image
            self.render_image.parent = self    

        if weapon_manager == None:
            self.weapon_manager = Weapon_Manager(gun_cooldown = 500, bullet_damage = 1.5, bullet_speed = 0.75, bullet_radius = 2, missile_cooldown=7000, missile_shot=1,max_missile_speed= 0.08, missile_launch_speed=0)
            self.weapon_manager.parent = self
        else:
            self.weapon_manager = weapon_manager
            self.weapon_manager.parent = self

    def out_of_bounds(self):
        #same reaction to out of bounds as spaceship
        radius = self.rigid_body.radius
        widthscreen = self.game_state.widthscreen
        heightscreen = self.game_state.heightscreen

        inverse_x = Vector2(-1, 1)
        inverse_y = Vector2(1, -1)
        coord = self.physics_object.pos.unpack()
        if coord[0] < 0 + radius:
            self.physics_object.pos = Vector2(0 + radius, coord[1])
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_x)
        if coord[0] > widthscreen - radius:
            self.physics_object.pos = Vector2(widthscreen - radius, coord[1])
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_x)
        if coord[1] < 0 + radius:
            self.physics_object.pos = Vector2(coord[0], 0 + radius)
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_y)
        if coord[1] > heightscreen - radius:
            self.physics_object.pos = Vector2(coord[0], heightscreen - radius)
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_y)

    def zero_hp(self):
        if rd.randint(0,2) == 1:
            health_pickup = Health_Pickup(physics_object= Physics_Object(mass=100, pos = self.physics_object.pos))
        self.remove_self()
        self.game_state.enemy_manager.enemies.remove(self)
        
    def point_gun(self):
        #function pointing the gun of the enemy towards the predicted position of the player
        base_vector = self.game_state.player.physics_object.pos - self.physics_object.pos
        time_to_player = Vector2.mag(base_vector)/0.75 #0.75 = bulletspeed
        #shooting_vector = base_vector/Vector2.mag(base_vector)
        next_player_position = self.game_state.player.physics_object.pos + time_to_player*self.game_state.player.physics_object.vel + 0.5*self.game_state.player.physics_object.accel*time_to_player**2-self.physics_object.vel*time_to_player -self.physics_object.pos
        shooting_vector_one = next_player_position/Vector2.mag(next_player_position)
        return shooting_vector_one

    def control_speed(self):
        #randomly controls enemy speed, makes sure it does not exceed set maximum speed
        speed_vector = self.physics_object.vel
        speed_mag = Vector2.mag(speed_vector)
        if speed_mag > 0.7:
            speed_vector -= 0.03*speed_vector
        if 0.2 <= speed_mag <= 0.7:
            speed_vector += Vector2(rd.uniform(-0.03,0.03), rd.uniform(-0.03,0.03))
        if speed_mag < 0.1:
            speed_vector += 0.03*speed_vector
        if speed_mag == 0:
            speed_vector+=Vector2(0.2,0)
        self.physics_object.vel = speed_vector

    def on_collision(self, other):
        #tells whats happens in case of collision
        if isinstance(other, SpaceShip):
            if hasattr(other, "health_manager"):
                other.health_manager.change_hp(-30)
    
    def shoot_at_player(self):
        #automaticly shoots at player at a set timestep
        self.weapon_manager.shoot_gun()
        self.weapon_manager.shoot_missiles(self.game_state.player)

    def local_update(self):
        self.shoot_at_player()
        self.out_of_bounds()
        self.control_speed()

class Missile(Game_Object):
    """Missile class setting properties"""
    def __init__(self, target, shooter, max_speed = 0.6, physics_object=None, rigid_body=None, bullet_damage = 1, render_image = None):
        Game_Object.__init__(self)

        if physics_object == None:
            self.physics_object = Physics_Object()
            self.physics_object.parent = self
        else:
            self.physics_object = physics_object
            self.physics_object.parent = self
        
        if rigid_body == None:
            self.rigid_body = Rigid_Body(radius = 10)
            self.rigid_body.parent = self
        else:
            self.rigid_body = rigid_body
            self.rigid_body.parent = self

        if render_image == None:
            self.render_image = Render_Image(self.game_state.image_manager.images["missile"], scalar_size = 0.15, ang = math.pi/2)
            self.render_image.parent = self
        else:
            self.render_image = render_image
            self.render_image.parent = self

        self.target = target
        self.shooter = shooter

        self.previous_distance = 0 #Vector2.mag(target_pos-missile_position)
        self.previous_closing_speed = 0#-1*(distance-self.previous_distance)/self.game_state.dt
        self.max_speed = max_speed

    def control_missile(self, target):
        #code for controlling missiles such that they hit their target
        target_pos = target.physics_object.pos
        missile_position = self.physics_object.pos
        distance = Vector2.mag(target_pos-missile_position)
         
        target_velocity = target.physics_object.vel
        target_acceleration = target.physics_object.accel

        missile_position = self.physics_object.pos
        missile_velocity = self.physics_object.vel

        if Vector2.mag(self.physics_object.vel) >= self.max_speed:
            self.physics_object.vel -= 0.1*self.physics_object.vel

        distance = Vector2.mag(target_pos-missile_position)

        closing_speed = -1*(distance-self.previous_distance)/self.game_state.dt

        time_impact = distance / self.max_speed

        predicted_target_pos = target_velocity*time_impact+0.5*target_acceleration*time_impact**2
        predicted_target_direction = target_pos + predicted_target_pos - missile_position
        predicted_target_direction_unitvector = predicted_target_direction/Vector2.mag(predicted_target_direction)

        missile_deviation_velocity = missile_velocity - (closing_speed * predicted_target_direction_unitvector)

        predicted_missile_deviation = missile_deviation_velocity * time_impact

        aim_point = target_pos + predicted_target_pos - predicted_missile_deviation
        aim_point_direction = aim_point - missile_position

        velocity_add_unit_vector = (aim_point_direction-missile_velocity)/Vector2.mag(aim_point_direction-missile_velocity)
        control = 0.05
        self.physics_object.vel += control*velocity_add_unit_vector
        self.physics_object.ang = -0.5*math.pi + self.physics_object.vel.get_angle()

        self.previous_distance = distance
        self.previous_closing_speed = closing_speed

    def on_collision(self, other):
        #sets points if the missile hits a target (asteroid or enemy)
        if isinstance(self.shooter, SpaceShip):
            if isinstance(other, Asteroid):
                other.health_manager.change_hp(-500) 
                self.game_state.points_total += 25
                self.zero_hp()
            if isinstance(other, Enemy):
                other.health_manager.change_hp(-500) 
                self.zero_hp()
                self.game_state.points_total += 50

        if isinstance(self.shooter, Enemy):
            if isinstance(other, SpaceShip):
                other.health_manager.change_hp(-20) 
                self.game_state.sound_manager.play_sound("bangLarge")
                self.zero_hp()
            if isinstance(other, Bullet):
                if isinstance(other.shooter, SpaceShip):
                    self.zero_hp()
        
            
    def out_of_bounds(self):
        #makes sure the missile is removed when out of bounds
        coord = Vector2.unpack(self.physics_object.pos)
        radius = self.rigid_body.radius
        if  coord[0] < 0 - radius or coord[0] > self.game_state.widthscreen + radius or coord[1] < 0 - radius or coord[1] > self.game_state.heightscreen + radius:
            self.zero_hp()

    def zero_hp(self):
        self.remove_self([self.shooter.weapon_manager.missiles])

    def local_update(self):
        self.control_missile(self.target)
        self.out_of_bounds()
        self.check_enemy_alive()

    def check_enemy_alive(self):
        #checks if target is still alive, if not dead by missile, missile automatically deleted
        if self.target.removed:
            self.zero_hp()

class Bar(Game_Object):
    """Class for generating health and weapon loading bars"""
    def __init__(self, size, position, position_middle  = False, number= None, percentage = 1,  background_color = (150,0,0), bar_color = (255,0,0)):
        Game_Object.__init__(self)

        self.size = size
        self.position = position
        self.background_color = background_color
        self.bar_color = bar_color

        if position_middle == True:
            self.position = (int(self.position[0] - self.size[0]/2), int(self.position[1] - self.size[1]/2))

        self.bar = pg.Rect(int(self.position[0]), int(self.position[1]),  int(self.size[0]),  int(self.size[1]))
        self.background = pg.Rect(int(self.position[0]), int(self.position[1]),  int(self.size[0]),  int(self.size[1]))

        if number != None:
            self.number = number
        else:
            self.number = None

    def update_bar(self, percentage, number = None, position = None, background_color = None, bar_color = None):
        #updates bars
        if position != None:
            self.position = position
        if background_color != None:
            self.background_color = background_color
        if bar_color != None:
            self.bar_color = bar_color
        
        bar_size = self.size[0]*percentage
        self.bar =  pg.Rect(int(self.position[0]), int(self.position[1]),  int(bar_size),  int(self.size[1]))

        if number != None:
            self.number = number
            
        return
    
    def local_update(self):
        self.draw_bar()

    def draw_bar(self):
        #draws the bar
        pg.draw.rect(self.game_state.screen, self.background_color, self.background)
        pg.draw.rect(self.game_state.screen, self.bar_color, self.bar)
        if self.number != None:
            draw_position = (int(self.position[0] + self.size[0]/2), int(self.position[1] + self.size[1]/2 + 2))
            draw_text(str(self.number), int(self.size[1]), (255,255,255), draw_position, True, self.game_state.screen)

class Health_Pickup(Game_Object):
    def __init__(self, hp = 20, physics_object = None, rigid_body = None, render_image = None):
        Game_Object.__init__(self)

        if physics_object == None:
            self.physics_object = Physics_Object()
            self.physics_object.parent = self
        else:
            self.physics_object = physics_object
            self.physics_object.parent = self

        if rigid_body == None:
            self.rigid_body = Rigid_Body(radius = 25)
            self.rigid_body.parent = self
        else:
            self.rigid_body = rigid_body
            self.rigid_body.parent = self
        
        if render_image == None:
            self.render_image=Render_Image(self.game_state.image_manager.images["health_pickup"], scalar_size = 0.04)
            self.render_image.parent = self
        else:
            self.render_image = render_image
            self.render_image.parent = self   

        self.hp = hp

    def on_collision(self, other):
        if isinstance(other, SpaceShip):
            other.health_manager.change_hp(self.hp)
            self.game_state.sound_manager.play_sound('health')
            self.zero_hp()
    
    def zero_hp(self):
        self.remove_self()

    def local_update(self):
        self.out_of_bounds()

    def out_of_bounds(self):
        #same reaction to out of bounds as spaceship
        radius = self.rigid_body.radius
        widthscreen = self.game_state.widthscreen
        heightscreen = self.game_state.heightscreen

        inverse_x = Vector2(-1, 1)
        inverse_y = Vector2(1, -1)
        coord = self.physics_object.pos.unpack()
        if coord[0] < 0 + radius:
            self.physics_object.pos = Vector2(0 + radius, coord[1])
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_x)
        if coord[0] > widthscreen - radius:
            self.physics_object.pos = Vector2(widthscreen - radius, coord[1])
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_x)
        if coord[1] < 0 + radius:
            self.physics_object.pos = Vector2(coord[0], 0 + radius)
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_y)
        if coord[1] > heightscreen - radius:
            self.physics_object.pos = Vector2(coord[0], heightscreen - radius)
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_y)
   
game_state = Game_State()