import asyncio
import math
from pathlib import Path
import osmnx as ox
from osmnx import graph as ox_graph
from osmnx import distance as ox_distance
import networkx as nx
from pyrosm import OSM
import numpy as np
import pandas as pd
from geopy.distance import geodesic
from collections.abc import Callable
from typing import List, Dict, Optional, Any, Union
from navconfig import BASE_DIR
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from shapely.geometry import Polygon
from scipy.spatial.distance import pdist, squareform
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.neighbors import BallTree
from .flow import FlowComponent
from ..exceptions import DataNotFound, ConfigError, ComponentError


# -----------------------------
# Utility Functions
# -----------------------------
def meters_to_miles(m):
    return m * 0.000621371


def miles_to_radians(miles):
    earth_radius_km = 6371.0087714150598
    km_per_mi = 1.609344
    return miles / (earth_radius_km * km_per_mi)

def degrees_to_radians(row):
    lat = np.deg2rad(row[0])
    lon = np.deg2rad(row[1])

    return lat, lon


def radians_to_miles(rad):
    # Options here: https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    earth_radius = 6371.0087714150598
    mi_per_km = 0.62137119

    return rad * earth_radius * mi_per_km


def create_data_model(distance_matrix, num_vehicles, depot=0, max_distance=150, max_stores_per_vehicle=3):
    """Stores the data for the VRP problem."""
    data = {}
    data['distance_matrix'] = distance_matrix  # 2D list or numpy array
    data['num_vehicles'] = num_vehicles
    data['depot'] = depot
    data['max_distance'] = max_distance
    data['max_stores_per_vehicle'] = max_stores_per_vehicle
    return data


