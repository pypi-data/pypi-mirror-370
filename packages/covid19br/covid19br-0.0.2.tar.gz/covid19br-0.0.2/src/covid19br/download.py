import pandas as pd
import requests
from typing import Literal, Optional
import urllib.error


def download_covid19(
    level: Literal["brazil", "regions", "states", "cities", "world"] = "brazil"
) -> Optional[pd.DataFrame]:
    """
    Downloads COVID-19 data from a web repository.

    Parameters
    ----------
    level : {"brazil", "regions", "states", "cities", "world"}, default "brazil"
        The desired level of data aggregation.

    Returns
    -------
    pandas.DataFrame or None
        A DataFrame containing the downloaded data, or None if download failed.
    
   Notes
    -----
    This function requires a Parquet reading engine like `pyarrow`.
    Install it with `pip install pyarrow`.

    Data Dictionary (variables common to Brazilian and world data):
    - date: date of data registry
    - epi_week: epidemiological week
    - pop: estimated population
    - accumCases: accumulative number of confirmed cases
    - newCases: daily count of new confirmed cases
    - accumDeaths: accumulative number of deaths
    - newDeaths: daily count of new deaths
    - newRecovered: daily count of new recovered patients

    Data Dictionary (variables in the Brazilian data):
    - region: regions' names
    - state: states' names.
    - city: cities' names.
    - state_code: numerical code attributed to states
    - city_code: numerical code attributed to cities
    - healthRegion_code: health region code
    - healthRegion: heald region name
    - newFollowup: daily count of new patients under follow up
    - metro_area: indicator variable for city localized in a metropolitan area
    - capital: indicator variable for capital of brazilian states

    Data Dictionary (variables in the world data):
    - country: countries' names
    - accumRecovered: accumulative number of recovered patients

    Examples
    --------
    >>> # Downloading Brazilian COVID-19 data:
    >>> # from covid19br import
    >>> # Downloading Brazilian COVID-19 data:
    >>> # brazil_df = download_covid19(level="brazil")
    >>> # regions_df = download_covid19(level="regions")
    >>> # states_df = download_covid19(level="states")
    >>> # cities_df = download_covid19(level="cities")

    >>> # Downloading world COVID-19 data:
    >>> # world_df = download_covid19(level="world")
    """    

    BASE_URL = "https://raw.githubusercontent.com/dest-ufmg/covid19repo/master/data/"

    # Normalize input
    level = level.lower()
    valid_levels = ["brazil", "regions", "states", "cities", "world"]
    if level not in valid_levels:
        raise ValueError(f"Invalid level '{level}'. Must be one of {valid_levels}")

    print("Downloading COVID-19 data... please, be patient!")

    url = f"{BASE_URL}{level}.parquet"

    try:
        data = pd.read_parquet(url)
        if "date" in data.columns:
            data["date"] = pd.to_datetime(data["date"], errors="coerce")
        return data
    except ImportError:
        print("Error: `pyarrow` or `fastparquet` is not installed. Install with `pip install pyarrow`.")
        return None
    except (OSError, ValueError):
        print(f"Error: Could not read data file at the specified URL: {url}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
