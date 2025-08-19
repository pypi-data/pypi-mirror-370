import mujoco
import numpy as np
from sai_mujoco.utils.rotations import mat2euler
from sai_mujoco.envs.base import BaseEnv


def goal_distance(goal_a, goal_b):
    """Calculate the Euclidean distance between two goals.

    Args:
        goal_a (np.ndarray): First goal position
        goal_b (np.ndarray): Second goal position

    Returns:
        float: Euclidean distance between the two goals
    """
    assert goal_a.shape == goal_b.shape
    return np.linalg.norm(goal_a - goal_b, axis=-1)


class PickAndPlaceEnv(BaseEnv):
    r"""

        ## Description
        A Pick and place environment with playing adesigned for object lifting. The task is to control the robot arm to reach, grasp, and lift a single cube from
        the table surface, and then place it accurately at a designated target position.

        ## Observation Space
        The observation space consists of the following parts (in order):

        - *qpos:* Position values of the robot's body parts. The dimensionality depends on the robot's joint configuration.
        - *qvel:* The velocities of these individual body parts (their derivatives). The dimensionality depends on the robot's joint configuration.
        - *gripper_pos (3 elements):* The end effector's position in the world frame.
        - *object_pos (3 elements):* The object's position in the world frame.
        - *pos_rel_gripper_object (3 elements):* The object's position in the end effector frame.
        - *vel_rel_gripper_object (3 elements):* The object's velocity in the end effector frame.
        - *object_rot (3 elements):* The object's rotation (euler angles) in the world frame.
        - *object_velp (3 elements):* The object's linear velocity in the world frame.
        - *object_velr (3 elements):* The object's rotational velocity in the world frame.
        - *target_pos (3 elements):* The target position in the world frame.
        - *target_rot (3 elements):* The target rotation in the world frame.

        The order of elements in the observation space related to the environment is as follows -

        | Num | Observation                        | Min  | Max | Type (Unit)              |
        | --- | -----------------------------------| ---- | --- | ------------------------ |
        | 0   | x-coordinate of gripper position   | -Inf | Inf | position (m)             |
        | 1   | y-coordinate of gripper position   | -Inf | Inf | position (m)             |
        | 2   | z-coordinate of gripper position   | -Inf | Inf | position (m)             |
        | 3   | x-coordinate of object position    | -Inf | Inf | position (m)             |
        | 4   | y-coordinate of object position    | -Inf | Inf | position (m)             |
        | 5   | z-coordinate of object position    | -Inf | Inf | position (m)             |
        | 6   | x rel pos of object in gripper     | -Inf | Inf | position (m)             |
        | 7   | y rel pos of object in gripper     | -Inf | Inf | position (m)             |
        | 8   | z rel pos of object in gripper     | -Inf | Inf | position (m)             |
        | 9   | x rel vel of object in gripper     | -Inf | Inf | linear velocity (m/s)    |
        | 10  | y rel vel of object in gripper     | -Inf | Inf | linear velocity (m/s)    |
        | 11  | z rel vel of object in gripper     | -Inf | Inf | linear velocity (m/s)    |
        | 12  | roll of object                     | -Inf | Inf | rotation (rad)           |
        | 13  | pitch of object                    | -Inf | Inf | rotation (rad)           |
        | 14  | yaw of object                      | -Inf | Inf | rotation (rad)           |
        | 15  | x velocity of object               | -Inf | Inf | linear velocity (m/s)    |
        | 16  | y velocity of object               | -Inf | Inf | linear velocity (m/s)    |
        | 17  | z velocity of object               | -Inf | Inf | linear velocity (m/s)    |
        | 18  | x angular velocity of object       | -Inf | Inf | angular velocity (rad/s) |
        | 20  | y angular velocity of object       | -Inf | Inf | angular velocity (rad/s) |
        | 21  | z angular velocity of object       | -Inf | Inf | angular velocity (rad/s) |
        | 22  | x-coordinate of target             | -Inf | Inf | position (m)             |
        | 23  | y-coordinate of target             | -Inf | Inf | position (m)             |
        | 24  | z-coordinate of target             | -Inf | Inf | position (m)             |
        | 25  | roll of target                     | -Inf | Inf | rotation (rad)           |
        | 26  | pitch of target                    | -Inf | Inf | rotation (rad)           |
        | 27  | yaw of target                      | -Inf | Inf | rotation (rad)           |

        ## Rewards

        The environment supports two reward types that can be specified during initialization:

        ### Dense Reward (default)
        The dense reward components include:

            1. `grasp_reward`: Encourages the gripper to move closer to the object by assigning higher reward as the distance between the gripper and object decreases (exponentially scaled).
            2. `place_reward`: Encourages the agent to place the object near the target location by increasing the reward as the object approaches the target (exponentially scaled).
            3. `success_bonus`: Provides a fixed bonus when the object is successfully placed at the target location.

        ### Sparse Reward
        When `reward_type="sparse"` is specified during initialization, the reward becomes:
            - `1.0` if the object is successfully placed at the target location
            - `0.0` otherwise

        `info` contains the success parameter if the given episode succeeded.

        ## Episode End
        ### Termination

        The current episode should terminate based on termination criteria defined as follow:
            1. If the distance between object and target is less than threshold (0.05)

        ### Truncation
        The default duration of an episode is 500 timesteps.

        ## Arguments
        The environment accepts the following parameters during initialization:

        - `reward_type` (str, optional): Specifies the reward type. Options are:
            - `"dense"` (default): Provides continuous reward based on distances
            - `"sparse"`: Provides binary reward (1.0 for success, 0.0 otherwise)

        Env provides the parameter to modify the start state of the robot upon reset.
        It can be applied during `gymnasium.make` by changing deterministic_reset (bool).
    ."""

    env_name: str = "pick_place"
    scene_name: str = "base_scene"

    default_camera_config = {
        "trackbodyid": -1,
        "lookat": [0.5, 0.5, 0.5],
        "distance": 3.5,
        "elevation": -30,
        "azimuth": 135,
    }

    reward_config = {
        "grasp_reward": 2.0,
        "place_reward": 5.0,
        "success_bonus": 10.0,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reward_type = kwargs.get("reward_type", "dense")

        if self.reward_type == "sparse":
            self.reward_config = {"success_bonus": 1.0}

    def _setup_references(self):
        self.ee_site_name = self.robot_model._arms["left_arm"].gripper.site_name
        self.ee_site_id = self.robot_model.sim.model.site_name2id(self.ee_site_name)

    def _reset_env(self):
        """
        Reset the environment to an initial state.
        """
        self._sample_object()
        self.goal_pos = self._sample_goal()

    def _render_callback(self):
        """Update the visualization of the target site."""
        sites_offset = (
            self.robot_model.sim.data.site_xpos - self.robot_model.model.site_pos
        ).copy()
        site_id = mujoco.mj_name2id(
            self.robot_model.model, mujoco.mjtObj.mjOBJ_SITE, "target0"
        )
        self.robot_model.model.site_pos[site_id] = self.goal_pos - sites_offset[site_id]
        mujoco.mj_forward(self.robot_model.model, self.robot_model.sim.data)

    def _get_env_obs(self):
        """
        Collects and returns the current environment observation.

        This function gathers the relevant physical states of the main entities
        in the pick and place simulation environment—namely, the end effector, object,
        and the target—and concatenates their positions and orientation into a single
        observation vector.

        Specifically, it retrieves:
            - The 3D position of the gripper (`gripper_pos`)
            - The 3D relative position between gripper and object (`pos_rel_gripper_object`)
            - The 3D relative linear velocity between gripper and object (`vel_rel_gripper_object`)
            - The orientation of the object in Euler angles (`object_rot`)
            - The 3D linear velocity of the object (`object_velp`)
            - The 3D angular velocity of the object (`object_velr`)
            - The 3D position of the target (`target_pos`)
            - The orientation of the target in Euler angles (`target_rot`)

        The final observation is a 27-dimensional float32 NumPy array:
            [gripper_x, gripper_y, gripper_z,
            gripper_obj_dx, gripper_obj_dy, gripper_obj_dz,
            gripper_obj_vx, gripper_obj_vy, gripper_obj_vz,
            object_euler_x, object_euler_y, object_euler_z,
            object_vx, object_vy, object_vz,
            object_wx, object_wy, object_wz,
            target_x, target_y, target_z,
            target_euler_x, target_euler_y, target_euler_z]

        Returns
        -------
        obs : np.ndarray of shape (27,), dtype np.float32
            The concatenated observation vector representing the positions and
            orientation of key environment elements.
        """
        gripper_pos = self.robot_model.sim.data.get_site_xpos(self.ee_site_name)
        gripper_velp = self.robot_model.sim.data.get_site_xvelp(self.ee_site_name)

        object_pos = self.robot_model.sim.data.get_site_xpos("object0")
        object_rot = mat2euler(self.robot_model.sim.data.get_site_xmat("object0"))

        object_velp = self.robot_model.sim.data.get_site_xvelp("object0")
        object_velr = self.robot_model.sim.data.get_site_xvelr("object0")

        target_pos = self.robot_model.sim.data.get_site_xpos("target0")
        target_rot = mat2euler(self.robot_model.sim.data.get_site_xmat("target0"))

        pos_rel_object_target = object_pos - target_pos

        pos_rel_gripper_object = gripper_pos - object_pos

        vel_rel_gripper_object = object_velp - gripper_velp

        return np.concatenate(
            [
                gripper_pos,
                object_pos,
                pos_rel_gripper_object,
                vel_rel_gripper_object,
                object_rot,
                object_velp,
                object_velr,
                target_pos,
                target_rot,
            ],
            dtype=np.float32,
        )

    def _get_info(self):
        """Get additional information about the environment state.

        Returns:
            dict: Additional information dictionary
        """
        return {
            "success": self._is_success(
                self.robot_model.sim.data.get_site_xpos("object0"), self.goal_pos
            )
        }

    def compute_terminated(self):
        """
        Determines whether the current episode should terminate based on task conditions.

        This function checks for the termination criteria in the pick and place environment:
            1. If the distance between object and target is less than threshold (0.05) 

        Returns
        -------
        terminated : bool
            `True` if any of the termination conditions are met; otherwise `False`.
        """
        object_pos = self.robot_model.sim.data.get_site_xpos("object0")
        target_pos = self.robot_model.sim.data.get_site_xpos("target0")
        return self._is_success(object_pos, target_pos)

    def compute_reward(self):
        """
        Computes and returns individual reward components for the current simulation state.

        The reward components include:

        1. `grasp_reward`: Encourages the gripper to move closer to the object by assigning higher reward as the distance between the gripper and object decreases (exponentially scaled).
        2. `place_reward`: Encourages the agent to place the object near the target location by increasing the reward as the object approaches the target (exponentially scaled).
        3. `success_bonus`: Provides a fixed bonus when the object is successfully placed at the target location.

        Returns
        -------
        raw_reward : dict
            A dictionary mapping each reward term name (str) to its corresponding scalar value (float).
            These are raw values and not yet combined into a scalar total reward.
        """
        if self.reward_type == "sparse":
            return self._compute_sparse_reward()
        else:
            return self._compute_dense_reward()

    def _compute_sparse_reward(self):
        """Compute sparse reward for the current simulation state."""
        return {
            "success_bonus": 1.0
            if self._is_success(
                self.robot_model.sim.data.get_site_xpos("object0"), self.goal_pos
            )
            else 0.0,
        }

    def _compute_dense_reward(self):
        """Compute dense reward for the current simulation state."""
        gripper_pos = self.robot_model.sim.data.get_site_xpos(self.ee_site_name)
        object_pos = self.robot_model.sim.data.get_site_xpos("object0")
        target_pos = self.robot_model.sim.data.get_site_xpos("target0")

        gripper_object_dist = goal_distance(gripper_pos, object_pos)
        object_target_dist = goal_distance(object_pos, target_pos)

        is_success = 1.0 if self._is_success(object_pos, target_pos) else 0.0

        # Reward for getting closer to the object (grasping phase)
        # Convert distance to a positive reward that increases as distance decreases
        grasp_reward = np.exp(-5.0 * gripper_object_dist)

        # Reward for getting closer to the target (placing phase)
        # Convert distance to a positive reward that increases as distance decreases
        place_reward = np.exp(-5.0 * object_target_dist)

        # Success bonus when object is at target
        success_bonus = 1.0 if is_success else 0.0

        raw_reward = {
            "grasp_reward": grasp_reward,
            "place_reward": place_reward,
            "success_bonus": success_bonus,
        }

        return raw_reward

    def _sample_goal(self):
        """Sample a new goal position and orientation.

        Returns:
            np.array: (goal_pos) where goal_pos is the position
        """
        object_xpos = self.robot_model.sim.data.get_site_xpos("object0")
        goal_pos = np.array([0.75, 0, 0.68])
        goal_pos[2] = object_xpos[2] + self.np_random.uniform(0, 0.3)
        while np.linalg.norm(goal_pos[:2] - object_xpos[:2]) < 0.2:
            goal_pos[0] += self.np_random.uniform(-0.05, 0.25)
            goal_pos[1] += self.np_random.uniform(-0.25, 0.25)
        return goal_pos.copy()

    def _render_callback(self):
        """Update the visualization of the target site."""
        sites_offset = (
            self.robot_model.sim.data.site_xpos - self.robot_model.model.site_pos
        ).copy()
        site_id = mujoco.mj_name2id(
            self.robot_model.model, mujoco.mjtObj.mjOBJ_SITE, "target0"
        )
        self.robot_model.model.site_pos[site_id] = self.goal_pos - sites_offset[site_id]
        self.robot_model.sim.forward()

    def _is_success(self, achieved_goal, desired_goal, distance_threshold=0.05):
        """Check if the achieved goal is close enough to the desired goal.

        Args:
            achieved_goal (np.ndarray): The achieved goal position
            desired_goal (np.ndarray): The desired goal position

        Returns:
            float: 1.0 if successful, 0.0 otherwise
        """
        d = goal_distance(achieved_goal, desired_goal)
        return bool(d < distance_threshold)

    def _sample_object(self):
        """Sample a new initial position for the object.

        Returns:
            bool: True if successful
        """
        object_xpos = self.robot_model.sim.data.get_site_xpos("object0")
        object_x = object_xpos[0] + self.np_random.uniform(-0.1, 0.35)
        object_y = object_xpos[1] + self.np_random.uniform(-0.2, 0.2)
        object_xpos[:2] = np.array([object_x, object_y])
        object_qpos = self.robot_model.sim.data.get_joint_qpos("object0:joint")
        assert object_qpos.shape == (7,)
        object_qpos[:2] = object_xpos[:2]
        self.robot_model.sim.data.set_joint_qpos("object0:joint", object_qpos)
        self.robot_model.sim.forward()
        return True
