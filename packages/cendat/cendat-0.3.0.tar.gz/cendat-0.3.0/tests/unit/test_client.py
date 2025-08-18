# tests/test_cendat.py

import pytest
from unittest.mock import patch, Mock, ANY
import json
from pathlib import Path
from cendat import CenDatHelper, CenDatResponse

# --- 1. Mock Data ---

SIMPLE_PRODUCTS_JSON = {
    "dataset": [
        {
            "title": "American Community Survey",
            "c_isAggregate": "true",
            "c_vintage": 2022,
            "distribution": [{"accessURL": "http://api.census.gov/data/2022/acs/acs5"}],
        },
        {
            "title": "PUMS Household Data",
            "c_isMicrodata": "true",
            "c_vintage": 2022,
            "distribution": [
                {"accessURL": "http://api.census.gov/data/2022/acs/acs5/pums"}
            ],
        },
        {
            "title": "A Timeseries Dataset",  # This product should be filtered out
            "c_isAggregate": "false",
            "c_isMicrodata": "false",
            "c_vintage": 2022,
            "distribution": [
                {"accessURL": "http://api.census.gov/data/2022/timeseries"}
            ],
        },
    ]
}

FAKE_GEOS_JSON = {
    "fips": [
        {"name": "us", "geoLevelDisplay": "010", "requires": None},
        {"name": "state", "geoLevelDisplay": "040", "requires": None},
        {"name": "county", "geoLevelDisplay": "050", "requires": ["state"]},
        {"name": "tract", "geoLevelDisplay": "140", "requires": ["state", "county"]},
        {
            "name": "public use microdata area",
            "geoLevelDisplay": "795",
            "requires": ["state"],
        },
    ]
}

SIMPLE_VARIABLES_JSON = {
    "variables": {
        "B01001_001E": {"label": "Total Population", "concept": "SEX BY AGE"},
        "B19013_001E": {"label": "Median Household Income", "concept": "INCOME"},
        "PUMA": {"label": "Public Use Microdata Area Code", "concept": "GEOGRAPHY"},
    }
}


# --- 2. Pytest Fixtures ---
@pytest.fixture
def cdh():
    """Returns a fresh CenDatHelper instance for each test."""
    return CenDatHelper()


@pytest.fixture
def sample_response():
    """Returns a pre-populated CenDatResponse object for testing its methods."""
    data = [
        {
            "product": "Product A",
            "vintage": [2022],
            "sumlev": "040",
            "desc": "state",
            "schema": ["NAME", "POP"],
            "data": [["Alabama", "5000000"], ["Alaska", "700000"]],
        },
        {
            "product": "Product B",
            "vintage": [2022],
            "sumlev": "050",
            "desc": "county",
            "schema": ["NAME", "POP"],
            "data": [["Autauga County", "58000"]],
        },
    ]
    return CenDatResponse(data)


# --- 3. Test Functions ---


@pytest.mark.unit
@patch("cendat.client.requests.get")
def test_list_products_filters_unsupported_types(mock_get, cdh):
    mock_response = Mock()
    mock_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_get.return_value = mock_response
    products = cdh.list_products()
    assert len(products) == 2  # Should include aggregate and microdata
    assert products[0]["title"] == "American Community Survey (2022/acs/acs5)"
    assert products[1]["title"] == "PUMS Household Data (2022/acs/acs5/pums)"


@pytest.mark.unit
@patch("cendat.client.requests.get")
def test_list_variables_with_patterns_and_logic(mock_get, cdh):
    """Tests that the search and filter parameters work correctly."""
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON
    mock_get.side_effect = [mock_product_response, mock_variable_response]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    variables = cdh.list_variables(
        patterns=["INCOME", "GEOGRAPHY"], logic=any, match_in="concept"
    )

    assert len(variables) == 2
    assert variables[0]["name"] == "B19013_001E"
    assert variables[1]["name"] == "PUMA"


@pytest.mark.unit
@patch("cendat.client.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.client.requests.get")
def test_get_data_preview_only_skips_fetching(mock_get, mock_get_combos, cdh):
    """Tests that preview_only=True sets n_calls but does not fetch data."""
    with patch("cendat.client.ThreadPoolExecutor") as mock_executor:
        mock_product_response = Mock()
        mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
        mock_geo_response = Mock()
        mock_geo_response.json.return_value = FAKE_GEOS_JSON
        mock_variable_response = Mock()
        mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON
        # --- FIX: Correct the sequence of mock responses for the setup calls ---
        mock_get.side_effect = [
            mock_product_response,
            mock_geo_response,
            mock_variable_response,
        ]
        mock_get_combos.return_value = [{}]

        cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
        cdh.set_geos(values="state", by="desc")
        cdh.set_variables(names="B01001_001E")
        response = cdh.get_data(preview_only=True)

        assert cdh.n_calls == 1
        mock_executor.assert_not_called()
        assert response is None


