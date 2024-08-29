"""
advanced_route_utils.py

This module provides utility functions specific to the advanced drone routing algorithm.
It includes functions for segmenting edges, calculating edge weights based on land use data,
creating and saving a network graph with advanced constraints, and adding new nodes to the graph.

Functions:
- segment_edge(line, segment_length): Segments a line into smaller segments of specified length.
- calculate_segment_weight(segment, roads_gdf, buildings_gdf, open_space_gdf, avoidance_zones_gdf):
  Calculates the weight of a segment based on intersection with roads, buildings, open spaces, and avoidance zones.
- calculate_edge_weight(line, roads_gdf, buildings_gdf, open_space_gdf, avoidance_zones_gdf):
  Calculates the total weight of an edge by summing the weights of its segments.
- create_and_save_graph(health_facilities_gdf, roads_gdf, buildings_gdf, open_space_gdf, no_fly_zones_gdf, avoidance_zones_gdf, drone_range_km, output_path):
  Creates a network graph with advanced constraints and saves it to a file.
- add_node_to_graph(G, lat, lon, node_name, health_facilities_gdf, roads_gdf, buildings_gdf, open_space_gdf, no_fly_zones_gdf, avoidance_zones_gdf, drone_range_km):
  Adds a new node to the existing graph, considering advanced constraints.
- download_land_use_data(place_name): Downloads land use data (roads, buildings, open spaces) for a specified place using OSMnx.
"""

import networkx as nx
from shapely.geometry import LineString
from geopy.distance import geodesic
import pickle


def segment_edge(line, segment_length=1):
    """
    Segments a given line into smaller segments of a specified length.

    Args:
        line (shapely.geometry.LineString): The line to be segmented.
        segment_length (float): The desired length of each segment.

    Returns:
        list: A list of LineString objects representing the segments of the original line.
    """
    segments = []
    num_segments = int(line.length / segment_length)
    for i in range(num_segments):
        segment = LineString(
            [
                line.interpolate(i / num_segments, normalized=True),
                line.interpolate((i + 1) / num_segments, normalized=True),
            ]
        )
        segments.append(segment)
    return segments


def calculate_segment_weight(
    segment, roads_gdf, buildings_gdf, open_space_gdf, avoidance_zones_gdf
):
    """
    Calculates the weight of a line segment based on its intersection with roads, buildings,
    open spaces, and avoidance zones.

    Args:
        segment (shapely.geometry.LineString): The line segment to be evaluated.
        roads_gdf (geopandas.GeoDataFrame): GeoDataFrame containing road geometries.
        buildings_gdf (geopandas.GeoDataFrame): GeoDataFrame containing building geometries.
        open_space_gdf (geopandas.GeoDataFrame): GeoDataFrame containing open space geometries.
        avoidance_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing avoidance zone geometries.

    Returns:
        float: The calculated weight of the segment.
    """
    weight = segment.length  # Start with the base weight (length of the segment)

    if roads_gdf.intersects(segment).any():
        weight *= 1.5  # Increase weight if segment intersects a road
    if buildings_gdf.intersects(segment).any():
        weight *= 1  # Increase weight if segment intersects a building
    if open_space_gdf.intersects(segment).any():
        weight *= 0.8  # Decrease weight if segment intersects open space
    if avoidance_zones_gdf.intersects(segment).any():
        weight *= 3  # Heavily increase weight if segment intersects an avoidance zone

    return weight


def calculate_edge_weight(
    line, roads_gdf, buildings_gdf, open_space_gdf, avoidance_zones_gdf
):
    """
    Calculates the total weight of an edge by summing the weights of its segments.

    Args:
        line (shapely.geometry.LineString): The line representing the edge.
        roads_gdf (geopandas.GeoDataFrame): GeoDataFrame containing road geometries.
        buildings_gdf (geopandas.GeoDataFrame): GeoDataFrame containing building geometries.
        open_space_gdf (geopandas.GeoDataFrame): GeoDataFrame containing open space geometries.
        avoidance_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing avoidance zone geometries.

    Returns:
        float: The total weight of the edge.
    """
    segments = segment_edge(line)
    total_weight = sum(
        calculate_segment_weight(
            segment, roads_gdf, buildings_gdf, open_space_gdf, avoidance_zones_gdf
        )
        for segment in segments
    )
    return total_weight


