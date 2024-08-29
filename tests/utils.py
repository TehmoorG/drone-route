# tests/utils.py
import pandas as pd
import geopandas as gpd
import networkx as nx
from shapely.geometry import Polygon


def mock_healthcare_facilities():
    data = {
        "name": ["Facility 1", "Facility 2", "Facility 3"],
        "latitude": [5.58, 5.60, 5.62],
        "longitude": [-0.13, -0.15, -0.17],
    }
    df = pd.DataFrame(data)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
    return gdf


def mock_zones():
    no_fly_zone = Polygon([(-0.18, 5.57), (-0.14, 5.57), (-0.14, 5.61), (-0.18, 5.61)])
    avoidance_zone = Polygon(
        [(-0.20, 5.59), (-0.16, 5.59), (-0.16, 5.63), (-0.20, 5.63)]
    )
    no_fly_gdf = gpd.GeoDataFrame(geometry=[no_fly_zone])
    avoidance_gdf = gpd.GeoDataFrame(geometry=[avoidance_zone])
    return no_fly_gdf, avoidance_gdf


def create_test_graph():
    G = nx.Graph()
    G.add_node(0, pos=(-0.137573559298005, 5.576227677008859), name="Start")
    G.add_node(
        1, pos=(-0.181442428851426, 5.590547823304689), name="Charging Station 204"
    )
    G.add_node(
        2, pos=(-0.203249626337936, 5.611922849863589), name="Charging Station 139"
    )
    G.add_node(3, pos=(-0.235185096524191, 5.643041503585579), name="End")
    G.add_edge(0, 1, weight=10)
    G.add_edge(1, 2, weight=10)
    G.add_edge(2, 3, weight=10)
    return G
