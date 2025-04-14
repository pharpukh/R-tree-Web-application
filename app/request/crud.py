import json
import pickle
import io
import base64
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.request.models import UserRequest
from app.request.schemas import RequestCreate, RequestOutFull
from app.services.r_tree import build_rtree, gather_leaf_objects, generate_random_objects, RTree
from app.services.visualization import (
    visualize_2d_range_query,
    visualize_2d_knn_query,
    build_range_query_line_graph,
    build_knn_line_graph
)
from app.services.queries import get_range_query_experiment_data, get_knn_experiment_data


async def create_request(db: AsyncSession, user_id: int, req_in: RequestCreate) -> UserRequest:
    """
    Create a new R-tree request based on the input schema.
    Builds the R-tree using provided parameters, serializes it, and saves to the database.
    """
    db_request = UserRequest(
        user_id=user_id,
        number_of_objects=req_in.number_of_objects,
        dimensions=req_in.dimensions,
        max_entries=req_in.max_entries,
        split_method=req_in.split_method,
        main_region_min_coordinates=req_in.main_region_min_coordinates,
        main_region_max_coordinates=req_in.main_region_max_coordinates
    )
    r_tree = build_rtree(
        num_objects=req_in.number_of_objects,
        dimensions=req_in.dimensions,
        max_entries=req_in.max_entries,
        split_method=req_in.split_method,
        main_region_min=req_in.main_region_min_coordinates,
        main_region_max=req_in.main_region_max_coordinates
    )
    db_request.r_tree_data = pickle.dumps(r_tree)
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    return db_request


async def import_request(db: AsyncSession, user_id: int, file_data: bytes) -> UserRequest:
    """
    Import an R-tree from a provided pickle file.
    Unpickles the tree, extracts its parameters, and saves a new UserRequest with these parameters.
    """
    r_tree = pickle.loads(file_data)
    number_of_objects = len(gather_leaf_objects(r_tree.root))
    dimensions = r_tree.dimensions
    max_entries = r_tree.max_entries
    split_method = r_tree.split_method
    mbr = r_tree._calc_node_mbr(r_tree.root)
    main_region_min_coordinates = [int(x) for x in mbr[0]]
    main_region_max_coordinates = [int(x) for x in mbr[1]]
    db_request = UserRequest(
        user_id=user_id,
        number_of_objects=number_of_objects,
        dimensions=dimensions,
        max_entries=max_entries,
        split_method=split_method,
        main_region_min_coordinates=main_region_min_coordinates,
        main_region_max_coordinates=main_region_max_coordinates
    )
    db_request.r_tree_data = file_data
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    return db_request


async def get_requests_by_user(db: AsyncSession, user_id: int):
    """
    Retrieve all R-tree requests created by a specific user.
    """
    result = await db.execute(select(UserRequest).where(UserRequest.user_id == user_id))
    return result.scalars().all()


async def delete_request_crud(db: AsyncSession, user_id: int, request_id: int) -> dict:
    """
    Delete a specific R-tree request if it belongs to the given user.
    """
    db_req = await db.get(UserRequest, request_id)
    if not db_req or db_req.user_id != user_id:
        raise Exception("Request not found")
    await db.delete(db_req)
    await db.commit()
    return {"detail": "Request deleted"}


async def get_request_detail_crud(db: AsyncSession, user_id: int, request_id: int) -> RequestOutFull:
    """
    Retrieve detailed information about an R-tree request including a generated 2D visualization (if dimensions == 2).
    """
    db_req = await db.get(UserRequest, request_id)
    if not db_req or db_req.user_id != user_id:
        raise Exception("Request not found")
    image_base64 = None
    if db_req.r_tree_data and db_req.dimensions == 2:
        r_tree = pickle.loads(db_req.r_tree_data)
        leafs = gather_leaf_objects(r_tree.root)
        fig, ax = plt.subplots()
        (min_x, min_y) = db_req.main_region_min_coordinates
        (max_x, max_y) = db_req.main_region_max_coordinates
        width = max_x - min_x
        height = max_y - min_y
        main_rect = patches.Rectangle((min_x, min_y), width, height,
                                      linewidth=2, edgecolor='black',
                                      facecolor='none', label='Main Region')
        ax.add_patch(main_rect)
        for (mbr, _) in leafs:
            (lx, ly), (ux, uy) = mbr
            rect = patches.Rectangle(
                (lx, ly), ux - lx, uy - ly,
                linewidth=1, edgecolor='blue', facecolor='blue', alpha=0.3
            )
            ax.add_patch(rect)
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlim(min_x - 5, max_x + 5)
        ax.set_ylim(min_y - 5, max_y + 5)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'R-Tree for Request #{db_req.id}')
        ax.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return RequestOutFull(
        id=db_req.id,
        number_of_objects=db_req.number_of_objects,
        dimensions=db_req.dimensions,
        max_entries=db_req.max_entries,
        split_method=db_req.split_method,
        main_region_min_coordinates=db_req.main_region_min_coordinates,
        main_region_max_coordinates=db_req.main_region_max_coordinates,
        created_at=db_req.created_at,
        image_base64=image_base64
    )


