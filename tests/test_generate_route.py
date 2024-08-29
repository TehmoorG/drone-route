from unittest.mock import patch
import os
import pandas as pd
from scripts.generate_simple_route import main as simple_route_main
from scripts.generate_advanced_route import main as advanced_route_main


@patch(
    "builtins.input",
    side_effect=[
        "7",
        "1.5",
        "5.576227677008859",
        "-0.137573559298005",
        "5.643041503585579",
        "-0.235185096524191",
    ],
)
def test_simple_route(mock_input):
    # Run the simple route generation
    simple_route_main()
    # Validate the generated route
    assert os.path.exists("../output/drone_route.csv")
    df = pd.read_csv("../output/drone_route.csv")
    expected_route = [
        ("Start", 5.576227677008859, -0.137573559298005),
        ("Charging Station 204", 5.590547823304689, -0.181442428851426),
        ("Charging Station 139", 5.611922849863589, -0.203249626337936),
        ("End", 5.643041503585579, -0.235185096524191),
    ]
    for idx, row in df.iterrows():
        assert (row["label"], row["lat"], row["longitude"]) == expected_route[idx]
    # Optionally keep or remove the file after validation
    os.remove("../output/drone_route.csv")


@patch(
    "builtins.input",
    side_effect=[
        "7",
        "1.5",
        "5.576227677008859",
        "-0.137573559298005",
        "5.643041503585579",
        "-0.235185096524191",
    ],
)
def test_advanced_route(mock_input):
    # Run the advanced route generation
    advanced_route_main()
    # Validate the generated route
    assert os.path.exists("../output/advanced_drone_route.csv")
    df = pd.read_csv("../output/advanced_drone_route.csv")
    expected_route = [
        ("Start", 5.576227677008859, -0.137573559298005),
        ("Charging Station 6", 5.584336246319907, -0.162356835325312),
        ("Charging Station 4", 5.590430560479291, -0.203872904657914),
        ("End", 5.643041503585579, -0.235185096524191),
    ]
    for idx, row in df.iterrows():
        assert (row["label"], row["lat"], row["longitude"]) == expected_route[idx]
    # Optionally keep or remove the file after validation
    os.remove("../output/advanced_drone_route.csv")
