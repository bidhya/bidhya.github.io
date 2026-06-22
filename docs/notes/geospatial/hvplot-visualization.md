---
tags:
  - Visualization
  - hvPlot
  - Xarray
  - GeoPandas
  - Bokeh
---

# Interactive Geospatial Visualizations with hvplot: Implementation Guide

An engineering reference guide on building high-performance, interactive geospatial dashboards and visual overlays in Python notebooks using HoloViews, Bokeh, and GeoViews backends.

---

## Essential Setup

```python
import hvplot.pandas  # For GeoPandas DataFrames
import hvplot.xarray  # For xarray/rioxarray rasters
import holoviews as hv
hv.extension('bokeh')  # Enable Bokeh backend for interactivity

# Optional: For overlays and layouts
import panel as pn
```

---

## 1. Raster Visualization (hvplot.xarray)

### Basic Raster Plot
```python
import xarray as xr
import rioxarray

# Load raster
da = rioxarray.open_rasterio("dem.tif")

# Squeeze out band dimension if single-band
if 'band' in da.dims and da.sizes['band'] == 1:
    da = da.squeeze('band')

# Basic plot
da.hvplot(
    x='x', y='y',               # Coordinate dimensions
    cmap='terrain',             # Color map
    title='Elevation (DEM)',
    width=600, height=400,
    colorbar=True,
    xlabel='Longitude', ylabel='Latitude'
)
```

### Raster with Custom Color Limits (Remove Outliers)
```python
# Use percentiles to clip extreme values
da.hvplot(
    x='x', y='y',
    cmap='viridis',
    clim=(da.quantile(0.02).values, da.quantile(0.98).values),  # 2nd to 98th percentile
    title='Elevation (clipped)',
    width=600, height=400,
    colorbar=True
)
```

### Raster with Basemap (ESRI, OpenStreetMap, etc.)
```python
da.hvplot(
    x='x', y='y',
    cmap='terrain',
    title='DEM with Basemap',
    width=700, height=500,
    tiles='ESRI',  # Options: 'OSM', 'ESRI', 'CartoDark', 'CartoLight'
    alpha=0.7,     # Transparency for basemap visibility
    colorbar=True
)
```

### Multi-band Raster (Select Band)
```python
# Load multi-band raster
da = rioxarray.open_rasterio("landsat.tif")

# Plot single band
da.sel(band=1).hvplot(
    x='x', y='y',
    cmap='gray',
    title='Band 1 (Red)',
    width=600, height=400,
    colorbar=True
)

# Or use .isel() for index-based selection
da.isel(band=0).hvplot(...)  # First band
```

---

## 2. Vector Visualization (hvplot.pandas for GeoPandas)

### Basic Vector Plot
```python
import geopandas as gpd

# Load vector data
gdf = gpd.read_file("watersheds.shp")

# Basic plot
gdf.hvplot(
    geo=True,              # Enable geographic plotting
    color='blue',
    alpha=0.5,
    title='Watersheds',
    width=600, height=400,
    line_width=2
)
```

### Vector with Basemap
```python
gdf.hvplot(
    geo=True,
    color='red',
    alpha=0.6,
    title='Study Area',
    width=700, height=500,
    tiles='ESRI',         # Add basemap
    hover_cols=['name', 'area'],  # Show attributes on hover
    legend=False
)
```

### Choropleth Map (Color by Attribute)
```python
# Color polygons by attribute value
gdf.hvplot(
    geo=True,
    c='population',       # Column to color by
    cmap='YlOrRd',        # Color map
    alpha=0.7,
    title='Population by County',
    width=700, height=500,
    colorbar=True,
    hover_cols=['name', 'population'],  # Attributes shown on hover
    tiles='CartoDark'
)
```

### Points with Size/Color
```python
# Point data
points_gdf = gpd.GeoDataFrame(...)

points_gdf.hvplot(
    geo=True,
    color='red',
    size='magnitude',     # Size points by attribute
    alpha=0.6,
    title='Sample Locations',
    width=600, height=400,
    tiles='OSM',
    hover_cols='all'      # Show all attributes on hover
)
```

### Lines (e.g., Rivers, Roads)
```python
# LineString geometries
rivers_gdf = gpd.read_file("rivers.shp")

rivers_gdf.hvplot(
    geo=True,
    color='blue',
    line_width=2,
    alpha=0.8,
    title='River Network',
    width=700, height=500,
    tiles='ESRI'
)
```

---

## 3. Overlay Plots (Raster + Vector)

