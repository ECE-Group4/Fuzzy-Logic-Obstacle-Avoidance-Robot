#!/usr/bin/env python3
"""
Fuzzy Logic Controller (FLC) for Ultrasonic Obstacle Avoidance Robot.
Provides:
  1. FuzzyLogicController: Standard 1-Meter Course Practical (Universe: [0, 100] cm, Cutoff: < 10 cm).
  2. FuzzyLogicController2M: 2-Meter Range Mode (Universe: [0, 200] cm, Complete Stop: <= 20 cm).
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class FLCResult:
    raw_distance: float
    clamped_distance: float
    mu_near: float
    mu_medium: float
    mu_far: float
    speed_percent: float
    pwm_value: int
    is_emergency_stop: bool
    behavior_description: str


class FuzzyLogicController:
    """Standard Lab Course FLC: Universe [0, 100] cm, Safety Cutoff < 10 cm."""
    NEAR_PARAMS = (0.0, 0.0, 30.0)      # (a, b, c) Left shoulder
    MED_PARAMS  = (15.0, 45.0, 75.0)    # (a, b, c) Symmetric triangle
    FAR_PARAMS  = (60.0, 100.0, 100.0)  # (a, b, c) Right shoulder

    SPEED_SLOW   = 20.0   # 20% PWM duty cycle
    SPEED_MEDIUM = 60.0   # 60% PWM duty cycle
    SPEED_FAST   = 100.0  # 100% PWM duty cycle

    SAFETY_DISTANCE = 10.0  # cm
    MAX_DISTANCE    = 100.0 # cm

    @staticmethod
    def trimf(x: float, a: float, b: float, c: float) -> float:
        if x <= a or x >= c: return 0.0
        if x == b: return 1.0
        if a < x < b: return (x - a) / (b - a)
        return (c - x) / (c - b)

    @staticmethod
    def trimf_left(x: float, b: float, c: float) -> float:
        if x <= b: return 1.0
        if x >= c: return 0.0
        return (c - x) / (c - b)

    @staticmethod
    def trimf_right(x: float, a: float, b: float) -> float:
        if x <= a: return 0.0
        if x >= b: return 1.0
        return (x - a) / (b - a)

    @classmethod
    def fuzzify(cls, d: float) -> Tuple[float, float, float]:
        d_clamped = max(0.0, min(cls.MAX_DISTANCE, float(d)))
        mu_near   = cls.trimf_left(d_clamped, cls.NEAR_PARAMS[1], cls.NEAR_PARAMS[2])
        mu_medium = cls.trimf(d_clamped, cls.MED_PARAMS[0], cls.MED_PARAMS[1], cls.MED_PARAMS[2])
        mu_far    = cls.trimf_right(d_clamped, cls.FAR_PARAMS[0], cls.FAR_PARAMS[1])
        return mu_near, mu_medium, mu_far

    @classmethod
    def compute(cls, distance_cm: float) -> FLCResult:
        raw_d = float(distance_cm)
        d = max(0.0, min(cls.MAX_DISTANCE, raw_d))

        mu_near, mu_medium, mu_far = cls.fuzzify(d)

        if raw_d < cls.SAFETY_DISTANCE:
            return FLCResult(
                raw_distance=raw_d,
                clamped_distance=d,
                mu_near=mu_near,
                mu_medium=mu_medium,
                mu_far=mu_far,
                speed_percent=0.0,
                pwm_value=0,
                is_emergency_stop=True,
                behavior_description="EMERGENCY STOP (<10cm) -> Halts & Reverses"
            )

        numerator = (mu_near * cls.SPEED_SLOW) + (mu_medium * cls.SPEED_MEDIUM) + (mu_far * cls.SPEED_FAST)
        denominator = mu_near + mu_medium + mu_far

        speed_pct = (numerator / denominator) if denominator > 1e-6 else 0.0
        speed_pct = max(0.0, min(100.0, speed_pct))
        pwm_val = int(round((speed_pct / 100.0) * 255.0))
        pwm_val = max(0, min(255, pwm_val))

        if speed_pct < 35.0:
            behavior = "Creeping / Smooth Slow Deceleration"
        elif speed_pct < 75.0:
            behavior = "Smooth Moderate Cruising Speed"
        else:
            behavior = "Full Forward Cruising Velocity"

        return FLCResult(
            raw_distance=raw_d,
            clamped_distance=d,
            mu_near=mu_near,
            mu_medium=mu_medium,
            mu_far=mu_far,
            speed_percent=speed_pct,
            pwm_value=pwm_val,
            is_emergency_stop=False,
            behavior_description=behavior
        )


class FuzzyLogicController2M:
    """FLC with 2-Meter Universe of Discourse [0, 200] cm and Complete Stop at <= 20 cm."""
    NEAR_PARAMS = (0.0, 0.0, 60.0)       # cm (Left shoulder)
    MED_PARAMS  = (40.0, 100.0, 160.0)   # cm (Triangle, peak at 1m)
    FAR_PARAMS  = (140.0, 200.0, 200.0)  # cm (Right shoulder, peak at 2m)

    SPEED_SLOW   = 20.0   # 20% PWM
    SPEED_MEDIUM = 60.0   # 60% PWM
    SPEED_FAST   = 100.0  # 100% PWM

    STOP_DISTANCE = 20.0  # cm (Stop moving approximately at 20 cm)
    MAX_DISTANCE  = 200.0 # cm (2 meters is Far)

    @staticmethod
    def trimf(x: float, a: float, b: float, c: float) -> float:
        if x <= a or x >= c: return 0.0
        if x == b: return 1.0
        if a < x < b: return (x - a) / (b - a)
        return (c - x) / (c - b)

    @staticmethod
    def trimf_left(x: float, b: float, c: float) -> float:
        if x <= b: return 1.0
        if x >= c: return 0.0
        return (c - x) / (c - b)

    @staticmethod
    def trimf_right(x: float, a: float, b: float) -> float:
        if x <= a: return 0.0
        if x >= b: return 1.0
        return (x - a) / (b - a)

    @classmethod
    def fuzzify(cls, d: float) -> Tuple[float, float, float]:
        d_clamped = max(0.0, min(cls.MAX_DISTANCE, float(d)))
        mu_near   = cls.trimf_left(d_clamped, cls.NEAR_PARAMS[1], cls.NEAR_PARAMS[2])
        mu_medium = cls.trimf(d_clamped, cls.MED_PARAMS[0], cls.MED_PARAMS[1], cls.MED_PARAMS[2])
        mu_far    = cls.trimf_right(d_clamped, cls.FAR_PARAMS[0], cls.FAR_PARAMS[1])
        return mu_near, mu_medium, mu_far

    @classmethod
    def compute(cls, distance_cm: float) -> FLCResult:
        raw_d = float(distance_cm)
        d = max(0.0, min(cls.MAX_DISTANCE, raw_d))

        mu_near, mu_medium, mu_far = cls.fuzzify(d)

        # Stop at approximately 20 cm
        if raw_d <= cls.STOP_DISTANCE:
            return FLCResult(
                raw_distance=raw_d,
                clamped_distance=d,
                mu_near=mu_near,
                mu_medium=mu_medium,
                mu_far=mu_far,
                speed_percent=0.0,
                pwm_value=0,
                is_emergency_stop=True,
                behavior_description="STOPPED (Obstacle <= 20 cm) -> Motors Off"
            )

        numerator = (mu_near * cls.SPEED_SLOW) + (mu_medium * cls.SPEED_MEDIUM) + (mu_far * cls.SPEED_FAST)
        denominator = mu_near + mu_medium + mu_far

        speed_pct = (numerator / denominator) if denominator > 1e-6 else 0.0
        speed_pct = max(0.0, min(100.0, speed_pct))
        pwm_val = int(round((speed_pct / 100.0) * 255.0))
        pwm_val = max(0, min(255, pwm_val))

        if raw_d >= 180.0:
            behavior = "2m Range: Far / Maximum Speed Ahead"
        elif speed_pct > 70.0:
            behavior = "High Speed Cruising"
        elif speed_pct > 40.0:
            behavior = "1m Range: Moderate Cruise"
        else:
            behavior = "Approaching Obstacle: Decelerating Smoothly"

        return FLCResult(
            raw_distance=raw_d,
            clamped_distance=d,
            mu_near=mu_near,
            mu_medium=mu_medium,
            mu_far=mu_far,
            speed_percent=speed_pct,
            pwm_value=pwm_val,
            is_emergency_stop=False,
            behavior_description=behavior
        )


if __name__ == "__main__":
    res25 = FuzzyLogicController.compute(25.0)
    print(f"Standard 1M FLC @ d=25cm -> Speed={res25.speed_percent:.1f}% | PWM={res25.pwm_value}")
    assert abs(res25.speed_percent - 46.7) < 0.2

    res200 = FuzzyLogicController2M.compute(200.0)
    res20 = FuzzyLogicController2M.compute(20.0)
    print(f"2M FLC @ d=200cm -> Speed={res200.speed_percent:.1f}% | PWM={res200.pwm_value}")
    print(f"2M FLC @ d=20cm  -> Speed={res20.speed_percent:.1f}%  | PWM={res20.pwm_value}")
    assert res200.pwm_value == 255
    assert res20.pwm_value == 0
    print("ALL PYTHON SELF-TESTS PASSED!")
