import pygame as pg
import physics_engine as pe
from physics_engine import Physics_Manager, Physics_Object, Rigid_Body, Vector2
import random as rd
import math

widthscreen = 1920
heightscreen = 1080

class Game_State():
    def __init__(self):
        self.level_reached = 0
        self.points_total = 0
        self.health = 0
        self.asteroids_broken = 0

        self.game_objects = []
        
        self.fps = 60

        self.running = True
        self.level_one = 10 #ten asteroids in level one
        self.time_per_level = 600 #dt = 1/60 --> t = 10
        self.asteroids = []
        self.bullets = []
        self.time_asteroid = 100
        self.max_asteroids = 10
        self.number_of_asteroids = 0

        #[# asteroids], [level duration (ms) ], [waveprop (how many sides)], [random/non random]

        self.physics_manager = Physics_Manager(self.screen)
        Game_Object.game_state = self
        self.player = SpaceShip(physics_object = Physics_Object(pos = Vector2(200,150)), rigid_body = Rigid_Body(radius = 10, color= (0,255,0)))

    def init_pygame(self):
        pg.init()
        self.screen = pg.display.set_mode((self.widthscreen, self.heightscreen))
        self.clock = pg.time.Clock()

    def collision(self, this_object, other_object):
        if (type(this_object).__name__ == Asteroid and type(other_object).__name__ == Bullet) or (type(other_object).__name__ == Asteroid and type(this_object).__name__ == Bullet):
            if type(this_object).__name__ == Bullet: #
                other_object.health -= 1
                this_object.remove(Bullet) #remove this bullet
                if other_object.health <= 0:
                    other_object.remove(Asteroid) #also remove the asteroid
            else:
                this_object.health -= 1
                other_object.remove(Bullet) #remove this bullet
                if this_object.health <= 0:
                    this_object.remove(Asteroid) #also remove the asteroid

            player.points_total += 1 #is this correct?

        if (type(this_object).__name__ == SpaceShip and type(other_object).__name__ == Asteroid) or (type(other_object).__name__ == SpaceShip and type(this_object).__name__ == Asteroid):
            if this_object == Spaceship:
                this_object.health -= 1
                this_object.physics_object.vel += 0 #velocity needs to stay the same
                otherobject.remove(Asteroid)
            else:
                other_object.health -= 1
                other_object.physics_object.vel += 0 #velocity spaceship needs to stay the same
                this_object.remove(Asteroid)

            #if self.health <=0:
                    #print("Game Over, your score is:" + str(self.points_total))

        return

    def remove_game_object(self, game_object):
        if hasattr(game_object, 'physics_object'):
            self.physics_manager.physics_objects.remove(game_object.physics_object)
        if hasattr(game_object, 'rigid_body'):
            self.physics_manager.rigid_bodies.remove(game_object.rigid_body)
        self.game_objects.remove(game_object)

    
    def update(self):
        while self.running:
            self.dt = self.clock.tick(self.fps)
            self.screen.fill((0, 0, 0))

            asteroid_frequency = self.time_per_level/self.level_one #how often to generate an asteroid
            if self.max_asteroids > len(asteroids) and time_asteroid > asteroid_frequency:
                current_asteroid = asteroidGenerator(number_of_asteroids)
                asteroids.append(current_asteroid)
                time_asteroid = 0
                number_of_asteroids+=1
            else:
                time_asteroid+=dt

            for elements in asteroids:
                coord = Vector2.unpack(elements.physics_object.pos)
                if 0 > coord[0] > widthscreen or 0 > coord[1] > heightscreen:
                    asteroids.remove(elements)

            coord = player.physics_object.pos.unpack()
            if widthscreen-30 < coord[0] < widthscreen or 0 < coord[0] < 30: #making sure spaceship cant go out of bounds
                player.physics_object.vel = Vector2.__mul__(player.physics_object.vel, Vector2(-1, 0)) #"bounce" of sides
            if heightscreen-30 < coord[1] < heightscreen or 0 < coord[1] < 30:
                player.physics_object.vel = Vector2.__mul__(player.physics_object.vel, Vector2(0, -1))

            player_angle = player.physics_object.ang

            vel_add = 1 #instantaneous velocity added


            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    key = event.key
                    #shoot stuff
                    if key == pg.K_SPACE:
                        player.weapon_manager.shoot_gun()
                    #control the spacecraft
                    if key == pg.K_q: #pushing q rotates 10 deg positive
                        player.physics_object.ang_vel += 10
                    if key == pg.K_e: #pushing e rotates -10 deg, 0 deg aligned with x-axis
                        player.physics_object.ang_vel -= 10
                    if key == pg.K_r: #possibility to set ang_vel to zero, remove if fly_by_wire!!!
                        playe.physics_objects.ang_vel = 0
                    if key == pg.K_f: #ossibility to set velocity to zero, remove if fly_by_wire!!!
                        player.physics_object.vel = Vector2(0,0)
                    if key == pg.K_w: #go forward
                        player.physics_object.vel += player.physics_object.vel, Vector2(vel_add*math.cos(player_angle), vel_add*math.sin(player_angle))
                    if key == pg.K_s: #go backward
                        player.physics_object.vel += player.physics_object.vel, Vector2(vel_add*-math.cos(player_angle), vel_add*math.sin(player_angle))
                    if key == pg.K_a: #go left
                        player.physics_object.vel += player.physics_object.vel, Vector2(vel_add*math.sin(player_angle), -vel_add*math.cos(player_angle))
                    if key == pg.K_d: #go right
                        player.physics_object.vel += player.physics_object.vel, Vector2(vel_add*math.sin(player_angle), vel_add*math.cos(player_angle))
                    #close the game
                    if key == pg.K_ESCAPE:
                        running = False


            pg.event.pump()

            physics_manager.update_all(dt)

            pg.display.flip()

            print(game_state.game_objects)


class Game_Object():
    game_state = None

    def __init__(self, game_state):
        self.game_state = game_state

class Level_Manager():
    def __init__(self, level = 0, level_time = 0, level_prop = 1, random = False):
        self.level = []
        self.level_prop = level_prop
        self.random = random
        self.level_time = level_time

    def set_level_props(self):
        self.level = list(range(0,6))
        for levels in self.level:
            if levels <= 3:
                self.random = False
            else:
                self.random = True
        self.level_time
        return

        if self.level <=
        self.waves = [
            [50, 10000, 1, False],
            [50, 10000, 2, False],
            [50, 10000, 4, False],
            [50, 10000, 1, True],
            [50, 10000, 2, True],
            [50, 10000, 4, True]]

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
    def __init__(self, physics_object = Physics_Object(), rigid_body = Rigid_Body(), weapon_manager = Weapon_Manager()):
        self.physics_object = physics_object
        self.physics_object.parent = self

        self.rigid_body = rigid_body
        self.rigid_body.parent = self

        self.weapon_manager = weapon_manager
        self.weapon_manager.parent = self

        self.game_state.game_objects.append(self)

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

def asteroidGenerator(number_ast, waveprop, random): #set constant initially, increase if wave functionality added
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

    current_asteroid = Asteroid(physics_object = Physics_Object(mass = mass, pos = pos, vel = vel), rigid_body = Rigid_Body(radius=radius))

    return current_asteroid

game_state = Game_State()
game_state.update()