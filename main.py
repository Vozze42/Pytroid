import pygame as pg
import physics_engine as pe
from physics_engine import Physics_Manager, Physics_Object, Rigid_Body, Vector2
import random as rd
import math

class Game_State():
    def __init__(self):
        self.points_total = 0
        self.health = 0
        self.asteroids_broken = 0

        self.game_objects = []
        
        self.fps = 60

        self.asteroid_index = 1 
        self.running = True
        self.asteroids = []
        self.bullets = []

        self.widthscreen = 1920
        self.heightscreen = 1080

        self.init_pygame()
        self.physics_manager = Physics_Manager(self.screen)
        Game_Object.game_state = self
        self.player = SpaceShip(physics_object = Physics_Object(pos = Vector2(200,150)), rigid_body = Rigid_Body(radius = 10, color= (0,255,0)))

    def init_pygame(self):
        pg.init()
        self.screen = pg.display.set_mode((self.widthscreen, self.heightscreen))
        self.clock = pg.time.Clock()

    def collision(self, this_object, other_object):
        collision_should_occur = True
        if (type(this_object).__name__ == Asteroid and type(other_object).__name__ == Bullet) or (type(other_object).__name__ == Asteroid and type(this_object).__name__ == Bullet):
            if type(this_object).__name__ == Bullet: #
                other_object.health -= 1
                self.remove_game_object(this_object) #remove this bullet
                if other_object.health <= 0:
                    self.remove_game_object(other_object) #also remove the asteroid
            else:
                this_object.health -= 1
                self.remove_game_object(other_object) #remove this bullet
                if this_object.health <= 0:
                    self.remove_game_object(this_object) #also remove the asteroid

            self.points_total += 1 #is this correct?

        if (type(this_object).__name__ == SpaceShip and type(other_object).__name__ == Asteroid) or (type(other_object).__name__ == SpaceShip and type(this_object).__name__ == Asteroid):
            if type(this_object).__name__ == SpaceShip:
                this_object.health -= 1
                collision_should_occur = False #velocity needs to stay the same
                self.remove_game_object(other_object)
            else:
                other_object.health -= 1
                collision_should_occur = False
                self.remove_game_object(this_object)


        return collision_should_occur

    def remove_game_object(self, game_object):
        if hasattr(game_object, 'physics_object'):
            self.physics_manager.physics_objects.remove(game_object.physics_object)
        if hasattr(game_object, 'rigid_body'):
            self.physics_manager.rigid_bodies.remove(game_object.rigid_body)
        self.game_objects.remove(game_object)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            key = event.key
            player_angle = self.player.physics_object.ang
            vel_add = 0.01 #instantaneous velocity added
            if key == pg.K_SPACE:
                self.player.weapon_manager.shoot_gun()
            #control the spacecraft: TODO: Move to SpaceShip as function
            if key == pg.K_q: #pushing q rotates 10 deg positive
                self.player.physics_object.ang_vel += 10
            if key == pg.K_e: #pushing e rotates -10 deg, 0 deg aligned with x-axis
                self.player.physics_object.ang_vel -= 10
            if key == pg.K_r: #possibility to set ang_vel to zero, remove if fly_by_wire!!!
                self.player.physics_object.ang_vel = 0
            if key == pg.K_f: #ossibility to set velocity to zero, remove if fly_by_wire!!!
                self.player.physics_object.vel = Vector2(0,0)
            if key == pg.K_w: #go forward
                self.player.physics_object.vel += Vector2(vel_add*math.cos(player_angle), vel_add*math.sin(player_angle))
            if key == pg.K_s: #go backward
                self.player.physics_object.vel += Vector2(vel_add*-math.cos(player_angle), vel_add*math.sin(player_angle))
            if key == pg.K_a: #go left
                self.player.physics_object.vel += Vector2(vel_add*math.sin(player_angle), -vel_add*math.cos(player_angle))
            if key == pg.K_d: #go right
                self.player.physics_object.vel += Vector2(vel_add*math.sin(player_angle), vel_add*math.cos(player_angle))
            #close the game
            if key == pg.K_ESCAPE:
                running = False    

    def asteroidGenerator(self, number_ast, waveprop, random): #set constant initially, increase if wave functionality added
        if random == True:
            angle = rd.randint(-40, 40) #angle between x and y component velocity
        else:
            angle = 0   
        momentum = 400
        mass = rd.randint(60, 100) #avg mass of 80 kg assumed
        radius = int(mass/4) #with average mass 80, radius average asteroid 20 pixels
        vel_int = 40/mass #standard total momentum of 400 , avg 50 velocity in pixel/second,
        ang_vel = 0
        ang_pos = 0
        if number_ast%waveprop == 0:
            pos = Vector2(self.widthscreen, rd.randint(0,self.heightscreen)) #right screen border
            coord = Vector2.unpack(pos)
            if coord[1] < 0.5*self.heightscreen:
                vel = Vector2(-vel_int*math.cos(angle), vel_int*math.sin(abs(angle)))
            else:
                vel = Vector2(-vel_int*math.cos(angle), -vel_int*math.sin(abs(angle)))
        elif number_ast%waveprop == 1:
            pos = Vector2(0, rd.randint(0,self.heightscreen)) #left screen border #right screen border
            coord = Vector2.unpack(pos)
            if coord[1] < 0.5*self.heightscreen:
                vel = Vector2(vel_int*math.cos(angle), vel_int*math.sin(abs(angle)))
            else:
                vel = Vector2(vel_int*math.cos(angle), -vel_int*math.sin(abs(angle)))
        elif number_ast%waveprop == 2:
            pos = Vector2(rd.randint(0,self.widthscreen), 0) #left handed coordinate system, [x,y], top_screen border
            coord = Vector2.unpack(pos)
            if coord[0] < 0.5*self.widthscreen:
                vel = Vector2(vel_int*math.sin(abs(angle)), vel_int*math.cos(angle)) #downward, positive y
            else:
                vel = Vector2(-vel_int*math.sin(abs(angle)), vel_int*math.cos(angle))
        elif number_ast%waveprop == 3:
            pos = Vector2(rd.randint(0,self.widthscreen), self.heightscreen) #bottom screen border
            coord = Vector2.unpack(pos)
            if coord[0] < 0.5*self.widthscreen:
                vel = Vector2(vel_int*math.sin(abs(angle)), -vel_int*math.cos(angle)) #downward, positive y
            else:
                vel = Vector2(-vel_int*math.sin(abs(angle)), -vel_int*math.cos(angle))

        current_asteroid = Asteroid(physics_object = Physics_Object(mass = mass, pos = pos, vel = vel), rigid_body = Rigid_Body(radius=radius))

        return current_asteroid

    def local_update_game_objects(self):
        for game_object in self.game_objects:
            if hasattr(game_object, "local_update"):
                game_object.local_update()
        return

    def update(self):
        self.astroid_time = 0
        self.player.health = 3
        while self.running:
            self.dt = self.clock.tick(self.fps)
            self.screen.fill((0, 0, 0))

            self.current_level = Level_Manager()

            if (self.current_level.asteroids > len(self.asteroids)) and (self.astroid_time > self.current_level.frequency):
                current_asteroid = self.asteroidGenerator(self.asteroid_index, self.current_level.level_prop, self.current_level.random)
                self.asteroid_index += 1 
                self.asteroids.append(current_asteroid)
                self.astroid_time = 0
                self.astroid_time += self.dt
            elif self.current_level.asteroids == len(self.asteroids) and (self.astroid_time >= 2000):
                self.asteroid_index = 1
                for astroid_objects in self.asteroids:
                    self.remove_game_object(astroid_objects)
            else:
                self.astroid_time += self.dt
                
            for elements in self.asteroids:
                coord = Vector2.unpack(elements.physics_object.pos)
                if (0 > coord[0] > self.widthscreen) or (0 > coord[1] > self.heightscreen):
                    self.remove_game_object(elements)

            coord = self.player.physics_object.pos.unpack()
            if (self.widthscreen-30 < coord[0] < self.widthscreen):
                self.player.physics_object.pos += Vector2(-40,0)
                self.player.physics_object.vel -= 1.5 * self.player.physics_object.vel  #"bounce" of sides
            if (0 < coord[0] < 30): #making sure spaceship cant go out of bounds
                self.player.physics_object.pos += Vector2(40,0)
                self.player.physics_object.vel -= 1.5 * self.player.physics_object.vel  #"bounce" of sides
            if (self.heightscreen-30 < coord[1] < self.heightscreen):
                self.player.physics_object.pos += Vector2(0,-40)
                self.player.physics_object.vel -= 1.5 * self.player.physics_object.vel
            if (0 < coord[1] < 30):
                self.player.physics_object.pos += Vector2(0,40)
                self.player.physics_object.vel -= 1.5 * self.player.physics_object.vel

            for event in pg.event.get():
                self.handle_event(event)

            pg.event.pump()

            self.local_update_game_objects()

            self.physics_manager.update_all(self.dt)

            pg.display.flip()


