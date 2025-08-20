import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox
from typing import List, Optional
from pydantic import BaseModel

class RoutePathBuilderConfig(BaseModel):
    """
    A Pydantic model to validate the configuration for the RoutePathBuilder.
    """
    graph: nx.MultiDiGraph
    sort_key: List[str]  # Made mandatory
    grouping_col: Optional[str] = None
    lat_col: str = "latitude"
    lon_col: str = "longitude"

    class Config:
        arbitrary_types_allowed = True

class RoutePathBuilder:
    """
    Builds shortest paths (Dijkstra Algorithm) for consecutive GPS points.
    This version requires an explicit sort_key for correctness.
    """

    def __init__(self, config: RoutePathBuilderConfig):
        """
        Initializes the builder with a validated configuration object.
        """
        self.config = config

    # Static methods _get_shortest_path and _path_length_from_nodes remain unchanged...
    @staticmethod
    def _get_shortest_path(u: int, v: int, graph: nx.MultiDiGraph) -> List[int]:
        try:
            return nx.shortest_path(graph, u, v, weight="length", method="dijkstra")
        except nx.NetworkXNoPath:
            return []

    @staticmethod
    def _path_length_from_nodes(node_list: List[int], graph: nx.MultiDiGraph) -> float:
        if len(node_list) < 2:
            return np.nan
        total = 0.0
        for u, v in zip(node_list[:-1], node_list[1:]):
            edge_data = graph.get_edge_data(u, v)
            lengths = [edata.get("length", 0) for edata in edge_data.values()]
            total += min(lengths) if lengths else 0
        return total


    def build_routes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates routes from a DataFrame of GPS points.
        """
        df = df.copy()

        df = df.sort_values(by=self.config.sort_key).reset_index(drop=True)

        # 2. Create destination columns by shifting within each group or across the df
        if self.config.grouping_col:
            df["dest_lat"] = df.groupby(by=self.config.grouping_col)[self.config.lat_col].shift(-1)
            df["dest_lon"] = df.groupby(by=self.config.grouping_col)[self.config.lon_col].shift(-1)
        else:
            df["dest_lat"] = df[self.config.lat_col].shift(-1)
            df["dest_lon"] = df[self.config.lon_col].shift(-1)

        df = df.dropna(subset=["dest_lat", "dest_lon"]).reset_index(drop=True)

        # 3. Snap origin & destination coordinates to the nearest graph nodes
        df["origin_node"] = ox.nearest_nodes(
            self.config.graph, X=df[self.config.lon_col].values, Y=df[self.config.lat_col].values
        )
        df["dest_node"] = ox.nearest_nodes(
            self.config.graph, X=df["dest_lon"].values, Y=df["dest_lat"].values
        )

        # 4. Calculate paths, coordinates, and distances
        df["path_nodes"] = [
            self._get_shortest_path(u, v, self.config.graph)
            for u, v in zip(df["origin_node"], df["dest_node"])
        ]

        df = df[df["path_nodes"].str.len() > 0].reset_index(drop=True)

        df["path_coords"] = df["path_nodes"].apply(
            lambda nl: [(self.config.graph.nodes[n]["y"], self.config.graph.nodes[n]["x"]) for n in nl]
        )

        df["distance_m"] = df["path_nodes"].apply(
            lambda nl: self._path_length_from_nodes(nl, self.config.graph)
        )
        df["distance_m"] = df["distance_m"].fillna(0)

        # The final sort is no longer needed, as it was done at the beginning
        return df