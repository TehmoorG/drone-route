import sys
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(current_dir, "..")))

import logging
import geopandas as gpd
import pandas as pd
import networkx as nx
from src.common_route_utils import get_coordinates, load_graph, save_route_to_csv
from src.advanced_route_utils import (
    create_and_save_graph,
    add_node_to_graph,
    download_land_use_data,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

output_dir = "../output/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# Utility function to handle user inputs with validation
def get_drone_constraints():
    while True:
        try:
            drone_range_km = float(input("Enter the drone's maximum range (in km): "))
            payload_capacity_kg = float(
                input("Enter the drone's maximum payload capacity (in kg): ")
            )
            if drone_range_km <= 0 or payload_capacity_kg <= 0:
                raise ValueError("Range and payload must be positive numbers.")
            logging.info(
                f"Drone constraints set: Range = {drone_range_km} km, Payload Capacity = {payload_capacity_kg} kg"
            )
            return drone_range_km, payload_capacity_kg
        except ValueError as e:
            logging.error(f"Invalid input: {e}")
            print("Please enter valid numeric values greater than 0.")


# Main function
def main():
    # Define the latitude and longitude bounds for Accra
    lat_range = (5.47, 5.89)
    lon_range = (-0.24, -0.02)

    # Get drone constraints from the user
    drone_range_km, payload_capacity_kg = get_drone_constraints()

    # Load healthcare facilities data
    try:
        health_facilities_df = pd.read_csv("../data/accra_facilities_filtered.csv")
        health_facilities_gdf = gpd.GeoDataFrame(
            health_facilities_df,
            geometry=gpd.points_from_xy(
                health_facilities_df.longitude, health_facilities_df.latitude
            ),
        )
        logging.info("Healthcare facilities data loaded successfully.")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(
            "Healthcare facilities data file not found. Please check the file path."
        )
    except Exception as e:
        logging.error(f"Error loading healthcare facilities data: {e}")
        sys.exit("An error occurred while loading healthcare facilities data.")

    # Load no-fly zones and avoidance areas
    try:
        no_fly_zones_gdf = gpd.read_file("../map/no_fly_zones.geojson")
        avoidance_zones_gdf = gpd.read_file("../map/avoidance_zones.geojson")
        logging.info("No-fly zones and avoidance areas loaded successfully.")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(
            "No-fly zones or avoidance areas file not found. Please check the file path."
        )
    except Exception as e:
        logging.error(f"Error loading no-fly zones or avoidance areas: {e}")
        sys.exit("An error occurred while loading no-fly zones or avoidance areas.")

    # Download land use data using OSMnx
    try:
        roads_gdf, buildings_gdf, open_space_gdf = download_land_use_data(
            "Accra, Ghana"
        )
        logging.info("Land use data downloaded successfully.")
    except Exception as e:
        logging.error(f"Error downloading land use data: {e}")
        sys.exit("An error occurred while downloading land use data.")

    graph_path = os.path.join(output_dir, "advanced_route.pkl")

    # Check if the graph already exists and load it, otherwise create and save it
    G = load_graph(graph_path)
    if G is None:
        create_and_save_graph(
            health_facilities_gdf,
            roads_gdf,
            buildings_gdf,
            open_space_gdf,
            no_fly_zones_gdf,
            avoidance_zones_gdf,
            drone_range_km,
            graph_path,
        )
        G = load_graph(graph_path)
        if G is None:
            logging.error("Failed to create and load the graph.")
            sys.exit("Failed to create and load the graph.")

    # Get start and end coordinates from the user
    print("Please provide the start coordinates:")
    start_lat, start_lon = get_coordinates(lat_range, lon_range)
    print("Please provide the end coordinates:")
    end_lat, end_lon = get_coordinates(lat_range, lon_range)

    # Add start and end nodes to the graph
    start_node = add_node_to_graph(
        G,
        start_lat,
        start_lon,
        "Start",
        health_facilities_gdf,
        roads_gdf,
        buildings_gdf,
        open_space_gdf,
        no_fly_zones_gdf,
        avoidance_zones_gdf,
        drone_range_km,
    )
    end_node = add_node_to_graph(
        G,
        end_lat,
        end_lon,
        "End",
        health_facilities_gdf,
        roads_gdf,
        buildings_gdf,
        open_space_gdf,
        no_fly_zones_gdf,
        avoidance_zones_gdf,
        drone_range_km,
    )

    # If start and end nodes are successfully added, proceed with pathfinding
    if start_node is not None and end_node is not None:
        try:
            shortest_path = nx.dijkstra_path(G, start_node, end_node, weight="weight")
            logging.info(f"Shortest path found: {shortest_path}")

            pos = nx.get_node_attributes(G, "pos")

            # Handle nodes without positions
            missing_pos_nodes = [node for node in G.nodes if node not in pos]
            if missing_pos_nodes:
                logging.warning(
                    f"Nodes without positions detected: {missing_pos_nodes}"
                )
                G.remove_nodes_from(missing_pos_nodes)
                logging.info(f"Removed nodes without positions: {missing_pos_nodes}")

            # Save the route to a CSV file
            csv_file_path = os.path.join(output_dir, "advanced_drone_route.csv")
            save_route_to_csv(G, shortest_path, pos, csv_file_path)

        except nx.NetworkXNoPath:
            logging.error("No path found between the start and end nodes.")
            print("Error: No path found between the start and end nodes.")
        except Exception as e:
            logging.error(f"An unexpected error occurred during pathfinding: {e}")
    else:
        logging.warning(
            "Start or end node was not added due to being within a no-fly zone."
        )
        print(
            "Error: Start or end node was not added due to being within a no-fly zone."
        )


if __name__ == "__main__":
    main()
