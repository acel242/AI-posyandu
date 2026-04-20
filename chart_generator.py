"""
Growth Chart Generator — PNG charts for Telegram / API responses
Uses WHO LMS data from who_anthro.py
"""

import io
import math
from datetime import datetime
from typing import List, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from who_anthro import (
    WFA_BOY, WFA_GIRL,
    HFA_BOY, HFA_GIRL,
    WFH_BOY_L, WFH_GIRL_L,
    _interpolate_lms, _calc_zscore,
    calculate_age_in_months,
    calc_zscore_weight_for_age,
    calc_zscore_height_for_age,
    calc_zscore_weight_for_height,
    classify_zscore,
)


# WHO reference percentiles (approximated from WHO tables)
def _get_wfa_points(gender: str, age_months_range: range):
    """Get WHO weight-for-age reference points."""
    table = WFA_BOY if gender == "L" else WFA_GIRL
    points = []
    for mo in age_months_range:
        L, M, S = _interpolate_lms(table, mo)
        points.append((mo, M))
    return points


def _get_hfa_points(gender: str, age_months_range: range):
    """Get WHO height-for-age reference points."""
    table = HFA_BOY if gender == "L" else HFA_GIRL
    points = []
    for mo in age_months_range:
        L, M, S = _interpolate_lms(table, mo)
        points.append((mo, M))
    return points


def _get_wfh_points(gender: str, height_range: range):
    """Get WHO weight-for-height reference points."""
    table = WFH_BOY_L if gender == "L" else WFH_GIRL_L
    points = []
    for h in height_range:
        if h < 45 or h > 120:
            continue
        L, M, S = _interpolate_lms(table, h)
        points.append((h, M))
    return points


def _build_sd_lines(points, sd: int = -2):
    """Build +/- SD reference lines from median points."""
    if sd == 0:
        return [p[1] for p in points]
    factor = 1 - sd * 0.1  # rough approximation for WHO bands
    return [p[1] * factor for p in points]


