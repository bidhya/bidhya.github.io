---
tags:
  - GeoPandas
  - Rasterio
  - Xarray
  - Geospatial
  - Python
---

# Geospatial Analysis and Multi-Dimensional Data Pipelines: Vector and Raster Reference Guide

This reference outlines production conventions and optimized design patterns for handling high-resolution satellite imagery, spatiotemporal array telemetry, and vector layers in Python.

## Core Architectural Library Stack

```python
# ============================================================
# CORE IMPORTS - STANDARD PRODUCTION STACK
# ============================================================

# VECTOR OPERATIONS
import geopandas as gpd
from shapely.geometry import Point, Polygon, box

# RASTER OPERATIONS  
import rioxarray                 # Optimized index and coordinate-aware raster I/O

# GRIDDED / SPATIOTEMPORAL DATA (NetCDF, GRIB, Zarr)
import xarray as xr

# MATRICES & COMPUTATIONAL UTILITIES
import numpy as np
import pandas as pd

# FILE & SYSTEM OPERATIONS
import requests
import os                        # Standard OS and file-system path operations

# ============================================================
# SUBSYSTEM BACKUPS (Reserved for legacy / low-level integrations)
# ============================================================
# import rasterio                # Use only if rioxarray won't work
# import gdal                    # Last resort only
```

---

## File Operations (Using `os` Library)

### Check Existence
```python
import os

# Check if file exists
if os.path.exists('data.tif'):
    print("File found!")

# Check if directory
if os.path.isdir('output'):
    print("Directory exists")
```

### Create Directories
```python
# Create single directory
if not os.path.exists('output'):
    os.mkdir('output')

# Create nested directories
os.makedirs('output/results/maps', exist_ok=True)
```

### Path Operations
```python
# Join paths (cross-platform)
file_path = os.path.join('data', 'rasters', 'dem.tif')

# Get absolute path
abs_path = os.path.abspath('data.tif')

# Split path
directory, filename = os.path.split('/path/to/file.tif')
name, ext = os.path.splitext('file.tif')  # ('file', '.tif')

# Get components
dirname = os.path.dirname('/path/to/file.tif')   # '/path/to'
basename = os.path.basename('/path/to/file.tif') # 'file.tif'

# File size
size = os.path.getsize('data.tif')  # Bytes

# List directory
files = os.listdir('data')
```

---

## Raster Operations (Rioxarray - Dataset Integration & Processing)

### Read Raster
```python
import rioxarray

# Read raster
da = rioxarray.open_rasterio('dem.tif')

# Inspect metadata
print(f"CRS: {da.rio.crs}")
print(f"Bounds: {da.rio.bounds()}")
print(f"Resolution: {da.rio.resolution()}")
print(f"Nodata: {da.rio.nodata}")
print(f"Shape: {da.shape}")

# Access as NumPy array
data = da.values

# Lazy loading for big data
da_lazy = rioxarray.open_rasterio('big.tif', chunks={'band': 1, 'y': 1024, 'x': 1024})
```

### Write/Save Raster
```python
# Save raster
da.rio.to_raster('output.tif')

# With compression
da.rio.to_raster('output.tif', compress='lzw')
```

### Reproject Raster
```python
# Reproject to different CRS (ONE LINE!)
da_reprojected = da.rio.reproject('EPSG:4326', resampling=5)  # 5=bilinear

# Reproject to match another raster (CRS + extent + resolution)
da_matched = da.rio.reproject_match(other_da)

# Resampling methods:
# 0 = nearest (for categorical: land cover, soil type)
# 5 = bilinear (for continuous: elevation, temperature)
# 3 = cubic (smoother, slower)
```

### Clip/Mask Raster
```python
# Clip to polygon extent
da_clipped = da.rio.clip(
    polygon_gdf.geometry,
    polygon_gdf.crs,
    drop=True,             # Crop to polygon extent
    all_touched=False      # Only pixels with centers inside
)
```

### Handle Nodata
```python
# Mask nodata values
da_valid = da.where(da != da.rio.nodata)

# Replace nodata with NaN
da_clean = da.where(da != da.rio.nodata, np.nan)

# Set nodata value
da.rio.write_nodata(-9999, inplace=True)
```

### Raster Math
```python
# Simple operations
slope_percent = slope_radians * 100
elevation_feet = elevation_meters * 3.28084

# Band math
ndvi = (nir - red) / (nir + red)

# Conditional
da_masked = da.where(da > 0, 0)  # Replace values <= 0 with 0

# Apply function
da_log = np.log(da.where(da > 0))
```

---

## Vector Operations (GeoPandas)

### Read Vector
```python
import geopandas as gpd

# Read file (shapefile, GeoJSON, GeoPackage, etc.)
gdf = gpd.read_file('watersheds.shp')

# Inspect
print(f"CRS: {gdf.crs}")
print(f"Features: {len(gdf)}")
print(f"Columns: {list(gdf.columns)}")
print(f"Geometry types: {gdf.geometry.type.unique()}")
print(f"Bounds: {gdf.total_bounds}")  # (minx, miny, maxx, maxy)

# View data
print(gdf.head())
```

