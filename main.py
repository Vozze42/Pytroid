import pygame 
import physics_engine
from physics_engine import Physics_Object

class SpaceShip():
        def __init__(self, mass = 1, radius = 1, hp = 1, Physics_Object = Physics_Object()):
                self.physics_object = Physics_Object.__init__(self)


class Asteroid():
        def __init__(self, mass = 1, radius = 1, hp = 1, physics_object = Physics_Object()):
                self.physics_object = Physics_Object.__init__(self)
                self.energy = 1 #assuming average mass = 200 kg
                self.points = points #points player gets when asteroid gets destoryed


class Ray():
        def __init__(self, direction, pos): #pos is equal to the center position of the spacecraft
                self.pos  = pos #[x, y]
                self.vel = math.cosvel #[vx, vy]
                impulse = 10 #enough to slow avg astronaut down by ...
                energy = 100 #damage done

pygame.init()
screen = pygame.display.set_mode((400, 300))
done = False
is_blue = True
x = 30
y = 30
clock = pygame.time.Clock()

player = SpaceShip(10,1,[0,0],[0,0],[0,0],0,0,0)

while not done:
        for event in pygame.event.get():
                pass

        player.add_force([100,0])
        player.physics_update(1/60)
        print(player.pos)

        screen.fill((0, 0, 0))

        pygame.display.flip()
        clock.tick(60)

