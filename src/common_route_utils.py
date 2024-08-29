"""
common_route_utils.py

This module provides utility functions that are commonly used across different drone routing scripts.
It includes functions for obtaining user inputs, loading and saving graph data, and handling
common drone constraints.

Functions:
- get_coordinates(lat_range, lon_range): Prompts the user to enter valid coordinates within a specified range.
- load_graph(graph_path): Loads a previously saved graph from a pickle file.
- save_route_to_csv(G, shortest_path, pos, csv_file_path): Saves a computed drone route to a CSV file.
- get_drone_constraints(): Prompts the user to input drone constraints (range and payload) with validation.
"""

import logging
import pickle
import csv


def get_coordinates(lat_range, lon_range):
    """
    Prompts the user to input valid latitude and longitude coordinates within a specified range.

    Args:
        lat_range (tuple): A tuple specifying the valid range of latitudes (min_lat, max_lat).
        lon_range (tuple): A tuple specifying the valid range of longitudes (min_lon, max_lon).

    Returns:
        tuple: A tuple containing the validated latitude and longitude (latitude, longitude).
    """
    while True:
        try:
            # Prompt user for latitude and longitude
            latitude = float(input("Enter the latitude (in decimal degrees): "))
            longitude = float(input("Enter the longitude (in decimal degrees): "))

            # Validate if the coordinates are within the specified bounds
            if (
                lat_range[0] <= latitude <= lat_range[1] and lon_range[0] <= longitude <= lon_range[1]
            ):
                print(
                    f"Coordinates ({latitude}, {longitude}) are valid within the specified range."
                )
                return latitude, longitude
            else:
                print(
                    "Error: The coordinates are not within the valid range. Please try again."
                )
        except ValueError:
            print(
                "Error: Please enter valid numeric values for latitude and longitude."
            )


def load_graph(graph_path="../output/simple_route.pkl"):
    """
    Loads a previously saved network graph from a pickle file.

    Args:
        graph_path (str): The file path of the pickle file to load the graph from.

    Returns:
        networkx.Graph: The loaded graph object.
        None: If the file is not found, returns None.
    """
    try:
        with open(graph_path, "rb") as f:
            G = pickle.load(f)
        print(f"Network graph loaded from '{graph_path}'.")
        return G
    except FileNotFoundError:
        print(f"Error: Graph file '{graph_path}' not found.")
        return None


def save_route_to_csv(G, shortest_path, pos, csv_file_path="../output/drone_route.csv"):
    """
    Saves the shortest path route of a drone to a CSV file.

    Args:
        G (networkx.Graph): The graph object containing the drone route.
        shortest_path (list): A list of nodes representing the shortest path.
        pos (dict): A dictionary of node positions keyed by node IDs.
        csv_file_path (str): The file path where the CSV file will be saved.

    Returns:
        None
    """
    route_data = []

    # Add start node
    start_pos = pos[shortest_path[0]]
    route_data.append(
        {"label": "Start", "lat": start_pos[1], "longitude": start_pos[0]}
    )

    # Add intermediate nodes (charging stations)
    for node in shortest_path[1:-1]:
        node_pos = pos[node]
        route_data.append(
            {
                "label": f"Charging Station {node}",
                "lat": node_pos[1],
                "longitude": node_pos[0],
            }
        )

    # Add end node
    end_pos = pos[shortest_path[-1]]
    route_data.append({"label": "End", "lat": end_pos[1], "longitude": end_pos[0]})

    # Write the data to a CSV file
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["label", "lat", "longitude"])
        writer.writeheader()
        writer.writerows(route_data)

    print(f"Route data saved to {csv_file_path}")


def get_drone_constraints():
    """
    Prompts the user to input the drone's maximum range and payload capacity, with validation.

    Returns:
        tuple: A tuple containing the validated drone range (in km) and payload capacity (in kg).
    """
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
