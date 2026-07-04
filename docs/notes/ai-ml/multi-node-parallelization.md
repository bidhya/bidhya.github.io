---
tags:
  - HPC
  - Dask
  - Joblib
  - Parallel Computing
  - SLURM
  - Distributed Computing
---

# Multi-Node Parallelization: Joblib and Dask on SLURM

A recurring decision point in scaling Python workloads on HPC systems: a parallel job needs more cores than one node provides, and the code should scale from a laptop prototype to a single-node run to a true multi-node cluster without rewriting the parallel logic at each stage. The most common source of confusion is treating "more cores" and "more nodes" as the same request. They are not, and the distinction comes down to memory.

## 1. Cores, Memory, and Where Parallelism Lives

- **A core** is a physical execution unit inside one node.
- **Shared memory** (within a node): every core on that node reads and writes the same physical RAM directly over the local memory bus. No serialization, no network — this is why single-node parallelism is fast and simple.
- **Distributed memory** (across nodes): each node has its own separate RAM. Nothing is shared. Moving data from one node to another means serializing it and sending it over the network (Ethernet or InfiniBand), which is orders of magnitude slower than a memory access.

This single fact explains most of the confusion around scaling: requesting more cores (`--cpus-per-task`) only works up to the number of cores physically present on **one** node. Ask for more than that on a single task, and Slurm either rejects the submission outright or leaves the job `Pending` indefinitely with reason `ReqNodeNotAvail` — a single Slurm task cannot span physical node boundaries. Scaling past one node requires a different mechanism entirely (Section 4), not a bigger `--cpus-per-task` value.

## 2. Task Decomposition Happens First

Before writing any Slurm script, the workload has to be broken into independent units — per-tile raster reprojection, per-basin hydrology run, per-fold cross-validation, per-hyperparameter-combination fit. This decomposition, done early in the workflow, determines everything downstream:

- If (number of units × per-unit cost) fits inside one node's core count and memory, **stay single-node**. Simpler, no network overhead, easiest to debug.
- If it doesn't — too many units, or each unit needs more memory/cores than one node provides — the workload needs to span multiple nodes, and now a distributed scheduler has to manage the network communication between processes.

In practice, most workloads decompose cleanly enough to stay single-node. Multi-node is the exception, reserved for genuinely large batch runs.

## 3. Single-Node Parallelism: Joblib, Shared Memory

This is the default case, and where every job should start. Joblib's default backends (`loky`, `multiprocessing`) are shared-memory parallelism — they fork worker processes on the same physical machine and require no distributed framework, no network, no cluster setup.

**Slurm allocation for single-node Joblib:**
```bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
```

**Common pitfall**: `joblib`'s `n_jobs=-1` uses all CPU cores visible to the *current task allocation*, not the full node. If `--cpus-per-task` is not set explicitly, `n_jobs=-1` sees only the default (often 1) core, silently under-utilizing the allocation. The fix is to read the Slurm environment variable directly rather than assuming `-1` detects the right core count:

```python
import os
from joblib import Parallel, delayed

n_cores = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))
results = Parallel(n_jobs=n_cores)(delayed(heavy_computation)(i) for i in inputs)
```

## 4. Multi-Node Parallelism: Dask as the Distributed-Memory Backend

Once the task count or per-task memory genuinely exceeds one node, Dask becomes the distributed backend for Joblib, sending tasks across the network to workers running on other physical nodes — without changing the `Parallel(delayed(...))` call sites in the code.

### The "Manager" Slurm Script
The main script (the "Manager") runs on a small, lightweight allocation, and it then requests separate "Worker" jobs from the scheduler — each worker job lands on its own physical node.

```bash
#!/bin/bash
#SBATCH --job-name=dask_manager
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=02:00:00
#SBATCH --output=manager_%j.log

# Load your environment (Conda or Apptainer)
module load python/3.13
source activate your_env

python distributed_script.py
```

### The Python Implementation
This script uses `SLURMCluster` from the `dask_jobqueue` library to request and manage genuinely separate physical nodes as workers.

