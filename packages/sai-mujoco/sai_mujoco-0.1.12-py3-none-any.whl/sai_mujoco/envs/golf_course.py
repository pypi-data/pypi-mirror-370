import mujoco
import numpy as np
from sai_mujoco.envs.base import BaseEnv
import sai_mujoco.utils.rotations as R


class GolfCourseEnv(BaseEnv):
    r"""

    ## Description
    A Golf Course environment with playing a simplified golf game by grasping a golf club, striking a golf ball, and maneuvering it toward a designated hole.
    The robot must precisely control its end-effector to approach the club, align and close its gripper to secure it, lift the club, and swing to hit the
    ball, ultimately guiding the ball closer to the hole. The primary challenges are: precise manipulation for grasping, dynamic control for hitting the ball,
    and spatial reasoning to approach the hole, all within a continuous and high-dimensional action and observation space.

    ## Observation Space
    The observation space consists of the following parts (in order):

    - *qpos:* Position values of the robot's body parts. The dimensionality depends on the robot's joint configuration.
    - *qvel:* The velocities of these individual body parts (their derivatives). The dimensionality depends on the robot's joint configuration.
    - *ball_xpos (3 elements):* The golf ball's position in the world frame.
    - *golf_club_xpos (3 elements):* The golf club's position in the world frame.
    - *golf_club_quat (4 elements):* The quaternion orientation of the golf club in the world frame.
    - *hole_xpos (3 elements):* The golf hole's position in the world frame.

    The order of elements in the observation space related to the environment is as follows -

    | Num | Observation                        | Min  | Max | Type (Unit)              |
    | --- | -----------------------------------| ---- | --- | ------------------------ |
    | 0   | x-coordinate of the golf ball      | -Inf | Inf | position (m)             |
    | 1   | y-coordinate of the golf ball      | -Inf | Inf | position (m)             |
    | 2   | z-coordinate of the golf ball      | -Inf | Inf | position (m)             |
    | 3   | x-coordinate of the golf club      | -Inf | Inf | position (m)             |
    | 4   | y-coordinate of the golf club      | -Inf | Inf | position (m)             |
    | 5   | z-coordinate of the golf club      | -Inf | Inf | position (m)             |
    | 6   | w quaternion of the golf club      | -Inf | Inf | orientation (q)          |
    | 7   | x quaternion of the golf club      | -Inf | Inf | orientation (q)          |
    | 8   | y quaternion of the golf club      | -Inf | Inf | orientation (q)          |
    | 9   | z quaternion of the golf club      | -Inf | Inf | orientation (q)          |
    | 10  | x-coordinate of the hole           | -Inf | Inf | position (m)             |
    | 11  | y-coordinate of the hole           | -Inf | Inf | position (m)             |
    | 12  | z-coordinate of the hole           | -Inf | Inf | position (m)             |

    ## Rewards

    The reward components include:

        1. `ee_club_dist` (weight: 1.0): Encourages the end-effector to move closer to the club grip.
        2. `align_ee_handle` (weight: 2.0): Encourages alignment between the gripper orientation and the club handle.
        3. `fingers_club_grasp` (weight: 5.0): Rewards proper grasping of the club grip with the fingers.
        4. `ball_hole_dist` (weight: 10.0): Encourages minimizing the distance between the golf ball and the hole.
        5. `ball_in_hole` (weight: 20.0): Rewards when the ball enters the hole.
        6. `club_dropped` (weight: -2.0): Penalizes dropping the club prematurely.
        7. `ball_passed_hole` (weight: -4.0): Penalizes overshooting the ball past the hole.
        8. `joint_vel` (weight: -0.0001): Penalizes high joint velocities to encourage smooth motions.

    `info` contains the success parameter if the given episode succeeded.

    ## Episode End
    ### Termination

    The current episode should terminate based on three termination criteria defined as follow:
        1. If the golf ball has entered the hole
        2. If the ball has passed beyond the hole without entering
        3. If the golf club has been dropped

    ### Truncation
    The default duration of an episode is 650 timesteps.

    ## Arguments
    Env provides the parameter to modify the start state of the robot upon reset.
    It can be applied during `gymnasium.make` by changing deterministic_reset (bool).
    """

    env_name: str = "golf_course"
    scene_name: str = "base_scene"
    default_camera_config = {
        "distance": 2.8,
        "azimuth": -130,
        "elevation": -45.0,
        "lookat": np.array([0.2, 0.0, 0.35]),
    }

    reward_config = {
        "ee_club_dist": 1.0,
        "align_ee_handle": 2.0,
        "fingers_club_grasp": 5.0,
        "ball_hole_dist": 10.0,
        "ball_in_hole": 20.0,
        "club_dropped": -2.0,
        "ball_passed_hole": -4.0,
        "joint_vel": -0.0001,
    }

    def _get_env_obs(self):
        """
        Collects and returns the current environment observation.

        This function gathers the relevant physical states of the main entities
        in the golf simulation environment—namely, the golf ball, the golf club,
        and the hole—and concatenates their positions and orientation into a single
        observation vector.

        Specifically, it retrieves:
            - The 3D position of the golf ball (`ball_xpos`)
            - The 3D position of the golf club (`golf_club_xpos`)
            - The orientation of the golf club as a quaternion (`golf_club_quat`)
            - The 3D position of the hole (`hole_xpos`)

        The final observation is a 13-dimensional float32 NumPy array:
            [ball_x, ball_y, ball_z,
            club_x, club_y, club_z,
            club_qw, club_qx, club_qy, club_qz,
            hole_x, hole_y, hole_z]

        Returns
        -------
        obs : np.ndarray of shape (13,), dtype np.float32
            The concatenated observation vector representing the positions and
            orientation of key environment elements.
        """
        ball_xpos = self.robot_model.data.xpos[self.golf_ball_id]
        hole_xpos = self.robot_model.data.xpos[self.golf_hole_id]
        golf_club_xpos = self.robot_model.data.xpos[self.golf_club_id]
        golf_club_quat = self.robot_model.data.xquat[self.golf_club_id]

        obs = np.concatenate(
            [ball_xpos, golf_club_xpos, golf_club_quat, hole_xpos],
            dtype=np.float32,
        )

        return obs

    def compute_terminated(self):
        """
        Determines whether the current episode should terminate based on task conditions.

        This function checks for three termination criteria in the golf environment:
            1. If the golf ball has entered the hole (`_ball_in_hole`)
            2. If the ball has passed beyond the hole without entering (`_ball_passed_hole`)
            3. If the golf club has been dropped (`_club_dropped`)

        Returns
        -------
        terminated : bool
            `True` if any of the termination conditions are met; otherwise `False`.
        """
        ball_pos = self.robot_model.data.xpos[self.golf_ball_id]
        hole_pos = self.robot_model.data.xpos[self.golf_hole_id]
        club_grip_pos = self.robot_model.data.xpos[self.golf_club_id]

        is_ball_in_hole = self._ball_in_hole(ball_pos, hole_pos)
        is_ball_passed_hole = self._ball_passed_hole(ball_pos, hole_pos)
        is_club_dropped = self._club_dropped(club_grip_pos)
        return bool(is_ball_in_hole or is_ball_passed_hole or is_club_dropped)

    def _setup_references(self):
        """
        Initializes and stores environment-specific reference IDs for key entities in the simulation.

        This function sets up MuJoCo internal IDs (body and site IDs) for objects and components
        involved in the golf environment. These references are necessary for accessing
        position, orientation, and other dynamic properties during simulation.

        Specifically, it retrieves:
            - Body IDs for the golf ball, hole (flag assembly), golf club grip, and club head
            - Site ID for the left arm end-effector
            - Body names and IDs for the left and right gripper fingers of the left arm

        These references are stored as instance attributes and used throughout the environment
        for computing observations, rewards, and termination conditions.
        """

        # Set body IDs for various objects like golf ball, golf hole, and the golf club.
        self.golf_ball_id = self.robot_model.sim.model.body_name2id("golf_ball")
        self.golf_hole_id = self.robot_model.sim.model.body_name2id("flag_assembly")
        self.golf_club_id = self.robot_model.sim.model.body_name2id("grip_link")
        self.club_head_id = self.robot_model.sim.model.body_name2id("head_link")

        self.ee_site_name = self.robot_model._arms["left_arm"].gripper.site_name
        self.ee_site_id = self.robot_model.sim.model.site_name2id(self.ee_site_name)

        self.left_finger_body_name = self.robot_model._arms[
            "left_arm"
        ].gripper.important_bodies["left_finger"]
        self.left_finger_body_id = self.robot_model.sim.model.body_name2id(
            self.left_finger_body_name
        )

        self.right_finger_body_name = self.robot_model._arms[
            "left_arm"
        ].gripper.important_bodies["right_finger"]
        self.right_finger_body_id = self.robot_model.sim.model.body_name2id(
            self.right_finger_body_name
        )

    def compute_reward(self):
        """
        Computes and returns individual reward components for the current simulation state.

        The reward components include:

        1. `ee_club_dist`: Encourages the end-effector to move closer to the club grip.
        2. `align_ee_handle`: Encourages alignment between the gripper orientation and the club handle.
        3. `fingers_club_grasp`: Rewards proper grasping of the club grip with the fingers.
        4. `ball_hole_dist`: Encourages minimizing the distance between the golf ball and the hole.
        5. `joint_vel`: Penalizes high joint velocities to encourage smooth motions.
        6. `club_dropped`: Penalizes dropping the club prematurely.
        7. `ball_passed_hole`: Penalizes overshooting the ball past the hole.

        Returns
        -------
        raw_reward : dict
            A dictionary mapping each reward term name (str) to its corresponding scalar value (float).
            These are raw values and not yet combined into a scalar total reward.
        """
        # Get positions and orientations
        ee_pos = self.robot_model.data.site(self.ee_site_id).xpos
        ee_xmat = self.robot_model.data.site(self.ee_site_id).xmat.reshape(3, 3)

        # Get club grip position and orientation
        club_grip_pos = self.robot_model.data.xpos[self.golf_club_id]
        club_grip_xmat = self.robot_model.data.xmat[self.golf_club_id].reshape(3, 3)

        # Get ball and hole positions
        ball_pos = self.robot_model.data.xpos[self.golf_ball_id]
        hole_pos = self.robot_model.data.xpos[self.golf_hole_id]

        # 1. Approach the club grip
        approach_ee_club_grip = self._ee_club_dist(ee_pos, club_grip_pos)

        align_ee_handle = self._align_gripper(ee_xmat, club_grip_xmat)

        # 2. Grasp the handle
        approach_gripper_handle = self._approach_fingers_handle(
            ee_pos, club_grip_pos, offset=0.04
        )

        # 4. Approach ball to the hole
        approach_ball_hole = self._ball_hole_dist(ball_pos, hole_pos)

        # 5. Penalize joint velocities
        joint_vel = self._joint_vel_l2()

        # 6. Penalize if the club is dropped
        club_dropped = self._club_dropped(club_grip_pos)

        # 7. Penalize if the ball passed the hole
        ball_passed_hole = self._ball_passed_hole(ball_pos, hole_pos)

        raw_reward = {
            "ee_club_dist": approach_ee_club_grip,
            "align_ee_handle": align_ee_handle,
            "fingers_club_grasp": approach_gripper_handle,
            "ball_hole_dist": approach_ball_hole,
            "joint_vel": joint_vel,
            "club_dropped": club_dropped,
            "ball_passed_hole": ball_passed_hole,
        }
        return raw_reward

    def _ee_club_dist(self, ee_pos, club_grip_pos):
        """
        Computes a reward based on the distance between the end-effector and the club grip.

        This function calculates how close the end-effector is to the target position
        above the club grip. A vertical offset of 0.12 meters is added to the club grip
        position to encourage approaching from above, which is typically better for grasping.

        The reward is computed using an exponential decay based on the Euclidean distance:
            reward = exp(-20 * distance)

        Parameters
        ----------
        ee_pos : np.ndarray of shape (3,)
            The 3D position of the robot end-effector.
        club_grip_pos : np.ndarray of shape (3,)
            The 3D position of the golf club grip.

        Returns
        -------
        rew : float
            A reward scalar with higher values indicating closer proximity
            to the target approach point above the club grip.
        """
        target_pos = club_grip_pos.copy()
        target_pos[2] += 0.12  # Add offset for z axis
        dist = np.linalg.norm(ee_pos - target_pos)
        rew = np.exp(-20 * dist)
        return rew

    def _align_gripper(self, eef_mat, handle_mat):
        """
        Calculate alignment reward for end effector and handle based on rotation matrices.

        This function computes a reward that measures how well the end effector is aligned
        with the handle according to specific orientation constraints:
        - EEF z-axis should align with negative handle y-axis
        - EEF x-axis should align with handle x-axis
        - EEF y-axis should align with handle z-axis

        Parameters
        ----------
        eef_mat : np.ndarray of shape (3, 3)
            Rotation matrix of the end-effector (column-wise axes: x, y, z).
        handle_mat : np.ndarray of shape (3, 3)
            Rotation matrix of the club handle.

        Returns
        -------
        reward : float
            Scalar reward indicating how well the gripper is aligned with the handle.
        """
        eef_x, eef_y, eef_z = eef_mat[:, 0], eef_mat[:, 1], eef_mat[:, 2]
        handle_x, handle_y, handle_z = (
            handle_mat[:, 0],
            handle_mat[:, 1],
            handle_mat[:, 2],
        )

        # Define alignment constraints
        # 1. EEF z-axis should align with -handle y-axis
        z_alignment = np.dot(eef_z, -handle_y)

        # 2. EEF x-axis should align with handle x-axis
        x_alignment = np.dot(eef_x, handle_x)

        # 3. EEF y-axis should align with handle z-axis
        y_alignment = np.dot(eef_y, handle_z)

        # Combine alignments (each dot product ranges from -1 to 1)
        # Perfect alignment gives dot product = 1
        total_alignment = (z_alignment + x_alignment + y_alignment) / 3.0

        # Convert to reward (0 to 1 scale)
        reward = (total_alignment + 1) / 2.0

        return reward

    def _approach_fingers_handle(self, ee_pos, handle_pos, offset=0.04):
        """
        Computes a reward based on the gripper's fingers approaching the club handle with the correct pose.

        This function evaluates the proximity of the gripper's fingers to the club grip when they are in
        a graspable orientation. 

        If the fingers are not in a graspable pose, the reward is 0. Otherwise, the reward is inversely
        proportional to the distance of each finger from the handle, encouraging the fingers to approach
        the handle closely.

        Parameters
        ----------
        ee_pos : np.ndarray of shape (3,)
            The 3D position of the robot's end-effector.
        handle_pos : np.ndarray of shape (3,)
            The 3D position of the club handle.
        offset : float, optional, default=0.04
            A small offset for tuning the reward computation.

        Returns
        -------
        reward : float
            A scalar reward indicating how well the gripper's fingers are positioned
            to grasp the handle. The reward is higher when the fingers are closer to the handle in
            a correct orientation.
        """
        left_finger_pos = self.robot_model.data.xpos[self.left_finger_body_id]
        right_finger_pos = self.robot_model.data.xpos[self.right_finger_body_id]

        # Check if hand is in a graspable pose
        is_graspable = (right_finger_pos[1] < handle_pos[1]) & (
            left_finger_pos[1] > handle_pos[1]
        )

        is_graspable = (
            is_graspable
            & (ee_pos[2] < handle_pos[2] + 0.16)
            & (ee_pos[0] - handle_pos[0] < 0.02)
        )

        if not is_graspable:
            return 0.0

        # Compute the distance of each finger from the handle
        lfinger_dist = np.abs(left_finger_pos[1] - handle_pos[1])
        rfinger_dist = np.abs(handle_pos[1] - right_finger_pos[1])

        # Reward is proportional to how close the fingers are to the handle when in a graspable pose
        reward = is_graspable * (1 / (lfinger_dist + rfinger_dist)) / 10.0
        return reward

    def _ball_hole_dist(self, ball_pos, hole_pos):
        """
        Computes a reward based on the distance between the ball and the hole.

        This function calculates the Euclidean distance between the golf ball and the hole,
        then returns a reward based on an exponential decay of this distance. The reward
        is highest when the ball is close to the hole and decreases as the distance increases.

        Parameters
        ----------
        ball_pos : np.ndarray of shape (3,)
            The 3D position of the golf ball.
        hole_pos : np.ndarray of shape (3,)
            The 3D position of the hole.

        Returns
        -------
        reward : float
            A scalar reward based on the distance between the ball and the hole.
            The reward is higher for closer proximity and decays exponentially with distance.
        """
        distance = np.linalg.norm(ball_pos - hole_pos)
        reward = np.exp(distance * -2.0)
        return reward

    def _joint_vel_l2(self):
        """
        Computes the penalty for joint velocities in the system.

        This function calculates the L2 norm (sum of squares) of the joint velocities,
        which acts as a penalty term. The penalty encourages the robot to move smoothly,
        avoiding rapid or jerky movements that could result from high joint velocities.

        Returns
        -------
        penalty : float
            The total L2 penalty for all robot joint velocities. Higher values indicate
            faster and more abrupt movements, which are penalized more heavily.
        """
        joint_vel = []
        for joint in self.robot_model.robot_joints:
            joint_vel.append(self.robot_model.sim.data.get_joint_qvel(joint))
        joint_vel = np.array(joint_vel)
        return np.sum(joint_vel**2)

    def _club_dropped(self, club_grip_pos, minimum_height=0.06):
        """
        Penalizes if the golf club is dropped below a specified minimum height.

        This function checks if the grip of the golf club falls below a certain height threshold
        (default is 0.06 meters), which signifies that the club has been dropped. A penalty is
        returned when the club's grip position violates this condition.

        Parameters
        ----------
        club_grip_pos : np.ndarray of shape (3,)
            The 3D position of the golf club grip.
        minimum_height : float, optional, default=0.06
            The minimum height threshold to determine if the club has been dropped.

        Returns
        -------
        penalty : float
            A scalar penalty of 1.0 if the club has dropped (i.e., its z-position is below the threshold),
            otherwise 0.0.
        """
        return float(club_grip_pos[2] < minimum_height)

    def _ball_passed_hole(self, ball_pos, hole_pos):
        """
        Penalizes if the ball has passed beyond the hole in the x-direction.

        This function checks if the golf ball has moved past the hole in the x-axis direction,
        indicating that the ball has overshot the hole. A penalty is applied when this condition is met.

        Parameters
        ----------
        ball_pos : np.ndarray of shape (3,)
            The 3D position of the golf ball.
        hole_pos : np.ndarray of shape (3,)
            The 3D position of the hole.

        Returns
        -------
        penalty : float
            A scalar penalty of 1.0 if the ball has passed the hole in the x-direction (with an offset),
            otherwise 0.0.
        """
        # Check if the ball has passed the hole in the x direction
        return float(ball_pos[0] < hole_pos[0] - 0.08)

    def _ball_in_hole(self, ball_pos, hole_pos):
        """
        Checks if the ball is within the hole.

        This function computes the Euclidean distance between the golf ball and the hole.
        If the distance is below a specified threshold (0.06 meters), it considers the ball to be in the hole.

        Parameters
        ----------
        ball_pos : np.ndarray of shape (3,)
            The 3D position of the golf ball.
        hole_pos : np.ndarray of shape (3,)
            The 3D position of the hole.

        Returns
        -------
        is_in_hole : float
            A scalar value of 1.0 if the ball is within the hole (distance is below the threshold),
            otherwise 0.0.
        """
        return (np.linalg.norm(ball_pos - hole_pos) < 0.06).astype(np.float32)

    def _get_info(self) -> dict:
        return {
            "success": bool(
                self._ball_in_hole(
                    self.robot_model.data.xpos[self.golf_ball_id],
                    self.robot_model.data.xpos[self.golf_hole_id],
                )
            )
        }
