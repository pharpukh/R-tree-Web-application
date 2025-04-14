import math
import pickle
import random
import heapq
import itertools


def build_rtree(num_objects, dimensions, max_entries, split_method, main_region_min, main_region_max):
    """
    Build an R-tree by generating random objects within the specified region and inserting them into the tree.
    """
    rects = generate_random_objects(num_objects, dimensions, main_region_min, main_region_max)
    tree = RTree(max_entries=max_entries, dimensions=dimensions, split_method=split_method)
    for r in rects:
        tree.insert(r, data=r)
    return tree


def overlaps(mbr1, mbr2):
    """
    Check if two Minimum Bounding Rectangles (MBRs) overlap.
    """
    min1, max1 = mbr1
    min2, max2 = mbr2
    for i in range(len(min1)):
        if min1[i] > max2[i] or min2[i] > max1[i]:
            return False
    return True


def combine_mbr(mbr1, mbr2):
    """
    Combine two MBRs into the minimal bounding rectangle that contains both.
    """
    min1, max1 = mbr1
    min2, max2 = mbr2
    new_min = tuple(min(min1[i], min2[i]) for i in range(len(min1)))
    new_max = tuple(max(max1[i], max2[i]) for i in range(len(max1)))
    return (new_min, new_max)


def area(mbr):
    """
    Compute the area (or hypervolume) of the MBR.
    """
    min_pt, max_pt = mbr
    vol = 1
    for i in range(len(min_pt)):
        vol *= (max_pt[i] - min_pt[i])
    return vol


def mindist_point_to_mbr(point, mbr):
    """
    Compute the squared Euclidean distance from a point to the MBR.
    """
    min_pt, max_pt = mbr
    d2 = 0
    for i, coord in enumerate(point):
        if coord < min_pt[i]:
            d2 += (min_pt[i] - coord) ** 2
        elif coord > max_pt[i]:
            d2 += (coord - max_pt[i]) ** 2
    return d2


class Node:
    """
    Represents a node in the R-tree. Leaf nodes store (MBR, data) pairs,
    while internal nodes store (MBR, child_node) pairs.
    """

    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.entries = []

    def __repr__(self):
        typ = "Leaf" if self.is_leaf else "Node"
        return f"<{typ} entries={len(self.entries)}>"


