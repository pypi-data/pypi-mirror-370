from typing import Sequence
from nova import Nova
from attr import dataclass
import wandelbots_isaacsim_api as isaac_sim_api
import wandelbots_api_client as nova_api
from nova.viewers import Viewer, manager as viewer_manager
from nova.actions import Action
import nova.core.motion_group
import os
from . import utils as trajectory_utils
from nova.core.exceptions import PlanTrajectoryFailed


@dataclass
class TrajectoryPlanResultConfiguration:
    parent_prim_path: str = "/World"
    name: str = "PlannedTrajectory"
    options: isaac_sim_api.models.TrajectoryOptions = (
        isaac_sim_api.models.TrajectoryOptions(color=[255, 255, 255], width=20),
    )
    optimization: trajectory_utils.TrajectoryDrawOptimization = (
        trajectory_utils.TrajectoryDrawOptimization()
    )


class TrajectoryViewer(Viewer):
    """Viewer for visualizing trajectories in Omniverse."""

    def __init__(
        self,
        omniverse_host: str = None,
        trajectory_success=TrajectoryPlanResultConfiguration(name="PlannedTrajectory"),
        trajectory_failure=TrajectoryPlanResultConfiguration(
            name="PlannedTrajectoryFailed",
            options=isaac_sim_api.models.TrajectoryOptions(color=[255, 0, 0], width=20),
        ),
    ) -> None:
        """Initialize viewer.

        Args:
            omniverse_host (str, optional): Custom host to omniverse. If None OMNIVERSE_HOST env variable will be used. Defaults to None.
            trajectory_success (_type_, optional): Settings of success callback.
            trajectory_failure (_type_, optional): Settings of failure callback.
        """

        viewer_manager.register_viewer(self)
        self._omniverse_host = omniverse_host

        self.trajectory_success = trajectory_success
        self.trajectory_failure = trajectory_failure

    def configure(self, nova: Nova) -> None:
        """Configure the viewer with the Nova instance."""
        self.nova = nova

    def cleanup(self) -> None:
        """Clean up the viewer resources."""
        pass

    async def log_planning_success(
        self,
        actions: Sequence[Action],
        trajectory: nova_api.models.JointTrajectory,
        tcp: str,
        motion_group: nova.core.motion_group.MotionGroup,
    ) -> None:
        host = self._omniverse_host or os.getenv("OMNIVERSE_HOST")
        async with isaac_sim_api.ApiClient(
            isaac_sim_api.Configuration(host=host)
        ) as isaac_sim_api_client:
            await trajectory_utils.draw_joint_trajectory(
                api_client=isaac_sim_api_client,
                nova_api_client=self.nova._api_client._api_client,
                joint_trajectory=trajectory,
                cell=motion_group._cell,
                motion_group=motion_group.motion_group_id,
                tcp=tcp,
                parent_prim_path=self.trajectory_success.parent_prim_path,
                name=self.trajectory_success.name,
                options=self.trajectory_success.options,
                optimiation=self.trajectory_success.optimization,
                overwrite_existing=True,
            )

    async def log_planning_failure(
        self,
        actions: Sequence[Action],
        error: Exception,
        tcp: str,
        motion_group: nova.core.motion_group.MotionGroup,
    ) -> None:
        if not isinstance(error, PlanTrajectoryFailed):
            return
        host = self._omniverse_host or os.getenv("OMNIVERSE_HOST")

        async with isaac_sim_api.ApiClient(
            isaac_sim_api.Configuration(host=host)
        ) as omniservice_api_client:
            await trajectory_utils.draw_joint_trajectory(
                api_client=omniservice_api_client,
                nova_api_client=self.nova._api_client._api_client,
                joint_trajectory=error.error.joint_trajectory,
                cell=motion_group._cell,
                motion_group=motion_group.motion_group_id,
                tcp=tcp,
                parent_prim_path=self.trajectory_failure.parent_prim_path,
                name=self.trajectory_failure.name,
                options=self.trajectory_failure.options,
                optimiation=self.trajectory_failure.optimization,
                overwrite_existing=True,
            )
