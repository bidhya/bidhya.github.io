---
tags:
  - Geospatial
  - Rasterio
  - Xarray
  - Python
  - Best Practices
---

# Production Design Patterns in Geospatial Analysis and Remote Sensing Pipelines

An engineering reference mapping high-performance, robust collection of implementation patterns for processing multidimensional satellite arrays, vector-raster spatial intersections, and hierarchical climate formats in Python.

---

## 1. Rioxarray + hvplot Visualization Pattern

### Side-by-Side Image Comparison (Common Workflow!)
```python
# Two raster images (e.g., before/after, different bands, time series)
img1 = rioxarray.open_rasterio("image1.tif")
img2 = rioxarray.open_rasterio("image2.tif")

# Create side-by-side plots with hvplot
fig_img1 = img1.hvplot.image(
    rasterize=True,        # For large rasters - renders faster
    x="x", y="y",
    frame_width=600,
    aspect=0.90,           # Aspect ratio (height/width)
    cmap="gray",           # Grayscale for imagery
    title="Img1",
    robust=True            # Use percentiles for color limits (removes outliers)
)

fig_img2 = img2.hvplot.image(
    rasterize=True,
    x="x", y="y",
    frame_width=600,
    aspect=0.90,
    cmap="gray",
    title="Img2",
    robust=True
)

# Display side-by-side using + operator
comparison = fig_img1 + fig_img2
comparison
```

**When to use:**
- Comparing before/after processing
- Multi-temporal analysis
- Different data sources for same area
- Quality control checks

**Key parameters:**
- `rasterize=True` - Essential for large rasters (faster rendering)
- `robust=True` - Auto color scaling using percentiles (2nd-98th)
- `frame_width` - Control figure size
- `aspect` - Adjust height/width ratio

---

## 2. Data Type Management

### Convert to float32 (Memory Optimization)
```python
import numpy as np

# Load raster
da = rioxarray.open_rasterio("large_file.tif")

# Convert to float32 to save memory (vs float64)
da.data = da.data.astype(np.float32)

# Now safe to do calculations without excessive memory use
result = da * 2.5 + 10.0
```

**Why this matters:**
- float64: 8 bytes per pixel
- float32: 4 bytes per pixel
- **50% memory savings** for large rasters!
- Sufficient precision for most geospatial work

---

## 3. CRS Management

### Set/Write CRS Explicitly
```python
# Set CRS on raster (in-place modification)
da.rio.write_crs("EPSG:4326", inplace=True)

# Or create a copy with CRS
da_with_crs = da.rio.write_crs("EPSG:4326", inplace=False)

# Common for data downloaded without proper metadata
```

**When needed:**
- Downloaded data missing CRS
- Programmatically created rasters
- After certain processing operations that strip metadata

---

## 4. Reproject to Match Template

### Align Raster to Reference Grid (CRITICAL for analysis!)
```python
from rasterio.enums import Resampling

# Template raster (defines target grid)
lis_template = rioxarray.open_rasterio("reference.tif")
lis_template.rio.write_crs("EPSG:4326", inplace=True)

# Raster to reproject
da = rioxarray.open_rasterio("data.tif")

# Reproject to match template exactly (CRS, resolution, extent, grid alignment)
da_clipped = da.rio.reproject_match(
    lis_template,
    resampling=Resampling.average  # Options: nearest, bilinear, cubic, average
)

# Now da_clipped has EXACT same grid as lis_template
# Perfect for pixel-by-pixel operations!
```

**Resampling options:**
- `Resampling.nearest` - Categorical data (land cover, classes)
- `Resampling.bilinear` - Continuous data (elevation, temperature) - default
- `Resampling.cubic` - Smooth continuous data (higher quality, slower)
- `Resampling.average` - Downsampling (prevents aliasing)
- `Resampling.mode` - Most common value (for categorical downsampling)

**When to use:**
- Combining multiple rasters (must have same grid!)
- Raster math operations
- Time series analysis
- Machine learning (all inputs must align)

