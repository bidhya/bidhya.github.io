---
tags:
  - CRS
  - Projections
  - PyProj
  - Geospatial
  - Python
---

# Coordinate Reference Systems and Precision Transformations with PyProj: Reference Guide

An engineering reference mapping low-level geodetic calculations, datum conversions, coordinate projection transforms, and UTM validation in Python.

---

## Essential Imports

```python
from pyproj import CRS, Transformer
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
import pyproj
```

---

## 1. CRS Creation & Inspection

### Create CRS from EPSG Code
```python
# Most common way
crs = CRS.from_epsg(4326)  # WGS84
print(crs.name)            # 'WGS 84'
print(crs.is_geographic)   # True
print(crs.is_projected)    # False

# UTM example
crs_utm = CRS.from_epsg(32613)  # UTM Zone 13N
print(crs_utm.name)             # 'WGS 84 / UTM zone 13N'
print(crs_utm.is_projected)     # True
```

### Create CRS from WKT or PROJ String
```python
# From WKT (Well-Known Text)
wkt = '''GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563]],
    PRIMEM["Greenwich",0],
    UNIT["degree",0.0174532925199433]]'''
crs = CRS.from_wkt(wkt)

# From PROJ string (older format)
crs = CRS.from_proj4("+proj=longlat +datum=WGS84 +no_defs")
```

### Inspect CRS Properties
```python
crs = CRS.from_epsg(32613)

print(crs.name)                    # 'WGS 84 / UTM zone 13N'
print(crs.area_of_use)             # Geographic area where valid
print(crs.datum)                   # Datum information
print(crs.ellipsoid)               # Ellipsoid parameters
print(crs.to_epsg())               # 32613 (if EPSG code exists)
print(crs.to_wkt())                # Full WKT representation
print(crs.to_proj4())              # PROJ string (deprecated but useful)
print(crs.axis_info)               # Axis order and units
```

---

## 2. CRS Comparison

### Check if Two CRS are Equivalent
```python
crs1 = CRS.from_epsg(4326)
crs2 = CRS.from_epsg(4326)
crs3 = CRS.from_epsg(32613)

print(crs1 == crs2)        # True
print(crs1 == crs3)        # False
print(crs1.equals(crs2))   # True (more robust comparison)
```

### Check CRS Type
```python
crs = CRS.from_epsg(4326)

if crs.is_geographic:
    print("Geographic CRS (lat/lon)")
elif crs.is_projected:
    print("Projected CRS (meters/feet)")
elif crs.is_vertical:
    print("Vertical CRS (elevation)")
```

---

## 3. Coordinate Transformation (Most Important!)

### Basic Point Transformation
```python
# Create transformer: source CRS -> target CRS
transformer = Transformer.from_crs(
    "EPSG:4326",      # Source: WGS84 (lon, lat)
    "EPSG:32613",     # Target: UTM Zone 13N (x, y in meters)
    always_xy=True    # CRITICAL: Use (lon, lat) order, not (lat, lon)
)

# Transform single point
lon, lat = -105.0, 40.0
x, y = transformer.transform(lon, lat)
print(f"UTM: ({x:.2f}, {y:.2f})")  # (500000.00, 4427621.26)

# Transform multiple points (arrays)
import numpy as np
lons = np.array([-105.0, -105.1, -105.2])
lats = np.array([40.0, 40.1, 40.2])
xs, ys = transformer.transform(lons, lats)
print(xs)  # Array of x coordinates
print(ys)  # Array of y coordinates
```

### Reverse Transformation
```python
# UTM -> WGS84
transformer_reverse = Transformer.from_crs(
    "EPSG:32613",  # Source: UTM
    "EPSG:4326",   # Target: WGS84
    always_xy=True
)

x, y = 500000, 4427621
lon, lat = transformer_reverse.transform(x, y)
print(f"Lon/Lat: ({lon:.6f}, {lat:.6f})")  # (-105.0, 40.0)
```

### Why `always_xy=True` Matters
```python
# WITHOUT always_xy=True (dangerous - uses CRS native order)
transformer_latlon = Transformer.from_crs("EPSG:4326", "EPSG:32613")
# EPSG:4326 native order is (lat, lon), so you'd need:
x, y = transformer_latlon.transform(40.0, -105.0)  # (lat, lon) - confusing!

# WITH always_xy=True (recommended - consistent)
transformer_xy = Transformer.from_crs("EPSG:4326", "EPSG:32613", always_xy=True)
x, y = transformer_xy.transform(-105.0, 40.0)  # (lon, lat) - clear!

# ALWAYS USE always_xy=True to avoid confusion!
```

---

## 4. Find Appropriate UTM Zone

