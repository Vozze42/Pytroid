def fly_by_wire_speed(self):
        player = self.parent
        player_physics = self.parent.physics_object
        
        if not self.forward and player_physics.vel.y > 0: #go forward = up
            force_to_add = Vector2(0, 1)*min(abs(self.thrust_force*self.correction_boost*player_physics.vel.y), self.thrust_force*self.correction_boost)*-1 
            player_physics.add_force(force_to_add)
        if not self.back and player_physics.vel.y < 0: #go backward
            force_to_add = Vector2(0, -1)*min(abs(self.thrust_force*self.correction_boost*player_physics.vel.y), self.thrust_force*self.correction_boost)*-1 
            player_physics.add_force(force_to_add)
        if not self.left and player_physics.vel.x < 0: #go left
            force_to_add = Vector2(-1,0)*min(abs(self.thrust_force*self.correction_boost*player_physics.vel.x), self.thrust_force*self.correction_boost)*-1 
            player_physics.add_force(force_to_add)
        if not self.right and player_physics.vel.x > 0: #go right
            force_to_add = Vector2(1,0)*min(abs(self.thrust_force*self.correction_boost*player_physics.vel.x), self.thrust_force*self.correction_boost)*-1 
            player_physics.add_force(force_to_add)
        """
        currently not necessary because all thrust directions have the same thrust, re-add if different thrust directions have different thrust levels:
        if self.reference_frame == "local":
            player_forward = Vector2().vector_from_angle(player_physics.ang)
            if not self.forward: #go forward
                force_to_add = player_forward*self.thrust_force*self.correction_boost*-1
                player_physics.add_force(force_to_add)
            if not self.back: #go backward
                force_to_add = player_forward*-self.thrust_force*self.correction_boost*-1
                player_physics.add_force(force_to_add)
            if not self.left: #go left
                player_left = Vector2().vector_from_angle(player_physics.ang-0.5*math.pi)
                force_to_add = player_left*self.thrust_force*self.correction_boost*-1 
                player_physics.add_force(force_to_add)
            if not self.right: #go right
                player_right = Vector2().vector_from_angle(player_physics.ang+0.5*math.pi)
                force_to_add = player_right*self.thrust_force*self.correction_boost*-1
                player_physics.add_force(force_to_add)
        """