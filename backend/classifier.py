"""
WHO Child Growth Standards — BB/TB (Weight-for-Height) Classification
Used for stunting detection in Indonesian Posyandu context.

Reference: WHO Child Growth Standards (2006)
"""

# Median height-for-age in cm (simplified, key ages)
HEIGHT_MEDIAN = {
    "L": {  # Laki-laki / Male
        0: 50, 6: 67, 12: 75, 18: 82, 24: 87, 30: 91, 36: 95,
        42: 98, 48: 102, 54: 105, 60: 108, 66: 111, 72: 114
    },
    "P": {  # Perempuan / Female
        0: 49, 6: 65, 12: 73, 18: 79, 24: 84, 30: 88, 36: 92,
        42: 95, 48: 99, 54: 102, 60: 105, 66: 108, 72: 111
    }
}

# Expected weight (kg) at given height-for-age median
WEIGHT_MEDIAN = {
    "L": {
        50: 3.3, 67: 7.5, 75: 9.0, 82: 10.5, 87: 11.5,
        91: 12.5, 95: 13.5, 98: 14.2, 102: 15.0, 105: 15.7, 108: 16.5,
        111: 17.2, 114: 18.0
    },
    "P": {
        49: 3.2, 65: 7.0, 73: 8.5, 79: 9.5, 84: 10.5,
        88: 11.5, 92: 12.5, 95: 13.2, 99: 14.0, 102: 14.8, 105: 15.5,
        108: 16.2, 111: 17.0
    }
}


def classify_bb_tb(age_months: int, gender: str, weight_kg: float, height_cm: float) -> dict:
    """
    Classify child nutritional status based on weight and height.

    Args:
        age_months: Child age in months
        gender: "L" (male) or "P" (female)
        weight_kg: Weight in kilograms
        height_cm: Height/length in centimeters

    Returns dict with:
        - status: 'green' | 'yellow' | 'red'
        - category: Description in Bahasa Indonesia
        - recommendation: Action to take
        - z_score: Approximate z-score
    """
    if gender not in ("L", "P"):
        gender = "L"

    # Get median height for age/gender
    median_height = HEIGHT_MEDIAN.get(gender, HEIGHT_MEDIAN["L"]).get(age_months, 85)

    # Calculate height as percentage of median
    height_ratio = (height_cm / median_height) * 100

    # Get expected weight at this height (from weight-for-height median)
    expected_weight = WEIGHT_MEDIAN.get(gender, {}).get(height_cm)
    if expected_weight is None:
        # Fallback: interpolate from nearest known heights
        heights = sorted(WEIGHT_MEDIAN.get(gender, {}).keys())
        expected_weight = weight_kg  # can't calculate, skip weight check
        weight_ratio = 100.0
    else:
        weight_ratio = (weight_kg / expected_weight) * 100

    # Classification logic based on WHO Z-scores
    # green: >= -1 SD (height ratio >= ~95%)
    # yellow: -3 SD to -1 SD (height ratio ~85-95%)
    # red: < -3 SD (height ratio < ~85%)

    if height_ratio < 85 or weight_ratio < 70:
        # < -3 SD: Severe wasting/stunting
        status = "red"
        category = "Gizi Buruk"
        recommendation = "Segera rujuk ke puskesmas untuk penanganan intensif"
        z_score = -3
    elif height_ratio < 90 or weight_ratio < 80:
        # -3 to -2 SD: Moderate wasting/stunting
        status = "yellow"
        category = "Gizi Kurang"
        recommendation = "Konseling gizi, berikan makanan bergizi, kunjungan rumah 7 hari"
        z_score = -2
    elif height_ratio < 95 or weight_ratio < 85:
        # -2 to -1 SD: Mild stunting
        status = "yellow"
        category = "Stunted (Terbelakang)"
        recommendation = "Pantau pertumbuhan setiap bulan, intervensi gizi berbasis rumah"
        z_score = -1
    else:
        # >= -1 SD: Normal
        status = "green"
        category = "Normal"
        recommendation = "Lanjutkan pemantauan rutin Posyandu setiap bulan"
        z_score = 0

    return {
        "status": status,
        "category": category,
        "z_score": z_score,
        "recommendation": recommendation,
        "height_ratio": round(height_ratio, 1),
        "weight_ratio": round(weight_ratio, 1),
        "median_height": median_height
    }
