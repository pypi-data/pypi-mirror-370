import numpy as np
from sai_mujoco.robots.base import BaseRobot
from sai_mujoco.robots.models import ArmPart, GripperPart


class XArm7Gripper(GripperPart):
    """
    Modifies XArm7 Gripper to only take one action.

    This gripper class provides a simplified control interface for the XArm7 gripper,
    mapping continuous actions to gripper opening/closing states with smooth transitions.

    Attributes
    ----------
    speed : float
        The speed at which the gripper opens/closes (0.2).
    dof : int
        Degrees of freedom for the gripper (1).
    current_action : np.ndarray
        Current gripper state, maintained across actions for smooth transitions.
    """

    def format_action(self, action):
        """
        -1 => fully open, +1 => fully closed
        """
        assert len(action) == self.dof  # i.e., 1
        # Suppose self.current_action is also shape (1,). Then:
        delta = self.speed * np.sign(action)
        if not hasattr(self, "current_action"):
            self.current_action = np.zeros(self.dof)
        self.current_action = np.clip(self.current_action + delta, -1.0, 1.0)
        return self.current_action

    @property
    def speed(self):
        return 0.2

    @property
    def dof(self):
        return 1


class XArm7(BaseRobot):
    r"""
    Robot model for XArm7 robotic arm consisting of 7 DOFs and a gripper.

    This class defines the robot kinematics, default joint configuration, and controller
    parameters for the XArm7 collaborative manipulator in the Sai MuJoCo framework.

    Attributes
    ----------
    default_pose : list of float
        A 7-element list specifying the default joint positions (radians) for
        [joint1, …, joint7] on reset: [0.0, 0.0, 0.0, 0.39π, 0.0, 0.39π, 0.0].
    name : str
        Unique identifier for this robot class ("xarm7").
    metadata : dict
        Rendering configuration, including available modes ("human", "rgb_array", "depth_array")
        and frames per second ("render_fps": 12).
    left_arm : ArmPart
        Defines the 7-DOF arm part, including:
          - `joint_names`: List of 7 joint names in the MuJoCo XML.
          - `_actuator_names`: List of 7 actuator keys corresponding to torque control.
          - `controller_config`: OSC controller gains, limits, and modes for both
            position and orientation control.
        The `gripper` sub-part is a `GripperPart` that encapsulates:
          - `joint_names`: Two driver joints for opening/closing.
          - `_actuator_names`: Single actuator for gripper control.
          - `site_name`: Name of the grasp site in the MuJoCo model.
          - `controller_config`: Grip-specific control mode.

    ## Observation Space

    The observation space consists of the following parts (in order):

    - *qpos (9 elements):* Position values of the robot's body parts. 7 elements for the joint positions and 2 for two gripper joints.
    - *qvel (9 elements):* The velocities of these individual body parts (their derivatives). 7 elements for the joint positions and 2 for two gripper joints.

    The order of elements in the observation space related to XArm7 is as follows -

    | Num | Observation                              | Min  | Max | Type (Unit)              |
    | --- | -----------------------------------------| ---- | --- | ------------------------ |
    | 0   | joint1 position                          | -Inf | Inf | orientation (rad)        |
    | 1   | joint2 position                          | -Inf | Inf | orientation (rad)        |
    | 2   | joint3 position                          | -Inf | Inf | orientation (rad)        |
    | 3   | joint4 position                          | -Inf | Inf | orientation (rad)        |
    | 4   | joint5 position                          | -Inf | Inf | orientation (rad)        |
    | 5   | joint6 position                          | -Inf | Inf | orientation (rad)        |
    | 6   | joint7 position                          | -Inf | Inf | orientation (rad)        |
    | 7   | left_driver_joint position               | -Inf | Inf | position (m)             |
    | 8   | right_driver_joint position              | -Inf | Inf | position (m)             |
    | 9   | joint1 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 10  | joint2 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 11  | joint3 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 12  | joint4 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 13  | joint5 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 14  | joint6 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 15  | joint7 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 16  | left_driver_joint velocity               | -Inf | Inf | linear velocity (m/s)    |
    | 17  | right_driver_joint velocity              | -Inf | Inf | linear velocity (m/s)    |

    ## Action Space

    The action space is a continuous vector of shape `(7,)`, where each dimension corresponds to a component of the inverse kinematics command for the robotic arm's end-effector pose and gripper control. The table below describes each dimension, interpreted by the IK solver to compute joint commands.

    | Index | Action                                     |
    | ----- | ------------------------------------------ |
    | 0     | End-Effector X ($\Delta x$)                |
    | 1     | End-Effector Y ($\Delta y$)                |
    | 2     | End-Effector Z ($\Delta z$)                |
    | 3     | End-Effector Roll ($\Delta \text{roll}$)   |
    | 4     | End-Effector Pitch ($\Delta \text{pitch}$) |
    | 5     | End-Effector Yaw ($\Delta \text{yaw}$)     |
    | 6     | Gripper Open/Close                         |

    - *End-Effector X, Y, Z (Indices 0-2):* Specifies the displacement (delta) of the end-effector relative to its current position, given as $[\Delta x, \Delta y, \Delta z]$ in meters.
    - *End-Effector Roll, Pitch, Yaw (Indices 3-5):* Specifies the angular displacement (delta) of the end-effector orientation relative to its current orientation, given as $[\Delta \text{roll}, \Delta \text{pitch}, \Delta \text{yaw}]$ in radians, applied as incremental rotations.
    - *Gripper Open/Close (Index 6):* Adjusts the gripper state, where $-1$ closes and $1$ fully opens. This behavior is identical in both environments.
    """

    name: str = "xarm7"

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 12,
    }

    left_arm = ArmPart(
        joint_names=[
            "joint1",
            "joint2",
            "joint3",
            "joint4",
            "joint5",
            "joint6",
            "joint7",
        ],
        _init_qpos=[0.0, 0.0, 0.0, 0.39 * np.pi, 0.0, 0.39 * np.pi, 0.0],
        _actuator_names=[
            "torq_j1",
            "torq_j2",
            "torq_j3",
            "torq_j4",
            "torq_j5",
            "torq_j6",
            "torq_j7",
        ],
        controller_config={
            "type": "OSC_POSE",
            "input_max": 1,
            "input_min": -1,
            "output_max": [0.1, 0.1, 0.1, 0.5, 0.5, 0.5],
            "output_min": [-0.1, -0.1, -0.1, -0.5, -0.5, -0.5],
            "kp": 150,
            "damping_ratio": 1,
            "impedance_mode": "fixed",
            "kp_limits": [0, 300],
            "damping_ratio_limits": [0, 10],
            "position_limits": None,
            "orientation_limits": None,
            "uncouple_pos_ori": True,
            "input_type": "delta",
            "input_ref_frame": "base",
            "interpolation": None,
            "ramp_ratio": 0.2,
        },
        gripper=XArm7Gripper(
            joint_names=[
                "robot:left_driver_joint",
                "robot:right_driver_joint",
            ],
            _actuator_names=["gripper"],
            site_name="grip_site",
            controller_config={"type": "GRIP"},
            important_bodies={
                "left_finger": "left_finger",
                "right_finger": "right_finger",
            },
        ),
    )
