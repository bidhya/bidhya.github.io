# Technical Workflows & Jupyter Notebooks

End-to-end computational workflows implemented as fully-documented Jupyter notebooks — covering real satellite and scientific text datasets from raw acquisition through validated final outputs.

---

## :material-satellite: Satellite Remote Sensing

<div class="grid cards" markdown>

-   **[NASA PACE Ocean Color Analysis](ocean-color.ipynb)**

    Atmospheric correction and spectral analysis of PACE OCI hyperspectral data targeting phytoplankton community classification and ocean colour retrieval from continuous-band sensor measurements.

-   **[Sentinel-2 Change Detection](change-detection.ipynb)**

    Preprocessing, spectral index computation, and classification applied to Sentinel-2 time-series imagery for land cover change detection mapping.

</div>

## :material-text-search: Applied NLP for Scientific Text

<div class="grid cards" markdown>

-   **[Named Entity Recognition](nlp-ner.ipynb)**

    Transformer pipelines for extracting domain entities, geographic markers, and scientific terminology from unstructured research text.

-   **[Topic Modeling & Semantic Structuring](nlp-topic-modeling.ipynb)**

    Organising unstructured scientific abstracts into latent thematic clusters using LDA and neural topic models.

-   **[Zero-Shot Document Classification](nlp-sentiment-analysis.ipynb)**

    Pre-trained language models for zero-shot tagging and classification of research documents on arbitrary criteria without task-specific fine-tuning.

</div>

---

## Running Notebooks Locally

All tutorials are managed through the `pixi` environment for full reproducibility:

```bash
git clone https://github.com/bidhya/bidhya.github.io.git
cd bidhya.github.io
pixi run jupyter notebook
```
