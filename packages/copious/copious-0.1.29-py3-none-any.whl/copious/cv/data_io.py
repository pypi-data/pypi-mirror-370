from pathlib import Path
from typing import Union, Optional, List

import pypcd4 as pypcd
import polars as pl
import numpy as np


def read_pcd(path: Union[str, Path], fields: Optional[List[str]] = None) -> pl.DataFrame:
    """Read PCD file and return as Polars DataFrame
    
    This optimized implementation uses bulk data extraction for better performance,
    reducing memory allocations and eliminating field-by-field processing.
    
    Parameters
    ----------
    path : Union[str, Path]
        Path to the PCD file
    fields : Optional[List[str]], optional
        List of field names to read. If None, reads all available fields.
        
    Returns
    -------
    pl.DataFrame
        DataFrame containing the requested PCD fields
        
    Examples
    --------
    >>> # Read all fields
    >>> df = read_pcd("pointcloud.pcd")
    >>> 
    >>> # Read specific fields only
    >>> df = read_pcd("pointcloud.pcd", fields=["x", "y", "z", "intensity"])
    """
    pcd = pypcd.PointCloud.from_path(str(path))
    
    # Get available fields from PCD file
    available_fields = list(pcd.fields)
    
    # Determine which fields to read
    if fields is None:
        # Read all available fields - use bulk extraction
        all_data = pcd.numpy()
        return pl.DataFrame(all_data, schema=available_fields)
    else:
        # Validate requested fields exist in PCD file
        missing_fields = [f for f in fields if f not in available_fields]
        if missing_fields:
            raise ValueError(f"Requested fields {missing_fields} not found in PCD file. Available fields: {available_fields}")
        
        # Use targeted bulk extraction for requested field subset
        # This ensures field ordering matches the user's request
        subset_data = pcd.numpy(fields)
        
        # Create DataFrame using dictionary method for better robustness
        # This avoids potential issues with array interpretation
        data_dict = {}
        for i, field in enumerate(fields):
            data_dict[field] = subset_data[:, i]
        
        return pl.DataFrame(data_dict)


def write_pcd(data: pl.DataFrame, path: Union[str, Path], fields: Optional[List[str]] = None) -> None:
    """Write point cloud data to PCD file
    
    Parameters
    ----------
    data : pl.DataFrame
        Point cloud data as Polars DataFrame
    path : Union[str, Path]
        Output file path
    fields : Optional[List[str]], optional
        List of field names to write. If None, writes all DataFrame columns.
        
    Examples
    --------
    >>> # Write all DataFrame columns
    >>> write_pcd(df, "output.pcd")
    >>> 
    >>> # Write specific fields only
    >>> write_pcd(df, "output.pcd", fields=["x", "y", "z", "intensity"])
    """
    if not isinstance(data, pl.DataFrame):
        raise TypeError(f"Expected pl.DataFrame, got {type(data)}")
    
    path = str(path)
    
    # Determine which fields to write
    available_columns = data.columns
    if fields is None:
        fields_to_write = available_columns
    else:
        # Validate requested fields exist in DataFrame 
        missing_fields = [f for f in fields if f not in available_columns]
        if missing_fields:
            raise ValueError(f"Requested fields {missing_fields} not found in DataFrame. Available columns: {available_columns}")
        fields_to_write = fields
    
    # Extract data for specified fields
    subset_df = data.select(fields_to_write)
    
    # Convert to numpy arrays for pypcd4
    points_dict = {}
    for field in fields_to_write:
        field_data = subset_df[field].to_numpy()
        points_dict[field] = field_data
    
    # Stack all field data into a single array
    points_array = np.column_stack([points_dict[field] for field in fields_to_write])
    points_array = points_array.astype(np.float32)
    
    # Determine data types for each field
    field_types = []
    for field in fields_to_write:
        # Default to float32 for all fields, can be extended later for other types
        field_types.append(np.float32)
    
    # Create point cloud using pypcd4's generic from_points method
    pcd = pypcd.PointCloud.from_points(
        points_array,
        fields=fields_to_write,
        types=field_types
    )
    
    # Save the point cloud
    pcd.save(path)
