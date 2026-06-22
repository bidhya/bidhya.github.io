# Bidhyananda Yadav, PhD

**Research Associate · Geocomputational Scientist · Spatial Data Engineer**  
Byrd Polar and Climate Research Center, The Ohio State University  
[yadav.111@osu.edu](mailto:yadav.111@osu.edu) · [Google Scholar](https://scholar.google.com/citations?user=ZMb8ADQAAAAJ&hl=en){target="_blank"}

---

## About

I build systems that turn satellite data into scientific knowledge. Over seven years at OSU's Byrd Polar and Climate Research Center, I have designed and deployed large-scale geospatial pipelines, machine learning algorithms, and analytics platforms for NASA and NSF Earth observation missions — working across the full stack from raw HPC data ingestion to stakeholder-facing dashboards.

My background sits at the intersection of remote sensing physics, computational hydrology, and applied ML. I trained as a geoscientist (PhD, UF) — my dissertation (2018) applied eight ML algorithms (Random Forest, Gradient Boosting, Extra Trees, SVM, regularized regression) to predict hydrologic signatures across 1,200+ USGS gages at continental scale, with rigorous cross-validation, feature selection, and ensemble evaluation. That grounding in applied statistical ML preceded my OSU role and shaped how I approach model development: feature engineering first, proper evaluation discipline, production-aware pipelines. Since joining OSU, that foundation extended into deep learning integration, large-scale satellite data workflows, and AI application delivery for NASA and NSF programmes.

My work bridges domain science and engineering — translating scientific questions into production-grade data systems, AI workflows, and analytics platforms. I approach complex problems by combining deep methodology discipline with AI-assisted development (Copilot, Claude, HuggingFace), enabling rapid implementation without sacrificing scientific rigor.

---

## Selected Work

### SWOT Global River Dashboard
NASA's Surface Water and Ocean Topography satellite generates continuous global river and lake observations. I co-led the remote sensing workflows for river discharge and lake dynamics estimation, then built the worldwide visual analytics dashboard ([swotviz.cuahsi.io](https://swotviz.cuahsi.io/){target="_blank"}) for federal agency partners and the research community. The platform handles multi-terabyte SWOT swath data and serves interactive visualizations to NOAA, USGS, and NASA stakeholders.

### Continental Snow Water Equivalent Dataset
There is no direct satellite sensor for snow water equivalent at the scale and resolution needed for water resource decision-making. I fused outputs from NASA's Land Information System (LIS) land surface model with MODIS and VIIRS remote sensing observations to produce a 20-year (2000-2020), daily, 0.01° resolution SWE dataset covering all of North America. The pipeline runs on OSU's HPC cluster in Julia and Python, processing roughly 30 TB of input data into a reproducible, publication-quality data product.

### Deep Learning for Water Body Classification
Sub-meter detection of river surface water from satellite imagery requires models that go well beyond standard thresholding approaches. I contributed the remote-sensing data engineering and workflow-integration layers for PyTorch-based water classification research, working alongside deep-learning model architects. My work centered on satellite-data acquisition (Sentinel-2, Maxar/WorldView), preprocessing, ArcticDEM-derived 3D context extraction, model-output integration, and downstream hydrology pipeline operationalization. The collaboration produced two peer-reviewed publications.

### ICESat-2 Processing Toolkit
Processing ICESat-2 laser altimetry data across Antarctica and the Arctic involves correcting systematic vertical biases against reference DEMs (ArcticDEM, REMA, WorldDEM) at continental scale. I built an open-source Python toolkit that automated what had been weeks-long manual processing workflows into a reproducible pipeline, presented at NASA Goddard and adopted by collaborators across the cryosphere community.

---

## Experience

| Role | Organization | Years |
|------|-------------|-------|
| Research Associate (GIS/Remote Sensing) | The Ohio State University, Byrd Polar and Climate Research Center | 2019 – Present |
| Graduate Research Assistant | University of Florida, Civil Engineering | 2010 – 2019 |
| Research Assistant | National Center for Airborne Laser Mapping (NCALM), UF | 2006 – 2009 |

---

## Education

| Degree | Institution | Year |
|--------|------------|------|
| PhD, Civil Engineering | University of Florida | 2018 |
| MS, Civil Engineering (Geosensing Systems Engineering) | University of Florida | 2009 |
| MSc, Geo-Information Science | Wageningen University, Netherlands | 2004 |
| BSc, Environmental Science | Kathmandu University, Nepal | 2001 |

---

## Peer-Reviewed Publications

1. Shutkin, T.Y. et al. (2025). Modeling the impacts of climate trends and lake formation on the retreat of a tropical Andean glacier (1962-2020). *The Cryosphere*, 19, 4835–4853.
2. Andreadis, K.M. et al. (2025). A first look at river discharge estimation from SWOT satellite observations. *Geophysical Research Letters*, 52, e2024GL114185.
3. Durand, M., Dai, C., Moortgat, J., **Yadav, B.** et al. (2024). Using river hypsometry to improve remote sensing of river discharge. *Remote Sensing of Environment*, 315, 114455.
4. Ziwei, L., Leong, W.J., Durand, M., Howat, I., Wadkowski, K., **Yadav, B.**, Moortgat, J. (2023). Super-resolution deep neural networks for water classification from free multispectral satellite imagery. *Journal of Hydrology*, 626, 130248.
5. Moortgat, J., Ziwei, L., Durand, M., Howat, I., **Yadav, B.** (2022). Deep learning models for river classification at sub-meter resolutions from multispectral and panchromatic commercial satellite imagery. *Remote Sensing of Environment*, 282, 113279.
6. Chudley, T.R., Howat, I.M., **Yadav, B.**, and Noh, M.J. (2022). Empirical correction of systematic orthorectification error in Sentinel-2 velocity fields for Greenlandic outlet glaciers. *The Cryosphere*, 16, 2629–2642.
7. **Yadav, B.** and Hatfield, K. (2018). Stream network conflation with topographic DEMs. *Environmental Modelling & Software*, 102, 241–249.

---

## Research Funding

| Grant | Agency | Role | Period | Amount |
|-------|--------|------|--------|--------|
| Adopting SWOT measurements to improve decision making for currently ungauged basins: Decision support for Alaska | NASA | Co-Investigator | 2022–2024 | $925,353 |
| The Permafrost Discovery Gateway: Navigating the New Arctic through Big Imagery, AI, and cyberinfrastructure | NSF | Collaborator | 2019–2024 | $106,230 |

---

## Service

- Proposal reviewer, NASA ROSES grants
- Manuscript reviewer: *International Journal of Digital Earth*, *Journal of Mountain Science*, NSF EarthCube Notebooks
- OSU Geospatial Steering Committee
