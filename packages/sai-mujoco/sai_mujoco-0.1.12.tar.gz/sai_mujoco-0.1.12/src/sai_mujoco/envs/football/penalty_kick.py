import mujoco
import numpy as np
from sai_mujoco.envs.football import FootballEnv
import sai_mujoco.utils.rotations as R

class PenaltyKick(FootballEnv):
    r"""

    ## Description

    Penalty Kick tasks a humanoid robot with executing a simplified penalty kick in a soccer environment. The robot must approach 
    the ball, position itself for an optimal strike, and apply controlled force to direct the ball toward the opponent’s goal. Throughout 
    the episode, it must balance offensive play with precision, generating velocity toward the goal while avoiding penalties such as 
    going offside, making excessive or inefficient ball contacts and falling.

    The task demands precise positioning to close in on the ball, dynamic control to deliver an effective and well-aimed kick, and strategic 
    movement to navigate the field, all within a continuous and high-dimensional action and observation space.

    ## Observation Space
    The observation space consists of the following parts (in order):

    - *qpos:* Position values of the robot's body parts. The dimensionality depends on the robot's joint configuration.
    - *qvel:* The velocities of these individual body parts (their derivatives). The dimensionality depends on the robot's joint configuration.
    - *field_dimensions (5 elements):* Field length, width, goal width, goal height, and goal depth.
    - *ball_xpos (3 elements):* The ball’s position in the world frame.
    - *ball_velp (3 elements):* The ball’s linear velocity in the world frame.
    - *ball_velr (3 elements):* The ball’s angular velocity (rotation) in the world frame.
    - *player_team (2 elements):* One-hot encoded vector indicating the player’s team.
    - *ball_to_goal_relpos* (3 elements):* Vector from the ball to the center of the goal.

    The order of elements in the observation space related to the environment is as follows -

    | Num | Observation                   | Min  | Max | Type (Unit)              |
    | --- | ----------------------------- | ---- | --- | ------------------------ |
    | 0   | Field length                  | -Inf | Inf | length (meters)          |
    | 1   | Field width                   | -Inf | Inf | width (meters)           |
    | 2   | Goal width                    | -Inf | Inf | width (meters)           |
    | 3   | Goal height                   | -Inf | Inf | height (meters)          |
    | 4   | Goal depth                    | -Inf | Inf | depth (meters)           |
    | 5   | Ball x-coordinate             | -Inf | Inf | position (meters)        |
    | 6   | Ball y-coordinate             | -Inf | Inf | position (meters)        |
    | 7   | Ball z-coordinate             | -Inf | Inf | position (meters)        |
    | 8   | Ball linear velocity x        | -Inf | Inf | velocity (m/s)           |
    | 9   | Ball linear velocity y        | -Inf | Inf | velocity (m/s)           |
    | 10  | Ball linear velocity z        | -Inf | Inf | velocity (m/s)           |
    | 11  | Ball angular velocity x       | -Inf | Inf | angular velocity (rad/s) |
    | 12  | Ball angular velocity y       | -Inf | Inf | angular velocity (rad/s) |
    | 13  | Ball angular velocity z       | -Inf | Inf | angular velocity (rad/s) |
    | 14  | Player team (one-hot: team 0) | 0    | 1   | binary indicator         |
    | 15  | Player team (one-hot: team 1) | 0    | 1   | binary indicator         |
    | 16  | Ball-to-goal relative x       | -Inf | Inf | position difference (m)  |
    | 17  | Ball-to-goal relative y       | -Inf | Inf | position difference (m)  |
    | 18  | Ball-to-goal relative z       | -Inf | Inf | position difference (m)  |

    ## Rewards

    The reward components include:

        1. `r_robot_distance_ball` (weight: 10.0): Encourages the robot to reduce its distance to the ball for better control.
        2. `r_ball_vel_twd_goal` (weight: 1.0): Rewards the ball’s velocity towards the opponent’s goal, promoting offensive play.
        3. `r_goal_scored` (weight: +25.0): Provides a large positive reward when the ball successfully enters the goal.
        4. `r_offside` (weight: -10.0): Penalizes when the ball is out of bounds or in an offside position, discouraging unproductive positioning.
        5. `r_ball_hits` (weight: -1.0): Applies a small penalty for repeated ball contacts by the same robot to encourage efficient play rather than random kicking.
        6. `r_robot_fallen` (weight: -15.0): Penalizes the robot if it falls, incentivizing stable movement.

    `info` contains the success parameter if the given episode succeeded.

    ##Episode End
    ### Termination

    The current episode should terminate based on below termination criteria defined as follow:
        1. The ball successfully crosses the goal line between the posts and under the crossbar.
        2. The ball is found in an offside position as determined by the environment’s offside detection logic.
        3. The humanoid agent’s torso height moves outside the allowed range, indicating a fall or collapse.
        4. The physics simulation produces invalid numerical values (e.g., `NaN`), making further computation unreliable.

    ### Truncation
    The default duration of an episode is 5000 timesteps.

    """
    env_name: str = "football"
    scene_name: str = "base_scene"
    default_camera_config = {
        "distance": 7.8,
        "azimuth": -160,
        "elevation": -20.0,
        "lookat": np.array([-8.0, 0.0, 0.35]),
    }

    reward_config = {
        "robot_distance_ball": 10.0,
        "ball_vel_twd_goal": 1.0,
        "goal_scored": 25.0,
        "offside": -10.0,
        "ball_hits": -1.0,
        "robot_fallen": -10.0
    }

    def __init__(self, *args, **kwargs):
        self.ball_hits_by_robot = 0
        self._ball_contact_active = False

        super().__init__(*args, **kwargs)

    def _get_env_obs(self):

        field_envs = super()._get_env_obs()
        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        goal_xpos = self.robot_model.sim.data.get_site_xpos("goal_post_south")
        
        ball_goal_rel = goal_xpos - ball_xpos

        obs = np.concatenate([field_envs, ball_goal_rel],
            dtype=np.float32,
        )

        return obs
    
    def compute_terminated(self):

        terminated = super().compute_terminated()
        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        inside_goal = self.ball_inside_goal(ball_xpos)
        outside_field = self.is_outside_field(ball_xpos, inside_goal)

        return bool(terminated or outside_field or inside_goal)
    
    def compute_penalty_reward(self,ball_xpos, ball_inside_goal, site="goal_post_south"):

        robot_xpos = self.robot_model.sim.data.get_site_xpos(f"imu")
        ball_velp = self.robot_model.sim.data.get_site_xvelp("ball")
        goal_xpos = self.robot_model.sim.data.get_site_xpos(site)

        distance_robot_ball = self.calculate_distance_ball(robot_xpos, ball_xpos)

        ball_vel_twd_goal = self.velocity_toward_goal(ball_velp, goal_xpos)
        offside = self.is_outside_field(ball_xpos, ball_inside_goal)

        self.count_robot_ball_contacts()

        distance_robot_ball = 1.5 if self.ball_hits_by_robot > 0 else distance_robot_ball
        ball_hits = np.log1p(max(0, self.ball_hits_by_robot - 1))
        
        height = self.robot_model.sim.data.get_site_xpos(self._root_site)[2]
        has_fallen = self.has_robot_fallen(height)

        raw_reward = {
        "robot_distance_ball": distance_robot_ball,
        "ball_vel_twd_goal": ball_vel_twd_goal,
        "offside": offside,
        "ball_hits": ball_hits,
        "robot_fallen": has_fallen
        }

        return raw_reward
    
    def count_robot_ball_contacts(self):

        ball_geom_id = self.robot_model.sim.model.geom("ball").id
        new_contact = False
        for i in range(self.robot_model.sim.data.ncon):
            contact = self.robot_model.sim.data.contact[i]
            if (contact.geom1 in self.robot_geom_ids and contact.geom2 == ball_geom_id) or \
            (contact.geom2 in self.robot_geom_ids and contact.geom1 == ball_geom_id):
                new_contact = True
                break

        if new_contact and not self._ball_contact_active:
        # It's a new contact event
            self.ball_hits_by_robot += 1
            self._ball_contact_active = True

        elif not new_contact and self._ball_contact_active:
            # Contact has ended
            self._ball_contact_active = False
        
    def compute_reward(self):
        
        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        ball_inside_goal = self.ball_inside_goal(ball_xpos)

        raw_reward = self.compute_penalty_reward(ball_xpos, ball_inside_goal)

        raw_reward.update(
            {
                "goal_scored": ball_inside_goal,
            }
        )
        
        return raw_reward
    
    def calculate_distance_ball(self, robot_xpos, ball_xpos):

        distance = np.linalg.norm(robot_xpos - ball_xpos)
        distance = 1 - np.tanh(distance, dtype=np.float32)
        return distance
        
    def velocity_toward_goal(self, ball_velp, goal_xpos):

        goal_plan_vertices = np.array([
            [goal_xpos[0],-self.parameters_dict["env_parameters"]["goal"]["width"],0.0],
            [goal_xpos[0],self.parameters_dict["env_parameters"]["goal"]["width"],0.0],
            [goal_xpos[0],-self.parameters_dict["env_parameters"]["goal"]["width"],self.parameters_dict["env_parameters"]["goal"]["height"]]
        ])  

        normal = np.cross(goal_plan_vertices[1] - goal_plan_vertices[0], goal_plan_vertices[2] - goal_plan_vertices[1])
        normal = normal / np.linalg.norm(normal)  # normalize

        vel_towards_goal = -np.dot(ball_velp, normal)

        return vel_towards_goal  # could be negative if going away
    
    def _reset_env(self):
        """
        Reset the environment to an initial state.
        """
        super()._reset_env()
        self.ball_hits_by_robot = 0
        self._ball_contact_active = False
        self._change_team()

    def _change_team(self):
        
        robot_qpos = self.robot_model.sim.data.get_joint_qpos(f"root")
        ball_qpos = self.robot_model.sim.data.get_joint_qpos("env:ball")
        ball_qpos[0] = self.parameters_dict["team_parameters"][self.current_team]["goal"]["centre"]

        robot_qpos[0] = ball_qpos[0] + 2*self.direction
        robot_orientation = np.array(self.rotation)
        robot_qpos[3:] = R.euler2quat(robot_orientation)

        self.robot_model.sim.data.set_joint_qpos(f"root", robot_qpos)
        self.robot_model.sim.data.set_joint_qpos("env:ball", ball_qpos)

    def _get_info(self):

        return {
            "success": self.ball_inside_goal(
                self.robot_model.sim.data.get_site_xpos("ball"))
        }
    
