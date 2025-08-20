#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/7/14 11:35 
# @File    : LoadSHP.py

import pathlib
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, LineString, MultiLineString, MultiPolygon
from rasterio import features
from rasterio.transform import from_origin
import shapely.validation

from typing import List, Union, Dict, Optional

import sagea


def load_shp(
        shp_path,
        resolution=1.,
        buffer_distance=0.1,
        line_to_polygon=False,
        combine_features=True,
        all_touched=True,
        make_valid=False
):
    """
    Convert shapefile to global grid mask

    Parameters:
        shp_path: Path to shapefile
        resolution: Grid resolution (in degrees)
        buffer_distance: Buffer distance for line features (in degrees)
        line_to_polygon: For line features, True=convert to polygon, False=keep as line
        combine_features: True=merge all features into single mask, False=output each feature separately
        all_touched: Whether to include all touched pixels during rasterization
        make_valid: Whether to fix invalid geometries automatically

    Returns:
        mask, in numpy.ndarray:
            - If combine_features=True: shape is (180/resolution, 360/resolution)
            - If combine_features=False: shape is (n, 180/resolution, 360/resolution)
        lat, in 1d numpy.ndarray: unit degrees
        lon, in 1d numpy.ndarray: unit degrees
    """
    # Read and validate data
    gdf = gpd.read_file(shp_path)

    # Check coordinate system
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Validate geometry types
    valid_types = ['Polygon', 'MultiPolygon', 'LineString', 'MultiLineString']
    if not all(gdf.geometry.type.isin(valid_types)):
        invalid_types = set(gdf.geometry.type.unique()) - set(valid_types)
        raise ValueError(f"Unsupported geometry types: {invalid_types}. Only polygons and lines are supported")

    if make_valid:
        gdf['geometry'] = gdf['geometry'].apply(shapely.validation.make_valid)

    # Process line features
    if any(gdf.geometry.type.isin(['LineString', 'MultiLineString'])):
        if line_to_polygon:
            # Check if lines are closed
            closed_lines = gdf.geometry.apply(
                lambda geom: isinstance(geom, LineString) and geom.is_closed
                             or isinstance(geom, MultiLineString)
                             and all(line.is_closed for line in geom.geoms)
            )

            # Convert closed lines directly to polygons, buffer unclosed lines
            def line_to_poly(geom):
                if isinstance(geom, LineString) and geom.is_closed:
                    return Polygon(geom.coords)
                elif isinstance(geom, MultiLineString) and all(line.is_closed for line in geom.geoms):
                    return Polygon(geom[0].coords)  # Take first closed line
                return geom.buffer(buffer_distance)

            gdf.geometry = gdf.geometry.apply(line_to_poly)
        else:
            # Keep as lines but buffer to ensure visibility in rasterization
            gdf.geometry = gdf.geometry.buffer(max(buffer_distance, resolution / 2))

    # Set up global grid parameters
    lat, lon = sagea.MathTool.get_global_lat_lon_range(resolution)
    n_rows = lat.size
    n_cols = lon.size
    transform = from_origin(-180, -90, resolution, -resolution)

    # Handle geometries crossing the antimeridian
    gdf = _fix_antimeridian_crossing(gdf)

    if combine_features:
        # Combine all features into single mask
        shapes = [(geom, 1) for geom in gdf.geometry]
        mask = features.rasterize(
            shapes,
            out_shape=(n_rows, n_cols),
            transform=transform,
            fill=0,
            all_touched=all_touched
        )
        masks = mask
    else:
        # Output each feature separately
        masks = np.zeros((len(gdf), n_rows, n_cols), dtype=np.uint8)
        for i, geom in enumerate(gdf.geometry):
            mask = features.rasterize(
                [(geom, 1)],
                out_shape=(n_rows, n_cols),
                transform=transform,
                fill=0,
                all_touched=all_touched
            )
            masks[i] = mask

    return masks, lat, lon


def _fix_antimeridian_crossing(gdf):
    """
    Handle geometries crossing the antimeridian (±180° longitude)
    """

    def split_geom(geom):
        if geom.is_empty:
            return geom

        bounds = geom.bounds
        if bounds[0] < -170 and bounds[2] > 170:  # Crosses antimeridian
            # Split into western and eastern parts
            west = geom.intersection(Polygon([
                (-180, 90), (-180, -90),
                (0, -90), (0, 90), (-180, 90)
            ]))
            east = geom.intersection(Polygon([
                (0, 90), (0, -90),
                (180, -90), (180, 90), (0, 90)
            ]))

            # Shift eastern part to western hemisphere
            if not east.is_empty:
                east = _shift_geometry(east, -360)

            return west.union(east)
        return geom

    gdf.geometry = gdf.geometry.apply(split_geom)
    return gdf


