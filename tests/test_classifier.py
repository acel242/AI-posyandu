import sys
sys.path.insert(0, 'backend')
from classifier import classify_bb_tb


def test_normal_stunting():
    """2 tahun 男, 85cm, 12kg — normal green"""
    result = classify_bb_tb(age_months=24, gender="L", weight_kg=12, height_cm=85)
    assert result["status"] == "green"
    assert result["category"] == "Normal"


def test_moderate_stunting():
    """2 tahun 女, 78cm, 11kg — yellow/gizi kurang"""
    result = classify_bb_tb(age_months=24, gender="P", weight_kg=11, height_cm=78)
    assert result["status"] == "yellow"


def test_severe_stunting():
    """2 tahun 男, 70cm, 9kg — red/gizi buruk"""
    result = classify_bb_tb(age_months=24, gender="L", weight_kg=9, height_cm=70)
    assert result["status"] == "red"


def test_edge_normal():
    """Presis normal boundary"""
    result = classify_bb_tb(age_months=24, gender="L", weight_kg=11.5, height_cm=87)
    assert result["status"] == "green"