class RTree:
    """
    RTree data structure for spatial indexing.
    """

    def __init__(self, max_entries=4, min_entries=None, dimensions=2, split_method='quadratic'):
        self.max_entries = max_entries
        self.min_entries = min_entries if min_entries is not None else max(2, max_entries // 2)
        self.dimensions = dimensions
        self.split_method = split_method  # 'quadratic' or 'linear'
        self.root = Node(is_leaf=True)

    def insert(self, mbr, data=None):
        """
        Insert a new object with its MBR into the R-tree.
        """
        if data is None:
            data = mbr
        new_entry = (mbr, data)
        path = []
        node = self.root
        # Traverse the tree to find a leaf node for insertion.
        while not node.is_leaf:
            best_index = None
            best_increase = None
            best_area = None
            for i, (child_mbr, child_node) in enumerate(node.entries):
                current_area = area(child_mbr)
                new_area = area(combine_mbr(child_mbr, mbr))
                increase = new_area - current_area
                if best_increase is None or increase < best_increase or (
                        increase == best_increase and current_area < best_area):
                    best_index = i
                    best_increase = increase
                    best_area = current_area
            parent = node
            node = parent.entries[best_index][1]
            path.append((parent, best_index))
        node.entries.append(new_entry)
        split_node = node
        # Handle node overflow by splitting.
        while split_node is not None and len(split_node.entries) > self.max_entries:
            new_node = self._split_node(split_node)
            if not path:
                new_root = Node(is_leaf=False)
                mbr1 = self._calc_node_mbr(split_node)
                mbr2 = self._calc_node_mbr(new_node)
                new_root.entries = [(mbr1, split_node), (mbr2, new_node)]
                self.root = new_root
                split_node = None
            else:
                parent, idx = path.pop()
                parent.entries[idx] = (self._calc_node_mbr(split_node), split_node)
                parent.entries.append((self._calc_node_mbr(new_node), new_node))
                split_node = parent
        for (parent, idx) in path:
            child_node = parent.entries[idx][1]
            parent.entries[idx] = (self._calc_node_mbr(child_node), child_node)

    def _calc_node_mbr(self, node):
        """
        Calculate the minimal bounding rectangle (MBR) of a node by combining MBRs of its entries.
        """
        if not node.entries:
            return None
        current = node.entries[0][0]
        for i in range(1, len(node.entries)):
            current = combine_mbr(current, node.entries[i][0])
        return current

    def _split_node(self, node):
        """
        Split a node using the chosen splitting method.
        """
        if self.split_method == 'quadratic':
            return self._quadratic_split(node)
        else:
            return self._linear_split(node)

    def _quadratic_split(self, node):
        """
        Split node using quadratic split algorithm.
        """
        entries = node.entries
        if len(entries) < 2:
            return Node(is_leaf=node.is_leaf)
        best_pair = None
        best_waste = -1
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                mbr1, _ = entries[i]
                mbr2, _ = entries[j]
                combined = combine_mbr(mbr1, mbr2)
                waste = area(combined) - area(mbr1) - area(mbr2)
                if waste > best_waste:
                    best_waste = waste
                    best_pair = (i, j)
        if best_pair is None:
            best_pair = (0, 1)
        i, j = best_pair
        group1 = [entries[i]]
        group2 = [entries[j]]
        mbr1 = entries[i][0]
        mbr2 = entries[j][0]
        remaining = [e for k, e in enumerate(entries) if k not in (i, j)]
        while remaining:
            if len(group1) + len(remaining) == self.min_entries:
                group1.extend(remaining)
                break
            if len(group2) + len(remaining) == self.min_entries:
                group2.extend(remaining)
                break
            best_diff = -1
            chosen_entry = None
            chosen_group = None
            for e in remaining:
                cand = e[0]
                new_mbr1 = combine_mbr(mbr1, cand)
                new_mbr2 = combine_mbr(mbr2, cand)
                inc1 = area(new_mbr1) - area(mbr1)
                inc2 = area(new_mbr2) - area(mbr2)
                diff = abs(inc1 - inc2)
                if diff > best_diff:
                    best_diff = diff
                    if inc1 < inc2:
                        chosen_group = 1
                        chosen_entry = e
                    else:
                        chosen_group = 2
                        chosen_entry = e
            remaining.remove(chosen_entry)
            if chosen_group == 1:
                group1.append(chosen_entry)
                mbr1 = combine_mbr(mbr1, chosen_entry[0])
            else:
                group2.append(chosen_entry)
                mbr2 = combine_mbr(mbr2, chosen_entry[0])
        node.entries = group1
        new_node = Node(is_leaf=node.is_leaf)
        new_node.entries = group2
        return new_node

    def _linear_split(self, node):
        """
        Split node using linear split algorithm.
        """
        entries = node.entries
        d = self.dimensions
        best_sep = -1
        best_low_idx = None
        best_high_idx = None
        for dim in range(d):
            low_min = float('inf')
            high_max = -float('inf')
            low_idx = None
            high_idx = None
            for i, (m, _) in enumerate(entries):
                if m[0][dim] < low_min:
                    low_min = m[0][dim]
                    low_idx = i
                if m[1][dim] > high_max:
                    high_max = m[1][dim]
                    high_idx = i
            sep = high_max - low_min
            if sep > best_sep:
                best_sep = sep
                best_low_idx = low_idx
                best_high_idx = high_idx
        if best_low_idx == best_high_idx:
            best_high_idx = (best_low_idx + 1) % len(entries)
        group1 = [entries[best_low_idx]]
        group2 = [entries[best_high_idx]]
        mbr1 = group1[0][0]
        mbr2 = group2[0][0]
        remaining = [e for i, e in enumerate(entries) if i not in (best_low_idx, best_high_idx)]
        for e in remaining:
            cand = e[0]
            new_mbr1 = combine_mbr(mbr1, cand)
            new_mbr2 = combine_mbr(mbr2, cand)
            inc1 = area(new_mbr1) - area(mbr1)
            inc2 = area(new_mbr2) - area(mbr2)
            if inc1 < inc2:
                group1.append(e)
                mbr1 = combine_mbr(mbr1, cand)
            else:
                group2.append(e)
                mbr2 = combine_mbr(mbr2, cand)
        node.entries = group1
        new_node = Node(is_leaf=node.is_leaf)
        new_node.entries = group2
        return new_node

    def range_query(self, query_mbr):
        """
        Perform a range query: return all data whose MBRs overlap with the query_mbr.
        Also returns the number of nodes visited during the search.
        """
        results = []
        visited = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            visited += 1
            if node.is_leaf:
                for m, data in node.entries:
                    if overlaps(m, query_mbr):
                        results.append(data)
            else:
                for (child_m, child_node) in node.entries:
                    if overlaps(child_m, query_mbr):
                        stack.append(child_node)
        return results, visited

    def knn_query(self, point, k=1):
        """
        Perform a k-Nearest Neighbors query: return the k nearest data objects to the given point.
        Uses a best-first search with a priority queue.
        Returns the list of (data, distance) pairs and the number of nodes visited.
        """
        counter = itertools.count()
        q = []
        visited = 1
        if self.root.is_leaf:
            for m, data in self.root.entries:
                d = math.sqrt(mindist_point_to_mbr(point, m))
                heapq.heappush(q, (d, next(counter), data, True))
        else:
            for (m, child) in self.root.entries:
                d = math.sqrt(mindist_point_to_mbr(point, m))
                heapq.heappush(q, (d, next(counter), child, False))
        result = []
        best_dist = float('inf')
        while q:
            d, _, item, is_data = heapq.heappop(q)
            if is_data:
                result.append((item, d))
                if len(result) == k:
                    result.sort(key=lambda x: x[1])
                    best_dist = result[-1][1]
                elif len(result) > k:
                    result.sort(key=lambda x: x[1])
                    result = result[:k]
                    best_dist = result[-1][1]
                if len(result) >= k:
                    if not q or q[0][0] >= best_dist:
                        break
            else:
                node = item
                visited += 1
                if node.is_leaf:
                    for m, data in node.entries:
                        d_new = math.sqrt(mindist_point_to_mbr(point, m))
                        if len(result) >= k and d_new >= best_dist:
                            continue
                        heapq.heappush(q, (d_new, next(counter), data, True))
                else:
                    for (m, child) in node.entries:
                        d_new = math.sqrt(mindist_point_to_mbr(point, m))
                        if len(result) >= k and d_new >= best_dist:
                            continue
                        heapq.heappush(q, (d_new, next(counter), child, False))
                if len(result) >= k:
                    if not q or q[0][0] >= best_dist:
                        break
        result.sort(key=lambda x: x[1])
        return result, visited


def gather_leaf_objects(node):
    """
    Recursively collects and returns all leaf entries from the given node.
    """
    if node.is_leaf:
        return node.entries[:]
    else:
        result = []
        for (m, child) in node.entries:
            result.extend(gather_leaf_objects(child))
        return result


def generate_random_objects(num_objects, dimensions, main_min, main_max):
    """
    Generate a list of random objects represented as MBRs (minimum and maximum coordinates)
    within the given main region.
    """
    objs = []
    for _ in range(num_objects):
        lower = []
        upper = []
        for d in range(dimensions):
            x1 = random.uniform(main_min[d], main_max[d])
            x2 = random.uniform(main_min[d], main_max[d])
            lower.append(min(x1, x2))
            upper.append(max(x1, x2))
        mbr = (tuple(lower), tuple(upper))
        objs.append(mbr)
    return objs