def _shift_geometry(geom, x_shift):
    """
    Shift geometry's x-coordinates
    """
    if geom.is_empty:
        return geom

    if geom.geom_type == 'Polygon':
        exterior = np.array(geom.exterior.coords)
        exterior[:, 0] += x_shift
        interiors = []
        for interior in geom.interiors:
            coords = np.array(interior.coords)
            coords[:, 0] += x_shift
            interiors.append(coords)
        return Polygon(exterior, interiors)

    elif geom.geom_type in ['LineString', 'LinearRing']:
        coords = np.array(geom.coords)
        coords[:, 0] += x_shift
        return LineString(coords)

    elif geom.geom_type == 'MultiLineString':
        lines = []
        for line in geom.geoms:
            coords = np.array(line.coords)
            coords[:, 0] += x_shift
            lines.append(LineString(coords))
        return MultiLineString(lines)

    return geom


class ShapefileInspector:
    def __init__(self, shp_path: pathlib.Path):
        """
        Initialize Shapefile inspector

        Parameters:
            shp_path: Path to shapefile (.shp)
        """
        self.gdf = gpd.read_file(shp_path)
        self.original_crs = self.gdf.crs

    def get_feature_info(self) -> Dict:
        """
        Get basic feature information from shapefile

        Returns:
            Dictionary containing:
            - 'crs': Coordinate reference system
            - 'geometry_type': Geometry types present
            - 'feature_count': Number of features
            - 'attributes': List of all attribute fields
            - 'extent': Spatial extent (xmin, ymin, xmax, ymax)
        """
        return {
            'crs': str(self.gdf.crs),
            'geometry_type': self.gdf.geometry.type.unique().tolist(),
            'feature_count': len(self.gdf),
            'attributes': self.gdf.columns.tolist(),
            'extent': self.gdf.total_bounds.tolist()
        }

    def list_unique_values(self, attribute: str, top_n: int = None) -> List:
        """
        List unique values for specified attribute

        Parameters:
            attribute: Attribute field name
            top_n: Only return top n most frequent values

        Returns:
            List of unique values
        """
        if attribute not in self.gdf.columns:
            raise ValueError(f"Attribute '{attribute}' does not exist in file")

        value_counts = self.gdf[attribute].value_counts()
        return value_counts.head(top_n).index.tolist()

    def filter_features(
            self,
            attribute: Optional[str] = None,
            value: Optional[Union[str, int, float, List]] = None,
            bbox: Optional[List[float]] = None,
            geometry_type: Optional[str] = None,
            save_to: Optional[str] = None
    ) -> gpd.GeoDataFrame:
        """
        Filter features based on conditions

        Parameters:
            attribute: Attribute field to filter by
            value: Value(s) to match (single value or list)
            bbox: Spatial filter [xmin, ymin, xmax, ymax]
            geometry_type: Filter by geometry type
            save_to: Path to save filtered results (optional)

        Returns:
            Filtered GeoDataFrame
        """
        filtered = self.gdf.copy()

        # Attribute filter
        if attribute is not None:
            if attribute not in filtered.columns:
                raise ValueError(f"Attribute '{attribute}' does not exist")

            if value is not None:
                if isinstance(value, list):
                    filtered = filtered[filtered[attribute].isin(value)]
                else:
                    filtered = filtered[filtered[attribute] == value]

        # Spatial filter
        if bbox is not None:
            if len(bbox) != 4:
                raise ValueError("bbox requires 4 values [xmin, ymin, xmax, ymax]")
            filtered = filtered.cx[bbox[0]:bbox[2], bbox[1]:bbox[3]]

        # Geometry type filter
        if geometry_type is not None:
            valid_types = ['Point', 'LineString', 'Polygon',
                           'MultiPoint', 'MultiLineString', 'MultiPolygon']
            if geometry_type not in valid_types:
                raise ValueError(f"Invalid geometry type, must be one of: {valid_types}")
            filtered = filtered[filtered.geometry.type == geometry_type]

        # Save results
        if save_to is not None:
            filtered.to_file(save_to, driver='ESRI Shapefile')

        return filtered

    def export_selected_features(
            self,
            selection: Dict[str, Union[str, List[str]]],
            save_to: str,
            keep_attributes: List[str] = None
    ) -> None:
        """
        Export selected features to new shapefile

        Parameters:
            selection: Filter conditions as dictionary:
                      {'attribute1': value_or_list, 'attribute2': value_or_list}
            save_to: Output file path
            keep_attributes: List of attributes to keep (None keeps all)
        """
        filtered = self.gdf.copy()

        for attr, val in selection.items():
            if attr not in filtered.columns:
                raise ValueError(f"Attribute '{attr}' does not exist")

            if isinstance(val, list):
                filtered = filtered[filtered[attr].isin(val)]
            else:
                filtered = filtered[filtered[attr] == val]

        if keep_attributes is not None:
            keep_attrs = set(keep_attributes) & set(filtered.columns)
            filtered = filtered[list(keep_attrs) + ['geometry']]

        filtered.to_file(save_to, driver='ESRI Shapefile')
