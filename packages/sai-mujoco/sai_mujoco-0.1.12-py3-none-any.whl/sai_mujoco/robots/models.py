from dataclasses import dataclass, field
import numpy as np


@dataclass
class Part:
    joint_names: list[str] = field(default_factory=list)
    controller_config: dict = None
    _actuator_names: list[str] = None
    _init_qpos: np.ndarray | dict[str, np.ndarray] = None
    _init_qvel: np.ndarray = None
    naming_prefix: str = ""

    @property
    def actuator_names(self):
        if self._actuator_names is None:
            return self.joint_names
        return self._actuator_names

    @property
    def dof(self):
        """
        Defines the number of DOF of the gripper

        Returns:
            int: gripper DOF
        """
        return len(self.actuator_names)

    @property
    def init_qpos(self):
        if self._init_qpos is None:
            return np.zeros(len(self.joint_names))
        return self._init_qpos

    @property
    def init_qvel(self):
        if self._init_qvel is None:
            return np.zeros(len(self.joint_names))
        return self._init_qvel


@dataclass
class GripperPart(Part):
    site_name: str = None
    important_bodies: dict[str, str] = field(default_factory=dict)

    @property
    def speed(self):
        """
        How quickly the gripper opens / closes

        Returns:
            float: Speed of the gripper
        """
        return 0.3

    def format_action(self, action):
        return action

@dataclass
class ArmPart(Part):
    gripper: GripperPart = None