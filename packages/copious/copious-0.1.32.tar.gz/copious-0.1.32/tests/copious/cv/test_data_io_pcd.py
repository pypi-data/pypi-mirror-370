import pytest
import numpy as np
import polars as pl
import tempfile
import os
from pathlib import Path

from copious.cv.data_io import read_pcd, write_pcd


def create_test_pcd_data():
    """Create sample point cloud data with x,y,z, intensity and RGB values."""
    # Create 100 random points
    n_points = 100
    np.random.seed(42)  # For reproducible tests
    
    # Generate random 3D points
    points = np.random.uniform(-10, 10, (n_points, 3)).astype(np.float32)
    
    # Add intensity values (0-255)
    intensity = np.random.uniform(0, 255, (n_points, 1)).astype(np.float32)
    
    # Add RGB values (0-255 for each channel)
    rgb = np.random.randint(0, 256, (n_points, 3)).astype(np.uint8)
    
    return points, intensity, rgb


def create_test_pcd_file_with_rgb():
    """Create a test PCD file with x,y,z, intensity and RGB values."""
    points, intensity, rgb = create_test_pcd_data()
    
    # Create PCD content manually
    n_points = len(points)
    
    pcd_content = f"""# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z intensity rgb
SIZE 4 4 4 4 4
TYPE F F F F U
COUNT 1 1 1 1 1
WIDTH {n_points}
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS {n_points}
DATA ascii
"""
    
    # Add data rows
    for i in range(n_points):
        x, y, z = points[i]
        intens = intensity[i, 0]
        # Pack RGB into a single uint32
        r, g, b = rgb[i]
        rgb_packed = (int(r) << 16) | (int(g) << 8) | int(b)
        pcd_content += f"{x:.6f} {y:.6f} {z:.6f} {intens:.6f} {rgb_packed}\n"
    
    # Write to temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pcd', delete=False)
    temp_file.write(pcd_content)
    temp_file.close()
    
    return temp_file.name, points, intensity, rgb