---

## 5. Nodata and Invalid Value Handling

### Access Fill Value and Replace with NaN
```python
import numpy as np

# Load data with fill values (e.g., NetCDF)
dmag = xr.open_dataarray("displacement.nc")

# Replace fill value with NaN (common pattern)
dmag.data[dmag.data == dmag._FillValue] = np.nan

# Replace invalid values (e.g., negatives where not physically possible)
dmag.data[dmag.data <= 0] = np.nan

# Now calculations ignore these invalid pixels automatically
mean_displacement = dmag.mean()  # NaN values excluded
```

**Pattern for rioxarray:**
```python
# For GeoTIFF with nodata value
da = rioxarray.open_rasterio("dem.tif")

# Mask nodata values
if da.rio.nodata is not None:
    da_clean = da.where(da != da.rio.nodata)
    
# Or set to NaN explicitly
da.data[da.data == da.rio.nodata] = np.nan
```

**Why this matters:**
- Prevents contamination of statistics
- Essential for scientific accuracy
- Common in remote sensing data

---

## 6. Extract Single Values from DataArray

### Get Scalar Value from xarray
```python
# Get maximum value as Python scalar
max_val = dmag.max().item(0)  # .item(0) extracts scalar from array

# Compare two datasets
max_new = dmag.max().item(0)
max_old = dmag_old.max().item(0)
print(f"Max displacement: {max_new:.2f} m (was {max_old:.2f} m)")

# Also works for other reductions
min_val = dmag.min().item(0)
mean_val = dmag.mean().item(0)
```

**Alternative methods:**
```python
# Using .values
max_val = float(dmag.max().values)

# Using .item() with no args (if 0-dimensional)
max_val = dmag.max().item()

# Direct indexing for single pixel
pixel_value = dmag.isel(x=100, y=50).item()
```

---

## 7. Create xarray Dataset from Multiple Arrays

### Combine Related Arrays into Dataset
```python
import xarray as xr

# Two related data arrays (same dimensions)
dmag = xr.DataArray(...)    # Displacement magnitude
angle = xr.DataArray(...)   # Displacement direction

# Create dataset with multiple variables
ds = xr.Dataset({
    "dmag": dmag,
    "angle": angle
})

# Access variables
print(ds["dmag"])
print(ds["angle"])

# Save dataset (preserves all variables)
ds.to_netcdf("displacement_data.nc")
```

**When to use:**
- Multiple related variables (e.g., velocity components, multi-band data)
- Keeping metadata together
- NetCDF output format

---

## 8. Data Validation with xarray.testing

### Assert Datasets are Equal (Unit Testing / QA)
```python
import xarray as xr

# Compare two data arrays (useful for validation)
xr.testing.assert_equal(dmag_reverse, dmag)

# If they don't match, raises AssertionError with details
# If they match, passes silently (good for unit tests)
```

**Other comparison functions:**
```python
# Check if close (within tolerance)
xr.testing.assert_allclose(da1, da2, rtol=1e-5)

# Check if identical (including metadata)
xr.testing.assert_identical(da1, da2)
```

**When to use:**
- Validate processing reversibility
- Unit tests
- Quality control
- Debugging transformations

---

## 9. Advanced hvplot Visualization

### Publication-Quality Raster Plot
```python
# Displacement magnitude map with robust color scaling
fig_dmag = dmag.hvplot.image(
    rasterize=True,
    x="x", y="y",
    frame_width=800,
    aspect=0.90,              # Can calculate: asp = height/width
    cmap="jet",               # Rainbow colormap (common for displacement)
    title="dmag (displacement magnitude map (meter))",
    robust=True,              # Auto color limits from percentiles
    # clim=(0, 40)            # Or set explicit color limits
)

fig_dmag
```

