import os
from typing import Dict, List, Optional, Union

import pandas as pd
import pytest

from toronto_open_data import TorontoOpenData

# Run only when explicitly enabled to avoid network in CI
pytestmark = pytest.mark.skipif(
    os.environ.get("TOD_INTEGRATION") != "1",
    reason=("Set TOD_INTEGRATION=1 to run live integration tests against Toronto Open Data"),
)

# Dataset slugs from the portal
DATASET_SLUGS: List[str] = [
    "properties-requiring-a-cultural-heritage-evaluation-report-under-opa-720",
    "toronto-population-health-status-indicators",
    "neighbourhood-intensification-estimates-to-2051",
]

# Simple queries derived from titles to exercise search
SEARCH_QUERIES: List[str] = [
    "cultural heritage evaluation",
    "population health status indicators",
    "neighbourhood intensification",
]


@pytest.fixture(scope="module")
def tod() -> TorontoOpenData:
    return TorontoOpenData()


@pytest.mark.integration
def test_search_datasets_returns_dataframe(tod: TorontoOpenData) -> None:
    for query in SEARCH_QUERIES:
        result = tod.search_datasets(query, as_frame=True)
        assert isinstance(result, pd.DataFrame)


@pytest.mark.integration
def test_get_dataset_resources_handles_retired_or_missing(tod: TorontoOpenData) -> None:
    for slug in DATASET_SLUGS:
        # as_frame=True
        df_or_none = tod.search_resources_by_name(slug, as_frame=True)
        assert df_or_none is None or isinstance(df_or_none, pd.DataFrame)

        # as_frame=False
        list_or_none: Optional[Union[List[Dict], None]] = tod.search_resources_by_name(slug, as_frame=False)
        assert list_or_none is None or isinstance(list_or_none, list)


@pytest.mark.integration
def test_get_dataset_info_no_exception(tod: TorontoOpenData) -> None:
    for slug in DATASET_SLUGS:
        info = tod.get_dataset_info(slug)
        assert info is None or isinstance(info, dict)
