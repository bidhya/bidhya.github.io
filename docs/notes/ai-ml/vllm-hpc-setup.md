---
tags:
  - HPC
  - vLLM
  - LLM
  - CUDA
  - GPU
---

# Installing vLLM on HPC: A CUDA 12.9 / H200 Case Study

## What vLLM is, and why it's harder to install than it looks

vLLM is a high-throughput inference *server* for large language models. Its defining feature is **PagedAttention**, a memory-management scheme for the attention KV-cache that lets the engine batch many concurrent requests against one loaded model far more efficiently than naive serving. It also exposes an OpenAI-compatible HTTP API, so any application written against OpenAI's client library can point at a self-hosted vLLM endpoint with nothing more than a URL change.

For contrast: tools like Ollama optimize for simplicity — a single binary, `ollama pull`, one interactive session. vLLM optimizes for throughput under concurrent load — many requests, one model, maximum GPU utilization. The tradeoff is installation complexity, and understanding *why* that complexity exists is the difference between fighting it blindly and reasoning through it.

**The core fact to internalize: vLLM is not a Python package. It is a C++/CUDA inference engine — custom attention kernels, FlashInfer, CUTLASS, Triton-JIT'd ops — wrapped in a thin Python interface.** A `pip install vllm` doesn't just fetch Python source; it fetches (or in some cases builds) compiled binaries that must match your system's CUDA runtime version, its CUDA compiler toolchain, and its OS glibc baseline, exactly. This is fundamentally different from installing something like `requests` or `pandas`, and treating it as an ordinary pip package is where nearly every installation problem originates.

Three things have to line up for a vLLM install to work at all:

| Axis | What it constrains | Where it shows up |
|---|---|---|
| **CUDA runtime version** | The version PyTorch and vLLM's compiled kernels were built against | `libcudart.so.X` load errors at import time |
| **CUDA compiler toolchain** | What's available on the system for *runtime* JIT compilation (FlashInfer, Triton) | Kernel build failures the first time a specific op is exercised, sometimes minutes after the process starts |
| **glibc / manylinux baseline** | Whether a given wheel can even be loaded on your OS at all | Install-time `uv`/`pip` platform-compatibility rejections |

*Reference setup: NVIDIA H200 GPU, HPC cluster CUDA toolkit capped at 12.9 (`module load cuda/12.9.0-vvrwkrx`), OS baseline `manylinux_2_28` (glibc 2.28), managed with `uv`. vLLM version: v0.22.1. Verified July 2026.*

---

## Part 1: The CUDA-version trap

Since vLLM v0.20.0, the **default PyPI wheel targets CUDA 13**, not CUDA 12.x. Any HPC cluster running an older CUDA module — common, since institutional toolkits lag consumer releases by a year or more — will fail immediately on a bare `pip install vllm` or `vllm>=X` dependency, with an error like `libcudart.so.13: cannot open shared object file`.

The instinctive fix — force PyTorch to a CUDA-13 build to match — creates a *second*, more subtle problem: vLLM's FlashInfer/Triton backend JIT-compiles custom kernels at runtime using whatever `nvcc` is on the system `PATH`. If that `nvcc` is version 12.9 (because that's what the cluster's module system provides) while PyTorch's runtime is 13.0, you get a compiler/runtime mismatch that crashes with errors like `tvm_ffi` failures — deep in kernel compilation, not in Python.

**The rule this teaches: every layer — driver/toolkit, PyTorch, and vLLM's own compiled wheel — must target the same CUDA major.minor version.** On a CUDA-12.9 cluster, that means CUDA-12.9 builds of PyTorch *and* vLLM, full stop. Don't split the difference.

## Part 2: The manylinux trap

Even after solving the CUDA version, a specific vLLM release wheel might still refuse to install — not because of CUDA, but because of the **manylinux tag** in the wheel filename (e.g. `manylinux_2_28` vs `manylinux_2_34`). This tag encodes the minimum glibc version the wheel was built against. Installing a `manylinux_2_34` wheel on a `manylinux_2_28` system (older glibc) fails at the package-manager level, before any Python code even runs.

**Lesson:** always check a wheel's manylinux tag against your cluster's glibc version (`ldd --version`) before pinning a specific release URL. Don't assume the newest-looking wheel is compatible — HPC systems frequently run OS baselines several years behind consumer Linux.

## Part 3: The project-naming trap (uv-specific)

Package resolvers (via PEP 503) normalize names case- and hyphen-insensitively. If your `pyproject.toml` project itself is named `vLLM`, `uv` will treat your *own project* as already satisfying the `vllm` dependency and silently skip installing the real package. **Never name a project the same as a dependency you need actually installed** — use something distinct like `vLLM-sandbox`.

## Part 4: Deprecated environment variables

