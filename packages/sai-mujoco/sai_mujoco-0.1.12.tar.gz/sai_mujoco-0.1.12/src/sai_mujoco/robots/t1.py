from sai_mujoco.robots.base import BaseRobot
from sai_mujoco.robots.models import Part, ArmPart


class T1(BaseRobot):
    name: str = "t1"

    standing_height: list = [0.3, 0.7]

    frame_skip: int = 1

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 500,
    }

    head = Part(
        joint_names=["AAHead_yaw", "Head_pitch"],
        _actuator_names=["AAHead_yaw", "Head_pitch"],
        controller_config={
            "type": "JOINT_POSITION",
            "input_max": 1,
            "input_min": -1,
            "output_max": 0.5,
            "output_min": -0.5,
            "kd": 5,
            "kv": 5,
            "kp": 75,
            "velocity_limits": [-1, 1],
            "kp_limits": [0, 1000],
            "interpolation": None,
            "ramp_ratio": 0.2,
            "damping_ratio": 0.7,
        },
    )

    left_arm = ArmPart(
        joint_names=[
            "Left_Shoulder_Pitch",
            "Left_Shoulder_Roll",
            "Left_Elbow_Pitch",
            "Left_Elbow_Yaw",
        ],
        _actuator_names=[
            "Left_Shoulder_Pitch",
            "Left_Shoulder_Roll",
            "Left_Elbow_Pitch",
            "Left_Elbow_Yaw",
        ],
        controller_config={
            "type": "JOINT_POSITION",
            "input_max": 1,
            "input_min": -1,
            "output_max": 0.5,
            "output_min": -0.5,
            "kd": 5,
            "kv": 5,
            "kp": 75,
            "velocity_limits": [-1, 1],
            "kp_limits": [0, 1000],
            "interpolation": None,
            "ramp_ratio": 0.2,
            "damping_ratio": 0.7,
        },
    )

    right_arm = ArmPart(
        joint_names=[
            "Right_Shoulder_Pitch",
            "Right_Shoulder_Roll",
            "Right_Elbow_Pitch",
            "Right_Elbow_Yaw",
        ],
        _actuator_names=[
            "Right_Shoulder_Pitch",
            "Right_Shoulder_Roll",
            "Right_Elbow_Pitch",
            "Right_Elbow_Yaw",
        ],
        controller_config={
            "type": "JOINT_POSITION",
            "input_max": 1,
            "input_min": -1,
            "output_max": 0.5,
            "output_min": -0.5,
            "kd": 5,
            "kv": 5,
            "kp": 75,
            "velocity_limits": [-1, 1],
            "kp_limits": [0, 1000],
            "interpolation": None,
            "ramp_ratio": 0.2,
            "damping_ratio": 0.7,
        },
    )

    left_leg = Part(
        joint_names=[
            "Left_Hip_Pitch",
            "Left_Hip_Roll",
            "Left_Hip_Yaw",
            "Left_Knee_Pitch",
            "Left_Ankle_Pitch",
            "Left_Ankle_Roll",
        ],
        _actuator_names=[
            "Left_Hip_Pitch",
            "Left_Hip_Roll",
            "Left_Hip_Yaw",
            "Left_Knee_Pitch",
            "Left_Ankle_Pitch",
            "Left_Ankle_Roll",
        ],
        controller_config={
            "type": "JOINT_POSITION",
            "input_max": 1,
            "input_min": -1,
            "output_max": 0.5,
            "output_min": -0.5,
            "kd": 5,
            "kv": 5,
            "kp": 75,
            "velocity_limits": [-1, 1],
            "kp_limits": [0, 1000],
            "interpolation": None,
            "ramp_ratio": 0.2,
            "damping_ratio": 0.7,
        },
    )

    right_leg = Part(
        joint_names=[
            "Right_Hip_Pitch",
            "Right_Hip_Roll",
            "Right_Hip_Yaw",
            "Right_Knee_Pitch",
            "Right_Ankle_Pitch",
            "Right_Ankle_Roll",
        ],
        _actuator_names=[
            "Right_Hip_Pitch",
            "Right_Hip_Roll",
            "Right_Hip_Yaw",
            "Right_Knee_Pitch",
            "Right_Ankle_Pitch",
            "Right_Ankle_Roll",
        ],
        controller_config={
            "type": "JOINT_POSITION",
            "input_max": 1,
            "input_min": -1,
            "output_max": 0.5,
            "output_min": -0.5,
            "kd": 5,
            "kv": 5,
            "kp": 75,
            "velocity_limits": [-1, 1],
            "kp_limits": [0, 1000],
            "interpolation": None,
            "ramp_ratio": 0.2,
            "damping_ratio": 0.7,
        },
    )
    torso = Part(
        joint_names=[
            "Waist",
        ],
        _actuator_names=["Waist"],
        controller_config={
            "type": "JOINT_POSITION",
            "input_max": 1,
            "input_min": -1,
            "output_max": 0.5,
            "output_min": -0.5,
            "kd": 5,
            "kv": 5,
            "kp": 75,
            "velocity_limits": [-1, 1],
            "kp_limits": [0, 1000],
            "interpolation": None,
            "ramp_ratio": 0.2,
            "damping_ratio": 0.7,
        },
    )

