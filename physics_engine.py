import math

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

    def __mul__(self, other):
        x = self.x * other
        y = self.y * other
        return Vector2(x,y) 

    def __div__(self, other):
        x = self.x / other
        y = self.y / other
        return Vector2(x,y) 

    def __iadd__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2(x,y) 

class Physics_Object:
    physics_objects = []

    def __init__(self, mass = 1, pos = Vector2(0,0), vel = Vector2(0,0), accel = Vector2(0,0), moi = 1, ang = 0, ang_vel = 0, ang_accel = 0):
        self.mass = mass
        self.moi = moi
        self.pos = pos
        self.vel = vel
        self.accel = accel
        self.ang = ang
        self.ang_vel = ang_vel
        self.ang_accel = ang_accel

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