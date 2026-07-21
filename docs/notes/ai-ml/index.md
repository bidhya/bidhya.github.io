# AI & Machine Learning Engineering Notes

In-depth engineering references covering the full ML development stack: from statistical foundations through large-scale distributed training and transformer architectures, to production fine-tuning strategies for geospatial foundation models.

The articles follow a deliberate learning arc — building from mathematical fundamentals through architectural deep-dives to the practical challenges of adapting foundation models to domain-specific targets.

---

## Foundations

<div class="grid cards" markdown>

-   :material-function-variant: **[Statistics to Deep Learning](stats-to-deep-learning.md)**

    The conceptual bridge from classical statistics to neural network optimization — written for domain scientists transitioning from probabilistic modelling to deep learning.

-   :material-scale-balance: **[Bias–Variance](bias-variance.md)**

    The central tension between model simplicity and flexibility: overfitting, underfitting, and the strategies (regularization, cross-validation, ensembles) that keep models generalizable.

-   :material-target: **[Precision-Recall](precision-recall.md)**

    Building intuition for the confusion matrix from first principles, bridging ML vocabulary (false positive/negative) with remote-sensing accuracy assessment (omission/commission error, producer's/user's accuracy).

-   :material-fire: **[PyTorch Fundamentals](pytorch-foundations.md)**

    Deep learning mechanics from first principles: tensors, gradient descent, training loops, and production model architectures in PyTorch.

</div>

## Architectures

<div class="grid cards" markdown>

-   :material-code-brackets: **[Transformers & Attention](transformers.md)**

    Inside self-attention, multi-head attention, key-query-value dimensions, positional encodings, and the structural foundations of large language and vision models.

-   :material-text-box: **[Tokenization & Embeddings](tokenization-embeddings.md)**

    How raw text and spatial signals are encoded into dense vector representations: BPE, SentencePiece, and geospatial embedding strategies.

-   :material-vector-line: **[Embeddings Across Domains](embeddings.md)**

    How a single vector representation and one formula (cosine similarity) make satellite pixels, biomedical records, and crop stress directly comparable — from geospatial foundation models (Prithvi, Clay, AlphaEarth, OlmoEarth) to the same pattern showing up far outside Earth science.

-   :material-memory: **[LLM Inference & KV-Cache](qkv-kvcache.md)**

    Engineering lifecycle of transformer inference: embedding dimensions, QKV projection math, multi-head attention mechanics, and GPU memory footprint of the KV-cache at scale.

-   :material-thermometer: **[Temperature & Sampling](llm-temperature.md)**

    How temperature controls token entropy via the Boltzmann distribution, the difference between standard and reasoning models, and how MCTS-based models like Kimi K2.6 use high entropy productively.

</div>

## Scale & Infrastructure

<div class="grid cards" markdown>

-   :material-server: **[GPU & Distributed Training](gpu-ddp.md)**

    GPU memory management, single- and multi-GPU optimization, Distributed Data Parallel (DDP) configuration, and SLURM HPC integration for deep learning workloads.

-   :material-lan-connect: **[Multi-Node Parallelization](multi-node-parallelization.md)**

    Scaling Python workloads with Joblib and Dask from a laptop to a single HPC node to a true multi-node cluster: shared vs. distributed memory, task decomposition, and the network/serialization bottlenecks that separate the two.

-   :material-shield-lock: **[Ollama on HPC](on-prem-ai-assistant.md)**

    Hosting Ollama on HPC (H200 GPUs) and tunneling it into VS Code Copilot Chat via BYOK — keeping prompts and institutional data off third-party cloud infrastructure entirely, for research collaborations bound by data governance agreements.

-   :material-server-network: **[vLLM on HPC](vllm-hpc-setup.md)**

    Why vLLM is a compiled CUDA inference engine, not a Python package — matching driver, toolkit, PyTorch, and wheel versions exactly, diagnosing manylinux/glibc and JIT-compilation failures, and a working `uv`-managed `pyproject.toml` for CUDA 12.9 / H200.

-   :material-console: **[Linux Shell Setup](linux-shell-setup.md)**

    Separating environment configuration from interactive shell behavior (`.bash_profile` vs. `.bashrc`), keeping caches and secrets out of the home directory, and a reproducible pattern for HPC accounts, workstations, WSL, and cloud VMs.

</div>

## Adaptation & Fine-Tuning

<div class="grid cards" markdown>

-   :material-tune: **[Fine-Tuning](fine-tuning.md)**

    Full fine-tuning vs. linear probing vs. feature extraction — when to use each strategy and the computational trade-offs involved.

-   :material-earth: **[Geospatial PEFT](geospatial-peft.md)**

    Parameter-Efficient Fine-Tuning (LoRA) applied to geospatial vision transformers (Prithvi, Clay) for hydrological and cryospheric classification.

</div>

## Computer Vision

<div class="grid cards" markdown>

-   :material-image-multiple: **[Vision Transformers](vision-transformer.md)**

    How ViT adapts the Transformer to image understanding: patch tokenization, positional encodings, and the conceptual shift from CNNs to attention-based vision models.

-   :material-chart-bar: **[ViT Data Requirements](vit-data-requirements.md)**

    Why Vision Transformers are more data-hungry than CNNs — the role of inductive bias, what CNNs encode by design vs. what ViTs must learn from data, and implications for transfer learning.

</div>
