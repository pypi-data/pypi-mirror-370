import mujoco
import numpy as np
from sai_mujoco.envs.football import FootballEnv
import sai_mujoco.utils.rotations as R

class KickToTarget(FootballEnv):

    env_name: str = "football"
    scene_name: str = "base_scene"
    default_camera_config = {
        "distance": 7.8,
        "azimuth": -160,
        "elevation": -20.0,
        "lookat": np.array([0.0, 0.0, 0.35]),
    }

    reward_config = {
        "offside": -10.0,
        "success": 20.0,
        "distance": 5.0
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.move_target = kwargs.get("move_target", False)
    
    def _get_env_obs(self):
        
        field_envs = super()._get_env_obs()

        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")

        goal_xpos = self.robot_model.sim.data.get_site_xpos("target0")
        goal_velp = self.robot_model.sim.data.get_site_xvelp("target0")
        
        ball_goal_rel = goal_xpos - ball_xpos

        obs = np.concatenate(
            [field_envs, ball_goal_rel, goal_velp],
            dtype=np.float32,
        )

        return obs
        
    def compute_reward(self):

        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        outside_field = self.is_outside_field(ball_xpos, False)
        distance_reward, inside_target = self._is_success(ball_xpos, self.goal_pos)
        
        raw_reward = {
        "offside": outside_field,
        "success": inside_target,
        "distance": distance_reward
        }

        return raw_reward
    
    def compute_terminated(self):

        terminated = super().compute_terminated()

        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        outside_field = self.is_outside_field(ball_xpos, False)
        _, inside_target = self._is_success(ball_xpos, self.goal_pos)

        return bool(terminated or outside_field or inside_target)
        
    def _is_success(self, ball_xpos, target_xpos, distance_threshold=0.4):
        """Check if the achieved goal is close enough to the desired goal.

        Args:
            achieved_goal (np.ndarray): The achieved goal position
            desired_goal (np.ndarray): The desired goal position

        Returns:
            float: 1.0 if successful, 0.0 otherwise
        """

        distance = np.linalg.norm(ball_xpos - target_xpos, axis=-1)
        return np.exp(-distance), bool(distance < distance_threshold)
        
    def _reset_env(self):
        """
        Reset the environment to an initial state.
        """
        super()._reset_env()
        self._sample_robot()
        self.goal_pos = self._sample_target()

    def _sample_robot(self):
        
        robot_qpos = self.robot_model.sim.data.get_joint_qpos("root")
        ball_qpos = self.robot_model.sim.data.get_joint_qpos("env:ball")
        robot_pose, robot_z = self.sample_robot_pose()
        ball_pose = self.sample_ball_position(robot_pose, robot_z)
        ball_qpos[:2] = ball_pose
        robot_quat = R.euler2quat([0.0, 0.0, robot_z])

        robot_qpos[:2] = robot_pose
        robot_qpos[3:] = robot_quat
        self.robot_model.sim.data.set_joint_qpos("root", robot_qpos)
        self.robot_model.sim.data.set_joint_qpos("env:ball", ball_qpos)
        self.robot_model.sim.forward()
    
    def sample_robot_pose(self,offset=0.5):

        x = self.np_random.uniform(-self.parameters_dict["env_parameters"]["field"]["length"]+offset, self.parameters_dict["env_parameters"]["field"]["length"]-offset)
        y = self.np_random.uniform(-self.parameters_dict["env_parameters"]["field"]["width"]+offset, self.parameters_dict["env_parameters"]["field"]["width"]-offset)

        dx = -x
        dy = -y
        theta = np.arctan2(dy, dx)
        return np.array([x, y]), theta

    def sample_ball_position(self, robot_xy, angle, min_dist=0.5, max_dist=2.0, bord_offset=0.5):
        while True:  # Try up to 100 times to sample a valid point
            dist = self.np_random.uniform(min_dist, max_dist)
            offset = np.array([dist * np.cos(angle), dist * np.sin(angle)])
            ball_xy = robot_xy + offset
            if (-self.parameters_dict["env_parameters"]["field"]["length"]+bord_offset <= ball_xy[0] <= self.parameters_dict["env_parameters"]["field"]["length"]-bord_offset and
                -self.parameters_dict["env_parameters"]["field"]["width"]+bord_offset <= ball_xy[1] <= self.parameters_dict["env_parameters"]["field"]["width"]-bord_offset):
                return ball_xy
    
    def _sample_target(self, min_offset=2.0, max_offset=3.5, offset=0.5):

        robot_qpos = self.robot_model.sim.data.get_joint_qpos("root")
        goal_pos = self.robot_model.sim.data.get_site_xpos("target0")

        while True:
            y_offset = self.np_random.uniform(min_offset, max_offset)
            if self.np_random.uniform() > 0.5:
                y_offset = -y_offset  # Flip direction randomly
            goal_pos[1] = robot_qpos[1] + y_offset
            goal_pos[0] = self.np_random.uniform(-self.parameters_dict["env_parameters"]["field"]["length"]+offset, self.parameters_dict["env_parameters"]["field"]["length"]-offset)
            if -self.parameters_dict["env_parameters"]["field"]["width"]+offset <= goal_pos[1] <= self.parameters_dict["env_parameters"]["field"]["width"]-offset:
                return goal_pos.copy() 
      
    def _render_callback(self):
        """Update the visualization of the target site."""
        sites_offset = (self.robot_model.sim.data.site_xpos - self.robot_model.sim.model._model.site_pos).copy()
        site_id = mujoco.mj_name2id(
            self.robot_model.sim.model._model, mujoco.mjtObj.mjOBJ_SITE, "target0"
        )
        self.robot_model.sim.model._model.site_pos[site_id] = self.goal_pos - sites_offset[site_id]
        self.robot_model.sim.forward()

    def _make_scene_model(self, robot_xml_path: str):

        scene_mjcf = super()._make_scene_model(robot_xml_path)

        scene_mjcf = self._add_target(scene_mjcf)

        return scene_mjcf
    
    def _add_target(self, scene_mjcf):

        red_body = scene_mjcf.worldbody.add_body(
            name="target0",
            pos=[0, 0, 0.0]  # adjust z to place it above the ground
            )

        red_body.add_site(
            type=mujoco.mjtGeom.mjGEOM_CYLINDER,
            name="target0",
            pos=[0, 0, 0.001],  # optional, can center it
            size=[self.parameters_dict["kick_to_target"]["target_size"], 0.01, 0.0],
            rgba=[1, 0, 0, 0.4],
        )

        return scene_mjcf

    def _get_info(self):
        """Get additional information about the environment state.

        Returns:
            dict: Additional information dictionary
        """
        return {
            "success": self._is_success(
                self.robot_model.sim.data.get_site_xpos("ball"), self.goal_pos
            )[1]
        }