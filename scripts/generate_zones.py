import sys
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

import osmnx as ox
from src.zone_utils import create_zones_gdf, save_zones_to_geojson, plot_zones, clear_existing_maps

def get_user_input():
    """
    Collects user input for the generation of no-fly and avoidance zones.

    Returns:
    dict: A dictionary containing no-fly and avoidance zone data.
    """
    # Ask the user if they want visualization
    visualize = input("Would you like to visualize the zones? (yes/no): ").strip().lower()

    if visualize == 'yes':
        # If visualization is chosen, ask for the place name to download the map
        place_name = input("Enter the name of the place (e.g., 'Accra, Ghana'): ").strip()
        G = ox.graph_from_place(place_name, network_type='drive')
    else:
        # If no visualization, don't download the map
        G = None

    # Collect no-fly zone data
    no_fly_zones = []
    print("\nEnter no-fly zone coordinates and radius (in meters). Type 'done' when finished.")
    while True:
        lat = input("Enter latitude (or type 'done' to finish): ").strip()
        if lat.lower() == 'done':
            break
        lon = input("Enter longitude: ").strip()
        radius = input("Enter radius in meters: ").strip()
        no_fly_zones.append({"latitude": float(lat), "longitude": float(lon), "radius": float(radius)})

    # Collect avoidance zone data
    avoidance_zones = []
    print("\nEnter avoidance zone coordinates and radius (in meters). Type 'done' when finished.")
    while True:
        lat = input("Enter latitude (or type 'done' to finish): ").strip()
        if lat.lower() == 'done':
            break
        lon = input("Enter longitude: ").strip()
        radius = input("Enter radius in meters: ").strip()
        avoidance_zones.append({"latitude": float(lat), "longitude": float(lon), "radius": float(radius)})

    return {
        "visualize": visualize == 'yes',
        "graph": G,
        "no_fly_zones": no_fly_zones,
        "avoidance_zones": avoidance_zones
    }

def main():
    # Clear out the existing maps
    map_directory = os.path.abspath(os.path.join(current_dir, '..', 'map'))
    clear_existing_maps(map_directory)

    # Get user input
    user_input = get_user_input()

    # Create GeoDataFrames for no-fly zones and avoidance zones
    no_fly_zones_gdf = create_zones_gdf(user_input['no_fly_zones'])
    avoidance_zones_gdf = create_zones_gdf(user_input['avoidance_zones'])

    # Plot the zones if visualization is requested
    if user_input['visualize']:
        plot_zones(user_input['graph'], no_fly_zones_gdf, avoidance_zones_gdf)

    # Save the no-fly zones GeoDataFrame to GeoJSON
    save_zones_to_geojson(no_fly_zones_gdf, os.path.join(map_directory, "no_fly_zones.geojson"))

    # Save the avoidance zones GeoDataFrame to GeoJSON
    save_zones_to_geojson(avoidance_zones_gdf, os.path.join(map_directory, "avoidance_zones.geojson"))

    print("No-fly and avoidance zones have been saved to the 'map' directory.")

if __name__ == "__main__":
    main()
