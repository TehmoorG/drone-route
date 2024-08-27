# common_route_utils.py
import logging
import pickle
import csv

def get_coordinates(lat_range, lon_range):
    while True:
        try:
            # Prompt user for latitude and longitude
            latitude = float(input("Enter the latitude (in decimal degrees): "))
            longitude = float(input("Enter the longitude (in decimal degrees): "))
            
            # Validate if the coordinates are within the specified bounds
            if lat_range[0] <= latitude <= lat_range[1] and lon_range[0] <= longitude <= lon_range[1]:
                print(f"Coordinates ({latitude}, {longitude}) are valid within the specified range.")
                return latitude, longitude
            else:
                print("Error: The coordinates are not within the valid range. Please try again.")
        except ValueError:
            print("Error: Please enter valid numeric values for latitude and longitude.")

def load_graph(graph_path='../output/simple_route.pkl'):
    try:
        with open(graph_path, 'rb') as f:
            G = pickle.load(f)
        print(f"Network graph loaded from '{graph_path}'.")
        return G
    except FileNotFoundError:
        print(f"Error: Graph file '{graph_path}' not found.")
        return None

def save_route_to_csv(G, shortest_path, pos, csv_file_path='../output/drone_route.csv'):
    route_data = []

    # Add start node
    start_pos = pos[shortest_path[0]]
    route_data.append({
        "label": "Start",
        "lat": start_pos[1],
        "longitude": start_pos[0]
    })

    # Add intermediate nodes (charging stations)
    for node in shortest_path[1:-1]:
        node_pos = pos[node]
        route_data.append({
            "label": f"Charging Station {node}",
            "lat": node_pos[1],
            "longitude": node_pos[0]
        })

    # Add end node
    end_pos = pos[shortest_path[-1]]
    route_data.append({
        "label": "End",
        "lat": end_pos[1],
        "longitude": end_pos[0]
    })

    # Write the data to a CSV file
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["label", "lat", "longitude"])
        writer.writeheader()
        writer.writerows(route_data)

    print(f"Route data saved to {csv_file_path}")

# Utility function to handle user inputs with validation
def get_drone_constraints():
    while True:
        try:
            drone_range_km = float(input("Enter the drone's maximum range (in km): "))
            payload_capacity_kg = float(input("Enter the drone's maximum payload capacity (in kg): "))
            if drone_range_km <= 0 or payload_capacity_kg <= 0:
                raise ValueError("Range and payload must be positive numbers.")
            logging.info(f"Drone constraints set: Range = {drone_range_km} km, Payload Capacity = {payload_capacity_kg} kg")
            return drone_range_km, payload_capacity_kg
        except ValueError as e:
            logging.error(f"Invalid input: {e}")
            print("Please enter valid numeric values greater than 0.")