class TestPCDUtils:
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.test_pcd_file, self.expected_points, self.expected_intensity, self.expected_rgb = create_test_pcd_file_with_rgb()
        
        # Create expected DataFrame
        self.expected_df = pl.DataFrame({
            'x': self.expected_points[:, 0],
            'y': self.expected_points[:, 1], 
            'z': self.expected_points[:, 2],
            'intensity': self.expected_intensity[:, 0]
        })
    
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_pcd_file):
            os.unlink(self.test_pcd_file)
    
    def test_read_pcd_all_fields(self):
        """Test reading PCD file with all available fields."""
        result = read_pcd(self.test_pcd_file)
        
        # Should return DataFrame with all fields
        assert isinstance(result, pl.DataFrame)
        expected_fields = {'x', 'y', 'z', 'intensity', 'rgb'}
        assert set(result.columns) == expected_fields
        assert len(result) == 100
        
        # Check coordinate data
        np.testing.assert_allclose(result['x'].to_numpy(), self.expected_points[:, 0], rtol=1e-5)
        np.testing.assert_allclose(result['y'].to_numpy(), self.expected_points[:, 1], rtol=1e-5)
        np.testing.assert_allclose(result['z'].to_numpy(), self.expected_points[:, 2], rtol=1e-5)
        np.testing.assert_allclose(result['intensity'].to_numpy(), self.expected_intensity[:, 0], rtol=1e-5)
    
    def test_read_pcd_specific_fields(self):
        """Test reading PCD file with specific fields only."""
        # Test reading only position fields
        result_xyz = read_pcd(self.test_pcd_file, fields=['x', 'y', 'z'])
        assert isinstance(result_xyz, pl.DataFrame)
        assert result_xyz.columns == ['x', 'y', 'z']
        assert len(result_xyz) == 100
        
        # Test reading position + intensity
        result_xyzi = read_pcd(self.test_pcd_file, fields=['x', 'y', 'z', 'intensity'])
        assert result_xyzi.columns == ['x', 'y', 'z', 'intensity']
        np.testing.assert_allclose(result_xyzi['x'].to_numpy(), self.expected_points[:, 0], rtol=1e-5)
        np.testing.assert_allclose(result_xyzi['intensity'].to_numpy(), self.expected_intensity[:, 0], rtol=1e-5)
    
    def test_read_pcd_path_types(self):
        """Test that read_pcd works with both str and Path objects."""
        # Test with string path
        result_str = read_pcd(self.test_pcd_file, fields=['x', 'y', 'z'])
        
        # Test with Path object
        result_path = read_pcd(Path(self.test_pcd_file), fields=['x', 'y', 'z'])
        
        # Results should be identical
        assert result_str.equals(result_path)
    
    def test_read_pcd_nonexistent_file(self):
        """Test that read_pcd raises appropriate error for nonexistent file."""
        with pytest.raises(Exception):  # The exact exception type depends on pypcd4 implementation
            read_pcd("/nonexistent/file.pcd")
    
    def test_read_pcd_invalid_fields(self):
        """Test that read_pcd raises error for nonexistent fields."""
        with pytest.raises(ValueError, match="not found in PCD file"):
            read_pcd(self.test_pcd_file, fields=['x', 'y', 'z', 'nonexistent'])
    
    def test_write_pcd_basic(self):
        """Test writing PCD file with DataFrame containing x,y,z,intensity."""
        # Create test DataFrame
        test_df = pl.DataFrame({
            'x': np.random.uniform(-5, 5, 50).astype(np.float32),
            'y': np.random.uniform(-5, 5, 50).astype(np.float32),
            'z': np.random.uniform(-5, 5, 50).astype(np.float32),
            'intensity': np.random.uniform(0, 255, 50).astype(np.float32)
        })
        
        # Write to temporary file
        temp_output = tempfile.NamedTemporaryFile(suffix='.pcd', delete=False)
        temp_output.close()
        
        try:
            write_pcd(test_df, temp_output.name)
            
            # Read back and verify
            read_result = read_pcd(temp_output.name)
            assert isinstance(read_result, pl.DataFrame)
            assert set(read_result.columns) == {'x', 'y', 'z', 'intensity'}
            assert len(read_result) == 50
            
            # Compare values with tolerance
            for col in ['x', 'y', 'z', 'intensity']:
                np.testing.assert_allclose(read_result[col].to_numpy(), test_df[col].to_numpy(), rtol=1e-5)
            
        finally:
            if os.path.exists(temp_output.name):
                os.unlink(temp_output.name)
    
    def test_write_pcd_specific_fields(self):
        """Test writing PCD file with specific fields only."""
        # Create test DataFrame with multiple fields
        test_df = pl.DataFrame({
            'x': np.random.uniform(-5, 5, 30).astype(np.float32),
            'y': np.random.uniform(-5, 5, 30).astype(np.float32),
            'z': np.random.uniform(-5, 5, 30).astype(np.float32),
            'intensity': np.random.uniform(0, 255, 30).astype(np.float32),
            'r': np.random.uniform(0, 255, 30).astype(np.float32),
            'g': np.random.uniform(0, 255, 30).astype(np.float32)
        })
        
        # Write only XYZ fields
        temp_output = tempfile.NamedTemporaryFile(suffix='.pcd', delete=False)
        temp_output.close()
        
        try:
            write_pcd(test_df, temp_output.name, fields=['x', 'y', 'z'])
            
            # Read back and verify only XYZ fields are present
            read_result = read_pcd(temp_output.name)
            assert set(read_result.columns) == {'x', 'y', 'z'}
            
            for col in ['x', 'y', 'z']:
                np.testing.assert_allclose(read_result[col].to_numpy(), test_df[col].to_numpy(), rtol=1e-5)
            
        finally:
            if os.path.exists(temp_output.name):
                os.unlink(temp_output.name)
    
    def test_write_read_round_trip(self):
        """Test that writing and reading back preserves DataFrame data."""
        # Write to temporary file
        temp_output = tempfile.NamedTemporaryFile(suffix='.pcd', delete=False)
        temp_output.close()
        
        try:
            write_pcd(self.expected_df, temp_output.name)
            read_result = read_pcd(temp_output.name)
            
            # Check structure
            assert isinstance(read_result, pl.DataFrame)
            assert set(read_result.columns) == set(self.expected_df.columns)
            assert len(read_result) == len(self.expected_df)
            
            # Compare values
            for col in self.expected_df.columns:
                np.testing.assert_allclose(read_result[col].to_numpy(), self.expected_df[col].to_numpy(), rtol=1e-5)
            
        finally:
            if os.path.exists(temp_output.name):
                os.unlink(temp_output.name)
    
    def test_write_pcd_path_types(self):
        """Test that write_pcd works with both str and Path objects."""
        test_df = pl.DataFrame({
            'x': np.random.uniform(-5, 5, 10).astype(np.float32),
            'y': np.random.uniform(-5, 5, 10).astype(np.float32),
            'z': np.random.uniform(-5, 5, 10).astype(np.float32)
        })
        
        # Test with string path
        temp_str = tempfile.NamedTemporaryFile(suffix='.pcd', delete=False)
        temp_str.close()
        
        # Test with Path object
        temp_path = tempfile.NamedTemporaryFile(suffix='.pcd', delete=False)
        temp_path.close()
        
        try:
            write_pcd(test_df, temp_str.name)
            write_pcd(test_df, Path(temp_path.name))
            
            # Both should work without errors
            result_str = read_pcd(temp_str.name)
            result_path = read_pcd(temp_path.name)
            
            # Compare DataFrames
            assert result_str.equals(result_path)
            
        finally:
            for temp_file in [temp_str.name, temp_path.name]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def test_write_pcd_invalid_input(self):
        """Test that write_pcd raises errors for invalid inputs."""
        temp_output = tempfile.NamedTemporaryFile(suffix='.pcd', delete=False)
        temp_output.close()
        
        try:
            # Test invalid data type
            with pytest.raises(TypeError, match="Expected pl.DataFrame"):
                write_pcd("invalid", temp_output.name)
            
            # Test DataFrame with missing fields
            test_df = pl.DataFrame({'x': [1.0], 'y': [2.0], 'z': [3.0]})
            with pytest.raises(ValueError, match="not found in DataFrame"):
                write_pcd(test_df, temp_output.name, fields=['x', 'y', 'z', 'nonexistent'])
                
        finally:
            if os.path.exists(temp_output.name):
                os.unlink(temp_output.name)
