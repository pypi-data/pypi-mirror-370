from .franka import Franka
from .humanoid import Humanoid
from .xarm7 import XArm7
from .cobot import Cobot
from .t1 import LowerT1, T1

__all__ = ["Franka", "Humanoid", "XArm7", "Cobot", "LowerT1", "T1"]

ROBOT_CLASS_REGISTORY = {
    "franka": Franka,
    "humanoid": Humanoid,
    "xarm7": XArm7,
    "cobot": Cobot,
    "lower_t1": LowerT1,
    "t1": T1
}
