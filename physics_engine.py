import math
import pygame

class Vector2:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    
    def __str__(self):
        return "({0},{1})".format(self.x,self.y)
    
    def __add__(self,other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2(x,y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Vector2(x,y)

    def __rsub__(self, other):   # not commutative operation
        other = Vector2(other)
        return other - self

    def __mul__(self, other):
        x = self.x * other
        y = self.y * other
        return Vector2(x,y) 

    __rmul__ = __mul__   # commutative operation

    def __truediv__(self, other):
        x = self.x / other
        y = self.y / other
        return Vector2(x,y) 

    def __iadd__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2(x,y) 

    def __pow__(self, other):
        x = self.x ** other
        y = self.y ** other
        return Vector2(x,y)

    def mag(self):
        mag = math.sqrt(self.x**2 + self.y**2)
        return mag

    def dot(self,other):
        x = self.x * other.x
        y = self.y * other.y
        return Vector2(x,y)

    def get_angle(self):
        angle = math.atan(self.y/self.x)
        return angle

    def unpack(self):
        return [self.x, self.y]

class Physics_Object:
    physics_objects = []

    def __init__(self, mass = 1, pos = Vector2(0,0), vel = Vector2(0,0), accel = Vector2(0,0), moi = 1, ang = 0, ang_vel = 0, ang_accel = 0, momentum = 0, parent = None):
        self.mass = mass
        self.moi = moi
        self.pos = pos
        self.vel = vel
        self.accel = accel
        self.ang = ang
        self.ang_vel = ang_vel
        self.ang_accel = ang_accel
        self.momentum = momentum
        self.parent = parent

        self.forces = []
        self.physics_objects.append(self)

    def add_force(self, force):
        self.forces.append(force)

    def physics_update(self, dt):
        for force in self.forces:
            self.accel += force / self.mass
        self.vel += self.accel * dt
        self.pos += self.vel * dt
        self.accel = Vector2()
        self.ang_vel += self.ang_accel * dt
        self.ang += self.ang_vel * dt
        if self.ang > 180:
            self.ang -= 360 #set angular position with switch point at 180 deg
        if self.ang < -180:
            self.ang += 360

class Rigid_Body():
    rigid_bodies = []

    def __init__(self, radius = 1, color = (255,255,255), parent = None):
        self.radius = radius
        self.color = color
        self.parent = parent
        self.rigid_bodies.append(self)

    def draw_body(self, screen):
        if self.parent != None:
            coord = self.parent.physics_object.pos.unpack()
            coord = [int(coord[0]), int(coord[1])]
            while 0 <= coord[0] <= 400 and 0 <= coord[1] <= 300: #is this correct??
                pygame.draw.circle(screen, self.color, coord, int(self.radius))