```python
import os
import numpy as np
from joblib import Parallel, delayed
from dask_jobqueue import SLURMCluster
from dask.distributed import Client, progress
import joblib

def heavy_computation(data):
    """Standard embarrassingly parallel function — no inter-task communication required."""
    return np.sqrt(data**2).sum()

if __name__ == "__main__":
    # 1. Define the Slurm Worker configuration.
    # Each 'job' Dask requests below is a separate Slurm allocation —
    # i.e. a distinct physical node with its own memory space.
    cluster = SLURMCluster(
        cores=48,                     # CPUs per node
        memory="180GB",               # RAM per node
        walltime="01:00:00",
        interface="ib0",              # Use InfiniBand for fast multi-node comms
        queue="pitzer-gpu",           # Or 'serial' / 'parallel'
        project="PASXXXX"             # Your OSC Project ID
    )

    # 2. Scale to 3 separate physical nodes (not 3 processes on one node).
    cluster.scale(jobs=3)

    # 3. Connect the Dask Client to the cluster
    client = Client(cluster)
    print(f"Dask Dashboard available at: {client.dashboard_link}")

    # 4. Generate some dummy data
    inputs = range(1000)

    # 5. Use Joblib with the Dask Backend
    # Joblib now sends these 1000 tasks across the 3-node cluster.
    with joblib.parallel_backend('dask'):
        results = Parallel(verbose=10)(
            delayed(heavy_computation)(i) for i in inputs
        )

    print(f"Finished processing. Result count: {len(results)}")
    client.close()
    cluster.close()
```

### Data Movement: The Real Multi-Node Bottleneck
Once workers live on separate nodes, every argument passed into `delayed()` has to be serialized (pickled) and sent over the network to the worker that runs it. This is where multi-node jobs commonly stall even though CPU usage looks low:

- **Large, repeated inputs** (a big NumPy array or DataFrame passed to every task) get serialized and re-sent for *each* task unless handled explicitly. Use `client.scatter(data, broadcast=True)` once, and pass the resulting future into `delayed()` calls instead of the raw object — this ships the data to every worker exactly once.
- **InfiniBand (`interface="ib0"`)**: explicitly selecting the high-speed network interface avoids falling back to a slower Ethernet path for inter-node traffic.
- **Chunk size matters**: too many tiny tasks means the network/scheduling overhead per task dominates; too few large tasks means poor load balancing across nodes. Aim for task granularity where computation time clearly exceeds serialization + network transfer time.

## 5. Decision Guide: Which Pattern Do I Need?

| Situation | Pattern | Why |
|---|---|---|
| Total parallel units fit within one node's cores/memory | Single-node Joblib (`loky`/`multiprocessing`) | No network involved, shared memory, simplest to debug |
| Total units exceed one node's cores/memory, but each unit runs independently (no communication mid-task) | Multi-node Dask (`SLURMCluster` + `joblib.parallel_backend('dask')`) | Distributed-memory scheduling, same `Parallel(delayed(...))` code as single-node |
| Workers must exchange data synchronously *during* the computation (e.g. an iterative PDE solve where each step depends on neighboring nodes' results) | MPI (`mpi4py`) | Task-graph schedulers assume independent tasks; genuine synchronous coupling needs a message-passing model instead |

## 6. Where MPI Still Fits

Joblib/Dask and MPI solve different communication patterns, and the choice follows from the algorithm, not from familiarity with either ecosystem. MPI's message-passing model is the right tool when processes must exchange data synchronously at every iteration — tightly-coupled simulations like CFD, N-body, or PDE solvers. Joblib/Dask's task-graph model fits the far more common case in data and ML pipelines: independent units of work — ensemble fits, per-tile processing, hyperparameter search — with no communication required between tasks during execution. Since nearly all of the workloads in this reference decompose into independent units (Section 2), the task-graph model is the correct default here.

## 7. Production-Grade Design Considerations
1. **Separation of concerns**: The Manager job is lightweight. If a worker node crashes, the Manager stays alive and can request a replacement from Slurm.
2. **Dashboard link**: Printing `client.dashboard_link` allows real-time monitoring of CPU/RAM usage across all nodes via a web browser (tunnelled through OSC OnDemand).
3. **Dynamic scaling**: `cluster.adapt(minimum=1, maximum=10)` lets Dask grow or shrink the worker pool based on the `joblib` queue size.

## 8. Portability Beyond HPC
The `SLURMCluster` backend above is one of several `dask_jobqueue`/Dask-native cluster backends. The identical `joblib.parallel_backend('dask')` call and task graph run against:

- **Local machine**: `from dask.distributed import LocalCluster` — same API, no scheduler involved.
- **Other HPC schedulers**: `PBSCluster`, `SGECluster`, `LSFCluster` from `dask_jobqueue` — swap the cluster class, keep the algorithm.
- **Cloud infrastructure**: Dask on Kubernetes, AWS Fargate, or managed services like Coiled — the compute backend changes, the parallel logic does not.

The same processing code moves from a laptop prototype to a single-node HPC run to a multi-node production run to a cloud deployment by swapping a cluster configuration object, not by rewriting the task decomposition or the communication logic.
