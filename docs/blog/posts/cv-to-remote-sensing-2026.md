---
date: 2026-10-17
slug: cv-to-remote-sensing-2026
authors:
  - bidhya
categories:
  - Geospatial & Remote Sensing
tags:
  - AI & Machine Learning
  - Geospatial & Remote Sensing
  - Computer Vision
  - Remote Sensing
  - Foundation Models
  - Transformers
---

# From Computer Vision to Remote Sensing: A 2026 Model Landscape

*A concise map of tasks, architectures, and models — and how the CV world's ideas carry over (and don't) to remote sensing. Written as a jumping-off point for deeper research, not a tutorial.*

*A snapshot of the 2026 landscape. Model names in this space turn over within a year; the structural arguments (band mismatch, label scarcity, why U-Net persists) should outlast them.*

Most computer-vision advice assumes a three-band photograph. Satellite imagery rarely is one: Sentinel-2 records 13 bands, SAR has no optical channel at all, and hyperspectral sensors record hundreds. That single mismatch explains most of where remote sensing follows mainstream CV and where it quietly goes its own way.

This post maps the two worlds side by side: the core CV tasks and their go-to models, why the standard pipeline breaks on satellite data, why a 2015 architecture is still the remote-sensing default, and where geospatial foundation models and precomputed embeddings now fit.

<!-- more -->

---

## 1. Two architectural eras in CV

- **CNNs** (2012–2020): convolution kernels slide over the image, building features hierarchically (edges → parts → objects). Lineage: LeNet → AlexNet → ResNet → DenseNet → ConvNeXt (a modernized CNN).
- **Vision Transformers** (2020–now): image split into patches, treated like tokens, processed with self-attention — global receptive field from layer one, no built-in locality assumption. Lineage: ViT → Swin Transformer (windowed attention) → hybrids like CoAtNet (conv + attention).

**Trade-off:** CNNs are more data-efficient at small scale; ViTs need more data/compute but scale further and now lead most benchmarks. This tension is exactly why remote sensing — often label-scarce — still leans heavily on CNN-based U-Nets even in a transformer-dominated field.

---

## 2. Core CV tasks and go-to models

| Task | Go-to model(s) | Notes |
|---|---|---|
| Classification | ViT, ConvNeXt | `google/vit-base-patch16-224` |
| Object detection (simple) | DETR | CNN backbone + transformer, no anchors/NMS |
| Object detection (SOTA) | RT-DETR, RF-DETR | RF-DETR: DINOv2 backbone, real-time, >60 AP on COCO |
| Object detection (fast/edge) | YOLO family (YOLO26) | NMS-free, end-to-end, unified across detection/seg/pose |
| Semantic segmentation | Mask2Former, SegFormer | pixel → class, no instance separation |
| Instance segmentation | Mask2Former, Mask R-CNN | separates individual object instances |
| Panoptic segmentation | Mask2Former | unifies "things" (countable) + "stuff" (background) |
| Zero-shot segmentation | SAM / SAM 2 / SAM 3 | promptable via point, box, or text/concept |
| Open-vocabulary detection | Grounding DINO | detect via text prompt, no fixed class list |
| Vision + language | CLIP, Florence-2 | CLIP: joint image/text embeddings · Florence-2: captioning, grounding, OCR |

---

## 3. Why remote sensing (RS) breaks the standard pipeline

Almost every model above expects **3-channel RGB** — baked into the patch/conv input layer from ImageNet pretraining. RS imagery usually isn't 3-band:

- Sentinel-2: 13 bands · Landsat: 11 bands · Sentinel-1 SAR: 2 polarizations, no optical · Hyperspectral: hundreds of narrow bands

Three ways models handle this:
1. Retrain the input layer for N channels, keep the rest of a pretrained backbone
2. Reduce to pseudo-RGB (band selection / PCA) — simplest, loses information
3. Use an architecture built for variable bands from the start (see §5)

---

## 4. U-Net — the RS workhorse (deliberately not "trendy")

CNN encoder-decoder with **skip connections** passing fine spatial detail straight from encoder to decoder — important in RS because targets are often thin/precise (roads, field boundaries, coastlines). Originally for medical imaging; transfers directly.

Why it dominates RS in practice over transformer-based SOTA models:
- Input layer trivially adapts to N-band input (unlike transformer patch embeddings tied to RGB pretraining)
- Trains from scratch on modest labeled datasets — RS is usually label-scarce, transformers are usually data-hungry
- Variants: **U-Net++** (denser skip connections), **Attention U-Net** (attention gates on the skip connections suppress irrelevant regions), **ResU-Net**

Go-to for: land cover classification, deforestation/change detection, flood/water mapping, crop segmentation, building footprints.

---

## 5. RS task → model map