```python
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info

# Find UTM zone for a location
lon, lat = -105.0, 40.0

utm_crs_list = query_utm_crs_info(
    datum_name="WGS 84",
    area_of_interest=AreaOfInterest(
        west_lon_degree=lon,
        south_lat_degree=lat,
        east_lon_degree=lon,
        north_lat_degree=lat
    )
)

# Get the best match (usually first result)
utm_crs = CRS.from_epsg(utm_crs_list[0].code)
print(f"Best UTM zone: {utm_crs.name}")  # WGS 84 / UTM zone 13N
print(f"EPSG code: {utm_crs_list[0].code}")  # 32613
```

---

## 5. Geodesic Calculations (Distance/Area on Ellipsoid)

### Calculate Distance Between Points
```python
from pyproj import Geod

# Create geodesic calculator for WGS84 ellipsoid
geod = Geod(ellps="WGS84")

# Two points
lon1, lat1 = -105.0, 40.0
lon2, lat2 = -104.9, 40.1

# Calculate forward azimuth, back azimuth, and distance
fwd_azimuth, back_azimuth, distance = geod.inv(lon1, lat1, lon2, lat2)

print(f"Distance: {distance:.2f} meters")  # ~15,713 m
print(f"Bearing: {fwd_azimuth:.2f} degrees")
```

### Calculate Point at Distance/Bearing
```python
# Starting point
lon, lat = -105.0, 40.0

# Go 10 km at 45 degrees bearing
distance = 10000  # meters
bearing = 45      # degrees

lon_new, lat_new, back_az = geod.fwd(lon, lat, bearing, distance)
print(f"New point: ({lon_new:.6f}, {lat_new:.6f})")
```

### Calculate Polygon Area (Geodesic)
```python
# Polygon vertices (closed ring)
lons = [-105.0, -104.9, -104.9, -105.0, -105.0]
lats = [40.0, 40.0, 40.1, 40.1, 40.0]

area, perimeter = geod.polygon_area_perimeter(lons, lats)
print(f"Area: {abs(area) / 1e6:.2f} km²")
print(f"Perimeter: {perimeter / 1000:.2f} km")
```

---

## 6. Integration with GeoPandas/Rioxarray

### Check CRS Compatibility
```python
import geopandas as gpd
import rioxarray
from pyproj import CRS

# Read data
gdf = gpd.read_file("watersheds.shp")
da = rioxarray.open_rasterio("dem.tif")

# Get PyProj CRS objects
gdf_crs = CRS.from_user_input(gdf.crs)
raster_crs = CRS.from_user_input(da.rio.crs)

# Check if they match
if gdf_crs.equals(raster_crs):
    print("CRS match!")
else:
    print(f"CRS mismatch: {gdf_crs.name} vs {raster_crs.name}")
```

### Manual Coordinate Transformation (if needed)
```python
# Usually GeoPandas handles this, but for manual control:
gdf = gpd.read_file("points.shp")  # EPSG:4326

# Extract coordinates
lons = gdf.geometry.x.values
lats = gdf.geometry.y.values

# Transform using PyProj
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32613", always_xy=True)
xs, ys = transformer.transform(lons, lats)

# Create new GeoDataFrame (or update geometry)
from shapely.geometry import Point
gdf_utm = gdf.copy()
gdf_utm['geometry'] = [Point(x, y) for x, y in zip(xs, ys)]
gdf_utm = gdf_utm.set_crs("EPSG:32613")
```

---

## 7. Common Production & Software Architectural Scenarios

### Scenario 1: Validate CRS Match Before Operation
```python
def check_crs_match(crs1, crs2):
    """Check if two CRS are equivalent"""
    pyproj_crs1 = CRS.from_user_input(crs1)
    pyproj_crs2 = CRS.from_user_input(crs2)
    return pyproj_crs1.equals(pyproj_crs2)

# Usage
if not check_crs_match(gdf.crs, da.rio.crs):
    print("Reprojecting required!")
    gdf = gdf.to_crs(da.rio.crs)
```

### Scenario 2: Transform Point Cloud (Batch)
```python
def transform_points(lons, lats, source_epsg, target_epsg):
    """Transform arrays of coordinates"""
    transformer = Transformer.from_crs(
        f"EPSG:{source_epsg}",
        f"EPSG:{target_epsg}",
        always_xy=True
    )
    return transformer.transform(lons, lats)

# Usage
xs, ys = transform_points(
    lons=[-105.0, -105.1, -105.2],
    lats=[40.0, 40.1, 40.2],
    source_epsg=4326,
    target_epsg=32613
)
```

