from __future__ import annotations
from sibi_dst.osmnx_helper.utils import get_distance_between_points, add_arrows
from collections import defaultdict
import folium
from folium.plugins import AntPath
import networkx as nx

from sibi_dst.osmnx_helper import BaseOsmMap
from sibi_dst.osmnx_helper.basemaps.calendar_html import calendar_html

class RoutePlotter(BaseOsmMap):
    def __init__(self, osmnx_graph, df, **kwargs):
        self.action_field = kwargs.pop('action_field', '')
        self.action_groups = kwargs.pop('action_groups', {})
        self.action_styles = kwargs.pop('action_styles', {})
        self.use_ant_path = kwargs.pop('use_ant_path', False)
        self.show_calendar = kwargs.pop('show_calendar', False)
        self.show_order_markers = kwargs.pop('show_order_markers', False)
        self.show_map_title = kwargs.pop('show_map_title', True)
        self.sort_keys = kwargs.pop('sort_keys', None)
        self.main_route_layer = folium.FeatureGroup(name="Main Route")
        self.feature_groups = {}
        self.feature_group_counts = {}
        self.total_distance = 0.0
        self.actions = []
        self.action_group_counts = {action_group: 0 for action_group in self.action_groups}
        self.marker_count = 1
        # Add a snapping threshold (in meters) to avoid drawing nodes/markers that are too close.
        self.snap_distance = kwargs.pop('snap_distance', 30)
        kwargs.update({'calc_nearest_nodes': True})
        kwargs['dt_field'] = 'date_time'
        super().__init__(osmnx_graph, df, **kwargs)

    def pre_process_map(self):
        super().pre_process_map()
        self.actions = self.df[self.action_field].tolist()

    def process_map(self):
        self._calculate_routes()
        self._plot_routes()
        self._add_markers()
        if self.show_order_markers:
            self._add_order_markers()
        self.main_route_layer.add_to(self.osm_map)
        if self.show_calendar:
            self._add_calendar()

    def _calculate_routes(self):
        if self.verbose:
            print("Calculating routes and markers...")
        distances = [
            get_distance_between_points(tuple(self.gps_points[0]), tuple(coord), 'm')
            for coord in self.gps_points
        ]
        self.max_distance_index = distances.index(max(distances))
        self.max_time_index = self.dt.index(max(self.dt))
        self.route_polylines = []
        self.markers = defaultdict(list)  # Store markers for action groups
        for i in range(len(self.gps_points) - 1):
            polyline, color, markers = self._calculate_route(i)
            if polyline:
                self.route_polylines.append((polyline, color))
                for action_group, action_markers in markers.items():
                    self.markers[action_group].extend(action_markers)
                    self.action_group_counts[action_group] += len(action_markers)
                    self.marker_count += len(action_markers)
        if self.verbose:
            print("Route and marker calculation complete.")

        for action_group in self.action_groups:
            count = self.action_group_counts[action_group]
            self.feature_groups[action_group] = folium.FeatureGroup(name=f"{action_group} ({count})").add_to(
                self.osm_map)
            self.osm_map.add_child(self.feature_groups[action_group])

    def _calculate_route(self, i):
        if self.verbose:
            print(f"Calculating for item: {i}")
        orig = self.nearest_nodes[i]
        dest = self.nearest_nodes[i + 1]
        try:
            route = nx.shortest_path(self.G, orig, dest, weight='length')
            route_length = sum(self.G[u][v][0]['length'] for u, v in zip(route[:-1], route[1:]))
            self.total_distance += route_length
            offset = 0 if i < self.max_distance_index else 0.0005
            lats, lons = zip(*[(self.G.nodes[node]['y'] + offset, self.G.nodes[node]['x']) for node in route])
            color = 'blue' if i < self.max_distance_index else 'red'
            polyline = list(zip(lats, lons))
            # Apply node snapping to the polyline to remove points that are too close.
            polyline = self._snap_polyline(polyline)
            markers = self._calculate_markers(i)
            return polyline, color, markers
        except nx.NetworkXNoPath:
            if self.verbose:
                print(f"Item: {i} - No path found for {orig} to {dest}")
            return None, None, {}
        except nx.NodeNotFound:
            if self.verbose:
                print(f"Item: {i} - No path found for {orig} to {dest}")
            return None, None, {}

    def _snap_polyline(self, polyline: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """
        Returns a filtered polyline where consecutive points closer than snap_distance are removed.
        """
        if not polyline:
            return polyline
        snapped_polyline = [polyline[0]]
        for point in polyline[1:]:
            if get_distance_between_points(snapped_polyline[-1], point, 'm') >= self.snap_distance:
                snapped_polyline.append(point)
        return snapped_polyline

    def _calculate_markers(self, i):
        # Calculate markers for action groups
        markers = defaultdict(list)
        for action_group in self.action_groups:
            action_indices = [idx for idx, action in enumerate(self.actions) if action == action_group]
            for idx in action_indices:
                if idx == i:
                    location = self.gps_points[i]
                    tooltip = f"Result {self.marker_count}: {action_group}<br>Date/time:{self.dt[i]}"
                    popup_data = self._get_data(i)
                    action_style = self.action_styles.get(action_group,
                                                          {'color': 'blue', 'icon': 'marker', 'prefix': 'fa'})
                    markers[action_group].append((location, tooltip, popup_data, action_style))
        return markers

    def _plot_routes(self):
        if self.verbose:
            print("Plotting routes and markers...")
        for polyline, color in self.route_polylines:
            if self.use_ant_path:
                AntPath(
                    locations=polyline,
                    color=color,
                    weight=3,       # Increased line thickness
                    opacity=10,     # Increased opacity
                    delay=1000,     # Slower animation to reduce flickering
                ).add_to(self.main_route_layer)
            else:
                folium.PolyLine(locations=polyline, color=color).add_to(self.main_route_layer)
                self.osm_map = add_arrows(self.osm_map, polyline, color, n_arrows=3)
        # Plot markers for action groups with snapping to avoid drawing too many nearby markers.
        for action_group, action_markers in self.markers.items():
            seen_positions = []
            for location, tooltip, popup_data, action_style in action_markers:
                # Skip marker if a nearby marker (within snap_distance) has already been added.
                if any(get_distance_between_points(location, pos, 'm') < self.snap_distance for pos in seen_positions):
                    continue
                seen_positions.append(location)
                folium.Marker(
                    location=location,
                    popup=folium.Popup(popup_data, max_width=600),
                    tooltip=tooltip,
                    icon=folium.Icon(
                        icon=action_style.get("icon"),
                        color=action_style.get("color"),
                        prefix=action_style.get("prefix")
                    )
                ).add_to(self.feature_groups[action_group])

        if self.verbose:
            print("Route and marker plotting complete.")

    def _add_markers(self):
        if self.verbose:
            print("Adding markers...")
        # Add a start marker
        start_popup = folium.Popup(f"Start of route at {self.dt[0]}", max_width=300)
        folium.Marker(
            location=self.gps_points[0],
            popup=start_popup,
            icon=folium.Icon(icon='flag-checkered', prefix='fa')
        ).add_to(self.osm_map)
        # Add an end marker with total distance info
        folium.Marker(
            self.gps_points[-1],
            popup=f"End of Route at {self.dt[self.max_time_index]}. Total Distance Travelled: {self.total_distance / 1000:.2f} km",
            icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa")
        ).add_to(self.osm_map)
        if self.verbose:
            print("Marker addition complete.")

    def _add_calendar(self):
        calendar_element = folium.Element(calendar_html)
        self.osm_map.get_root().html.add_child(calendar_element)

    def _add_map_title(self):
        if self.map_html_title and self.show_map_title:
            title_html = f'''
                 <div style="position: fixed;
                             top: 10px;
                             left: 50%;
                             transform: translate(-50%, 0%);
                             z-index: 9999;
                             font-size: 24px;
                             font-weight: bold;
                             background-color: white;
                             padding: 10px;
                             border: 2px solid black;
                             border-radius: 5px;">
                    {self.map_html_title}
                 </div>
                 '''
            self.osm_map.get_root().html.add_child(folium.Element(title_html))

    def _add_order_markers(self):
        """Adds numbered markers to indicate the visit order."""
        order_feature_group = folium.FeatureGroup(name="Visit Order")
        for idx, location in enumerate(self.gps_points):
            # Create a DivIcon with the number (starting at 1)
            icon = folium.DivIcon(
                icon_size=(24, 24),
                icon_anchor=(12, 12),
                html=f'''
                    <div style="
                        font-size: 12pt;
                        color: black;
                        background-color: white;
                        border: 1px solid black;
                        border-radius: 50%;
                        width: 24px;
                        height: 24px;
                        text-align: center;
                        line-height: 24px;">
                        {idx + 1}
                    </div>
                '''
            )
            folium.Marker(
                location=location,
                icon=icon,
                tooltip=f"GPS Set No. {idx + 1}: {self.dt[idx]}"
            ).add_to(order_feature_group)

        order_feature_group.add_to(self.osm_map)

    def _get_data(self, index):
        # Implement in subclass to populate popups
        ...