class Game_Object():
    game_state = None

    def __init__(self):
        self.game_state.game_objects.append(self)

class Level_Manager(Game_Object):
    def __init__(self, frequency = 200, level = 0, level_time = 10000, level_prop = 1, asteroids = 50, random = False, level_text = ""):
        self.level = level
        self.level_prop = level_prop
        self.random = random
        self.level_time = level_time
        self.level_text = level_text
        self.asteroids = asteroids
        self.frequency = frequency
        self.time = 0
        self.asteroid_amount = 75
    
    def local_update(self):
        self.new_level()

    def new_level(self):
        #set level time of 
        if self.time >= 12000:
            self.level += 1
            self.time = 0
            self.level_text = "Level" + str(self.level)
        elif self.game_state.player.health <= 0:
            self.level = 0
            self.asteroid_amount = 75
            self.level_text = "Game over"
            self.game_state.player.health = 3
            self.game_state.points_total = 0
            #also reset 
        else:
            self.time+=self.game_state.dt
            self.level_text = ""
        #set amount of asteroids
        if self.level < 3:
            self.asteroids = list(range(0,50))
        elif (3 <= self.level < 5):
            self.asteroids = list(range(0,75))
        else:
            self.asteroid_amount += 10
            self.asteroids = list(range(0,asteroid_amount))
        #set direction of asteroids
        if self.level < 3:
            self.random = False
        elif (3 <= self.level < 5):
            self.random = True
        else:
            self.random  = random.choice([True, False])
        #set sides at which asteroid appears
        if (self.level%1) or (self.level == 0):
            self.level_prop = 1
        if self.level%2:
            self.level_prop = 2
        if self.level%3:
            self.level_prop = 4
        #asteroid_frequency
        if self.asteroids != 0:
            self.frequency = int(self.level_time)/int(len(self.asteroids))
        return

