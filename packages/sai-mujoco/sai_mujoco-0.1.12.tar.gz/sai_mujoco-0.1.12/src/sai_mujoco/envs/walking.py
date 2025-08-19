import numpy as np
from sai_mujoco.envs.base import BaseEnv
from sai_mujoco.utils.sim_utils import check_contact


class WalkingEnv(BaseEnv):
    r"""

    ## Description
    A Walking environment where a robot learns to walk and maintain stable locomotion. The robot must learn to coordinate its
    leg movements to achieve forward motion while maintaining balance and avoiding falls. The primary challenges include:
    maintaining upright posture, coordinating foot movements for stable gait, managing energy efficiency, and adapting to
    different walking speeds and terrains, all within a continuous and high-dimensional action and observation space.

    ## Observation Space
    The observation space consists of the following parts (in order):

    - *qpos:* Position values of the robot's body parts. The dimensionality depends on the robot's joint configuration.
    - *qvel:* The velocities of these individual body parts (their derivatives). The dimensionality depends on the robot's joint configuration.

    The observation space is inherited from the base environment and includes the robot's joint positions and velocities.

    ## Rewards

    The reward components include:

        1. `linear_vel_z` (weight: 0.0): Penalizes vertical linear velocity to encourage forward motion.
        2. `ang_vel_xy` (weight: -0.15): Penalizes angular velocity in the x-y plane to encourage stable orientation.
        3. `orientation` (weight: -1.0): Penalizes deviation from upright orientation.
        4. `cost_base_height` (weight: -20): Penalizes deviation from target base height.
        5. `cost_torques` (weight: -2e-4): Penalizes high actuator torques to encourage energy efficiency.
        6. `action_rate` (weight: -1.0): Penalizes rapid action changes to encourage smooth motion.
        7. `robot_energy` (weight: -2e-3): Penalizes energy consumption based on joint velocities and torques.
        8. `dof_qacc` (weight: -1e-7): Penalizes high joint accelerations.
        9. `dof_qvel` (weight: -1e-4): Penalizes high joint velocities.
        10. `foot_clearance` (weight: 0.0): Rewards proper foot clearance during swing phase.
        11. `foot_slip` (weight: -0.1): Penalizes foot slipping during stance phase.
        12. `survival` (weight: 0.25): Rewards staying upright and not falling.
        13. `feet_distance` (weight: -1.0): Penalizes feet being too close together.

    ## Episode End
    ### Termination

    The current episode should terminate based on the following criteria:
        1. If the robot has fallen (base height outside acceptable range)
        2. If the simulation data contains NaN values

    ### Truncation
    The episode will be truncated when the maximum number of timesteps is reached.
    """

    scene_name: str = "base_scene"

    default_camera_config = {
        "trackbodyid": 0,
        "distance": 3,
    }

    reward_config = {
        "linear_vel_z": 0.0,
        "ang_vel_xy": -0.15,
        "orientation": -1.0,
        "cost_base_height": -20,
        "cost_torques": -2e-4,
        "action_rate": -1.0,
        "robot_energy": -2e-3,
        "dof_qacc": -1e-7,
        "dof_qvel": -1e-4,
        "foot_clearance": 0.0,
        "foot_slip": -0.1,
        "survival": 0.25,
        "feet_distance": -1.0,
    }

    def compute_reward(self) -> float:
        """
        Computes and returns individual reward components for the current simulation state.

        This function calculates various reward terms that encourage stable walking behavior:
        - Penalizes vertical motion and angular velocities to encourage forward walking
        - Rewards maintaining upright posture and target base height
        - Penalizes high energy consumption and jerky movements
        - Rewards proper foot clearance and penalizes foot slipping
        - Rewards survival (not falling) and penalizes feet being too close

        Returns
        -------
        raw_reward : dict
            A dictionary mapping each reward term name (str) to its corresponding scalar value (float).
            These are raw values and not yet combined into a scalar total reward.
        """
        base_height = self.robot_model.sim.data.get_site_xpos(
            self.robot_model._root_site
        )[2]
        linear_vel_z = np.linalg.norm(
            self.robot_model.get_sensor_measurement("torso_vel")
        )
        ang_vel_xy = np.linalg.norm(
            self.robot_model.get_sensor_measurement("torso_gyro")
        )
        orientation = np.linalg.norm(
            self.robot_model.get_sensor_measurement("upvector")
        )

        cost_base_height = self.cost_base_height(base_height)
        robot_energy = self.robot_energy()
        survival = float(not self.has_robot_fallen(base_height))
        feet_distance = self.feet_distance()
        foot_clearance = self.foot_clearance()
        foot_slip = self.foot_slip()
        cost_torques = np.sum(np.abs(self.robot_model.data.actuator_force))
        robot_joints_qvel = np.array(
            [
                self.robot_model.sim.data.get_joint_qvel(j)
                for j in self.robot_model.robot_joints
            ]
        )
        robot_joints_qacc = np.array(
            [
                self.robot_model.sim.data.get_joint_qacc(j)
                for j in self.robot_model.robot_joints
            ]
        )
        dof_qacc = np.sum(np.square(robot_joints_qacc))
        dof_qvel = np.sum(np.square(robot_joints_qvel))

        return {
            "linear_vel_z": linear_vel_z,
            "ang_vel_xy": ang_vel_xy,
            "orientation": orientation,
            "cost_base_height": cost_base_height,
            "cost_torques": cost_torques,
            "robot_energy": robot_energy,
            "survival": survival,
            "feet_distance": feet_distance,
            "foot_clearance": foot_clearance,
            "foot_slip": foot_slip,
            "dof_qacc": dof_qacc,
            "dof_qvel": dof_qvel,
        }

    def compute_terminated(self) -> bool:
        """
        Determines whether the current episode should terminate based on failure conditions.

        This function checks for two termination criteria in the walking environment:
            1. If the robot has fallen (base height outside acceptable range)
            2. If the simulation data contains NaN values (indicating numerical instability)

        Returns
        -------
        terminated : bool
            `True` if any of the termination conditions are met; otherwise `False`.
        """
        height = self.robot_model.sim.data.get_site_xpos(self.robot_model._root_site)[2]
        has_fallen = self.has_robot_fallen(height)

        data_nan = (
            np.isnan(self.robot_model.data.qpos).any()
            | np.isnan(self.robot_model.data.qvel).any()
        )

        return has_fallen or data_nan

    def _setup_references(self):
        """
        Initializes and stores environment-specific reference IDs for key components in the simulation.

        This function sets up MuJoCo internal IDs (site IDs) for robot components involved in the walking
        environment. These references are necessary for accessing position, orientation, and other dynamic
        properties during simulation.

        Specifically, it retrieves:
            - Site IDs for the robot's feet (left and right)
            - Floor geometry name for contact detection
            - Root site ID for base position tracking

        These references are stored as instance attributes and used throughout the environment
        for computing observations, rewards, and termination conditions.
        """
        self._feet_site_id = np.array(
            [
                self.robot_model.model.site(name).id
                for name in self.robot_model.feet_sites
            ]
        )

        self._floor_geom = "floor"
        self._root_site_id = self.robot_model.model.site(self.robot_model._root_site).id

    def has_robot_fallen(self, height, min_height=1.0, max_height=2.0):
        """
        Determines if the robot has fallen based on its base height.

        This function checks if the robot's base height is within an acceptable range.
        If the robot has a defined standing height range, it uses those values;
        otherwise, it uses the default minimum and maximum height thresholds.

        Parameters
        ----------
        height : float
            The current height of the robot's base from the ground.
        min_height : float, optional, default=1.0
            The minimum acceptable height for the robot base.
        max_height : float, optional, default=2.0
            The maximum acceptable height for the robot base.

        Returns
        -------
        fallen : bool
            `True` if the robot has fallen (height outside acceptable range); otherwise `False`.
        """
        if hasattr(self.robot_model, "standing_height"):
            min_height = self.robot_model.standing_height[0]
            max_height = self.robot_model.standing_height[1]

        fallen = min_height < height < max_height
        return not fallen

    def cost_base_height(self, base_height, base_height_target=0.665) -> float:
        """
        Computes a cost based on the deviation of the robot's base height from a target height.

        This function calculates the squared difference between the current base height and
        a target height. This encourages the robot to maintain a specific height during walking,
        which is important for stable locomotion.

        Parameters
        ----------
        base_height : float
            The current height of the robot's base from the ground.
        base_height_target : float, optional, default=0.665
            The target height for the robot's base.

        Returns
        -------
        cost : float
            The squared difference between current and target base height.
        """
        return np.square(base_height - base_height_target)

    def robot_energy(self):
        """
        Computes the energy consumption of the robot based on joint velocities and actuator forces.

        This function calculates the total energy consumption by multiplying joint velocities
        with actuator forces and taking the absolute sum. This encourages the robot to move
        efficiently and avoid wasteful energy consumption.

        Returns
        -------
        energy : float
            The total energy consumption of the robot (joint velocity * actuator force).
        """
        actuators_ids = [
            self.robot_model.model.actuator(name).id
            for name in self.robot_model.robot_actuators
        ]
        forces = self.robot_model.data.actuator_force[actuators_ids]
        vel = np.array(
            [
                self.robot_model.sim.data.get_joint_qvel(j)
                for j in self.robot_model.robot_joints
            ]
        )

        return np.sum(np.abs(vel * forces))

    def foot_clearance(self, max_foot_height: float = 0.12):
        """
        Computes a reward based on foot clearance during the swing phase of walking.

        This function calculates how well the robot's feet clear the ground during the swing
        phase. It considers the vertical distance of each foot from a maximum foot height
        threshold, weighted by the horizontal velocity of the feet. This encourages proper
        foot lifting during walking.

        Parameters
        ----------
        max_foot_height : float, optional, default=0.12
            The maximum acceptable foot height during swing phase.

        Returns
        -------
        clearance_reward : float
            A reward based on foot clearance, higher values indicate better foot lifting.
        """
        feet_vel = self.robot_model.get_sensor_measurement("global_linvel")
        vel_xy = feet_vel[..., :2]
        vel_norm = np.sqrt(np.linalg.norm(vel_xy, axis=-1))
        foot_pos = self.robot_model.data.site_xpos[self._feet_site_id]
        foot_z = foot_pos[..., -1]
        delta = np.abs(foot_z - max_foot_height)

        return np.sum(delta * vel_norm)

    def _feet_contact(self):
        """
        Determines which feet are in contact with the ground.

        This function checks the contact status between the robot's feet and the floor
        using MuJoCo's contact detection system. It returns a boolean array indicating
        which feet are currently in contact with the ground.

        Returns
        -------
        contact : np.ndarray
            A boolean array indicating which feet are in contact with the ground.
        """
        left_feet_contact = np.array(
            [
                check_contact(self.robot_model.sim, geom, self._floor_geom)
                for geom in self.robot_model._left_feet_geoms
            ]
        )
        right_feet_contact = np.array(
            [
                check_contact(self.robot_model.sim, geom, self._floor_geom)
                for geom in self.robot_model._right_feet_geoms
            ]
        )
        contact = np.hstack([np.any(left_feet_contact), np.any(right_feet_contact)])

        return contact

    def foot_slip(self):
        """
        Computes a penalty for foot slipping during the stance phase of walking.

        This function calculates a penalty based on the horizontal velocity of the robot's
        body when feet are in contact with the ground. This encourages the robot to maintain
        stable foot contact and avoid slipping during the stance phase.

        Returns
        -------
        slip_penalty : float
            A penalty based on foot slipping, higher values indicate more slipping.
        """
        contact = self._feet_contact()
        body_vel = self.robot_model.get_sensor_measurement("global_linvel")[:2]
        reward = np.sum(np.linalg.norm(body_vel, axis=-1) * contact)
        return reward

    def feet_distance(self):
        """
        Computes a penalty based on the distance between the robot's feet.

        This function calculates the distance between the left and right feet in the robot's
        local coordinate frame. It penalizes feet being too close together, which can lead
        to instability during walking. The penalty is clipped to encourage maintaining a
        reasonable stance width.

        Returns
        -------
        distance_penalty : float
            A penalty based on feet distance, higher values indicate feet are too close.
        """
        left_foot_pos = self.robot_model.data.site_xpos[self._feet_site_id[0]]
        right_foot_pos = self.robot_model.data.site_xpos[self._feet_site_id[1]]
        base_xmat = self.robot_model.data.site_xmat[self._root_site_id]
        base_yaw = np.arctan2(base_xmat[1], base_xmat[0])
        feet_distance = np.abs(
            np.cos(base_yaw) * (left_foot_pos[1] - right_foot_pos[1])
            - np.sin(base_yaw) * (left_foot_pos[0] - right_foot_pos[0])
        )
        return np.clip(0.2 - feet_distance, 0.0, 0.1)
