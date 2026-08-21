# Workflows

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

## Running These Notebooks

The raw `.ipynb` source for every workflow lives in the site repository, under
[`docs/tutorials/`](https://github.com/bidhya/bidhya.github.io/tree/main/docs/tutorials){target="_blank"}.
Download a single notebook from there, or clone the lot:

```bash
git clone https://github.com/bidhya/bidhya.github.io.git
cd bidhya.github.io/docs/tutorials
```

The `pixi` environment in this repository builds the site; it does not install Jupyter or
the scientific stack each notebook needs. Run them under your own environment, installing
the imports each notebook declares in its first cell.
