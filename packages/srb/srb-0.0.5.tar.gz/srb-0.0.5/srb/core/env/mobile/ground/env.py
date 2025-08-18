from dataclasses import MISSING

import torch

from srb import assets
from srb.core.action import WheeledDriveAction
from srb.core.asset import AssetVariant, GroundRobot
from srb.core.env import ViewerCfg
from srb.core.env.mobile.env import (
    MobileEnv,
    MobileEnvCfg,
    MobileEventCfg,
    MobileSceneCfg,
)
from srb.core.manager import EventTermCfg, SceneEntityCfg
from srb.core.mdp import reset_root_state_uniform
from srb.utils.cfg import configclass
from srb.utils.math import deg_to_rad


@configclass
class GroundSceneCfg(MobileSceneCfg):
    env_spacing: float = 32.0


@configclass
class GroundEventCfg(MobileEventCfg):
    randomize_robot_state: EventTermCfg = EventTermCfg(
        func=reset_root_state_uniform,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot"),
            "pose_range": {
                "x": (-0.5, 0.5),
                "y": (-0.5, 0.5),
                "z": (0.4, 0.6),
                "yaw": (-torch.pi, torch.pi),
            },
            "velocity_range": {
                "x": (-0.5, 0.5),
                "y": (-0.5, 0.5),
                "z": (0.0, 0.5),
                "roll": (-deg_to_rad(5.0), deg_to_rad(5.0)),
                "pitch": (-deg_to_rad(5.0), deg_to_rad(5.0)),
                "yaw": (-deg_to_rad(15.0), deg_to_rad(15.0)),
            },
        },
    )


@configclass
class GroundEnvCfg(MobileEnvCfg):
    ## Assets
    robot: GroundRobot | AssetVariant = assets.Perseverance()
    _robot: GroundRobot = MISSING  # type: ignore

    ## Scene
    scene: GroundSceneCfg = GroundSceneCfg()

    ## Events
    events: GroundEventCfg = GroundEventCfg()

    ## Time
    env_rate: float = 1.0 / 50.0
    agent_rate: float = 1.0 / 25.0

    ## Viewer
    viewer: ViewerCfg = ViewerCfg(
        eye=(7.5, -7.5, 15.0), lookat=(0.0, 0.0, 0.0), origin_type="env"
    )

    def __post_init__(self):
        super().__post_init__()


class GroundEnv(MobileEnv):
    cfg: GroundEnvCfg

    def __init__(self, cfg: GroundEnvCfg, **kwargs):
        super().__init__(cfg, **kwargs)

        ## Check if the robot uses a wheeled drive action term
        self._wheeled_drive_action_term_key = next(
            filter(
                lambda term_key: isinstance(
                    self.action_manager._terms[term_key], WheeledDriveAction
                ),
                self.action_manager._terms.keys(),
            ),
            None,
        )