def create_and_save_graph(
    health_facilities_gdf,
    roads_gdf,
    buildings_gdf,
    open_space_gdf,
    no_fly_zones_gdf,
    avoidance_zones_gdf,
    drone_range_km,
    output_path,
):
    """
    Creates a network graph of healthcare facilities with advanced constraints and saves it to a file.

    Nodes represent healthcare facilities, and edges are created between facilities that are within
    a specified drone range, with consideration of roads, buildings, open spaces, no-fly zones, and avoidance areas.

    Args:
        health_facilities_gdf (geopandas.GeoDataFrame): GeoDataFrame containing healthcare facilities with geometry points.
        roads_gdf (geopandas.GeoDataFrame): GeoDataFrame containing road geometries.
        buildings_gdf (geopandas.GeoDataFrame): GeoDataFrame containing building geometries.
        open_space_gdf (geopandas.GeoDataFrame): GeoDataFrame containing open space geometries.
        no_fly_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing no-fly zones as polygons.
        avoidance_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing avoidance zones as polygons.
        drone_range_km (float): The maximum distance the drone can travel between facilities in kilometers.
        output_path (str): The file path where the graph will be saved as a pickle file.

    Returns:
        None
    """
    G = nx.Graph()

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

                        if no_fly_zones_gdf.intersects(line).any():
                            continue  # Skip if the line intersects a no-fly zone

                        edge_weight = calculate_edge_weight(
                            line,
                            roads_gdf,
                            buildings_gdf,
                            open_space_gdf,
                            avoidance_zones_gdf,
                        )
                        G.add_edge(idx1, idx2, weight=edge_weight)

    with open(output_path, "wb") as f:
        pickle.dump(G, f)
    print(f"Network graph created and saved as '{output_path}'.")


def add_node_to_graph(
    G,
    lat,
    lon,
    node_name,
    health_facilities_gdf,
    roads_gdf,
    buildings_gdf,
    open_space_gdf,
    no_fly_zones_gdf,
    avoidance_zones_gdf,
    drone_range_km,
):
    """
    Adds a new node to the existing network graph, connecting it to other nodes within the drone's range,
    considering advanced constraints such as roads, buildings, open spaces, no-fly zones, and avoidance areas.

    Args:
        G (networkx.Graph): The existing graph to which the node will be added.
        lat (float): The latitude of the new node.
        lon (float): The longitude of the new node.
        node_name (str): A name/label for the new node.
        health_facilities_gdf (geopandas.GeoDataFrame): GeoDataFrame containing healthcare facilities with geometry points.
        roads_gdf (geopandas.GeoDataFrame): GeoDataFrame containing road geometries.
        buildings_gdf (geopandas.GeoDataFrame): GeoDataFrame containing building geometries.
        open_space_gdf (geopandas.GeoDataFrame): GeoDataFrame containing open space geometries.
        no_fly_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing no-fly zones as polygons.
        avoidance_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing avoidance zones as polygons.
        drone_range_km (float): The maximum distance the drone can travel between nodes in kilometers.

    Returns:
        int: The index of the newly added node.
        None: If the node is within a no-fly zone and cannot be added.
    """
    from shapely.geometry import Point

    point = Point(lon, lat)
    if no_fly_zones_gdf.contains(point).any():
        print(f"{node_name} is within a no-fly zone and cannot be added.")
        return None

    new_node_idx = max(G.nodes) + 1 if len(G.nodes) > 0 else 0
    G.add_node(new_node_idx, pos=(lon, lat), name=node_name)

    pos = nx.get_node_attributes(G, "pos")
    pos[new_node_idx] = (lon, lat)
    nx.set_node_attributes(G, pos, "pos")

    for idx, row in health_facilities_gdf.iterrows():
        distance = geodesic((lat, lon), (row["latitude"], row["longitude"])).km
        if distance <= drone_range_km:
            line = LineString([point, row.geometry])

            if no_fly_zones_gdf.intersects(line).any():
                print(
                    f"Edge from {node_name} to {row['name']} intersects a no-fly zone, not adding."
                )
                continue  # Skip if the line intersects a no-fly zone

            edge_weight = calculate_edge_weight(
                line, roads_gdf, buildings_gdf, open_space_gdf, avoidance_zones_gdf
            )
            G.add_edge(new_node_idx, idx, weight=edge_weight)

    return new_node_idx


def download_land_use_data(place_name="Accra, Ghana"):
    """
    Downloads land use data (roads, buildings, open spaces) for a specified place using OSMnx.

    Args:
        place_name (str): The name of the place to download land use data for.

    Returns:
        tuple: A tuple containing GeoDataFrames for roads, buildings, and open spaces.
    """
    import osmnx as ox

    print("Downloading land use data...")

    roads = ox.graph_from_place(place_name, network_type="drive")
    roads_gdf = ox.graph_to_gdfs(roads, nodes=False, edges=True)

    buildings_gdf = ox.geometries_from_place(place_name, tags={"building": True})

    open_space_gdf = ox.geometries_from_place(place_name, tags={"leisure": "park"})

    print("Land use data downloaded successfully.")
    return roads_gdf, buildings_gdf, open_space_gdf
