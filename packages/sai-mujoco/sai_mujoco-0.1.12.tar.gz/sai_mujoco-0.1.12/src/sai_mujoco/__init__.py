from os import path
from gymnasium import register
import yaml

__version__ = "0.1.12"

dir_path = path.dirname(path.realpath(__file__))
with open(f"{dir_path}/config/registry.yaml", "r") as f:
    env_config = yaml.safe_load(f)


register(
    id="InvertedPendulumWheel-v0",
    entry_point="sai_mujoco.envs:InvertedPendulumWheelEnv",
    kwargs={},
)

for env in env_config["environments"]:
    env_name = env["name"]
    entry_point = env["entry_point"]
    robots = env["robots"]

    # Normalize to list of dicts
    if isinstance(robots, dict):  # single robot dict
        robots = [robots]

    for robot_entry in robots:
        for robot_name, robot_config in robot_entry.items():
            robot_env = "".join(robot_name.title().split("_"))
            max_episode_steps = env.get("max_episode_steps", 1000)
            env_id = f"{robot_env}{env_name}-v0"
            env_config = {}
            env_config["robot_pos"] = robot_config.pop("position")
            env_config["robot_quat"] = robot_config.pop("orientation")
            robot_config["name"] = robot_name
            robot_config["reset_noise"] = "default"
            kwargs = {
                "env_config": env_config,
                "robot_config": robot_config,
                "deterministic_reset": False,
            }

            register(
                id=env_id,
                entry_point=entry_point,
                kwargs=kwargs,
                max_episode_steps=max_episode_steps,
            )
