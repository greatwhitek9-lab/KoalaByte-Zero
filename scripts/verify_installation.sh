#!/bin/bash
# Verify basic Jetson/CUDA host installation
jetson_release || echo "Error: Jetson release information unavailable"
nvcc --version || echo "Error: CUDA Toolkit not detected"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi || echo "Error: NVIDIA drivers not working"
else
  echo "nvidia-smi not found on PATH"
fi
