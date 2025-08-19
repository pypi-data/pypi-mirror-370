from pathlib import Path
import numpy as np
import mujoco
from gymnasium import spaces
from sai_mujoco.controllers.composite import composite_controller_factory
from sai_mujoco.utils.mujoco_env import MujocoEnv
import sai_mujoco
from sai_mujoco.robots.models import Part, ArmPart


class BaseRobotMeta(type):
    """Metaclass to automatically construct XML path from robot name and set up part dictionaries."""

    def __new__(mcs, name, bases, namespace):
        # Get the robot name
        robot_name = namespace.get("name")

        xml_path = namespace.get("xml_path")

        if xml_path is None:
            xml_path = "robot.xml"

        # Construct XML path if robot_name is provided
        if robot_name is not None:
            namespace["xml_path"] = str(
                Path(sai_mujoco.__file__).parent
                / "assets"
                / "robots"
                / robot_name
                / xml_path
            )

        # Define part categories
        part_categories = {
            "arms": ["left_arm", "right_arm"],
            "legs": ["left_leg", "right_leg"],
            "core_parts": ["base", "torso", "head"],
        }

        # Create part dictionaries directly as class attributes
        parts = {}
        arms = {}
        legs = {}
        grippers = {}

        # Process all part categories
        for part_name in (
            part_categories["core_parts"]
            + part_categories["arms"]
            + part_categories["legs"]
        ):
            part = namespace.get(part_name, None)
            if part is not None and part.controller_config is not None:
                parts[part_name] = part

                # Categorize the part
                if part_name in part_categories["arms"]:
                    arms[part_name] = part
                    # Handle gripper if present
                    if hasattr(part, "gripper") and part.gripper is not None:
                        gripper_name = f"{part_name}_gripper"
                        grippers[gripper_name] = part.gripper
                        parts[gripper_name] = part.gripper
                elif part_name in part_categories["legs"]:
                    legs[part_name] = part

        # Set class attributes
        namespace["_parts"] = parts
        namespace["_arms"] = arms
        namespace["_legs"] = legs
        namespace["_grippers"] = grippers
        namespace["gripper_joints"] = [
            joint for gripper in grippers.values() for joint in gripper.joint_names
        ]

        return super().__new__(mcs, name, bases, namespace)