def solve_vrp(data):
    """Solves the VRP problem using OR-Tools and returns the routes."""
    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'], data['depot']
    )

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(data['distance_matrix'][from_node][to_node] * 1000)  # Convert to integer

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        int(data['max_distance'] * 1000),  # maximum distance per vehicle
        True,  # start cumul to zero
        'Distance')
    distance_dimension = routing.GetDimensionOrDie('Distance')
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Add Constraint: Maximum number of stores per vehicle
    def demand_callback(from_index):
        """Returns the demand of the node."""
        return 1  # Each store is a demand of 1

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [data['max_stores_per_vehicle']] * data['num_vehicles'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    # If no solution found, return empty routes
    if not solution:
        print("No solution found!")
        return []

    # Extract routes
    routes = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        routes.append(route)
    return routes


def print_routes(routes, store_ids):
    """Prints the routes in a readable format."""
    for i, route in enumerate(routes):
        print(f"Route for ghost employee {i+1}:")
        # Exclude depot if it's part of the route
        route_store_ids = [store_ids[node] for node in route if store_ids[node] != store_ids[route[0]]]
        print(" -> ".join(map(str, route_store_ids)))
        print()


class MarketClustering(FlowComponent):
    """
    Offline clustering of stores using BallTree+DBSCAN (in miles or km),
    then generating a fixed number of ghost employees for each cluster,
    refining if store-to-ghost distance > threshold,
    and optionally checking daily route constraints.

    Steps:
        1) Clustering with DBSCAN (haversine + approximate).
        2) Create ghost employees at cluster centroid (random offset).
        3) Remove 'unreachable' stores if no ghost employee can reach them within a threshold (e.g. 25 miles).
        4) Check if a single ghost can cover up to `max_stores_per_day` in a route < `day_hours` or `max_distance_by_day`.
            If not, we mark that store as 'rejected' too.
        5) Return two DataFrames: final assignment + rejected stores.


    Parameters:
        cluster_radius (default: 150.0)

        Purpose: Controls the search radius for the BallTree clustering algorithm
        Usage: Converted to radians and used in tree.query_radius() to find nearby stores during cluster formation
        Effect: Determines how far apart stores can be and still be considered for the same cluster during the initial clustering phase
        Location: Used in _create_cluster() method

        max_cluster_distance (default: 50.0)

        Purpose: Controls outlier detection within already-formed clusters
        Usage: Used in _detect_outliers() to check if stores are too far from their cluster's centroid
        Effect: Stores farther than this distance from their cluster center get marked as outliers
        Location: Used in validation after clusters are formed

    """  # noqa

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        # DBSCAN config
        self.max_cluster_distance = kwargs.pop('max_cluster_distance', 50.0)
        self.cluster_radius = kwargs.pop('cluster_radius', 150.0)
        self.max_cluster_size: int = kwargs.pop('max_cluster_size', 25)  # number of items in cluster
        self.min_cluster_size: int = kwargs.pop('min_cluster_size', 5)  # minimum number of items in cluster
        self.rejected_stores_file: Path = kwargs.pop('rejected_stores', None)
        self.distance_unit = kwargs.pop('distance_unit', 'miles')  # or 'km'
        self.min_samples = kwargs.pop('min_samples', 1)
        self._cluster_id: str = kwargs.pop('cluster_id', 'market_id')
        self._cluster_name: str = kwargs.pop('cluster_name', 'market')
        # degrees around min/max lat/lon
        self.buffer_deg = kwargs.pop('buffer_deg', 0.01)
        # OSMnx config
        self.custom_filter = kwargs.get(
            "custom_filter",
            '["highway"~"motorway|trunk|primary|secondary|tertiary"]'
        )
        self.network_type = kwargs.get("network_type", "drive")
        # Ghost employees config
        self.num_ghosts_per_cluster = kwargs.pop('num_ghosts_per_cluster', 2)
        self.ghost_distance_threshold = kwargs.pop('ghost_distance_threshold', 50.0)
        # e.g. 25 miles or km to consider a store "reachable" from that ghost
        self.reassignment_threshold_factor = kwargs.pop(
            'reassignment_threshold_factor', 0.5
        )  # 50% of max_cluster_distance
        # Default 20% of max_cluster_size
        self.max_reassignment_percentage = kwargs.pop('max_reassignment_percentage', 0.2)
        # Daily route constraints
        self.max_stores_per_day = kwargs.pop('max_stores_per_day', 3)
        self.day_hours = kwargs.pop('day_hours', 8.0)
        self.max_distance_by_day = kwargs.pop('max_distance_by_day', 150.0)
        # e.g. 150 miles, or if using km, adapt accordingly

        # Refinement with OSMnx route-based distances?
        self.borderline_threshold = kwargs.pop('borderline_threshold', 2.5)
        # max force distance to assign a rejected store to the nearest market:
        self._max_force_assign_distance = kwargs.pop('max_assign_distance', 50)
        # bounding box or place
        self.bounding_box = kwargs.pop('bounding_box', None)
        self.place_name = kwargs.pop('place_name', None)

        # Internals
        self._data: pd.DataFrame = pd.DataFrame()
        self._result: Optional[pd.DataFrame] = None
        self._rejected: pd.DataFrame = pd.DataFrame()  # for stores that get dropped
        self._ghosts: List[Dict[str, Any]] = []
        self._graphs: dict = {}
        self._cluster_centroids: Dict[int, Dict[str, float]] = {}  # Store cluster centroids
        super().__init__(loop=loop, job=job, stat=stat, **kwargs)
        self._outlier_stores: set = set()  # Track stores that were marked as outliers

    async def start(self, **kwargs):
        """Validate input DataFrame and columns."""
        if self.previous:
            self._data = self.input
            if not isinstance(self._data, pd.DataFrame):
                raise ConfigError("Incompatible input: Must be a Pandas DataFrame.")
        else:
            raise DataNotFound("No input DataFrame found.")

        required_cols = {'store_id', 'latitude', 'longitude'}
        missing = required_cols - set(self._data.columns)
        if missing:
            raise ComponentError(f"DataFrame missing required columns: {missing}")

        return True

    async def close(self):
        pass

    def get_rejected_stores(self) -> pd.DataFrame:
        """Return the DataFrame of rejected stores (those removed from any final market)."""
        return self._rejected

    # ------------------------------------------------------------------
    #  BallTree + Haversine
    # ------------------------------------------------------------------

    def _detect_outliers(
        self,
        stores: pd.DataFrame,
        cluster_label: int,
        cluster_indices: List[int]
    ) -> List[int]:
        """
        1) Compute centroid of all stores in 'cluster_indices'.
        2) Check each store in that cluster: if dist(store -> centroid) >
            self.max_cluster_distance, mark as outlier.
        3) Return a list of outlier indices.
        """
        if not cluster_indices:
            return []

        # coordinates of cluster
        arr = stores.loc[cluster_indices, ['latitude', 'longitude']].values

        # Simple approach: K-Means with n_clusters=1
        # This basically finds the centroid that minimizes sum of squares.
        km = KMeans(n_clusters=1, random_state=42).fit(arr)
        centroid = km.cluster_centers_[0]  # [lat, lon]

        # Store the centroid for this cluster
        self._cluster_centroids[cluster_label] = {
            'centroid_lat': centroid[0],
            'centroid_lon': centroid[1]
        }

        outliers = []
        for idx in cluster_indices:
            store_lat = stores.at[idx, 'latitude']
            store_lon = stores.at[idx, 'longitude']
            d = self._haversine_miles(centroid[0], centroid[1], store_lat, store_lon)
            if d > (self.max_cluster_distance + self.borderline_threshold):
                outliers.append(idx)
        self._outlier_stores.update(outliers)  # Track outliers globally
        return outliers

    def _validate_distance(self, stores, cluster_stores: pd.DataFrame):
        """
        Validates distances between neighbors using precomputed distances.
        Args:
            coords_rad (ndarray): Array of [latitude, longitude] in radians.
            neighbors (ndarray): Array of indices of neighbors.
            distances (ndarray): Distances from the query point to each neighbor.
        """
        # Convert max_cluster_distance (in miles) to radians
        max_distance_radians = miles_to_radians(
            self.max_cluster_distance + self.borderline_threshold
        )

        # Extract coordinates of the stores in the cluster
        cluster_coords = cluster_stores[['latitude', 'longitude']].values
        cluster_indices = cluster_stores.index.tolist()

        # Iterate through each store in the cluster
        outliers = []
        for idx, (store_lat, store_lon) in zip(cluster_indices, cluster_coords):
            # Compute the traveled distance using OSMnx to all other stores in the cluster
            traveled_distances = []
            for neighbor_idx, (neighbor_lat, neighbor_lon) in zip(cluster_indices, cluster_coords):
                if idx == neighbor_idx:
                    continue  # Skip self-distance
                try:
                    # Calculate the traveled distance using OSMnx (network distance)
                    traveled_distance = self._osmnx_travel_distance(
                        store_lat, store_lon, neighbor_lat, neighbor_lon
                    )
                    traveled_distances.append(traveled_distance)
                except Exception as e:
                    print(f"Error calculating distance for {idx} -> {neighbor_idx}: {e}")

            # Check if the maximum traveled distance exceeds the threshold
            if traveled_distances and max(traveled_distances) > max_distance_radians:
                outliers.append(idx)
                # Mark store as unassigned
                stores.at[idx, self._cluster_id] = -1

        return outliers

    def _post_process_outliers(self, stores: pd.DataFrame, unassigned: set):
        """
        Assign unassigned stores to the nearest cluster using relaxed distance criteria.
        """
        if not unassigned:
            return

        # Get cluster centroids
        clusters = stores[stores[self._cluster_id] != -1].groupby(self._cluster_id)
        centroids = {
            cluster_id: cluster_df[['latitude', 'longitude']].mean().values
            for cluster_id, cluster_df in clusters
        }

        # Relaxed distance threshold
        relaxed_threshold = self.cluster_radius + self.relaxed_threshold

        for outlier_idx in list(unassigned):
            outlier_lat = stores.at[outlier_idx, 'latitude']
            outlier_lon = stores.at[outlier_idx, 'longitude']

            # Find nearest cluster within relaxed threshold
            nearest_cluster = None
            min_distance = float('inf')

            for cluster_id, centroid in centroids.items():
                distance = self._haversine_miles(centroid[0], centroid[1], outlier_lat, outlier_lon)
                if distance < relaxed_threshold and distance < min_distance:
                    nearest_cluster = cluster_id
                    min_distance = distance

            # Assign to the nearest cluster if valid
            if nearest_cluster is not None:
                stores.at[outlier_idx, self._cluster_id] = nearest_cluster
                self._outlier_stores.discard(outlier_idx)  # Remove from outliers if reassigned
                unassigned.remove(outlier_idx)

        print(f"Post-processing completed. Remaining unassigned: {len(unassigned)}")

    def _add_outlier_column_to_result(self, df: pd.DataFrame):
        """Add outlier boolean column to indicate stores that were marked as outliers."""
        df['outlier'] = df.index.isin(self._outlier_stores)

    def _create_cluster(self, stores: pd.DataFrame):
        """
        1) BFS with BallTree to create a provisional cluster.
        2) Post-check each cluster with a distance validation (centroid-based or K-Means).
        3) Mark outliers as -1 or store them as rejected.
        """
        # 1) Sort by latitude and longitude to ensure spatial proximity in clustering
        stores = stores.sort_values(by=['latitude', 'longitude']).reset_index(drop=True)
        stores['rad'] = stores.apply(
            lambda row: np.radians([row.latitude, row.longitude]), axis=1
        )
        # rad_df = stores[['latitude', 'longitude']].apply(degrees_to_radians, axis=1).apply(pd.Series)
        # stores = pd.concat([stores, rad_df], axis=1)
        # stores.rename(columns={0: "rad_latitude", 1: "rad_longitude"}, inplace=True)

        # Convert 'rad' column to a numpy array for BallTree
        coords_rad = np.stack(stores['rad'].to_numpy())

        # Create BallTree with all coordinates:
        tree = BallTree(
            coords_rad,
            leaf_size=15,
            metric='haversine'
        )

        # All unassigned
        N = len(stores)
        # Initialize cluster labels to -1 (unassigned)
        stores[self._cluster_id] = -1
        unassigned = set(range(N))
        outliers = set()
        outlier_attempts = {idx: 0 for idx in range(N)}  # Track attempts to recluster

        cluster_label = 0

        # Convert self.cluster_radius (in miles) to radians for BallTree search
        radius_radians = miles_to_radians(self.cluster_radius)

        while unassigned:

            # Convert unassigned set to list and rebuild BallTree
            unassigned_list = sorted(list(unassigned))
            unassigned_coords = coords_rad[unassigned_list]

            # Build a new BallTree with only unassigned elements
            tree = BallTree(
                unassigned_coords,
                leaf_size=50,
                metric='haversine'
            )

            # Start a new cluster
            cluster_indices = []
            # Get the first unassigned store
            current_idx = unassigned_list[0]
            cluster_indices.append(current_idx)
            stores.at[current_idx, self._cluster_id] = cluster_label
            unassigned.remove(current_idx)

            # Frontier for BFS
            frontier = [current_idx]

            while frontier and len(cluster_indices) < self.max_cluster_size:
                # Map global index to local index for the BallTree query
                global_idx = frontier.pop()
                local_idx = unassigned_list.index(global_idx)

                neighbors, distances = tree.query_radius(
                    [unassigned_coords[local_idx]], r=radius_radians, return_distance=True
                )

                neighbors = neighbors[0]  # Extract the single query point's neighbors
                distances = distances[0]  # Extract the single query point's distances

                # Map local indices back to global indices
                global_neighbors = [unassigned_list[i] for i in neighbors]
                new_candidates = [idx for idx in global_neighbors if idx in unassigned]

                # print('New candidates ', len(new_candidates))
                if not new_candidates and len(cluster_indices) < self.min_cluster_size:
                    # Expand search radius for small clusters
                    expanded_radius = radius_radians * 1.1  # Slightly larger radius
                    neighbors, distances = tree.query_radius(
                        [unassigned_coords[local_idx]], r=expanded_radius, return_distance=True
                    )
                elif not new_candidates:
                    continue

                # Limit number of stores to add to not exceed max_cluster_size
                num_needed = self.max_cluster_size - len(cluster_indices)
                new_candidates = new_candidates[:num_needed]

                # Assign them to the cluster
                for cand_idx in new_candidates:
                    if cand_idx not in cluster_indices:
                        frontier.append(cand_idx)
                    stores.at[cand_idx, self._cluster_id] = cluster_label
                    # Remove new_indices from unassigned_indices
                    unassigned.remove(cand_idx)

                # Add them to BFS frontier
                frontier.extend(new_candidates)
                cluster_indices.extend(new_candidates)

            # Validate cluster
            outliers = self._detect_outliers(stores, cluster_label, cluster_indices)
            for out_idx in outliers:
                stores.at[out_idx, self._cluster_id] = -1
                unassigned.add(out_idx)

            cluster_label += 1

        # Post-process unassigned stores
        print(f"Starting post-processing for {len(unassigned)} unassigned stores.")
        self._post_process_outliers(stores, unassigned)

        # Map cluster -> Market1, Market2, ...
        print(f"Final clusters formed: {cluster_label}")
        print(f"Total outliers: {len(outliers)}")

        print(stores)
        self._apply_market_labels(stores, stores[self._cluster_id].values)
        return stores

    def _build_haversine_matrix(self, coords_rad, tree: BallTree) -> np.ndarray:
        """
        Build a full NxN matrix of haversine distances in radians.
        """
        n = len(coords_rad)
        dist_matrix = np.zeros((n, n), dtype=float)

        for i in range(n):
            dist, idx = tree.query([coords_rad[i]], k=n)
            dist = dist[0]  # shape (n,)
            idx = idx[0]    # shape (n,)
            dist_matrix[i, idx] = dist

        return dist_matrix

    def _convert_to_radians(self, value: float, unit: str) -> float:
        """
        Convert value in miles or km to radians (on Earth).
        Earth radius ~ 6371 km or 3959 miles.
        """
        if unit.lower().startswith('mile'):
            # miles
            earth_radius = 3959.0
        else:
            # kilometers
            earth_radius = 6371.0

        return value / earth_radius

    def _apply_market_labels(self, df: pd.DataFrame, labels: np.ndarray):
        """Map cluster_id => Market1, Market2, etc."""
        cluster_map = {}
        cluster_ids = sorted(set(labels))
        market_idx = 0
        for cid in cluster_ids:
            if cid == -1:
                cluster_map[cid] = "Outlier"
            else:
                cluster_map[cid] = f"Market-{market_idx}"
                market_idx += 1
        df[self._cluster_name] = df[self._cluster_id].map(cluster_map)

    def _add_cluster_centroids_to_result(self, df: pd.DataFrame):
        """Add cluster centroid coordinates to the result DataFrame."""
        df['centroid_lat'] = df[self._cluster_id].map(
            lambda cid: self._cluster_centroids.get(cid, {}).get('centroid_lat', np.nan)
        )
        df['centroid_lon'] = df[self._cluster_id].map(
            lambda cid: self._cluster_centroids.get(cid, {}).get('centroid_lon', np.nan)
        )

    # ------------------------------------------------------------------
    #  OSMnx-based refinement
    # ------------------------------------------------------------------

    def load_graph_from_pbf(self, pbf_path, bounding_box: list) -> nx.MultiDiGraph:
        """
        Load a road network graph from a PBF file for the specified bounding box.
        Args:
            pbf_path (str): Path to the PBF file.
            north, south, east, west (float): Bounding box coordinates.
        Returns:
            nx.MultiDiGraph: A road network graph for the bounding box.
        """
        osm = OSM(str(pbf_path), bounding_box=bounding_box)

        # Extract the road network
        road_network = osm.get_network(network_type="driving")

        # Convert to NetworkX graph
        G = osm.to_graph(road_network, graph_type="networkx")
        return G

    def _build_osmnx_graph_for_point(self, lat: float, lon: float) -> nx.MultiDiGraph:
        """
        Build a local OSMnx graph for the point (lat, lon) + self.network_type.
        """
        # For example:
        G = ox.graph_from_point(
            (lat, lon),
            dist=50000,
            network_type=self.network_type,
            simplify=True,
            custom_filter=self.custom_filter
        )
        return G

    def _build_osmnx_graph_for_bbox(self, north, south, east, west) -> nx.MultiDiGraph:
        """
        Build a local OSMnx graph for the bounding box + self.network_type.
        """
        # For example:
        buffer = 0.005  # Degrees (~0.5 km buffer)
        bbox = (north + buffer, south - buffer, east + buffer, west - buffer)
        print('BOX > ', bbox)
        G = ox.graph_from_bbox(
            bbox=bbox,
            network_type=self.network_type,
            # simplify=True,
            # retain_all=True,
            # truncate_by_edge=True,
            # custom_filter=self.custom_filter
        )
        ox.plot_graph(G)
        return G

    def _find_borderline_stores(self):
        """
        Re-evaluate stores that are > half cluster radius from their center
        to see if they should be reassigned to a closer market center.
        Respects maximum cluster size limits during reassignment.
        """
        reassignment_threshold = self.max_cluster_distance * self.reassignment_threshold_factor
        reassigned_count = 0
        # 20% of max_cluster_size
        max_reassignment_limit = int(self.max_cluster_size * self.max_reassignment_percentage)

        # Track current cluster sizes
        cluster_sizes = self._data[
            self._data[self._cluster_id] != -1
        ].groupby(self._cluster_id).size().to_dict()

        # Group stores by current market
        for current_cid in self._data[self._cluster_id].unique():
            if current_cid == -1:
                continue

            current_market_stores = self._data[self._data[self._cluster_id] == current_cid].copy()

            for idx, store in current_market_stores.iterrows():
                store_distance = store.get('distance_to_center', 0)

                # Only re-evaluate stores beyond the threshold
                if store_distance > reassignment_threshold:
                    store_lat = store['latitude']
                    store_lon = store['longitude']

                    # Find the closest market center (including current one)
                    min_distance = float('inf')
                    best_market = current_cid

                    for other_cid in self._data[self._cluster_id].unique():
                        if other_cid == -1:
                            continue

                        # Check if target market would exceed size limit
                        current_size = cluster_sizes.get(other_cid, 0)
                        if current_size >= (self.max_cluster_size - max_reassignment_limit):
                            continue  # Skip this market - too close to size limit

                        if other_cid in self._cluster_centroids:
                            center_lat = self._cluster_centroids[other_cid]['centroid_lat']
                            center_lon = self._cluster_centroids[other_cid]['centroid_lon']

                            distance = self._haversine_miles(store_lat, store_lon, center_lat, center_lon)

                            # Only reassign if significantly closer (at least 5 miles difference)
                            # and within max_cluster_distance
                            if (
                                distance < min_distance and distance <= self.max_cluster_distance and distance < (store_distance - 5.0)  # noqa
                            ):  # Must be at least 5 miles closer
                                min_distance = distance
                                best_market = other_cid

                    # Reassign if we found a better market
                    if best_market != current_cid:
                        self._data.at[idx, self._cluster_id] = best_market
                        self._data.at[idx, self._cluster_name] = f"Market-{best_market}"
                        self._data.at[idx, 'ghost_id'] = f"Ghost-{best_market}-1"

                        # Update centroid coordinates
                        self._data.at[idx, 'centroid_lat'] = self._cluster_centroids[best_market]['centroid_lat']
                        self._data.at[idx, 'centroid_lon'] = self._cluster_centroids[best_market]['centroid_lon']

                        reassigned_count += 1

                        self._logger.info(
                            f"Reassigned store {store.get('store_id', idx)} from Market-{current_cid} "
                            f"(dist: {store_distance:.1f}mi) to Market-{best_market} (dist: {min_distance:.1f}mi)"
                        )

        if reassigned_count > 0:
            self._logger.info(
                f"Re-evaluated and reassigned {reassigned_count} distant stores to closer markets"
            )
            # Recalculate distances after reassignment
            self._add_distance_to_center_column(self._data)

    def _compute_cluster_representatives(self):
        """
        For each cluster, pick a "representative" store (e.g., the first one).
        Then record the OSMnx node after we build the graph.
        """
        info = {}
        for cid, grp in self._data.groupby(self._cluster_id):
            if cid == -1:
                info[cid] = {"index": None, "latitude": None, "longitude": None, "node": None}
                continue
            first_idx = grp.index[0]
            lat = grp.at[first_idx, 'latitude']
            lon = grp.at[first_idx, 'longitude']
            info[cid] = {"index": first_idx, "latitude": lat, "longitude": lon, "node": None}

        # We can fill 'node' after we have the graph if needed
        lat_array = self._data['latitude'].values
        lon_array = self._data['longitude'].values
        # But we do that in _refine_border_stores to ensure we only do nearest_nodes once
        return info

    # ------------------------------------------------------------------
    #  Ghost Employees
    # ------------------------------------------------------------------
    def _haversine_distance_km(self, lat1, lon1, lat2, lon2):
        """
        Calculate the geodesic distance between two points in kilometers using Geopy.
        """
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers

    def _get_num_ghosts_for_cluster(self, cid, cluster_df: pd.DataFrame) -> int:
        """
        Determine the number of ghost employees for a cluster.
        First check if 'fte' column exists and has values for this market.
        If not, use the default num_ghosts_per_cluster.
        """
        # Check if 'fte' column exists
        if 'fte' in cluster_df.columns:
            # Get the FTE values for this cluster (should be the same for all stores in the market)
            fte_values = cluster_df['fte'].dropna().unique()
            if len(fte_values) > 0:
                # Use the first non-null FTE value found
                fte_value = fte_values[0]
                if pd.notna(fte_value) and fte_value > 0:
                    return max(1, int(fte_value))  # Ensure at least 1 ghost employee

        # Fallback to default number of ghosts per cluster
        return self.num_ghosts_per_cluster

    def _create_ghost_employees(self, cid, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create ghost employees around each cluster's centroid.
        Uses 'fte' column if available, otherwise uses num_ghosts_per_cluster.
        Ensure no ghost is more than 5 km from the centroid.
        Spread ghosts within the cluster to maximize coverage.
        """
        ghosts = []
        cluster_rows = df[df[self._cluster_id] == cid]
        if cluster_rows.empty:
            return ghosts

        if len(cluster_rows) == 1:
            # Only one store in this cluster, no need for ghosts
            return ghosts

        # Centroid of this Cluster
        lat_mean = cluster_rows['latitude'].mean()
        lon_mean = cluster_rows['longitude'].mean()

        max_offset_lat = 0.002  # ~5 km
        max_offset_lon = 0.002  # ~5 km at 40° latitude
        max_offset_miles = 50.0  # Maximum distance from centroid
        min_distance_km = 10.0  # Minimum distance between ghosts to prevent overlapping

        # Get number of ghost employees for this cluster
        num_ghosts = self._get_num_ghosts_for_cluster(cid, cluster_rows)

        for i in range(num_ghosts):
            attempt = 0
            while True:
                # lat_offset = np.random.uniform(-max_offset_lat, max_offset_lat)
                # lon_offset = np.random.uniform(-max_offset_lon, max_offset_lon)

                # ghost_lat = lat_mean + lat_offset
                # ghost_lon = lon_mean + lon_offset

                # # Calculate distance to centroid using geodesic distance for precision
                # distance_km = self._haversine_distance_km(lat_mean, lon_mean, ghost_lat, ghost_lon)
                # if distance_km > 5.0:
                #     attempt += 1
                #     if attempt >= 100:
                #         self._logger.warning(
                #             f"Could not place ghost {i+1} within 5 km after 100 attempts in cluster {cid}."
                #         )
                #         break
                #     continue  # Exceeds maximum distance, retry

                # Generate a random point within a circle of radius 50 miles from the centroid
                angle = np.random.uniform(0, 2 * np.pi)
                distance = np.random.uniform(0, max_offset_miles)
                delta_lat = (distance * math.cos(angle)) / 69.0  # Approx. degrees per mile
                delta_lon = (distance * math.sin(angle)) / (69.0 * math.cos(math.radians(lat_mean)))

                ghost_lat = lat_mean + delta_lat
                ghost_lon = lon_mean + delta_lon

                # Ensure ghosts are not too close to each other
                too_close = False
                for existing_ghost in ghosts:
                    existing_distance = self._haversine_distance_km(
                        existing_ghost['latitude'],
                        existing_ghost['longitude'],
                        ghost_lat,
                        ghost_lon
                    )
                    if existing_distance < min_distance_km:
                        too_close = True
                        break
                if not too_close:
                    break  # Valid position found
                if too_close:
                    attempt += 1
                    if attempt >= 100:
                        self._logger.warning(
                            f"Ghost {i+1} in cluster {cid} is too close to existing ghosts after 100 attempts."
                        )
                        break
                    continue  # Ghost too close to existing, retry

                # Valid position found
                break

            ghost_id = f"Ghost-{cid}-{i+1}"
            ghost = {
                'ghost_id': ghost_id,
                self._cluster_id: cid,
                'latitude': ghost_lat,
                'longitude': ghost_lon
            }
            ghosts.append(ghost)

        return ghosts

    # ------------------------------------------------------------------
    #  Filter stores unreachable from any ghost
    # ------------------------------------------------------------------
    def _filter_unreachable_stores(
        self,
        cid: int,
        employees: List[Dict[str, Any]],
        cluster_stores: pd.DataFrame
    ) -> List[int]:
        """
        For each store in the given cluster's df_cluster, check if
        any of the provided employees is within ghost_distance_threshold miles.
        Return a list of indices that are unreachable.
        """
        unreachable_indices = []

        # If no employees for this cluster, everything is unreachable
        if not employees:
            return cluster_stores.index.tolist()

        if cid == -1 or len(cluster_stores) == 1:
            return []

        for idx, row in cluster_stores.iterrows():
            store_lat = row['latitude']
            store_lon = row['longitude']
            cluster_id = row['market_id']
            store_id = row['store_id']

            reachable = False
            for ghost in employees:
                g_lat = ghost['latitude']
                g_lon = ghost['longitude']
                distance_km = self._haversine_distance_km(store_lat, store_lon, g_lat, g_lon)
                dist = meters_to_miles(distance_km * 1000)
                if dist <= self.ghost_distance_threshold:
                    reachable = True
                    break
            if not reachable:
                unreachable_indices.append(idx)

        return unreachable_indices

    def _haversine_miles(self, lat1, lon1, lat2, lon2):
        """
        Simple haversine formula returning miles between two lat/lon points.
        Earth radius ~3959 miles.
        """
        R = 3959.0  # Earth radius in miles
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c

    def _nearest_osm_node(self, G: nx.MultiDiGraph, lat: float, lon: float) -> int:
        """
        Return the nearest node in graph G to (lat, lon).
        """
        node = ox_distance.nearest_nodes(G, X=[lon], Y=[lat])
        # node is usually an array or single value
        if isinstance(node, np.ndarray):
            return node[0]
        return node

    def _road_distance_miles(
        self, G: nx.MultiDiGraph,
        center_lat: float,
        center_lon: float,
        lat: float,
        lon: float
    ) -> Optional[float]:
        """
        Compute route distance in miles from node_center to (lat, lon) in G.
        If no path, return None.
        1) nearest node for center, nearest node for candidate
        2) shortest_path_length with weight='length'
        3) convert meters->miles
        If no path, return None
        """
        node_center = self._nearest_osm_node(G, center_lat, center_lon)
        node_target = self._nearest_osm_node(G, lat, lon)
        try:
            dist_m = nx.shortest_path_length(G, node_center, node_target, weight='length')
            dist_miles = dist_m * 0.000621371
            return dist_miles
        except nx.NetworkXNoPath:
            return None

    def _compute_distance_matrix(
        self,
        cluster_df: pd.DataFrame,
        G_local: nx.MultiDiGraph,
        depot_lat: float,
        depot_lon: float
    ) -> np.ndarray:
        """
        Computes the road-based distance matrix for the cluster.
        Includes the depot as the first node.
        """
        store_ids = cluster_df.index.tolist()
        all_coords = [(depot_lat, depot_lon)] + list(cluster_df[['latitude', 'longitude']].values)
        distance_matrix = np.zeros((len(all_coords), len(all_coords)), dtype=float)

        # Precompute nearest nodes
        nodes = ox_distance.nearest_nodes(
            G_local, X=[lon for lat, lon in all_coords], Y=[lat for lat, lon in all_coords]
        )

        for i in range(len(all_coords)):
            for j in range(len(all_coords)):
                if i == j:
                    distance_matrix[i][j] = 0
                else:
                    try:
                        dist_m = nx.shortest_path_length(G_local, nodes[i], nodes[j], weight='length')
                        dist_miles = dist_m * 0.000621371  # meters to miles
                        distance_matrix[i][j] = dist_miles
                    except nx.NetworkXNoPath:
                        distance_matrix[i][j] = np.inf  # No path exists

        return distance_matrix

    def _assign_routes_vrp(
        self,
        cluster_df: pd.DataFrame,
        G_local: nx.MultiDiGraph,
        depot_lat: float,
        depot_lon: float
    ) -> Dict[int, List[int]]:
        """
        Assigns stores in the cluster to ghost employees using VRP.
        Returns a dictionary where keys are ghost IDs and values are lists of store indices.
        """
        store_ids = cluster_df.index.tolist()

        # Get the number of vehicles (ghost employees) for this cluster
        cid = cluster_df[self._cluster_id].iloc[0] if not cluster_df.empty else 0
        num_vehicles = self._get_num_ghosts_for_cluster(cid, cluster_df)

        # Compute distance matrix with depot as first node
        distance_matrix = self._compute_distance_matrix(cluster_df, G_local, depot_lat, depot_lon)

        # Handle infinite distances by setting a large number
        distance_matrix[np.isinf(distance_matrix)] = 1e6

        # Create data model for VRP
        data = create_data_model(
            distance_matrix=distance_matrix.tolist(),  # OR-Tools requires lists
            num_vehicles=num_vehicles,
            depot=0,
            max_distance=self.max_distance_by_day,
            max_stores_per_vehicle=self.max_stores_per_day
        )

        # Solve VRP
        routes = solve_vrp(data)

        # Map routes to store indices (excluding depot)
        assignment = {}
        for vehicle_id, route in enumerate(routes):
            # Exclude depot (first node)
            assigned_store_indices = route[1:-1]  # Remove depot start and end
            assignment[vehicle_id] = [store_ids[idx - 1] for idx in assigned_store_indices]

        return assignment

    def _validate_clusters_by_vrp(self):
        """
        For each cluster, assign stores to ghost employees using VRP.
        Remove any stores that cannot be assigned within constraints.
        """
        df = self._data
        clusters = df[self._cluster_id].unique()
        to_remove = []
        assignment_dict = {}  # To store assignments per cluster

        for cid in clusters:
            if cid == -1:
                continue  # Skip outliers

            cluster_df = df[df[self._cluster_id] == cid]
            if cluster_df.empty:
                continue

            # 1) Compute bounding box with buffer
            lat_min = cluster_df['latitude'].min()
            lat_max = cluster_df['latitude'].max()
            lon_min = cluster_df['longitude'].min()
            lon_max = cluster_df['longitude'].max()

            buffer_deg = 0.1
            north = lat_max + buffer_deg
            south = lat_min - buffer_deg
            east = lon_max + buffer_deg
            west = lon_min - buffer_deg

            # 2) Build local OSMnx graph for the cluster
            G_local = self._build_osmnx_graph_for_bbox(north, south, east, west)

            # 3) Define depot (cluster centroid)
            centroid_lat = cluster_df['latitude'].mean()
            centroid_lon = cluster_df['longitude'].mean()

            # 4) Assign routes using VRP
            assignment = self._assign_routes_vrp(cluster_df, G_local, centroid_lat, centroid_lon)

            # 5) Assign ghost IDs to stores
            for vehicle_id, store_ids in assignment.items():
                ghost_id = f"Ghost-{cid}-{vehicle_id + 1}"
                df.loc[store_ids, 'ghost_id'] = ghost_id

            # 6) Identify unassigned stores (if any)
            assigned_store_ids = set()
            for route in assignment.values():
                assigned_store_ids.update(route)

            all_store_ids = set(cluster_df.index.tolist())
            unassigned_store_ids = all_store_ids - assigned_store_ids

            if unassigned_store_ids:
                to_remove.extend(list(unassigned_store_ids))

        # 6) Remove unassigned stores
        to_remove = list(set(to_remove))
        if to_remove:
            self._logger.info(
                f"Removing {len(to_remove)} stores that could not be assigned via VRP."
            )
            self._rejected = pd.concat([self._rejected, self._data.loc[to_remove]]).drop_duplicates()
            self._data.drop(index=to_remove, inplace=True)

        # 8) Update DataFrame with assignments
        self._data = df.copy()

        # 9) Apply market labels again if needed
        self._apply_market_labels(self._data, self._data[self._cluster_id].values)

    def _reassign_rejected_stores(self):
        """
        Attempt to reassign rejected stores to existing clusters if within the borderline threshold.
        """
        if self._rejected.empty:
            return

        borderline_threshold = self.borderline_threshold
        to_remove = []
        df = self._rejected.copy()

        for idx, row in df.iterrows():
            # Find the nearest cluster centroid
            min_distance = np.inf
            assigned_cid = -1

            for cid in self._data[self._cluster_id].unique():
                if cid == -1:
                    continue
                centroid_lat = self._data[self._cluster_id == cid]['latitude'].mean()
                centroid_lon = self._data[self._cluster_id == cid]['longitude'].mean()
                distance = self._haversine_miles(centroid_lat, centroid_lon, row['latitude'], row['longitude'])
                if distance < min_distance:
                    min_distance = distance
                    assigned_cid = cid

            # Check if within the borderline threshold
            if min_distance <= self.max_cluster_distance * borderline_threshold:
                # Assign to this cluster
                self._data.at[idx, self._cluster_id] = assigned_cid
                self._data.at[idx, 'ghost_id'] = f"Ghost-{assigned_cid}-1"  # Assign to the first ghost for simplicity
                to_remove.append(idx)

        # Remove reassigned stores from rejected
        if to_remove:
            self._rejected.drop(index=to_remove, inplace=True)
            self._logger.info(
                f"Reassigned {len(to_remove)} rejected stores to existing clusters."
            )

    def _save_rejected_stores(self):
        """Save rejected stores to Excel file if file path is provided."""
        if self.rejected_stores_file and not self._rejected.empty:
            try:
                # Convert to absolute path if relative
                if isinstance(self.rejected_stores_file, str):
                    self.rejected_stores_file = self.rejected_stores_file.strip()
                    file_path = Path(self.rejected_stores_file)
                elif isinstance(self.rejected_store_file, Path):
                    file_path = self.rejected_stores_file
                if not file_path.is_absolute():
                    file_path = Path.cwd() / file_path

                # Ensure directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Save to Excel
                self._rejected.to_excel(file_path, index=False)

                self._logger.info(
                    f"Saved {len(self._rejected)} rejected stores to {file_path}"
                )
            except Exception as e:
                self._logger.error(
                    f"Failed to save rejected stores to {self.rejected_stores_file}: {e}"
                )
        elif self.rejected_stores_file and self._rejected.empty:
            self._logger.info(
                "No rejected stores to save - all stores were assigned to markets"
            )

    def _force_assign_all_rejected_stores(self):
        """
        Force assign all rejected stores to their nearest market cluster.
        This ensures no stores are left unassigned.
        """
        if self._rejected.empty:
            return

        self._logger.info(
            f"Force assigning {len(self._rejected)} rejected stores to nearest markets..."
        )

        # Get all valid cluster centroids (excluding outliers)
        valid_clusters = self._data[self._data[self._cluster_id] != -1][self._cluster_id].unique()

        if len(valid_clusters) == 0:
            self._logger.warning("No valid clusters found for force assignment!")
            return

        reassigned_stores = []
        still_rejected_indices = []  # Track stores that remain rejected

        for idx, row in self._rejected.iterrows():
            min_distance = float('inf')
            nearest_cluster = None

            # Find the nearest cluster centroid
            for cid in valid_clusters:
                if cid in self._cluster_centroids:
                    centroid_lat = self._cluster_centroids[cid]['centroid_lat']
                    centroid_lon = self._cluster_centroids[cid]['centroid_lon']
                    distance = self._haversine_miles(
                        centroid_lat, centroid_lon,
                        row['latitude'], row['longitude']
                    )
                    if distance < min_distance:
                        min_distance = distance
                        nearest_cluster = cid

            if nearest_cluster is not None and min_distance <= self._max_force_assign_distance:
                # Add store to main dataframe with nearest cluster assignment
                store_data = row.copy()
                store_data[self._cluster_id] = nearest_cluster
                store_data[self._cluster_name] = f"Market-{nearest_cluster}"
                store_data['ghost_id'] = f"Ghost-{nearest_cluster}-1"
                store_data['outlier'] = True

                # Add centroid coordinates
                store_data['centroid_lat'] = self._cluster_centroids[nearest_cluster]['centroid_lat']
                store_data['centroid_lon'] = self._cluster_centroids[nearest_cluster]['centroid_lon']

                # Add distance to center
                store_data['distance_to_center'] = round(min_distance, 2)

                reassigned_stores.append(store_data)
            else:
                # Store is too far even from nearest cluster - keep as rejected
                still_rejected_indices.append(idx)
                self._logger.warning(
                    f"Store {row.get('store_id', idx)} is {min_distance:.1f} miles from nearest market - leaving unassigned"  # noqa
                )

        if reassigned_stores:
            # Convert to DataFrame and concatenate with main data
            reassigned_df = pd.DataFrame(reassigned_stores)
            self._data = pd.concat([self._data, reassigned_df], ignore_index=True)

            self._logger.info(
                f"Successfully force-assigned {len(reassigned_stores)} stores to nearest markets"
            )

        # Update rejected stores to only include those that are still too far
        if still_rejected_indices:
            self._rejected = self._rejected.loc[still_rejected_indices].copy()
            self._logger.info(
                f"{len(still_rejected_indices)} stores remain rejected (beyond {self._max_force_assign_distance} miles from nearest market)"  # noqa
            )
        else:
            # All stores were successfully assigned
            self._rejected = pd.DataFrame()

    def _add_distance_to_center_column(self, df: pd.DataFrame):
        """Add distance column showing miles from each store to its market center."""
        distances = []

        for idx, row in df.iterrows():
            cluster_id = row[self._cluster_id]

            if cluster_id == -1 or cluster_id not in self._cluster_centroids:
                # For outliers or missing centroids, set distance as NaN
                distances.append(np.nan)
            else:
                # Calculate distance from store to its market center
                store_lat = row['latitude']
                store_lon = row['longitude']
                center_lat = self._cluster_centroids[cluster_id]['centroid_lat']
                center_lon = self._cluster_centroids[cluster_id]['centroid_lon']

                distance_miles = self._haversine_miles(store_lat, store_lon, center_lat, center_lon)
                distances.append(round(distance_miles, 2))  # Round to 2 decimal places

        df['distance_to_center'] = distances

    async def run(self):
        """
        1) Cluster with BallTree + K-Means validation.
        2) Road-based validation: assign stores to ghost employees via VRP.
        3) Remove any stores that cannot be assigned within constraints.
        4) Re-assign rejected stores if possible.
        5) Add cluster centroids to result DataFrame.
        6) Return final assignment + rejected stores.
        """
        self._logger.info(
            "=== Running MarketClustering ==="
        )

        # --- create cluster in haversine space (balltree)
        self._data = self._create_cluster(self._data)

        # 2) Road-based validation via VRP
        # self._validate_clusters_by_vrp()

        # 3) Reassign rejected stores
        # self._reassign_rejected_stores()

        unreachable_stores = []  # gather all unreachable store indices globally
        grouped = self._data.groupby(self._cluster_id)
        for cid, cluster_stores in grouped:
            if cid == -1 or len(cluster_stores) <= 1:
                continue  # skip outliers

            # Validate distances after cluster creation
            # outliers = self._validate_distance(self._data, cluster_stores)

            # Log outlier count
            # print(f"Number of outliers detected: {len(outliers)}")

            # Create the ghost employees for this Cluster:
            employees = self._create_ghost_employees(cid, self._data)
            cluster_unreachable = self._filter_unreachable_stores(
                cid=cid,
                employees=employees,
                cluster_stores=cluster_stores
            )
            unreachable_stores.extend(cluster_unreachable)

        # TODO: remove unreachable stores from the cluster
        unreachable_stores = list(set(unreachable_stores))
        self._rejected = self._data.loc[unreachable_stores].copy()
        self._data.drop(index=unreachable_stores, inplace=True)
        self._logger.info(
            f"Unreachable stores: {len(unreachable_stores)}"
        )

        # Add cluster centroids to the result DataFrame
        self._add_cluster_centroids_to_result(self._data)
        self._add_outlier_column_to_result(self._data)

        # Force assign all rejected stores to nearest markets
        self._force_assign_all_rejected_stores()

        # Add the distance to center of market
        self._add_distance_to_center_column(self._data)

        # Re-evaluate distant stores for better market assignment
        self._find_borderline_stores()

        self._logger.info(
            f"Final clusters formed: {self._data[self._cluster_id].nunique() - 1} (excluding Outliers)"
        )
        self._logger.info(
            f"Total rejected stores: {len(self._rejected)}"
        )
        self._save_rejected_stores()

        self._result = self._data
        return self._result
