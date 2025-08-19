import numpy as np
from sai_mujoco.envs.football import FootballEnv
import sai_mujoco.utils.rotations as R

class GoalKeeper(FootballEnv):

    env_name: str = "football"
    scene_name: str = "base_scene"
    default_camera_config = {
        "distance": 7.8,
        "azimuth": -160,
        "elevation": -20.0,
        "lookat": np.array([-8.0, 0.0, 0.35]),
    }

    reward_config = {
        "distance_to_ball": 5.0,
        "approach_ball_reward":10.0,
        "inside_goal": -20.0,
        "is_alive": 2.0,
    }
    
    def compute_terminated(self):

        terminated = super().compute_terminated()
        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        inside_goal = self.ball_inside_goal(ball_xpos)
        outside_field = self.is_outside_field(ball_xpos, inside_goal)

        return bool(terminated or outside_field or inside_goal or self.time_after_contact > 100.0)
        
    def compute_reward(self):

        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        self.count_robot_ball_contacts()

        if self.robot_contact:
            self.time_after_contact += 1

        distance_reward, approach_ball_vel = self.approach_velocity_reward()
        approach_ball_vel = 2.0 if self.robot_contact else approach_ball_vel
        distance_reward = 1.0 if self.robot_contact else distance_reward

        is_alive = min(15, max(0.5, self.time_after_contact*0.5))        
        inside_goal = self.ball_inside_goal(ball_xpos)

        rew_reward = {
            "distance_to_ball": distance_reward,
            "approach_ball_reward": approach_ball_vel,
            "inside_goal": inside_goal,
            "is_alive": is_alive,
        }
                
        return rew_reward
    
    def approach_velocity_reward(self):
        
        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        robot_xpos = self.robot_model.sim.data.get_site_xpos(self._root_site)
        robot_xvelp = self.robot_model.sim.data.get_site_xvelp("imu")

        vec_to_ball = ball_xpos - robot_xpos
        dist_to_ball = np.linalg.norm(vec_to_ball)

        distance_reward = (1 - self.robot_contact)*(1 - np.tanh(dist_to_ball, dtype=np.float32))

        direction_to_ball = ball_xpos - robot_xpos        # Vector pointing from robot to ball
        approach_velocity_reward = (1 - self.robot_contact)*np.dot(robot_xvelp, direction_to_ball)

        return distance_reward, approach_velocity_reward

    def step(self, *args):
        
        self.move_ball(self.velocity)
        observation, reward, terminated, truncated, info = super().step(*args)

        return observation, reward, terminated, truncated, info
    
    def move_ball(self, velocity):
        """Apply a sinusoidal velocity to the actuator."""
        self.robot_model.sim.data.set_joint_qvel("env:ball", velocity) 
    
    def _reset_env(self):
        
        super()._reset_env()
        self._change_team()
        self.get_velocity()
        self.move_ball(self.velocity)
        self.time_after_contact = 0
        self.robot_contact = False

    def get_velocity(self):
        
        start_pos = np.array([self.parameters_dict["team_parameters"][self.current_team]["goal"]["centre"], 0, 0])
        goal_x = -self.parameters_dict["env_parameters"]["field"]["length"]*self.direction
        goal_y_range = [-self.parameters_dict["env_parameters"]["goal"]["width"], self.parameters_dict["env_parameters"]["goal"]["width"]]
        goal_z =  1.0

        # Sample a random goal position within the goal region
        goal_y = self.np_random.uniform(*goal_y_range)
        goal_pos = np.array([goal_x, goal_y, goal_z])

        # Direction vector from start to goal
        direction = goal_pos - start_pos

        # Normalize direction and scale with speed
        speed = self.np_random.uniform(1.0, 2.0)  # Adjust speed range as needed
        unit_direction = direction / np.linalg.norm(direction)
        velocity = unit_direction * speed

        # Final 6D velocity vector: [vx, vy, vz, wx, wy, wz]
        self.velocity = np.array([velocity[0], velocity[1], velocity[2], 0.0, 0.0, 0.0])

    def _change_team(self):
        
        robot_qpos = self.robot_model.sim.data.get_joint_qpos("root")
        ball_qpos = self.robot_model.sim.data.get_joint_qpos("env:ball")
        ball_qpos[0] = self.parameters_dict["team_parameters"][self.current_team]["goal"]["centre"]

        robot_qpos[0] = ball_qpos[0] - 2*self.direction
        robot_orientation = np.array(self.rotation)
        robot_orientation[-1] += 3.14
        robot_qpos[3:] = R.euler2quat(robot_orientation)

        self.robot_model.sim.data.set_joint_qpos("root", robot_qpos)
        self.robot_model.sim.data.set_joint_qpos("env:ball", ball_qpos)
    
    def count_robot_ball_contacts(self):

        ball_geom_id = self.robot_model.sim.model.geom("ball").id
        for i in range(self.robot_model.sim.data.ncon):
            contact = self.robot_model.sim.data.contact[i]
            if (contact.geom1 in self.robot_geom_ids and contact.geom2 == ball_geom_id) or \
            (contact.geom2 in self.robot_geom_ids and contact.geom1 == ball_geom_id):
                self.robot_contact = True
                break

    def _get_info(self):

        return {
            "success": self.time_after_contact > 100.0
        }