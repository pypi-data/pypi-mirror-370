import wandelbots_api_client as nova_api
import wandelbots_isaacsim_api as isaac_sim_api
from typing import cast


def to_nova_collider(
    shape: isaac_sim_api.models.Collider,
) -> nova_api.models.Collider:
    pose = nova_api.models.Pose2(
        position=[
            shape.pose.position[0].actual_instance,
            shape.pose.position[1].actual_instance,
            shape.pose.position[2].actual_instance,
        ],
        orientation=[
            shape.pose.orientation[0].actual_instance,
            shape.pose.orientation[1].actual_instance,
            shape.pose.orientation[2].actual_instance,
        ],
    )

    if isinstance(shape.shape.actual_instance, isaac_sim_api.models.Sphere):
        return nova_api.models.Collider(
            shape=nova_api.models.ColliderShape(
                nova_api.models.Sphere2(
                    radius=shape.shape.actual_instance.radius,
                    shape_type="sphere",
                )
            ),
            pose=pose,
        )
    elif isinstance(shape.shape.actual_instance, isaac_sim_api.models.Box):
        return nova_api.models.Collider(
            shape=nova_api.models.ColliderShape(
                nova_api.models.Box2(
                    size_x=shape.shape.actual_instance.size_x,
                    size_y=shape.shape.actual_instance.size_y,
                    size_z=shape.shape.actual_instance.size_z,
                    shape_type="box",
                    box_type="FULL",
                )
            ),
            pose=pose,
        )
    elif isinstance(shape.shape.actual_instance, isaac_sim_api.models.Capsule):
        return nova_api.models.Collider(
            shape=nova_api.models.ColliderShape(
                nova_api.models.Capsule2(
                    cylinder_height=shape.shape.actual_instance.height,
                    radius=shape.shape.actual_instance.radius,
                    shape_type="capsule",
                )
            ),
            pose=pose,
        )
    elif isinstance(shape.shape.actual_instance, isaac_sim_api.models.Cylinder):
        return nova_api.models.Collider(
            shape=nova_api.models.ColliderShape(
                nova_api.models.Cylinder2(
                    height=shape.shape.actual_instance.height,
                    radius=shape.shape.actual_instance.radius,
                    shape_type="cylinder",
                )
            ),
            pose=pose,
        )
    elif isinstance(shape.shape.actual_instance, isaac_sim_api.models.Plane):
        return nova_api.models.Collider(
            shape=nova_api.models.ColliderShape(
                nova_api.models.Plane2(shape_type="plane")
            ),
            pose=pose,
        )
    elif isinstance(shape.shape.actual_instance, isaac_sim_api.models.ConvexHull):
        return nova_api.models.Collider(
            shape=nova_api.models.ColliderShape(
                nova_api.models.convex_hull2.ConvexHull2(
                    shape_type="convex_hull",
                    vertices=cast(
                        isaac_sim_api.models.ConvexHull,
                        shape.shape.actual_instance,
                    ).vertices,
                )
            ),
            pose=pose,
        )
    return None


async def sweep_colliders(
    api_client: isaac_sim_api.ApiClient,
    sweep_parameters: isaac_sim_api.models.SphereSweepParameters
    | isaac_sim_api.models.BoxSweepParameters,
) -> dict[str, nova_api.models.Collider]:
    collider_api = isaac_sim_api.CollisionWorldApi(api_client)
    colliders = await collider_api.sweep_collisions(
        isaac_sim_api.models.SweepArguments(sweep_parameters)
    )
    return {shape_id: to_nova_collider(shape) for shape_id, shape in colliders.items()}
