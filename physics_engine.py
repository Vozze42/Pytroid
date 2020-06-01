#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Servaas & Lennart
"""

import math
import pygame
import random
import os

class Vector2:
    """Self-written class for vector manipulation"""
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

    def pseudo_cross(self,other):
        x = self.x * other.x
        y = self.y * other.y
        return Vector2(x,y)

    def get_angle(self):
        angle = math.atan2(self.y,self.x)
        return angle
        
    def unpack(self):
        return [self.x, self.y]
    
    def vector_from_angle(self, angle):
        x = math.cos(angle)
        y = math.sin(angle)
        return Vector2(x,y)
        
class Physics_Object:
    #class for managing all physics
    def __init__(self, mass = 1, pos = Vector2(0,0), vel = Vector2(0,0), accel = Vector2(0,0), moi = 1, ang = 0, ang_vel = 0, ang_accel = 0, parent = None):
        self.mass = mass
        self.moi = moi
        self.pos = pos
        self.vel = vel
        self.accel = accel
        self.ang = ang
        self.ang_vel = ang_vel
        self.ang_accel = ang_accel
        self.parent = parent

        self.forces = []
        self.moments = []
        Physics_Manager.physics_objects.append(self)

    def add_force(self, force):
        self.forces.append(force)

    def add_moment(self, moment):
        self.moments.append(moment)

    def set_momentum(self, momentum):
        velocity_direction = self.vel / self.vel.mag()
        new_velocity = momentum / self.mass
        self.vel = velocity_direction * new_velocity

    def physics_update(self, dt):
        #updates physics based on forces
        for force in self.forces:
            self.accel += force / self.mass
        self.vel += self.accel * dt
        self.pos += self.vel * dt
        self.accel = Vector2()

        for moment in self.moments:
            self.ang_accel += moment / self.moi
        self.ang_vel += self.ang_accel * dt
        self.ang += self.ang_vel * dt

        self.forces = []
        self.moments = []
        self.accel = Vector2(0,0)
        self.ang_accel = 0
        #makes sure angles stay between 0 and 2*pi
        while self.ang >= 2*math.pi:
            self.ang -= 2*math.pi
        while self.ang < 0:
            self.ang += 2*math.pi

class Rigid_Body():
    #class mainly for collision detection and response
    def __init__(self, radius = 1, parent = None, e = 1):
        self.radius = radius
        self.parent = parent
        self.e = e
        self.collided = []

        Physics_Manager.rigid_bodies.append(self)

    def collision_detection(self, other):
        #detects whether or not a collision takes place, 
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
        #regulates what happens when objects collide (energy transfer, relative speeds etc.)
        if hasattr(self.parent, "on_collision"):
            self.parent.on_collision(other.parent)
        if hasattr(other.parent, "on_collision"):
            other.parent.on_collision(self.parent)

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
    render_images = []
    render_circles = []
    screen = None

    def __init__(self, screen):
        self.screen = screen

    def draw_bodies(self):
        #renders all images and circles
        for render_image in self.render_images:
            render_image.render_img(self.screen)

        for render_circle in self.render_circles:
            render_circle.render_circle(self.screen)
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

        return

    def update_physics(self, dt):
        #updates physics of all physics objects
        total_momentum = 0
        for physics_object in self.physics_objects:
            if physics_object.parent != None: #Bandage solution
                physics_object.physics_update(dt)
        return

    def update_all(self, dt):
        #includes all update functions, called in Game_State to update all physics
        self.update_physics(dt)
        self.update_collisions()
        self.draw_bodies()
        return

class Render_Circle():
    """Function for rendering circles, was frequently used at beginning stages of development"""
    def __init__(self, radius = 0, color = (255,255,255), parent = None):
        self.radius = radius
        self.color = color
        self.parent = parent
        self.collided = []

        Physics_Manager.render_circles.append(self)

    def render_circle(self, screen):
        if self.parent != None:
            coord = self.parent.physics_object.pos.unpack()
            coord = [int(coord[0]), int(coord[1])]
            pygame.draw.circle(screen, self.color, coord, int(self.radius))


class Render_Image():
    """Makes it easy to initialize, scale, rotate and render images in main.py"""
    def __init__(self, image, size = None, scalar_size= None, ang = None, parent = None):
        self.image = image
        if size != None:
            self.image = self.scale_image(size)
        if ang != None:
            self.image = self.rotate_image(ang) 
        if scalar_size != None:
            self.image = self.scalar_scale_image(scalar_size)
        self.size = size
        self.image_for_angle = []
        
        Physics_Manager.render_images.append(self)

    def scalar_scale_image(self, scalar_size):
        current_size = self.image.get_rect().size
        new_size = (int(current_size[0] * scalar_size), int(current_size[1] * scalar_size))
        image = pygame.transform.scale(self.image, new_size)
        return image

    def scale_image(self, size):
        image = pygame.transform.scale(self.image, (int(size[0]), int(size[1])))
        return image

    def rotate_image(self, rot_ang):
        image = pygame.transform.rotate(self.image, myround(math.degrees(-1*rot_ang),1)) #-1 to convert from right handed to left handed
        return image

    def render_img(self, screen):
        if self.parent != None:
            coord = self.parent.physics_object.pos.unpack()
            coord = [int(coord[0]), int(coord[1])]
            self.getrect = self.image.get_rect()
            self.getrect.center = (coord[0], coord[1])
            if self.parent.physics_object.ang == 0:
                screen.blit(self.image, self.getrect) 
            
            if self.parent.physics_object.ang != 0:
                center = (coord[0], coord[1])
                rotated_image = pygame.transform.rotate(self.image, myround(math.degrees(-1*self.parent.physics_object.ang),1)) #-1 to convert from right handed to left handed
                new_rect = rotated_image.get_rect(center = center)

                screen.blit(rotated_image, new_rect)

#manages, converts, prepares images for use in main.py
class Image_Manager():
    def __init__(self, image_folder = "", asteroid_path = ""):
        self.image_folder = image_folder
        self.asteroid_path = asteroid_path
        self.prepare_images()

    def get_and_convert_images(self, path):
        images = {}
        files = os.listdir(path)
        for file in files:
            joint_path = os.path.join(path, file)
            if os.path.isfile(os.path.join(path, file)):
                image = pygame.image.load(joint_path).convert_alpha()
                images[file] = image

        return images

    def prepare_images(self):
        self.images = self.get_and_convert_images(self.image_folder)
        self.asteroids = self.get_and_convert_images(self.asteroid_path)

class Ray():
    def cast_ray(self, start_pos, direction, widthscreen, heightscreen, step = 5):
        norm_direction = direction / direction.mag()
        collisions = []
        beyond_edge = False
        i = 0
        while not beyond_edge:
            check_pos = start_pos + direction * i*step
            if check_pos.x > 0 and check_pos.x < widthscreen and check_pos.y > 0 and check_pos.y < heightscreen:
                for rigid_body in Physics_Manager.rigid_bodies:
                    radius = rigid_body.radius
                    pos = rigid_body.parent.physics_object.pos
                    distance_vec = pos - check_pos
                    distance = distance_vec.mag()
                    if distance < radius:
                        if len(collisions) > 1:
                            if collisions[len(collisions)-1] != rigid_body:
                                collisions.append(rigid_body)
                        else:
                            collisions.append(rigid_body)
            else:
                beyond_edge = True
            i += 1
        return collisions 

#function sets mixer channels for all different soudns played in the game.
def play_sound(filepath):
    sound = pygame.mixer.Sound(filepath)
    if filepath == "./sounds/fire.wav":
        pygame.mixer.Channel(0).play(pygame.mixer.Sound(filepath))
    elif filepath == "./sounds/bangMedium.wav":
        pygame.mixer.Channel(1).play(pygame.mixer.Sound(filepath))
    elif filepath == "./sounds/bangSmall.wav":
        pygame.mixer.Channel(2).play(pygame.mixer.Sound(filepath))
    elif filepath == "./sounds/bangLarge.wav":
        pygame.mixer.Channel(3).play(pygame.mixer.Sound(filepath))
    if filepath == "./sounds/thrust.wav":
        pygame.mixer.Channel(4).play(pygame.mixer.Sound(filepath))
        sound.set_volume(0.16)

#function for drawing text on the display
def draw_text(text, size, color, position, middle, screen):
        text = str(text)

        default_font = pygame.font.get_default_font()
        font = pygame.font.Font(default_font, size)

        textsurface = font.render(text, False, color)
        if middle:
            offset = textsurface.get_size()
            position = (position[0] - offset[0] / 2, position[1] - offset[1] / 2)

        screen.blit(textsurface, position)

#function for rounding numbers to a certain base
def myround(x, base):
        return base * round(x/base)
