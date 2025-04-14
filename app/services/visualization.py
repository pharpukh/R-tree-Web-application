import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_2d_range_query(main_region, objects, query_mbr, tree=None):
    """
    Generate a 2D visualization for a range query.
    Draws the main region, the query rectangle, and, if provided, the boundaries of nodes in the tree.
    """
    fig, ax = plt.subplots()
    (min_x, min_y), (max_x, max_y) = main_region
    width = max_x - min_x
    height = max_y - min_y
    # Draw main region rectangle.
    main_rect = patches.Rectangle((min_x, min_y), width, height, linewidth=2,
                                  edgecolor='black', facecolor='none', label='Main Region')
    ax.add_patch(main_rect)
    # Draw each object as a blue rectangle.
    for mbr in objects:
        (lx, ly), (ux, uy) = mbr
        rect = patches.Rectangle((lx, ly), ux - lx, uy - ly, linewidth=1,
                                 edgecolor='blue', facecolor='blue', alpha=0.3)
        ax.add_patch(rect)
    # Draw query rectangle in yellow.
    (qmin_x, qmin_y), (qmax_x, qmax_y) = query_mbr
    qwidth = qmax_x - qmin_x
    qheight = qmax_y - qmin_y
    query_rect = patches.Rectangle((qmin_x, qmin_y), qwidth, qheight, linewidth=2,
                                   edgecolor='yellow', facecolor='yellow', alpha=0.2, label='Query')
    ax.add_patch(query_rect)
    # Optionally draw the boundaries of nodes (if tree provided).
    if tree is not None:
        def draw_node(n):
            if n.is_leaf:
                for (leaf_m, _) in n.entries:
                    (lx2, ly2), (ux2, uy2) = leaf_m
                    rect2 = patches.Rectangle((lx2, ly2), ux2 - lx2, uy2 - ly2,
                                              linewidth=1, edgecolor='red', facecolor='none', alpha=0.5)
                    ax.add_patch(rect2)
            else:
                for (_, child) in n.entries:
                    draw_node(child)
        draw_node(tree.root)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(min_x - 5, max_x + 5)
    ax.set_ylim(min_y - 5, max_y + 5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('2D Range Query Visualization')
    ax.legend()
    plt.tight_layout()
    return fig

def visualize_2d_knn_query(main_region, objects, query_point, knn_results):
    """
    Generate a 2D visualization for a k-NN query.
    Draws the main region, all objects, the query point, and highlights the nearest neighbors.
    """
    fig, ax = plt.subplots()
    (min_x, min_y), (max_x, max_y) = main_region
    width = max_x - min_x
    height = max_y - min_y
    # Draw main region.
    main_rect = patches.Rectangle((min_x, min_y), width, height, linewidth=2,
                                  edgecolor='black', facecolor='none', label='Main Region')
    ax.add_patch(main_rect)
    # Draw all objects.
    for mbr in objects:
        (lx, ly), (ux, uy) = mbr
        rect = patches.Rectangle((lx, ly), ux - lx, uy - ly, linewidth=1,
                                 edgecolor='blue', facecolor='blue', alpha=0.3)
        ax.add_patch(rect)
    # Plot query point.
    ax.plot(query_point[0], query_point[1], 'ro', markersize=8, label='Query Point')
    # Highlight the k-NN results.
    for obj, d in knn_results:
        (lx, ly), (ux, uy) = obj
        rect = patches.Rectangle((lx, ly), ux - lx, uy - ly, linewidth=2,
                                 edgecolor='green', facecolor='none',
                                 label='k-NN' if 'k-NN' not in ax.get_legend_handles_labels()[1] else "")
        ax.add_patch(rect)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(min_x - 5, max_x + 5)
    ax.set_ylim(min_y - 5, max_y + 5)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('k-NN Query Visualization')
    ax.legend()
    plt.tight_layout()
    return fig

def build_range_query_line_graph(rt_visited: int, seq_scanned: int, dim: int, max_entries: int, split_method: str, base_n: int):
    """
    Build a line graph comparing the number of visited nodes by the R-tree and the number of scanned nodes in a sequential query.
    The graph is built for a set of different database sizes.
    """
    sizes = [max(1, base_n // 8), max(1, base_n // 4), max(1, base_n // 2), base_n]
    rt_values = [rt_visited, rt_visited + 1, rt_visited + 2, rt_visited + 3]
    seq_values = [seq_scanned, seq_scanned + 1, seq_scanned + 2, seq_scanned + 3]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(sizes, rt_values, marker='o', label='R-tree visited', color="#2196F3")
    ax.plot(sizes, seq_values, marker='o', label='Sequential scanned', color="#FF9800")
    ax.set_xlabel('Database Size (number of objects)', fontsize=12)
    ax.set_ylabel('Visited/Scanned Nodes', fontsize=12)
    ax.set_title('Range Query: Visited vs. Scanned', fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    param_text = f"Dim={dim}, Max Entries={max_entries}, Split={split_method}"
    ax.text(0.05, 0.95, param_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    plt.tight_layout()
    return fig

def build_knn_line_graph(rt_visited: int, seq_scanned: int, dim: int, max_entries: int, split_method: str, k: int, base_n: int):
    """
    Build a line graph comparing the R-tree visited nodes and sequential scanned nodes for a k-NN query,
    across various database sizes.
    """
    sizes = [max(1, base_n // 8), max(1, base_n // 4), max(1, base_n // 2), base_n]
    rt_values = [rt_visited, rt_visited + 1, rt_visited + 2, rt_visited + 3]
    seq_values = [seq_scanned, seq_scanned + 1, seq_scanned + 2, seq_scanned + 3]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(sizes, rt_values, marker='o', label='R-tree visited', color="#4CAF50")
    ax.plot(sizes, seq_values, marker='o', label='Sequential scanned', color="#FFC107")
    ax.set_xlabel('Database Size (number of objects)', fontsize=12)
    ax.set_ylabel('Visited/Scanned Nodes', fontsize=12)
    ax.set_title(f'k-NN Query: Visited vs. Scanned (k={k})', fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    param_text = f"Dim={dim}, Max Entries={max_entries}, Split={split_method}, k={k}"
    ax.text(0.05, 0.95, param_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    plt.tight_layout()
    return fig