### Scenario 3: Calculate Great Circle Distance
```python
def calculate_distance(lon1, lat1, lon2, lat2):
    """Calculate geodesic distance between two points"""
    geod = Geod(ellps="WGS84")
    _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
    return distance

# Usage
dist_m = calculate_distance(-105.0, 40.0, -104.9, 40.1)
print(f"Distance: {dist_m / 1000:.2f} km")
```

---

## 8. Quick Reference Table

| Operation | Code |
|-----------|------|
| Create CRS | `CRS.from_epsg(4326)` |
| Get EPSG code | `crs.to_epsg()` |
| Check if geographic | `crs.is_geographic` |
| Check if projected | `crs.is_projected` |
| Compare CRS | `crs1.equals(crs2)` |
| Transform point | `Transformer.from_crs(src, dst, always_xy=True).transform(x, y)` |
| Calculate distance | `Geod(ellps="WGS84").inv(lon1, lat1, lon2, lat2)` |
| Find UTM zone | `query_utm_crs_info(datum_name="WGS 84", area_of_interest=...)` |

---

## Common EPSG Codes (Memorize These!)

| EPSG | Description | Units |
|------|-------------|-------|
| **4326** | WGS 84 (GPS) | degrees |
| **3857** | Web Mercator (Google Maps) | meters |
| **32613** | UTM Zone 13N (Colorado) | meters |
| **32633** | UTM Zone 33N (Central Europe) | meters |
| **5070** | NAD83 Albers (CONUS) | meters |
| **2163** | US National Atlas Equal Area | meters |

---

## When to Use PyProj vs GeoPandas/Rioxarray

### ✅ Use PyProj When:
- Need low-level coordinate transformation
- Working with point arrays (not GeoDataFrames)
- Need geodesic calculations (distance, bearing, area)
- Validating CRS compatibility
- Finding appropriate UTM zone programmatically

### ✅ Use GeoPandas/Rioxarray When:
- Reprojecting vector/raster data
- Working with spatial data files
- Need automatic CRS handling
- Doing spatial operations (clip, intersect, buffer)

### 💡 Architectural Integration Pattern:
- **Low-Level Precision and Domain Separation**: Use `pyproj` directly when you require highly precise control over low-level coordinate transformations, localized datums, geodesic calculations, or custom projection lookup parameters.
- **High-Level Pipelines**: Leverage the high-level wrappers in `geopandas` and `rioxarray` for standard dataset-wide operations (e.g., calling `.to_crs()` or `.rio.reproject()`) to maintain code cleanliness and let those engines internally delegate tasks to modern standard PROJ installations efficiently.

---

## Critical Reminders

⚠️ **ALWAYS use `always_xy=True`** in Transformer to avoid lat/lon confusion  
⚠️ **Check CRS match** before spatial operations  
⚠️ **Geographic CRS** (EPSG:4326) = degrees, **Projected CRS** (UTM) = meters  
⚠️ **UTM zones** valid only within ~6° longitude bands  
⚠️ **Use geodesic calculations** (Geod) for distances in geographic coordinates, not simple Euclidean!

---

## Practice Questions

1. **Transform point** (-105.27, 40.02) from WGS84 to UTM Zone 13N
2. **Calculate distance** between Denver (-104.99, 39.74) and Boulder (-105.27, 40.02)
3. **Find UTM zone** for coordinates (-122.42, 37.77) (San Francisco)
4. **Check if CRS match**: EPSG:4326 vs EPSG:32613

<details>
<summary>Solutions</summary>

```python
# 1. Transform point
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32613", always_xy=True)
x, y = transformer.transform(-105.27, 40.02)
print(f"UTM: ({x:.2f}, {y:.2f})")  # (478613.97, 4429833.85)

# 2. Calculate distance
geod = Geod(ellps="WGS84")
_, _, dist = geod.inv(-104.99, 39.74, -105.27, 40.02)
print(f"Distance: {dist/1000:.2f} km")  # ~37.5 km

# 3. Find UTM zone
utm_list = query_utm_crs_info(
    datum_name="WGS 84",
    area_of_interest=AreaOfInterest(-122.42, 37.77, -122.42, 37.77)
)
print(f"UTM Zone: EPSG:{utm_list[0].code}")  # EPSG:32610 (Zone 10N)

# 4. Check CRS match
crs1 = CRS.from_epsg(4326)
crs2 = CRS.from_epsg(32613)
print(crs1.equals(crs2))  # False
```
</details>

---

**Architectural Summary:**  
PyProj is the low-level geodetic engine powering spatial data libraries. Designing robust ETL pipelines involves delegating typical tabular and gridded transformations to high-level structures (`geopandas`, `rioxarray`, `rasterio`) while utilizing `pyproj` directly for fine-grained geodetic validations, custom transformations, precise geodesic calculations, or region-of-interest coordinate projection mapping across massive distributed scales. 🎯
