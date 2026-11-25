#!/usr/bin/env python3
"""
Fuzzy Logic Obstacle Avoidance Simulation & Telemetry Monitor
Course: Artificial Intelligence and Logic
"""

import sys
import time
import argparse
from fuzzy_controller import FuzzyLogicController, FLCResult


def print_table():
    """Prints distance vs speed response table."""
    print("\n" + "=" * 90)
    print("       FUZZY LOGIC CONTROLLER - EXPERIMENTAL RESULTS TABLE       ".center(86))
    print("=" * 90)
    print(f"| {'Distance (cm)':^15} | {'mu_Near':^10} | {'mu_Medium':^10} | {'mu_Far':^10} | {'Speed (%)':^11} | {'PWM':^8} | {'Robot Behavior':^20} |")
    print("-" * 90)

    test_points = [5.0, 15.0, 20.0, 25.0, 35.0, 50.0, 70.0, 90.0, 100.0]

    for d in test_points:
        res = FuzzyLogicController.compute(d)
        if res.is_emergency_stop:
            behavior = "Stop / Evasive Turn"
        elif res.speed_percent < 35.0:
            behavior = "Slow Approach"
        elif res.speed_percent < 75.0:
            behavior = "Moderate Cruise"
        else:
            behavior = "Full Speed Forward"

        print(f"| {d:^15.1f} | {res.mu_near:^10.3f} | {res.mu_medium:^10.3f} | {res.mu_far:^10.3f} | {res.speed_percent:^11.1f} | {res.pwm_value:^8} | {behavior:<20} |")

    print("-" * 90 + "\n")


def simulate_approach():
    """Simulates moving an obstacle towards the sensor and away."""
    print("\n" + "=" * 80)
    print("       SIMULATION: OBSTACLE APPROACH AND WITHDRAWAL       ".center(76))
    print("=" * 80 + "\n")

    distances = [100.0, 85.0, 70.0, 55.0, 45.0, 35.0, 25.0, 20.0, 15.0, 8.0]

    print(">>> Approaching obstacle (Deceleration):")
    for d in distances:
        r = FuzzyLogicController.compute(d)
        bar = "█" * int(r.speed_percent / 2) + "░" * (50 - int(r.speed_percent / 2))
        status = "STOP" if r.is_emergency_stop else f"{r.speed_percent:5.1f}%"
        print(f"Dist: {d:5.1f} cm | [{bar}] {status} | PWM: {r.pwm_value:3d}")
        time.sleep(0.04)

    print("\n>>> Obstacle moving away (Acceleration):")
    for d in reversed(distances):
        r = FuzzyLogicController.compute(d)
        bar = "█" * int(r.speed_percent / 2) + "░" * (50 - int(r.speed_percent / 2))
        status = "STOP" if r.is_emergency_stop else f"{r.speed_percent:5.1f}%"
        print(f"Dist: {d:5.1f} cm | [{bar}] {status} | PWM: {r.pwm_value:3d}")
        time.sleep(0.04)

    print("\nSimulation complete.\n")


def main():
    parser = argparse.ArgumentParser(description="FLC Simulation & Results Generator")
    parser.add_argument("--table", action="store_true", help="Print experimental results table")
    parser.add_argument("--demo", action="store_true", help="Run simulated approach demo")
    args = parser.parse_args()

    if args.demo:
        simulate_approach()
    else:
        print_table()
        simulate_approach()


if __name__ == "__main__":
    main()
