import pygame 
import physics_engine as pe
import random as rd
import math

class SpaceShip(physics.Physics_Object):
        def __init__(self, mass, radius, pos, vel, accel, ang_pos, ang_vel, ang_accel):
                physics.Physics_Object.__init__(self, mass, radius, pos, vel, accel, ang_pos, ang_vel, ang_accel)


class Asteroid(physics.Physics_Object):
        def __init__(self, mass, radius, pos, vel, accel, ang_pos, ang_vel, ang_accel, points):
                physics.Physics_Object.__init__(self, mass, radius, pos, vel, accel, ang_pos, ang_vel, ang_accel, energy)


class Ray():
        def __init__(self, direction, pos): #pos is equal to the center position of the spacecraft
                self.pos  = pos #[x, y]
                self.vel = math.cosvel #[vx, vy]
                energy = 100 #damage done

def asteroidGenerator(asteroids): #set constant initially, increase if wave functionality added
        mass = rd.randint(60, 100) #avg mass of 80 kg assumed
        radius = mass/4 #with average mass 80, radius average asteroid 20 pixels
        vel = 400/mass#standard total momentum of .... , velocity in pixel/dt
        angle = rd.randint(-40, 40) #angle between x and y component velocity
        ang_vel = 0
        ang_pos = 0
        if asteroids%4 == 0:
                pos = [rd.randint(0,400), 0] #left handed coordinate system, [x,y], top_screen border
                vel = [vel*math.sin(angle), vel*math.cos(angle)] #downward, positive y
        elif asteroids%4 == 1:
                pos = [400, rd.randint(0,300)] #right screen border
                [-vel*math.cos(angle), vel*math.sin(angle)]
        elif asteroids%4 == 2:
                pos = [rd.randint(0,400), 300] #bottom screen border
                vel = [vel*math.sin(angle), -vel*math.cos(angle)]
        elif asteroids%4 == 3:
                pos = [0, rd.randint(0,300)] #left screen border
                vel = [vel*math.cos(angle), vel*math.sin(angle)]
        return Asteroid(mass, radius, pos, vel, 0, 0, 0, 0) #add properties to asteroid asteroid pe.drawCircle(radius)

pygame.init()
widthscreen = 400
heightscreen = 300
screen = pygame.display.set_mode((400, 300))
done = False
is_blue = True
x = 30
y = 30
clock = pygame.time.Clock()

#initial state vars
running = True #use this method??
keys = pg.key.get_pressed()
level_one = 10 #ten asteroids in level one

while running:
        player = SpaceShip(10,1,[0,0],[0,0],[0,0],0,0,0) #spawn at center of screen?
        
        for level in range(0,1): #just 1 level for now
                #now done simultaneously, should be in time steps!!!
                for asteroids in level_one:
                        asteroid = asteroidGenerator(asteroids)
                        pe.drawCircle(asteroid.radius)
                asteroids_level +=1

        if keys[pe.K_ESCAPE]:
                running = False


while not done:
        for event in pygame.event.get():
                pass

        player.add_force([100,0])
        player.physics_update(1/60)
        print(player.pos)

        screen.fill((0, 0, 0))

        pygame.display.flip()
        clock.tick(60)

