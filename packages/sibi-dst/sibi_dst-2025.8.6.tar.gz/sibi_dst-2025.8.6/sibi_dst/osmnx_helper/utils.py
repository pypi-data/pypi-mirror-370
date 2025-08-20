import math
import os
import pickle
from urllib.parse import urlencode, urlsplit, urlunsplit

import folium
import geopandas as gpd
import numpy as np
import osmnx as ox
from geopy.distance import geodesic


#
# options = {
#    'ox_files_save_path': ox_files_save_path,
#    'network_type': 'drive',
#    'place': 'Costa Rica',
#    'files_prefix': 'costa-rica-',
# }
# Usage example
# handler = PBFHandler(**options)
# handler.load()


class PBFHandler:
    """
    Handles the creation, management, and visualization of graph data derived
    from .pbf (Protocolbuffer Binary Format) files. This class enables the
    loading, processing, saving, and reutilization of graph, node, and edge
    data for geographical regions, supporting verbose mode for detailed outputs.

    :ivar graph: The generated graph object representing the spatial network; can be None if not yet loaded or processed.
    :type graph: Optional[NetworkX.Graph]
    :ivar nodes: GeoDataFrame representing the nodes of the graph; can be None if not yet loaded or processed.
    :type nodes: Optional[geopandas.GeoDataFrame]
    :ivar edges: GeoDataFrame representing the edges of the graph; can be None if not yet loaded or processed.
    :type edges: Optional[geopandas.GeoDataFrame]
    :ivar rebuild: Indicates whether to rebuild the graph data, ignoring any existing cached files. Default is ``False``.
    :type rebuild: bool
    :ivar verbose: Enables verbose mode to provide detailed status messages during operations. Default is ``False``.
    :type verbose: bool
    :ivar place: The name of the geographical region to process with OpenStreetMap. Default is ``Costa Rica``.
    :type place: str
    :ivar filepath: The path to the directory where the graph, nodes, and edges pickle files are saved. Default is ``gis_data/``.
    :type filepath: str
    :ivar file_prefix: The prefix for the filenames of the saved graph, node, and edge pickle files. Default is ``costa-rica-``.
    :type file_prefix: str
    :ivar network_type: The type of network to extract from OpenStreetMap, such as "all" or other specific network types. Default is ``all``.
    :type network_type: str
    :ivar graph_file: Full path of the file to save or load the graph data as a pickle file.
    :type graph_file: str
    :ivar node_file: Full path of the file to save or load the graph's node data as a pickle file.
    :type node_file: str
    :ivar edge_file: Full path of the file to save or load the graph's edge data as a pickle file.
    :type edge_file: str
    """
    def __init__(self, **kwargs):
        self.graph = None
        self.nodes = None
        self.edges = None
        self.rebuild = kwargs.setdefault("rebuild", False)
        self.verbose = kwargs.setdefault("verbose", False)
        self.place = kwargs.setdefault('place', 'Costa Rica')
        self.filepath = kwargs.setdefault('ox_files_save_path', "gis_data/")
        self.file_prefix = kwargs.setdefault('file_prefix', 'costa-rica-')
        self.network_type = kwargs.setdefault('network_type', 'all')
        self.graph_file = f"{self.filepath}{self.file_prefix}graph.pkl"
        self.node_file = f"{self.filepath}{self.file_prefix}nodes.pkl"
        self.edge_file = f"{self.filepath}{self.file_prefix}edges.pkl"

    def load(self):
        """
        Loads the required data files for processing. If the files do not exist or
        if the `rebuild` flag is set to True, it will process and recreate the
        necessary data from the source. Otherwise, it will load the data from
        existing pickle files. This function ensures the target directory exists,
        and processes files conditionally based on their presence.

        :param verbose: Flag to control the verbosity of the function's output.
        :param rebuild: Indicates whether the data should be rebuilt from the raw
            source files.
        :param graph_file: Path to the graph file to be loaded or rebuilt.
        :param node_file: Path to the node file to be loaded or rebuilt.
        :param edge_file: Path to the edge file to be loaded or rebuilt.
        :param filepath: Path to the directory where files are processed and saved.

        :return: None
        """
        if self.verbose:
            print("Loading data...")

        files_to_check = [self.graph_file, self.node_file, self.edge_file]

        if self.rebuild:
            for file in files_to_check:
                if os.path.exists(file):
                    os.remove(file)
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath, exist_ok=True)
            # self.process_pbf()
            # self.save_to_pickle()
        if not all(os.path.exists(f) for f in files_to_check):
            self.process_pbf()
            self.save_to_pickle()
        else:
            self.load_from_pickle()

        if self.verbose:
            print("Data loaded successfully.")

    def process_pbf(self):
        """
        Processes the Protocolbuffer Binary Format (PBF) data specified for a given place by
        utilizing the OSMnx library to create a graph representation and extracts nodes and
        edges into GeoDataFrames. The function provides verbose output if enabled.

        :param self: Refers to the current instance of the class containing this method.

        :param self.verbose: bool
            A flag to control verbose output. If True, detailed processing status messages are
            logged to the console.

        :param self.place: str
            The name or description of the geographic place for which PBF data is processed. It
            is used to construct a graph representation of the place.

        :param self.network_type: str
            The type of network graph to be created, typically one of 'all', 'walk', 'drive',
            etc., reflecting the type of paths or streets included in the graph.

        :return: None
            This function does not return a value, but updates class attributes ``graph``,
            ``nodes``, and ``edges``.

        :raises Exception:
            Raises a general exception when there is an error in processing the PBF data. Error
            details are printed when verbose output is enabled.
        """
        try:
            if self.verbose:
                print(f"Processing PBF for {self.place}...")

            self.graph = ox.graph_from_place(self.place, network_type=self.network_type)
            self.nodes, self.edges = ox.graph_to_gdfs(self.graph)

            if self.verbose:
                print("PBF processed successfully.")
        except Exception as e:
            print(f"Error processing PBF: {e}")
            raise

    def save_to_pickle(self):
        """
        Saves data, including graph, nodes, and edges, to pickle files. Each data object is
        saved to its corresponding file if available. If verbose mode is enabled, prints
        messages indicating the saving progress and success.

        :param self:
            Represents the instance of the class that contains attributes `graph_file`,
            `graph`, `node_file`, `nodes`, `edge_file`, `edges`, and `verbose`. These
            attributes determine the files to save to and the data to save.

        :raises Exception:
            Raises an exception if an error occurs during the saving process.

        :return:
            None
        """
        try:
            if self.verbose:
                print("Saving data to pickle files...")

            data_to_save = {
                self.graph_file: self.graph,
                self.node_file: self.nodes,
                self.edge_file: self.edges
            }

            for file, data in data_to_save.items():
                if data is not None:
                    with open(file, 'wb') as f:
                        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

            if self.verbose:
                print("Data saved to pickle files successfully.")
        except Exception as e:
            print(f"Error saving to pickle: {e}")
            raise

    def load_from_pickle(self):
        """
        Loads data from pickle files specified by the attributes `graph_file`, `node_file`,
        and `edge_file` and assigns them to the corresponding attributes `graph`,
        `nodes`, and `edges`, respectively. Displays verbose messages during the load
        process if the `verbose` attribute is set to True.

        :raises Exception: If an error occurs during reading or deserialization of the
                           pickle files.
        """
        try:
            if self.verbose:
                print("Loading data from pickle files...")

            files_to_load = {
                self.graph_file: 'graph',
                self.node_file: 'nodes',
                self.edge_file: 'edges'
            }

            for file, attr in files_to_load.items():
                with open(file, 'rb') as f:
                    setattr(self, attr, pickle.load(f))

            if self.verbose:
                print("Data loaded from pickle files successfully.")
        except Exception as e:
            print(f"Error loading from pickle: {e}")
            raise

    def plot_graph(self):
        """
        Plots the loaded graph using the OSMnx library.

        This method checks if a graph is loaded and, if available, plots it. Outputs
        verbose messages during the process if verbosity is enabled.

        :raises Exception: Raises if an error occurs during the plotting process.
        :return: None
        """
        try:
            if self.graph is not None:
                if self.verbose:
                    print("Plotting the graph...")
                ox.plot_graph(self.graph)
                if self.verbose:
                    print("Graph plotted successfully.")
            else:
                print("Graph is not loaded. Please load a PBF file first.")
        except Exception as e:
            print(f"Error plotting the graph: {e}")
            raise


