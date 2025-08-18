# cendat: A Python Helper for the Census API

## Introduction
cendat is a Python library designed to simplify the process of exploring and retrieving data from the U.S. Census Bureau's API. It provides a high-level, intuitive workflow for discovering available datasets, filtering geographies and variables, and fetching data concurrently.

The library handles the complexities of the Census API's structure, such as geographic hierarchies and inconsistent product naming, allowing you to focus on getting the data you need.

## Workflow
The library is designed around a simple, four-step "List -> Set -> Get -> Convert" workflow:

List: Use the list_* methods (list_products, list_geos, list_variables) with patterns to explore what's available and filter down to what you need.

Set: Use the set_* methods (set_products, set_geos, set_variables) to lock in your selections. You can call these methods without arguments to use the results from your last "List" call.

Get: Call the get_data() method to build and execute all the necessary API calls. This method handles complex geographic requirements automatically and utilizes thread pooling for speed. Thread pooling is controlled through the `max_workers` parameter. Note that for requests that will generate many (thousands or more) API calls, setting `max_workers` explicitly and at low values (say, < 100) will reduce the probability of errors due to server-side intervention.

Convert: Use the to_polars() or to_pandas() methods on the response object to get your data in a ready-to-use DataFrame format.

# Installation

You can install cendat using pip.

```bash
pip install cendat
```
The library has optional dependencies for converting the response data into pandas or polars DataFrames. You can install the support you need:

## Install with pandas support

```bash
pip install cendat[pandas]
```
## Install with polars support

```bash
pip install cendat[polars]
```

## Install with both

```bash
pip install cendat[all]
```

# Usage

The intended workflow is a step-by-step process of refining your data query. You start by selecting dataset products, then geographies, and finally the specific variables you need.

1.  **Initialize**: Create an instance of `CenDatHelper`, optionally setting the year(s) and API key.
2.  **Select Product**: Use `list_products()` to find products and `set_products()` to select them.
3.  **Select Geography**: Use `list_geos()` to see available geographic levels and `set_geos()` to choose them.
4.  **Select Variables**: Use `list_variables()` to explore available variables and `set_variables()` to select them.
5.  **Get Data**: Call `get_data()` to concurrently execute the required queries. This returns a `CenDatResponse` object.
6.  **Convert**: Use `.to_pandas()` or `.to_polars()` on the response object to get a ready-to-use DataFrame.

---

## `CenDatHelper` Class

### `__init__(self, years=None, key=None)`

Initializes the helper object.

* **`years`** (`int` | `list[int]`, optional): The year or years of interest. Can be a single integer or a list of integers. Defaults to `None`.
* **`key`** (`str`, optional): Your Census API key. Providing a key is recommended to avoid strict rate limits. Defaults to `None`.

### `set_years(self, years)`

Sets the primary year or years for data queries.

* **`years`** (`int` | `list[int]`): The year or years to set.

### `load_key(self, key=None)`

Loads a Census API key for authenticated requests.

* **`key`** (`str`, optional): The API key to load.

### `list_products(self, years=None, patterns=None, to_dicts=True, logic=all, match_in='title')`

Lists available data products, filtered by year and search patterns.

* **`years`** (`int` | `list[int]`, optional): Filters products available for the specified year(s). Defaults to the years set on the object.
* **`patterns`** (`str` | `list[str]`, optional): Regex pattern(s) to search for within the product metadata.
* **`to_dicts`** (`bool`): If `True` (default), returns a list of dictionaries with full product details. If `False`, returns a list of product titles.
* **`logic`** (`callable`): The logic to use when multiple patterns are provided. Can be `all` (default) or `any`.
* **`match_in`** (`str`): The field to match patterns against. Can be `'title'` (default) or `'desc'`.

### `set_products(self, titles=None)`

Sets the active data products for the session.

* **`titles`** (`str` | `list[str]`, optional): The title or list of titles of the products to set. If `None`, it sets all products from the last `list_products()` call.

### `list_geos(self, to_dicts=False, patterns=None, logic=all)`

Lists available geographies for the currently set products.

* **`to_dicts`** (`bool`): If `True`, returns a list of dictionaries with full geography details. If `False` (default), returns a list of unique summary level (`sumlev`) strings.
* **`patterns`** (`str` | `list[str]`, optional): Regex pattern(s) to search for within the geography description.
* **`logic`** (`callable`): The logic to use when multiple patterns are provided. Can be `all` (default) or `any`.

### `set_geos(self, values=None, by='sumlev')`

Sets the active geographies for the session.

