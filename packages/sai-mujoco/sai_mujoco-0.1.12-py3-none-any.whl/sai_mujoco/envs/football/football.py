import yaml
import mujoco
import numpy as np
import sai_mujoco
from pathlib import Path
from typing import Tuple, List
from sai_mujoco.envs.base import BaseEnv

class FootballEnv(BaseEnv):
    r"""
    Base class for football (soccer) simulation environments in sai_mujoco.

    This class provides the core tools, structure, and MuJoCo integration needed 
    to create different football environments involving robots, a ball, and a field. 
    It handles physics setup, observation construction, episode termination checks, 
    and in-game logic (e.g., goal detection, ball position checks).

    A key feature is its scaling mechanism, which automatically adjusts robot 
    dimensions, field size, goal size, and mesh scaling based on the selected 
    robot type. This allows the same environment logic to be reused for robots 
    of different sizes without rewriting geometry or parameters.
    """

    env_name: str = "football"  
    scene_name: str = "base_scene"
    default_camera_config = {
        "distance": 2.8,
        "azimuth": -130,
        "elevation": -45.0,
        "lookat": np.array([0.2, 0.0, 0.35]),
    }

    field_dict = {
        "t1" : 1.0,
        "lower_t1" : 1.0
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize the FootballEnv instance.

        This constructor reads the robot configuration, team assignment, and texture
        settings from keyword arguments, determines the scaling factor for the robot
        and field based on the robot type, and loads environment parameters from the
        YAML configuration file. The parameters are automatically scaled and flattened
        for convenient access during simulation.
        """
        robot_config = kwargs.get("robot_config",{})
        self.textures = kwargs.get("textures", -1)
        self.team = kwargs.get("team", 0)

        self.robot_name = robot_config.get("name","lower_t1")
        self.size = self.field_dict.get(self.robot_name, 1.0)
        self.parameters_dict = self._flatten_robot_keys(self._scale_parameters(self.load_yaml()))

        super().__init__(*args, **kwargs)

    def _scale_parameters(self, d, inside_robot=False):
        """
        Scale numeric values inside the "robot" part of the config by self.size.

        Recursively goes through the input dict or list. If inside a "robot" key, 
        multiplies numbers by the size to adjust for robot scale.

        Parameters:
            d: dict, list, int, or float - input data to scale
            inside_robot: bool - whether currently inside a "robot" key

        Returns:
            The scaled data with the same structure as input.
        """
        if isinstance(d, dict):
            # Check if we're entering a 'robot' key
            return {
                k: self._scale_parameters(v, inside_robot=(inside_robot or k == "robot"))
                for k, v in d.items()
            }
        elif isinstance(d, list):
            return [self._scale_parameters(v, inside_robot=inside_robot) for v in d]
        elif isinstance(d, (int, float)):
            return d * self.size if inside_robot else d
        else:
            return d 
    
    def _flatten_robot_keys(self, d):
        """
        Remove the "robot" nesting in the config by merging its contents up.

        Recursively processes dicts and lists. When a "robot" key is found, its 
        content is merged directly into the parent dict.

        Parameters:
            d: dict, list, or other - input data to flatten

        Returns:
            The data with "robot" keys flattened out.
        """
        if isinstance(d, dict):
            new_dict = {}
            for k, v in d.items():
                # If key is "robot", we inline its contents (assuming it's a dict)
                if k == "robot" and isinstance(v, dict):
                    # Recursively flatten its children
                    flattened = self._flatten_robot_keys(v)
                    new_dict.update(flattened)
                else:
                    new_dict[k] = self._flatten_robot_keys(v)
            return new_dict
        elif isinstance(d, list):
            return [self._flatten_robot_keys(v) for v in d]
        else:
            return d

    def _setup_references(self):
        """
        Set up references to important MuJoCo model parts for easy access.

        Finds and stores IDs of robot geoms, the floor geom, the robot torso geom,
        the soccer ball body, and the robot's root site. This allows quick access
        to these elements during simulation and observation.
        """

        super()._setup_references()

        body_names = [body for body in self.robot_model.sim.model.body_names if "robot" in body]

        self.robot_geom_ids = []
        for body_name in body_names:
            body_id = self.robot_model.sim.model.body_name2id(body_name)

            for geom_id in range(self.robot_model.sim.model.ngeom):
                if self.robot_model.sim.model.geom_bodyid[geom_id] == body_id:
                    self.robot_geom_ids.append(geom_id)

        self._floor_geom = "floor"
        self._torso_id = self.robot_model.sim.model.geom_name2id(f"Trunk")
        self.ball_id = self.robot_model.sim.model.body_name2id("soccer_ball")
        self._root_site = "imu"

    def _get_env_obs(self):
        """
        Get the current environment observation.

        Returns a numpy array containing field dimensions, goal size, the ball's
        position and velocity (both linear and rotational), and a one-hot vector
        indicating the current team.

        Returns:
            np.ndarray: Observation vector representing the environment state.
        """
        
        # length = self.parameters_dict["env_parameters"]["field"]["length"]
        # width = self.parameters_dict["env_parameters"]["field"]["width"]
        # goal_width = self.parameters_dict["env_parameters"]["goal"]["width"]
        # goal_height = self.parameters_dict["env_parameters"]["goal"]["height"]
        # goal_depth = self.parameters_dict["env_parameters"]["goal"]["depth"]

        ball_xpos = self.robot_model.sim.data.get_site_xpos("ball")
        ball_velp = self.robot_model.sim.data.get_site_xvelp("ball")
        ball_velr = self.robot_model.sim.data.get_site_xvelr("ball")
        # player_team = np.array([1, 0]) if self.current_team == 0 else np.array([0, 1])

        # obs = np.array(
        #     [length, width, goal_width, goal_height, goal_depth],
        #     dtype=np.float32,
        # )

        obs = np.concatenate([ball_xpos, ball_velp, ball_velr])

        return obs
    
    def compute_terminated(self):
        """
        Check if the episode should terminate.

        The episode ends if the robot has fallen or if any simulation data
        (positions or velocities) contain NaNs.

        Returns:
            bool: True if terminated, False otherwise.
        """

        height = self.robot_model.sim.data.get_site_xpos(self._root_site)[2]
        has_fallen = self.has_robot_fallen(height)
        
        data_nan = (
            np.isnan(self.robot_model.sim.data.qpos).any()
            | np.isnan(self.robot_model.sim.data.qvel).any()
        )
        return bool(has_fallen or data_nan)
    
    def has_robot_fallen(self, height: float, min_height: float = 1.0, max_height: float = 2.0) -> bool:
        """
        Determine if the robot has fallen based on its torso height.

        Uses custom standing height bounds if available; otherwise defaults.

        Parameters:
            height (float): Current height of the robot's torso.
            min_height (float): Minimum allowed height before considered fallen.
            max_height (float): Maximum height threshold (unused here).

        Returns:
            bool: True if robot is standing, False if fallen.
        """
        if hasattr(self.robot_model, "standing_height"):
            min_height = self.robot_model.standing_height[0]
            max_height = self.robot_model.standing_height[1]

        fallen = min_height < height
        return not fallen
    
    def is_outside_field(self, ball_xpos: np.ndarray, inside_goal: np.ndarray) -> bool:
        """
        Check if the ball is outside the field boundaries (excluding goals).

        Parameters:
            ball_xpos (array-like): Ball position [x, y, z].
            inside_goal (bool): Whether the ball is inside a goal.

        Returns:
            bool: True if ball is outside the field and not inside a goal.
        """

        outside_field = ball_xpos[0] < -self.parameters_dict["env_parameters"]["field"]["length"] or ball_xpos[0] > self.parameters_dict["env_parameters"]["field"]["length"] or ball_xpos[1] < -self.parameters_dict["env_parameters"]["field"]["width"] or ball_xpos[1] > self.parameters_dict["env_parameters"]["field"]["width"]
        return not inside_goal and outside_field
    
    def ball_inside_goal(self, ball_xpos: np.ndarray) -> bool:
        """
        Check if the ball is inside the current team's goal area.

        Parameters:
            ball_xpos (np.ndarray): The (x, y, z) position of the ball.

        Returns:
            bool: True if the ball is within the goal boundaries, False otherwise.
        """

        # Check if the ball is in goal
        goal_centre = self.robot_model.sim.data.get_site_xpos(self.parameters_dict["team_parameters"][self.current_team]["goal"]["name"])
        
        x = goal_centre[0]
        x_max = x + self.parameters_dict["env_parameters"]["goal"]["depth"] if x >= 0 else x - self.parameters_dict["env_parameters"]["goal"]["depth"]
        
        if x > x_max:
            x, x_max = x_max, x

        is_ball_inside = (x <= ball_xpos[0] <= x_max) and \
                         (goal_centre[1] - self.parameters_dict["env_parameters"]["goal"]["width"] <= ball_xpos[1] < goal_centre[1] + self.parameters_dict["env_parameters"]["goal"]["width"]) and \
                         (ball_xpos[2] < goal_centre[2] + self.parameters_dict["env_parameters"]["goal"]["height"])
        
        return bool(is_ball_inside)
    
    def _make_scene_model(self, robot_xml_path: str) -> mujoco.MjModel:
        """
        Create and compile a MuJoCo model from XML files.

        This method combines scene, environment, and robot XML files into a single
        MuJoCo model. It handles the composition of different XML components and
        applies robot positioning and orientation.

        Args:
            robot_xml_path (str): Path to the robot XML file

        Returns:
            mujoco.MjModel: Compiled MuJoCo model

        Note:
            The method attaches environment and robot components to the scene
            using attachment sites, and applies robot positioning from env_config.
        """
        scene_mjcf = super()._make_scene_model(robot_xml_path)

        scene_mjcf = self._rescale_meshes(scene_mjcf, self.size)
        scene_mjcf = self._rescale_field(scene_mjcf, self.size)

        return scene_mjcf
            
    def _reset_env(self):
        """
        Reset internal state of the environment.

        Calls the parent reset, then updates textures, team states, and
        sets direction and rotation for the current team.
        """

        super()._reset_env()
        self._change_model_texture(self.textures)
        self._change_team_state(self.team)

        self.direction = self.parameters_dict["team_parameters"][self.current_team]["direction"][0]
        self.rotation = self.parameters_dict["team_parameters"][self.current_team]["rotation"]

    def _rescale_meshes(self, scene_mjcf, size: float):
        """
        Rescale the robot meshes based on the given size factor.

        Parameters:
            size (float): Scaling factor to apply to mesh dimensions.
        """
        for i in range(0,4):
        # Change the mesh size
            scale = scene_mjcf.meshes[i].scale
            scale = [size*scl for scl in scale]
            scene_mjcf.meshes[i].scale = scale
        
        return scene_mjcf

    def _rescale_field(self, scene_mjcf, size: float):
        """
        Rescale field geometries, goals, boundary walls, and logos.

        Parameters:
            size (float): Scaling factor to apply to field components.
        """

        scale = scene_mjcf.geoms[1].size
        scale[:2] = [size*scl for scl in scale[:2]]
        scene_mjcf.geoms[1].size = scale

        # SOUTH GOAL
        for i in range(3,5):
            pos = scene_mjcf.bodies[i].pos
            pos[0:2] = [ps*size for ps in pos[:2]]
            scene_mjcf.bodies[i].pos = pos     

        # Change the boundary walls and SAI logo size
        geom_list = list(range(2,4)) + list(range(21,25))
        for i in geom_list:
            scale = scene_mjcf.geoms[i].size
            scale[0:2] = [scl*size for scl in scale[:2]]
            scene_mjcf.geoms[i].size = scale

            pos = scene_mjcf.geoms[i].pos
            pos[:2] = [ps*size for ps in pos[:2]]
        
        for i in range(5,21):

            scale = scene_mjcf.geoms[i].size
            scale[0:2] = [scl*size for scl in scale[:2]]
            scene_mjcf.geoms[i].size = scale
            
            pos = scene_mjcf.geoms[i].pos
            pos[:3] = [ps*size for ps in pos[:3]]
            scene_mjcf.geoms[i].pos = pos

            return scene_mjcf      
    
    def _change_model_texture(self, texture: float):
        """
        Update ground texture properties based on the given texture index or value.

        Adjusts friction and color accordingly.
        """

        friction, rgba = self.get_friction_rgba(texture)

        self.robot_model.sim.model.geom_rgba[1] = rgba
        self.robot_model.sim.model.geom_friction[1] = friction

    def _change_team_state(self, team: int):
        """
        Set the current team and update the robot's jersey color.

        Parameters:
            team (int): Team index (0 or 1).
        """
        self.current_team, jersey_colour = self._choose_teams(team)
        self.robot_model.sim.model.geom_rgba[self._torso_id] = jersey_colour
    
    def get_friction_rgba(self, texture) -> Tuple[List[float], List[float]]:
        """
        Compute friction and color values interpolated by the texture parameter.

        Parameters:
            texture (float or int): Texture index or random value for interpolation.

        Returns:
            tuple: (friction, rgba color) lists.
        """
        if texture == -1:
            texture = self.np_random.random()

        friction = self.parameters_dict["env_parameters"]["friction"]
        color = self.parameters_dict["env_parameters"]["color"]

        fric = [(1 - texture)*friction[0][i] + texture*friction[1][i] for i in range(len(friction[0]))]
        rgba = [(1 - texture)*color[0][i] + texture*color[1][i] for i in range(len(color[0]))]

        return fric, rgba
    
    def _choose_teams(self, team: int) -> Tuple[int, List[int]]:
        """
        Choose a team index and corresponding jersey color.

        If team == -1, randomly select between team 0 or 1.

        Parameters:
            team (int): Team index or -1 for random choice.

        Returns:
            tuple: (team index, jersey RGBA color list)
        """
        if team == -1:
            team = self.np_random.choice([0,1])
        jersey_colour = [1,0,0,1] if team else [0,0,1,1]

        return team, jersey_colour
    
    def load_yaml(self) -> dict:
        """
        Load the football environment configuration from a YAML file.

        Returns:
            dict: Parsed configuration data.
        """
        file_path = Path(sai_mujoco.__file__).parent / "envs" / self.env_name / "config.yaml"
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        return data