### Write/Save Vector
```python
# Save to shapefile
gdf.to_file('output.shp')

# Save to GeoJSON
gdf.to_file('output.geojson', driver='GeoJSON')

# Save to GeoPackage (modern, single file)
gdf.to_file('output.gpkg', driver='GPKG')
```

### Reproject Vector
```python
# Reproject to different CRS
gdf_reprojected = gdf.to_crs('EPSG:4326')

# Reproject to match another GeoDataFrame
gdf_reprojected = gdf.to_crs(other_gdf.crs)

# Reproject to match raster
gdf_reprojected = gdf.to_crs(da.rio.crs)
```

### Create Geometries
```python
from shapely.geometry import Point, Polygon, box

# Create point
point = Point(-105.0, 40.0)  # (lon, lat) or (x, y)

# Create polygon
polygon = Polygon([(-105, 40), (-104, 40), (-104, 41), (-105, 41)])

# Create bounding box (easier!)
bbox = box(-105.5, 39.5, -104.5, 40.5)  # (minx, miny, maxx, maxy)

# Create GeoDataFrame from geometries
gdf = gpd.GeoDataFrame(
    {'name': ['Site A', 'Site B']},
    geometry=[Point(-105, 40), Point(-104, 40)],
    crs='EPSG:4326'
)
```

### Spatial Operations
```python
# Intersection (overlay)
intersection = gpd.overlay(gdf1, gdf2, how='intersection')

# Union
union = gpd.overlay(gdf1, gdf2, how='union')

# Difference
difference = gpd.overlay(gdf1, gdf2, how='difference')

# Point in polygon (spatial join)
points_in_poly = gpd.sjoin(points_gdf, polygon_gdf, predicate='within')

# Buffer
gdf_buffered = gdf.copy()
gdf_buffered['geometry'] = gdf.buffer(1000)  # Distance in CRS units
```

### Calculate Properties
```python
# Area (in CRS units squared)
gdf['area'] = gdf.geometry.area

# Length/perimeter
gdf['length'] = gdf.geometry.length

# Centroid
gdf['centroid'] = gdf.geometry.centroid
```

---

## Gridded/Climate Data (Xarray - NetCDF)

### Read NetCDF
```python
import xarray as xr

# Open dataset
ds = xr.open_dataset('climate_data.nc')

# Inspect
print(f"Dimensions: {dict(ds.dims)}")
print(f"Variables: {list(ds.data_vars)}")
print(f"Coordinates: {list(ds.coords)}")

# Extract variable
temp = ds['temperature']
precip = ds['precipitation']
```

### Spatial Subset
```python
# Bounding box
subset = ds.sel(
    lat=slice(30, 50),      # Note: may need to reverse for descending coords
    lon=slice(-110, -90)
)
```

### Temporal Subset
```python
# Time range
subset = ds.sel(time=slice('2020-01-01', '2020-12-31'))
```

### Extract Time Series at Point
```python
# Get time series at location
ts = ds['temperature'].sel(lat=40.0, lon=-105.0, method='nearest')
```

### Save NetCDF
```python
# Save subset or modified data
subset.to_netcdf('subset.nc')
```

---

## Raster-Vector Operations

### Sample Raster at Points
```python
import rioxarray
import geopandas as gpd
import xarray as xr

# Load data
da = rioxarray.open_rasterio('raster.tif')
points_gdf = gpd.read_file('points.shp')

# Ensure CRS match
if points_gdf.crs != da.rio.crs:
    points_gdf = points_gdf.to_crs(da.rio.crs)

# Extract coordinates
x_coords = [p.x for p in points_gdf.geometry]
y_coords = [p.y for p in points_gdf.geometry]

# Sample raster
if 'band' in da.dims:
    values = da.sel(
        x=xr.DataArray(x_coords),
        y=xr.DataArray(y_coords),
        band=1,
        method='nearest'
    ).values
else:
    values = da.sel(
        x=xr.DataArray(x_coords),
        y=xr.DataArray(y_coords),
        method='nearest'
    ).values

# Add to GeoDataFrame
points_gdf['raster_value'] = values

# Handle nodata
if da.rio.nodata is not None:
    points_gdf['raster_value'] = points_gdf['raster_value'].replace(
        da.rio.nodata, np.nan
    )
```

### Zonal Statistics
```python
import rioxarray

da = rioxarray.open_rasterio('raster.tif')
polygons_gdf = gpd.read_file('polygons.shp')

# Ensure CRS match
if polygons_gdf.crs != da.rio.crs:
    polygons_gdf = polygons_gdf.to_crs(da.rio.crs)

# Calculate stats for each polygon
for idx, polygon in polygons_gdf.iterrows():
    # Clip raster to polygon
    clipped = da.rio.clip([polygon.geometry], polygons_gdf.crs, drop=True)
    
    # Handle nodata
    if da.rio.nodata is not None:
        clipped_valid = clipped.where(clipped != da.rio.nodata)
    else:
        clipped_valid = clipped
    
    # Calculate statistics
    polygons_gdf.loc[idx, 'mean'] = float(clipped_valid.mean().values)
    polygons_gdf.loc[idx, 'min'] = float(clipped_valid.min().values)
    polygons_gdf.loc[idx, 'max'] = float(clipped_valid.max().values)
    polygons_gdf.loc[idx, 'std'] = float(clipped_valid.std().values)
    polygons_gdf.loc[idx, 'count'] = int(clipped_valid.count().values)
```

