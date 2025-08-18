from dataclasses import MISSING
from typing import Sequence

import torch

from srb._typing import StepReturn
from srb.core.asset import (
    Articulation,
    RigidObjectCfg,
    RigidObjectCollection,
    RigidObjectCollectionCfg,
)
from srb.core.env import ManipulationEnv
from srb.core.manager import EventTermCfg, SceneEntityCfg
from srb.core.mdp import reset_collection_root_state_uniform_poisson_disk_2d
from srb.core.sensor import ContactSensor, ContactSensorCfg
from srb.utils.cfg import configclass
from srb.utils.math import (
    combine_frame_transforms,
    matrix_from_quat,
    rotmat_to_rot6d,
    scale_transform,
    subtract_frame_transforms,
)
from srb.utils.sampling import sample_grid

from .asset import select_peg_in_hole_assembly
from .task import EventCfg, SceneCfg, TaskCfg

##############
### Config ###
##############


@configclass
class MultiSceneCfg(SceneCfg):
    peg: None = None
    pegs: RigidObjectCollectionCfg = RigidObjectCollectionCfg(
        rigid_objects=MISSING,  # type: ignore
    )
    hole: None = None
    holes: RigidObjectCollectionCfg = RigidObjectCollectionCfg(
        rigid_objects=MISSING,  # type: ignore
    )


@configclass
class MultiEventCfg(EventCfg):
    randomize_object_state: EventTermCfg = EventTermCfg(
        func=reset_collection_root_state_uniform_poisson_disk_2d,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("pegs"),
            "pose_range": {
                "x": MISSING,
                "y": MISSING,
                "roll": (torch.pi / 2, torch.pi / 2),
                "pitch": (-torch.pi, torch.pi),
                "yaw": (-torch.pi, torch.pi),
            },
            "velocity_range": {},
            "radius": 0.1,
        },
    )


@configclass
class MultiTaskCfg(TaskCfg):
    ## Scene
    scene: MultiSceneCfg = MultiSceneCfg()
    num_pegs: int = 4
    hole_spacing: float = 0.15

    ## Events
    events: MultiEventCfg = MultiEventCfg()

    ## Time
    episode_length_s: float = MISSING  # type: ignore
    _base_episode_length_s: float = 10.0

    def __post_init__(self):
        super().__post_init__()

        # Time
        self.episode_length_s = self.num_pegs * self._base_episode_length_s

        # Task setup: Peg-in-hole assembly
        self.scene.peg = None
        self.scene.hole = None
        (num_rows, num_cols), (grid_spacing_pos, grid_spacing_rot) = sample_grid(
            num_instances=self.num_pegs,
            spacing=self.hole_spacing,
            global_pos_offset=(0.5, 0.0, 0.1),
        )
        self.peg_in_hole_assemblies = [
            select_peg_in_hole_assembly(
                self,
                seed=self.seed + (i * self.scene.num_envs),
                prim_path_peg=f"{{ENV_REGEX_NS}}/peg{i}",
                prim_path_hole=f"{{ENV_REGEX_NS}}/hole{i}",
                init_state=RigidObjectCfg.InitialStateCfg(
                    pos=grid_spacing_pos[i],
                    rot=grid_spacing_rot[i],
                ),
                peg_kwargs={
                    "activate_contact_sensors": True,
                },
            )
            for i in range(self.num_pegs)
        ]
        # Scene: Pegs
        self.scene.pegs.rigid_objects = {
            f"peg{i}": cfg.peg.asset_cfg.replace(  # type: ignore
                init_state=RigidObjectCfg.InitialStateCfg(
                    pos=(0.5, 0.0, 0.13),
                )
            )
            for i, cfg in enumerate(self.peg_in_hole_assemblies)
        }
        # Scene: Holes
        self.scene.holes.rigid_objects = {
            f"hole{i}": cfg.hole.asset_cfg
            for i, cfg in enumerate(self.peg_in_hole_assemblies)
        }

        # Sensor: End-effector contacts
        if isinstance(self.scene.contacts_end_effector, ContactSensorCfg):
            self.scene.contacts_end_effector.filter_prim_paths_expr = [
                f"{{ENV_REGEX_NS}}/peg{i}" for i in range(self.num_pegs)
            ]

        # Event: Randomize object state
        self.events.randomize_object_state.params["pose_range"]["x"] = (  # type: ignore
            -0.5 * (num_rows - 0.5) * self.hole_spacing,
            0.5 * (num_rows - 0.5) * self.hole_spacing,
        )
        self.events.randomize_object_state.params["pose_range"]["y"] = (  # type: ignore
            -0.5 * (num_cols - 0.5) * self.hole_spacing,
            0.5 * (num_cols - 0.5) * self.hole_spacing,
        )

        # Update seed & number of variants for procedural assets
        self._update_procedural_assets()


