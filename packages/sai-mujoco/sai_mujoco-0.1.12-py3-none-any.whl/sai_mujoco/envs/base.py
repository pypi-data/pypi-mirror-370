from pathlib import Path
from typing import Optional
import gymnasium as gym
from gymnasium.utils.ezpickle import EzPickle
import numpy as np
import sai_mujoco
from sai_mujoco.robots import ROBOT_CLASS_REGISTORY
from sai_mujoco.robots.base import BaseRobot
import mujoco


class BaseEnvMeta(type):
    """
    Metaclass to automatically construct XML paths from env_name and scene_name.

    This metaclass automatically generates the XML file paths for environment and scene
    configurations based on the class attributes set by subclasses. It constructs
    the paths relative to the sai_mujoco package assets directory.

    Attributes:
        env_name (str): The name of the environment directory under assets/envs/
        scene_name (str): The name of the scene XML file under assets/scene/

    Generated Attributes:
        env_xml_path (str): Full path to the environment XML file
        scene_xml_path (str): Full path to the scene XML file
    """

    def __new__(mcs, name, bases, namespace):
        """
        Create a new class with automatically constructed XML paths.

        Args:
            mcs: The metaclass instance
            name (str): The name of the class being created
            bases (tuple): Base classes
            namespace (dict): The class namespace containing attributes

        Returns:
            type: The new class with XML paths added to its namespace
        """
        # Get the class variables
        env_name = namespace.get("env_name")
        scene_name = namespace.get("scene_name")

        # Construct paths if env_name and scene_name are provided
        if env_name is not None:
            namespace["env_xml_path"] = str(
                Path(sai_mujoco.__file__).parent
                / "assets"
                / "envs"
                / env_name
                / "env.xml"
            )

        if scene_name is not None:
            namespace["scene_xml_path"] = str(
                Path(sai_mujoco.__file__).parent
                / "assets"
                / "scene"
                / f"{scene_name}.xml"
            )
        else:
            # Default to base_scene if no scene_name is provided
            namespace["scene_xml_path"] = str(
                Path(sai_mujoco.__file__).parent / "assets" / "scene" / "base_scene.xml"
            )

        return super().__new__(mcs, name, bases, namespace)


