__version__ = '0.0.1'

import zipcodes
from uszipcode.search import SearchEngine
import pandas as pd

def us_get_demographics(state: str, city: str = None, zip_list: list = None) -> pd.DataFrame:
    """
    This gets demographic information for associated with zipcodes in the United States of America.

    Parameters
    ----------
    * state : str - the US state
    * city : str [Optional] - the US city
    * zip_list : list [Optional] - a zip list is the query results from the zipcodes library.
    Found here: https://github.com/seanpianka/zipcodes
    If you use zip_list state and city will be ignored.

    Returns
    -------
    A pandas dataframe with zipcode and everything typically returned by
    https://github.com/EricSchles/uszipcode-project
    """
    search = SearchEngine()
    payload = {
        "state": state,
        "city": city
    }
    if zip_list is None:
        zipcode_and_demo = [
            [zipcode["zip_code"], search.by_zipcode(zipcode["zip_code"])]
            for zipcode in zipcodes.filter_by(**payload)
        ]
    else:
        zipcode_and_demo = zip_list[:]
    demographics = []
    for index in range(len(zipcode_and_demo)):
        tmp_dict = zipcode_and_demo[index][1].to_dict()
        tmp_dict["zip_code"] = zipcode_and_demo[index][0]
        demographics.append(tmp_dict)
    return pd.DataFrame(demographics)
