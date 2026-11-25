.PHONY: all sim plot demo clean help

PYTHON ?= python3

all: plot sim

plot:
	@echo "Generating plots..."
	@$(PYTHON) simulation/generate_plots.py

sim:
	@echo "Running simulation..."
	@$(PYTHON) simulation/robot_simulation.py --table

demo:
	@echo "Running demo approach simulation..."
	@$(PYTHON) simulation/robot_simulation.py --demo

clean:
	@echo "Cleaning temporary files..."
	@rm -rf simulation/__pycache__

help:
	@echo "Available targets:"
	@echo "  make all   - Generate plots and print results table"
	@echo "  make plot  - Generate SVG and PNG plots in images/"
	@echo "  make sim   - Display experimental results table"
	@echo "  make demo  - Run interactive terminal approach simulation"
	@echo "  make clean - Clean temporary pycache files"
