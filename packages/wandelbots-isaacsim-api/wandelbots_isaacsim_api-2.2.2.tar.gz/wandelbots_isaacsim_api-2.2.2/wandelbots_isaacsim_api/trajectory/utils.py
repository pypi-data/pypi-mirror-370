from attr import dataclass
import wandelbots_isaacsim_api as isaac_sim_api
import wandelbots_api_client as nova_api


@dataclass
class TrajectoryDrawOptimization:
    min_time_delta_seconds: float = 0.5
    min_pose_distance_millimeters: float = 10.0


async def draw_joint_trajectory(
    api_client: isaac_sim_api.ApiClient,
    nova_api_client: nova_api.ApiClient,
    joint_trajectory: nova_api.models.JointTrajectory,
    cell: str,
    motion_group: str,
    tcp="Flange",
    parent_prim_path="/World",
    name="JointTrajectory",
    options: isaac_sim_api.models.TrajectoryOptions = isaac_sim_api.models.TrajectoryOptions(
        color=[255, 255, 255], width=20
    ),
    optimiation: TrajectoryDrawOptimization = TrajectoryDrawOptimization(),
    overwrite_existing=True,
) -> None:
    kinematic_api = nova_api.MotionGroupKinematicApi(nova_api_client)

    joint_trajectory = _resacle_trajectory_timeline(
        joint_trajectory, min_time_delta_seconds=optimiation.min_time_delta_seconds
    )

    poses = [
        await kinematic_api.calculate_forward_kinematic(
            cell=cell,
            motion_group=motion_group,
            tcp_pose_request=nova_api.models.TcpPoseRequest(
                motion_group=motion_group,
                tcp=tcp,
                joint_position=joint_state,
            ),
        )
        for joint_state in joint_trajectory.joint_positions
    ]
    await draw_pose_trajectory(
        api_client,
        poses=poses,
        parent_prim_path=parent_prim_path,
        name=name,
        options=options,
        overwrite_existing=overwrite_existing,
        min_pose_distance_millimeters=optimiation.min_pose_distance_millimeters,
    )


async def draw_pose_trajectory(
    api_client: isaac_sim_api.ApiClient,
    poses: list[nova_api.models.Pose],
    name="Trajectory",
    parent_prim_path="/World",
    options: isaac_sim_api.models.TrajectoryOptions = isaac_sim_api.models.TrajectoryOptions(
        color=[255, 255, 255], width=20
    ),
    overwrite_existing=True,
    min_pose_distance_millimeters=10.0,
) -> None:
    trajectory_api = isaac_sim_api.TrajectoryApi(api_client)
    update_trajectory = False

    poses = _reduce_pose_overlap(poses, min_pose_distance_millimeters)

    poses = [
        [
            pose.position.x,
            pose.position.y,
            pose.position.z,
            pose.orientation.x,
            pose.orientation.y,
            pose.orientation.z,
        ]
        for pose in poses
    ]

    if overwrite_existing:
        update_trajectory = f"{parent_prim_path}/{name}" in [
            f"{parent_prim_path}/{trajectory.name}"
            for trajectory in await trajectory_api.list_trajectories()
        ]

    if update_trajectory:
        await trajectory_api.update_trajectory(
            name=name,
            patch_trajectory_data=isaac_sim_api.models.PatchTrajectoryData(
                poses=poses,
                options=options,
            ),
        )
    else:
        await trajectory_api.create_trajectory(
            isaac_sim_api.models.TrajectoryData(
                name=name,
                parent_prim_path=parent_prim_path,
                poses=poses,
                options=options,
            )
        )


def _resacle_trajectory_timeline(
    trajectory: nova_api.models.JointTrajectory, min_time_delta_seconds=0.5
) -> nova_api.models.JointTrajectory:
    time_rescaled_trajectory = nova_api.models.JointTrajectory(
        joint_positions=[], times=[], locations=[]
    )
    last_time = 0.0
    last_index = -1
    for time_idx, time in enumerate(trajectory.times):
        # Do not skip starting point
        if time < last_time + min_time_delta_seconds and time_idx != 0:
            continue
        time_rescaled_trajectory.joint_positions.append(
            trajectory.joint_positions[time_idx]
        )
        time_rescaled_trajectory.times.append(time)
        time_rescaled_trajectory.locations.append(trajectory.locations[time_idx])
        last_time += min_time_delta_seconds

    # do not forget to add the last point if it was not added
    # its the most noticeable point if removed
    if last_index != len(trajectory.times):
        time_rescaled_trajectory.joint_positions.append(trajectory.joint_positions[-1])
        time_rescaled_trajectory.times.append(trajectory.times[-1])
        time_rescaled_trajectory.locations.append(trajectory.locations[-1])
    return time_rescaled_trajectory


def _reduce_pose_overlap(
    poses: list[nova_api.models.Pose], min_pose_distance_millimeters=10.0
) -> list[nova_api.models.Pose]:
    if len(poses) < 2:
        return poses
    last_point = poses[0]

    reduced_poses = [last_point]
    for pose in poses[1:]:
        distance = (
            (pose.position.x - last_point.position.x) ** 2
            + (pose.position.y - last_point.position.y) ** 2
            + (pose.position.z - last_point.position.z) ** 2
        ) ** 0.5
        if distance >= min_pose_distance_millimeters:
            reduced_poses.append(pose)
            last_point = pose
    return reduced_poses
