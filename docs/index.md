---
hide:
  - navigation
  - toc
---

<div class="hero-banner" markdown="1">

# Bidhyananda Yadav

**Geocomputational Scientist &nbsp;·&nbsp; Spatial Data Engineer &nbsp;·&nbsp; ML/AI Researcher**

Seven years designing TB-scale Earth observation pipelines, ML/AI workflows, and HPC infrastructure for NASA and NSF programmes at The Ohio State University.

[Engineering Notes](notes/ai-ml/index.md){ .md-button .md-button--primary }
[Technical Workflows](tutorials/index.md){ .md-button }

</div>

---

## What I Build

<div class="grid cards" markdown>

-   :material-earth: **Geospatial & Remote Sensing**

    ---

    Processing optical, SAR, LiDAR, and hyperspectral satellite data at TB scale. ETL pipelines for continental coverage built on `Xarray`, `Rioxarray`, `GDAL`, and `GeoPandas`.

-   :material-brain: **Scientific ML & AI Systems**

    ---

    Doctoral research in applied ML: ensemble methods (Random Forest, Gradient Boosting, Extra Trees), regularized regression, and geospatial feature engineering across 1,200+ USGS gages at continental scale. Extended since into deep learning integration, remote-sensing data pipelines, and AI application support for research teams.

-   :material-server: **HPC & Cloud Infrastructure**

    ---

    Distributed SLURM cluster workflows and AWS-native pipelines (Lambda, S3, containers). Designed for reproducibility and seamless HPC-to-cloud migration at scale.

</div>

---

## Featured Research

<div class="grid cards" markdown>

-   **:material-satellite-variant: NASA SWOT Satellite Mission**

    ---

    Co-led remote sensing algorithms for global river discharge and lake dynamics. Led the initial prototype of worldwide SWOT analytics dashboard ([swotviz.cuahsi.io](https://swotviz.cuahsi.io/){target="_blank"}) serving international hydrology teams.

    *NASA Grant · $925,353 · 2022–2025*

-   **:material-snowflake: Continental Snow Water Equivalent**

    ---

    Architected a 20-year daily SWE data product for North America at 0.01° resolution (~30 TB). Fused MODIS satellite observations with LISF land surface model outputs. Implemented on NASA Discover HPC clusters using [Julia](https://julialang.org/){target="_blank"} and [JuMP](https://jump.dev/JuMP.jl/stable/){target="_blank"}. [Open-source pipeline](https://github.com/bidhya/verse/){target="_blank"}.

    *NASA Grant · 2022–2025*

-   **:material-chart-line: ICESat-2 & ArcticDEM Elevation Toolkit**

    ---

    Python toolkit to download and process ICESat-2 laser altimetry data across Antarctica and the Arctic, correcting systematic elevation biases in high-resolution DEMs ([Data products](https://www.pgc.umn.edu/data){target="_blank"}: ArcticDEM, REMA, WorldDEM). A multi-agency collaborative work with Universities and Federal Agencies.

-   **:material-map-marker-path: Greenland Glacier Velocity**

    ---

    Satellite pipeline to map ice velocity across Greenland outlet glaciers using Sentinel-2 (A/B/C) and Landsat imagery. [Open-source pipeline](https://github.com/bidhya/greenland-glacier-flow){target="_blank"} with data delivered to [NSIDC DAAC](https://nsidc.org/data/nsidc-0777/versions/1/){target="_blank"}. Published in *The Cryosphere*.

-   **:material-monitor-dashboard: Fluid Earth Viewer**

    ---

    Contributed to FEVer, an interactive web application visualizing global atmospheric and ocean conditions for public science communication. Implemented climate metric aggregations (monthly, seasonal, annual) and derived data products. Later adopted by the [Permafrost Discovery Gateway](https://pdg.open.uaf.edu/){target="_blank"}. [fever.byrd.osu.edu](https://fever.byrd.osu.edu/){target="_blank"}

    *NSF Grant*

-   **:material-water: Deep Learning for ArcticDEM Hydrology**

    ---

    Built satellite-data pipelines, preprocessing workflows, and downstream integration layers for PyTorch-based water classification research using Sentinel-2 and commercial high-resolution imagery. Published in *Journal of Hydrology* and *Remote Sensing of Environment*.

</div>

---

## Explore the Knowledge Base

<div class="grid cards" markdown>

-   :material-book-open-page-variant: **Engineering Notes**

    ---

    Deep-dives into GPU and distributed training, transformer architectures, Kalman filtering, hyperspectral physics, and the geospatial Python engineering stack. Developed as public reference material to help domain scientists and research teams build practical intuition for AI/ML workflows.

    [:octicons-arrow-right-24: Browse Engineering Notes](notes/ai-ml/index.md)

-   :material-test-tube: **Technical Workflows**

    ---

    End-to-end Jupyter notebooks: the NASA PACE hyperspectral series, a satellite change detection pipeline, and applied NLP workflows.

    [:octicons-arrow-right-24: Browse Technical Workflows](tutorials/index.md)

</div>
