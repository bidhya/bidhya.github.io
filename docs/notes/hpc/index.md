# HPC & Infrastructure Engineering Notes

Engineering references for the layer beneath the science: distributed execution across
cluster nodes, self-hosted model inference on institutional GPUs, and the environment
configuration that makes any of it reproducible.

Most machine-learning material assumes a laptop or a managed cloud runtime. These notes
cover what changes when the compute is a shared scheduler-managed cluster, where you do
not have root, storage is shared with hundreds of other users, and the compute nodes may
have no route to the internet at all.

---

## Distributed Execution

<div class="grid cards" markdown>

-   :material-lan-connect: **[Multi-Node Parallelization](multi-node-parallelization.md)**

    Scaling Python workloads with Joblib and Dask from a laptop to a single HPC node to a true multi-node cluster: shared vs. distributed memory, task decomposition, and the network/serialization bottlenecks that separate the two.

</div>

## On-Premise Model Serving

<div class="grid cards" markdown>

-   :material-shield-lock: **[Ollama on HPC](on-prem-ai-assistant.md)**

    Hosting Ollama on HPC (H200 GPUs) and tunneling it into VS Code Copilot Chat via BYOK — keeping prompts and institutional data off third-party cloud infrastructure entirely, for research collaborations bound by data governance agreements.

-   :material-server-network: **[vLLM on HPC](vllm-hpc-setup.md)**

    Why vLLM is a compiled CUDA inference engine, not a Python package — matching driver, toolkit, PyTorch, and wheel versions exactly, diagnosing manylinux/glibc and JIT-compilation failures, and a working `uv`-managed `pyproject.toml` for CUDA 12.9 / H200.

</div>

## Environment & Configuration

<div class="grid cards" markdown>

-   :material-console: **[Linux Shell Setup](linux-shell-setup.md)**

    Separating environment configuration from interactive shell behavior (`.bash_profile` vs. `.bashrc`), keeping caches and secrets out of the home directory, and a reproducible pattern for HPC accounts, workstations, WSL, and cloud VMs.

</div>