class Weapon_Manager():
    def __init__(self, gun_cooldown = 1, bullet_damage = 1, bullet_speed = 0.1):
        self.parent = None

        self.gun_cooldown = gun_cooldown #in ms
        self.bullet_damage = bullet_damage
        self.bullet_speed = bullet_speed
        self.last_gunfire_time = 0

    def shoot_gun(self):
        current_time = pg.time.get_ticks()
        shooter = self.parent
        shooter_radius = shooter.rigid_body.radius
        if current_time - self.last_gunfire_time > self.gun_cooldown:
            bullet = Bullet(shooter = shooter, bullet_damage = self.bullet_damage)
            bullet.physics_object.pos = shooter.physics_object.pos + Vector2.vector_from_angle(shooter.physics_object.ang) * shooter_radius
            bullet.physics_object.vel = Vector2.vector_from_angle(shooter.physics_object.ang) * self.bullet_speed
            self.last_gunfire_time = pg.time.get_ticks()

class SpaceShip(Game_Object):
    def __init__(self, health = 3, points_total = 0, physics_object = Physics_Object(), rigid_body = Rigid_Body(), weapon_manager = Weapon_Manager()):
        self.physics_object = physics_object
        self.physics_object.parent = self

        self.rigid_body = rigid_body
        self.rigid_body.parent = self

        self.weapon_manager = weapon_manager
        self.weapon_manager.parent = self

        self.game_state.game_objects.append(self)

        self.health = health
        self.points_total = points_total

class Asteroid(Game_Object):
    def __init__(self, physics_object = Physics_Object(), rigid_body = Rigid_Body()):
        self.physics_object = physics_object
        self.physics_object.parent = self

        self.rigid_body = rigid_body
        self.rigid_body.parent = self

        self.game_state.game_objects.append(self)

class Bullet(Game_Object):
    def __init__(self, physics_object=Physics_Object(mass=2), rigid_body = Rigid_Body(radius=2), bullet_damage = 1, shooter = None):
        self.physics_object = physics_object
        self.physics_object.parent = self

        self.rigid_body = rigid_body
        self.rigid_body.parent = self

        self.bullet_damage = bullet_damage
        self.shooter = shooter

        self.game_state.game_objects.append(self)

game_state = Game_State()
game_state.update()