############
### Task ###
############


class MultiTask(ManipulationEnv):
    cfg: MultiTaskCfg

    def __init__(self, cfg: MultiTaskCfg, **kwargs):
        super().__init__(cfg, **kwargs)

        ## Get scene assets
        self._objs: RigidObjectCollection = self.scene["pegs"]
        self._targets: RigidObjectCollection = self.scene["holes"]

        ## Initialize buffers
        self._tf_pos_objs_initial = torch.zeros(
            (self.num_envs, self.cfg.num_pegs, 3),
            dtype=torch.float32,
            device=self.device,
        )
        self._offset_pos_pegs_ends = torch.tensor(
            [
                self.cfg.peg_in_hole_assemblies[i].peg.offset_pos_ends
                for i in range(self.cfg.num_pegs)
            ],
            dtype=torch.float32,
            device=self.device,
        ).repeat(self.num_envs, 1, 1, 1)

        self._symmetry_pegs = torch.tensor(
            [
                self.cfg.peg_in_hole_assemblies[i].peg.symmetry
                for i in range(self.cfg.num_pegs)
            ],
            dtype=torch.int32,
            device=self.device,
        ).repeat(self.num_envs, 1)
        self._offset_pos_holes_bottom = torch.tensor(
            [
                self.cfg.peg_in_hole_assemblies[i].hole.offset_pos_bottom
                for i in range(self.cfg.num_pegs)
            ],
            dtype=torch.float32,
            device=self.device,
        ).repeat(self.num_envs, 1, 1)
        self._offset_pos_holes_entrance = torch.tensor(
            [
                self.cfg.peg_in_hole_assemblies[i].hole.offset_pos_entrance
                for i in range(self.cfg.num_pegs)
            ],
            dtype=torch.float32,
            device=self.device,
        ).repeat(self.num_envs, 1, 1)

    def _reset_idx(self, env_ids: Sequence[int]):
        super()._reset_idx(env_ids)
        self._tf_pos_objs_initial[env_ids] = self._objs.data.object_pos_w[env_ids]

    def extract_step_return(self) -> StepReturn:
        return _compute_step_return(
            ## Time
            episode_length=self.episode_length_buf,
            max_episode_length=self.max_episode_length,
            truncate_episodes=self.cfg.truncate_episodes,
            ## Actions
            act_current=self.action_manager.action,
            act_previous=self.action_manager.prev_action,
            ## States
            # Joints
            joint_pos_robot=self._robot.data.joint_pos,
            joint_pos_limits_robot=(
                self._robot.data.soft_joint_pos_limits
                if torch.all(torch.isfinite(self._robot.data.soft_joint_pos_limits))
                else None
            ),
            joint_pos_end_effector=self._end_effector.data.joint_pos
            if isinstance(self._end_effector, Articulation)
            else None,
            joint_pos_limits_end_effector=(
                self._end_effector.data.soft_joint_pos_limits
                if isinstance(self._end_effector, Articulation)
                and torch.all(
                    torch.isfinite(self._end_effector.data.soft_joint_pos_limits)
                )
                else None
            ),
            joint_acc_robot=self._robot.data.joint_acc,
            joint_applied_torque_robot=self._robot.data.applied_torque,
            # Kinematics
            fk_pos_end_effector=self._tf_end_effector.data.target_pos_source[:, 0, :],
            fk_quat_end_effector=self._tf_end_effector.data.target_quat_source[:, 0, :],
            # Transforms (world frame)
            tf_pos_end_effector=self._tf_end_effector.data.target_pos_w[:, 0, :],
            tf_quat_end_effector=self._tf_end_effector.data.target_quat_w[:, 0, :],
            tf_pos_objs_initial=self._tf_pos_objs_initial,
            tf_pos_objs=self._objs.data.object_pos_w,
            tf_quat_objs=self._objs.data.object_quat_w,
            tf_pos_targets=self._targets.data.object_pos_w,
            tf_quat_targets=self._targets.data.object_quat_w,
            # Contacts
            contact_forces_robot=self._contacts_robot.data.net_forces_w,  # type: ignore
            contact_forces_end_effector=self._contacts_end_effector.data.net_forces_w
            if isinstance(self._contacts_end_effector, ContactSensor)
            else None,
            contact_force_matrix_end_effector=self._contacts_end_effector.data.force_matrix_w
            if isinstance(self._contacts_end_effector, ContactSensor)
            else None,
            ## Peg-in-hole descriptors
            offset_pos_pegs_ends=self._offset_pos_pegs_ends,
            symmetry_pegs=self._symmetry_pegs,
            offset_pos_holes_bottom=self._offset_pos_holes_bottom,
            offset_pos_holes_entrance=self._offset_pos_holes_entrance,
        )


