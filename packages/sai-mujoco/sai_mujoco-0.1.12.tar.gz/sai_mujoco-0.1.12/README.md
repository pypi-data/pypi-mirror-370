# ArenaX Lab's Mujoco Environments

This package contains the Mujoco environments used for the SAI Platform.

## Installation

```bash
pip install sai-mujoco
```

## Usage

```python
import gymnasium as gym
import sai_mujoco

env = gym.make("HumanoidObstacle-v0")
```

# Environment List

- `HumanoidObstacle-v0`: A humanoid obstacle environment.
- `InvertedPendulumWheel-v0`: An inverted pendulum on a wheel environment.
- `RoboticArm-v0`: A robotic arm environment.

# More Information

- [SAI Platform](https://competesai.com)
- [SAI Documentation](https://docs.competesai.com)
