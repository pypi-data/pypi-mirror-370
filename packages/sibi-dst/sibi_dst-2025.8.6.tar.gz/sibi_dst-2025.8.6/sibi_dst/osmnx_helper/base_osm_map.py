from __future__ import annotations

import html
from abc import abstractmethod

import folium
import geopandas as gpd
import numpy as np
import osmnx as ox
from folium.plugins import Fullscreen


class BaseOsmMap:
    """
    BaseOsmMap class serves as a foundational class for creating and managing maps
    using OpenStreetMap data. It integrates features from libraries like osmnx and
    folium to facilitate visualization, tile layer management, bounding box handling,
    and nearest node calculation for geographic coordinates.

    The class is designed to be subclassed, enabling customization of map processing
    logic while providing core functionalities needed for map creation and manipulation.

    :ivar tile_options: Dictionary containing options for pre-defined tile layers.
                        Keys represent display names while values represent tile layer configurations.
    :type tile_options: dict
    :ivar bounds: Default map bounds representing geographical extents for Costa Rica.
    :type bounds: list[list[float]]
    :ivar osmnx_graph: Input graph representing OpenStreetMap network data, used for
                       operations like subgraph extraction and nearest node calculation.
    :type osmnx_graph: networkx.classes.multidigraph.MultiDiGraph
    :ivar df: DataFrame containing data points with geographic coordinates. It must
              not be empty and should include latitude and longitude columns as specified
              in `lat_col` and `lon_col`.
    :type df: pandas.DataFrame
    :ivar lat_col: Name of the column in `df` representing latitude coordinates of data points.
    :type lat_col: str
    :ivar lon_col: Name of the column in `df` representing longitude coordinates of data points.
    :type lon_col: str
    :ivar osm_map: Folium Map object that serves as a container for geographic visualization.
                   This is dynamically initialized based on the provided data.
    :type osm_map: folium.Map
    :ivar G: Subgraph of the provided `osmnx_graph`, extracted based on bounding box
             derived from the input data.
    :type G: networkx.classes.multidigraph.MultiDiGraph
    :ivar map_html_title: HTML-escaped title for map visualization, shown on the interactive map.
    :type map_html_title: str
    :ivar zoom_start: Initial zoom level for the map when rendered.
    :type zoom_start: int
    :ivar fullscreen: Boolean option to enable or disable fullscreen control on the interactive map.
    :type fullscreen: bool
    :ivar fullscreen_position: Position of the fullscreen control on the map, e.g., 'topright'.
    :type fullscreen_position: str
    :ivar tiles: Default tile layer to be used for the map visualization.
    :type tiles: str
    :ivar verbose: Boolean flag indicating if verbose logging of operations should be enabled.
    :type verbose: bool
    :ivar sort_keys: Keys to sort the DataFrame by, if applicable, before processing.
    :type sort_keys: list[str] or None
    :ivar dt_field: Column name in `df` representing datetimes, if applicable, for specialized processing.
    :type dt_field: str or None
    :ivar dt: List of datetime objects extracted from `dt_field` in `df`, dynamically initialized.
    :type dt: list[datetime.datetime] or None
    :ivar calc_nearest_nodes: Boolean flag to indicate whether nearest nodes to the input
                              points should be calculated from `osmnx_graph`.
    :type calc_nearest_nodes: bool
    :ivar nearest_nodes: List of nearest node IDs for each point in the input data, if calculated.
    :type nearest_nodes: list[int] or None
    :ivar max_bounds: Boolean indicating whether bounds (default to Costa Rica) should be applied
                      to fit the map within those limits interactively.
    :type max_bounds: bool
    """
    tile_options = {
        "OpenStreetMap": "OpenStreetMap",
        "CartoDB": "cartodbpositron",
        "CartoDB Voyager": "cartodbvoyager"
    }
    # Set default bounds for Costa Rica
    bounds = [[8.0340, -85.9417], [11.2192, -82.5566]]

    def __init__(self, osmnx_graph=None, df=None, **kwargs):
        """
        Initializes a map visualization handler with input parameters for managing and displaying
        spatial data in conjunction with an OSMnx graph. It validates input parameters for completeness
        and correctness, and configures internal attributes for the visualization of map layers.

        :param osmnx_graph: The OSMnx graph to be used for spatial data processing.
        :param df: The pandas DataFrame containing spatial data.
        :param kwargs: Additional keyword arguments for customization.
        :type osmnx_graph: object
        :type df: pandas.DataFrame
        :type kwargs: dict

        :raises ValueError: If `osmnx_graph` is not provided.
        :raises ValueError: If `df` is not provided.
        :raises ValueError: If the provided `df` is empty.

        :attribute df: A copy of the provided DataFrame.
        :attribute osmnx_graph: The input OSMnx graph used for spatial data operations.
        :attribute lat_col: The name of the column in `df` containing latitude values.
        :attribute lon_col: The name of the column in `df` containing longitude values.
        :attribute osm_map: Internal representation of the map; initialized to None.
        :attribute G: Placeholder for graph-related data; initialized to None.
        :attribute map_html_title: Sanitized HTML title to be used in rendered map outputs.
        :attribute zoom_start: The initial zoom level for the map visualization (default: 13).
        :attribute fullscreen: Boolean flag to enable fullscreen map display (default: True).
        :attribute fullscreen_position: The position of the fullscreen control button
            (default: 'topright').
        :attribute tiles: The tile set to be used for the map visualization (default: 'OpenStreetMap').
        :attribute verbose: Boolean flag for enabling verbose output (default: False).
        :attribute sort_keys: Optional parameter dictating sorting order for keys (default: None).
        :attribute dt_field: Optional name of the datetime field in the DataFrame (default: None).
        :attribute dt: Placeholder for date/time data; initialized to None.
        :attribute calc_nearest_nodes: Boolean flag to calculate nearest nodes to coordinates
            (default: False).
        :attribute nearest_nodes: Placeholder for nearest nodes data; initialized to None.
        :attribute max_bounds: Boolean flag to restrict the map view to maximum bounds
            (default: False).

        :note: This class also initializes necessary internal functionalities including DataFrame
            pre-processing (`_prepare_df`) and base map setup (`_initialise_map`).
        """
        if osmnx_graph is None:
            raise ValueError('osmnx_graph must be provided')
        if df is None:
            raise ValueError('df must be provided')
        if df.empty:
            raise ValueError('df must not be empty')
        self.df = df.copy()
        self.osmnx_graph = osmnx_graph
        self.lat_col = kwargs.get('lat_col', 'latitude')
        self.lon_col = kwargs.get('lon_col', 'longitude')
        self.osm_map = None
        self.G = None
        self.map_html_title = self._sanitize_html(kwargs.get('map_html_title', 'OSM Basemap'))

        self.zoom_start = kwargs.pop('zoom_start', 13)
        self.fullscreen = kwargs.pop('fullscreen', True)
        self.fullscreen_position = kwargs.pop('fullscreen_position', 'topright')
        self.tiles = kwargs.pop('tiles', 'OpenStreetMap')
        self.verbose = kwargs.pop('verbose', False)
        self.sort_keys = kwargs.pop('sort_keys', None)
        self.dt_field = kwargs.pop('dt_field', None)
        self.dt = None
        self.calc_nearest_nodes = kwargs.pop('calc_nearest_nodes', False)
        self.nearest_nodes = None
        self.max_bounds = kwargs.pop('max_bounds', False)
        self._prepare_df()
        self._initialise_map()


    def _prepare_df(self):
        """
        Prepares the underlying DataFrame for further processing.

        This method performs several operations on the DataFrame, such as sorting,
        resetting the index, and extracting relevant columns into various lists.
        Additionally, it calculates the nearest nodes from an OSMnx graph if
        required. The operations are governed by instance attributes and their
        current states.

        :raises AttributeError: If required attributes for processing are not
            correctly set or do not exist in the DataFrame.
        :param self: Object that contains the DataFrame (df) and other related
            attributes required for processing.
        :return: None
        """
        if self.sort_keys:
            self.df.sort_values(by=self.sort_keys, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.gps_points = self.df[[self.lat_col, self.lon_col]].values.tolist()
        if self.dt_field is not None:
            self.dt = self.df[self.dt_field].tolist()

        if self.calc_nearest_nodes:
            self.nearest_nodes = ox.distance.nearest_nodes(self.osmnx_graph, X=self.df[self.lon_col],
                                                           Y=self.df[self.lat_col])


    def _initialise_map(self):
        """
        Initializes an OpenStreetMap (OSM) map instance and extracts a subgraph of map
        data based on provided GPS points. The map's central location is calculated
        as the mean of the latitudinal and longitudinal values of the GPS points.
        Additionally, a bounding box is determined to extract the relevant section
        of the map graph.

        :return: None
        """
        gps_array = np.array(self.gps_points)
        mean_latitude = np.mean(gps_array[:, 0])
        mean_longitude = np.mean(gps_array[:, 1])
        self.osm_map = folium.Map(location=[mean_latitude, mean_longitude], zoom_start=self.zoom_start,
                                  tiles=self.tiles, max_bounds=self.max_bounds)
        north, south, east, west = self._get_bounding_box_from_points(margin=0.001)
        self.G = self._extract_subgraph(north, south, east, west)


    def _attach_supported_tiles(self):
        """
        Attach supported tile layers from the provided tile options to the map object.

        This method normalizes the default tile layer name and ensures that it is not
        duplicated in the map by filtering out the default tile from the `tile_options`.
        Then, it iterates over the filtered tile options and attaches each supported
        tile layer to the map object using the folium library.

        :raises KeyError: If any key in `tile_options` is invalid or not found.

        :param self:
            The instance of the class. It is expected to have the following attributes:
                - tiles (str): The name of the default tile layer.
                - tile_options (Dict[str, str]): A dictionary of tile layer names
                  and their associated URLs.
                - osm_map (folium.Map): The map object to which tile layers are attached.
        :return: None
        """
        # Normalize the default tile name to lowercase for comparison
        normalized_default_tile = self.tiles.lower()

        # Filter out the default tile layer from the options to avoid duplication
        tile_options_filtered = {k: v for k, v in self.tile_options.items() if v.lower() != normalized_default_tile}

        for tile, description in tile_options_filtered.items():
            folium.TileLayer(name=tile, tiles=description, show=False).add_to(self.osm_map)


    def _get_bounding_box_from_points(self, margin=0.001):
        """
        Calculate a bounding box from GPS points with an additional margin.

        This method processes the GPS points in the `self.gps_points` list
        and calculates a geographical bounding box encompassing all
        points with an optional margin added to its boundaries. The
        bounding box is defined by the northernmost, southernmost,
        easternmost, and westernmost boundaries.

        :param margin: A float value that adds a margin to the bounding
            box boundaries.
            Defaults to 0.001.
        :return: A tuple containing four float values in the order:
            north (northernmost boundary), south (southernmost boundary),
            east (easternmost boundary), and west (westernmost boundary).
        """
        latitudes = [point[0] for point in self.gps_points]
        longitudes = [point[1] for point in self.gps_points]

        north = max(latitudes) + margin
        south = min(latitudes) - margin
        east = max(longitudes) + margin
        west = min(longitudes) - margin

        return north, south, east, west


    def _extract_subgraph(self, north, south, east, west):
        """
        Extracts a subgraph from the OSMnx graph based on a specified bounding box.

        This function takes the northern, southern, eastern, and western bounds to
        define a geographic bounding box. It creates a polygon from these bounds and
        identifies nodes within the graph that fall within this boundary. A new subgraph
        is then created using these identified nodes. This functionality supports different
        approaches depending on the OSMnx version.

        :param north: The northern boundary of the bounding box.
        :type north: float
        :param south: The southern boundary of the bounding box.
        :type south: float
        :param east: The eastern boundary of the bounding box.
        :type east: float
        :param west: The western boundary of the bounding box.
        :type west: float
        :return: A subgraph extracted from the OSMnx graph containing nodes within the bounding box.
        :rtype: networkx.Graph
        """
        # Create a bounding box polygon
        # from osmnx v2 this is how it is done
        if ox.__version__ >= '2.0':
            bbox_poly = gpd.GeoSeries([ox.utils_geo.bbox_to_poly(bbox=(west, south, east, north))])
        else:
            bbox_poly = gpd.GeoSeries([ox.utils_geo.bbox_to_poly(north, south, east, west)])

        # Get nodes GeoDataFrame
        nodes_gdf = ox.graph_to_gdfs(self.osmnx_graph, nodes=True, edges=False)

        # Find nodes within the bounding box
        nodes_within_bbox = nodes_gdf[nodes_gdf.geometry.within(bbox_poly.geometry.unary_union)]

        # Create subgraph
        subgraph = self.osmnx_graph.subgraph(nodes_within_bbox.index)

        return subgraph


    @abstractmethod
    def process_map(self):
        """
        This abstract method serves as a blueprint for processing a map. It is intentionally
        left unimplemented and must be overridden in any concrete subclass. Subclasses should
        provide their own specific logic for map processing by implementing this interface.

        :return: None
        """
        # this is to be implemented at the subclass level
        # implement here your specific map logic.
        ...


    def pre_process_map(self):
        """
        Pre-processes the map data.

        This method is designed to be overridden in a subclass to perform specific
        pre-processing procedures on map data. When overridden, the implementation
        in the subclass must call `super().pre_process_map` first to inherit and
        maintain the existing behavior of this base implementation.

        :return: None
        """
        # this is to be implemented at the subclass level
        # call super().pre_process_map first to inherit the following behaviour
        ...


    def _post_process_map(self):
        """
        Performs post-processing tasks on the map object to enhance its functionality
        and ensure required adjustments or attributes are attached to it. This method
        is mainly used internally to finalize map setup based on current configurations.

        :raises AttributeError: This error is raised if one of the required attributes
            is not properly initialized or missing during the processing.
        :raises ValueError: This error is raised if provided bounds are invalid or
            incompatible for fitting.
        """
        self._attach_supported_tiles()
        self.add_tile_layer()
        self._add_fullscreen()
        self._add_map_title()
        if self.max_bounds:
            self.osm_map.fit_bounds(self.bounds)


    def add_tile_layer(self):
        """
        Adds a tile layer to the OpenStreetMap (OSM) representation.
        This method is intended to handle the inclusion of additional
        tile layers in the map. Subclasses should override this method,
        call their custom logic, and conclude with a call to this base
        implementation to add necessary controls to the map instance.

        :rtype: None
        :return: This method does not return any value.
        """
        # Override in subclass and call super().add_tile_layer at the end
        folium.LayerControl().add_to(self.osm_map)


    def _add_fullscreen(self):
        """
        Adds a fullscreen functionality to the map if the fullscreen attribute is set.

        This method checks whether the fullscreen mode is enabled by evaluating
        the `fullscreen` attribute of the class. If `fullscreen` is set to True,
        a Fullscreen instance is created with the specified position from
        `fullscreen_position` and added to the map (`osm_map`).

        :return: None
        """
        if self.fullscreen:
            Fullscreen(position=self.fullscreen_position).add_to(self.osm_map)


    def _add_map_title(self):
        """
        Adds a title to the map if the title is specified.

        This method checks if the attribute `map_html_title` is set. If it is,
        it creates an HTML element containing the title and adds it to the
        map's root HTML structure using Folium's API.

        :raises AttributeError: If `osm_map` or `osm_map.get_root()` is not defined
            or does not support the necessary operations.
        """
        if self.map_html_title:
            self.osm_map.get_root().html.add_child(folium.Element(self.map_html_title))


    @staticmethod
    def _sanitize_html(input_html):
        """
        Sanitizes the provided HTML input by escaping special HTML characters.
        This method ensures the input string is safe for use in HTML contexts
        by converting characters like `<`, `>`, and `&` into their corresponding
        HTML-safe representations.

        :param input_html: The HTML string that needs to be sanitized.
        :type input_html: str
        :return: The sanitized version of the input HTML string with special
            characters escaped.
        :rtype: str
        """
        return html.escape(input_html)


    def generate_map(self):
        """
        Generates a map by executing preprocessing, main processing, and
        post-processing tasks sequentially. This method combines multiple
        stages to prepare and retrieve the final map object.

        :return: The completed and processed OpenStreetMap map instance
        :rtype: object
        """
        self.pre_process_map()
        self.process_map()
        self._post_process_map()

        return self.osm_map