@pytest.mark.unit
@patch("cendat.client.requests.get")
def test_get_data_handles_microdata_correctly(mock_get, cdh):
    """Tests that the microdata workflow constructs the correct API call."""
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_geo_response = Mock()
    mock_geo_response.json.return_value = FAKE_GEOS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON
    mock_get.side_effect = [
        mock_product_response,
        mock_geo_response,
        mock_variable_response,
        Mock(),
        Mock(),
    ]

    cdh.set_products(titles="PUMS Household Data (2022/acs/acs5/pums)")
    cdh.set_geos(values="public use microdata area", by="desc")
    cdh.set_variables(names="PUMA")
    cdh.get_data(
        within={"state": "08", "public use microdata area": ["01301", "01302"]}
    )

    assert mock_get.call_count == 5  # 3 setup calls + 2 data calls

    first_data_call = mock_get.call_args_list[-2]
    assert first_data_call.kwargs["params"]["for"] == "public use microdata area:01301"
    assert first_data_call.kwargs["params"]["in"] == "state:08"

    second_data_call = mock_get.call_args_list[-1]
    assert second_data_call.kwargs["params"]["for"] == "public use microdata area:01302"
    assert second_data_call.kwargs["params"]["in"] == "state:08"


@pytest.mark.unit
@patch("cendat.client.requests.get")
def test_set_geos_requires_message(mock_get, cdh, capsys):
    mock_product_response = Mock()
    mock_product_response.json.return_value = {
        "dataset": [
            {
                "title": "American Community Survey",
                "c_isAggregate": "true",
                "c_vintage": 2022,
                "distribution": [
                    {"accessURL": "http://api.census.gov/data/2022/acs/acs5"}
                ],
            }
        ]
    }
    mock_product_response.raise_for_status.return_value = None
    mock_geo_response = Mock()
    mock_geo_response.json.return_value = FAKE_GEOS_JSON
    mock_geo_response.raise_for_status.return_value = None
    mock_get.side_effect = [mock_product_response, mock_geo_response]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")

    captured = capsys.readouterr()
    expected_message = (
        "✅ Geographies set: 'tract' (requires `within` for: county, state)\n"
    )
    assert captured.out.endswith(expected_message)


@pytest.mark.unit
@patch("cendat.client.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.client.requests.get")
def test_get_data_expands_within_clauses_correctly(mock_get, mock_get_combos, cdh):
    mock_product_response = Mock()
    mock_product_response.json.return_value = {
        "dataset": [
            {
                "title": "American Community Survey",
                "c_isAggregate": "true",
                "c_vintage": 2022,
                "distribution": [
                    {"accessURL": "http://api.census.gov/data/2022/acs/acs5"}
                ],
            }
        ]
    }
    mock_geo_response = Mock()
    mock_geo_response.json.return_value = FAKE_GEOS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON
    mock_get.side_effect = [
        mock_product_response,
        mock_geo_response,
        mock_variable_response,
    ]
    mock_get_combos.return_value = [{"state": "08", "county": "123", "tract": "000100"}]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")
    cdh.set_variables(names="B01001_001E")
    cdh.get_data(within=[{"state": "08", "county": "123"}, {"state": "56"}])

    assert mock_get_combos.call_count == 2
    first_call_args = mock_get_combos.call_args_list[0]
    assert first_call_args.args[1] == []
    assert first_call_args.args[2] == {"state": "08", "county": "123"}
    second_call_args = mock_get_combos.call_args_list[1]
    assert second_call_args.args[1] == ["county"]
    assert second_call_args.args[2] == {"state": "56"}


@pytest.mark.unit
@patch("cendat.client.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.client.requests.get")
def test_get_data_handles_complex_list_expansion(mock_get, mock_get_combos, cdh):
    mock_product_response = Mock()
    mock_product_response.json.return_value = {
        "dataset": [
            {
                "title": "American Community Survey",
                "c_isAggregate": "true",
                "c_vintage": 2022,
                "distribution": [
                    {"accessURL": "http://api.census.gov/data/2022/acs/acs5"}
                ],
            }
        ]
    }
    mock_geo_response = Mock()
    mock_geo_response.json.return_value = FAKE_GEOS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON
    mock_get.side_effect = [
        mock_product_response,
        mock_geo_response,
        mock_variable_response,
    ]
    mock_get_combos.return_value = [{}]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")
    cdh.set_variables(names="B01001_001E")
    cdh.get_data(
        within=[{"state": "08", "county": ["069", "123"]}, {"state": ["36", "06"]}]
    )

    assert mock_get_combos.call_count == 4
    call_args = [call.args for call in mock_get_combos.call_args_list]
    assert call_args[0][1] == []
    assert call_args[0][2] == {"state": "08", "county": "069"}
    assert call_args[1][1] == []
    assert call_args[1][2] == {"state": "08", "county": "123"}
    assert call_args[2][1] == ["county"]
    assert call_args[2][2] == {"state": "36"}
    assert call_args[3][1] == ["county"]
    assert call_args[3][2] == {"state": "06"}


@pytest.mark.unit
def test_to_pandas_concatenation(sample_response):
    """Tests that concat=True returns a single pandas DataFrame."""
    import pandas as pd

    df = sample_response.to_pandas(concat=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3


@pytest.mark.unit
def test_to_polars_schema_overrides(sample_response):
    """Tests that schema_overrides correctly casts types in Polars."""
    import polars as pl

    df = sample_response.to_polars(schema_overrides={"POP": pl.Int64}, concat=True)
    assert df["POP"].dtype == pl.Int64