* **`values`** (`str` | `list[str]`, optional): The geography values to set. If `None`, sets all geos from the last `list_geos()` call.
* **`by`** (`str`): The key to use for matching `values`. Must be either `'sumlev'` (default) or `'desc'`.

### `list_variables(self, to_dicts=True, patterns=None, logic=all, match_in='label')`

Lists available variables for the currently set products.

* **`to_dicts`** (`bool`): If `True` (default), returns a list of dictionaries with full variable details. If `False`, returns a list of unique variable names.
* **`patterns`** (`str` | `list[str]`, optional): Regex pattern(s) to search for within the variable metadata.
* **`logic`** (`callable`): The logic to use when multiple patterns are provided. Can be `all` (default) or `any`.
* **`match_in`** (`str`): The field to match patterns against. Can be `'label'` (default), `'name'` or `'concept'`.

### `set_variables(self, names=None)`

Sets the active variables for the session.

* **`names`** (`str` | `list[str]`, optional): The name or list of names of the variables to set. If `None`, sets all variables from the last `list_variables()` call.

### `get_data(self, within='us', max_workers=100)`

Executes the API calls based on the set parameters and retrieves the data.

* **`within`** (`str` | `dict` | `list[dict]`, optional): Defines the geographic scope of the query.
    * For **aggregate** data, this can be a dictionary filtering parent geographies (e.g., `{'state': '06'}` for California).
    * For **microdata**, this must be a dictionary specifying the target geography and its codes (e.g., `{'public use microdata area': ['7701', '7702']}`).
    * Defaults to `'us'` for nationwide data where applicable.
* **`max_workers`** (`int`, optional): The maximum number of concurrent threads to use for making API calls. Defaults to `100`.

---

## `CenDatResponse` Class

A container for the data returned by `CenDatHelper.get_data()`.

### `to_polars(self, schema_overrides=None, concat=False)`

Converts the raw response data into a list of Polars DataFrames.

* **`schema_overrides`** (`dict`, optional): A dictionary mapping column names to Polars data types to override the inferred schema. Example: `{'POP': pl.Int64}`.

* **`concat`** (`bool`): If `True`, DataFrames are concatenated across response list items.

### `to_pandas(self, dtypes=None, concat=False)`

Converts the raw response data into a list of Pandas DataFrames.

* **`dtypes`** (`dict`, optional): A dictionary mapping column names to Pandas data types, which is passed to the `.astype()` method. Example: `{'POP': 'int64'}`.

* **`concat`** (`bool`): If `True`, DataFrames are concatenated across response list items.

# Usage Examples

## Example 1: ACS Microdata (PUMS) Request
This example demonstrates a complete workflow for retrieving Public Use Microdata Sample (PUMS) data from the ACS for specific geographic areas in Alabama and Arizona.

```python
import polars as pl
from dotenv import load_dotenv
import os
from cendat import CenDatHelper
from pprint import pprint

# Load environment variables (e.g., for CENSUS_API_KEY)
load_dotenv()

# 1. Initialize the helper for a set of years and provide API key
cd = CenDatHelper(years=[2017], key=os.getenv("CENSUS_API_KEY"))

# 2. Find and select the desired data product
# Use patterns to find the 5-year ACS PUMS product for 2017
potential_products = cd.list_products(
    patterns=[
        "american community|acs",
        "public use micro|pums",
        "5-year",
        "^(?!.*puerto rico).*$",
    ]
)

for product in potential_products:
    print(product["title"], product["vintage"])

# Call set_products() with no arguments to use the filtered results
cd.set_products()

# 3. Find and select the desired geography
# For PUMAs we can use 'public use microdata area' (sumlev 795)
cd.list_geos(to_dicts=True)
cd.set_geos("795")

# 4. Find and select variables
# Find variables related to income, weights, or PUMA
potential_vars = cd.list_variables(
    to_dicts=True,
    patterns=["income", "person weight", "public.*area"],
    logic=any,
)

for var in potential_vars:
    print(var["name"], var["label"])

cd.set_variables(["PUMA", "PWGTP", "HINCP", "ADJINC"])

# 5. Get the data
# Provide a list of dictionaries to `within` to make multiple
#  specific geographic requests in one call.
# For microdata requests - due to the volume of data returned - this
#  level of specificity is required.
response = cd.get_data(
    within=[
        {"state": "1", "public use microdata area": ["400", "2500"]},
        {"state": "4", "public use microdata area": "105"},
    ]
)

# 6. Review subscriptable attributes
for detail in ["products", "geos", "variables"]:
    print('-'*20, detail, '-'*20)
    pprint(cd[detail])

# 7. Convert to a DataFrame
# The response object can be converted to a list of Polars DataFrames 
#  which itself is easily concatenated (assuming the products are compatible)
pums_df = response.to_polars(concat=True)

```

