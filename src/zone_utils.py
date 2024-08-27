import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

def create_circular_zone(lat, lon, radius):
    """
    Create a circular polygon around a point defined by latitude and longitude.

    Parameters:
    lat (float): Latitude of the center point.
    lon (float): Longitude of the center point.
    radius (float): Radius of the circle in meters.

    Returns:
    shapely.geometry.polygon.Polygon: Circular polygon around the given point.
    """
    return Point(lon, lat).buffer(radius / 111320)  # Convert meters to degrees (approximation)

def create_zones_gdf(zones):
    """
    Create a GeoDataFrame from a list of zone dictionaries.

    Parameters:
    zones (list): A list of dictionaries where each dictionary has keys 'latitude', 'longitude', and 'radius'.

    Returns:
    geopandas.GeoDataFrame: GeoDataFrame containing the zones as geometries.
    """
    return gpd.GeoDataFrame(
        zones, 
        geometry=[create_circular_zone(zone["latitude"], zone["longitude"], zone["radius"]) for zone in zones]
    )

def save_zones_to_geojson(gdf, filepath):
    """
    Save a GeoDataFrame to a GeoJSON file.

    Parameters:
    gdf (geopandas.GeoDataFrame): GeoDataFrame containing the geometries to save.
    filepath (str): Path to save the GeoJSON file.
    """
    gdf.to_file(filepath, driver="GeoJSON")

def plot_zones(G, no_fly_zones_gdf, avoidance_zones_gdf):
    """
    Plot the road network with no-fly zones and avoidance zones overlaid.

    Parameters:
    G (networkx.MultiDiGraph): The road network graph.
    no_fly_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing no-fly zones.
    avoidance_zones_gdf (geopandas.GeoDataFrame): GeoDataFrame containing avoidance zones.
    """
    fig, ax = ox.plot_graph(G, node_size=0.1, bgcolor='k', node_color='r', edge_linewidth=0.5, show=False, close=False)

    # Plot the no-fly zones as red transparent circles
    no_fly_zones_gdf.plot(ax=ax, color='red', alpha=0.3)

    # Plot the avoidance zones as yellow transparent circles
    avoidance_zones_gdf.plot(ax=ax, color='yellow', alpha=0.3)

    plt.show()

def clear_existing_maps(map_directory):
    """
    Clears out existing GeoJSON files in the specified map directory.

    Parameters:
    map_directory (str): The directory containing GeoJSON files to be cleared.
    """
    geojson_files = glob.glob(os.path.join(map_directory, "*.geojson"))
    for file in geojson_files:
        try:
            os.remove(file)
            print(f"Removed existing map file: {file}")
        except Exception as e:
            print(f"Error removing file {file}: {e}")