def generate_growth_chart_png(
    child_name: str,
    gender: str,
    measurements: List[dict],
    chart_type: str = "wfa",  # wfa | hfa | wfh
    width_px: int = 800,
    height_px: int = 480,
) -> bytes:
    """
    Generate a growth chart PNG.
    
    measurements: list of {date, weight_kg, height_cm, age_months}
    chart_type: 'wfa' (weight-for-age) or 'hfa' (height-for-age)
    """
    dpi = 100
    width_in = width_px / dpi
    height_in = height_px / dpi
    
    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
    
    # Background
    fig.patch.set_facecolor('#f8fffe')
    ax.set_facecolor('#f8fffe')
    
    # Determine x-axis (age in months)
    if chart_type == "wfa":
        xlabel = "Umur (bulan)"
        ylabel = "Berat (kg)"
        title = f"📊 Grafik Pertumbuhan: {child_name} (Berat per Umur)"
        x_key = "age_months"
        y_key = "weight_kg"
        ref_points = _get_wfa_points(gender, range(0, 61))
        y_min, y_max = 3, 25
        
    elif chart_type == "hfa":
        xlabel = "Umur (bulan)"
        ylabel = "Tinggi (cm)"
        title = f"📊 Grafik Pertumbuhan: {child_name} (Tinggi per Umur)"
        x_key = "age_months"
        y_key = "height_cm"
        ref_points = _get_hfa_points(gender, range(0, 61))
        y_min, y_max = 50, 125
    else:
        raise ValueError(f"Unknown chart_type: {chart_type}")
    
    # Plot WHO reference lines
    ref_x = [p[0] for p in ref_points]
    ref_y = [p[1] for p in ref_points]
    
    # Median (0 SD)
    ax.plot(ref_x, ref_y, color='#4CAF50', linewidth=1.5, linestyle='-', alpha=0.9, label='Median WHO')
    
    # Approximate +/- 1SD and +/- 2SD bands
    if ref_y:
        sd1_up = [y * 1.08 for y in ref_y]   # rough +1SD
        sd1_dn = [y * 0.92 for y in ref_y]  # rough -1SD
        sd2_dn = [y * 0.84 for y in ref_y]  # rough -2SD
        sd3_dn = [y * 0.77 for y in ref_y]  # rough -3SD
        
        ax.fill_between(ref_x, sd1_dn, sd1_up, alpha=0.12, color='#4CAF50', label='±1 SD')
        ax.fill_between(ref_x, sd2_dn, sd1_dn, alpha=0.15, color='#FFC107', label='-1SD to -2SD')
        ax.fill_between(ref_x, sd3_dn, sd2_dn, alpha=0.15, color='#F44336', label='<-2SD')
        
        ax.plot(ref_x, sd1_up, color='#4CAF50', linewidth=0.5, linestyle='--', alpha=0.5)
        ax.plot(ref_x, sd1_dn, color='#4CAF50', linewidth=0.5, linestyle='--', alpha=0.5)
        ax.plot(ref_x, sd2_dn, color='#FFC107', linewidth=0.8, linestyle='--', alpha=0.7, label='-2 SD')
        ax.plot(ref_x, sd3_dn, color='#F44336', linewidth=0.8, linestyle='--', alpha=0.7, label='-3 SD')
    
    # Plot child's measurements
    valid_pts = [(m[x_key], m[y_key]) for m in measurements if m.get(y_key) and m.get(x_key) is not None and m.get(x_key) is not None]
    if valid_pts:
        xs, ys = zip(*valid_pts)
        ax.scatter(xs, ys, color='#1565C0', s=60, zorder=5, label='Pengukuran')
        ax.plot(xs, ys, color='#1565C0', linewidth=2, zorder=4)
        
        # Color-code dots by risk
        for m in measurements:
            age = m.get(x_key)
            val = m.get(y_key)
            if age is None or val is None:
                continue
            z = calc_zscore_weight_for_age(val, age, gender) if chart_type == "wfa" else calc_zscore_height_for_age(val, age, gender)
            color = '#4CAF50' if (z and z >= -1) else '#FFC107' if (z and z >= -2) else '#F44336'
            ax.scatter([age], [val], color=color, s=60, zorder=6)
    
    # Labels and styling
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
    ax.set_ylim(y_min, y_max)
    valid_x = [m.get(x_key) for m in measurements if m.get(x_key) is not None]
    ax.set_xlim(0, max(60, max(valid_x, default=60) + 5))
    
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Legend
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9, ncol=2)
    
    # Risk summary
    if valid_pts:
        latest = measurements[-1]
        age = latest.get(x_key)
        val = latest.get(y_key)
        if age and val:
            z = calc_zscore_weight_for_age(val, age, gender) if chart_type == "wfa" else calc_zscore_height_for_age(val, age, gender)
            if z is not None:
                status = classify_zscore(z)
                emoji = "[OK]" if status == "green" else "[WARN]" if status == "yellow" else "[RISK]"
                status_text = f"Z-score: {z:.2f} {emoji} {'Normal' if status=='green' else 'Risiko' if status=='yellow' else 'Buruk'}"
                ax.text(0.98, 0.02, status_text, transform=ax.transAxes, fontsize=9,
                        ha='right', va='bottom',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf.read()


def generate_measurement_summary(measurements: List[dict], child_name: str, gender: str) -> str:
    """Generate a text summary of growth for Telegram."""
    if not measurements:
        return f"📊 {child_name}: Belum ada data pengukuran."
    
    latest = measurements[-1]
    earliest = measurements[0]
    
    age = latest.get("age_months", 0)
    weight = latest.get("weight_kg")
    height = latest.get("height_cm")
    
    z_wfa = calc_zscore_weight_for_age(weight, age, gender) if weight else None
    z_hfa = calc_zscore_height_for_age(height, age, gender) if height else None
    
    lines = [
        f"📊 *Grafik Pertumbuhan: {child_name}*",
        "",
    ]
    
    if weight:
        trend = "▲ Naik" if latest.get("weight_kg", 0) > earliest.get("weight_kg", 0) else "▼ Turun"
        lines.append(f"Weight: Berat: {earliest.get('weight_kg')}kg → {weight}kg {trend}")
    if height:
        trend = "▲ Naik" if latest.get("height_cm", 0) > earliest.get("height_cm", 0) else "▼ Turun"
        lines.append(f"Height: Tinggi: {earliest.get('height_cm')}cm → {height}cm {trend}")
    
    lines.append("")
    if z_wfa:
        status = "[OK] Normal" if z_wfa >= -1 else "[WARN] Risiko" if z_wfa >= -2 else "[RISK] Buruk"
        lines.append(f"Z-score BB/U: *{z_wfa:.2f}* {status}")
    if z_hfa:
        status = "[OK] Normal" if z_hfa >= -1 else "[WARN] Risiko" if z_hfa >= -2 else "[RISK] Buruk"
        lines.append(f"Z-score TB/U: *{z_hfa:.2f}* {status}")
    
    return "\n".join(lines)