class LowerT1(BaseRobot):
    name: str = "t1"
    xml_path: str = "robot_lower.xml"
    standing_height: list = [0.3, 0.7]

    frame_skip: int = 1

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 500,
    }

    torso = Part(joint_names=[])

    left_leg = Part(
        joint_names=[
            "Left_Hip_Pitch",
            "Left_Hip_Roll",
            "Left_Hip_Yaw",
            "Left_Knee_Pitch",
            "Left_Ankle_Pitch",
            "Left_Ankle_Roll",
        ],
        _actuator_names=[
            "Left_Hip_Pitch",
            "Left_Hip_Roll",
            "Left_Hip_Yaw",
            "Left_Knee_Pitch",
            "Left_Ankle_Pitch",
            "Left_Ankle_Roll",
        ],
        controller_config={
            "type": "JOINT_TORQUE",
            "input_max": [45.0, 45.0, 30.0, 65.0, 24.0, 15.0],
            "input_min": [-45.0, -45.0, -30.0, -65.0, -24.0, -15.0],
            "output_max": [45.0, 45.0, 30.0, 65.0, 24.0, 15.0],
            "output_min": [-45.0, -45.0, -30.0, -65.0, -24.0, -15.0],
            "kd": 5,
            "kv": 5,
            "kp": 75,
            "use_torque_compensation": False,
            "velocity_limits": [-1, 1],
            "kp_limits": [0, 1000],
            "interpolation": None,
            "ramp_ratio": 0.2,
            "damping_ratio": 0.7,
        },
    )

    right_leg = Part(
        joint_names=[
            "Right_Hip_Pitch",
            "Right_Hip_Roll",
            "Right_Hip_Yaw",
            "Right_Knee_Pitch",
            "Right_Ankle_Pitch",
            "Right_Ankle_Roll",
        ],
        _actuator_names=[
            "Right_Hip_Pitch",
            "Right_Hip_Roll",
            "Right_Hip_Yaw",
            "Right_Knee_Pitch",
            "Right_Ankle_Pitch",
            "Right_Ankle_Roll",
        ],
        controller_config={
            "type": "JOINT_TORQUE",
            "input_max": [45.0, 45.0, 30.0, 65.0, 24.0, 15.0],
            "input_min": [-45.0, -45.0, -30.0, -65.0, -24.0, -15.0],
            "output_max": [45.0, 45.0, 30.0, 65.0, 24.0, 15.0],
            "output_min": [-45.0, -45.0, -30.0, -65.0, -24.0, -15.0],
            "kd": 5,
            "kv": 5,
            "kp": 75,
            "use_torque_compensation": False,
            "velocity_limits": [-1, 1],
            "kp_limits": [0, 1000],
            "interpolation": None,
            "ramp_ratio": 0.2,
            "damping_ratio": 0.7,
        },
    )