### Simple Overlay with `*` Operator
```python
# Plot raster
raster_plot = da.hvplot(
    x='x', y='y',
    cmap='terrain',
    alpha=0.7,
    colorbar=True,
    width=700, height=500
)

# Plot vector
vector_plot = gdf.hvplot(
    geo=True,
    color='red',
    alpha=0.5,
    line_width=2
)

# Overlay using * operator
overlay = raster_plot * vector_plot
overlay
```

### Overlay with Basemap
```python
# All three layers: basemap + raster + vector
combined = da.hvplot(
    x='x', y='y',
    cmap='terrain',
    alpha=0.6,
    tiles='ESRI',          # Basemap
    colorbar=True,
    width=800, height=600
) * gdf.hvplot(
    geo=True,
    color='red',
    line_width=2,
    alpha=0.7
)

combined
```

### Multiple Vector Layers
```python
watersheds_plot = watersheds_gdf.hvplot(
    geo=True, color='blue', alpha=0.3, line_width=2
)

rivers_plot = rivers_gdf.hvplot(
    geo=True, color='cyan', line_width=3
)

points_plot = points_gdf.hvplot(
    geo=True, color='red', size=100, marker='o'
)

# Combine all
multi_layer = watersheds_plot * rivers_plot * points_plot * hv.Tiles('ESRI')
multi_layer
```

---

## 4. Side-by-Side Layouts

### Two Plots Side by Side with `+` Operator
```python
# Original raster
original = da.hvplot(
    x='x', y='y',
    cmap='terrain',
    title='Original DEM',
    width=400, height=350,
    colorbar=True
)

# Processed raster (e.g., slope)
processed = slope.hvplot(
    x='x', y='y',
    cmap='hot',
    title='Slope (%)',
    width=400, height=350,
    colorbar=True
)

# Side by side
comparison = original + processed
comparison
```

### Grid Layout (2x2)
```python
# Create 4 plots
plot1 = da.hvplot(title='DEM', width=350, height=300)
plot2 = slope.hvplot(title='Slope', width=350, height=300)
plot3 = aspect.hvplot(title='Aspect', width=350, height=300)
plot4 = hillshade.hvplot(title='Hillshade', width=350, height=300)

# Grid layout
grid = (plot1 + plot2 + plot3 + plot4).cols(2)
grid
```

---

## 5. Advanced Customization

### Custom Colorbar Label
```python
da.hvplot(
    x='x', y='y',
    cmap='terrain',
    colorbar=True,
    clabel='Elevation (meters)',  # Custom colorbar label
    title='DEM',
    width=600, height=400
)
```

### Aspect Ratio & Figure Size
```python
da.hvplot(
    x='x', y='y',
    cmap='viridis',
    width=800,
    height=600,
    aspect='equal',  # Or numeric value like 1.5
    frame_width=800,
    frame_height=600
)
```

### Interactive Tools
```python
da.hvplot(
    x='x', y='y',
    cmap='terrain',
    tools=['hover', 'box_zoom', 'wheel_zoom', 'pan', 'reset'],  # Interactive tools
    width=700, height=500
)
```

### Custom Hover Information
```python
# For vector data
gdf.hvplot(
    geo=True,
    hover_cols=['name', 'area', 'population'],  # Specific columns
    # OR
    hover_cols='all',  # All columns
    width=600, height=400
)
```

---

## 6. Common Colormaps

### For Raster Data
```python
# Terrain/Elevation
cmap='terrain'     # Brown-green-white for elevation
cmap='gist_earth'  # Earth tones

# Sequential
cmap='viridis'     # Blue-green-yellow (perceptually uniform)
cmap='plasma'      # Purple-yellow
cmap='YlOrRd'      # Yellow-Orange-Red

# Diverging (positive/negative)
cmap='RdBu'        # Red-Blue
cmap='coolwarm'    # Cool-warm

# Specialized
cmap='hot'         # Black-red-yellow (for slope, heat)
cmap='gray'        # Grayscale (for single-band imagery)
```

### For Vector Choropleth
```python
cmap='YlGnBu'      # Yellow-Green-Blue
cmap='RdYlGn'      # Red-Yellow-Green (diverging)
cmap='Spectral'    # Rainbow-like
```

---

## 7. Basemap Options

```python
tiles='OSM'           # OpenStreetMap (default)
tiles='ESRI'          # ESRI World Imagery (satellite)
tiles='CartoDark'     # Dark basemap (good for bright data)
tiles='CartoLight'    # Light basemap
tiles='WikiMedia'     # Wikipedia maps
tiles='EsriImagery'   # ESRI satellite imagery
tiles='EsriTerrain'   # ESRI terrain
```

---

## 8. Quick Matplotlib Fallback

**When hvplot isn't enough:**

