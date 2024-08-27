import sys
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

import pandas as pd
import geopandas as gpd
import networkx as nx
import logging
from src.common_route_utils import get_coordinates, load_graph, save_route_to_csv, get_drone_constraints
from src.simple_route_utils import create_and_save_graph, add_node_to_graph

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Main function
def main():
    # Define the latitude and longitude bounds for Accra
    lat_range = (5.47, 5.89)
    lon_range = (-0.24, -0.02)

    # Get drone constraints from the user
    drone_range_km, payload_capacity_kg = get_drone_constraints()

    # Load healthcare facilities data
    try:
        health_facilities_df = pd.read_csv('../data/accra_facilities_filtered.csv')
        health_facilities_gdf = gpd.GeoDataFrame(
            health_facilities_df, 
            geometry=gpd.points_from_xy(health_facilities_df.longitude, health_facilities_df.latitude)
        )
        logging.info("Healthcare facilities data loaded successfully.")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit("Healthcare facilities data file not found. Please check the file path.")
    except Exception as e:
        logging.error(f"Error loading healthcare facilities data: {e}")
        sys.exit("An error occurred while loading healthcare facilities data.")

    # Load no-fly zones and avoidance areas
    try:
        no_fly_zones_gdf = gpd.read_file('../map/no_fly_zones.geojson')
        avoidance_zones_gdf = gpd.read_file('../map/avoidance_zones.geojson')
        logging.info("No-fly zones and avoidance areas loaded successfully.")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit("No-fly zones or avoidance areas file not found. Please check the file path.")
    except Exception as e:
        logging.error(f"Error loading no-fly zones or avoidance areas: {e}")
        sys.exit("An error occurred while loading no-fly zones or avoidance areas.")

    # Load or create the graph
    G = load_graph()
    if G is None:
        create_and_save_graph(health_facilities_gdf, no_fly_zones_gdf, avoidance_zones_gdf, drone_range_km)
        G = load_graph()
        if G is None:
            logging.error("Failed to create and load the graph.")
            sys.exit("Failed to create and load the graph.")

    # Get start and end coordinates from the user
    print("Please provide the start coordinates:")
    start_lat, start_lon = get_coordinates(lat_range, lon_range)
    print("Please provide the end coordinates:")
    end_lat, end_lon = get_coordinates(lat_range, lon_range)

    # Add start and end nodes to the graph
    start_node = add_node_to_graph(G, start_lat, start_lon, 'Start', health_facilities_gdf, no_fly_zones_gdf, avoidance_zones_gdf, drone_range_km)
    end_node = add_node_to_graph(G, end_lat, end_lon, 'End', health_facilities_gdf, no_fly_zones_gdf, avoidance_zones_gdf, drone_range_km)

    # If start and end nodes are successfully added, proceed with pathfinding
    if start_node is not None and end_node is not None:
        try:
            shortest_path = nx.dijkstra_path(G, start_node, end_node, weight='weight')
            logging.info(f"Shortest path found: {shortest_path}")
            pos = nx.get_node_attributes(G, 'pos')
            save_route_to_csv(G, shortest_path, pos)
        except nx.NetworkXNoPath:
            logging.error("No path found between the start and end nodes.")
            print("No path found between the start and end nodes.")
        except Exception as e:
            logging.error(f"An unexpected error occurred during pathfinding: {e}")
    else:
        logging.warning("Start or end node was not added due to being within a no-fly zone.")
        print("Start or end node was not added due to being within a no-fly zone.")

if __name__ == "__main__":
    main()
