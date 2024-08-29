import sys
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(current_dir, "..")))


import pytest
import networkx as nx
import pandas as pd
import pickle
from src.common_route_utils import get_coordinates, load_graph, save_route_to_csv
from tests.utils import create_test_graph


def test_load_graph():
    G = create_test_graph()
    with open("../output/test_graph.gpickle", "wb") as f:
        pickle.dump(G, f)
    with open("../output/test_graph.gpickle", "rb") as f:
        loaded_G = pickle.load(f)
    assert len(loaded_G.nodes) == len(G.nodes)
    os.remove("../output/test_graph.gpickle")


def test_save_route_to_csv():
    G = create_test_graph()
    pos = nx.get_node_attributes(G, "pos")
    save_route_to_csv(G, [0, 1, 2, 3], pos, "../output/test_route.csv")
    df = pd.read_csv("../output/test_route.csv")
    assert len(df) == 4
    os.remove("../output/test_route.csv")