**Dynamic aspect ratio:**
```python
# Calculate aspect ratio from data bounds
bounds = dmag.rio.bounds()
width = bounds[2] - bounds[0]
height = bounds[3] - bounds[1]
asp = height / width

# Use in plot
fig = dmag.hvplot.image(..., aspect=asp)
```

**Color limit options:**
```python
# Option 1: robust=True (automatic, uses 2nd-98th percentile)
fig = dmag.hvplot.image(robust=True, ...)

# Option 2: Explicit limits
fig = dmag.hvplot.image(clim=(0, 40), ...)

# Option 3: Percentile-based (manual)
vmin = dmag.quantile(0.02).item()
vmax = dmag.quantile(0.98).item()
fig = dmag.hvplot.image(clim=(vmin, vmax), ...)
```

---

## 10. Complete Workflow Example (Your Typical Pattern)

```python
import numpy as np
import xarray as xr
import rioxarray
import hvplot.xarray
from rasterio.enums import Resampling

# 1. Load template (reference grid)
lis_template = rioxarray.open_rasterio("reference.tif")
lis_template.rio.write_crs("EPSG:4326", inplace=True)

# 2. Load and preprocess data
da = rioxarray.open_rasterio("raw_data.tif")
da.data = da.data.astype(np.float32)  # Memory optimization

# 3. Reproject to match template
da_aligned = da.rio.reproject_match(
    lis_template,
    resampling=Resampling.average
)

# 4. Handle invalid values
da_aligned.data[da_aligned.data <= 0] = np.nan

# 5. Calculate statistics
max_val = da_aligned.max().item(0)
mean_val = da_aligned.mean().item(0)
print(f"Range: {mean_val:.2f} (max: {max_val:.2f})")

# 6. Visualize
fig = da_aligned.hvplot.image(
    rasterize=True,
    x="x", y="y",
    frame_width=800,
    aspect=0.90,
    cmap="viridis",
    title="Processed Data",
    robust=True
)
fig
```

---

## 11. Quick Reference: Your Common Patterns

| Task | Your Pattern |
|------|--------------|
| **Open raster** | `rioxarray.open_rasterio("file.tif")` |
| **Inspect NetCDF groups** | `xr.open_datatree("file.nc")` (xarray >= 2023.9.0) |
| **Load specific group** | `xr.open_dataset("file.nc", group='radiance')` |
| **Set CRS** | `da.rio.write_crs("EPSG:4326", inplace=True)` |
| **Convert dtype** | `da.data = da.data.astype(np.float32)` |
| **Reproject to match** | `da.rio.reproject_match(template, resampling=Resampling.average)` |
| **Remove invalids** | `da.data[da.data <= 0] = np.nan` |
| **Extract scalar** | `da.max().item(0)` |
| **Create dataset** | `xr.Dataset({"var1": da1, "var2": da2})` |
| **Compare arrays** | `xr.testing.assert_equal(da1, da2)` |
| **Visualize (hvplot)** | `da.hvplot.image(rasterize=True, robust=True, ...)` |
| **Visualize (matplotlib)** | `da.plot.imshow(ax=ax, robust=True)` |
| **Side-by-side (hvplot)** | `fig1 + fig2` |
| **Side-by-side (matplotlib)** | `fig, axes = plt.subplots(1, 2, figsize=(20, 8))` |

---

## 12. Matplotlib Visualization Patterns

### Quick Single Raster Plot
```python
import matplotlib.pyplot as plt

# Simple raster display with colorbar
plt.figure(figsize=(12, 10))
plt.imshow(theta_degrees, cmap=plt.cm.magma)
plt.colorbar(shrink=0.6)  # Colorbar at 60% height (prevents overlap)
plt.title("Angle (degrees)")
plt.xlabel("Column")
plt.ylabel("Row")
plt.tight_layout()
plt.show()
```

**Colorbar shrink parameter:**
- `shrink=0.6` - Makes colorbar 60% of plot height
- Prevents colorbar from being taller than the plot
- Common values: 0.6-0.8 for single plots, 0.5 for subplots

