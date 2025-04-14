from app.services.r_tree import generate_random_objects, RTree, gather_leaf_objects


def get_range_query_experiment_data(db_req, query_mbr):
    """
    Conducts experiments for Range Query on the given R-tree request.
    Generates random objects for different database sizes and collects:
    - sizes: list of database sizes used in the experiment.
    - rt_visited_list: number of nodes visited by the R-tree query.
    - seq_scanned_list: number of nodes scanned by a sequential search.
    """
    n = db_req.number_of_objects
    d = db_req.dimensions
    M = db_req.max_entries
    sm = db_req.split_method
    main_min = db_req.main_region_min_coordinates
    main_max = db_req.main_region_max_coordinates
    sizes = [max(1, n // 8), max(1, n // 4), max(1, n // 2), n]
    rt_visited_list = []
    seq_scanned_list = []
    for size in sizes:
        rects = generate_random_objects(size, d, main_min, main_max)
        tree_temp = RTree(max_entries=M, dimensions=d, split_method=sm)
        for r in rects:
            tree_temp.insert(r, data=r)
        _, visited_val = tree_temp.range_query(query_mbr)
        rt_visited_list.append(visited_val)
        seq_data = gather_leaf_objects(tree_temp.root)
        seq_scanned_list.append(len(seq_data))
    return sizes, rt_visited_list, seq_scanned_list


def get_knn_experiment_data(db_req, point_coords, k):
    """
    Conducts experiments for k-NN Query on the given R-tree request.
    Generates random objects for different database sizes and collects:
    - sizes: list of database sizes used in the experiment.
    - rt_visited_list: number of nodes visited by the R-tree k-NN query.
    - seq_scanned_list: number of nodes scanned by a sequential search.
    """
    n = db_req.number_of_objects
    d = db_req.dimensions
    M = db_req.max_entries
    sm = db_req.split_method
    main_min = db_req.main_region_min_coordinates
    main_max = db_req.main_region_max_coordinates
    sizes = [max(1, n // 8), max(1, n // 4), max(1, n // 2), n]
    rt_visited_list = []
    seq_scanned_list = []
    for size in sizes:
        rects = generate_random_objects(size, d, main_min, main_max)
        tree_temp = RTree(max_entries=M, dimensions=d, split_method=sm)
        for r in rects:
            tree_temp.insert(r, data=r)
        _, visited_val = tree_temp.knn_query(tuple(point_coords), k=k)
        rt_visited_list.append(visited_val)
        seq_data = gather_leaf_objects(tree_temp.root)
        seq_scanned_list.append(len(seq_data))
    return sizes, rt_visited_list, seq_scanned_list