---

## Download Data

### Download from URL
```python
import requests
import os

url = "https://example.com/data.tif"
output_file = 'downloaded.tif'

response = requests.get(url)

if response.status_code == 200:
    with open(output_file, 'wb') as f:
        f.write(response.content)
    print(f"✓ Downloaded: {os.path.getsize(output_file)} bytes")
else:
    print(f"Download failed: {response.status_code}")
```

---

## Common Workflows

### Pattern 1: Load → Reproject → Clip
```python
import rioxarray
import geopandas as gpd

# Load data
da = rioxarray.open_rasterio('dem.tif')
watershed = gpd.read_file('watershed.shp')

# Reproject polygon to match raster
watershed = watershed.to_crs(da.rio.crs)

# Clip
da_clipped = da.rio.clip(watershed.geometry, watershed.crs, drop=True)

# Save
da_clipped.rio.to_raster('dem_clipped.tif')
```

### Pattern 2: Download → Process → Sample
```python
import requests
import rioxarray
import geopandas as gpd
import xarray as xr

# Download
url = "https://example.com/data.tif"
response = requests.get(url)
with open('data.tif', 'wb') as f:
    f.write(response.content)

# Process
da = rioxarray.open_rasterio('data.tif')
da_reproj = da.rio.reproject('EPSG:4326', resampling=5)

# Sample at points
points = gpd.GeoDataFrame(
    geometry=[Point(-105, 40), Point(-104, 40)],
    crs='EPSG:4326'
)
x = [p.x for p in points.geometry]
y = [p.y for p in points.geometry]
values = da_reproj.sel(x=xr.DataArray(x), y=xr.DataArray(y), 
                       method='nearest').values
points['value'] = values
```

### Pattern 3: Intersection + Zonal Stats
```python
import geopandas as gpd
import rioxarray

# Load data
polygons = gpd.read_file('polygons.shp')
points = gpd.read_file('points.shp')
da = rioxarray.open_rasterio('raster.tif')

# Spatial join
points_in_poly = gpd.sjoin(points, polygons, predicate='within')

# Zonal stats
for idx, poly in polygons.iterrows():
    clipped = da.rio.clip([poly.geometry], polygons.crs, drop=True)
    polygons.loc[idx, 'mean'] = float(
        clipped.where(clipped != da.rio.nodata).mean().values
    )

# Save
polygons.to_file('polygons_with_stats.shp')
```

---

## Error Handling

### Check File Existence
```python
import os

if not os.path.exists('data.tif'):
    raise FileNotFoundError("Input file not found!")
```

### Try-Except
```python
try:
    da = rioxarray.open_rasterio('data.tif')
except FileNotFoundError:
    print("File not found!")
except Exception as e:
    print(f"Error: {e}")
```

### Check CRS Match
```python
if gdf.crs != da.rio.crs:
    print("⚠ CRS mismatch! Reprojecting...")
    gdf = gdf.to_crs(da.rio.crs)
```

### Check Empty Results
```python
if len(intersection) == 0:
    print("⚠ Warning: No intersecting features found!")
```

---

## Critical Reminders

### ✅ ALWAYS Check CRS First
```python
# Before any spatial operation
if gdf.crs != da.rio.crs:
    gdf = gdf.to_crs(da.rio.crs)
```

### ✅ ALWAYS Handle Nodata
```python
# Before statistics or math
da_valid = da.where(da != da.rio.nodata)
mean_value = da_valid.mean().values
```

### ✅ Print Intermediate Results
```python
print(f"Loaded: {da.shape}, CRS: {da.rio.crs}")
print(f"After clip: {da_clipped.shape}")
print(f"Result: {len(result)} features")
```

### ✅ Remember Coordinate Order
```python
# (x, y) = (lon, lat)
point = Point(-105.0, 40.0)  # longitude first!
bbox = box(-105.5, 39.5, -104.5, 40.5)  # (minx, miny, maxx, maxy)
```

---

## Your Competitive Advantages

### Modern Stack
> "I use **rioxarray** for raster operations—it's more Pythonic than raw rasterio and scales to big data with Dask."

### NetCDF/Climate Data
> "I use **xarray** extensively for NetCDF climate data—I used it for NEXRAD precipitation analysis in my dissertation."

### Production Experience
> "For TB-scale satellite processing in my research, I use rioxarray with Dask chunking for lazy loading."

---

**Keep this open during the interview for quick syntax reference!** 🚀
