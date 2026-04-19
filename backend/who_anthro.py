"""
WHO Anthro Calculator — Z-score calculation for child growth assessment
Based on WHO Growth Reference 2007 (0-5 years)
Uses LMS method: Z = ((Y/M)^L - 1) / (L*S) when L != 0
"""

from datetime import date
from typing import Optional, Tuple

# WHO LMS parameters for Weight-for-Age (boys & girls 0-5 years, in months)
# Format: {age_months: (L, M, S)}
# Source: WHO Growth Reference 2007

WFA_BOY = {
    0: (0.3487, 3.3464, 0.14602),
    1: (0.2297, 4.4709, 0.13395),
    2: (0.1970, 5.5675, 0.12385),
    3: (0.1738, 6.3762, 0.11727),
    4: (0.1553, 7.0023, 0.11310),
    5: (0.1395, 7.5105, 0.10974),
    6: (0.1257, 7.9340, 0.10696),
    7: (0.1134, 8.2970, 0.10460),
    8: (0.1021, 8.6151, 0.10255),
    9: (0.0917, 8.9014, 0.10072),
    10: (0.0822, 9.1647, 0.09906),
    11: (0.0734, 9.4122, 0.09755),
    12: (0.0653, 9.6478, 0.09615),
    18: (0.0360, 10.8479, 0.09044),
    24: (0.0119, 11.9934, 0.08644),
    30: (-0.0068, 13.0796, 0.08362),
    36: (-0.0220, 14.1306, 0.08140),
    42: (-0.0346, 15.1672, 0.07968),
    48: (-0.0453, 16.2077, 0.07825),
    54: (-0.0545, 17.2670, 0.07712),
    60: (-0.0625, 18.3465, 0.07623),
}

WFA_GIRL = {
    0: (0.3809, 3.1822, 0.14171),
    1: (0.1710, 4.1871, 0.13727),
    2: (0.0962, 5.0860, 0.12995),
    3: (0.0401, 5.8458, 0.12485),
    4: (-0.0054, 6.5087, 0.12154),
    5: (-0.0436, 7.1030, 0.11900),
    6: (-0.0764, 7.6474, 0.11676),
    7: (-0.1047, 8.1539, 0.11480),
    8: (-0.1294, 8.6345, 0.11306),
    9: (-0.1507, 9.0970, 0.11150),
    10: (-0.1690, 9.5492, 0.11010),
    11: (-0.1846, 9.9954, 0.10883),
    12: (-0.1981, 10.4410, 0.10767),
    18: (-0.2551, 12.2336, 0.10344),
    24: (-0.2997, 13.9439, 0.10070),
    30: (-0.3367, 15.6062, 0.09876),
    36: (-0.3681, 17.2502, 0.09733),
    42: (-0.3952, 18.9018, 0.09626),
    48: (-0.4187, 20.5767, 0.09543),
    54: (-0.4390, 22.2832, 0.09477),
    60: (-0.4568, 24.0293, 0.09423),
}

# WHO LMS for Height-for-Age (0-5 years)
HFA_BOY = {
    0: (1.0, 49.8842, 0.03795),
    3: (1.0, 61.4259, 0.03057),
    6: (1.0, 67.6236, 0.02744),
    9: (1.0, 72.1377, 0.02539),
    12: (1.0, 75.7488, 0.02394),
    18: (1.0, 82.2964, 0.02207),
    24: (1.0, 87.8161, 0.02090),
    30: (1.0, 92.8873, 0.02023),
    36: (1.0, 97.6858, 0.01985),
    42: (1.0, 102.2966, 0.01970),
    48: (1.0, 106.7749, 0.01972),
    54: (1.0, 111.1604, 0.01984),
    60: (1.0, 115.4834, 0.02001),
}

HFA_GIRL = {
    0: (1.0, 49.1477, 0.03730),
    3: (1.0, 60.2463, 0.02981),
    6: (1.0, 66.1791, 0.02679),
    9: (1.0, 70.5564, 0.02484),
    12: (1.0, 74.0758, 0.02339),
    18: (1.0, 80.6588, 0.02164),
    24: (1.0, 86.4166, 0.02056),
    30: (1.0, 91.4505, 0.01997),
    36: (1.0, 96.0831, 0.01958),
    42: (1.0, 100.5471, 0.01941),
    48: (1.0, 104.8714, 0.01941),
    54: (1.0, 109.0939, 0.01954),
    60: (1.0, 113.2416, 0.01974),
}

# WHO LMS for Weight-for-Height (0-5 years, length/height in cm)
# Selected key percentiles for interpolation
WFH_BOY_L = {
    45: (0.3139, 2.2411, 0.12028),
    50: (0.1929, 2.8854, 0.11424),
    55: (0.0963, 3.5824, 0.11024),
    60: (0.0392, 4.2957, 0.10776),
    65: (-0.0031, 5.0029, 0.10615),
    70: (-0.0343, 5.6817, 0.10511),
    75: (-0.0570, 6.3175, 0.10447),
    80: (-0.0730, 6.9089, 0.10412),
    85: (-0.0838, 7.4696, 0.10397),
    90: (-0.0905, 8.0175, 0.10400),
    95: (-0.0943, 8.5656, 0.10418),
    100: (-0.0959, 9.1261, 0.10451),
    105: (-0.0959, 9.7093, 0.10499),
    110: (-0.0945, 10.3267, 0.10564),
    115: (-0.0919, 10.9846, 0.10649),
}