```python
import matplotlib.pyplot as plt

# Vector plot with matplotlib
fig, ax = plt.subplots(figsize=(10, 8))
gdf.plot(ax=ax, column='elevation', cmap='terrain', legend=True, edgecolor='black')
ax.set_title('Watershed Elevations')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()

# Raster plot with matplotlib (from xarray)
fig, ax = plt.subplots(figsize=(10, 8))
da.plot(ax=ax, cmap='terrain', cbar_kwargs={'label': 'Elevation (m)'})
ax.set_title('DEM')
plt.tight_layout()
plt.show()
```

---

## 9. Production-Ready Overlays and Layouts

### Example 1: DEM with Watershed Overlay
```python
# Load data
dem = rioxarray.open_rasterio("dem.tif").squeeze('band')
watershed = gpd.read_file("watershed.shp")

# Ensure CRS match
if watershed.crs != dem.rio.crs:
    watershed = watershed.to_crs(dem.rio.crs)

# Create visualization
plot = dem.hvplot(
    x='x', y='y',
    cmap='terrain',
    alpha=0.7,
    title='Elevation with Watershed Boundary',
    width=700, height=500,
    colorbar=True,
    clabel='Elevation (m)'
) * watershed.hvplot(
    geo=True,
    color='red',
    line_width=3,
    alpha=0.8
)

plot
```

### Example 2: Before/After Comparison
```python
# Original and processed rasters
original = dem.hvplot(
    x='x', y='y',
    cmap='gray',
    title='Original DEM',
    width=400, height=350,
    colorbar=True
)

clipped = dem_clipped.hvplot(
    x='x', y='y',
    cmap='terrain',
    title='Clipped to Watershed',
    width=400, height=350,
    colorbar=True
)

comparison = original + clipped
comparison
```

### Example 3: Points with Raster Context
```python
# Sample points on DEM
points_plot = sample_points.hvplot(
    geo=True,
    c='elevation',      # Color by elevation value
    cmap='RdYlGn',
    size=150,
    alpha=0.8,
    title='Sample Locations',
    colorbar=True,
    hover_cols=['id', 'elevation']
)

dem_plot = dem.hvplot(
    x='x', y='y',
    cmap='terrain',
    alpha=0.5,
    tiles='ESRI'
)

combined = dem_plot * points_plot
combined
```

---

## 10. Common Issues & Fixes

### Issue: Band Dimension Error
```python
# Error: "DataArray must be 2D"
# Fix: Squeeze out band dimension
da = da.squeeze('band')  # If single-band
# OR select band explicitly
da = da.sel(band=1)
```

### Issue: CRS Warning/No Basemap
```python
# Fix: Ensure CRS is set
da.rio.write_crs("EPSG:4326", inplace=True)
gdf = gdf.set_crs("EPSG:4326")
```

### Issue: Plot Too Small/Large
```python
# Adjust width and height
da.hvplot(width=800, height=600)  # Explicit size

# Or use frame dimensions
da.hvplot(frame_width=800, frame_height=600)
```

### Issue: Colorbar Overlaps Plot
```python
# Increase figure width to accommodate colorbar
da.hvplot(width=700, height=500, colorbar=True)
```

---

## 11. Core Best Practices for Collaborative Exploration and Visualization

When presenting or building tools for stakeholders and research partners:

- **Confirm Spatial Alignment Visually**: Early overlay of vector shapes on top of raster outputs mitigates CRS mismatches instantly.
- **Provide Ambient Geospatial Context**: Integrating Web Map Tile Service (WMTS) references (such as `basemap='ESRI'`) allows non-spatial stakeholders to intuitively interpret regional positions.
- **De-risk Scale with Dynamic Decimation**: On massive rasters, standardizing on rasterized Bokeh layers (`rasterize=True`) avoids client-side browser hangs by shifting downsampling computations back to the compiler.
- **Maintain High-Density Metrices**: Making active use of hovering tools and tooltips keeps raw statistics accessible without cluttering cartographic layouts.

---

## Quick Reference Card

| Task | Code |
|------|------|
| **Raster plot** | `da.hvplot(x='x', y='y', cmap='terrain')` |
| **Vector plot** | `gdf.hvplot(geo=True, color='blue')` |
| **Add basemap** | `tiles='ESRI'` |
| **Overlay** | `plot1 * plot2` |
| **Side-by-side** | `plot1 + plot2` |
| **Color by attribute** | `gdf.hvplot(c='column', cmap='viridis')` |
| **Transparency** | `alpha=0.7` |
| **Colorbar label** | `clabel='Elevation (m)'` |
| **Hover info** | `hover_cols=['name', 'value']` |

---

**Bottom Line**: hvplot makes you look professional, shows interactivity, and validates results visually. Use it! 🎨
