# Geospatial & Remote Sensing Engineering Notes

Production-grade references for the geospatial Python engineering stack, coordinate reference system transformations, state estimation algorithms, and hyperspectral physics — the foundational layers of any large-scale Earth observation system.

---

## Data Engineering & Python Stack

<div class="grid cards" markdown>

-   :material-layers: **[Geospatial Python Stack](gis-cheatsheet.md)**

    Canonical import patterns, optimised I/O routines, and production-tested code references for `GeoPandas`, `Rasterio`, `Rioxarray`, `Xarray`, and `GDAL`.

-   :material-map-marker: **[Coordinate Reference Systems & Projections](pyproj-crs.md)**

    Precision CRS transformations, EPSG codes, geodetic vs. projected systems, and float32 precision boundaries in large-scale raster workflows.

-   :material-pipe: **[Production Geospatial Patterns](real-world-patterns.md)**

    Battle-tested implementation patterns for large-scale raster and vector workflows: chunked I/O, memory-safe processing loops, spatial joins at scale, and reproducible pipeline conventions.

-   :material-chart-scatter-plot: **[Interactive Visualization with hvPlot](hvplot-visualization.md)**

    High-level declarative visualizations for `Xarray`, `Pandas`, and `GeoPandas` datasets — browser-native interactivity with HoloViews and Bokeh backends for multi-dimensional geospatial data exploration.

</div>

## State Estimation & Sensor Fusion

<div class="grid cards" markdown>

-   :material-chart-bell-curve: **[Kalman Filtering & State Estimation](kalman-filter.md)**

    Mathematical derivation of the predict-update cycle, extended Kalman filters, and application to LiDAR-IMU sensor fusion for vehicle localization systems.

</div>

## Sensor Physics & Imaging

<div class="grid cards" markdown>

-   :material-waves: **[Hyperspectral Sensor Physics](hyperspectral-concepts.md)**

    Continuous narrow-band spectral arrays vs. discrete multispectral sensors — AVIRIS, PACE OCI, and the radiometric physics behind atmospheric correction and ocean colour retrieval.

</div>
