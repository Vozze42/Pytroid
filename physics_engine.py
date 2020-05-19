import math
import pygame
import random

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
        return x+y

    def get_angle(self):
        angle = math.atan(self.y/self.x)
        return angle
        
    def unpack(self):
        return [self.x, self.y]
        
class Physics_Object:

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
        Physics_Manager.physics_objects.append(self)

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

    def __init__(self, radius = 1, color = (255,255,255), parent = None, e = 1):
        self.radius = radius
        self.color = color
        self.parent = parent
        self.e = e
        Physics_Manager.rigid_bodies.append(self)

    def draw_body(self, screen):
        if self.parent != None:
            coord = self.parent.physics_object.pos.unpack()
            coord = [int(coord[0]), int(coord[1])]
            pygame.draw.circle(screen, self.color, coord, int(self.radius))

    def collision_detection(self, other):
        other_pos = other.parent.physics_object.pos
        other_radius = other.radius
        own_pos = self.parent.physics_object.pos

        relative_position = other_pos - own_pos
        dist_between_positions = relative_position.mag()

        total_radius = self.radius + other_radius
        if dist_between_positions <= total_radius:
            return True
        else:
            return False

    def collision_response(self,other):
        other_pos = other.parent.physics_object.pos
        other_mass = other.parent.physics_object.mass
        own_pos = self.parent.physics_object.pos
        own_mass = self.parent.physics_object.mass
        own_vel = self.parent.physics_object.vel
        other_vel = other.parent.physics_object.vel
        own_rad = self.radius
        other_rad = other.radius
        own_e = self.e
        other_e = other.e

        total_radius = own_rad + other_rad

        relative_position = other_pos - own_pos
        relative_velocity = other_vel - own_vel

        overlap = relative_position.mag() - total_radius

        e = min(own_e, other_e)

        if relative_position.mag() != 0:
            normal = relative_position / relative_position.mag()

            J = -(1+e)*relative_velocity.dot(normal)/((normal / own_mass + normal / other_mass).dot(normal))

            self.parent.physics_object.vel += -1*J*normal/own_mass
            other.parent.physics_object.vel += 1*J*normal/other_mass

            self.parent.physics_object.pos += normal * overlap/2
            other.parent.physics_object.pos -= normal * overlap/2
        else:
            normal = Vector2(random.randint(0,100),random.randint(0,100))
            normal = normal / normal.mag()

            other.parent.physics_object.pos += (own_rad + other_rad) * normal

class Physics_Manager():
    rigid_bodies = []
    physics_objects = []
    screen = None

    def __init__(self, screen):
        self.screen = screen

    def draw_bodies(self, dt):
        for rigid_body in self.rigid_bodies:
                rigid_body.draw_body(self.screen)
        return

    def update_collisions(self):
        colliding_bodies_lst = []

        #Nested if structure for performance
        for own_body in self.rigid_bodies:
            for other_body in self.rigid_bodies:
                if own_body != other_body and own_body.parent != None and other_body.parent != None: #Bandage solution
                    if own_body.collision_detection(other_body):
                        if [other_body, own_body] not in colliding_bodies_lst: #Use the fact that rigid_bodies is ordered to check if the pair is already accounted for
                            colliding_bodies_lst.append([own_body,other_body])

        for colliding_bodies in colliding_bodies_lst:
            colliding_bodies[0].collision_response(colliding_bodies[1])
        print(colliding_bodies_lst)

        return

    def update_physics(self, dt):
        total_momentum = 0
        for physics_object in self.physics_objects:
                physics_object.physics_update(dt)
                total_momentum += physics_object.vel.mag() * physics_object.mass
        print(total_momentum)
        return

    def remove_strange_things(self):
        for rigid_body in self.rigid_bodies:
            if rigid_body.parent == None:
                self.rigid_bodies.remove(rigid_body)
        
        for physics_object in self.physics_objects:
            if physics_object.parent == None:
                self.physics_objects.remove(physics_object)

    def update_all(self, dt):
        self.remove_strange_things() #bandage solution
        self.update_physics(dt)
        self.update_collisions()
        self.draw_bodies(dt)
        return