**Common colormaps:**
```python
# Sequential (ordered data)
cmap=plt.cm.magma      # Dark purple to yellow
cmap=plt.cm.viridis    # Blue to yellow (perceptually uniform)
cmap=plt.cm.plasma     # Purple to yellow

# Diverging (positive/negative)
cmap="coolwarm"        # Blue to red (your pattern for magnitude)
cmap="RdBu"            # Red to blue
cmap="seismic"         # Blue-white-red

# Specialized
cmap="terrain"         # For elevation
cmap="gray"            # Grayscale
```

### Side-by-Side Comparison with Subplots (Your Pattern!)
```python
import matplotlib.pyplot as plt

# Load rasters (xarray DataArrays)
img1 = rioxarray.open_rasterio("image1.tif").squeeze('band')
img2 = rioxarray.open_rasterio("image2.tif").squeeze('band')

# Create figure with 2 subplots side-by-side
fig, axes = plt.subplots(1, 2, figsize=(20, 8))
ax0, ax1 = axes  # Unpack axes (cleaner than axes[0], axes[1])

# Plot first image
img1.plot.imshow(ax=ax0, robust=True)  # robust=True uses percentile limits
ax0.set_title("Input: Img1 (WV03_20181104_...)")

# Plot second image
img2.plot.imshow(ax=ax1, robust=True)
ax1.set_title("Input: Img2 (WV02_20181116_...)")

plt.tight_layout()  # Prevent overlap
plt.show()
```

**Why `plot.imshow()` from xarray:**
- Automatically handles coordinates (vs raw numpy array)
- `robust=True` uses 2nd-98th percentile for color limits (removes outliers)
- Preserves spatial extent and labels
- Can add `cmap=`, `vmin=`, `vmax=` parameters

### Enhanced Subplots Pattern (Best Practices)
```python
import matplotlib.pyplot as plt
import numpy as np

# Create subplots
fig, axes = plt.subplots(1, 2, figsize=(20, 8))
ax0, ax1 = axes

# Plot 1: Angle map
im0 = ax0.imshow(theta_degrees, cmap=plt.cm.magma)
ax0.set_title("Displacement Direction (degrees)", fontsize=14)
ax0.set_xlabel("Easting (pixels)")
ax0.set_ylabel("Northing (pixels)")
cbar0 = plt.colorbar(im0, ax=ax0, shrink=0.6)
cbar0.set_label("Degrees", rotation=270, labelpad=20)

# Plot 2: Magnitude map
im1 = ax1.imshow(mag, cmap="coolwarm")
ax1.set_title("Displacement Magnitude", fontsize=14)
ax1.set_xlabel("Easting (pixels)")
ax1.set_ylabel("Northing (pixels)")
cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.6)
cbar1.set_label("Magnitude (m)", rotation=270, labelpad=20)

plt.tight_layout()
plt.show()
```

**Best practices added:**
- ✅ Explicit axis labels (`set_xlabel`, `set_ylabel`)
- ✅ Font size control (`fontsize=14`)
- ✅ Colorbar labels with `set_label()`
- ✅ `rotation=270, labelpad=20` for vertical colorbar labels
- ✅ `tight_layout()` prevents overlap
- ✅ Save return value from `imshow()` for colorbar reference

### Save Figure (Interview-Ready)
```python
# Create plot
fig, ax = plt.subplots(figsize=(12, 10))
im = ax.imshow(theta_degrees, cmap=plt.cm.magma)
plt.colorbar(im, ax=ax, shrink=0.6, label="Angle (degrees)")
ax.set_title("Displacement Direction")

# Save with high DPI
plt.tight_layout()
plt.savefig("displacement_angle.png", dpi=300, bbox_inches='tight')
plt.show()
```

**Save options:**
- `dpi=300` - Publication quality (default is 100)
- `bbox_inches='tight'` - Removes extra whitespace
- `transparent=True` - Transparent background (for presentations)
- `format='pdf'` - Vector format (scalable)

