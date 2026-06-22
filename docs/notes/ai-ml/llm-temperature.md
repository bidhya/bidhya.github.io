---
tags:
  - LLM
  - Inference
  - Temperature
  - Sampling
  - Reasoning Models
---

# AI Core Concepts: From Statistical Physics to Reasoning Models

## 1. Temperature as Information Entropy
* **The Physics Bridge:** Model temperature is mathematically derived from the Boltzmann distribution.
* **The Setting Knob:** Temperature is the independent knob used to inflate or deflate natural token entropy.
* **Ground State (T = 0):** Zero entropy. Perfectly deterministic. The model always picks the highest-probability token. Useful for strict syntax coding.
* **Excited State (T = 1):** High entropy. Probability distributions flatten. Lower-probability tokens gain a fighting chance. Useful for creative brainstorming.

## 2. Standard Models vs. Reasoning Models
* **Standard Models (e.g., Claude Sonnet/Haiku, Llama 3):** High temperature (T=1) forces linear next-token guessing. This often causes syntax errors, hallucinations, and nice-sounding gibberish.
* **Reasoning Models (e.g., Kimi K2.6, OpenAI o-series):** High temperature (T=1) is strictly required to explore complex scientific and logical paths.

## 3. The Kimi K2.6 Search Mechanics
* **Monte Carlo Tree Search (MCTS):** Instead of guessing text in a straight line, Kimi branches out multiple hidden thought drafts.
* **The Internal Critic:** The model features a split architecture: a *generator* (needs high entropy to brainstorm paths) and a *verifier* (acts like a strict math professor).
* **The Output:** The verifier filters out high-entropy gibberish during the hidden thinking phase. You only see the finalized, logically sound response.

## 4. IDE Automation: GitHub Copilot's Hidden Tuning
* **No Manual Dials:** You do not need to manually set temperature flags inside GitHub Copilot.
* **Adaptive Context Tuning:** Copilot dynamically scales entropy behind the scenes. 
* **Inline Coding:** Forces low entropy for deterministic, bug-free syntax completion.
* **Workspace Agent Mode:** Automatically elevates reasoning depth to allow the model to brainstorm multi-file architectural changes.
