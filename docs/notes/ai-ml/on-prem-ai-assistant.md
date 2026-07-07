---
tags:
  - HPC
  - Ollama
  - LLM
  - Security
  - VS Code
  - GitHub Copilot
---

# Secure On-Prem AI Coding Assistant: Ollama on HPC + VS Code Copilot (BYOK)

**Why this matters:** research collaborators — PIs and faculty whose data governance agreements cover institutional, proprietary, or otherwise restricted datasets — cannot have that data transmitted to third-party AI providers, whether as prompt context or, worse, retained for model training. Commercially hosted AI coding agents (GitHub Copilot and similar) send prompts and file context to third-party cloud infrastructure by default, which is disqualifying for that class of work regardless of whether the exposure is intentional or accidental.

This setup satisfies that requirement directly: it hosts the AI model privately on HPC compute (H200 GPUs), keeping the model, prompts, and data entirely on-premises, while still using the familiar VS Code Copilot Chat interface. It's the configuration used whenever a stakeholder's data-handling policy requires demonstrable control over where prompts and context actually go — not a hypothetical precaution.

*Setup verified working July 2026 on the Unity (OSU/OSC) Slurm cluster, tunneled to a WSL2 laptop running VS Code with GitHub Copilot.*

**Ollama version installed: v0.31.1** (release asset: `ollama-linux-amd64.tar.zst`). Ollama has changed its release asset format before (`.tgz` → `.tar.zst`) — if a future install fails, check the [releases page](https://github.com/ollama/ollama/releases) for the current asset name and adjust the extraction step accordingly.

---

## Part 1: Installing Ollama on the HPC cluster (no sudo)

### Why the official installer doesn't work here
`curl -fsSL https://ollama.com/install.sh | sh` requires sudo/systemd, which HPC accounts don't have. Instead, the raw release binary is downloaded and unpacked manually.

### 1. Install location
```
/fs/full/path/to/ollama/
```
Chosen over `$HOME` because home directory quotas are small and the unpacked install is several GB.

### 2. Download the binary
`ollama.com` was blocked by the cluster firewall — GitHub releases worked instead:
```bash
curl -L https://github.com/ollama/ollama/releases/download/v0.31.1/ollama-linux-amd64.tar.zst -o ollama-linux-amd64.tar.zst
```
Sanity check the download isn't a tiny error page:
```bash
du -sh ollama-linux-amd64.tar.zst   # should be ~1.3-1.4GB, not KB
```

### 3. Extract it
The cluster's `tar` has no native zstd support (`tar --zstd` fails with "unrecognized option"), so pipe through `zstd` directly:
```bash
mkdir -p /fs/full/path/to/ollama
zstd -dc ollama-linux-amd64.tar.zst | tar -xf - -C /fs/full/path/to/ollama
```
If `zstd` isn't found as a command, check for it as a module:
```bash
module spider zstd
module load zstd/<version>
```
Result should be:
```
/fs/full/path/to/ollama/bin/ollama
/fs/full/path/to/ollama/lib/...
```

### 4. `~/.bashrc` additions
```bash
export PATH="/fs/full/path/to/ollama/bin:$PATH"
export OLLAMA_MODELS=/fs/full/path/to/ollama_models
export OLLAMA_HOST="0.0.0.0:11434"
```
**Why each line matters:**
- `PATH` — so `ollama` is callable directly without the full path.
- `OLLAMA_MODELS` — by default models download to `~/.ollama/models`, which will blow the home directory quota fast (models range ~1GB–120GB+ each). Redirecting to project space avoids this, and project space (unlike scratch) isn't auto-purged.
- `OLLAMA_HOST="0.0.0.0:11434"` — **critical for tunneling.** By default Ollama only binds to `127.0.0.1` on the compute node, which only accepts connections originating from that same node. Since the SSH tunnel connects to the compute node's hostname (e.g. `u190`) from the login node, the server needs to accept non-loopback connections — hence binding to all interfaces (`0.0.0.0`).

Reload and verify:
```bash
source ~/.bashrc
ollama --version
```

---

## Part 2: Getting a GPU allocation

Compute nodes are assigned dynamically by Slurm, so this is repeated each session. Two ways to do it — manual (interactive) or automated (batch, recommended for real use).

### Option A: Manual interactive session (`srun`)
Good for one-off testing, debugging, or when actively watching the terminal.

**1. Start a named `screen` session (survives SSH disconnects)**
```bash
screen -S ollama
```

**2. Request a GPU allocation, exclusive on the node**
```bash
srun --exclusive --gpus=1 -p batch-gpu -t 02:00:00 --pty bash -i
```
`--exclusive` requests the whole node (all CPUs + all RAM), not just a manually-guessed slice. This is safe to do here because each node in this partition (`u190`, `u191`) only has **one** GPU — confirmed via:
```bash
scontrol show partition batch-gpu   # OverSubscribe=NO
scontrol show node u190                 # gres/gpu:h200=1
```
Since there's no second GPU on the node for another job to use, taking the full CPU/RAM allocation doesn't block anyone else from GPU access — it only matters if you plan to run other CPU/RAM-heavy work (e.g. data preprocessing) alongside Ollama in the same session.

**3. Note the assigned node name**
```bash
hostname
```
Example: `u190` — needed for the tunnel command in Part 3.

**4. Start the Ollama server**
```bash
ollama serve &
```
Confirm it's alive: `ps aux | grep ollama`

**5. Detach from screen (optional, leaves it running)**
`Ctrl+A` then `D`. Reattach later with `screen -r ollama`.

### Option B: Automated batch job (`sbatch`) — recommended
Solves the real annoyance of `srun --pty` blocking the terminal while waiting in the GPU queue. Submit the job, get an email when it starts, and walk away in the meantime.

```bash
#!/usr/bin/env bash

#SBATCH --time=02:00:00
#SBATCH --exclusive
##SBATCH --cpus-per-task=90  # 90
##SBATCH --mem=140G  # 140G
#SBATCH --job-name=copilot-ollama
#SBATCH --output=OLLAMA_LOGS/ollama_session_%j.log
#SBATCH --error=OLLAMA_LOGS/ollama_session_%j.err
#SBATCH --partition=batch-gpu   # Match your cluster's GPU queue name
#SBATCH --gres=gpu:1                # Requests 1 GPU
#SBATCH --mail-type=ALL
#SBATCH --mail-user=your.email.edu
#SBATCH --begin=now+0minutes


# 1. Update PATH ollama executable, if not already done in your .bashrc
#export PATH="/fs/full/path/to/ollama/bin:$PATH"
# 2. Redirect models to large scratch file storage space
#export OLLAMA_MODELS="/fs/full/path/to/ollama_models"
# 3. Force Ollama to accept incoming tunnel configurations
#export OLLAMA_HOST="0.0.0.0:11434"


# 4. CRITICAL: Automatically write your dynamic tunnel instructions to a file
NODE_NAME=$(hostname)
echo "Run this specific command in your laptop's local terminal window:" > tunnel_instruction.txt
echo "ssh -NL 11500:${NODE_NAME}:11434 <username>@your-cluster.edu" >> tunnel_instruction.txt
echo "==========================================" >> tunnel_instruction.txt

# 5. Start the engine back-end
ollama serve &
OLLAMA_PID=$!
sleep 15

# Ensure your workspace model is downloaded (only downloads missing layers on subsequent runs)
# ollama pull deepseek-coder-v2

# Keep the compute session open
wait $OLLAMA_PID
```

**Notes on this script:**
- `mkdir -p OLLAMA_LOGS` may need to exist before first submission on some Slurm systems (this cluster currently auto-creates it, but that isn't guaranteed on every Slurm install — worth a quick manual `mkdir -p OLLAMA_LOGS` the first time on a new cluster, just in case).
- `wait $OLLAMA_PID` (not a bare `wait`) — waits specifically on the Ollama process. If `ollama serve` crashes early (OOM, bad model, etc.), the job ends immediately and releases the exclusive node back to the queue rather than idling for the full walltime.
- After submitting (`sbatch start_ollama.slurm`), check `tunnel_instruction.txt` (or the `.log` file) once the "job started" email arrives — it contains the exact `ssh -NL ...` command for that run's node, since the node name changes every time.

---

## Part 3: SSH tunnel from WSL2 laptop to the compute node

From a terminal on the WSL2 laptop (not on HPC):
```bash
ssh -NL 11500:u190:11434 <username>@your-cluster.edu
```
Breaking down `-NL local_port:remote_host:remote_port`:
- `11500` — the port opened on the **laptop**
- `u190` — the compute node hostname from Part 2 (**changes every session** — use whatever the job/`hostname` reports)
- `11434` — the port Ollama is actually listening on the compute node (fixed, matches `OLLAMA_HOST`)
- `-N` — tunnel only, no remote shell

**Local port choice (`11500`) is intentional, not arbitrary:** if a local WSL2 Ollama installation is also running, it will already occupy the default port `11434`. Using `11434` for both caused a port collision earlier (WSL2's local Ollama silently grabbed `127.0.0.1:11434`, pushing the SSH tunnel onto the IPv6 loopback, which `localhost` resolved to but `127.0.0.1` did not — leading to VS Code silently querying the empty local instance instead of the HPC one). Using a distinct port for the HPC tunnel avoids this entirely; both can now run simultaneously without conflict.

Leave this terminal open for the duration of the session.

### Test the tunnel
```bash
curl http://127.0.0.1:11500/api/tags
```
Should return the list of models pulled on the HPC side (e.g. `qwen2.5-coder:7b`).

---

## Part 4: VS Code setup (WSL2 — same process applies on native Windows)

### 1. Install the Ollama extension
Search "Ollama" in the VS Code Extensions Marketplace. Install the one published by **Ollama** (verified publisher, identifier `ollama.ollama`) — not one of the several third-party lookalikes in the search results.

### 2. Register two separate Ollama endpoints
Open `chatLanguageModels.json`:
```
C:\Users\<username>\AppData\Roaming\Code\User\chatLanguageModels.json
```
Open via Command Palette → `Preferences: Open User Data Folder`, or paste `%APPDATA%\Code\User` into File Explorer.

Add two distinctly named entries so local and HPC models never get confused with each other:
```json
{
    "name": "Ollama (Local)",
    "vendor": "ollama-models",
    "url": "http://127.0.0.1:11434"
},
{
    "name": "Ollama (HPC)",
    "vendor": "ollama-models",
    "url": "http://127.0.0.1:11500"
}
```

### 3. Reload and verify
Command Palette → `Developer: Reload Window`, then `Chat: Manage Language Models`. Both "Ollama (Local)" and "Ollama (HPC)" sections should appear, each listing their respective models.

### 4. Select the HPC model in Chat
Open the Chat panel → model picker at the bottom of the input box → choose the model under "Ollama (HPC)" (e.g. `qwen2.5-coder:7b`).

All chat traffic now routes through the tunnel to the HPC GPU node — no data leaves the local network to any cloud model provider.

---

## Part 5: Choosing a model

Ollama doesn't load a model into VRAM just because it's pulled/on disk — a model loads only when a request comes in, and unloads after an idle period (default 5 min, tunable via `OLLAMA_KEEP_ALIVE`). Multiple models can be pulled and visible in VS Code's picker without conflict; the risk is only in *choosing* one that doesn't fit the GPU actually running the job.

### On the H200 (141GB VRAM) — plenty of headroom
- **`qwen3-coder:30b`** — daily driver. 30B MoE (3.3B active), fast, strong general coding across Python/JS/fullstack, 256K context.
```bash
ollama pull qwen3-coder:30b
```
- **`devstral2:123b`** — heavier agentic/multi-file work (debugging loops, repo-level reasoning). ~65-75GB at Q4, still comfortable on the H200.
```bash
ollama pull devstral2:123b
```

### On a V100 (or other smaller GPU) — be deliberate
Ollama will **not** stop you from requesting a model too large for the card — it will either partially offload to CPU (10-50x slower) or fail with an out-of-memory error. There's no built-in safety net or allowlist. Options to keep this manageable:
- Only pull models that actually fit that GPU's VRAM in the first place — if it's never downloaded, it can't show up as a bad option in the picker.
- `OLLAMA_MAX_LOADED_MODELS=1` — forces only one model loaded at a time, preventing multiple models competing for the same limited VRAM.
- `OLLAMA_KEEP_ALIVE=2m` — frees VRAM faster after use if switching between models often.
- `ollama rm <model>` — removes a model you no longer want appearing as a selectable option.
- Multiple V100s can be used together for a single larger model (Ollama can split across GPUs it has access to) — a real option if V100s are more plentiful than H200s on the cluster.

**Bottom line:** the server doesn't enforce hardware fit — it's on the user to pull/select models sized appropriately for whichever GPU the job lands on.

---

## Known limitation
BYOK / local models apply to **Chat only**, not inline code completions — those still route through GitHub Copilot's cloud models by default. If completions must also avoid cloud data exposure, they'd need to be disabled separately.

## Full connection path (for reference)
```
VS Code Chat → Ollama (HPC) endpoint (127.0.0.1:11500)
            → SSH tunnel
            → compute node (u190:11434, OLLAMA_HOST=0.0.0.0)
            → ollama serve (GPU job via Slurm, --exclusive)
            → qwen3-coder:30b / devstral2:123b
```

## Gotchas encountered (keep for next time something breaks)
- `ollama.com` downloads blocked by cluster firewall → use GitHub releases instead
- Release asset format changed `.tgz` → `.tar.zst` in recent versions — check current format before assuming the old command works
- System `tar` lacks native zstd support → pipe through `zstd -dc` first
- Home directory quota gets blown by model weights if `OLLAMA_MODELS` isn't redirected
- Default `OLLAMA_HOST` (127.0.0.1-only) blocks tunneling → must set to `0.0.0.0`
- Local + remote Ollama both defaulting to port `11434` causes silent, confusing conflicts (IPv4 vs IPv6 loopback) → use different ports for each
- `sbatch` output/error log directory (`OLLAMA_LOGS/`) may need to be manually created first on some Slurm systems, not guaranteed to auto-create
- A model too large for the GPU in use doesn't fail cleanly — it either crawls (CPU offload) or OOMs; Ollama has no automatic hardware-fit check
