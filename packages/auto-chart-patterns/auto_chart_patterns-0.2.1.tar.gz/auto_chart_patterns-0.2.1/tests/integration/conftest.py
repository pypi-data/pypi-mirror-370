import pytest
from .helpers import scan_properties_fp, zigzag_fp, scan_properties_tl, zigzag_tl, \
    scan_properties_rp, zigzag_rp, zigzag_rsi, scan_properties_rsi

@pytest.fixture
def tickers():
    return ["BTCUSDT", "SOLUSDT", "ETHUSDT", "AVAXUSDT", "DOGEUSDT", "SHIBUSDT"]

@pytest.fixture
def default_properties_flags_pennants():
    return scan_properties_fp

@pytest.fixture
def zigzag_flags_pennants():
    return zigzag_fp

@pytest.fixture
def default_properties_trend_lines():
    return scan_properties_tl

@pytest.fixture
def zigzag_trend_lines():
    return zigzag_tl

@pytest.fixture
def default_properties_reversals():
    return scan_properties_rp

@pytest.fixture
def zigzag_reversals():
    return zigzag_rp

@pytest.fixture
def default_properties_rsi_divergences():
    return scan_properties_rsi

@pytest.fixture
def zigzag_rsi_divergences():
    return zigzag_rsi