### xarray Plot Integration (Your Workflow)
```python
# xarray DataArrays have built-in plotting
import xarray as xr

# Single plot
da.plot(cmap="terrain", robust=True, figsize=(10, 8))
plt.title("Elevation (m)")
plt.tight_layout()
plt.show()

# Subplots with xarray
fig, axes = plt.subplots(1, 2, figsize=(18, 7))

da1.plot.imshow(ax=axes[0], cmap="viridis", robust=True, 
                cbar_kwargs={'label': 'Value 1', 'shrink': 0.6})
axes[0].set_title("Dataset 1")

da2.plot.imshow(ax=axes[1], cmap="plasma", robust=True,
                cbar_kwargs={'label': 'Value 2', 'shrink': 0.6})
axes[1].set_title("Dataset 2")

plt.tight_layout()
plt.show()
```

**xarray plot advantages:**
- Automatically labels axes with coordinate names
- `robust=True` built-in
- `cbar_kwargs` for colorbar customization
- Works with geographic coordinates

### Quick Matplotlib vs hvplot Decision

| Use Matplotlib When: | Use hvplot When: |
|---------------------|------------------|
| Need fine control over styling | Want interactive plots |
| Publication-quality figures | Quick exploration |
| Multiple subplots with shared axes | Need tooltips/hover info |
| Complex annotations | Want basemaps |
| Saving static images | Real-time data inspection |
| Presentation slides | Jupyter notebook workflow |

**Workflow Selection Guide:**
- Use **hvplot** during early prototyping, exploratory analysis, and human-in-the-loop interactive validation.
- Standardize on **matplotlib** for static report rendering, detailed cartographic annotations, and publication-ready imagery outputs.

### Complete Matplotlib Example (Production Quality)
```python
import matplotlib.pyplot as plt
import rioxarray
import numpy as np

# Load data
img1 = rioxarray.open_rasterio("before.tif").squeeze('band')
img2 = rioxarray.open_rasterio("after.tif").squeeze('band')

# Calculate change
change = img2 - img1
change.data[np.abs(change.data) < 0.1] = np.nan  # Mask small changes

# Create 3-panel comparison
fig, axes = plt.subplots(1, 3, figsize=(24, 7))
ax0, ax1, ax2 = axes

# Before
img1.plot.imshow(ax=ax0, cmap="gray", robust=True,
                 cbar_kwargs={'shrink': 0.6, 'label': 'DN'})
ax0.set_title("Before (2018-11-04)", fontsize=14)

# After
img2.plot.imshow(ax=ax1, cmap="gray", robust=True,
                 cbar_kwargs={'shrink': 0.6, 'label': 'DN'})
ax1.set_title("After (2018-11-16)", fontsize=14)

# Change
change.plot.imshow(ax=ax2, cmap="coolwarm", robust=True,
                   cbar_kwargs={'shrink': 0.6, 'label': 'Change (DN)'})
ax2.set_title("Change Detection", fontsize=14)

plt.tight_layout()
plt.savefig("comparison.png", dpi=300, bbox_inches='tight')
plt.show()

print(f"Maximum change: {np.nanmax(np.abs(change.data)):.2f} DN")
```

---

## 13. xarray DataTree for NetCDF Group Exploration

### Inspect Hierarchical NetCDF Structure (Modern Best Practice)
```python
import xarray as xr

# STEP 1: Inspect NetCDF with groups using DataTree (xarray >= 2023.9.0)
dt = xr.open_datatree("aviris_data.nc")
print(dt)

# Output shows complete hierarchy:
# DataTree('/', parent=None)
# ├── Group: /
# │   └── Dimensions: lat: 1280, lon: 1234
# ├── Group: /geolocation_lookup_table
# │   └── Variables: northing, easting
# └── Group: /radiance
#     └── Variables: radiance (wavelength=284, lines=1280, samples=1234), fwhm

# STEP 2: Load specific group directly
ds_radiance = xr.open_dataset("aviris_data.nc", group='radiance')

# Extract data
radiance = ds_radiance['radiance'].values
wavelengths = ds_radiance['wavelength'].values

print(f"Loaded radiance: {radiance.shape}")  # (284, 1280, 1234) or similar
```