`VLLM_ATTENTION_BACKEND` was removed from recent vLLM releases in favor of a CLI/config argument, `--attention-config.backend`. Setting the old variable produces a harmless `Unknown vLLM environment variable detected` warning and does nothing — vLLM will auto-select a working backend (commonly `FLASH_ATTN`) regardless. If you need to force a specific backend deliberately, use the current flag, not the old env var.

---

## The working `pyproject.toml`

```toml
[project]
name = "vLLM-sandbox"   # not "vLLM" — see Part 3
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = [
    "ipykernel>=7.3.0",
    "torch",
    "torchaudio",
    "torchvision",
    "vllm",
]

[tool.uv.sources]
torch = { index = "pytorch-cu129" }
torchaudio = { index = "pytorch-cu129" }
torchvision = { index = "pytorch-cu129" }

# Pin to the official CUDA-12.9 release wheel (manylinux_2_28 baseline).
# Bump the version tag as newer vLLM releases come out.
vllm = { url = "https://github.com/vllm-project/vllm/releases/download/v0.22.1/vllm-0.22.1+cu129-cp38-abi3-manylinux_2_28_x86_64.whl" }

[[tool.uv.index]]
name = "pytorch-cu129"
url = "https://download.pytorch.org/whl/cu129"
explicit = true
```

Install with a clean slate:
```bash
rm -rf .venv uv.lock
uv sync
```
Since every dependency here resolves to a precompiled wheel, `uv sync` only downloads binaries — it never invokes `nvcc`. This means the CUDA toolkit module does not need to be loaded for installation, only for execution (next section).

## The Slurm launch script

```bash
#!/usr/bin/env bash
#SBATCH --time=02:00:00
#SBATCH --exclusive
#SBATCH --gres=gpu:1
#SBATCH --partition=batch-gpu-new

# Loading the CUDA toolkit module here is what makes FlashInfer/Triton's
# runtime JIT compilation possible. Skip this, and the job will still get
# through model loading and torch.compile successfully — the failure only
# surfaces on the *first inference call*, when a kernel needs to be built
# on the fly and `nvcc` isn't on PATH. This delayed failure point is what
# makes people mistakenly believe the toolkit module is unnecessary.
module load cuda/12.9.0-vvrwkrx

cd /path/to/your/project
uv run python your_inference_script.py
```

Two lines that are commonly added out of caution turn out to be unnecessary and can be dropped:
- `export CUDA_HOME=...` — on Spack-based module systems, `module load` already exports `CUDA_HOME` as part of loading the module. Check with `echo $CUDA_HOME` right after loading before adding this manually.
- `export VLLM_ATTENTION_BACKEND=...` — dead variable, see Part 4.

## Validating the setup

The fastest way to validate a new environment is to run inference against the smallest model you can, such as `facebook/opt-125m` (a ~125M parameter model that loads and runs in seconds). This isolates *toolchain* correctness — CUDA versions, compiler availability, wheel compatibility — from *model-specific* concerns like memory sizing or quantization, which only matter once the underlying environment is already proven sound.

A minimal script for this:
```python
from vllm import LLM

llm = LLM(model="facebook/opt-125m")
output = llm.generate(["The future of AI is"])
print(output[0].outputs[0].text)
```

If this runs cleanly end-to-end — model load, `torch.compile`, CUDA graph capture, and a generated completion — the environment is sound, and you can move to a production-scale model with confidence that any further issues are model-specific rather than toolchain-related.

---

## Where to go from here

This baseline covers single-GPU inference on a small model, which is sufficient to prove out the environment. Building toward a real deployment involves:
- Swapping in the target model family (Llama, Qwen, etc.)
- Serving via `vllm serve` for the OpenAI-compatible HTTP endpoint, rather than the one-off Python API
- Tuning `--gpu-memory-utilization` and `--tensor-parallel-size` for realistic concurrency and multi-GPU scaling
- Production concerns: auth, logging, and restart behavior under the scheduler

## Summary of failure modes and their root causes

| Symptom | Root cause | Fix |
|---|---|---|
| `libcudart.so.13` not found | PyPI's default wheel targets CUDA 13 | Pin torch + vLLM to matching CUDA 12.x builds |
| `tvm_ffi` crash / kernel build failure | CUDA runtime and compiler toolchain versions mismatched | Keep driver, toolkit, PyTorch, and vLLM on the same CUDA major.minor |
| Wheel install rejected by platform check | manylinux tag doesn't match cluster's glibc | Check `ldd --version`; match the wheel's manylinux tag accordingly |
| `vllm` silently not installed | Project itself named `vLLM`, colliding with the dependency name | Use a distinct project name |
| `Unknown vLLM environment variable` warning | `VLLM_ATTENTION_BACKEND` deprecated | Use `--attention-config.backend` if forcing a backend |
| `ninja`/`nvcc: No such file or directory`, but only on first inference call | CUDA toolkit module not loaded before runtime JIT compilation kicks in | `module load` the toolkit in the launch script, not just at install time |
