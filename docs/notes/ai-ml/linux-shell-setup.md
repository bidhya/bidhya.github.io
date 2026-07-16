---
tags:
  - Linux
  - Shell
  - HPC
  - Developer Tooling
---

# Linux Shell Setup for HPC, Python, and AI Workflows

## Why this matters

Many users coming from Windows develop the habit of putting every Linux setting into `.bashrc` because it works. On many HPC systems this appears to work because `.bash_profile` often loads `.bashrc` automatically.

Over time, however, this can mix together different kinds of settings:

- software paths
- cache locations
- API tokens
- aliases
- shell functions
- Conda/Mamba hooks

A cleaner approach is to separate **environment configuration** from **shell behavior**. This makes a system easier to understand, maintain, reproduce, and migrate to a new HPC account, workstation, WSL installation, or cloud VM.

---

## The main idea

Before adding a new line to a shell configuration file, ask:

### Am I configuring software?

Examples include:

```bash
PATH
PYTHONPATH
HF_HOME
HF_TOKEN
UV_CACHE_DIR
PIXI_CACHE_DIR
OLLAMA_MODELS
PL_API_KEY
CUDA_HOME
```

Put these in:

```bash
~/.bash_profile
```

Note: Some systems, such as many WSL installations, use `~/.profile` instead of `~/.bash_profile`; use it the same way for environment configuration.

These settings define where software lives, where data is stored, and how programs authenticate.

---

### Am I changing how Bash behaves?

Examples include:

```bash
alias
function
prompt
tab completion
history settings
```

Put these in:

```bash
~/.bashrc
```

These settings affect how you interact with the terminal.

---

## The files

### `.bash_profile`

Use this for environment setup.

Typical responsibilities:

- PATH additions
- Python paths
- cache locations
- model locations
- software-specific variables
- API keys or tokens, preferably loaded from a separate secrets file

Think:

> `.bash_profile` defines the environment that programs inherit.

On many HPC systems, this is the most important file for day-to-day software configuration.

---

### `.bashrc`

Use this for interactive shell behavior.

Typical responsibilities:

- aliases
- functions
- prompt customization
- shell completion
- Conda/Mamba/Pixi shell hooks

Example:

```bash
alias sq='squeue -u $USER'

myjobs() {
    squeue -u "$USER"
}
```

Think:

> `.bashrc` changes how the shell behaves while I am typing commands.

---

## Startup pattern on many HPC systems

Many HPC systems use this pattern:

```text
.bash_profile
    ↓
.bashrc
```

The login shell reads `.bash_profile`, and `.bash_profile` often sources `.bashrc`.

This means settings placed in `.bashrc` may still work, but for good organization, environment variables should usually live in `.bash_profile`.

---

## Cache management

Large caches should usually not live in the home directory.

Home directories are better for:

- scripts
- source code
- configuration files
- small working files

Project or scratch storage is better for:

- model weights
- package caches
- downloaded datasets
- temporary installation files

Useful examples:

```bash
export HF_HOME=/fs/project/.../cache/huggingface
export UV_CACHE_DIR=/fs/project/.../cache/uv
export PIXI_CACHE_DIR=/fs/project/.../cache/rattler
```

A clean cache layout might look like:

```text
cache/
├── huggingface/
├── rattler/
└── uv/
```

This keeps large, regenerable data out of the home directory.

---

## Secrets management

Credentials should be separated from general software configuration.

Create a file such as:

```bash
~/.secrets
```

Example contents:

```bash
export HF_TOKEN="..."
export PL_API_KEY="..."
export EARTHDATA_TOKEN="..."
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

Protect the file:

```bash
chmod 600 ~/.secrets
```

Then load it from `.bash_profile`:

```bash
if [ -f ~/.secrets ]; then
    . ~/.secrets
fi
```

This keeps tokens easier to rotate and avoids cluttering the main shell configuration file.

---

## Important distinctions

Most tools have several separate concepts.

### Executable location

Where the command lives.

Example:

```bash
PATH
```

### Cache location

Where downloaded or temporary data is stored.

Examples:

```bash
HF_HOME
UV_CACHE_DIR
PIXI_CACHE_DIR
```

### Credentials

How the software authenticates.

Examples:

```bash
HF_TOKEN
PL_API_KEY
EARTHDATA_TOKEN
```

Keeping these separate makes troubleshooting much easier.

---

## Practical rule of thumb

Use `.bash_profile` for software and environment configuration.

Use `.bashrc` for terminal convenience and interactive behavior.

---

## Going forward

When setting up a new Linux environment, HPC account, workstation, WSL system, or cloud VM:

1. Put environment variables in `.bash_profile`.
2. Put aliases and functions in `.bashrc`.
3. Move large caches away from the home directory.
4. Store credentials in `.secrets`.
5. Organize settings by software or project so they are easy to remove later.

This structure keeps the system cleaner, easier to debug, and easier to reproduce.