**When to use:**
- **First time** working with a new NetCDF file format (AVIRIS, PACE, EMIT, etc.)
- Files with **hierarchical group structure** (HDF5/NetCDF4)
- **Documentation/exploration phase** - understand what's available before coding
- **Rapid prototyping** - no guessing about group names or variable locations

**Advantages of DataTree inspection:**
- ✅ See **complete structure** in one call - no trial and error
- ✅ Identify **all groups, variables, dimensions** transparently
- ✅ **Built into xarray** (>= 2023.9.0) - no extra packages needed
- ✅ Same pattern works across datasets (AVIRIS, PACE, MODIS with groups, etc.)

**Workflow pattern:**
1. **Exploration**: Use `xr.open_datatree()` to inspect structure
2. **Production**: Use `xr.open_dataset(file, group='specific_group')` for targeted loading
3. **Documentation**: Include DataTree output in notebooks/comments for clarity

### Fallback for Older xarray Versions
```python
import xarray as xr

# If xr.open_datatree() is not available (xarray < 2023.9.0)
try:
    dt = xr.open_datatree("aviris_data.nc")
    print(dt)
except AttributeError:
    print("xarray version does not have built-in DataTree")
    print("Update with: pip install --upgrade xarray")
    # Manual exploration: try loading root and check groups attribute
    ds_root = xr.open_dataset("aviris_data.nc")
    print(f"Root variables: {list(ds_root.variables)}")
```

**Real-world example (from AVIRIS-3 processing):**
- AVIRIS files have `/`, `/geolocation_lookup_table`, `/radiance` groups
- Using DataTree showed radiance group has (wavelength: 284, lines: 1280, samples: 1234)
- Discovered coordinates needed transpose: `radiance.transpose('lines', 'samples', 'wavelength')`
- Same pattern applies to PACE ocean color (root + multiple science variable groups)

### Multi-dimensional Group Analysis Workflow
When ingest processes deal with scientific formats (like AVIRIS or PACE), using xarray's DataTree permits high-level group structural validation. This allows developers to systematically inspect variable distributions, dimensionality scales, and geometric resolutions upfront. For production integrations, target groups can then be opened on-demand using standard parameter calls `xr.open_dataset(group='specific_group')`.

**Related patterns:**
- Works seamlessly with patterns #4 (reproject), #5 (nodata handling), #7 (create datasets)
- Essential for **multi-modal satellite data** (optical + thermal + quality flags in separate groups)
- Foundation for **scalable pipelines** - inspect once, document structure, codify loading
  
---

## Summary of Core Implementation Best Practices

### 1. Robust Dataset Ingestion & Validation
- **CRS Alignment**: Always enforce matching coordinate systems upfront before executing multi-source calculations (`reproject_match`).
- **Nodata Filtering**: Remove or mask no-data values prior to statistical aggregations to avoid data skew.
- **Dynamic Limits**: Use quantile-based color mapping ranges (`robust=True`) to automatically drop distribution outliers during inspection.

### 2. Micro-Memory Optimization
- **Data-Precision Allocation**: Use single-precision arrays (`float32`) instead of double-precision (`float64`) to halve raw memory footprint.
- **Sparse Representations**: Isolate and mask regions of interest early inside processing streams to avoid computing over empty spatial bounds.

### 3. High-Throughput Web Exploitation
- **Raster Rendering Optimization**: Ensure large datasets make use of dynamically resampled tiles (`rasterize=True`) to preserve display latency during exploratory review.

---

**Bottom Line**: These implementation patterns form the foundational blueprint for production-grade geospatial and climate pipeline development. 🎯
