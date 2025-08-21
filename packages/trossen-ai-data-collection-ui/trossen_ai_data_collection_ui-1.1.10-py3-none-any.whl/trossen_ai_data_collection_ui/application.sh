#!/bin/bash

# Path to your conda installation
CONDA_PATH="$HOME/miniconda3"

# Activate the conda environment
source "$CONDA_PATH/bin/activate" trossen_ai_data_collection_ui_env

# Set the environment variable
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6

# Run the executable
trossen_ai_data_collection_ui
