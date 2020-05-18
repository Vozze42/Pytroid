import pygame as pg
import physics_engine as pe
from physics_engine import Physics_Manager, Physics_Object, Rigid_Body, Vector2
import random as rd
import math

widthscreen = 1920
heightscreen = 1080

class SpaceShip():
        def __init__(self, physics_object = Physics_Object(), rigid_body = Rigid_Body()):
                self.physics_object = physics_object
                self.physics_object.parent = self

                self.rigid_body = rigid_body
                self.rigid_body.parent = self
                
        def inBounds(physics_object = Physics_Object()):
                coord = self.parent.physics_object.pos.unpack()
                velocity = self.parent.physics_object.vel.unpack()
                if widthscreen-30 < coord[0] < widthscreen or 0 < coord[0] < 30: #making sure spaceship cant go out of bounds
                        Vector2.__mul__(velocity, Vector2(-1, 0)) #"bounce" of sides
                if heightscreen-30 < coord[1] < heightscreen or 0 < coord[1] < 30: 
                        Vector2.__mul__(velocity, Vector2(0, -1))
        

class Asteroid():
        def __init__(self, physics_object = Physics_Object(), rigid_body = Rigid_Body()):
                self.physics_object = physics_object
                self.physics_object.parent = self

                self.rigid_body = rigid_body
                self.rigid_body.parent = self

        #def removeAsteroid(self, coord):
        #        if 0 > coord[0] > widthscreen or 0 > coord[1] > heightscreen:

                

class Bullet():
        def __init__(self, width =2, height=10, physics_object = Physics_Object(), rigid_body = Rigid_Body(color=(255,0,0))):
                self.physics_object = physics_object
                self.width = width
                self.height = height

                self.rigid_body = rigid_body
                self.rigid_body.parent = self

def asteroidGenerator(number_ast, asteroid_frequency, time_asteroid): #set constant initially, increase if wave functionality added
        asteroid_list = []
        i = 0
        while i < number_ast:
                if time_asteroid > asteroid_frequency: #intended purpose to create an asteroid at time increments of asteroid_frequency
                        momentum = 400
                        mass = rd.randint(60, 100) #avg mass of 80 kg assumed
                        radius = int(mass/4) #with average mass 80, radius average asteroid 20 pixels
                        vel = 40/mass #standard total momentum of 400 , avg 50 velocity in pixel/second,
                        angle = rd.randint(-40, 40) #angle between x and y component velocity
                        ang_vel = 0
                        ang_pos = 0
                        if i%4 == 0:
                                pos = Vector2(rd.randint(0,widthscreen), 0) #left handed coordinate system, [x,y], top_screen border
                                vel = Vector2(vel*math.sin(angle), vel*math.cos(angle)) #downward, positive y
                        elif i%4 == 1:
                                pos = Vector2(rd.randint(0,widthscreen), heightscreen) #bottom screen border
                                vel = Vector2(vel*math.sin(angle), -vel*math.cos(angle))
                        elif i%4 == 2:
                                pos = Vector2(widthscreen, rd.randint(0,heightscreen)) #right screen border
                                vel = Vector2(-vel*math.cos(angle), vel*math.sin(angle))
                        elif i%4 == 3:
                                pos = Vector2(0, rd.randint(0,heightscreen)) #left screen border
                                vel = Vector2(vel*math.cos(angle), vel*math.sin(angle))
                i += 1
                asteroid_list.append(Asteroid(physics_object = Physics_Object(mass = mass, pos = pos, vel = vel, momentum=50), rigid_body = Rigid_Body(radius=radius)))
                
        return asteroid_list

def generateBullet(pos_player, angle):
        radius = 2
        momentum = 200
        mass = 2
        vel = 100 #momentum divided by mass, momentum bullet 50
        velocity = Vector2(vel*math.cos(angle), vel*math.sin(angle))
        return Bullet(physics_object=Physics_Object(mass=mass, vel=velocity, momentum=momentum), rigid_body = Rigid_Body(radius=radius))
        

pg.init()
screen = pg.display.set_mode((widthscreen, heightscreen))
done = False
is_blue = True
x = 30
y = 30
clock = pg.time.Clock()
fps = 60

#initial state vars
running = True
keys = pg.key.get_pressed()
level_one = 10 #ten asteroids in level one
time_per_level = 600 #dt = 1/60 --> t = 10
asteroids = []
time_asteroid = 100
max_astroids = 50
number_of_astroids = 0

physics_manager = Physics_Manager(screen)
player = SpaceShip(physics_object = Physics_Object(pos = Vector2(200,150)), rigid_body = Rigid_Body(radius = 10, color= (0,255,0)))

while running:
        dt = clock.tick(fps)
        screen.fill((0, 0, 0))

        asteroid_frequency = time_per_level/level_one #how often to generate an asteroid
        if time_asteroid > asteroid_frequency and max_astroids > number_of_astroids:
                asteroids = asteroidGenerator(level_one, asteroid_frequency, time_asteroid)
                number_of_astroids += len(asteroids)
                time_asteroid = 0 #reset it to 0 so you can count again
        else:
                time_asteroid += dt # dt is measured in milliseconds, therefore 250 ms = 0.25 seconds
        
        for elements in asteroids:
                coord = Vector2.unpack(elements.physics_object.pos)
                if 0 > coord[0] > widthscreen or 0 > coord[1] > heightscreen:
                        asteroids.remove(elements)

        player_angle = player.physics_object.ang

        vel_add = 1 #instantaneous velocity added
        #shoot stuff
        if keys[pg.K_SPACE]:
                generateBullet(player.physics_object.pos, player.physics_object.ang)
        #control the spacecraft
        if keys[pg.K_q]: #pushing q rotates 10 deg positive
                player.physics_object.ang_vel += 10
        if keys[pg.K_e]: #pushing e rotates -10 deg, 0 deg aligned with x-axis
                player.physics_object.ang_vel -= 10
        if keys[pg.K_r]: #possibility to set ang_vel to zero, remove if fly_by_wire!!!
                playe.physics_objects.ang_vel = 0
        if keys[pg.K_f]: #ossibility to set velocity to zero, remove if fly_by_wire!!!
                player.physics_object.vel = Vector2(0,0)
        if keys[pg.K_w]: #go forward
                player.physics_object.vel = Vector2.__add__(player.physics_object.vel, Vector2(vel_add*math.cos(player_angle), vel_add*math.sin(player_angle)))
        if keys[pg.K_s]: #go backward
                player.physics_object.vel = Vector2.__add__(player.physics_object.vel, Vector2(vel_add*-math.cos(player_angle), vel_add*math.sin(player_angle)))
        if keys[pg.K_a]: #go left
                player.physics_object.vel = Vector2.__add__(player.physics_object.vel, Vector2(vel_add*math.sin(player_angle), -vel_add*math.cos(player_angle)))
        if keys[pg.K_d]: #go right
                player.physics_object.vel = Vector2.__add__(player.physics_object.vel, Vector2(vel_add*math.sin(player_angle), vel_add*math.cos(player_angle)))
        #close the game
        if keys[pg.K_ESCAPE]:
                running = False

        for event in pg.event.get():
                pass

        physics_manager.update_all(dt)

        pg.display.flip()
        

        

