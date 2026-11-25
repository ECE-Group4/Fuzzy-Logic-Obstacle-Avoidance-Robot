#!/usr/bin/env bash
set -e

echo "=== Fuzzy Logic Robot Project: Build & Verification ==="
echo ""

# 1. Run Python model tests
echo "[1/3] Testing Fuzzy Controller Model..."
python3 simulation/fuzzy_controller.py

# 2. Generate membership and response plots
echo "[2/3] Generating Membership and Control Surface Plots..."
python3 simulation/generate_plots.py

# 3. Print experimental results table
echo "[3/3] Printing Experimental Results Table..."
python3 simulation/robot_simulation.py --table

echo ""
echo "=== Done! All files generated and ready. ==="
