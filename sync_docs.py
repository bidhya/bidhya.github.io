#!/usr/bin/env python3
"""
Python utility script to synchronize technical engineering notes and
Jupyter notebook tutorials from the private parent directory ('job/')
to the public MkDocs portfolio directory ('githubio/docs/').

This implements 'Option B' (Automated Structured Synchronization) ensuring
a single source of truth inside active directories.
"""

import sys
import os
import shutil
import re

# Resolve absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Reference: parent folder `/home/bny/Github/job`
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

# Hardcoded mapping of source to destination paths relative to githubio/docs
FILE_MAP = {
    # ------------------
    # Technical Notes (Markdown)
    # ------------------
    "KBase/02-AI-and-ML/Deep-Learning/gpu_ddp_primer.md":
        "notes/ai-ml/gpu-ddp.md",
    "KBase/02-AI-and-ML/Architecture-Models/transformer_decoder.md":
        "notes/ai-ml/transformers.md",
    "KBase/03-Geospatial/GIS-Tutorials/kalman_filter.md":
        "notes/geospatial/kalman-filter.md",
    "KBase/03-Geospatial/GIS-Tutorials/gis_cheatsheet.md":
        "notes/geospatial/gis-cheatsheet.md",
    "KBase/03-Geospatial/Remote-Sensing/hyperspectral/hyperspectral_concepts.md":
        "notes/geospatial/hyperspectral-concepts.md",

    # ------------------
    # AI/ML Notes (Phase 3)
    # ------------------
    "KBase/02-AI-and-ML/Machine-Learning/stats_to_deep_learning.md":
        "notes/ai-ml/stats-to-deep-learning.md",
    "KBase/02-AI-and-ML/Machine-Learning/bias_variance.md":
        "notes/ai-ml/bias-variance.md",
    "KBase/02-AI-and-ML/Deep-Learning/deep_learning_pytorch_foundations.md":
        "notes/ai-ml/pytorch-foundations.md",
    "KBase/02-AI-and-ML/Architecture-Models/tokenization_embeddings_primer.md":
        "notes/ai-ml/tokenization-embeddings.md",
    "KBase/02-AI-and-ML/Deep-Learning/fine_tuning.md":
        "notes/ai-ml/fine-tuning.md",
    "KBase/03-Geospatial/GIS-Tutorials/geospatial_peft.md":
        "notes/ai-ml/geospatial-peft.md",
    "KBase/02-AI-and-ML/Architecture-Models/qkv.md":
        "notes/ai-ml/qkv-kvcache.md",
    "KBase/02-AI-and-ML/Architecture-Models/llm_temperature.md":
        "notes/ai-ml/llm-temperature.md",

    # ------------------
    # Computer Vision Notes
    # ------------------
    "KBase/02-AI-and-ML/Computer-Vision/vision_transformer.md":
        "notes/ai-ml/vision-transformer.md",
    "KBase/02-AI-and-ML/Computer-Vision/vit_needs_more_data.md":
        "notes/ai-ml/vit-data-requirements.md",

    # ------------------
    # HPC & Distributed Computing
    # ------------------
    "KBase/04-HPC/multi_node_dask_joblib.md":
        "notes/ai-ml/multi-node-parallelization.md",

    # ------------------
    # Geospatial Notes (Phase 3)
    # ------------------
    "KBase/03-Geospatial/GIS-Tutorials/pyproj_cheatsheet.md":
        "notes/geospatial/pyproj-crs.md",
    "KBase/03-Geospatial/Remote-Sensing/real_world_patterns.md":
        "notes/geospatial/real-world-patterns.md",
    "KBase/03-Geospatial/Remote-Sensing/hvplot_visualization.md":
        "notes/geospatial/hvplot-visualization.md",

    # ------------------
    # Jupyter Notebook Tutorials (.ipynb)
    # ------------------
    "KBase/03-Geospatial/Remote-Sensing/hyperspectral/10_pace_ocean_color.ipynb":
        "tutorials/ocean-color.ipynb",
    "KBase/03-Geospatial/Remote-Sensing/satellite_change_detection/04_change_detection.ipynb":
        "tutorials/change-detection.ipynb",
    "KBase/02-AI-and-ML/NLP/01_NLP_Foundations_NER.ipynb":
        "tutorials/nlp-ner.ipynb",
    "KBase/02-AI-and-ML/NLP/02_NLP_Topic_Modeling.ipynb":
        "tutorials/nlp-topic-modeling.ipynb",
    "KBase/02-AI-and-ML/NLP/03_NLP_Sentiment_and_Zero_Shot.ipynb":
        "tutorials/nlp-sentiment-analysis.ipynb"
}


def sanitize_content(content, file_path):
    """
    Sanitize content to replace legacy candidate/prep search terms with
    professional, educational, and high-agency equivalents.
    """
    # Define simple string replacements to maintain "Instructor Tone"
    replacements = {
        r"\b(job search|interview preparation|interview prep"
        r"|prep guide|study notes for|interview notes"
        r"|hiring manager)\b":
            "engineering reference",
        r"\b(cheat sheet|cheatsheet|cheat_sheet|quick notes)\b":
            "Reference Guide",
        r"\b(coding challenge|practice script"
        r"|practice notebook)\b":
            "Reference Pipeline",
        r"\b(candidate|interviewee)\b":
            "Engineer",
    }

    sanitized = content
    for pattern, replacement in replacements.items():
        # Case insensitive substitution
        sanitized = re.sub(
            pattern, replacement, sanitized, flags=re.IGNORECASE
        )

    return sanitized


def run_sync():
    print("=" * 60)
    print("🚀 STARTING PORTFOLIO SYNC (Option B: Single Source of Truth)")
    print("=" * 60)

    docs_dir = os.path.join(SCRIPT_DIR, "docs")
    if not os.path.exists(docs_dir):
        print(f"❌ Error: MkDocs docs directory not found: {docs_dir}")
        sys.exit(1)

    success_count = 0
    fail_count = 0

    for src_rel, dest_rel in FILE_MAP.items():
        src_path = os.path.join(PARENT_DIR, src_rel)
        dest_path = os.path.join(docs_dir, dest_rel)

        # Verify source file exists
        if not os.path.exists(src_path):
            print(f"⚠️ Source file missing: {src_path}")
            fail_count += 1
            continue

        # Ensure destination parent folder exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        rel_dest = os.path.relpath(dest_path, SCRIPT_DIR)
        print(f"🔄 Syncing: [{src_rel}] -> [{rel_dest}]")

        try:
            # For markdown files, we read, sanitize, and write
            if src_path.endswith('.md'):
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                sanitized_content = sanitize_content(content, src_path)

                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(sanitized_content)
            else:
                # For Jupyter notebooks, perform direct content copy
                shutil.copy2(src_path, dest_path)

            success_count += 1

        except Exception as e:
            print(f"❌ Failed to sync {src_rel}: {e}")
            fail_count += 1

    print("=" * 60)
    print(f"📊 Sync Summary: {success_count} succeeded, {fail_count} failed.")
    print("=" * 60)

    if fail_count > 0:
        sys.exit(1)
    else:
        print("🎉 Sync completed successfully!")


if __name__ == "__main__":
    run_sync()