async def range_query_request(db: AsyncSession, user_id: int, request_id: int, query_params: dict) -> dict:
    """
    Processes a range query for a given R-tree request.
    Executes the query, collects experiment data, builds a comparison graph and 2D visualization (if applicable),
    and returns the results.
    """
    db_req = await db.get(UserRequest, request_id)
    if not db_req or db_req.user_id != user_id:
        raise Exception("Request not found")
    if not db_req.r_tree_data:
        raise Exception("No tree data")
    r_tree = pickle.loads(db_req.r_tree_data)
    query_mbr = (tuple(query_params.get("min")), tuple(query_params.get("max")))
    results, visited = r_tree.range_query(query_mbr)
    found_objects = [obj for obj in results]
    sizes, rt_list, seq_list = get_range_query_experiment_data(db_req, query_mbr)
    fig_line = build_range_query_line_graph(rt_list[-1], seq_list[-1],
                                            db_req.dimensions, db_req.max_entries,
                                            db_req.split_method, db_req.number_of_objects)
    buf_line = io.BytesIO()
    fig_line.savefig(buf_line, format="png")
    plt.close(fig_line)
    graph_b64 = base64.b64encode(buf_line.getvalue()).decode("utf-8")
    visualization_b64 = None
    if db_req.dimensions == 2:
        all_leafs = [m for (m, _) in gather_leaf_objects(r_tree.root)]
        fig_vis = visualize_2d_range_query(
            (tuple(db_req.main_region_min_coordinates), tuple(db_req.main_region_max_coordinates)),
            all_leafs,
            query_mbr,
            tree=r_tree
        )
        buf_vis = io.BytesIO()
        fig_vis.savefig(buf_vis, format="png")
        plt.close(fig_vis)
        visualization_b64 = base64.b64encode(buf_vis.getvalue()).decode("utf-8")
    return {
        "objects": found_objects,
        "visited": visited,
        "graph": graph_b64,
        "visualization": visualization_b64
    }


async def knn_query_request(db: AsyncSession, user_id: int, request_id: int, query_params: dict) -> dict:
    """
    Processes a k-NN query for a given R-tree request.
    Executes the query, collects experiment data, builds a comparison graph and 2D visualization (if applicable),
    and returns the results along with the distances.
    """
    db_req = await db.get(UserRequest, request_id)
    if not db_req or db_req.user_id != user_id:
        raise Exception("Request not found")
    if not db_req.r_tree_data:
        raise Exception("No tree data")
    r_tree = pickle.loads(db_req.r_tree_data)
    point_coords = query_params.get("point")
    k = query_params.get("k")
    results, visited = r_tree.knn_query(tuple(point_coords), k=k)
    found_objects = []
    distances = []
    for obj, dist in results:
        found_objects.append(obj)
        distances.append(dist)
    sizes, rt_list, seq_list = get_knn_experiment_data(db_req, point_coords, k)
    fig_line = build_knn_line_graph(rt_list[-1], seq_list[-1],
                                    db_req.dimensions, db_req.max_entries,
                                    db_req.split_method, k, db_req.number_of_objects)
    buf_line = io.BytesIO()
    fig_line.savefig(buf_line, format="png")
    plt.close(fig_line)
    graph_b64 = base64.b64encode(buf_line.getvalue()).decode("utf-8")
    visualization_b64 = None
    if db_req.dimensions == 2:
        fig_vis = visualize_2d_knn_query(
            (tuple(db_req.main_region_min_coordinates), tuple(db_req.main_region_max_coordinates)),
            [m for (m, _) in gather_leaf_objects(r_tree.root)],
            point_coords,
            results
        )
        buf_vis = io.BytesIO()
        fig_vis.savefig(buf_vis, format="png")
        plt.close(fig_vis)
        visualization_b64 = base64.b64encode(buf_vis.getvalue()).decode("utf-8")
    return {
        "objects": found_objects,
        "distances": distances,
        "visited": visited,
        "graph": graph_b64,
        "visualization": visualization_b64
    }