| Task | Standard CV analogue | RS go-to |
|---|---|---|
| Classification | ViT / ConvNeXt | U-Net encoder or ViT w/ modified stem; or a geospatial FM (§6) |
| Semantic segmentation | Mask2Former / SegFormer | **U-Net / U-Net++ / Attention U-Net** |
| Change detection | *(no direct CV equivalent)* | Siamese U-Net (shared-weight dual encoder) |
| Object detection | YOLO / RT-DETR | Same families, retrained; often with **oriented bounding boxes** (overhead view) |
| Instance/panoptic segmentation | Mask2Former | Less common; U-Net + postprocessing usually preferred |

---

## 6. Geospatial foundation models (GFMs)

Pretrained once on large unlabeled satellite archives, fine-tuned per task with fewer labels — the RS equivalent of CLIP/DINOv2 as a reusable backbone.

| Model | Origin | Distinguishing idea |
|---|---|---|
| **Prithvi-EO-2.0** | NASA/IBM | ViT + masked-autoencoder; 3D patch embeddings for multi-date stacks; 6 HLS bands |
| **Clay** | Clay Foundation | "Dynamic embedding block" conditions patch tokens on each band's wavelength — one model, any sensor's band set |
| **SatMAE / Scale-MAE** | Academic | Early MAE adaptations to satellite imagery; spectral-grouped patch embeddings |
| **DOFA** | Academic | Multimodal pretraining across sensor types (optical + SAR) |
| **TerraMind** | IBM/ESA | Newer multimodal GFM |

**Tooling:** `TorchGeo` (RS datasets/dataloaders) + `TerraTorch` (fine-tuning toolkit bundling Prithvi, Clay, SatMAE, DOFA, ScaleMAE under one API) — the practical entry point instead of hand-rolling band-adaptation logic.

---

## 7. Embeddings — the connective layer

An embedding is a fixed-length vector summarizing an image/patch/pixel such that similar content lands nearby in vector space. It decouples "understanding the image" (expensive, done once) from "using that understanding" (cheap, repeatable) — nearest-neighbor search, clustering, linear probes, or small downstream classifiers instead of full retraining.

**This is not a separate category from §2/§6 — it's the upstream half of nearly every model listed there.** DETR's detection head, Mask2Former's mask decoder, a U-Net decoder — all are thin task-specific layers on top of an embedding.

### CV-world embeddings
- **CLIP** — joint image/text embeddings; backbone of reverse-image-search and zero-shot classification
- **DINOv2** — self-supervised ViT embeddings; e.g. RF-DETR's backbone
- **ViT [CLS] token** — the basis of standard classification heads

### RS-world embeddings — two distinct flavors

**(a) Model-as-backbone** (same pattern as CLIP/DINOv2): run imagery through Prithvi/Clay/SatMAE yourself → get patch embeddings → fine-tune a small head (often U-Net-style) on top.

**(b) Precomputed, imagery-free embeddings** (no real CV equivalent): **AlphaEarth Foundations** (Google DeepMind) publishes ready-made 64-dimensional embeddings for every 10m pixel on Earth, annually since 2017, fusing optical + radar + LiDAR + climate + elevation. Pixel-level (not patch-level) — well suited to dense prediction. No GPU or raw imagery needed: pull the vector from Google Earth Engine/BigQuery and feed a plain classifier (random forest, small MLP) or compute cosine similarity across years for change detection.

No CV parallel exists for (b) because "the same 10m patch of Earth, imaged repeatedly over years" is a bounded, indexable space in a way that arbitrary photos aren't.

| Goal | Approach |
|---|---|
| Fine-tune for a labeled task, moderate data | Prithvi/Clay via TerraTorch |
| Very little labeled data, no GPU | AlphaEarth embeddings + classical ML |
| Pixel-precise segmentation | GFM embeddings → U-Net-style decoder |
| Change detection over time | AlphaEarth: cosine similarity, same pixel across years |
| Data locality / on-prem requirement | Prithvi or Clay (downloadable weights) — AlphaEarth is currently Earth Engine/BigQuery-only |

---

## 8. Starting points for deeper research

- **Architecture lineage:** ViT paper → Swin → CoAtNet → DETR → Mask2Former → SAM/SAM2/SAM3
- **RS foundation models:** `torchgeo/terratorch` on GitHub (bundles Prithvi, Clay, SatMAE, DOFA, ScaleMAE) · `Jack-bo1220/Awesome-Remote-Sensing-Foundation-Models` (curated, actively updated survey list)
- **Embeddings in RS:** AlphaEarth Foundations paper (Brown et al., 2025) · GEO-Bench (standard eval suite for GFMs)
- **Band-adaptation techniques:** search "channel-adaptive foundation model remote sensing" for methods beyond Clay's dynamic embedding block (e.g. HyperFree for hyperspectral)

**Related notes on this site:** [Vision Transformers](../../notes/ai-ml/vision-transformer.md) · [Why ViTs Need More Data](../../notes/ai-ml/vit-data-requirements.md) · [Embeddings](../../notes/ai-ml/embeddings.md) · [Parameter-Efficient Fine-Tuning for Geospatial Models](../../notes/geospatial/geospatial-peft.md)
