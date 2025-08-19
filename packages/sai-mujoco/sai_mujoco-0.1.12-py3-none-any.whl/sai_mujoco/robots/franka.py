import numpy as np
from sai_mujoco.robots.base import BaseRobot, ArmPart
from sai_mujoco.robots.models import GripperPart

class FrankaGripper(GripperPart):
    
    @property
    def dof(self):
        return 1

    def format_action(self, action):
        """
        Maps continuous action into binary output
        -1 => open, 1 => closed

        Args:
            action (np.array): gripper-specific action

        Raises:
            AssertionError: [Invalid action dimension size]
        """
        assert len(action) == self.dof
        if not hasattr(self, "current_action"):
            self.current_action = np.zeros(self.dof)
        self.current_action = np.clip(
            self.current_action + np.array([-1.0, 1.0]) * self.speed * np.sign(action),
            -1.0,
            1.0,
        )
        return self.current_action


class Franka(BaseRobot):
    r"""
    Robot model for Franka Emika's Panda arm consisting of 7 DOFs and a gripper. 

    This class defines the robot kinematics, default joint configuration, and controller
    parameters for a generic collaborative manipulator in the Sai MuJoCo framework.

    Attributes
    ----------
    default_pose : list of float
        A 12‑element list specifying the default joint positions (radians) for
        [joint1, …, joint7, finger_joint1, finger_joint2] on reset.
    name : str
        Unique identifier for this robot class (“franka”).
    metadata : dict
        Rendering configuration, including available modes (“human”, “rgb_array”, “depth_array”)
        and frames per second (“render_fps”: 12).
    left_arm : ArmPart
        Defines the 7‑DOF arm part, including:
          - `joint_names`: List of 7 joint names in the MuJoCo XML.
          - `_actuator_names`: List of 7 actuator keys corresponding to torque control.
          - `controller_config`: OSC controller gains, limits, and modes for both
            position and orientation control.
        The `gripper` sub‑part is a `GripperPart` that encapsulates:
          - `joint_names`: Two gear joints for opening/closing.
          - `_actuator_names`: Single actuator for finger torque.
          - `site_name`: Name of the grasp site in the MuJoCo model.
          - `controller_config`: Grip‐specific control mode.

    ## Observation Space

    The observation space consists of the following parts (in order):

    - *qpos (9 elements):* Position values of the robot's body parts. 7 elements for the joint positions and 2 for two gripper joints.
    - *qvel (9 elements):* The velocities of these individual body parts (their derivatives). 7 elements for the joint positions and 2 for two gripper joints.

    The order of elements in the observation space related to Mycobot is as follows - 

    | Num | Observation                              | Min  | Max | Type (Unit)              |
    | --- | -----------------------------------------| ---- | --- | ------------------------ |
    | 0   | joint1 position                          | -Inf | Inf | orientation (rad)        |
    | 1   | joint2 position                          | -Inf | Inf | orientation (rad)        |
    | 2   | joint3 position                          | -Inf | Inf | orientation (rad)        |
    | 3   | joint4 position                          | -Inf | Inf | orientation (rad)        |
    | 4   | joint5 position                          | -Inf | Inf | orientation (rad)        |
    | 5   | joint6 position                          | -Inf | Inf | orientation (rad)        |
    | 6   | joint7 position                          | -Inf | Inf | orientation (rad)        |
    | 7   | finger_joint1 position                   | -Inf | Inf | position (m)             |
    | 8   | finger_joint2 position                   | -Inf | Inf | position (m)             |
    | 9   | joint1 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 10  | joint2 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 11  | joint3 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 12  | joint4 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 13  | joint5 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 14  | joint6 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 15  | joint7 velocity                          | -Inf | Inf | angular velocity (rad/s) |
    | 16  | finger_joint1 velocity                   | -Inf | Inf | linear velocity (m/s)    |
    | 17  | finger_joint2 velocity                   | -Inf | Inf | linear velocity (m/s)    |

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
    
    name: str = "franka"

    frame_skip: int = 40

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
        _init_qpos=[
            0,
            np.pi / 16.0,
            0.00,
            -np.pi / 2.0 - np.pi / 3.0,
            0.00,
            np.pi - 0.2,
            np.pi / 4,
        ],
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
            "output_max": [0.05, 0.05, 0.05, 0.5, 0.5, 0.5],
            "output_min": [-0.05, -0.05, -0.05, -0.5, -0.5, -0.5],
            "kp": 550,
            "damping_ratio": 1.5,
            "impedance_mode": "fixed",
            "kp_limits": [0, 600],
            "damping_ratio_limits": [0, 10],
            "position_limits": None,
            "orientation_limits": None,
            "uncouple_pos_ori": True,
            "input_type": "delta",
            "input_ref_frame": "base",
            "interpolation": None,
            "ramp_ratio": 0.2,
        },
        gripper=FrankaGripper(
            joint_names=["finger_joint1", "finger_joint2"],
            _actuator_names=["gripper_finger_joint1", "gripper_finger_joint2"],
            site_name="grip_site",
            controller_config={"type": "GRIP"},
            important_bodies={
                "left_finger": "finger_joint1_tip",
                "right_finger": "finger_joint2_tip",
            },
        ),
    )
