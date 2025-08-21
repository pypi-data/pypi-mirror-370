import os
import pytest
import pandas as pd
from dotenv import load_dotenv

from ocfinance.scraper.cryptoquant import _download, _create_dataframe

load_dotenv()

email = os.getenv('CRYPTOQUANT_EMAIL')
password = os.getenv('CRYPTOQUANT_PASSWORD')

@pytest.fixture
def sample_results():
    return [
        ['2023-01-01', 100],
        ['2023-01-02', 200],
        ['2023-01-03', 300]
    ]

@pytest.fixture
def sample_columns():
    return ['day', 'value']

def test_download_missing_credentials():
    with pytest.raises(TypeError, match="Email and/or password hasn't been passed"):
        _download('https://cryptoquant.com/some/path/123')

def test_download_unsupported_url():
    with pytest.raises(NotImplementedError, match="Only third party metrics on cryptoquant have been implemented."):
        _download('https://cryptoquant.com/asset/some/path/123', email='test@example.com', password='password123')

def test_create_dataframe(sample_results, sample_columns):
    expected_df = pd.DataFrame({
        'value': [100, 200, 300]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))
    expected_df.index.name = 'Date'

    df = _create_dataframe(sample_results, sample_columns)

    pd.testing.assert_frame_equal(df, expected_df)

@pytest.mark.skipif(not email or not password, reason="Skipping cryptoquant integration tests: Email and/or password not provided.")
@pytest.mark.parametrize("url, expected_columns", [
    (
        "https://cryptoquant.com/analytics/query/66636764d376670a9fe4c3f4?v=66636764d376670a9fe4c3f6",
        ['avg_daily_price', 'avg_daily_realized_profit', 'avg_daily_realized_loss', 'sma_30d_realized_profit', 'sma_30d_realized_loss', 'ratio_30d_realized_profit_loss', 'Low_Liquidity']
    ),
    (
        "https://cryptoquant.com/analytics/query/6463b524885a7d37a1630f8b?v=6463f8c9fb92892124bd5864",
        ['Price', 'Adjusted_MVRV', 'mvrv', 'oversold', 'overbought']
    )
])
def test_cryptoquant(url, expected_columns):
    data = _download(url, email=email, password=password)

    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)
    assert all(data.dtypes == float)

    assert all(col in data.columns for col in expected_columns)
