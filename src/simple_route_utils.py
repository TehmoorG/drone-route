"""
simple_route_utils.py

This module provides utility functions specific to the simple drone routing algorithm.
It includes functions for creating and saving a network graph of healthcare facilities,
as well as adding new nodes (locations) to the graph while considering no-fly zones and avoidance areas.

Functions:
- create_and_save_graph(health_facilities_gdf, no_fly_zones_gdf, avoidance_zones_gdf, drone_range_km, output_path):
  Creates a network graph based on healthcare facilities and saves it to a file.
- add_node_to_graph(G, lat, lon, node_name, health_facilities_gdf, no_fly_zones_gdf, avoidance_zones_gdf, drone_range_km):
  Adds a new node to the existing graph, connecting it to other nodes based on proximity and constraints.
"""

import networkx as nx
from shapely.geometry import Point, LineString
from geopy.distance import geodesic
import pickle


def create_and_save_graph(
    health_facilities_gdf,
    no_fly_zones_gdf,
    avoidance_zones_gdf,
    drone_range_km,
    output_path="../output/simple_route.pkl",
):
    """
    Creates a network graph of healthcare facilities and saves it to a file.

    Nodes represent healthcare facilities, and edges are created between facilities that are within
    a specified drone range, with consideration of no-fly zones and avoidance areas.

    Args:
        health_facilities_gdf (geopandas.GeoDataFrame): GeoDataFrame containing healthcare facilities with geometry points.
        no_fly_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing no-fly zones as polygons.
        avoidance_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing avoidance zones as polygons.
        drone_range_km (float): The maximum distance the drone can travel between facilities in kilometers.
        output_path (str): The file path where the graph will be saved as a pickle file.

    Returns:
        None
    """
    G = nx.Graph()

    # Add healthcare facilities as nodes and connect them if they are within the drone's range
    for idx1, row1 in health_facilities_gdf.iterrows():
        if not no_fly_zones_gdf.contains(row1.geometry).any():
            G.add_node(idx1, pos=(row1["longitude"], row1["latitude"]))

            for idx2, row2 in health_facilities_gdf.iterrows():
                if idx1 != idx2:
                    distance = geodesic(
                        (row1["latitude"], row1["longitude"]),
                        (row2["latitude"], row2["longitude"]),
                    ).km

                    if distance <= drone_range_km:
                        line = LineString([row1.geometry, row2.geometry])

                        # Check if the edge intersects any no-fly zones
                        if no_fly_zones_gdf.intersects(line).any():
                            continue  # Skip adding this edge

                        # Adjust the edge weight if it intersects an avoidance zone
                        edge_weight = distance
                        if avoidance_zones_gdf.intersects(line).any():
                            edge_weight *= 10

                        G.add_edge(idx1, idx2, weight=edge_weight)

    # Save the graph to a file
    with open(output_path, "wb") as f:
        pickle.dump(G, f)
    print(f"Network graph created and saved as '{output_path}'.")


def add_node_to_graph(
    G,
    lat,
    lon,
    node_name,
    health_facilities_gdf,
    no_fly_zones_gdf,
    avoidance_zones_gdf,
    drone_range_km,
):
    """
    Adds a new node to the existing network graph, connecting it to other nodes within the drone's range,
    considering no-fly zones and avoidance areas.

    Args:
        G (networkx.Graph): The existing graph to which the node will be added.
        lat (float): The latitude of the new node.
        lon (float): The longitude of the new node.
        node_name (str): A name/label for the new node.
        health_facilities_gdf (geopandas.GeoDataFrame): GeoDataFrame containing healthcare facilities with geometry points.
        no_fly_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing no-fly zones as polygons.
        avoidance_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing avoidance zones as polygons.
        drone_range_km (float): The maximum distance the drone can travel between nodes in kilometers.

    Returns:
        int: The index of the newly added node.
        None: If the node is within a no-fly zone and cannot be added.
    """
    point = Point(lon, lat)
    if no_fly_zones_gdf.contains(point).any():
        print(f"{node_name} is within a no-fly zone and cannot be added.")
        return None

    # Ensure unique node index
    new_node_idx = max(G.nodes) + 1 if len(G.nodes) > 0 else 0
    G.add_node(new_node_idx, pos=(lon, lat), name=node_name)

    # Ensure the position is stored in the graph's 'pos' attribute
    pos = nx.get_node_attributes(G, "pos")
    pos[new_node_idx] = (lon, lat)
    nx.set_node_attributes(G, pos, "pos")

    # Add edges to other nodes within range
    for idx, row in health_facilities_gdf.iterrows():
        distance = geodesic((lat, lon), (row["latitude"], row["longitude"])).km
        if distance <= drone_range_km:
            edge_weight = distance
            line = LineString([point, row.geometry])

            # Check if the edge intersects any no-fly zones
            if no_fly_zones_gdf.intersects(line).any():
                print(
                    f"Edge from {node_name} to {row['name']} intersects a no-fly zone, not adding."
                )
                continue  # Skip adding this edge

            # If it intersects an avoidance zone, increase weight
            if avoidance_zones_gdf.intersects(line).any():
                edge_weight *= 3  # Increase the weight significantly if it intersects an avoidance zone

            G.add_edge(new_node_idx, idx, weight=edge_weight)

    return new_node_idx