def get_bounding_box_from_points(gps_points, margin=0.001):
    """
    Calculates a bounding box from a list of GPS points, with an optional margin added
    to expand the bounding box in all directions. The function iterates over the GPS
    points to determine the maximum and minimum latitude and longitude values, then
    applies the specified margin to calculate the bounding box's boundaries.

    :param gps_points: A list of GPS points, where each point is represented as a tuple
        containing a latitude and a longitude (latitude, longitude).
    :type gps_points: list[tuple[float, float]]
    :param margin: An optional margin value to expand the bounding box in all directions.
        Default value is 0.001.
    :type margin: float
    :return: A tuple containing the bounding box boundaries in the following order:
        north (maximum latitude), south (minimum latitude), east (maximum longitude),
        and west (minimum longitude), each adjusted with the margin.
    :rtype: tuple[float, float, float, float]
    """
    latitudes = [point[0] for point in gps_points]
    longitudes = [point[1] for point in gps_points]

    north = max(latitudes) + margin
    south = min(latitudes) - margin
    east = max(longitudes) + margin
    west = min(longitudes) - margin

    return north, south, east, west


def add_arrows(map_object, locations, color, n_arrows):
    """
    Adds directional arrows to a map object to indicate paths or flows along a polyline
    defined by the given locations.

    The function computes directional arrows based on the locations list, places them
    along the defined path at intervals determined by the number of arrows, and adds
    these arrows to the specified `map_object`.

    .. note::
        The function works optimally when the number of locations is greater than two.

    :param map_object: The folium map object to which the directional arrows will be added.
    :param locations: A list containing tuples of latitude and longitude values that define
        the polyline. Each tuple represents a geographic point.
    :type locations: list[tuple[float, float]]
    :param color: The color to be used for the directional arrows.
    :type color: str
    :param n_arrows: The number of arrows to be drawn along the path.
    :type n_arrows: int
    :return: The modified folium map object containing the added arrows.
    :rtype: folium.Map
    """
    # Get the number of locations
    n = len(locations)

    # If there are more than two points...
    if n > 2:
        # Add arrows along the path
        for i in range(0, n - 1, n // n_arrows):
            # Get the start and end point for this segment
            start, end = locations[i], locations[i + 1]

            # Calculate the direction in which to place the arrow
            rotation = -np.arctan2((end[1] - start[1]), (end[0] - start[0])) * 180 / np.pi

            folium.RegularPolygonMarker(location=end,
                                        fill_color=color,
                                        number_of_sides=2,
                                        radius=6,
                                        rotation=rotation).add_to(map_object)
    return map_object


def extract_subgraph(G, north, south, east, west):
    """
    Extracts a subgraph from the input graph `G` within a specified bounding box. The bounding
    box is defined by its north, south, east, and west coordinates. The function identifies
    nodes from the graph that lie within this bounding box and creates a subgraph containing
    only these nodes and their corresponding edges.

    :param G: The input graph representing the original main graph.
    :type G: networkx.Graph
    :param north: The northern latitude that defines the upper boundary of the bounding box.
    :type north: float
    :param south: The southern latitude that defines the lower boundary of the bounding box.
    :type south: float
    :param east: The eastern longitude that defines the right boundary of the bounding box.
    :type east: float
    :param west: The western longitude that defines the left boundary of the bounding box.
    :type west: float
    :return: A subgraph extracted from the input graph `G` containing nodes and edges within
             the specified bounding box.
    :rtype: networkx.Graph
    """
    # Create a bounding box polygon
    # from osmnx v2 this is how it is done
    if ox.__version__ >= '2.0':
        bbox_poly = gpd.GeoSeries([ox.utils_geo.bbox_to_poly(bbox=(west, south, east, north))])
    else:
        bbox_poly = gpd.GeoSeries([ox.utils_geo.bbox_to_poly(north, south, east, west)])

    # Get nodes GeoDataFrame
    nodes_gdf = ox.graph_to_gdfs(G, nodes=True, edges=False)

    # Find nodes within the bounding box
    nodes_within_bbox = nodes_gdf[nodes_gdf.geometry.within(bbox_poly.geometry.unary_union)]

    # Create subgraph
    subgraph = G.subgraph(nodes_within_bbox.index)

    return subgraph


def get_distance_between_points(point_a, point_b, unit='km'):
    """
    Calculate the geographical distance between two points on Earth.

    This function computes the distance between two points on the Earth's surface
    specified in their geographical coordinates (latitude, longitude). The calculation
    employs the geodesic distance, which represents the shortest distance between
    two points on the Earth's surface. The distance can be returned in different units of
    measurement depending on the provided parameter.

    :param point_a: A tuple representing the latitude and longitude of the first
        point in decimal degrees (e.g., (latitude, longitude)). Must be a tuple of
        two float values.
    :param point_b: A tuple representing the latitude and longitude of the second
        point in decimal degrees (e.g., (latitude, longitude)). Must be a tuple of
        two float values.
    :param unit: A string value representing the unit of the calculated distance. Can be
        'km' for kilometers (default), 'm' for meters, or 'mi' for miles.
    :return: A float value of the distance between the two points in the specified unit.
        Returns 0 if the input validation fails or the specified unit is invalid.
    """
    if not isinstance(point_a, tuple) or len(point_a) != 2:
        return 0
    if not all(isinstance(x, float) and not math.isnan(x) for x in point_a):
        return 0
    if not isinstance(point_b, tuple) or len(point_b) != 2:
        return 0
    if not all(isinstance(x, float) and not math.isnan(x) for x in point_b):
        return 0
    distance = geodesic(point_a, point_b)
    if unit == 'km':
        return distance.kilometers
    elif unit == 'm':
        return distance.meters
    elif unit == 'mi':
        return distance.miles
    else:
        return 0


tile_options = {
    "OpenStreetMap": "OpenStreetMap",
    "CartoDB": "cartodbpositron",
    "CartoDB Voyager": "cartodbvoyager"
}


def attach_supported_tiles(map_object, default_tile="OpenStreetMap"):
    """
    Attaches supported tile layers to a given folium map object, excluding the
    default tile layer, to provide layer selection functionality in the map.

    This function allows dynamic addition of multiple tile layers to the map
    object while avoiding duplication of the default tile. By filtering out the
    default tile, it prevents redundancy and ensures a cleaner map interface.

    :param map_object: The folium map object to which the tile layers will be added.
        It must be an instance of Folium's Map class or a compatible map object.
    :param default_tile: The name of the default tile layer to exclude from the
        list of tiles added to the map. If not specified, defaults to 'OpenStreetMap'.
    :return: None. The function modifies the provided map object in place.
    """
    # Normalize the default tile name to lowercase for comparison
    normalized_default_tile = default_tile.lower()

    # Filter out the default tile layer from the options to avoid duplication
    tile_options_filtered = {k: v for k, v in tile_options.items() if v.lower() != normalized_default_tile}

    for tile, description in tile_options_filtered.items():
        folium.TileLayer(name=tile, tiles=description, show=False).add_to(map_object)


def get_graph(**options):
    """
    Generates and returns a graph along with its nodes and edges based on the
    provided options. The function initializes a PBFHandler instance with the
    given options, processes any data required, and retrieves the resulting
    graph structure.

    :param options: Variable-length keyword arguments passed to initialize the
                    PBFHandler instance. These parameters play a role in
                    determining how the graph data is processed and structured.
    :return: Returns a tuple containing three elements:
             - The generated graph object
             - The list or collection of nodes within the graph
             - The list or collection of edges that describe relationships
               between nodes in the graph
    """
    if not options:
        raise ValueError("No options provided to PBFHandler for graph creation.")
    handler = PBFHandler(**options)
    handler.load()
    return handler.graph, handler.nodes, handler.edges


def add_query_params(url, params):
    """
    Update the query parameters of a given URL with new parameters.

    This function takes a URL and a dictionary of parameters, merges these
    parameters with the existing parameters in the URL, and returns a new URL
    with updated query parameters.

    :param url: The original URL whose query parameters are to be updated,
        including the scheme, netloc, path, and optional query string and fragment.
    :type url: str
    :param params: A dictionary containing the new parameters to be added or updated
        in the query string of the given URL.
    :type params: dict
    :return: A new URL with updated query parameters after merging the original
        and new parameters.
    :rtype: str
    """
    # Parse the original URL
    url_components = urlsplit(url)

    # Parse original query parameters and update with new params
    original_params = dict([tuple(pair.split('=')) for pair in url_components.query.split('&') if pair])
    original_params.update(params)

    # Construct the new query string
    new_query_string = urlencode(original_params)

    # Construct the new URL
    new_url = urlunsplit((
        url_components.scheme,
        url_components.netloc,
        url_components.path,
        new_query_string,
        url_components.fragment
    ))

    return new_url