## Example 2: Aggregate Data Request
This example shows how to retrieve aggregate data for a more complex geography--county (or part)--that requires API calls nested within parent-level geographies (place and state, in this case). API calls are constructed automatically for all nested parent geographies below either the entire nation (default) or parent geographies provided explicitly and at any legitimate level of granularity through the `within` parameter in the `get_data()` method.

```python
import polars as pl
from dotenv import load_dotenv
import os
from cendat import CenDatHelper

load_dotenv()

# 1. Initialize for multiple years
cdh = CenDatHelper(years=[2022, 2023], key=os.getenv("CENSUS_API_KEY"))

# 2. Find and select products
# Find the standard 5-year detailed tables
potential_products = cdh.list_products(
    to_dicts=True,
    patterns=[
        "american community|acs",
        "5-year",
        "detailed",
    ],
)

for product in potential_products:
    print(product["title"], product["vintage"])

# Further filter out special population products
potential_products = cdh.list_products(
    to_dicts=True,
    patterns=[
        "american community|acs",
        "5-year",
        "detailed",
        "^(?!.*(alaska|aian|selected)).*$",
    ],
)

for product in potential_products:
    print(product["title"], product["vintage"])

cdh.set_products()

# 3. Find and select geography
for geo in cdh.list_geos(to_dicts=True):
    print(geo)

# Set the geography to 'county (or part)' (sumlev 155). The success
#  message will inform us that this geography requires 'state and 
#  place' to be specified in the `within` clause.
cdh.set_geos(["155"])

# 4. Find and select variables
potential_variables = cdh.list_variables(
    to_dicts=True, patterns=["total", "less.*high"]
)

for var in potential_variables:
    print(var["name"], var["label"])

# Manually set variables after inspecting the list output
cdh.set_variables(["B07009_002E", "B16010_009E"])

# 5. Get the data - specify all parts in two places from one state 
#  and parts from all places in another state. This yields 3,233 API 
#  queries!
# It's important to not set `max_workers` too high to avoid having
#  Census block the connection. If that happens (you'll probably 
#  see an error with 'An existing connection was forcibly closed 
#  by the remote host'), lower the `max_workers` value and try again 
#  after a short wait.
response = cdh.get_data(
    max_workers=50,
    within=[
        {"state": "36", "place": ["61797", "61621"]},
        {"state": "06"},
    ],
)

# 6. Convert and combine DataFrames, forcing estimate variables 
#  to be integers
estimates = response.to_polars(
    schema_overrides={
        "B07009_002E": pl.Int64,
        "B16010_009E": pl.Int64,
    },
    concat=True,
)


# 7. Inspect
print(estimates.head())

```

## Example 3. Microdata Request
This example pulls monthly CPS microdata.

```python
import polars as pl
from dotenv import load_dotenv
import os
from cendat import CenDatHelper

load_dotenv()

# 1. Initialize without specifying years
cdh = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))

# 2. Explore available products without much restriction
potential_products = cdh.list_products(patterns=["cps"])

for product in potential_products:
    print(product["title"], product["vintage"], product["is_microdata"], product["url"])

# 3. Set to a specific year
cdh.set_years(2019)

# 4. Explore products again with more spcificity
potential_products = cdh.list_products(patterns=["cps basic"])

for product in potential_products:
    print(product["title"], product["vintage"], product["is_microdata"], product["url"])

# 5. Set the products based on the last (more specific) product listing
cdh.set_products()

# 6. Explore variables for employment, education, and age 
#  (also need to identify weight vars)
potential_variables = cdh.list_variables(
    patterns=[
        "unemployed","school","weight","age",
    ],
    logic=any,
)

for variable in potential_variables:
    print(variable["name"], variable["label"], variable["vintage"])

# 7. Set the variables
cdh.set_variables(["PELKAVL", "PEEDUCA", "PRTAGE", "PWCMPWGT", "PWLGWGT"])

# 8. Explore geographies
cdh.list_geos(to_dicts=True)

# 9. Set to state - for microdata, we then need to provide 
#  specific state[s] in the `within` clause
cdh.set_geos("040")

# 10. Get the data for Colorado (12 concurrent API queries)
response = cdh.get_data(
    within={'state': '08'}
)

# 11. Convert to polars df and stack
microdata = response.to_polars(
    schema_overrides={
        'PELKAVL': pl.Int64,
        'PEEDUCA': pl.Int64,
        'PRTAGE': pl.Int64,
        'PWCMPWGT': pl.Float64,
        'PWLGWGT': pl.Float64,
    },
    concat=True,
)


```