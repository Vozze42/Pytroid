#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Servaas & Lennart
"""

import pygame as pg
import physics_engine as pe
from physics_engine import Physics_Manager, Physics_Object, Rigid_Body, Vector2, Render_Image, Render_Circle
import random as rd
import math
import os

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

        self.physics_manager = Physics_Manager(self.screen)
        self.level_manager = Level_Manager()
        self.asteroid_manager = Asteroid_Manager()

        self.player = SpaceShip(physics_object = Physics_Object(mass = 1000, pos = Vector2(200,150), ang_vel = 0), rigid_body = Rigid_Body(radius = 25), health_manager = Health_Manager(hp=500), render_image=Render_Image("SpaceShip.png"))
        self.points_total = 0
        
        self.stats = Text_Stats()

    def init_pygame(self):
        pg.init()
        self.screen = pg.display.set_mode((self.widthscreen, self.heightscreen))
        self.clock = pg.time.Clock()

    def remove_game_object(self, game_object):
        if hasattr(game_object, 'physics_object'):
            self.physics_manager.physics_objects.remove(game_object.physics_object)
        if hasattr(game_object, 'rigid_body'):
            self.physics_manager.rigid_bodies.remove(game_object.rigid_body)
        if hasattr(game_object, 'render_image'):
            self.physics_manager.render_images.remove(game_object.render_image)
        if hasattr(game_object, 'render_circle'):
            self.physics_manager.render_circles.remove(game_object.render_circle)
        self.game_objects.remove(game_object)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            key = event.key
            #close the game
            if key == pg.K_ESCAPE:
                running = False    

    def local_update_game_objects(self):
        for game_object in self.game_objects:
            if hasattr(game_object, "local_update"):
                game_object.local_update()
        return

    def game_over(self):
        self.points_total = 0
        self.player.health_manager.hp = 500
        '''
        for game_object in self.game_objects:
            self.remove_game_object(game_object)
        '''
        self.player.vel = Vector2(0,0)
        self.asteroids_broken = 0
        self.level_manager.level_number = 1
        self.level_manager.time = 0
        return
        
    def update(self):
        while self.running:
            self.dt = self.clock.tick(self.fps)
            self.screen.fill((0, 0, 0))
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


class Level_Manager(Game_Object):
    def __init__(self, frequency = 200, level_number = 1, level_time = 10000, level_prop = 1, asteroids = 20):
        Game_Object.__init__(self)

        self.level_number = level_number
        self.level_prop = level_prop
        
        self.level_time = level_time

        self.time = 0
        self.asteroid_amount = 20

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
            elif (3 < self.level_number <= 5):
                asteroid_number = 30
            else:
                self.asteroid_amount += 5
                asteroid_number = self.asteroid_amount

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

            self.current_level = Level(asteroid_side = asteroid_side, random = random, asteroid_number = asteroid_number)

        else:
            self.time += self.game_state.dt

    def local_update(self):
        self.update_level()

class Level():
    def __init__(self, asteroid_number = 50, random = False, asteroid_side = 1, frequency = 0):
        self.asteroid_number = asteroid_number
        self.frequency = frequency
        self.random = random
        self.asteroid_side = asteroid_side

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
        mass = rd.randint(60, 100) #avg mass of 80 kg assumed
        radius = int(mass/4) #with average mass 80, radius average asteroid 20 pixels
        vel_int = rd.randint(10,40)/mass #standard total momentum of 400 , avg 50 velocity in pixel/second,

        widthscreen = self.game_state.widthscreen
        heightscreen = self.game_state.heightscreen

        if number_ast%waveprop == 0:
            pos = Vector2(widthscreen, rd.randint(0,heightscreen)) #right screen border
            coord = Vector2.unpack(pos)
            if coord[1] < 0.5*heightscreen:
                vel = Vector2(-vel_int*math.cos(angle), vel_int*math.sin(abs(angle)))
            else:
                vel = Vector2(-vel_int*math.cos(angle), -vel_int*math.sin(abs(angle)))
        elif number_ast%waveprop == 1:
            pos = Vector2(0, rd.randint(0,heightscreen)) #left screen border #right screen border
            coord = Vector2.unpack(pos)
            if coord[1] < 0.5*heightscreen:
                vel = Vector2(vel_int*math.cos(angle), vel_int*math.sin(abs(angle)))
            else:
                vel = Vector2(vel_int*math.cos(angle), -vel_int*math.sin(abs(angle)))
        elif number_ast%waveprop == 2:
            pos = Vector2(rd.randint(0,widthscreen), 0) #left handed coordinate system, [x,y], top_screen border
            coord = Vector2.unpack(pos)
            if coord[0] < 0.5*widthscreen:
                vel = Vector2(vel_int*math.sin(abs(angle)), vel_int*math.cos(angle)) #downward, positive y
            else:
                vel = Vector2(-vel_int*math.sin(abs(angle)), vel_int*math.cos(angle))
        elif number_ast%waveprop == 3:
            pos = Vector2(rd.randint(0,widthscreen), heightscreen) #bottom screen border
            coord = Vector2.unpack(pos)
            if coord[0] < 0.5*widthscreen:
                vel = Vector2(vel_int*math.sin(abs(angle)), -vel_int*math.cos(angle)) #downward, positive y
            else:
                vel = Vector2(-vel_int*math.sin(abs(angle)), -vel_int*math.cos(angle))

        current_asteroid = Asteroid(physics_object = Physics_Object(mass = mass, pos = pos, vel = vel), rigid_body =  Rigid_Body(radius=radius), render_circle= Render_Circle(radius=radius), health_manager =  Health_Manager(hp=1))

        return current_asteroid

    def remove_asteroid(self, asteroid):
        self.asteroids.remove(asteroid)

    def manage_asteroid_spawn(self):
        current_level = self.game_state.level_manager.current_level        
        if (current_level.asteroid_number > len(self.asteroids)) and (self.astroid_time > current_level.frequency):
            current_asteroid = self.asteroidGenerator(self.asteroid_index, current_level.asteroid_side, current_level.random)
            self.asteroid_index += 1 
            self.asteroids.append(current_asteroid)
            self.astroid_time = 0
        else:
            self.astroid_time += self.game_state.dt

    def local_update(self):
        self.manage_asteroid_spawn()

        return

class Health_Manager(Game_Object):
    def __init__(self, hp = 3, parent = None):
        Game_Object.__init__(self)

        self.hp = hp
        self.parent = parent

    def take_damage(self, damage):
        self.hp -= damage

        if self.hp <= 0:
            if hasattr(self.parent, "zero_hp"):
                self.parent.zero_hp()

class Asteroid(Game_Object):
    def __init__(self, asteroid_damage = 100, physics_object = None, rigid_body = None, health_manager = None, render_circle = None):
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

        if render_circle == None:
            self.render_circle = Render_Circle()
            self.render_circle.parent = self
        else:
            self.render_circle = render_circle
            self.render_circle.parent = self

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
                other.health_manager.take_damage(self.asteroid_damage) 
                pg.mixer.music.load("bangLarge.wav")
                pg.mixer.music.play(loops=0)
                pg.mixer.music.set_volume(0.1)

    def zero_hp(self):
        self.game_state.remove_game_object(self)
        self.game_state.asteroid_manager.asteroids.remove(self)


class Weapon_Manager(Game_Object):
    def __init__(self, gun_cooldown = 100, bullet_damage = 1, bullet_speed = 0.75, bullet_radius = 2):
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
            player_forward =  Vector2().vector_from_angle(self.game_state.player.physics_object.ang)
            '''Refer to angle in radians of shooter here to fix angle of shooting!!!!!!!! ''' 
            bullet = Bullet(
            shooter = shooter, 
            bullet_damage = self.bullet_damage, 
            rigid_body = Rigid_Body(radius = self.bullet_radius), 
            render_circle=  Render_Circle(radius= self.bullet_radius)
            )

            bullet.physics_object.pos = shooter.physics_object.pos + player_forward * (shooter_radius + self.bullet_radius + 5) 
            bullet.physics_object.vel = player_forward * self.bullet_speed + shooter.physics_object.vel
            pg.mixer.music.load("fire.wav")
            pg.mixer.music.play(loops=0)

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
        self.game_state.remove_game_object(self)

    def on_collision(self, other):
        if hasattr(other, "health_manager"):
            other.health_manager.take_damage(self.bullet_damage) 
            self.game_state.asteroids_broken += 1
            self.game_state.points_total += 1
            pg.mixer.music.load("bangSmall.wav")
            pg.mixer.music.play(loops=0)
            pg.mixer.music.set_volume(0.1)
        self.game_state.remove_game_object(self)

    def local_update(self):
        self.out_of_bounds()

class Player_Controller(Game_Object):
    def __init__(self, reference_frame = "global", control_mode = "coupled", rotation_mode = "zeroth", thrust_force = 1, rotation_moment = 1, rotation_speed = 0.05, correction_boost = 2): #control modes: coupled: speed and rotation compensated, assist: rotation compensated, decoupled: nothing compensated
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


        if keys[pg.K_UP]:
            player.weapon_manager.shoot_gun()
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
            if self.back: #go backward
                force_to_add = player_forward*-self.thrust_force 
                player_physics.add_force(force_to_add)
            if self.left: #go left
                player_left = Vector2().vector_from_angle(player_physics.ang-0.5*math.pi)
                force_to_add = player_left*self.thrust_force 
                player_physics.add_force(force_to_add)
            if self.right: #go right
                player_right = Vector2().vector_from_angle(player_physics.ang+0.5*math.pi)
                force_to_add = player_right*self.thrust_force 
                player_physics.add_force(force_to_add)

        if self.reference_frame == "global":
            if self.forward: #go forward = up
                force_to_add = Vector2(0, -1)*self.thrust_force 
                player_physics.add_force(force_to_add)
            if self.back: #go backward
                force_to_add = Vector2(0, 1)*self.thrust_force 
                player_physics.add_force(force_to_add)
            if self.left: #go left
                force_to_add = Vector2(-1,0)*self.thrust_force 
                player_physics.add_force(force_to_add)
            if self.right: #go right
                force_to_add = Vector2(1,0)*self.thrust_force 
                player_physics.add_force(force_to_add)

        if self.rotation_mode == "zeroth":
            if self.rot_left:
                player_physics.ang += -1*self.rotation_speed
            if self.rot_right:
                player_physics.ang += self.rotation_speed

        if self.rotation_mode == "first":
            if self.rot_left:
                player_physics.add_moment(self.rotation_moment)
            if self.rot_right:
                player_physics.add_moment(-1*self.rotation_moment)

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
        """
        if self.reference_frame == "local":
            player_forward = Vector2().vector_from_angle(player_physics.ang)
            if not self.forward: #go forward
                force_to_add = player_forward*self.thrust_force*self.correction_boost*-1
                player_physics.add_force(force_to_add)
            if not self.back: #go backward
                force_to_add = player_forward*-self.thrust_force*self.correction_boost*-1
                player_physics.add_force(force_to_add)
            if not self.left: #go left
                player_left = Vector2().vector_from_angle(player_physics.ang-0.5*math.pi)
                force_to_add = player_left*self.thrust_force*self.correction_boost*-1 
                player_physics.add_force(force_to_add)
            if not self.right: #go right
                player_right = Vector2().vector_from_angle(player_physics.ang+0.5*math.pi)
                force_to_add = player_right*self.thrust_force*self.correction_boost*-1
                player_physics.add_force(force_to_add)
        """
        return
    def fly_by_wire_rotation(self):
        return


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

        if weapon_manager == None:
            self.weapon_manager = Weapon_Manager()
            self.weapon_manager.parent = self
        else:
            self.weapon_manager = weapon_manager
            self.weapon_manager.parent = self

        if render_image == None:
            self.render_image = Render_Image()
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
        if coord[0] < 0 - radius:
            self.physics_object.pos = Vector2(0 + radius, coord[1])
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_x)
        if coord[0] > widthscreen + radius:
            self.physics_object.pos = Vector2(widthscreen - radius, coord[1])
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_x)
        if coord[1] < 0 - radius:
            self.physics_object.pos = Vector2(coord[0], 0 + radius)
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_y)
        if coord[1] > heightscreen + radius:
            self.physics_object.pos = Vector2(coord[0], heightscreen - radius)
            self.physics_object.vel = self.physics_object.vel.pseudo_cross(inverse_y)

    def zero_hp(self):
        self.game_state.game_over()

    def on_collision(self, other):
        if isinstance(other, Asteroid):
            if hasattr(other, "health_manager"):
                self.game_state.remove_game_object(other)
                pg.mixer.music.load("bangLarge.wav")
                pg.mixer.music.play(loops=0)


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


game_state = Game_State()
game_state.update()