class BaseEnv(gym.Env, EzPickle, metaclass=BaseEnvMeta):
    """
    Base environment class for MuJoCo environments.

    This class provides a foundation for creating MuJoCo-based reinforcement learning
    environments. It handles robot loading, scene composition, observation and action
    space definition, and provides a standard interface for environment interactions.

    Subclasses should set:
    - env_name: str - The name of the environment (used to construct env_xml_path)
    - scene_name: str - The name of the scene (used to construct scene_xml_path)

    The metaclass automatically constructs XML paths based on these attributes.

    Attributes:
        env_name (str): The name of the environment directory
        scene_name (str): The name of the scene XML file
        env_xml_path (str): Full path to the environment XML file (auto-generated)
        scene_xml_path (str): Full path to the scene XML file (auto-generated)
        metadata (dict): Gymnasium metadata including supported render modes
        default_camera_config (dict): Default camera configuration for rendering

    Example:
        class MyEnv(BaseEnv):
            env_name = "bowling"
            scene_name = "base_scene"
    """

    # Class-level configuration - subclasses should override these
    env_name: str = None
    scene_name: str = None

    # XML paths are automatically constructed by the metaclass
    env_xml_path: str = None
    scene_xml_path: str = None

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
    }

    default_camera_config: dict = None

    def __init__(self, env_config: dict, robot_config: dict = {}, **kwargs):
        """
        Initialize the base environment.

        Args:
            env_config (dict): Environment configuration parameters
            robot_config (dict, optional): Robot configuration parameters. Defaults to {}.
            **kwargs: Additional keyword arguments including:
                - deterministic_reset (bool): Whether to use deterministic reset. Defaults to True.
                - render_mode (str): Rendering mode. Defaults to None.
                - hide_overlay (bool): Whether to hide the overlay menu. Defaults to True.
        """
        super().__init__()
        self.env_config = env_config
        self.robot_config = robot_config
        self.kwargs = kwargs

        self.deterministic_reset = kwargs.get("deterministic_reset", True)

        self.render_mode = kwargs.get("render_mode", None)

        self.robot_name = self.robot_config["name"]

        self.robot_model: BaseRobot = self._load_robot_model()

        assert (
            hasattr(self.robot_model, "metadata")
            and self.robot_model.metadata is not None
        ), "Robot model must have a metadata attribute"
        self.metadata = self.robot_model.metadata

        self._setup_references()

        if self.kwargs.get("hide_overlay", True):
            self._hide_overlay()

        obs = self._get_obs()

        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=obs.shape, dtype=np.float32
        )

        self.action_space = self.robot_model.action_space

    def _make_scene_model(self, robot_xml_path: str):

        scene_mjcf = mujoco.MjSpec.from_file(self.scene_xml_path)
        if self.env_xml_path is not None:
            env_mjcf = mujoco.MjSpec.from_file(self.env_xml_path)
        else:
            env_mjcf = mujoco.MjSpec()

        robot_mjcf = mujoco.MjSpec.from_file(robot_xml_path)

        attachment_site = scene_mjcf.worldbody.add_site()

        scene_mjcf.attach(env_mjcf, site=attachment_site)

        if self.robot_config.get("base_xml", None) is not None:
            robot_mjcf = self._add_robot_base(robot_mjcf, self.robot_config["base_xml"])

        robot_mjcf.bodies[1].pos = (
            self.env_config.get("robot_pos", [0, 0, 0]) - robot_mjcf.bodies[1].pos
        )
        robot_mjcf.bodies[1].quat = self.env_config.get("robot_quat", [0, 0, 0, 1])

        scene_mjcf.attach(robot_mjcf, site=attachment_site)

        return scene_mjcf


    def _make_mjcf_model(self, robot_xml_path: str) -> mujoco.MjModel:
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
        
        scene_mjcf = self._make_scene_model(robot_xml_path)
        self._model_spec = scene_mjcf

        return scene_mjcf.compile()

    def _add_robot_base(
        self, robot_mjcf: mujoco.MjSpec, base_xml: str
    ) -> mujoco.MjSpec:
        """
        Add a base component to the robot model.

        This method loads a base XML file and attaches the robot to it. It handles
        potential naming conflicts between the robot's base body and the base component.

        Args:
            robot_mjcf (mujoco.MjSpec): The robot MuJoCo specification
            base_xml (str): Name of the base XML file (without .xml extension)

        Returns:
            mujoco.MjSpec: The combined robot and base specification

        Raises:
            AssertionError: If the base body is not found in the base XML file
        """
        base_xml_path = (
            Path(sai_mujoco.__file__).parent / "assets" / "bases" / f"{base_xml}.xml"
        )
        base_mjcf = mujoco.MjSpec.from_file(base_xml_path.as_posix())
        base_body = base_mjcf.body("base")
        assert base_body is not None, f"Base body not found in the {base_xml} XML file"

        # Fix conflict with robot "base" body name
        robot_base_body = robot_mjcf.body("base")
        if robot_base_body is not None:
            robot_base_body.name = "robot:base"

        attach_frame = base_body.add_frame()
        attach_frame.attach_body(robot_mjcf.bodies[1], "", "")

        return base_mjcf

    def _setup_references(self):
        """
        Set up environment-specific references.

        This method is called during initialization and can be overridden by
        subclasses to set up any environment-specific references or configurations
        that depend on the loaded robot model.
        """
        pass

    def _hide_overlay(self):
        """
        Hide the overlay menu in human render mode.

        This method hides the MuJoCo viewer menu when rendering in human mode,
        providing a cleaner visualization interface.
        """
        if self.render_mode == "human":
            viewer = self.robot_model.mujoco_renderer._get_viewer(
                render_mode=self.render_mode
            )
            viewer._hide_menu = True

    def _load_robot_model(self) -> BaseRobot:
        """
        Load and initialize the robot model.

        This method loads the robot class from the registry, creates the MuJoCo model,
        and initializes the robot with the provided configuration.

        Returns:
            BaseRobot: The initialized robot model

        Raises:
            AssertionError: If the robot name is not found in the registry
        """
        robot_name = self.robot_name.replace("_ik", "")
        assert robot_name in ROBOT_CLASS_REGISTORY, (
            f"Robot {robot_name} not found in the robot class registry"
        )
        robot_class: BaseRobot = ROBOT_CLASS_REGISTORY[robot_name]

        robot_xml_path = robot_class.xml_path

        mj_model = self._make_mjcf_model(robot_xml_path)

        robot_config = self.robot_config.copy()
        robot_config["mj_model"] = mj_model
        robot_config["default_camera_config"] = self.default_camera_config
        robot_config["render_mode"] = self.render_mode

        return robot_class(**robot_config)

    def _render_callback(self):
        """
        Callback function called before rendering.

        This method can be overridden by subclasses to perform any
        environment-specific rendering operations before the main render call.
        """
        pass

    def render(self):
        """
        Render the environment.

        Returns:
            The rendered output (format depends on render_mode)
        """
        self._render_callback()
        return self.robot_model.render()

    def compute_reward(self) -> float:
        """
        Compute the reward for the current state.

        This method must be implemented by subclasses to define the reward function
        for the specific environment.

        Returns:
            float: The computed reward value

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError

    def compute_terminated(self) -> bool:
        """
        Compute whether the episode has terminated.

        This method must be implemented by subclasses to define the termination
        conditions for the specific environment.

        Returns:
            bool: True if the episode should terminate, False otherwise

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError

    def _get_env_obs(self) -> np.ndarray:
        """
        Get environment-specific observations.

        This method can be overridden by subclasses to provide additional
        environment-specific observations beyond robot state.

        Returns:
            np.ndarray: Environment-specific observation array
        """
        return np.array([], dtype=np.float32)

    def _get_obs(self) -> np.ndarray:
        """
        Get the complete observation for the current state.

        This method combines robot observations with environment-specific
        observations to form the complete observation vector.

        Returns:
            np.ndarray: Complete observation array
        """
        robot_pos, robot_vel = self.robot_model.get_obs()
        env_obs = self._get_env_obs()
        return np.concatenate([robot_pos, robot_vel, env_obs], dtype=np.float32)

    def _get_info(self) -> dict:
        """
        Get additional information about the current state.

        This method can be overridden by subclasses to provide additional
        information that might be useful for debugging or logging.

        Returns:
            dict: Dictionary containing additional information
        """
        return {}

    def _reset_env(self):
        """
        Reset environment-specific components.

        This method can be overridden by subclasses to reset any
        environment-specific state that is not handled by the robot model.
        """
        pass

    def step(self, action):
        """
        Take a step in the environment based on the action and update the state.

        This method executes the given action, updates the environment state,
        computes the reward and termination condition, and returns the results.

        Args:
            action: The action to take (format depends on action_space)

        Returns:
            tuple: (observation, reward, terminated, truncated, info)
                - observation: The new observation after taking the action
                - reward: The reward received for this step
                - terminated: Whether the episode has terminated
                - truncated: Whether the episode was truncated (always False in this implementation)
                - info: Additional information about the step
        """
        self.robot_model.step(action)
        obs = self._get_obs()
        raw_reward = self.compute_reward()
        reward = self._total_reward(raw_reward)
        terminated = self.compute_terminated()
        truncated = False
        info = self._get_info()

        if self.robot_model.render_mode == "human":
            self.render()

        return obs, reward, terminated, truncated, info

    def close(self):
        """
        Clean up resources used by the environment.

        This method closes the robot model and any associated resources
        to prevent memory leaks.
        """
        self.robot_model.close()

    def reset(self, *, seed: Optional[int] = None, **kwargs):
        """
        Reset the environment to an initial state.

        This method resets both the robot model and any environment-specific
        components to their initial states.

        Args:
            seed (Optional[int]): Random seed for deterministic reset
            **kwargs: Additional keyword arguments passed to robot reset

        Returns:
            tuple: (observation, info)
                - observation: The initial observation
                - info: Additional information about the reset
        """
        self.robot_model.reset(seed=seed, deterministic=self.deterministic_reset)
        self._reset_env()
        obs = self._get_obs()
        info = self._get_info()

        return obs, info

    @property
    def data(self):
        """
        Get the MuJoCo data object.

        Returns:
            mujoco.MjData: The MuJoCo data object containing simulation state
        """
        return self.robot_model.data

    @property
    def model(self):
        """
        Get the MuJoCo model object.

        Returns:
            mujoco.MjModel: The MuJoCo model object containing simulation parameters
        """
        return self.robot_model.model

    def _total_reward(self, raw_reward: dict) -> float:
        """
        Compute the total reward from the raw reward dictionary.

        This method applies reward weights from the reward_config to compute
        the final reward value. It multiplies each reward component by its
        corresponding weight and sums them up.

        Args:
            raw_reward (dict): Dictionary containing individual reward components

        Returns:
            float: The weighted sum of all reward components

        Raises:
            AttributeError: If reward_config is not set on the environment
        """
        assert hasattr(self, "reward_config"), "reward_config is not set"
        reward_config = self.reward_config
        total_reward = 0.0
        for key, value in raw_reward.items():
            if key in reward_config:
                total_reward += reward_config[key] * value
        return total_reward