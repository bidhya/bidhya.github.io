# AI & Machine Learning Engineering Notes

In-depth engineering references covering the full ML development stack: from statistical foundations through large-scale distributed training and transformer architectures, to production fine-tuning strategies for geospatial foundation models.

The articles follow a deliberate learning arc — building from mathematical fundamentals through architectural deep-dives to the practical challenges of adapting foundation models to domain-specific targets.

---

## Foundations

<div class="grid cards" markdown>

-   :material-function-variant: **[From Statistics to Deep Learning](stats-to-deep-learning.md)**

    The conceptual bridge from classical statistics to neural network optimization — written for domain scientists transitioning from probabilistic modelling to deep learning.

-   :material-scale-balance: **[Bias–Variance Tradeoff & Regularization](bias-variance.md)**

    The central tension between model simplicity and flexibility: overfitting, underfitting, and the strategies (regularization, cross-validation, ensembles) that keep models generalizable.

-   :material-fire: **[PyTorch Training Fundamentals](pytorch-foundations.md)**

    Deep learning mechanics from first principles: tensors, gradient descent, training loops, and production model architectures in PyTorch.

</div>

## Architectures

<div class="grid cards" markdown>

-   :material-code-brackets: **[Transformer Architecture & Attention Mechanics](transformers.md)**

    Inside self-attention, multi-head attention, key-query-value dimensions, positional encodings, and the structural foundations of large language and vision models.

-   :material-text-box: **[Tokenization & Embeddings](tokenization-embeddings.md)**

    How raw text and spatial signals are encoded into dense vector representations: BPE, SentencePiece, and geospatial embedding strategies.

-   :material-memory: **[LLM Inference & KV-Cache Engineering](qkv-kvcache.md)**

    Engineering lifecycle of transformer inference: embedding dimensions, QKV projection math, multi-head attention mechanics, and GPU memory footprint of the KV-cache at scale.

-   :material-thermometer: **[Temperature, Sampling & Reasoning Models](llm-temperature.md)**

    How temperature controls token entropy via the Boltzmann distribution, the difference between standard and reasoning models, and how MCTS-based models like Kimi K2.6 use high entropy productively.

</div>

## Scale & Infrastructure

<div class="grid cards" markdown>

-   :material-server: **[GPU Memory & Distributed Training](gpu-ddp.md)**

    Single-GPU optimization, multi-GPU systems, Distributed Data Parallel (DDP) configuration, and SLURM HPC integration for deep learning workloads.

-   :material-lan-connect: **[Multi-Node Parallelization with Joblib and Dask](multi-node-parallelization.md)**

    Scaling Python workloads from a laptop to a single HPC node to a true multi-node cluster: shared vs. distributed memory, task decomposition, and the network/serialization bottlenecks that separate the two.

</div>

## Adaptation & Fine-Tuning

<div class="grid cards" markdown>

-   :material-tune: **[Model Adaptation & Fine-Tuning](fine-tuning.md)**

    Full fine-tuning vs. linear probing vs. feature extraction — when to use each strategy and the computational trade-offs involved.

-   :material-earth: **[PEFT for Geospatial Foundation Models](geospatial-peft.md)**

    Parameter-Efficient Fine-Tuning (LoRA) applied to geospatial vision transformers (Prithvi, Clay) for hydrological and cryospheric classification.

</div>

## Computer Vision

<div class="grid cards" markdown>

-   :material-image-multiple: **[Vision Transformer Architecture](vision-transformer.md)**

    How ViT adapts the Transformer to image understanding: patch tokenization, positional encodings, and the conceptual shift from CNNs to attention-based vision models.

-   :material-chart-bar: **[ViT Data Requirements & Inductive Bias](vit-data-requirements.md)**

    Why Vision Transformers are more data-hungry than CNNs — the role of inductive bias, what CNNs encode by design vs. what ViTs must learn from data, and implications for transfer learning.

</div>
