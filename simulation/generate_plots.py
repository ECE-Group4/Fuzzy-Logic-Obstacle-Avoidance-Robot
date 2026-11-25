#!/usr/bin/env python3
"""
Vector Plot Generator for Fuzzy Logic Controller Practical.
Generates publication-quality SVG and PNG diagrams:
  1. Triangular Membership Functions Plot (Near, Medium, Far) with overlap zones and d=25cm example.
  2. FLC Output Speed Response Surface & Comparison vs Crisp Bang-Bang Control.
  3. System Architecture & Block Diagram.
"""

import os
import subprocess
import math
from fuzzy_controller import FuzzyLogicController


def create_membership_functions_svg(filepath: str):
    width = 900
    height = 520
    margin_left = 80
    margin_right = 60
    margin_top = 70
    margin_bottom = 80

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    def x_to_px(d_cm: float) -> float:
        return margin_left + (d_cm / 100.0) * plot_width

    def y_to_px(mu: float) -> float:
        return margin_top + (1.0 - mu) * plot_height

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<defs>')
    svg.append('''
      <style>
        .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 22px; font-weight: bold; fill: #1e293b; text-anchor: middle; }
        .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13px; fill: #64748b; text-anchor: middle; }
        .axis-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 600; fill: #334155; }
        .tick-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #475569; text-anchor: middle; }
        .y-tick-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #475569; text-anchor: end; }
        .legend-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 600; fill: #1e293b; }
        .annotation { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #0f172a; }
        .grid-line { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 4,4; }
        .axis-line { stroke: #475569; stroke-width: 2; }
      </style>
      <linearGradient id="nearGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#ef4444" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#ef4444" stop-opacity="0.05"/>
      </linearGradient>
      <linearGradient id="medGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#10b981" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#10b981" stop-opacity="0.05"/>
      </linearGradient>
      <linearGradient id="farGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.35"/>
        <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.05"/>
      </linearGradient>
    ''')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{width}" height="{height}" fill="#ffffff" rx="12"/>')
    svg.append(f'<rect x="{margin_left}" y="{margin_top}" width="{plot_width}" height="{plot_height}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')

    # Title & Subtitle
    svg.append(f'<text x="{width/2}" y="32" class="title">Triangular Membership Functions for Obstacle Distance μ(d)</text>')
    svg.append(f'<text x="{width/2}" y="52" class="subtitle">Universe of Discourse: Distance d ∈ [0, 100] cm | Overlapping Fuzzy Subsets: Near, Medium, Far</text>')

    # Grid Lines & X-Ticks
    for d in range(0, 101, 10):
        px = x_to_px(d)
        svg.append(f'<line x1="{px}" y1="{margin_top}" x2="{px}" y2="{margin_top + plot_height}" class="grid-line"/>')
        svg.append(f'<line x1="{px}" y1="{margin_top + plot_height}" x2="{px}" y2="{margin_top + plot_height + 6}" stroke="#475569" stroke-width="1.5"/>')
        svg.append(f'<text x="{px}" y="{margin_top + plot_height + 22}" class="tick-label">{d}</text>')

    # Y-Ticks
    for mu_idx in range(0, 11, 2):
        mu = mu_idx / 10.0
        py = y_to_px(mu)
        svg.append(f'<line x1="{margin_left}" y1="{py}" x2="{margin_left + plot_width}" y2="{py}" class="grid-line"/>')
        svg.append(f'<line x1="{margin_left - 6}" y1="{py}" x2="{margin_left}" y2="{py}" stroke="#475569" stroke-width="1.5"/>')
        svg.append(f'<text x="{margin_left - 12}" y="{py + 4}" class="y-tick-label">{mu:.1f}</text>')

    # Axis Labels
    svg.append(f'<text x="{margin_left + plot_width/2}" y="{height - 20}" class="axis-label" text-anchor="middle">Obstacle Distance d (cm)</text>')
    svg.append(f'<text x="24" y="{margin_top + plot_height/2}" class="axis-label" text-anchor="middle" transform="rotate(-90 24 {margin_top + plot_height/2})">Degree of Membership μ(d)</text>')

    # Shaded Overlap Highlights
    # Overlap 1: 15 to 30 cm
    ov1_x1 = x_to_px(15)
    ov1_w = x_to_px(30) - ov1_x1
    svg.append(f'<rect x="{ov1_x1}" y="{margin_top}" width="{ov1_w}" height="{plot_height}" fill="#fef08a" opacity="0.35"/>')
    svg.append(f'<text x="{ov1_x1 + ov1_w/2}" y="{margin_top + 25}" font-size="11" font-weight="bold" fill="#854d0e" text-anchor="middle">Overlap [15–30 cm]</text>')

    # Overlap 2: 60 to 75 cm
    ov2_x1 = x_to_px(60)
    ov2_w = x_to_px(75) - ov2_x1
    svg.append(f'<rect x="{ov2_x1}" y="{margin_top}" width="{ov2_w}" height="{plot_height}" fill="#bae6fd" opacity="0.35"/>')
    svg.append(f'<text x="{ov2_x1 + ov2_w/2}" y="{margin_top + 25}" font-size="11" font-weight="bold" fill="#0369a1" text-anchor="middle">Overlap [60–75 cm]</text>')

    # Polygons / Areas under curves
    # 1. Near: (0, 1.0) -> (0, 1.0) -> (30, 0.0) -> (0, 0.0)
    near_pts = f"{x_to_px(0)},{y_to_px(1)} {x_to_px(0)},{y_to_px(1)} {x_to_px(30)},{y_to_px(0)} {x_to_px(0)},{y_to_px(0)}"
    svg.append(f'<polygon points="{near_pts}" fill="url(#nearGrad)"/>')

    # 2. Medium: (15, 0.0) -> (45, 1.0) -> (75, 0.0)
    med_pts = f"{x_to_px(15)},{y_to_px(0)} {x_to_px(45)},{y_to_px(1)} {x_to_px(75)},{y_to_px(0)}"
    svg.append(f'<polygon points="{med_pts}" fill="url(#medGrad)"/>')

    # 3. Far: (60, 0.0) -> (100, 1.0) -> (100, 0.0)
    far_pts = f"{x_to_px(60)},{y_to_px(0)} {x_to_px(100)},{y_to_px(1)} {x_to_px(100)},{y_to_px(0)}"
    svg.append(f'<polygon points="{far_pts}" fill="url(#farGrad)"/>')

    # Draw Lines for Membership Functions
    # Near Line (Red)
    svg.append(f'<polyline points="{x_to_px(0)},{y_to_px(1)} {x_to_px(30)},{y_to_px(0)} {x_to_px(100)},{y_to_px(0)}" fill="none" stroke="#dc2626" stroke-width="3.5" stroke-linecap="round"/>')
    # Medium Line (Green)
    svg.append(f'<polyline points="{x_to_px(0)},{y_to_px(0)} {x_to_px(15)},{y_to_px(0)} {x_to_px(45)},{y_to_px(1)} {x_to_px(75)},{y_to_px(0)} {x_to_px(100)},{y_to_px(0)}" fill="none" stroke="#16a34a" stroke-width="3.5" stroke-linecap="round"/>')
    # Far Line (Blue)
    svg.append(f'<polyline points="{x_to_px(0)},{y_to_px(0)} {x_to_px(60)},{y_to_px(0)} {x_to_px(100)},{y_to_px(1)}" fill="none" stroke="#2563eb" stroke-width="3.5" stroke-linecap="round"/>')

    # Worked Example Marker at d = 25 cm
    # d = 25: muNear = (30-25)/30 = 0.167; muMed = (25-15)/30 = 0.333
    ex_d = 25.0
    mu_near_25 = 5.0 / 30.0
    mu_med_25 = 10.0 / 30.0
    px25 = x_to_px(ex_d)
    py_near25 = y_to_px(mu_near_25)
    py_med25 = y_to_px(mu_med_25)

    svg.append(f'<line x1="{px25}" y1="{margin_top}" x2="{px25}" y2="{margin_top + plot_height}" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5,5"/>')
    svg.append(f'<circle cx="{px25}" cy="{py_near25}" r="6" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>')
    svg.append(f'<circle cx="{px25}" cy="{py_med25}" r="6" fill="#16a34a" stroke="#ffffff" stroke-width="2"/>')
    
    # Text callout for worked example
    svg.append(f'''
      <rect x="{px25 + 15}" y="{py_med25 - 45}" width="230" height="60" rx="6" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.5"/>
      <text x="{px25 + 25}" y="{py_med25 - 28}" class="annotation" fill="#5b21b6">Worked Example @ d = 25 cm</text>
      <text x="{px25 + 25}" y="{py_med25 - 12}" font-size="11" fill="#dc2626">μ_Near = 5/30 ≈ 0.167</text>
      <text x="{px25 + 25}" y="{py_med25 + 4}" font-size="11" fill="#16a34a">μ_Medium = 10/30 ≈ 0.333</text>
    ''')

    # Peak Points Circles
    svg.append(f'<circle cx="{x_to_px(0)}" cy="{y_to_px(1)}" r="5" fill="#dc2626"/>')
    svg.append(f'<circle cx="{x_to_px(45)}" cy="{y_to_px(1)}" r="5" fill="#16a34a"/>')
    svg.append(f'<circle cx="{x_to_px(100)}" cy="{y_to_px(1)}" r="5" fill="#2563eb"/>')

    # Legend at top-right
    leg_x = width - margin_right - 270
    leg_y = margin_top + 15
    svg.append(f'''
      <rect x="{leg_x}" y="{leg_y}" width="260" height="110" rx="8" fill="#ffffff" fill-opacity="0.95" stroke="#cbd5e1" stroke-width="1"/>
      <line x1="{leg_x + 15}" y1="{leg_y + 25}" x2="{leg_x + 45}" y2="{leg_y + 25}" stroke="#dc2626" stroke-width="3"/>
      <text x="{leg_x + 55}" y="{leg_y + 29}" class="legend-text">Near: (0, 0, 30) cm</text>
      
      <line x1="{leg_x + 15}" y1="{leg_y + 55}" x2="{leg_x + 45}" y2="{leg_y + 55}" stroke="#16a34a" stroke-width="3"/>
      <text x="{leg_x + 55}" y="{leg_y + 59}" class="legend-text">Medium: (15, 45, 75) cm</text>
      
      <line x1="{leg_x + 15}" y1="{leg_y + 85}" x2="{leg_x + 45}" y2="{leg_y + 85}" stroke="#2563eb" stroke-width="3"/>
      <text x="{leg_x + 55}" y="{leg_y + 89}" class="legend-text">Far: (60, 100, 100) cm</text>
    ''')

    svg.append('</svg>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
    print(f"Generated: {filepath}")


def create_flc_response_curve_svg(filepath: str):
    width = 900
    height = 520
    margin_left = 80
    margin_right = 80
    margin_top = 70
    margin_bottom = 80

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    def x_to_px(d_cm: float) -> float:
        return margin_left + (d_cm / 100.0) * plot_width

    def y_to_px(pct: float) -> float:
        return margin_top + (1.0 - pct / 100.0) * plot_height

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<defs>')
    svg.append('''
      <style>
        .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 22px; font-weight: bold; fill: #1e293b; text-anchor: middle; }
        .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13px; fill: #64748b; text-anchor: middle; }
        .axis-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 600; fill: #334155; }
        .tick-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #475569; text-anchor: middle; }
        .y-tick-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #475569; text-anchor: end; }
        .y2-tick-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #64748b; text-anchor: start; }
        .legend-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 600; fill: #1e293b; }
        .grid-line { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 4,4; }
      </style>
      <linearGradient id="curveGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#4f46e5" stop-opacity="0.30"/>
        <stop offset="100%" stop-color="#4f46e5" stop-opacity="0.02"/>
      </linearGradient>
    ''')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{width}" height="{height}" fill="#ffffff" rx="12"/>')
    svg.append(f'<rect x="{margin_left}" y="{margin_top}" width="{plot_width}" height="{plot_height}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')

    # Title & Subtitle
    svg.append(f'<text x="{width/2}" y="32" class="title">Control Surface: Fuzzy Speed Output vs. Distance</text>')
    svg.append(f'<text x="{width/2}" y="52" class="subtitle">Comparison: Smooth Fuzzy Controller vs. Abrupt Crisp Bang-Bang Control (with Safety Zone &lt; 10 cm)</text>')

    # Grid & Ticks
    for d in range(0, 101, 10):
        px = x_to_px(d)
        svg.append(f'<line x1="{px}" y1="{margin_top}" x2="{px}" y2="{margin_top + plot_height}" class="grid-line"/>')
        svg.append(f'<line x1="{px}" y1="{margin_top + plot_height}" x2="{px}" y2="{margin_top + plot_height + 6}" stroke="#475569" stroke-width="1.5"/>')
        svg.append(f'<text x="{px}" y="{margin_top + plot_height + 22}" class="tick-label">{d}</text>')

    # Y-Ticks (Speed % on Left, PWM on Right)
    for pct in range(0, 101, 20):
        py = y_to_px(pct)
        pwm = int(round(pct * 2.55))
        svg.append(f'<line x1="{margin_left}" y1="{py}" x2="{margin_left + plot_width}" y2="{py}" class="grid-line"/>')
        svg.append(f'<line x1="{margin_left - 6}" y1="{py}" x2="{margin_left}" y2="{py}" stroke="#475569" stroke-width="1.5"/>')
        svg.append(f'<text x="{margin_left - 12}" y="{py + 4}" class="y-tick-label">{pct}%</text>')
        # Right Axis PWM
        svg.append(f'<line x1="{margin_left + plot_width}" y1="{py}" x2="{margin_left + plot_width + 6}" stroke="#64748b" stroke-width="1.5"/>')
        svg.append(f'<text x="{margin_left + plot_width + 12}" y="{py + 4}" class="y2-tick-label">{pwm}</text>')

    # Axis Labels
    svg.append(f'<text x="{margin_left + plot_width/2}" y="{height - 20}" class="axis-label" text-anchor="middle">Obstacle Distance d (cm)</text>')
    svg.append(f'<text x="24" y="{margin_top + plot_height/2}" class="axis-label" text-anchor="middle" transform="rotate(-90 24 {margin_top + plot_height/2})">Motor Speed v (%)</text>')
    svg.append(f'<text x="{width - 20}" y="{margin_top + plot_height/2}" class="axis-label" text-anchor="middle" transform="rotate(90 {width - 20} {margin_top + plot_height/2})">PWM Output (0 - 255)</text>')

    # Safety Zone Shading (< 10 cm)
    safe_w = x_to_px(10) - margin_left
    svg.append(f'<rect x="{margin_left}" y="{margin_top}" width="{safe_w}" height="{plot_height}" fill="#fecaca" opacity="0.6"/>')
    svg.append(f'<text x="{margin_left + safe_w/2}" y="{margin_top + plot_height/2 - 20}" font-size="12" font-weight="bold" fill="#991b1b" text-anchor="middle" transform="rotate(-90 {margin_left + safe_w/2} {margin_top + plot_height/2 - 20})">HARD SAFETY STOP</text>')
    svg.append(f'<text x="{margin_left + safe_w/2}" y="{margin_top + plot_height - 15}" font-size="11" font-weight="bold" fill="#b91c1c" text-anchor="middle">&lt; 10 cm</text>')

    # Sample Points for Fuzzy Curve
    fuzzy_points = []
    # From 10 to 100 cm
    for i in range(100, 1001):
        d_val = i / 10.0
        res = FuzzyLogicController.compute(d_val)
        fuzzy_points.append((d_val, res.speed_percent))

    # Curve Polyline
    pts_str = " ".join([f"{x_to_px(d):.1f},{y_to_px(sp):.1f}" for d, sp in fuzzy_points])
    # Full polygon including safety baseline
    poly_str = f"{x_to_px(0)},{y_to_px(0)} {x_to_px(10)},{y_to_px(0)} " + pts_str + f" {x_to_px(100)},{y_to_px(0)}"
    svg.append(f'<polygon points="{poly_str}" fill="url(#curveGrad)"/>')

    # Crisp Step Curve (Bang-bang control: 0% < 20cm, 100% >= 20cm)
    crisp_path = f"M {x_to_px(0)},{y_to_px(0)} L {x_to_px(20)},{y_to_px(0)} L {x_to_px(20)},{y_to_px(100)} L {x_to_px(100)},{y_to_px(100)}"
    svg.append(f'<path d="{crisp_path}" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="6,6"/>')

    # Fuzzy Curve Line
    svg.append(f'<path d="M {x_to_px(0)},{y_to_px(0)} L {x_to_px(10)},{y_to_px(0)} L ' + ' L '.join([f"{x_to_px(d):.1f},{y_to_px(sp):.1f}" for d, sp in fuzzy_points]) + '" fill="none" stroke="#4f46e5" stroke-width="3.5" stroke-linecap="round"/>')

    # Highlight Test Distances: 5, 20, 25, 35, 50, 70, 90 cm
    test_d_list = [5.0, 20.0, 25.0, 35.0, 50.0, 70.0, 90.0]
    for td in test_d_list:
        r = FuzzyLogicController.compute(td)
        px = x_to_px(td)
        py = y_to_px(r.speed_percent)
        svg.append(f'<circle cx="{px}" cy="{py}" r="5" fill="#4f46e5" stroke="#ffffff" stroke-width="2"/>')
        # Label
        offset_y = -12 if td != 20 else 18
        svg.append(f'<text x="{px}" y="{py + offset_y}" font-size="11" font-weight="bold" fill="#312e81" text-anchor="middle">{r.speed_percent:.1f}%</text>')

    # Legend at bottom right
    leg_x = width - margin_right - 350
    leg_y = margin_top + plot_height - 110
    svg.append(f'''
      <rect x="{leg_x}" y="{leg_y}" width="330" height="95" rx="8" fill="#ffffff" fill-opacity="0.95" stroke="#cbd5e1" stroke-width="1"/>
      <line x1="{leg_x + 15}" y1="{leg_y + 25}" x2="{leg_x + 50}" y2="{leg_y + 25}" stroke="#4f46e5" stroke-width="3.5"/>
      <text x="{leg_x + 60}" y="{leg_y + 29}" class="legend-text">Fuzzy Logic Control (Smooth Deceleration)</text>
      
      <line x1="{leg_x + 15}" y1="{leg_y + 55}" x2="{leg_x + 50}" y2="{leg_y + 55}" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="6,6"/>
      <text x="{leg_x + 60}" y="{leg_y + 59}" class="legend-text">Crisp Bang-Bang Control (Jerky Step)</text>
      
      <rect x="{leg_x + 15}" y="{leg_y + 73}" width="35" height="12" fill="#fecaca" stroke="#b91c1c" stroke-width="1"/>
      <text x="{leg_x + 60}" y="{leg_y + 83}" font-size="11" fill="#7f1d1d">Emergency Cutoff Zone (&lt; 10 cm)</text>
    ''')

    svg.append('</svg>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
    print(f"Generated: {filepath}")


def create_system_block_diagram_svg(filepath: str):
    width = 960
    height = 420

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<defs>')
    svg.append('''
      <style>
        .diag-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 20px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
        .box-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: bold; fill: #ffffff; text-anchor: middle; }
        .box-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; fill: #f1f5f9; text-anchor: middle; }
        .conn-label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; font-weight: 600; fill: #334155; text-anchor: middle; }
        .flc-boundary { stroke: #6366f1; stroke-width: 2; stroke-dasharray: 6,6; fill: #eef2ff; fill-opacity: 0.5; }
      </style>
      <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155"/>
      </marker>
      <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#4f46e5"/>
      </marker>
    ''')
    svg.append('</defs>')

    # Background
    svg.append(f'<rect width="{width}" height="{height}" fill="#ffffff" rx="12"/>')
    svg.append(f'<text x="{width/2}" y="36" class="diag-title">System Block Diagram: Closed-Loop Fuzzy Logic Robot Speed Control</text>')

    # FLC Boundary Box
    svg.append('<rect x="180" y="70" width="460" height="220" rx="10" class="flc-boundary"/>')
    svg.append('<text x="410" y="92" font-family="sans-serif" font-size="13" font-weight="bold" fill="#4338ca" text-anchor="middle">FUZZY LOGIC CONTROLLER (FLC) ENGINE (ESP32 / Arduino Uno)</text>')

    # Stage 1: HC-SR04 Sensor Box
    svg.append('''
      <rect x="25" y="140" width="125" height="85" rx="8" fill="#0284c7" stroke="#0369a1" stroke-width="2"/>
      <text x="87" y="170" class="box-title">HC-SR04</text>
      <text x="87" y="190" class="box-sub">Ultrasonic</text>
      <text x="87" y="206" class="box-sub">Sensor (2-400cm)</text>
    ''')

    # Arrow 1: Sensor to Fuzzifier
    svg.append('''
      <line x1="150" y1="182" x2="200" y2="182" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>
      <text x="175" y="172" class="conn-label">Distance d</text>
    ''')

    # Inside FLC 1: Fuzzifier
    svg.append('''
      <rect x="205" y="140" width="125" height="85" rx="8" fill="#4f46e5" stroke="#3730a3" stroke-width="2"/>
      <text x="267" y="168" class="box-title">Fuzzifier</text>
      <text x="267" y="188" class="box-sub">Triangular MFs</text>
      <text x="267" y="204" class="box-sub">Near, Med, Far</text>
    ''')

    # Arrow 2: Fuzzifier to Rule Base
    svg.append('''
      <line x1="330" y1="182" x2="370" y2="182" stroke="#4f46e5" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
      <text x="350" y="165" class="conn-label">μ_Near, μ_Med</text>
      <text x="350" y="177" class="conn-label">μ_Far</text>
    ''')

    # Inside FLC 2: Rule Base
    svg.append('''
      <rect x="375" y="140" width="125" height="85" rx="8" fill="#6366f1" stroke="#4338ca" stroke-width="2"/>
      <text x="437" y="168" class="box-title">Rule Base</text>
      <text x="437" y="188" class="box-sub">Mamdani Rules</text>
      <text x="437" y="204" class="box-sub">(R1, R2, R3)</text>
    ''')

    # Arrow 3: Rule Base to Defuzzifier
    svg.append('''
      <line x1="500" y1="182" x2="540" y2="182" stroke="#4f46e5" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
      <text x="520" y="172" class="conn-label">Rule Fires</text>
    ''')

    # Inside FLC 3: Defuzzifier
    svg.append('''
      <rect x="545" y="140" width="125" height="85" rx="8" fill="#4f46e5" stroke="#3730a3" stroke-width="2"/>
      <text x="607" y="168" class="box-title">Defuzzifier</text>
      <text x="607" y="188" class="box-sub">Weighted Avg /</text>
      <text x="607" y="204" class="box-sub">Centroid (v_out)</text>
    ''')

    # Arrow 4: FLC to L298N
    svg.append('''
      <line x1="670" y1="182" x2="720" y2="182" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>
      <text x="695" y="170" class="conn-label">PWM</text>
      <text x="695" y="196" class="conn-label">(0 - 255)</text>
    ''')

    # Stage 5: L298N Motor Driver
    svg.append('''
      <rect x="725" y="140" width="105" height="85" rx="8" fill="#d97706" stroke="#b45309" stroke-width="2"/>
      <text x="777" y="168" class="box-title">L298N</text>
      <text x="777" y="188" class="box-sub">Dual H-Bridge</text>
      <text x="777" y="204" class="box-sub">Motor Driver</text>
    ''')

    # Arrow 5: L298N to Motors
    svg.append('''
      <line x1="830" y1="182" x2="865" y2="182" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow)"/>
    ''')

    # Stage 6: DC Geared Motors
    svg.append('''
      <rect x="870" y="140" width="75" height="85" rx="8" fill="#15803d" stroke="#166534" stroke-width="2"/>
      <text x="907" y="168" class="box-title">DC</text>
      <text x="907" y="188" class="box-sub">Geared</text>
      <text x="907" y="204" class="box-sub">Motors</text>
    ''')

    # Environmental Feedback Loop
    svg.append('''
      <path d="M 907 225 L 907 340 L 87 340 L 87 225" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="6,6" marker-end="url(#arrow)"/>
      <rect x="370" y="325" width="220" height="30" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
      <text x="480" y="345" font-family="sans-serif" font-size="12" font-weight="600" fill="#475569" text-anchor="middle">Physical Robot Movement &amp; Obstacle Range</text>
    ''')

    svg.append('</svg>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
    print(f"Generated: {filepath}")


def convert_svgs_to_png():
    """Converts SVGs to high-resolution PNGs using ImageMagick."""
    svg_files = [
        ("images/membership_functions.svg", "images/membership_functions.png"),
        ("images/flc_speed_response_curve.svg", "images/flc_speed_response_curve.png"),
        ("images/system_block_diagram.svg", "images/system_block_diagram.png")
    ]
    for svg_f, png_f in svg_files:
        try:
            res = subprocess.run(["convert", "-density", "200", svg_f, png_f], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"Converted {svg_f} -> {png_f}")
            else:
                print(f"Convert warning for {svg_f}: {res.stderr}")
        except Exception as e:
            print(f"Error converting {svg_f}: {e}")


if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)
    create_membership_functions_svg("images/membership_functions.svg")
    create_flc_response_curve_svg("images/flc_speed_response_curve.svg")
    create_system_block_diagram_svg("images/system_block_diagram.svg")
    convert_svgs_to_png()