class BaseRobot(MujocoEnv, metaclass=BaseRobotMeta):
    """
    Base robot class for MuJoCo robots.

    The BaseRobotMeta metaclass automatically constructs the xml_path from the robot name:
    - xml_path: assets/robots/{name}/robot.xml

    Subclasses should set:
    - name: str - The name of the robot (used to construct xml_path)

    Example:
        class FrankaRobot(BaseRobot):
            name = "franka"
            # xml_path will be automatically set to: assets/robots/franka/robot.xml
    """

    # Class-level configuration - subclasses should override this
    name: str = "base_robot"

    frame_skip: int = 40

    metadata: dict = None

    composite_controller_config: dict = {"type": "BASIC"}

    # Robot parts configuration
    base: Part = None
    torso: Part = None
    head: Part = None
    left_arm: ArmPart = None
    right_arm: ArmPart = None
    left_leg: Part = None
    right_leg: Part = None

    # XML path is automatically constructed by the metaclass
    xml_path: str = None

    def __init__(
        self,
        mj_model: mujoco.MjModel,
        default_camera_config: dict = None,
        **kwargs,
    ) -> None:
        self.kwargs = kwargs

        self.reset_noise = kwargs.get("reset_noise")

        if self.reset_noise is None:
            self.reset_noise = {
                "magnitude": 0.0,
                "type": "gaussian",
            }  # no noise conditions
        elif self.reset_noise == "default":
            self.reset_noise = {"magnitude": 0.02, "type": "gaussian"}
        self.reset_noise["magnitude"] = (
            self.reset_noise["magnitude"] if self.reset_noise["magnitude"] else 0.0
        )

        super().__init__(
            mj_model,
            observation_space=None,
            frame_skip=self.frame_skip,
            default_camera_config=default_camera_config,
            render_mode=kwargs.get("render_mode", None),
            width=kwargs.get("width", 1280),
            height=kwargs.get("height", 720),
        )

        self.composite_controller = None

        self.part_controllers = {}

        self.part_controller_config = {}

        self._ref_actuators_indexes_dict = {}
        self._robot_init_qpos = {}
        self.eef_site_id = {}

        self._default_init_qpos()

        if kwargs.get("init_qpos") is not None:
            assert isinstance(kwargs.get("init_qpos"), dict), (
                "init_qpos must be a dict of joint names and values! Instead, got type: {}".format(
                    type(kwargs.get("init_qpos"))
                )
            )
            for joint_name, init_q in kwargs.get("init_qpos").items():
                self._robot_init_qpos[joint_name] = init_q

        self._load_controller_config()

        self.reset_model()

        self._set_action_space()

    def _postprocess_part_controller_config(self):
        """
        Update part_controller_config with values from composite_controller_config for each body part.
        Remove unused parts that are not in the controller.
        Called by _load_controller() function
        """
        for part_name, controller_config in self.composite_controller_config.get(
            "body_parts", {}
        ).items():
            if part_name in self.part_controller_config:
                self.part_controller_config[part_name].update(controller_config)

    def _load_controller(self):
        """
        Loads controller to be used for dynamic trajectories
        """

        # Flag for loading urdf once (only applicable for IK controllers)
        self.composite_controller = composite_controller_factory(
            type=self.composite_controller_config.get("type", "BASIC"),
            sim=self.sim,
            arms=self._arms,
            grippers=self._grippers,
        )

        self._load_arm_controllers()

        # default base, torso, and head controllers are inherited from MobileRobot
        self._load_base_controller()

        self._load_leg_controllers()

        self._load_head_controller()
        self._load_torso_controller()
        self._postprocess_part_controller_config()

        self.composite_controller.load_controller_config(
            self.part_controller_config, self.composite_controller_config
        )

    def _load_controller_config(self):
        assert hasattr(self, "composite_controller_config"), (
            "composite_controller_config is not set"
        )

        for part_name, part in self._parts.items():
            self.part_controller_config[part_name] = part.controller_config

        self.composite_controller_config["body_parts"] = {}
        for name, config in self.part_controller_config.items():
            self.composite_controller_config["body_parts"][name] = config

    def step(self, action):
        for i in range(self.frame_skip):
            self.sim.step1()
            self.control(action)
            self.sim.step2()

    def control(self, action):
        """
        Actuate the robot with the
        passed joint velocities and gripper control.

        Args:
            action (np.array): The control to apply to the robot. The first @self.robot_model.dof dimensions should
                be the desired normalized joint velocities and if the robot has a gripper, the next @self.gripper.dof
                dimensions should be actuation controls for the gripper.

                :NOTE: Assumes inputted actions are of form:
                    [right_arm_control, right_gripper_control, left_arm_control, left_gripper_control]

        Raises:
            AssertionError: [Invalid action dimension]
        """
        # clip actions into valid range
        assert len(action) == self.action_dim, (
            "environment got invalid action dimension -- expected {}, got {}".format(
                self.action_dim, len(action)
            )
        )

        self.composite_controller.set_goal(action)

        applied_action_dict = self.composite_controller.run_controller()
        for part_name, applied_action in applied_action_dict.items():
            actuator_indexes = self._ref_actuators_indexes_dict[part_name]
            applied_action_low = self.model.actuator_ctrlrange[actuator_indexes, 0]
            applied_action_high = self.model.actuator_ctrlrange[actuator_indexes, 1]
            applied_action = np.clip(
                applied_action, applied_action_low, applied_action_high
            )
            self.data.ctrl[actuator_indexes] = applied_action

    def reset_model(self, deterministic: bool = False, **kwargs):
        qpos = self.init_qpos
        qvel = self.init_qvel
        self.set_state(qpos, qvel)
        self._reset_robot_joints(deterministic)

        self._load_controller()

        self.composite_controller.update_state()
        self.composite_controller.reset()

    def _reset_robot_joints(self, deterministic: bool = False):
        if not deterministic:
            # Determine noise
            if self.reset_noise["type"] == "gaussian":
                noise = (
                    self.np_random.normal(size=len(self._robot_init_qpos))
                    * self.reset_noise["magnitude"]
                )
            elif self.reset_noise["type"] == "uniform":
                noise = (
                    self.np_random.uniform(-1.0, 1.0, len(self._robot_init_qpos))
                    * self.reset_noise["magnitude"]
                )
            else:
                raise ValueError(
                    "Error: Invalid noise type specified. Options are 'gaussian' or 'uniform'."
                )
        else:
            noise = np.zeros(len(self._robot_init_qpos))

        for i, (joint_name, init_q) in enumerate(self._robot_init_qpos.items()):
            # Don't add noise to the gripper joints
            if joint_name in self.gripper_joints:
                noise[i] = 0
            self.sim.data.set_joint_qpos(joint_name, init_q + noise[i])
        self.sim.forward()

    def _default_init_qpos(self):
        for part_name, part in self._parts.items():
            if isinstance(part.init_qpos, dict):
                self._robot_init_qpos.update(part.init_qpos)
            elif isinstance(part.init_qpos, list) or isinstance(
                part.init_qpos, np.ndarray
            ):
                for i, joint_name in enumerate(part.joint_names):
                    self._robot_init_qpos[joint_name] = part.init_qpos[i]
            else:
                raise ValueError(
                    f"Invalid init_qpos type: {type(part.init_qpos)} for part {part_name}"
                )

    def close(self):
        self.mujoco_renderer.close()

    def get_obs(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns the joint positions and velocities of the robot."""
        robot_qpos = [
            self.sim.data.get_joint_qpos(joint_name) for joint_name in self.robot_joints
        ]
        robot_qvel = [
            self.sim.data.get_joint_qvel(joint_name) for joint_name in self.robot_joints
        ]
        return robot_qpos, robot_qvel

    def _load_leg_controllers(self):
        for leg_name, leg in self._legs.items():
            if leg.controller_config is None:
                continue

            self.part_controller_config[leg_name]["ramp_ratio"] = 1.0
            self.part_controller_config[leg_name]["robot_name"] = self.name

            self.part_controller_config[leg_name]["sim"] = self.sim
            self.part_controller_config[leg_name]["part_name"] = leg_name
            self.part_controller_config[leg_name]["naming_prefix"] = leg.naming_prefix
            self.part_controller_config[leg_name]["ndim"] = leg.dof
            self.part_controller_config[leg_name]["policy_freq"] = self.frame_skip

            ref_legs_joint_indexes = [
                self.sim.model.joint_name2id(x) for x in leg.joint_names
            ]
            ref_legs_joint_pos_indexes = [
                self.sim.model.get_joint_qpos_addr(x) for x in leg.joint_names
            ]
            ref_legs_joint_vel_indexes = [
                self.sim.model.get_joint_qvel_addr(x) for x in leg.joint_names
            ]
            self.part_controller_config[leg_name]["joint_indexes"] = {
                "joints": ref_legs_joint_indexes,
                "qpos": ref_legs_joint_pos_indexes,
                "qvel": ref_legs_joint_vel_indexes,
            }

            self._ref_actuators_indexes_dict[leg_name] = [
                self.sim.model.actuator_name2id(actuator)
                for actuator in leg.actuator_names
            ]

            low = self.sim.model.actuator_ctrlrange[
                self._ref_actuators_indexes_dict[leg_name], 0
            ]
            high = self.sim.model.actuator_ctrlrange[
                self._ref_actuators_indexes_dict[leg_name], 1
            ]

            self.part_controller_config[leg_name]["actuator_range"] = (low, high)

    def _load_arm_controllers(self):
        # Load composite controller configs for both left and right arm
        for arm_name, arm in self._arms.items():
            if arm.controller_config is None:
                continue

            # Assert that the controller config is a dict file:
            #             NOTE: "type" must be one of: {JOINT_POSITION, JOINT_TORQUE, JOINT_VELOCITY,
            #                                           OSC_POSITION, OSC_POSE, IK_POSE}
            assert isinstance(self.part_controller_config[arm_name], dict), (
                "Inputted controller config must be a dict! Instead, got type: {}".format(
                    type(self.part_controller_config[arm_name])
                )
            )

            # Add to the controller dict additional relevant params:
            #   the robot name, mujoco sim, eef_name, actuator_range, joint_indexes, timestep (model) freq,
            #   policy (control) freq, and ndim (# joints)
            self.part_controller_config[arm_name]["robot_name"] = self.name
            self.part_controller_config[arm_name]["sim"] = self.sim
            self.part_controller_config[arm_name]["ref_name"] = (
                arm.gripper.site_name if arm.gripper is not None else None
            )
            self.part_controller_config[arm_name]["part_name"] = arm_name
            self.part_controller_config[arm_name]["naming_prefix"] = arm.naming_prefix

            self.part_controller_config[arm_name]["eef_rot_offset"] = np.array(
                [0, 0, 0, 1]
            )
            self.part_controller_config[arm_name]["ndim"] = arm.dof
            self.part_controller_config[arm_name]["policy_freq"] = self.frame_skip
            self.part_controller_config[arm_name]["lite_physics"] = True

            self.part_controller_config[arm_name]["joint_indexes"] = {
                "joints": [
                    self.sim.model.joint_name2id(joint) for joint in arm.joint_names
                ],
                "qpos": [
                    self.sim.model.get_joint_qpos_addr(joint)
                    for joint in arm.joint_names
                ],
                "qvel": [
                    self.sim.model.get_joint_qvel_addr(joint)
                    for joint in arm.joint_names
                ],
            }
            self.part_controller_config[arm_name]["actuator_range"] = (
                self.sim.model.actuator_ctrlrange[
                    [
                        self.sim.model.actuator_name2id(actuator)
                        for actuator in arm.actuator_names
                    ],
                    0,
                ],
                self.sim.model.actuator_ctrlrange[
                    [
                        self.sim.model.actuator_name2id(actuator)
                        for actuator in arm.actuator_names
                    ],
                    1,
                ],
            )

            # Only load urdf the first time this controller gets called
            self.part_controller_config[arm_name]["load_urdf"] = False

            self._ref_actuators_indexes_dict[arm_name] = [
                self.sim.model.actuator_name2id(actuator)
                for actuator in arm.actuator_names
            ]

            if arm.gripper is not None:
                # Load gripper controllers
                gripper_name = f"{arm_name}_gripper"
                self.part_controller_config[gripper_name]["part_name"] = gripper_name
                self.part_controller_config[gripper_name]["robot_name"] = self.name
                self.part_controller_config[gripper_name]["sim"] = self.sim
                self.part_controller_config[gripper_name]["eef_name"] = (
                    arm.gripper.site_name
                )
                self.part_controller_config[gripper_name]["naming_prefix"] = (
                    arm.gripper.naming_prefix
                )
                self.part_controller_config[gripper_name]["ndim"] = arm.gripper.dof
                self.part_controller_config[gripper_name]["policy_freq"] = (
                    self.frame_skip
                )
                self.part_controller_config[gripper_name]["joint_indexes"] = {
                    "joints": [
                        self.sim.model.joint_name2id(joint)
                        for joint in arm.gripper.joint_names
                    ],
                    "actuators": [
                        self.sim.model.actuator_name2id(actuator)
                        for actuator in arm.gripper.actuator_names
                    ],
                    "qpos": [
                        self.sim.model.get_joint_qpos_addr(joint)
                        for joint in arm.gripper.joint_names
                    ],
                    "qvel": [
                        self.sim.model.get_joint_qvel_addr(joint)
                        for joint in arm.gripper.joint_names
                    ],
                }
                low = self.sim.model.actuator_ctrlrange[
                    [
                        self.sim.model.actuator_name2id(actuator)
                        for actuator in arm.gripper.actuator_names
                    ],
                    0,
                ]
                high = self.sim.model.actuator_ctrlrange[
                    [
                        self.sim.model.actuator_name2id(actuator)
                        for actuator in arm.gripper.actuator_names
                    ],
                    1,
                ]

                self.part_controller_config[gripper_name]["actuator_range"] = (
                    low,
                    high,
                )

                self._ref_actuators_indexes_dict[gripper_name] = [
                    self.sim.model.actuator_name2id(actuator)
                    for actuator in arm.gripper.actuator_names
                ]

    def _load_base_controller(self):
        """
        Load base controller
        """
        if self.base is None or self.base.controller_config is None:
            return

        self.part_controller_config["base"]["ramp_ratio"] = 1.0
        self.part_controller_config["base"]["robot_name"] = self.name

        self.part_controller_config["base"]["sim"] = self.sim
        self.part_controller_config["base"]["part_name"] = "base"
        self.part_controller_config["base"]["naming_prefix"] = self.base.naming_prefix
        self.part_controller_config["base"]["ndim"] = self.base.dof
        self.part_controller_config["base"]["policy_freq"] = self.frame_skip
        self.part_controller_config["base"]["lite_physics"] = True

        ref_base_joint_indexes = [
            self.sim.model.joint_name2id(x) for x in self.base.joint_names
        ]
        ref_base_joint_pos_indexes = [
            self.sim.model.get_joint_qpos_addr(x) for x in self.base.joint_names
        ]
        ref_base_joint_vel_indexes = [
            self.sim.model.get_joint_qvel_addr(x) for x in self.base.joint_names
        ]
        self.part_controller_config["base"]["joint_indexes"] = {
            "joints": ref_base_joint_indexes,
            "qpos": ref_base_joint_pos_indexes,
            "qvel": ref_base_joint_vel_indexes,
        }

        low = self.sim.model.actuator_ctrlrange[
            [
                self.sim.model.actuator_name2id(actuator)
                for actuator in self.base.actuator_names
            ],
            0,
        ]
        high = self.sim.model.actuator_ctrlrange[
            [
                self.sim.model.actuator_name2id(actuator)
                for actuator in self.base.actuator_names
            ],
            1,
        ]

        self.part_controller_config["base"]["actuator_range"] = (low, high)

        self._ref_actuators_indexes_dict["base"] = [
            self.sim.model.actuator_name2id(actuator)
            for actuator in self.base.actuator_names
        ]

    def _load_torso_controller(self):
        """
        Load torso controller
        """
        if self.torso is None or self.torso.controller_config is None:
            return

        self.part_controller_config["torso"]["robot_name"] = self.name
        self.part_controller_config["torso"]["sim"] = self.sim
        self.part_controller_config["torso"]["part_name"] = "torso"
        self.part_controller_config["torso"]["naming_prefix"] = self.torso.naming_prefix
        self.part_controller_config["torso"]["policy_freq"] = self.frame_skip
        self.part_controller_config["torso"]["lite_physics"] = True

        ref_torso_joint_indexes = [
            self.sim.model.joint_name2id(x) for x in self.torso.joint_names
        ]
        ref_torso_joint_pos_indexes = [
            self.sim.model.get_joint_qpos_addr(x) for x in self.torso.joint_names
        ]
        ref_torso_joint_vel_indexes = [
            self.sim.model.get_joint_qvel_addr(x) for x in self.torso.joint_names
        ]
        self.part_controller_config["torso"]["joint_indexes"] = {
            "joints": ref_torso_joint_indexes,
            "qpos": ref_torso_joint_pos_indexes,
            "qvel": ref_torso_joint_vel_indexes,
        }

        low = self.sim.model.actuator_ctrlrange[
            [
                self.sim.model.actuator_name2id(actuator)
                for actuator in self.torso.actuator_names
            ],
            0,
        ]
        high = self.sim.model.actuator_ctrlrange[
            [
                self.sim.model.actuator_name2id(actuator)
                for actuator in self.torso.actuator_names
            ],
            1,
        ]
        self.part_controller_config["torso"]["actuator_range"] = (low, high)

        self._ref_actuators_indexes_dict["torso"] = [
            self.sim.model.actuator_name2id(actuator)
            for actuator in self.torso.actuator_names
        ]

    def _load_head_controller(self):
        """
        Load head controller
        """
        if self.head is None or self.head.controller_config is None:
            return

        self.part_controller_config["head"]["robot_name"] = self.name
        self.part_controller_config["head"]["sim"] = self.sim

        self.part_controller_config["head"]["part_name"] = "head"
        self.part_controller_config["head"]["naming_prefix"] = self.head.naming_prefix
        self.part_controller_config["head"]["ndim"] = self.head.dof
        self.part_controller_config["head"]["policy_freq"] = self.frame_skip
        self.part_controller_config["head"]["lite_physics"] = True

        ref_head_joint_indexes = [
            self.sim.model.joint_name2id(x) for x in self.head.joint_names
        ]
        ref_head_joint_pos_indexes = [
            self.sim.model.get_joint_qpos_addr(x) for x in self.head.joint_names
        ]
        ref_head_joint_vel_indexes = [
            self.sim.model.get_joint_qvel_addr(x) for x in self.head.joint_names
        ]
        self.part_controller_config["head"]["joint_indexes"] = {
            "joints": ref_head_joint_indexes,
            "qpos": ref_head_joint_pos_indexes,
            "qvel": ref_head_joint_vel_indexes,
        }

        low = self.sim.model.actuator_ctrlrange[
            [
                self.sim.model.actuator_name2id(actuator)
                for actuator in self.head.actuator_names
            ],
            0,
        ]
        high = self.sim.model.actuator_ctrlrange[
            [
                self.sim.model.actuator_name2id(actuator)
                for actuator in self.head.actuator_names
            ],
            1,
        ]

        self.part_controller_config["head"]["actuator_range"] = (low, high)

        self._ref_actuators_indexes_dict["head"] = [
            self.sim.model.actuator_name2id(actuator)
            for actuator in self.head.actuator_names
        ]

    @property
    def action_limits(self):
        return self.composite_controller.action_limits

    @property
    def action_dim(self):
        return self.action_limits[0].shape[0]

    @property
    def robot_joints(self):
        _joints = []
        for _, part in self._parts.items():
            _joints.extend(part.joint_names)
        return _joints

    @property
    def robot_actuators(self):
        _actuators = []
        for part_name, part in self._parts.items():
            _actuators.extend(part.actuator_names)
        return _actuators

    def _set_action_space(self):
        self.action_space = spaces.Box(
            low=self.action_limits[0].astype(np.float32),
            high=self.action_limits[1].astype(np.float32),
            dtype=np.float32,
        )
        return self.action_space

    def get_sensor_measurement(self, sensor_name):
        """
        Grabs relevant sensor data from the sim object

        Args:
            sensor_name (str): name of the sensor

        Returns:
            np.array: sensor values
        """
        sensor_idx = np.sum(
            self.sim.model.sensor_dim[: self.sim.model.sensor_name2id(sensor_name)]
        )
        sensor_dim = self.sim.model.sensor_dim[
            self.sim.model.sensor_name2id(sensor_name)
        ]
        return np.array(self.sim.data.sensordata[sensor_idx : sensor_idx + sensor_dim])