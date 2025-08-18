import polars as pl
import os
from dotenv import load_dotenv

load_dotenv()
from cendat.client import CenDatHelper

confirm_src = {
    type: pl.read_csv(f"tests/data/{type}.txt", separator=delim)
    for type, delim in zip(
        [
            "block_groups",
            "tracts",
            "counties",
            "county_subs",
            "places",
            "places_by_county",
        ],
        [
            ",",
            ",",
            ",",
            "|",
            "|",
            "|",
        ],
    )
}

states = (
    confirm_src["counties"]
    .filter(pl.col.STATEFP != 9)
    .select(pl.col.STATEFP.cast(str).str.zfill(2).alias("STATEFP"))
    .get_column("STATEFP")
    .unique()
    .to_list()
)

c = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))
c.list_products(2020, r"\(2020/dec/dhc\)", False)
c.set_products()
c.set_variables("H9_001N")


def test_n_calls_counties():

    check_calls = confirm_src["counties"].get_column("STATEFP").unique().len()

    c.set_geos("050")
    c.get_data(preview_only=True)

    assert c["n_calls"] == check_calls


def test_n_calls_county_subs():

    check_calls = (
        confirm_src["county_subs"]
        .select(["STATEFP", "COUNTYFP"])
        # territories out of scope
        .filter(pl.col.STATEFP.is_in([60, 66, 69, 74, 78]).not_())
        .unique()
        .height
    )

    c.set_geos("060")
    c.get_data(
        preview_only=True,
    )

    assert c["n_calls"] == check_calls


def test_n_calls_tracts():

    check_calls = confirm_src["tracts"].select(["STATEFP", "COUNTYFP"]).unique().height

    c.set_geos("140")
    c.get_data(
        preview_only=True,
    )

    assert c["n_calls"] == check_calls


def test_n_calls_block_groups():

    check_calls = (
        confirm_src["block_groups"]
        .select(["STATEFP", "COUNTYFP", "TRACTCE"])
        .unique()
        .height
    )

    c.set_geos("150")
    c.get_data(preview_only=True, timeout=60, max_workers=50)

    assert c["n_calls"] == check_calls


def test_n_calls_places():

    check_calls = (
        confirm_src["places"]
        .filter(pl.col.STATEFP.is_in([60, 66, 69, 74, 78]).not_())
        .select(["STATEFP"])
        .unique()
        .height
    )

    c.set_geos("160")
    c.get_data(preview_only=True)

    assert c["n_calls"] == check_calls


def test_n_calls_places_by_county():

    check_calls = (
        confirm_src["places_by_county"]
        .filter(
            pl.col.STATEFP.is_in([60, 66, 69, 74, 78]).not_(),
        )
        .select(["STATEFP", "COUNTYFP"])
        .unique()
        .height
    )

    c.set_geos("159")
    c.get_data(preview_only=True)

    # there are three counties that don't contain places
    assert c["n_calls"] - 3 == check_calls
