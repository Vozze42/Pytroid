import pygame as pg
import physics_engine as pe
from physics_engine import Physics_Manager, Physics_Object, Rigid_Body, Vector2, Render_Image, Render_Circle
import random as rd
import math

class Game_State():
    def __init__(self):
        Game_Object.game_state = self

        self.points_total = 0
        self.health = 0
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

        self.player = SpaceShip(physics_object = Physics_Object(mass = 10000, pos = Vector2(200,150)), rigid_body = Rigid_Body(radius = 25), health_manager = Health_Manager(hp=500), render_image=Render_Image("SpaceShip.png"), render_circle= Render_Circle(radius= 0, color=(255,0,0)))

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
            player_angle = self.player.physics_object.ang
            vel_add = 0.2 #instantaneous velocity added
            if key == pg.K_SPACE:
                self.player.weapon_manager.shoot_gun()
            #control the spacecraft: TODO: Move to SpaceShip as function
            if key == pg.K_q: #pushing q rotates 10 deg positive
                self.player.physics_object.ang += 5
            if key == pg.K_e: #pushing e rotates -10 deg, 0 deg aligned with x-axis
                self.player.physics_object.ang -= 5
            #if key == pg.K_r: #possibility to set ang_vel to zero, remove if fly_by_wire!!!
                #self.player.physics_object.ang = 0
            if key == pg.K_f: #ossibility to set velocity to zero, remove if fly_by_wire!!!
                self.player.physics_object.vel = Vector2(0,0)
            if key == pg.K_w: #go forward
                player_forward = Vector2().vector_from_angle(self.player.physics_object.ang)
                force_to_add = player_forward*1
                self.player.physics_object.add_force(force_to_add)
            if key == pg.K_s: #go backward
                player_forward = Vector2().vector_from_angle(self.player.physics_object.ang)
                force_to_add = player_forward*-1
                self.player.physics_object.add_force(force_to_add)
            if key == pg.K_a: #go left
                player_forward = Vector2().vector_from_angle(self.player.physics_object.ang+0.5*3.14)
                force_to_add = player_forward*1
                self.player.physics_object.add_force(force_to_add)
            if key == pg.K_d: #go right
                player_forward = Vector2().vector_from_angle(self.player.physics_object.ang+0.5*3.14)
                force_to_add = player_forward*-1
                self.player.physics_object.add_force(force_to_add)
            #close the game
            if key == pg.K_ESCAPE:
                running = False    

    def local_update_game_objects(self):
        for game_object in self.game_objects:
            if hasattr(game_object, "local_update"):
                game_object.local_update()
        return

    def game_over(self):
        pg.quit()
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
    def __init__(self, frequency = 200, level_number = 0, level_time = 10000, level_prop = 1, asteroids = 20):
        Game_Object.__init__(self)

        self.level_number = level_number
        self.level_prop = level_prop
        
        self.level_time = level_time

        self.time = 0
        self.asteroid_amount = 75

        self.current_level = Level()

    def update_level(self):
        #set level time of 
        if self.time >= self.level_time:
            self.level_number += 1
            self.time = 0
            level_text = "Level" + str(self.level_number)
            asteroid_number = 0
            asteroid_side = 1

            #set amount of asteroids
            if self.level_number < 3:
                asteroid_number = 20
            elif (3 <= self.level_number < 5):
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
                frequency = int(self.level_time)/int(asteroid_number)

            self.current_level = Level(level_text = level_text, asteroid_side = asteroid_side, random = random, asteroid_number = asteroid_number)

        else:
            self.time += self.game_state.dt
            self.level_text = ""

    def local_update(self):
        self.update_level()

class Level():
    def __init__(self, asteroid_number = 50, level_text = "", random = False, asteroid_side = 1, frequency = 0):
        self.level_text = level_text
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
            angle = rd.randint(-40, 40) #angle between x and y component velocity
        else:
            angle = 0   
        momentum = 400
        mass = rd.randint(60, 100) #avg mass of 80 kg assumed
        radius = int(mass/4) #with average mass 80, radius average asteroid 20 pixels
        vel_int = rd.randint(10,40)/mass #standard total momentum of 400 , avg 50 velocity in pixel/second,
        ang_vel = 0
        ang_pos = 0

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

        current_asteroid = Asteroid(physics_object = Physics_Object(mass = mass, pos = pos, vel = vel), rigid_body =  Rigid_Body(radius=radius), render_circle= Render_Circle(radius=radius), health_manager =  Health_Manager(hp=3))

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

    def zero_hp(self):
        self.game_state.remove_game_object(self)
        self.game_state.asteroid_manager.asteroids.remove(self)


class Weapon_Manager(Game_Object):
    def __init__(self, gun_cooldown = 1, bullet_damage = 1, bullet_speed = 1, bullet_radius = 2):
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
            player_forward =  Vector2().vector_from_angle(shooter.physics_object.ang) 
            bullet = Bullet(shooter = shooter, bullet_damage = self.bullet_damage, rigid_body = Rigid_Body(radius = self.bullet_radius))
            bullet.physics_object.pos = shooter.physics_object.pos + player_forward * (shooter_radius + self.bullet_radius + 5) 
            bullet.physics_object.vel = player_forward * self.bullet_speed
            self.last_gunfire_time = pg.time.get_ticks()

class Bullet(Game_Object):
    def __init__(self, physics_object=None, rigid_body = None, bullet_damage = 1, shooter = None):
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
        self.game_state.remove_game_object(self)

    def local_update(self):
        self.out_of_bounds()

class SpaceShip(Game_Object):
    def __init__(self, physics_object = None, rigid_body = None, weapon_manager = None, health_manager = None, render_image = None, render_circle = None):
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

        if render_circle == None:
            self.render_circle = Render_Circle()
            self.render_circle.parent = self
        else:
            self.render_circle = render_circle
            self.render_circle.parent = self

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

    def local_update(self):
        self.out_of_bounds()

game_state = Game_State()
game_state.update()