class GoaliePenaltyKick(PenaltyKick):
    r"""

    ## Description

    Goalie Penalty Kick tasks a humanoid robot with executing a simplified penalty kick in a soccer environment. The robot must approach 
    the ball, position itself for an optimal strike, and apply controlled force to direct the ball toward the opponent’s goal. Throughout 
    the episode, it must balance offensive play with precision, generating velocity toward the goal while avoiding penalties such as 
    going offside, making excessive or inefficient ball contacts, falling, having the ball blocked by obstacles, or allowing it 
    to be caught by the goalkeeper. 

    The task demands precise positioning to close in on the ball, dynamic control to deliver an effective and well-aimed kick, and strategic 
    movement to navigate the field, all within a continuous and high-dimensional action and observation space.

    ## Observation Space
    The observation space consists of the following parts (in order):

    - *qpos:* Position values of the robot's body parts. The dimensionality depends on the robot's joint configuration.
    - *qvel:* The velocities of these individual body parts (their derivatives). The dimensionality depends on the robot's joint configuration.
    - *field_dimensions (5 elements):* Field length, width, goal width, goal height, and goal depth.
    - *ball_xpos (3 elements):* The ball’s position in the world frame.
    - *ball_velp (3 elements):* The ball’s linear velocity in the world frame.
    - *ball_velr (3 elements):* The ball’s angular velocity (rotation) in the world frame.
    - *player_team (2 elements):* One-hot encoded vector indicating the player’s team.
    - *ball_to_goal_relpos* (3 elements):* Vector from the ball to the center of the goal.
    - *goalkeeper_velp* (3 elements):* The goalkeeper’s linear velocity in the world frame.
    - *goalkeeper_to_ball_relpos (3 elements):* Vector from the ball to the goalkeeper.

    The order of elements in the observation space related to the environment is as follows -

    | Num | Observation                   | Min  | Max | Type (Unit)              |
    | --- | ----------------------------- | ---- | --- | ------------------------ |
    | 0   | Field length                  | -Inf | Inf | length (meters)          |
    | 1   | Field width                   | -Inf | Inf | width (meters)           |
    | 2   | Goal width                    | -Inf | Inf | width (meters)           |
    | 3   | Goal height                   | -Inf | Inf | height (meters)          |
    | 4   | Goal depth                    | -Inf | Inf | depth (meters)           |
    | 5   | Ball x-coordinate             | -Inf | Inf | position (meters)        |
    | 6   | Ball y-coordinate             | -Inf | Inf | position (meters)        |
    | 7   | Ball z-coordinate             | -Inf | Inf | position (meters)        |
    | 8   | Ball linear velocity x        | -Inf | Inf | velocity (m/s)           |
    | 9   | Ball linear velocity y        | -Inf | Inf | velocity (m/s)           |
    | 10  | Ball linear velocity z        | -Inf | Inf | velocity (m/s)           |
    | 11  | Ball angular velocity x       | -Inf | Inf | angular velocity (rad/s) |
    | 12  | Ball angular velocity y       | -Inf | Inf | angular velocity (rad/s) |
    | 13  | Ball angular velocity z       | -Inf | Inf | angular velocity (rad/s) |
    | 14  | Player team (one-hot: team 0) | 0    | 1   | binary indicator         |
    | 15  | Player team (one-hot: team 1) | 0    | 1   | binary indicator         |
    | 16  | Ball-to-goal relative x       | -Inf | Inf | position difference (m)  |
    | 17  | Ball-to-goal relative y       | -Inf | Inf | position difference (m)  |
    | 18  | Ball-to-goal relative z       | -Inf | Inf | position difference (m)  |
    | 19  | Goalkeeper linear velocity x  | -Inf | Inf | velocity (m/s)           |
    | 20  | Goalkeeper linear velocity y  | -Inf | Inf | velocity (m/s)           |
    | 21  | Goalkeeper linear velocity z  | -Inf | Inf | velocity (m/s)           |
    | 22  | Goalkeeper-to-ball relative x | -Inf | Inf | position difference (m)  |
    | 23  | Goalkeeper-to-ball relative y | -Inf | Inf | position difference (m)  |
    | 24  | Goalkeeper-to-ball relative z | -Inf | Inf | position difference (m)  |

    ## Rewards

    The reward components include:

        1. `r_robot_distance_ball` (weight: 10.0): Encourages the robot to reduce its distance to the ball for better control.
        2. `r_ball_vel_twd_goal` (weight: 1.0): Rewards the ball’s velocity towards the opponent’s goal, promoting offensive play.
        3. `r_goal_scored` (weight: +25.0): Provides a large positive reward when the ball successfully enters the goal.
        4. `r_offside` (weight: -10.0): Penalizes when the ball is out of bounds or in an offside position, discouraging unproductive positioning.
        5. `r_ball_hits` (weight: -1.0): Applies a small penalty for repeated ball contacts by the same robot to encourage efficient play rather than random kicking.
        6. `r_robot_fallen` (weight: -15.0): Penalizes the robot if it falls, incentivizing stable movement.
        7. `r_ball_blocked` (weight: -20.0): Applies a strong penalty if the ball is blocked by an obstacle, discouraging poor shot angles or dribbling into hazards.

    `info` contains the success parameter if the given episode succeeded.

    ##Episode End
    ### Termination

    The current episode should terminate based on below termination criteria defined as follow:
        1. The ball successfully crosses the goal line between the posts and under the crossbar.
        2. The ball is found in an offside position as determined by the environment’s offside detection logic.
        3. The goalkeeper catches or securely holds the ball, preventing further play.
        4. The humanoid agent’s torso height moves outside the allowed range, indicating a fall or collapse.
        5. The physics simulation produces invalid numerical values (e.g., `NaN`), making further computation unreliable.

    ### Truncation
    The default duration of an episode is 5000 timesteps.

    """
    reward_config = {
        "robot_distance_ball": 10.0,
        "ball_vel_twd_goal": 1.0,
        "goal_scored": 25.0,
        "offside": -10.0,
        "ball_hits": -1.0,
        "robot_fallen": -15.0,
        "ball_blocked": -20.0,
    }

    def _make_scene_model(self, robot_xml_path: str):

        scene_mjcf = super()._make_scene_model(robot_xml_path)

        scene_mjcf = self._add_goalkeeper(scene_mjcf)

        return scene_mjcf
    
    def _get_env_obs(self):
        """
        Get the environment observation, including the base observations plus
        the goalkeeper's relative position and velocity with respect to the ball.

        Returns:
            np.ndarray: Concatenated observation vector.
        """
        penalty_obs = super()._get_env_obs()
        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")

        goalkeeper_xpos = self.robot_model.sim.data.get_site_xpos("goalkeeper_site")
        goalkeeper_xvelp = self.robot_model.sim.data.get_site_xvelp("goalkeeper_site")

        goalkeeper_rel = goalkeeper_xpos - ball_xpos
        obs = np.concatenate(
            [penalty_obs, goalkeeper_rel, goalkeeper_xvelp],
            dtype=np.float32,
        )
        
        return obs
    
    def _setup_references(self):
        """
        Setup references to key simulation components, including the goalkeeper geometry ID.
        """
        super()._setup_references()
        self.keeper_id = self.robot_model.sim.model.geom_name2id("goalkeeper_geom")
    
    def move_goalkeeper(self, freq: float = 0.3):
        """
        Move the goalkeeper sinusoidally along the Y-axis to simulate patrolling behavior.

        Args:
            freq (float): Frequency of the sinusoidal movement (Hz).
        """
        amp = self.parameters_dict["env_parameters"]["goal"]["width"] - 0.6
        t = self.robot_model.sim.data.time
        pos = amp * np.sin(2 * np.pi * freq * t)
        vel = 2 * np.pi * freq * amp * np.cos(2 * np.pi * freq * t)
        self.robot_model.sim.data.set_joint_qpos("goalkeeper_joint", pos)
        self.robot_model.sim.data.set_joint_qvel("goalkeeper_joint", vel)

    def step(self, *args):
        """
        Perform a simulation step after moving the goalkeeper.

        Returns:
            tuple: (observation, reward, terminated, truncated, info) from the environment step.
        """
        self.move_goalkeeper()
        observation, reward, terminated, truncated, info = super().step(*args)

        return observation, reward, terminated, truncated, info
    
    def compute_reward(self) -> dict:
        """
        Compute the reward for the current timestep, including penalties and goal scoring.

        Returns:
            dict: Dictionary of reward components including 'goal_scored' and 'ball_blocked'.
        """
        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        ball_inside_goal = self.ball_inside_goal(ball_xpos)
        ball_hit_obstacle = self.ball_hit_obstacle()

        raw_reward = self.compute_penalty_reward(ball_xpos, ball_inside_goal)

        raw_reward.update(
            {
                "goal_scored": ball_inside_goal,
                "ball_blocked": ball_hit_obstacle
            }
        )

        return raw_reward
    
    def ball_hit_obstacle(self) -> bool:
        """
        Check if the ball is currently in contact with the goalkeeper.

        Returns:
            bool: True if ball is touching goalkeeper, False otherwise.
        """
        ball_geom_id = self.robot_model.sim.model.geom("ball").id

        for i in range(self.robot_model.sim.data.ncon):
            contact = self.robot_model.sim.data.contact[i]
            if (contact.geom1 == self.keeper_id and contact.geom2 == ball_geom_id) or \
            (contact.geom2 == self.keeper_id and contact.geom1 == ball_geom_id):
                return True
            
        return False
    
    def compute_terminated(self) -> bool:
        """
        Determine if the episode should terminate due to robot falling or ball hitting the goalkeeper.

        Returns:
            bool: True if terminated, False otherwise.
        """
        terminated = super().compute_terminated()
        ball_hit_goalkeeper = self.ball_hit_obstacle()

        return bool(terminated or ball_hit_goalkeeper)

    def _change_team(self):
        """
        Update team-related state and adjust the goalkeeper's position accordingly.
        """
        super()._change_team()
        keeper_qpos = self.robot_model.sim.model.geom_pos[self.keeper_id]
        keeper_qpos[0] = abs(keeper_qpos[0])*self.direction
        self.robot_model.sim.model.geom_pos[self.keeper_id] = keeper_qpos

    def _add_goalkeeper(self, scene_mjcf):
        """
        Add the goalkeeper body, joint, geometry, site, and actuator to the MJCF model.
        """
        goalkeeper_body = scene_mjcf.worldbody.add_body(
            name="goalkeeper_body",
            pos=[-self.parameters_dict["env_parameters"]["field"]["length"], 0, 0.2]  # adjust z to place it above the ground
        )

        goalkeeper_body.add_joint(
            name="goalkeeper_joint",
            type=mujoco.mjtJoint.mjJNT_SLIDE,
            axis=[0, 1, 0],  # Slide along the Y-axis
            pos=[0, 0, 0],
            range=[-3, 3],  # Limit motion between -3 and 3
            actfrcrange=[-10, 10],
        )

        goalkeeper_body.add_geom(
            name="goalkeeper_geom",
            type=mujoco.mjtGeom.mjGEOM_MESH,
            meshname="goalkeeper",
            material="goalkeeper_mat",
            pos=[0, 0, 0.7],          # half height to sit above the joint
            quat=[0.5, -0.5, 0.5, 0.5],
            mass=1.0,
        )

        goalkeeper_body.add_site(
            name="goalkeeper_site",
        )

        scene_mjcf.add_actuator(
            name="goalkeeper_joint",
            target="goalkeeper_joint",
            gaintype=mujoco.mjtGain.mjGAIN_FIXED,           # defines fixed gain for torque
            biastype=mujoco.mjtBias.mjBIAS_NONE,          # common for torque actuators
            ctrlrange=[-np.pi, np.pi],
            trntype=mujoco.mjtTrn.mjTRN_JOINT
        )

        return scene_mjcf