WFH_GIRL_L = {
    45: (0.4252, 2.2193, 0.11891),
    50: (0.3477, 2.8193, 0.11395),
    55: (0.2760, 3.4735, 0.11062),
    60: (0.2291, 4.1244, 0.10835),
    65: (0.1932, 4.7613, 0.10674),
    70: (0.1635, 5.3713, 0.10559),
    75: (0.1374, 5.9568, 0.10478),
    80: (0.1136, 6.5295, 0.10422),
    85: (0.0916, 7.1022, 0.10387),
    90: (0.0713, 7.6868, 0.10370),
    95: (0.0524, 8.2903, 0.10372),
    100: (0.0348, 8.9192, 0.10394),
    105: (0.0184, 9.5787, 0.10438),
    110: (0.0031, 10.2723, 0.10507),
    115: (-0.0111, 11.0047, 0.10604),
}


def _interpolate_lms(table: dict, x: float) -> Tuple[float, float, float]:
    """Interpolate LMS values for a given x (age or height)."""
    keys = sorted(table.keys())
    if x <= keys[0]:
        return table[keys[0]]
    if x >= keys[-1]:
        return table[keys[-1]]
    for i in range(len(keys) - 1):
        x0, x1 = keys[i], keys[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            L0, M0, S0 = table[x0]
            L1, M1, S1 = table[x1]
            return (L0 + t * (L1 - L0), M0 + t * (M1 - M0), S0 + t * (S1 - S0))
    return table[keys[-1]]


def _calc_zscore(y: float, L: float, M: float, S: float) -> float:
    """Calculate z-score using WHO LMS formula."""
    if y is None or y <= 0:
        return None
    if M <= 0:
        return None
    if L == 0:
        import math
        return math.log(y / M) / S
    z = ((y / M) ** L - 1) / (L * S)
    return round(z, 2)


def calculate_age_in_months(dob: str, measurement_date: str) -> float:
    """Calculate age in months from date strings (YYYY-MM-DD)."""
    from datetime import datetime
    d1 = datetime.strptime(dob, "%Y-%m-%d")
    d2 = datetime.strptime(measurement_date, "%Y-%m-%d")
    delta = d2 - d1
    return delta.days / 30.436875


def classify_zscore(z: float) -> str:
    """Classify z-score into green/yellow/red."""
    if z is None:
        return "unmeasured"
    if z >= -1:
        return "green"
    elif z >= -2:
        return "yellow"
    else:
        return "red"


def calc_zscore_weight_for_age(weight_kg: float, age_months: float, gender: str) -> Optional[float]:
    """Calculate Weight-for-Age z-score. gender: 'L' (boy) or 'P' (girl)."""
    table = WFA_BOY if gender == "L" else WFA_GIRL
    L, M, S = _interpolate_lms(table, age_months)
    return _calc_zscore(weight_kg, L, M, S)


def calc_zscore_height_for_age(height_cm: float, age_months: float, gender: str) -> Optional[float]:
    """Calculate Height-for-Age z-score."""
    table = HFA_BOY if gender == "L" else HFA_GIRL
    L, M, S = _interpolate_lms(table, age_months)
    return _calc_zscore(height_cm, L, M, S)


def calc_zscore_weight_for_height(weight_kg: float, height_cm: float, gender: str) -> Optional[float]:
    """Calculate Weight-for-Height z-score."""
    table = WFH_BOY_L if gender == "L" else WFH_GIRL_L
    # Height must be in cm range of table
    L, M, S = _interpolate_lms(table, height_cm)
    return _calc_zscore(weight_kg, L, M, S)


def classify_overall(weight_kg: float, height_cm: float, age_months: float, gender: str) -> str:
    """Overall risk classification based on all three indicators."""
    results = []
    if weight_kg and age_months:
        z_wfa = calc_zscore_weight_for_age(weight_kg, age_months, gender)
        if z_wfa is not None:
            results.append(z_wfa)
    if height_cm and age_months:
        z_hfa = calc_zscore_height_for_age(height_cm, age_months, gender)
        if z_hfa is not None:
            results.append(z_hfa)
    if weight_kg and height_cm:
        z_wfh = calc_zscore_weight_for_height(weight_kg, height_cm, gender)
        if z_wfh is not None:
            results.append(z_wfh)
    if not results:
        return "unmeasured"
    avg = sum(results) / len(results)
    return classify_zscore(avg)


def get_who_reference_data(indicator: str, gender: str, age_months: float = None, height_cm: float = None) -> dict:
    """Get WHO reference curve data points for charting.
    
    indicator: 'wfa' | 'hfa' | 'wfh'
    """
    if indicator == "wfa":
        table = WFA_BOY if gender == "L" else WFA_GIRL
        data = {}
        for mo in range(0, 61):
            L, M, S = _interpolate_lms(table, mo)
            data[mo] = {
                "age_months": mo,
                "median": round(M, 1),
                "sd_minus_1": round(_calc_zscore(M * (1 - S) ** (1/L) if L != 0 else M * (1 - S * L), L, M, S) if L != 0 else round(M * math.exp(-S), 1) if False else round(M * (1 - S), 1), 1),
                "sd_minus_2": round(_interpolate_lms(table, mo)[1] * 0.87, 1),  # rough
                "sd_minus_3": round(_interpolate_lms(table, mo)[1] * 0.80, 1),
            }
        return data
    
    elif indicator == "hfa":
        table = HFA_BOY if gender == "L" else HFA_GIRL
        data = {}
        for mo in range(0, 61):
            L, M, S = _interpolate_lms(table, mo)
            data[mo] = {
                "age_months": mo,
                "median": round(M, 1),
                "sd_minus_1": round(M - S * L * ((1 - S) ** (1/L) - 1) / (L * S) if L != 0 else round(M - S, 1), 1),
            }
        return data
    
    return {}
