from sai_mujoco.robots.base import BaseRobot
from sai_mujoco.robots.models import Part, ArmPart

class Humanoid(BaseRobot):
    r"""
    Robot model for a humanoid robot with articulated arms, legs, and torso.

    This class defines the robot kinematics, default joint configuration, and controller
    parameters for a humanoid robot in the Sai MuJoCo framework. The humanoid consists
    of multiple articulated parts including arms, legs, and torso, each with their own
    joint configurations and control parameters.

    Attributes
    ----------
    name : str
        Unique identifier for this robot class ("humanoid").
    frame_skip : int
        Number of simulation steps to skip between control actions (5).
    metadata : dict
        Rendering configuration, including available modes ("human", "rgb_array", "depth_array")
        and frames per second ("render_fps": 100).
    left_arm : ArmPart
        Defines the left arm with 3 DOFs:
          - `joint_names`: List of 3 joint names for shoulder and elbow control.
          - `_init_qpos`: Initial joint positions for the left arm.
          - `controller_config`: Joint position controller with kp=200.
    right_arm : ArmPart
        Defines the right arm with 3 DOFs:
          - `joint_names`: List of 3 joint names for shoulder and elbow control.
          - `controller_config`: Joint position controller with kp=200.
    left_leg : Part
        Defines the left leg with 6 DOFs:
          - `joint_names`: List of 6 joint names for hip, knee, and ankle control.
          - `controller_config`: Joint position controller with kp=200.
    right_leg : Part
        Defines the right leg with 6 DOFs:
          - `joint_names`: List of 6 joint names for hip, knee, and ankle control.
          - `controller_config`: Joint position controller with kp=200.
    torso : Part
        Defines the torso with 3 DOFs:
          - `joint_names`: List of 3 joint names for abdomen control.
          - `controller_config`: Joint position controller with kp=200.
    standing_height : list
        Height range for standing pose [0.6, 2.0] meters.
    feet_sites : list
        List of foot site names for contact detection.
    _left_feet_geoms : list
        List of left foot geometry names.
    _right_feet_geoms : list
        List of right foot geometry names.
    _root_site : str
        Name of the root site for the humanoid.

    ## Observation Space

    The observation space consists of the following parts (in order):

    - *qpos (21 elements):* Position values of the robot's body parts. 21 elements for all joint positions across arms, legs, and torso.
    - *qvel (21 elements):* The velocities of these individual body parts (their derivatives). 21 elements for all joint velocities.

    The order of elements in the observation space related to Humanoid is as follows -

    | Num | Observation                              | Min  | Max | Type (Unit)              |
    | --- | -----------------------------------------| ---- | --- | ------------------------ |
    | 0   | abdomen_y position                       | -Inf | Inf | orientation (rad)        |
    | 1   | abdomen_z position                       | -Inf | Inf | orientation (rad)        |
    | 2   | abdomen_x position                       | -Inf | Inf | orientation (rad)        |
    | 3   | hip_x_left position                      | -Inf | Inf | orientation (rad)        |
    | 4   | hip_z_left position                      | -Inf | Inf | orientation (rad)        |
    | 5   | hip_y_left position                      | -Inf | Inf | orientation (rad)        |
    | 6   | knee_left position                       | -Inf | Inf | orientation (rad)        |
    | 7   | ankle_x_left position                    | -Inf | Inf | orientation (rad)        |
    | 8   | ankle_y_left position                    | -Inf | Inf | orientation (rad)        |
    | 9   | hip_x_right position                     | -Inf | Inf | orientation (rad)        |
    | 10  | hip_z_right position                     | -Inf | Inf | orientation (rad)        |
    | 11  | hip_y_right position                     | -Inf | Inf | orientation (rad)        |
    | 12  | knee_right position                      | -Inf | Inf | orientation (rad)        |
    | 13  | ankle_x_right position                   | -Inf | Inf | orientation (rad)        |
    | 14  | ankle_y_right position                   | -Inf | Inf | orientation (rad)        |
    | 15  | shoulder1_left position                  | -Inf | Inf | orientation (rad)        |
    | 16  | shoulder2_left position                  | -Inf | Inf | orientation (rad)        |
    | 17  | elbow_left position                      | -Inf | Inf | orientation (rad)        |
    | 18  | shoulder1_right position                 | -Inf | Inf | orientation (rad)        |
    | 19  | shoulder2_right position                 | -Inf | Inf | orientation (rad)        |
    | 20  | elbow_right position                     | -Inf | Inf | orientation (rad)        |
    | 21  | abdomen_y velocity                       | -Inf | Inf | angular velocity (rad/s) |
    | 22  | abdomen_z velocity                       | -Inf | Inf | angular velocity (rad/s) |
    | 23  | abdomen_x velocity                       | -Inf | Inf | angular velocity (rad/s) |
    | 24  | hip_x_left velocity                      | -Inf | Inf | angular velocity (rad/s) |
    | 25  | hip_z_left velocity                      | -Inf | Inf | angular velocity (rad/s) |
    | 26  | hip_y_left velocity                      | -Inf | Inf | angular velocity (rad/s) |
    | 27  | knee_left velocity                       | -Inf | Inf | angular velocity (rad/s) |
    | 28  | ankle_x_left velocity                    | -Inf | Inf | angular velocity (rad/s) |
    | 29  | ankle_y_left velocity                    | -Inf | Inf | angular velocity (rad/s) |
    | 30  | hip_x_right velocity                     | -Inf | Inf | angular velocity (rad/s) |
    | 31  | hip_z_right velocity                     | -Inf | Inf | angular velocity (rad/s) |
    | 32  | hip_y_right velocity                     | -Inf | Inf | angular velocity (rad/s) |
    | 33  | knee_right velocity                      | -Inf | Inf | angular velocity (rad/s) |
    | 34  | ankle_x_right velocity                   | -Inf | Inf | angular velocity (rad/s) |
    | 35  | ankle_y_right velocity                   | -Inf | Inf | angular velocity (rad/s) |
    | 36  | shoulder1_left velocity                  | -Inf | Inf | angular velocity (rad/s) |
    | 37  | shoulder2_left velocity                  | -Inf | Inf | angular velocity (rad/s) |
    | 38  | elbow_left velocity                      | -Inf | Inf | angular velocity (rad/s) |
    | 39  | shoulder1_right velocity                 | -Inf | Inf | angular velocity (rad/s) |
    | 40  | shoulder2_right velocity                 | -Inf | Inf | angular velocity (rad/s) |
    | 41  | elbow_right velocity                     | -Inf | Inf | angular velocity (rad/s) |

    ## Action Space

    The action space is a continuous vector of shape `(21,)`, where each dimension corresponds to a joint position command for the humanoid's articulated parts. The table below describes each dimension, interpreted by the joint position controllers to compute joint commands.

    | Index | Action                                     |
    | ----- | ------------------------------------------ |
    | 0     | abdomen_y position                         |
    | 1     | abdomen_z position                         |
    | 2     | abdomen_x position                         |
    | 3     | hip_x_left position                        |
    | 4     | hip_z_left position                        |
    | 5     | hip_y_left position                        |
    | 6     | knee_left position                         |
    | 7     | ankle_x_left position                      |
    | 8     | ankle_y_left position                      |
    | 9     | hip_x_right position                       |
    | 10    | hip_z_right position                       |
    | 11    | hip_y_right position                       |
    | 12    | knee_right position                        |
    | 13    | ankle_x_right position                     |
    | 14    | ankle_y_right position                     |
    | 15    | shoulder1_left position                    |
    | 16    | shoulder2_left position                    |
    | 17    | elbow_left position                        |
    | 18    | shoulder1_right position                   |
    | 19    | shoulder2_right position                   |
    | 20    | elbow_right position                       |

    - *Torso Control (Indices 0-2):* Controls the abdomen joints for torso orientation and movement.
    - *Left Leg Control (Indices 3-8):* Controls the left leg joints including hip, knee, and ankle for walking and balance.
    - *Right Leg Control (Indices 9-14):* Controls the right leg joints including hip, knee, and ankle for walking and balance.
    - *Left Arm Control (Indices 15-17):* Controls the left arm joints including shoulder and elbow for manipulation tasks.
    - *Right Arm Control (Indices 18-20):* Controls the right arm joints including shoulder and elbow for manipulation tasks.
    """

    name: str = "humanoid"

    frame_skip: int = 5

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 100,
    }

    left_arm = ArmPart(
        joint_names=[
            "shoulder1_left",
            "shoulder2_left",
            "elbow_left",
        ],
        _init_qpos=[-0.68, 0.498, -1.58],
        controller_config={
            "type": "JOINT_POSITION",
            "kp": 200,
            "interpolation": None,
        },
    )

    right_arm = ArmPart(
        joint_names=[
            "shoulder1_right",
            "shoulder2_right",
            "elbow_right",
        ],
        # _init_qpos=[0.68, -0.498, -1.58],
        controller_config={
            "type": "JOINT_POSITION",
            "kp": 200,
            "interpolation": None,
        },
    )

    left_leg = Part(
        joint_names=[
            "hip_x_left",
            "hip_z_left",
            "hip_y_left",
            "knee_left",
            "ankle_x_left",
            "ankle_y_left",
        ],
        # _init_qpos=[-0.0125, 0.000454, 0.0098, -0.04, 0.0521, -0.0312],
        controller_config={
            "type": "JOINT_POSITION",
            "kp": 200,
            "interpolation": None,
        },
    )

    right_leg = Part(
        joint_names=[
            "hip_x_right",
            "hip_z_right",
            "hip_y_right",
            "knee_right",
            "ankle_x_right",
            "ankle_y_right",
        ],
        # _init_qpos=[-0.0125, 0.000454, 0.0098, -0.04, 0.0521, 0.0312],
        controller_config={
            "type": "JOINT_POSITION",
            "kp": 200,
            "interpolation": None,
        },
    )

    torso = Part(
        joint_names=[
            "abdomen_y",
            "abdomen_z",
            "abdomen_x",
        ],
        # _init_qpos=[0.0, -0.00874, 0.0],
        controller_config={
            "type": "JOINT_POSITION",
            "kp": 200,
            "interpolation": None,
        },
    )

    standing_height: list = [0.6, 2.0]

    feet_sites = [
        "left_foot",
        "right_foot",
    ]
    _left_feet_geoms = ["foot1_left", "foot2_left"]
    _right_feet_geoms = ["foot1_right", "foot2_right"]
    _root_site = "root"