"""
STAC catalog creation utilities for Open Polar Radar data.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

import pystac
import shapely
from shapely.geometry import mapping

from .metadata import extract_item_metadata, discover_campaigns, discover_flight_lines, get_mat_file_type


def create_catalog(
    catalog_id: str = "OPR",
    description: str = "Open Polar Radar airborne data",
    stac_extensions: Optional[List[str]] = None
) -> pystac.Catalog:
    """
    Create a root STAC catalog for OPR data.
    
    Args:
        catalog_id: Unique identifier for the catalog
        description: Human-readable description
        stac_extensions: List of STAC extension URLs to enable
        
    Returns:
        pystac.Catalog: Root catalog object
    """
    if stac_extensions is None:
        stac_extensions = [
            'https://stac-extensions.github.io/projection/v1.0.0/schema.json',
            'https://stac-extensions.github.io/file/v2.1.0/schema.json',
        ]
    
    return pystac.Catalog(
        id=catalog_id,
        description=description,
        stac_extensions=stac_extensions
    )


def create_collection(
    collection_id: str,
    description: str,
    extent: pystac.Extent,
    license: str = "",
    stac_extensions: Optional[List[str]] = None
) -> pystac.Collection:
    """
    Create a STAC collection for a campaign or data product grouping.
    
    Args:
        collection_id: Unique identifier for the collection
        description: Human-readable description
        extent: Spatial and temporal extent of the collection
        license: Data license identifier
        stac_extensions: List of STAC extension URLs to enable
        
    Returns:
        pystac.Collection: Collection object
    """
    if stac_extensions is None:
        stac_extensions = []
    
    return pystac.Collection(
        id=collection_id,
        description=description,
        extent=extent,
        license=license,
        stac_extensions=stac_extensions
    )


def create_item(
    item_id: str,
    geometry: Dict[str, Any],
    bbox: List[float],
    datetime: Any,
    properties: Optional[Dict[str, Any]] = None,
    assets: Optional[Dict[str, pystac.Asset]] = None,
    stac_extensions: Optional[List[str]] = None
) -> pystac.Item:
    """
    Create a STAC item for a flight line data segment.
    
    Args:
        item_id: Unique identifier for the item
        geometry: GeoJSON geometry object
        bbox: Bounding box [xmin, ymin, xmax, ymax]
        datetime: Acquisition datetime
        properties: Additional metadata properties
        assets: Dictionary of assets (data files, thumbnails, etc.)
        stac_extensions: List of STAC extension URLs to enable
        
    Returns:
        pystac.Item: Item object
    """
    if properties is None:
        properties = {}
    if stac_extensions is None:
        stac_extensions = ['https://stac-extensions.github.io/file/v2.1.0/schema.json']
    
    item = pystac.Item(
        id=item_id,
        geometry=geometry,
        bbox=bbox,
        datetime=datetime,
        properties=properties,
        stac_extensions=stac_extensions
    )
    
    if assets:
        for key, asset in assets.items():
            item.add_asset(key, asset)
    
    return item


def create_items_from_flight_data(
    flight_data: Dict[str, Any],
    base_url: str = "https://data.cresis.ku.edu/data/rds/",
    campaign_name: str = "",
    primary_data_product: str = "CSARP_standard"
) -> List[pystac.Item]:
    """
    Create STAC items from flight line data.
    
    Args:
        flight_data: Flight metadata from discover_flight_lines()
        base_url: Base URL for constructing asset hrefs
        campaign_name: Campaign name for URL construction
        data_product: Data product name
        
    Returns:
        List of pystac.Item objects, one per MAT file
    """
    items = []
    flight_id = flight_data['flight_id']

    primary_data_files = flight_data['data_files'][primary_data_product].values()
    
    for data_file_path in primary_data_files:
        data_path = Path(data_file_path)
        
        try:
            # Extract metadata from MAT file only (no CSV needed)
            metadata = extract_item_metadata(data_path)
        except Exception as e:
            print(f"Warning: Failed to extract metadata for {data_path}: {e}")
            continue

        item_id = f"{data_path.stem}"
        
        geometry = mapping(metadata['geom'])
        bbox = list(metadata['bbox'].bounds)
        datetime = metadata['date']

        rel_mat_path = f"{campaign_name}/{primary_data_product}/{flight_id}/{data_path.name}"
        data_href = base_url + rel_mat_path
        
        # Extract segment number from MAT filename (e.g., "Data_20161014_03_001.mat" -> "001")
        segment_match = re.search(r'_(\d+)\.mat$', data_path.name)
        segment = segment_match.group(1)
        
        # Extract date and flight number from flight_id (e.g., "20161014_03" -> "20161014", "03")
        # Split on underscore to avoid assuming fixed lengths
        parts = flight_id.split('_')
        date_part = parts[0]  # YYYYMMDD
        flight_num_str = parts[1]  # Flight number as string
        
        # Create OPR-specific properties
        properties = {
            'opr:date': date_part,
            'opr:flight': int(flight_num_str),
            'opr:segment': int(segment)
        }
        
        assets = {}

        for data_product_type in flight_data['data_files'].keys():
            if data_path.name in flight_data['data_files'][data_product_type]:
                product_path = flight_data['data_files'][data_product_type][data_path.name]
                file_type = get_mat_file_type(product_path)
                print(f"[{file_type}] {product_path}")
                assets[data_product_type] = pystac.Asset(
                    href=base_url + f"{campaign_name}/{data_product_type}/{flight_id}/{data_path.name}",
                    media_type=file_type
                )
                if data_product_type == primary_data_product:
                    assets['data'] = assets[data_product_type]
        
        thumb_href = base_url + f"{campaign_name}/images/{flight_id}/{flight_id}_{segment}_2echo_picks.jpg"
        assets['thumbnails'] = pystac.Asset(
            href=thumb_href,
            media_type=pystac.MediaType.JPEG
        )
        
        flight_path_href = base_url + f"{campaign_name}/images/{flight_id}/{flight_id}_{segment}_0maps.jpg"
        assets['flight_path'] = pystac.Asset(
            href=flight_path_href,
            media_type=pystac.MediaType.JPEG
        )
        
        item = create_item(
            item_id=item_id,
            geometry=geometry,
            bbox=bbox,
            datetime=datetime,
            properties=properties,
            assets=assets
        )
        
        items.append(item)
    
    return items


def build_collection_extent(items: List[pystac.Item]) -> pystac.Extent:
    """
    Calculate spatial and temporal extent from a list of items.
    
    Args:
        items: List of STAC items
        
    Returns:
        pystac.Extent: Combined spatial and temporal extent
    """
    if not items:
        raise ValueError("Cannot build extent from empty item list")
    
    bboxes = []
    datetimes = []
    
    for item in items:
        if item.bbox:
            bbox_geom = shapely.geometry.box(*item.bbox)
            bboxes.append(bbox_geom)
        
        if item.datetime:
            datetimes.append(item.datetime)
    
    if bboxes:
        union_bbox = bboxes[0]
        for bbox in bboxes[1:]:
            union_bbox = union_bbox.union(bbox)
        
        collection_bbox = list(union_bbox.bounds)
        spatial_extent = pystac.SpatialExtent(bboxes=[collection_bbox])
    else:
        spatial_extent = pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])
    
    if datetimes:
        sorted_times = sorted(datetimes)
        temporal_extent = pystac.TemporalExtent(
            intervals=[[sorted_times[0], sorted_times[-1]]]
        )
    else:
        temporal_extent = pystac.TemporalExtent(intervals=[[None, None]])
    
    return pystac.Extent(spatial=spatial_extent, temporal=temporal_extent)