@torch.jit.script
def _compute_step_return(
    *,
    ## Time
    episode_length: torch.Tensor,
    max_episode_length: int,
    truncate_episodes: bool,
    ## Actions
    act_current: torch.Tensor,
    act_previous: torch.Tensor,
    ## States
    # Joints
    joint_pos_robot: torch.Tensor,
    joint_pos_limits_robot: torch.Tensor | None,
    joint_pos_end_effector: torch.Tensor | None,
    joint_pos_limits_end_effector: torch.Tensor | None,
    joint_acc_robot: torch.Tensor,
    joint_applied_torque_robot: torch.Tensor,
    # Kinematics
    fk_pos_end_effector: torch.Tensor,
    fk_quat_end_effector: torch.Tensor,
    # Transforms (world frame)
    tf_pos_end_effector: torch.Tensor,
    tf_quat_end_effector: torch.Tensor,
    tf_pos_objs_initial: torch.Tensor,
    tf_pos_objs: torch.Tensor,
    tf_quat_objs: torch.Tensor,
    tf_pos_targets: torch.Tensor,
    tf_quat_targets: torch.Tensor,
    # Contacts
    contact_forces_robot: torch.Tensor,
    contact_forces_end_effector: torch.Tensor | None,
    contact_force_matrix_end_effector: torch.Tensor | None,
    ## Peg-in-hole descriptors
    offset_pos_pegs_ends: torch.Tensor,
    symmetry_pegs: torch.Tensor,
    offset_pos_holes_bottom: torch.Tensor,
    offset_pos_holes_entrance: torch.Tensor,
) -> StepReturn:
    num_envs = episode_length.size(0)
    num_objs = tf_pos_objs.size(1)
    dtype = episode_length.dtype
    device = episode_length.device

    ############
    ## States ##
    ############
    ## Joints
    # Robot joints
    joint_pos_robot_normalized = (
        scale_transform(
            joint_pos_robot,
            joint_pos_limits_robot[:, :, 0],
            joint_pos_limits_robot[:, :, 1],
        )
        if joint_pos_limits_robot is not None
        else joint_pos_robot
    )
    # End-effector joints
    joint_pos_end_effector_normalized = (
        scale_transform(
            joint_pos_end_effector,
            joint_pos_limits_end_effector[:, :, 0],
            joint_pos_limits_end_effector[:, :, 1],
        )
        if joint_pos_end_effector is not None
        and joint_pos_limits_end_effector is not None
        else (
            joint_pos_end_effector
            if joint_pos_end_effector is not None
            else torch.empty((num_envs, 0), dtype=dtype, device=device)
        )
    )

    ## Kinematics
    fk_rotmat_end_effector = matrix_from_quat(fk_quat_end_effector)
    fk_rot6d_end_effector = rotmat_to_rot6d(fk_rotmat_end_effector)

    ## Transforms (world frame)
    # End-effector -> Object
    tf_pos_end_effector_to_objs, tf_quat_end_effector_to_objs = (
        subtract_frame_transforms(
            t01=tf_pos_end_effector.unsqueeze(1).repeat(1, num_objs, 1),
            q01=tf_quat_end_effector.unsqueeze(1).repeat(1, num_objs, 1),
            t02=tf_pos_objs,
            q02=tf_quat_objs,
        )
    )
    tf_rotmat_end_effector_to_objs = matrix_from_quat(tf_quat_end_effector_to_objs)
    tf_rot6d_end_effector_to_objs = rotmat_to_rot6d(tf_rotmat_end_effector_to_objs)

    # Peg -> Peg ends
    _tf_pos_pegs_end0, _ = combine_frame_transforms(
        t01=tf_pos_objs,
        q01=tf_quat_objs,
        t12=offset_pos_pegs_ends[:, :, 0],
    )
    _tf_pos_pegs_end1, _ = combine_frame_transforms(
        t01=tf_pos_objs,
        q01=tf_quat_objs,
        t12=offset_pos_pegs_ends[:, :, 1],
    )
    tf_pos_pegs_ends = torch.stack([_tf_pos_pegs_end0, _tf_pos_pegs_end1], dim=2)

    # Hole -> Hole entrance | bottom
    tf_pos_holes_entrance, _ = combine_frame_transforms(
        t01=tf_pos_targets,
        q01=tf_quat_targets,
        t12=offset_pos_holes_entrance,
    )
    tf_pos_holes_bottom, _ = combine_frame_transforms(
        t01=tf_pos_targets,
        q01=tf_quat_targets,
        t12=offset_pos_holes_bottom,
    )

    # Peg ends -> Hole entrance
    tf_pos_pegs_end0_to_holes_entrance, tf_quat_pegs_to_holes_entrance = (
        subtract_frame_transforms(
            t01=tf_pos_pegs_ends[:, :, 0],
            q01=tf_quat_objs,
            t02=tf_pos_holes_entrance,
            q02=tf_quat_targets,
        )
    )
    tf_pos_pegs_end1_to_holes_entrance, _ = subtract_frame_transforms(
        t01=tf_pos_pegs_ends[:, :, 1],
        q01=tf_quat_objs,
        t02=tf_pos_holes_entrance,
    )
    tf_pos_pegs_ends_to_holes_entrance = torch.stack(
        [tf_pos_pegs_end0_to_holes_entrance, tf_pos_pegs_end1_to_holes_entrance], dim=2
    )
    tf_rotmat_pegs_to_holes = matrix_from_quat(tf_quat_pegs_to_holes_entrance)
    tf_rot6d_pegs_to_holes = rotmat_to_rot6d(tf_rotmat_pegs_to_holes)

    # Peg ends -> Hole bottom
    tf_pos_pegs_end0_to_holes_bottom, _ = subtract_frame_transforms(
        t01=tf_pos_pegs_ends[:, :, 0],
        q01=tf_quat_objs,
        t02=tf_pos_holes_bottom,
    )
    tf_pos_pegs_end1_to_holes_bottom, _ = subtract_frame_transforms(
        t01=tf_pos_pegs_ends[:, :, 1],
        q01=tf_quat_objs,
        t02=tf_pos_holes_bottom,
    )
    tf_pos_pegs_ends_to_holes_bottom = torch.stack(
        [tf_pos_pegs_end0_to_holes_bottom, tf_pos_pegs_end1_to_holes_bottom], dim=1
    )

    ## Contacts
    contact_forces_mean_robot = contact_forces_robot.mean(dim=1)
    contact_forces_mean_end_effector = (
        contact_forces_end_effector.mean(dim=1)
        if contact_forces_end_effector is not None
        else torch.empty((num_envs, 0), dtype=dtype, device=device)
    )
    contact_forces_end_effector = (
        contact_forces_end_effector
        if contact_forces_end_effector is not None
        else torch.empty((num_envs, 0), dtype=dtype, device=device)
    )

    #############
    ## Rewards ##
    #############
    # Penalty: Action rate
    WEIGHT_ACTION_RATE = -0.05
    penalty_action_rate = WEIGHT_ACTION_RATE * torch.sum(
        torch.square(act_current - act_previous), dim=1
    )

    # Penalty: Joint torque
    WEIGHT_JOINT_TORQUE = -0.000025
    MAX_JOINT_TORQUE_PENALTY = -4.0
    penalty_joint_torque = torch.clamp_min(
        WEIGHT_JOINT_TORQUE
        * torch.sum(torch.square(joint_applied_torque_robot), dim=1),
        min=MAX_JOINT_TORQUE_PENALTY,
    )

    # Penalty: Joint acceleration
    WEIGHT_JOINT_ACCELERATION = -0.0005
    MAX_JOINT_ACCELERATION_PENALTY = -4.0
    penalty_joint_acceleration = torch.clamp_min(
        WEIGHT_JOINT_ACCELERATION * torch.sum(torch.square(joint_acc_robot), dim=1),
        min=MAX_JOINT_ACCELERATION_PENALTY,
    )

    # Penalty: Undesired robot contacts
    WEIGHT_UNDESIRED_ROBOT_CONTACTS = -1.0
    THRESHOLD_UNDESIRED_ROBOT_CONTACTS = 10.0
    penalty_undesired_robot_contacts = WEIGHT_UNDESIRED_ROBOT_CONTACTS * (
        torch.max(torch.norm(contact_forces_robot, dim=-1), dim=1)[0]
        > THRESHOLD_UNDESIRED_ROBOT_CONTACTS
    )

    # Reward: End-effector top-down orientation
    WEIGHT_TOP_DOWN_ORIENTATION = 1.0
    TANH_STD_TOP_DOWN_ORIENTATION = 0.15
    top_down_alignment = torch.sum(
        fk_rotmat_end_effector[:, :, 2]
        * torch.tensor((0.0, 0.0, -1.0), device=device)
        .unsqueeze(0)
        .expand(num_envs, 3),
        dim=1,
    )
    reward_top_down_orientation = WEIGHT_TOP_DOWN_ORIENTATION * (
        1.0 - torch.tanh((1.0 - top_down_alignment) / TANH_STD_TOP_DOWN_ORIENTATION)
    )

    # Reward: Distance | End-effector <--> Object
    WEIGHT_DISTANCE_END_EFFECTOR_TO_OBJ = 2.5
    TANH_STD_DISTANCE_END_EFFECTOR_TO_OBJ = 0.2
    reward_distance_end_effector_to_objs = WEIGHT_DISTANCE_END_EFFECTOR_TO_OBJ * (
        1.0
        - torch.tanh(
            torch.norm(tf_pos_end_effector_to_objs, dim=-1)
            / TANH_STD_DISTANCE_END_EFFECTOR_TO_OBJ
        )
    ).sum(dim=-1)

    # Reward: Grasp object
    WEIGHT_GRASP = 8.0
    THRESHOLD_GRASP = 5.0
    reward_grasp = (
        WEIGHT_GRASP
        * (
            torch.mean(
                torch.max(
                    torch.norm(contact_force_matrix_end_effector, dim=-1), dim=-1
                )[0],
                dim=1,
            )
            > THRESHOLD_GRASP
        )
        if contact_force_matrix_end_effector is not None
        else torch.zeros(num_envs, dtype=dtype, device=device)
    )

    # Reward: Lift object
    WEIGHT_LIFT = 4.0
    HEIGHT_OFFSET_LIFT = 0.2
    HEIGHT_SPAN_LIFT = 0.1
    TANH_STD_HEIGHT_LIFT = 0.05
    reward_lift = WEIGHT_LIFT * (
        1.0
        - torch.tanh(
            (
                torch.abs(
                    tf_pos_objs[:, :, 2]
                    - tf_pos_objs_initial[:, :, 2]
                    - HEIGHT_OFFSET_LIFT
                )
                - HEIGHT_SPAN_LIFT
            ).clamp(min=0.0)
            / TANH_STD_HEIGHT_LIFT
        )
    ).sum(dim=-1)

    # Reward: Alignment | Peg -> Hole | Primary Z axis
    WEIGHT_ALIGN_PEG_TO_HOLE_PRIMARY = 8.0
    TANH_STD_ALIGN_PEG_TO_HOLE_PRIMARY = 0.5
    _pegs_to_holes_primary_axis_similarity = torch.abs(
        tf_rotmat_pegs_to_holes[:, :, 2, 2]
    )
    reward_align_pegs_to_holes_primary = WEIGHT_ALIGN_PEG_TO_HOLE_PRIMARY * (
        1.0
        - torch.tanh(
            (1.0 - _pegs_to_holes_primary_axis_similarity)
            / TANH_STD_ALIGN_PEG_TO_HOLE_PRIMARY
        )
    ).sum(dim=-1)

    # Reward: Alignment | Peg -> Hole | Secondary XY axes (affected by primary via power)
    WEIGHT_ALIGN_PEG_TO_HOLE_SECONDARY = 4.0
    TANH_STD_ALIGN_PEG_TO_HOLE_SECONDARY = 0.2
    _pegs_to_holes_yaw = torch.atan2(
        tf_rotmat_pegs_to_holes[:, :, 0, 1], tf_rotmat_pegs_to_holes[:, :, 0, 0]
    )
    _symmetry_step = 2 * torch.pi / symmetry_pegs
    _pegs_to_holes_yaw_symmetric_directional = _pegs_to_holes_yaw % _symmetry_step
    # Note: Lines above might result in NaN/inf when `peg_rot_symmetry_n=0` (infinite circular symmetry)
    #       However, the following `torch.where()` will handle this case
    _pegs_to_holes_yaw_symmetric_normalized = torch.where(
        symmetry_pegs <= 0,
        0.0,
        torch.min(
            _pegs_to_holes_yaw_symmetric_directional,
            _symmetry_step - _pegs_to_holes_yaw_symmetric_directional,
        )
        / (_symmetry_step / 2.0),
    )
    reward_align_pegs_to_holes_secondary = WEIGHT_ALIGN_PEG_TO_HOLE_SECONDARY * (
        1.0
        - torch.tanh(
            _pegs_to_holes_yaw_symmetric_normalized.pow(
                _pegs_to_holes_primary_axis_similarity
            )
            / TANH_STD_ALIGN_PEG_TO_HOLE_SECONDARY
        )
    ).sum(dim=-1)

    # Reward: Distance | Peg -> Hole entrance (gradual)
    WEIGHT_DISTANCE_PEG_TO_HOLE_ENTRANCE_GRADUAL = 8.0
    TANH_STD_DISTANCE_PEG_TO_HOLE_ENTRANCE_GRADUAL = 0.16
    reward_distance_pegs_to_holes_entrance_gradual = (
        WEIGHT_DISTANCE_PEG_TO_HOLE_ENTRANCE_GRADUAL
        * (
            1.0
            - torch.tanh(
                torch.min(
                    torch.norm(tf_pos_pegs_ends_to_holes_entrance, dim=-1), dim=1
                )[0]
                / TANH_STD_DISTANCE_PEG_TO_HOLE_ENTRANCE_GRADUAL
            )
        )
    ).sum(dim=-1)

    # Reward: Distance | Peg -> Hole entrance
    WEIGHT_DISTANCE_PEG_TO_HOLE_ENTRANCE = 32.0
    TANH_STD_DISTANCE_PEG_TO_HOLE_ENTRANCE = 0.04
    reward_distance_pegs_to_holes_entrance = WEIGHT_DISTANCE_PEG_TO_HOLE_ENTRANCE * (
        1.0
        - torch.tanh(
            torch.min(torch.norm(tf_pos_pegs_ends_to_holes_entrance, dim=-1), dim=1)[0]
            / TANH_STD_DISTANCE_PEG_TO_HOLE_ENTRANCE
        )
    ).sum(dim=-1)

    # Reward: Distance | Peg -> Hole bottom
    WEIGHT_DISTANCE_PEG_TO_HOLE_BOTTOM = 256.0
    TANH_STD_DISTANCE_PEG_TO_HOLE_BOTTOM = 0.002
    reward_distance_pegs_to_holes_bottom = WEIGHT_DISTANCE_PEG_TO_HOLE_BOTTOM * (
        1.0
        - torch.tanh(
            torch.min(torch.norm(tf_pos_pegs_ends_to_holes_bottom, dim=-1), dim=1)[0]
            / TANH_STD_DISTANCE_PEG_TO_HOLE_BOTTOM
        )
    ).sum(dim=-1)

    ##################
    ## Terminations ##
    ##################
    # No termination condition
    termination = torch.zeros(num_envs, dtype=torch.bool, device=device)
    # Truncation
    truncation = (
        episode_length >= max_episode_length
        if truncate_episodes
        else torch.zeros(num_envs, dtype=torch.bool, device=device)
    )

    return StepReturn(
        {
            "state": {
                "contact_forces_mean_robot": contact_forces_mean_robot,
                "contact_forces_mean_end_effector": contact_forces_mean_end_effector,
                "tf_pos_end_effector_to_objs": tf_pos_end_effector_to_objs,
                "tf_rot6d_end_effector_to_objs": tf_rot6d_end_effector_to_objs,
                "tf_pos_pegs_end0_to_holes_entrance": tf_pos_pegs_end0_to_holes_entrance,
                "tf_pos_pegs_end1_to_holes_entrance": tf_pos_pegs_end1_to_holes_entrance,
                "tf_pos_pegs_end0_to_holes_bottom": tf_pos_pegs_end0_to_holes_bottom,
                "tf_pos_pegs_end1_to_holes_bottom": tf_pos_pegs_end1_to_holes_bottom,
                "tf_rot6d_pegs_to_holes": tf_rot6d_pegs_to_holes,
            },
            "state_dyn": {
                "contact_forces_robot": contact_forces_robot,
                "contact_forces_end_effector": contact_forces_end_effector,
            },
            "proprio": {
                "fk_pos_end_effector": fk_pos_end_effector,
                "fk_rot6d_end_effector": fk_rot6d_end_effector,
            },
            "proprio_dyn": {
                "joint_pos_robot_normalized": joint_pos_robot_normalized,
                "joint_pos_end_effector_normalized": joint_pos_end_effector_normalized,
                "joint_acc_robot": joint_acc_robot,
                "joint_applied_torque_robot": joint_applied_torque_robot,
            },
        },
        {
            "penalty_action_rate": penalty_action_rate,
            "penalty_joint_torque": penalty_joint_torque,
            "penalty_joint_acceleration": penalty_joint_acceleration,
            "penalty_undesired_robot_contacts": penalty_undesired_robot_contacts,
            "reward_top_down_orientation": reward_top_down_orientation,
            "reward_distance_end_effector_to_objs": reward_distance_end_effector_to_objs,
            "reward_grasp": reward_grasp,
            "reward_lift": reward_lift,
            "reward_align_pegs_to_holes_primary": reward_align_pegs_to_holes_primary,
            "reward_align_pegs_to_holes_secondary": reward_align_pegs_to_holes_secondary,
            "reward_distance_pegs_to_holes_entrance_gradual": reward_distance_pegs_to_holes_entrance_gradual,
            "reward_distance_pegs_to_holes_entrance": reward_distance_pegs_to_holes_entrance,
            "reward_distance_pegs_to_holes_bottom": reward_distance_pegs_to_holes_bottom,
        },
        termination,
        truncation,
    )