class ObstaclePenaltyKick(PenaltyKick):

    reward_config = {
        "ball_vel_twd_goal": 1.0,
        "goal_scored": 20.0,
        "offside": -10.0,
        "ball_hits": -1.0,
        "ball_blocked": -5.0,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _make_scene_model(self, robot_xml_path: str):

        scene_mjcf = super()._make_scene_model(robot_xml_path)

        scene_mjcf = self._add_goalkeeper(scene_mjcf)

        return scene_mjcf

    def _setup_references(self):

        super()._setup_references()
        geom_names = [name for name in self.robot_model.sim.model.geom_names if name and "goalkeeper_geom" in name]

        self.goalkeeper_geom_ids = []
        for geom_name in geom_names:
            geom_id = self.robot_model.sim.model.geom_name2id(geom_name)
            self.goalkeeper_geom_ids.append(geom_id)        
    
    def _get_env_obs(self):

        penalty_obs = super()._get_env_obs()
        target_xpos = self.robot_model.sim.data.get_site_xpos(self.goal_site)

        obs = np.concatenate(
            [penalty_obs, target_xpos],
            dtype=np.float32,
        )

        for i in range(3):
            obstacle_xpos = self.robot_model.sim.data.get_geom_xpos(f"goalkeeper_geom{i}")
            obs = np.concatenate([obs, obstacle_xpos], dtype=np.float32)
        
        return obs
    
    def compute_reward(self):
        
        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        ball_inside_goal = self.ball_inside_goal(ball_xpos)
        ball_hit_obstacle = self.ball_hit_obstacle()

        raw_reward = self.compute_penalty_reward(ball_xpos, ball_inside_goal, self.goal_site)

        raw_reward.update(
            {
                "goal_scored": ball_inside_goal,
                "ball_blocked": ball_hit_obstacle
            }
        )

        return raw_reward
    
    def ball_inside_goal(self, ball_xpos, threshold = 0.3):

        goal_centre = self.robot_model.sim.data.get_site_xpos(self.goal_site)
        
        distance = np.linalg.norm(goal_centre - ball_xpos)
        
        return bool(distance < threshold)
    
    def ball_hit_obstacle(self):

        ball_geom_id = self.robot_model.sim.model.geom("ball").id

        for i in range(self.robot_model.sim.data.ncon):
            contact = self.robot_model.sim.data.contact[i]
            if (contact.geom1 in self.goalkeeper_geom_ids and contact.geom2 == ball_geom_id) or \
            (contact.geom2 in self.goalkeeper_geom_ids and contact.geom1 == ball_geom_id):
                return True
            
        return False
    
    def compute_terminated(self):

        terminated = super().compute_terminated()
        ball_hit_obstacle = self.ball_hit_obstacle()

        return bool(terminated or ball_hit_obstacle)
    
    def _reset_env(self):
        """
        Reset the environment to an initial state.
        """
        super()._reset_env()
        self.goal_pos = self._sample_target()

    def _sample_target(self):
        
        goal_pose = np.zeros(5)
        max_pos = self.parameters_dict["env_parameters"]["goal"]["width"] - 0.14
        num_sections = 8
        step_size = (2* max_pos) / (num_sections) if num_sections > 1 else 0
        positions_y = [-max_pos  + i * step_size for i in range(1,num_sections+1,2)]
        self.np_random.shuffle(positions_y)

        goal_pose[:4] = positions_y
        goal_pose[-1] = self.np_random.uniform(low=0.44, high=self.parameters_dict["env_parameters"]["goal"]["height"]-0.6)
        
        return goal_pose

    def _render_callback(self):
        """Update the visualization of the target site."""

        for i in range(3):
            site_id = mujoco.mj_name2id(
                self.robot_model.sim.model._model, mujoco.mjtObj.mjOBJ_GEOM, f"goalkeeper_geom{i}"
            )
            self.robot_model.sim.model._model.geom_pos[site_id] = [0, self.goal_pos[i], 0.4]

        site_id = mujoco.mj_name2id(
            self.robot_model.sim.model._model, mujoco.mjtObj.mjOBJ_SITE, self.goal_site
        )
        self.robot_model.sim.model._model.site_pos[site_id] = [0, self.goal_pos[3], self.goal_pos[4]]
        self.robot_model.sim.forward()

    def _add_goalkeeper(self, scene_mjcf):
        
        self.goal_site = "goalarea_site"

        goal_area = scene_mjcf.worldbody.add_body(
            name="goalarea_body",
            pos=[-self.parameters_dict["env_parameters"]["field"]["length"], 0, 0.2]  # adjust z to place it above the ground
        )

        goal_area.add_site(
            name=self.goal_site,
            type=mujoco.mjtGeom.mjGEOM_BOX,
            size=[0.03, 0.42, 0.4],  # depth, height, and small width to look like 2D
            pos=[0, -1.44, self.parameters_dict["env_parameters"]["goal"]["height"]/3],          # half height to sit above the joint
            quat=[1, 0, 0, 0],
            rgba=[0,0,1,0.5],
        )
        
        goalkeeper_body = scene_mjcf.worldbody.add_body(
            name="goalkeeper_body",
            pos=[-self.parameters_dict["env_parameters"]["field"]["length"], 0, 0.2]  # adjust z to place it above the ground
        )

        for i in range(0,3):
            goalkeeper_body.add_geom(
                name=f"goalkeeper_geom{i}",
                type=mujoco.mjtGeom.mjGEOM_MESH,
                meshname="defender",
                pos=[0, -0.48 + 0.96*i, 0.3],          # half height to sit above the joint
                quat=[0.5, 0.5, 0.5, 0.5],
                rgba=[1,0,0,1],
                mass=1.0,
            )

        goalkeeper_body.add_site(
            name="goalkeeper_site",
        )

        return scene_mjcf