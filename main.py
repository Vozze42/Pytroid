#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Servaas & Lennart
"""

import pygame as pg
import physics_engine as pe
from physics_engine import Physics_Manager, Physics_Object, Rigid_Body, Vector2, Render_Image, Render_Circle, play_sound, Image_Manager
import random as rd
import math
import os
import inspect
import sys


class Game_State():
    def __init__(self):
        
        Game_Object.game_state = self

        self.asteroids_broken = 0

        self.game_objects = []
        self.fps = 60

        self.asteroid_index = 1
        self.running = True

        self.widthscreen = 1920
        self.heightscreen = 1080

        self.init_pygame()
        self.main_menu()

    def main_menu(self):
        self.image_manager = Image_Manager(image_folder= "./images", asteroid_path = "./images/asteroids")
        start_image = self.image_manager.images["Pytroid.png"]
        start_image = pg.transform.scale(start_image, (self.widthscreen, self.heightscreen))
        pg.mixer.music.load("./sounds/battletheme.mp3")
        pg.mixer.music.play(loops = -1)
        while True:
            for event in pg.event.get():
                self.handle_event(event)
                if event.type == pg.KEYDOWN:
                    self.start_game()

            self.screen.blit(start_image, [0, 0])
            pg.display.flip()

    def start_game(self):    
        self.clock = pg.time.Clock()           
        self.physics_manager = Physics_Manager(self.screen)
        self.level_manager = Level_Manager()
        self.asteroid_manager = Asteroid_Manager() #TODO: Move to level_manager
        self.enemy_manager = Enemy_Manager() #TODO: Move to level_manager
        
        self.player = SpaceShip()

        self.points_total = 0
        
        self.stats = Text_Stats()

        self.background_image = self.image_manager.images["Andromeda.png"]
        self.the_image = pg.transform.scale(self.background_image, (self.widthscreen,self.heightscreen))

        self.update()

    def init_pygame(self):
        pg.init()
        self.screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        
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
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()   

    def local_update_game_objects(self):
        for game_object in self.game_objects:
            if hasattr(game_object, "local_update"):
                game_object.local_update()
        return

    def game_over(self):
        game_over_image = self.image_manager.images["game over.png"]
        game_over_image = pg.transform.scale(game_over_image, (self.widthscreen, self.heightscreen))
        while True:
            self.screen.blit(game_over_image, (0, 0))
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
                    self.asteroids_broken = 0
                    self.level_manager.level_number = 0
                    self.level_manager.time = 0
                    return
     
    def update(self):
        while self.running:
            self.dt = self.clock.tick(self.fps)
            #self.screen.fill((0, 0, 0))
            self.screen.blit(self.the_image, [0, 0])
            for event in pg.event.get():
                self.handle_event(event)

            pg.event.pump()

            self.local_update_game_objects()

            self.physics_manager.update_all(self.dt)

            pg.display.flip()


class Game_Object():
    game_state = None

    def __init__(self):
        if self.game_state != None:
            self.game_state.game_objects.append(self)
            self.removed = False

    def remove_self(self):
        if not self.removed:
            self.removed = True
            self.game_state.remove_game_object(self)

class Level_Manager(Game_Object):
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
                self.frequency = int(self.level_time)/int(asteroid_number)

            self.current_level = Level(asteroid_side = asteroid_side, random = random, asteroid_number = asteroid_number, frequency=self.frequency, enemy_number=enemy_number)

        else:
            self.time += self.game_state.dt

    def local_update(self):
        self.update_level()
        self.game_state.asteroid_manager.manage_asteroid_spawn()
        self.game_state.enemy_manager.manage_enemy_spawn()

class Level():
    def __init__(self, asteroid_number = 0, random = False, asteroid_side = 1, frequency = 0, enemy_number = 0):
        self.asteroid_number = asteroid_number
        self.frequency = frequency
        self.random = random
        self.asteroid_side = asteroid_side
        self.enemy_number = enemy_number

class Enemy_Manager(Game_Object):
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
            self.enemy_frequency = rd.randint(3000,50000)
            self.enemy_time = 0
        else:
            self.enemy_time += self.game_state.dt


class Asteroid_Manager(Game_Object):
    def __init__(self):
        Game_Object.__init__(self)
        self.astroid_time = 0
        self.asteroids = []
        self.asteroid_index = 1

    def asteroidGenerator(self, number_ast, waveprop, random): #set constant initially, increase if wave functionality added
        
        if random == True:
            angle = math.radians(rd.randint(-40, 40)) #angle between x and y component velocity
        else:
            angle = 0   

        rand = rd.randint(0,100)/100
        mass = 40 + (400-40)*rand**3 #rd.randint(40, 250) #avg mass of 80 kg assumed
        radius = int(mass/4) #with average mass 80, radius average asteroid 20 pixels
        vel_int = rd.randint(15,30)/mass #standard total momentum of 400 , avg 50 velocity in pixel/second,

        widthscreen = self.game_state.widthscreen
        heightscreen = self.game_state.heightscreen

        lin_size = int(radius * 2 *1.4)
        size = (lin_size, lin_size)
        margin = 50
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
        health_manager =  Health_Manager(hp=mass**2/3000)
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
    def __init__(self, hp = 3, parent = None):
        Game_Object.__init__(self)

        self.hp = hp
        self.parent = parent

    def take_damage(self, damage):
        self.hp -= int(damage)

        if hasattr(self.parent, "health_update"):
            self.parent.health_update()

        if self.hp <= 0:
            if hasattr(self.parent, "zero_hp"):
                self.parent.zero_hp()

class Asteroid(Game_Object):
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
        coord = Vector2.unpack(self.physics_object.pos)
        radius = self.rigid_body.radius
        if  coord[0] < 0 - radius or coord[0] > self.game_state.widthscreen + radius or coord[1] < 0 - radius or coord[1] > self.game_state.heightscreen + radius:
            self.zero_hp()
    
    def on_collision(self, other):
        if isinstance(other, SpaceShip):
            if hasattr(other, "health_manager"):
                damage = ((self.physics_object.vel - other.physics_object.vel).mag() ** 0.5) * self.physics_object.mass / 5
                other.health_manager.take_damage(damage) 
                play_sound("./sounds/bangLarge.wav")

    def zero_hp(self):
        self.remove_self()
        self.game_state.asteroid_manager.asteroids.remove(self)

class Weapon_Manager(Game_Object):
    def __init__(self, gun_cooldown = 100, bullet_damage = 1.5, bullet_speed = 0.75, bullet_radius = 2):
        Game_Object.__init__(self)
        self.parent = None

        self.gun_cooldown = gun_cooldown #in ms
        self.bullet_damage = bullet_damage
        self.bullet_speed = bullet_speed
        self.last_gunfire_time = 0
        self.bullet_radius = bullet_radius

    def shoot_gun(self):
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

            self.last_gunfire_time = pg.time.get_ticks()

class Bullet(Game_Object):
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
        coord = Vector2.unpack(self.physics_object.pos)
        radius = self.rigid_body.radius
        if  coord[0] < 0 - radius or coord[0] > self.game_state.widthscreen + radius or coord[1] < 0 - radius or coord[1] > self.game_state.heightscreen + radius:
            self.zero_hp()

    def zero_hp(self):
        self.remove_self()

    def on_collision(self, other):
        if hasattr(other, "health_manager"):
            other.health_manager.take_damage(self.bullet_damage) 
            self.game_state.asteroids_broken += 1
            self.game_state.points_total += 1
            #play_sound("./sounds/bangSmall.wav")
        self.zero_hp()

    def local_update(self):
        self.out_of_bounds()

class Player_Controller(Game_Object):
    def __init__(self, reference_frame = "global", control_mode = "coupled", rotation_mode = "second", thrust_force = 0.04, rotation_moment = 1, rotation_speed = 0.05, correction_boost = 2): #control modes: coupled: speed and rotation compensated, assist: rotation compensated, decoupled: nothing compensated
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

        if keys[pg.K_SPACE]:
            player.weapon_manager.shoot_gun()
            play_sound("./sounds/fire.wav")
        #control the spacecraft: 
        if keys[pg.K_LEFT]: 
            self.rot_left = True
        
        if keys[pg.K_RIGHT]: 
            self.rot_right = True

        if keys[pg.K_w]: #go forward
            self.forward = True
        
        if keys[pg.K_s]: #go backward
            self.back = True

        if keys[pg.K_a]: #go left
            self.left = True

        if keys[pg.K_d]: #go right
            self.right = True

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

    def fly_by_wire_speed(self):
        player = self.parent
        player_physics = self.parent.physics_object
        
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

        if self.control_mode == "coupled":
            self.fly_by_wire_speed()
            self.fly_by_wire_rotation()
        if self.control_mode == "assist":
            self.fly_by_wire_rotation()


class SpaceShip(Game_Object):
    def __init__(self, physics_object = None, rigid_body = None, weapon_manager = None, health_manager = None, render_image = None, player_controller = None):
        Game_Object.__init__(self)

        if physics_object == None:

            self.physics_object = Physics_Object(mass = 50, pos = Vector2(self.game_state.widthscreen/2,self.game_state.heightscreen/2), ang = -math.pi/2, moi = 100000)
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
            self.health_manager = Health_Manager(hp=100)
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
            self.render_image = Render_Image(self.game_state.image_manager.images["Spaceship.png"], scalar_size = 0.1, ang = math.pi/2)
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

    def out_of_bounds(self):
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
        if isinstance(other, Asteroid):
            if hasattr(other, "health_manager"):
                other.zero_hp()
                play_sound("./sounds/bangLarge.wav")

    def point_gun(self):
        gun_vector = Vector2(math.cos(self.physics_object.ang), math.sin(self.physics_object.ang))
        return gun_vector

    def local_update(self):
        self.out_of_bounds()

class Text_Stats(Game_Object):
    def __init__(self, x=10, y=10):
        Game_Object.__init__(self)

        self.x = x
        self.y = y

    def draw_text(self,text, size, color, position, middle):
        text = str(text)

        default_font = pg.font.get_default_font()
        self.font = pg.font.Font(default_font, size)

        textsurface = self.font.render(text, False, color)
        if middle:
            offset = textsurface.get_size()
            position = (position[0] - offset[0] / 2, position[1] - offset[1] / 2)

        self.game_state.screen.blit(textsurface, position)
    
    def update_text(self):
        WHITE = (255,255,255)

        self.draw_text("Level: "+str(self.game_state.level_manager.level_number), 40, WHITE, (4, 0), False)
        self.draw_text("Health: "+str(self.game_state.player.health_manager.hp), 40, WHITE, (4, 40), False)
        self.draw_text("Points total: "+str(self.game_state.points_total), 40, WHITE, (4, 80), False)
        self.draw_text("Asteroids broken: "+str(self.game_state.asteroids_broken), 40, WHITE, (4, 120), False)

    def local_update(self):
        self.update_text()

class Enemy(Game_Object):
    def __init__(self, physics_object = None, rigid_body = None, weapon_manager = None, health_manager = None, render_image = None):
        Game_Object.__init__(self)

        if physics_object == None:
            self.physics_object = Physics_Object(mass = 100, pos = Vector2(0,self.game_state.heightscreen/(rd.randint(1,6))), moi = 100000)
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
            self.health_manager = Health_Manager(hp=3)
            self.health_manager.parent = self
        else:
            self.health_manager = health_manager
            self.health_manager.parent = self
        
        if render_image == None:
            self.render_image=Render_Image(self.game_state.image_manager.images["enemy.png"], scalar_size = 0.1, ang = math.pi/2) 
            self.render_image.parent = self
        else:
            self.render_image = render_image
            self.render_image.parent = self    

        if weapon_manager == None:
            self.weapon_manager = Weapon_Manager(gun_cooldown = 500, bullet_damage = 1.5, bullet_speed = 0.75, bullet_radius = 2)
            self.weapon_manager.parent = self
        else:
            self.weapon_manager = weapon_manager
            self.weapon_manager.parent = self

    def out_of_bounds(self):
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
        self.remove_self()
        self.game_state.enemy_manager.enemies.remove(self)
        
    def point_gun(self):
        base_vector = self.game_state.player.physics_object.pos - self.physics_object.pos
        time_to_player = Vector2.mag(base_vector)/0.75 #0.75 = bulletspeed
        #shooting_vector = base_vector/Vector2.mag(base_vector)
        next_player_position = self.game_state.player.physics_object.pos + time_to_player*self.game_state.player.physics_object.vel + 0.5*self.game_state.player.physics_object.accel*time_to_player**2-self.physics_object.vel*time_to_player -self.physics_object.pos
        shooting_vector_one = next_player_position/Vector2.mag(next_player_position)
        return shooting_vector_one

    def control_speed(self):
        speed_vector = self.physics_object.vel
        speed_mag = Vector2.mag(speed_vector)
        if speed_mag > 1:
            speed_vector -= 0.03*speed_vector
        if 0.2 <= speed_mag <= 1:
            speed_vector += Vector2(rd.uniform(-0.03,0.03), rd.uniform(-0.03,0.03))
        if speed_mag < 0.2:
            speed_vector += 0.03*speed_vector
        if speed_mag == 0:
            speed_vector+=Vector2(0.2,0)
        self.physics_object.vel = speed_vector

    def on_collision(self, other):
        if isinstance(other, Asteroid):
            play_sound("./sounds/bangLarge.wav")
        if isinstance(other, SpaceShip):
            if hasattr(other, "health_manager"):
                other.health_manager.take_damage(500)
                play_sound("./sounds/bangLarge.wav")
    
    def shoot_at_player(self):
        self.weapon_manager.shoot_gun()

    def local_update(self):
        self.shoot_at_player()
        self.out_of_bounds()
        self.control_speed()

class Bar(Game_Object):
    def init(self, size, position, background_color = (150,0,0), bar_color = (255,0,0)):
        return

    def update_bar():
        return


game_state = Game_State()