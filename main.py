import pygame as pg
import physics_engine as pe
from physics_engine import Physics_Object, Rigid_Body, Vector2
import random as rd
import math

class SpaceShip():
        def __init__(self, physics_object = Physics_Object(), rigid_body = Rigid_Body()):
                self.physics_object = physics_object
                self.physics_object.parent = self

                self.rigid_body = rigid_body
                self.rigid_body.parent = self
                


class Asteroid():
        def __init__(self, physics_object = Physics_Object(), rigid_body = Rigid_Body()):
                self.physics_object = physics_object
                self.physics_object.parent = self

                self.rigid_body = rigid_body
                self.rigid_body.parent = self
                

class Bullet():
        def __init__(self, width =2, height=10, physics_object = Physics_Object(), rigid_body = Rigid_Body(color=(255,0,0))):
                self.physics_object = physics_object
                self.width = width
                self.height = height

                self.rigid_body = rigid_body
                self.rigid_body.parent = self

def asteroidGenerator(number_ast, asteroid_frequency, time_asteroid): #set constant initially, increase if wave functionality added
        asteroid_list = []
        for iteration in range(number_ast):
                if time_asteroid > asteroid_frequency: #intended purpose to create an asteroid at time increments of asteroid_frequency
                        momentum = 400
                        mass = rd.randint(60, 100) #avg mass of 80 kg assumed
                        radius = int(mass/4) #with average mass 80, radius average asteroid 20 pixels
                        vel = 40/mass #standard total momentum of 400 , avg 50 velocity in pixel/second,
                        angle = rd.randint(-40, 40) #angle between x and y component velocity
                        ang_vel = 0
                        ang_pos = 0
                        if iteration%4 == 0:
                                pos = Vector2(rd.randint(0,widthscreen), 0) #left handed coordinate system, [x,y], top_screen border
                                vel = Vector2(vel*math.sin(angle), vel*math.cos(angle)) #downward, positive y
                        elif iteration%4 == 1:
                                pos = Vector2(rd.randint(0,widthscreen), heightscreen) #bottom screen border
                                vel = Vector2(vel*math.sin(angle), -vel*math.cos(angle))
                        elif iteration%4 == 2:
                                pos = Vector2(widthscreen, rd.randint(0,heightscreen)) #right screen border
                                vel = Vector2(-vel*math.cos(angle), vel*math.sin(angle))
                        elif iteration%4 == 3:
                                pos = Vector2(0, rd.randint(0,heightscreen)) #left screen border
                                vel = Vector2(vel*math.cos(angle), vel*math.sin(angle))
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
widthscreen = 1920
heightscreen = 1080
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
time_asteroid = 0

while running:
        dt = clock.tick(fps)
        screen.fill((0, 0, 0))
        
        player = SpaceShip(physics_object = Physics_Object(pos = Vector2(200,150)), rigid_body = Rigid_Body(radius = 10, color= (0,255,0)))

        asteroid_frequency = time_per_level/level_one #how often to generate an asteroid
        if time_asteroid > asteroid_frequency:
                asteroids = asteroidGenerator(level_one, asteroid_frequency, time_asteroid)  
                time_asteroid = 0 #reset it to 0 so you can count again
        else:
                time_asteroid += dt # dt is measured in milliseconds, therefore 250 ms = 0.25 seconds
        
        #shoot stuff
        if keys[pg.K_SPACE]:
                generateBullet(player.physics_object.pos, player.physics_object.ang)
        #control the spacecraft
        if keys[pg.K_q]: #pushing q rotates 10 deg positive
                player.physics_object.ang += 10
        if keys[pg.K_e]: #pushing e rotates -10 deg, 0 deg aligned with x-axis
                player.physics_object.ang -= 10
        #if keys[pg.K_w]: go forward
                
        #if keys[pg.K_s]: go backward
        #if keys[pg.K_a]: go left
        #if keys[pg.K_d]: go right
        #close the game
        if keys[pg.K_ESCAPE]:
                running = False

        for event in pg.event.get():
                pass

        for physics_object in Physics_Object.physics_objects:
                physics_object.physics_update(dt)
        
        for rigid_body in Rigid_Body.rigid_bodies:
                rigid_body.draw_body(screen)

        player.physics_object.physics_update(1/60)

        pg.display.flip()
        

        

