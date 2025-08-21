#####
# Imports
from collections import Counter
from datetime import datetime
from itertools import combinations
import numpy as np
import pandas as pd
from random import choice
from scipy.spatial import cKDTree
from shapely import Point


#####
# Main function
def thinst(
        df: pd.DataFrame = None,
        coords: str | pd.Series | list[tuple[int, int], Point] = None,
        sp_threshold: int | float = None,
        datetimes: str | pd.Series | list[str | pd.Timestamp | datetime] = None,
        tm_threshold: int | float = None,
        tm_unit: str = 'day',
        ids: pd.Series | list[str | int | float] = None,
        no_reps: int = 100,
        block: str = None) \
        -> pd.DataFrame | tuple[list | list | list]:
    """Thin points spatially, temporally, or spatiotemporally.

    Spatiotemporal thinning will remove points so that no two points are within a given spatial threshold and within a
     given temporal threshold of each other. Accordingly, two points may overlap spatially, provided that they do not
     overlap temporally and vice versa.
    Spatial thinning will remove points so that no two points are within a given spatial threshold of each other.
    Temporal thinning will remove points so that no two points are within a given temporal threshold of each other.

    For input, there are two options:
    The first (recommended) is to input a pandas.DataFrame or geopandas.GeoDataFrame and specify the column(s) that
     contain the coordinates and/or datetimes. In this case, the parameter 'df' will be the DataFrame and the parameters
     'coords' and 'datetimes' will be the names of the columns that contain the coordinates and datetimes, respectively.
    The second is to input the coordinates and/or datetimes as lists or pandas.Series. In this case, the parameter 'df'
     will be None and the parameters 'coords' and 'datetimes' will be the lists or pandas.Series that contain the
     coordinates and datetimes, respectively.

    With both input options, the spatial threshold is set with 'sp_threshold' and the temporal threshold with
     'tm_threshold'. Additionally, the units of the temporal threshold (e.g., days, years) are set with 'tm_unit'.
    If both a spatial and temporal threshold are specified, spatiotemporal thinning will occur. If only a spatial
     threshold is specified, spatial thinning will occur. If only a temporal threshold is specified, temporal thinning
     will occur.

    Note that spatial thinning uses Euclidean distances and so is incompatible with latitude-longitude coordinates.
     Latitude-longitude coordinates must be reprojected into an appropriate projected CRS before thinning. Moreover,
     there will be some discrepancy between these Euclidean distances and geodesic distances. Assuming an appropriate
     CRS is chosen, this discrepancy should be negligible over short distances (<0.1% for distances <1000 kms) and
     medium distances (<1% for distances <2500 kms), but may become more significant for longer distances. The thinst
     package is, thus, unsuitable for data on a global or continental scale.

    __________
    Parameters:
    df : pandas.DataFrame | geopandas.GeoDataFrame, optional, default None
        A dataframe containing the points to be thinned. If specified, the column(s) containing the coordinates and/or
         datetimes must be specified with the parameters 'coords' and 'datetimes', respectively.
    coords : str | pandas.Series | list[tuple[int, int], Point], optional, default None
        One of the following:
            the name of the column in 'df' that contains the coordinates
            a pandas.Series of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
            a list of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
    sp_threshold : int | float, optional, default None
        The spatial threshold to use for spatial and spatiotemporal thinning in the units of the coordinates. If both a
         spatial and temporal threshold are specified, spatiotemporal thinning will occur. If only a spatial threshold
         is specified, spatial thinning will occur. If only a temporal threshold is specified, temporal thinning will
         occur.
    datetimes : str | pandas.Series | list[str | pandas.Timestamp | datetime], optional, default None
        One of the following:
            the name of the column in 'df' that contains the datetimes
            a pandas.Series of datetimes as strings, pandas.Timestamps, or datetime.datetimes
            a list of datetimes as strings, pandas.Timestamps, or datetime.datetimes
    tm_threshold : int | float, optional, default None
        The temporal threshold to use for temporal and spatiotemporal thinning in the units set with 'tm_unit'. If both
         a spatial and temporal threshold are specified, spatiotemporal thinning will occur. If only a spatial threshold
         is specified, spatial thinning will occur. If only a temporal threshold is specified, temporal thinning will
         occur.
    tm_unit : {'year', 'month', 'day', 'hour', 'moy', 'doy'}, optional, default 'day'
        The temporal units to use for temporal or spatiotemporal thinning. Must be one of the following:
            'year': year (all datetimes from the same year will be given the same value)
            'month': month (all datetimes from the same month and year will be given the same value)
            'day': day (all datetimes with the same date will be given the same value)
            'hour': hour (all datetimes in the same hour on the same date will be given the same value)
            'moy': month of the year (i.e., January is 1, February is 2, regardless of the year)
            'doy': day of the year (i.e., January 1st is 1, February 1st is 32, regardless of the year)
        The default value is 'day'.
    ids : pandas.Series | list[str | int | float], optional, default None
        If using the second option for data input, a pandas.Series or list of unique IDs to identify the points that
         were kept after thinning.
    no_reps : int, optional, default 100
        The number of repetitions to run when conducting thinning. From these repetitions, one of those that retains the
         most points will be output.
    block : str, optional, default None
        Optionally, the name of a column in df that contains unique values to be used to separate the data into blocks
         that will be thinned independently. Note, only applicable if using the first input option.

    __________
    Returns:
      One of the following, depending on the input:
        pandas.DataFrame | geopandas.GeoDataFrame
          If using the first input option, a pandas.DataFrame or a geopandas.GeoDataFrame, depending on which was input,
           containing only those points that were kept after thinning.
        tuple[list | list | list]
          If using the second input option, a tuple containing three lists that contain the coordinates, datetimes, and
           IDs, respectively. If one or more of the coordinates, datetimes, and IDs is not input, an empty list will be
           returned in its place (meaning that the tuple will always have three elements: coordinates, datetimes, IDs).
    """

    if block is not None:
        thinned_list = []  # list for thinned DataFrames
        for uniq in df[block].unique():  # for each unique value in block col
            df_block = df.copy()[df[block] == uniq]  # subset the DataFrame
            pairs_block = get_pairs(
                df=df_block,
                coords=coords,
                sp_threshold=sp_threshold,
                datetimes=datetimes,
                tm_threshold=tm_threshold,
                tm_unit=tm_unit
            )
            thinned_list.append(thinner(
                pairs=pairs_block,
                df=df_block,
                coords=coords,
                datetimes=datetimes,
                no_reps=no_reps
            ))
        thinned = pd.concat(thinned_list)

    else:
        pairs = get_pairs(
            df=df,
            coords=coords,
            sp_threshold=sp_threshold,
            datetimes=datetimes,
            tm_threshold=tm_threshold,
            tm_unit=tm_unit
        )
        thinned = thinner(
            pairs=pairs,
            df=df,
            coords=coords,
            datetimes=datetimes,
            ids=ids,
            no_reps=no_reps
        )
    return thinned.reset_index(drop=True)


#####
# Functions
def get_coords(df: pd.DataFrame = None, coords: str | pd.Series | list = None)\
        -> list[tuple[float | int, float | int] | Point]:
    """Get the coordinates.
    For either input option, takes the input coordinates and reformats them into a standardised list of coordinates that
     are either tuples of XY coordinates or shapely.Points.
    __________
    Parameters:
      df: pandas.DataFrame | geopandas.GeoDataFrame, optional, default None
        Optionally, a dataframe containing the points to be thinned. If specified, the column containing the
        coordinates must be specified with the parameter 'coords'.
      coords : str | pandas.Series | list[tuple[int, int], Point], optional, default None
        One of the following:
         the name of the column in 'df' that contains the coordinates
         a pandas.Series of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
         a list of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
    __________
    Returns:
      A standardised list of coordinates that are either tuples or shapely.Points.
    """
    
    if isinstance(df, pd.DataFrame) and isinstance(coords, str):  # option 1: dataframe and column name
        if coords in df:  # if coords is a column in the dataframe...
            coords = list(df[coords])  # ...convert the column to a list
        else:  # else if coords is not a column in the dataframe...
            raise KeyError(f"the column '{coords}' could not be found in the dataframe.")  # ...raise error
    elif isinstance(coords, (pd.Series, list)):  # option 2: list or series
        coords = list(coords)  # convert coords to list
    else:  # else an unknown combination of df and coords, raise error...
        raise TypeError("the parameters 'df' and/or 'coords' are of an invalid or incompatible type."
                        f"\nThe datatype of 'df' is {type(df).__name__}"
                        f"\nThe datatype of 'coords' is {type(coords).__name__}"
                        "\nPlease use one of the following options:"
                        "\n  Option 1: 'df' is a pandas.DataFrame or geopandas.GeoDataFrame and 'coords' is a string "
                        "indicating the name of a column in 'df'."
                        "\n  Option 2: 'df' is None (or left unspecified) and 'coords' is a list or pandas.Series.")

    # coords is a list, now to check the datatypes of its elements
    dtypes = list(set([type(coord) for coord in coords]))  # get the datatypes of the coords in a list
    if len(dtypes) == 1:  # if there is only one datatype...
        if isinstance(coords[0], (tuple, Point)):  # ...and that is tuple or shapely.Point...
            pass  # ...leave them as they are
        else:  # ...else that is some other datatype, raise error
            raise TypeError("the coordinates are of an invalid datatype."
                            f"\nPlease ensure that all coordinates are of one of the following datatypes:"
                            f"\n  tuple (containing an X and Y coordinate)"
                            f"\n  shapely.Point")
    elif len(dtypes) > 1:  # if there is more than one datatype, raise error
        raise TypeError("the coordinates are of more than one datatype."
                        f"\nThe datatypes are: {', '.join([dtype.__name__ for dtype in dtypes])}"
                        f"\nPlease ensure that all coordinates are of one of the following datatypes:"
                        f"\n  tuple (containing an x and y coordinate)"
                        f"\n  shapely.Point")
    else:  # else there are no datatypes...
        raise Exception("'coords' is empty")  # ...raise error
    return coords  # return a list of coords that are either tuples or shapely.Points


def get_xs_ys(coords: list[tuple[float | int, float | int] | Point]) -> tuple[list[float | int], list[float | int]]:
    """Get the X and Y values of the coordinates.
    From the coordinates, gets the X and Y values and puts them into two corresponding lists.
    __________
    Parameters:
      coords: list[tuple[float | int, float | int] | Point]
        A standardised list of coordinates that are either tuples or shapely.Points as output by get_coords().
    __________
    Returns:
      A tuple containing two corresponding lists that contain the X and Y coordinates, respectively.
    """
    # coords is a list of coords that are all either tuples or shapely.Points
    if isinstance(coords[0], Point):  # if the coords are shapely.Points...
        xs = [point.x for point in coords]  # ...get the X coordinates of the shapely.Points
        ys = [point.y for point in coords]  # ...get the Y coordinates of the shapely.Points
    elif isinstance(coords[0], tuple):  # if the coords are tuples of x and y coordinates...
        xs = [point[0] for point in coords]  # ...get the X coordinates
        ys = [point[1] for point in coords]  # ...get the Y coordinates
    else:  # else the coords are neither Points nor tuples (should never be reached given checks in get_coords())
        raise TypeError('coords are of an invalid datatype')
    return xs, ys  # return the Xs and Ys as lists of floats or integers


def get_sp_pairs(coords: list[tuple[float | int, float | int] | Point], sp_threshold: int | float)\
        -> list[tuple[int, int]]:
    """Get pairs of points that are within the spatial threshold.
    Uses get_xs_ys() to get the X and Y values from the coordinates. Then inputs the X and Y values into a cKDTree to
     get those points that are within the spatial threshold of each other.
    __________
    Parameters:
      coords: list[tuple[float | int, float | int] | Point]
        A standardised list of coordinates that are either tuples or shapely.Points as output by get_coords().
      sp_threshold : int | float, optional, default None
        The spatial threshold to use for spatial and spatiotemporal thinning in the units of the coordinates.
    __________
    Returns:
      A list of tuples that each contain the indices of a pair of points that are within the spatial threshold of each
       other.
    """
    
    xs, ys = get_xs_ys(coords=coords)  # get the X and Y values
    tree = cKDTree(np.array([xs, ys]).T)  # create a cKD tree from the X and Y values
    pairs_list = list(tree.query_pairs(sp_threshold))  # get indices of pairs that are within the spatial threshold
    return pairs_list  # list of pairs that are within the spatial threshold of each other


def get_datetimes(df: pd.DataFrame = None, datetimes: str | pd.Series | list = None) -> list[datetime | pd.Timestamp]:
    """Get the datetimes.
    For either input option, takes the input datetimes and reformats them into a standardised list of datetimes that are
     either datetime.datetimes or pandas.Timestamps.
    __________
    Parameters:
      df: pandas.DataFrame | geopandas.GeoDataFrame, optional, default None
        Optionally, a dataframe containing the points to be thinned. If specified, the column containing the
        datetimes must be specified with the parameter 'datetimes'.
      datetimes : str | pandas.Series | list[str | pandas.Timestamp | datetime], optional, default None
        One of the following:
          the name of the column in 'df' that contains the datetimes
          a pandas.Series of datetimes as strings, pandas.Timestamps, or datetime.datetimes
          a list of datetimes as strings, pandas.Timestamps, or datetime.datetimes
    __________
    Returns:
      A standardised list of datetimes that are either datetime.datetimes or pandas.Timestamps.
    """
    if isinstance(df, pd.DataFrame) and isinstance(datetimes, str):  # option 1: dataframe and column name
        if datetimes in df:  # if datetimes is a column in the dataframe...
            datetimes = list(df[datetimes])  # ...convert the column to a list
        else:  # else if datetimes is not a column in the dataframe...
            raise KeyError(f"the column '{datetimes}' could not be found in the dataframe.")  # ...raise error
    elif isinstance(datetimes, (pd.Series, list)):  # option 2: list or series
        datetimes = list(datetimes)  # convert datetimes to list
    else:  # else an unknown combination of df and datetimes, raise error...
        raise TypeError("the parameters 'df' and/or 'coords' are of an invalid or incompatible type."
                        f"\nThe datatype of 'df' is {type(df).__name__}"
                        f"\nThe datatype of 'datetimes' is {type(datetimes).__name__}"
                        "\nPlease use one of the following options:"
                        "\n  Option 1: 'df' is a pandas.DataFrame or geopandas.GeoDataFrame and 'datetimes' is a string "
                        "indicating the name of a column in df."
                        "\n  Option 2: 'df' is None (or left unspecified) and 'datetimes' is a list or pandas.Series.")

    # datetimes is a list, now to check the datatypes of its elements
    dtypes = list(set([type(dt) for dt in datetimes]))  # get the datatypes of the datetimes
    if len(dtypes) == 1:  # if there is only one datatype...
        if isinstance(datetimes[0], str):  # ...and that is str...
            datetimes = [pd.to_datetime(date) for date in datetimes]  # ...convert the strings to Timestamps
        elif isinstance(datetimes[0], (pd.Timestamp, datetime)):  # ...and that is pandas.Timestamp or datetime.datetime...
            pass  # ...leave them as they are
        else:  # ...and that is some other datatype, raise error
            raise TypeError("the datetimes are of an invalid datatype."
                            f"\nPlease ensure that all datetimes are of one of the following datatypes:"
                            f"\n  str"
                            f"\n  pandas.Timestamp"
                            f"\n  datetime.datetime")
    elif len(dtypes) > 1:  # if there is more than one datatype, raise error
        raise TypeError("the datetimes are of more than one datatype."
                        f"\nThe datatypes are: {', '.join([dtype.__name__ for dtype in dtypes])}"
                        f"\nPlease ensure that all datetimes are of one of the following datatypes:"
                        f"\n  str"
                        f"\n  pandas.Timestamp"
                        f"\n  datetime.datetime")
    else:  # else there are no datatypes...
        raise Exception("'datetimes' is empty")  # ...raise error
    return datetimes  # return a list of datetimes that are either datetime.datetimes or pandas.Timestamps


def get_zs(datetimes: list[datetime | pd.Timestamp], tm_unit: str = 'day'):
    """Get the Z values of the datetimes.
    From the datetimes, gets the Z values and puts them into a list. Essentially converts datetimes into values along a
     single, continuous, linear axis to facilitate assessment.
    __________
    Parameters:
      datetimes: list[datetime | pd.Timestamp]
        A standardised list of datetimes that are either datetime.datetimes or pandas.Timestamps as output by
         get_datetimes().
      tm_unit: {'year', 'month', 'day', 'hour', 'moy', 'doy'}, optional, default 'day'
        The temporal units to use for temporal or spatiotemporal thinning. Must be one of the following:
          'year': year (all datetimes from the same year will be given the same value)
          'month': month (all datetimes from the same month and year will be given the same value)
          'day': day (all datetimes with the same date will be given the same value)
          'hour': hour (all datetimes in the same hour on the same date will be given the same value)
          'moy': month of the year (i.e., January is 1, February is 2, regardless of the year)
          'doy': day of the year (i.e., January 1st is 1, February 1st is 32, regardless of the year)
        The default value is 'day'.
    __________
    Returns:
      A list that contains the Z coordinates.
    """

    # get minimum date
    date_min = min(datetimes)

    if tm_unit in ['year']:  # if temporal unit is year
        zs = [date.year for date in datetimes]  # Zs are year (plain and simple)
    elif tm_unit in ['month']:  # if temporal unit is month
        zs = [(date.year - date_min.year) * 12 + date.month for date in datetimes]  # Zs are number of months since min date
    elif tm_unit in ['moy']:  # if temporal unit is month of year
        zs = [date.month for date in datetimes]  # Zs are month of the year (1-12)
    elif tm_unit in ['day']:  # if temporal unit is day
        zs = [(date - date_min).days for date in datetimes]  # Zs are number of days since min date
    elif tm_unit in ['doy']:  # if temporal unit is day of year
        zs = [min(365, int(date.strftime('%j'))) for date in datetimes]  # Zs are day of the year (1-366)
    elif tm_unit in ['hour']:  # if temporal unit is hour
        zs = [(date - date_min).days * 24 + (date - date_min).seconds / 3600 for date in datetimes]  # Zs are hours since min date
    else:  # else unrecognised value for temporal unit
        raise ValueError(" temporal unit not recognised. Please ensure that value for 'tm_unit' is valid.")

    return zs  # return the Zs as a list of integers


def get_tm_pairs(datetimes: list[datetime | pd.Timestamp], tm_threshold: int | float, tm_unit: str = 'day')\
        -> list[tuple[int, int]]:
    """Get pairs of points that are within the temporal threshold.
    Uses get_zs() to get the Z values from the datetimes. Then inputs the Z values into a cKDTree to get those points
     that are within the temporal threshold of each other.
    __________
    Parameters:
      datetimes: list[datetime | pd.Timestamp]
        A standardised list of datetimes that are either datetime.datetimes or pandas.Timestamps as output by
         get_datetimes().
      tm_threshold : int | float, optional, default None
        The temporal threshold to use for temporal and spatiotemporal thinning in the units set with 'tm_unit'.
      tm_unit: {'year', 'month', 'day', 'hour', 'moy', 'doy'}, optional, default 'day'
        The temporal units to use for temporal or spatiotemporal thinning. Must be one of the following:
          'year': year (all datetimes from the same year will be given the same value)
          'month': month (all datetimes from the same month and year will be given the same value)
          'day': day (all datetimes with the same date will be given the same value)
          'hour': hour (all datetimes in the same hour on the same date will be given the same value)
          'moy': month of the year (i.e., January is 1, February is 2, regardless of the year)
          'doy': day of the year (i.e., January 1st is 1, February 1st is 32, regardless of the year)
        The default value is 'day'.
    __________
    Returns:
      A list of tuples that each contain the indices of a pair of points that are within the temporal threshold of each
       other.
    """

    zs = get_zs(datetimes=datetimes, tm_unit=tm_unit)  # get the Z values

    if tm_unit.lower() in ['year', 'month', 'day', 'hour']:  # if the temporal unit is non-cyclical
        tree = cKDTree(np.array([zs]).T)  # create a cKD tree from the Z values
        pairs_list = list(tree.query_pairs(tm_threshold))  # get indices of pairs that are within the temporal threshold
    elif tm_unit.lower() in ['moy', 'doy']:  # else if the temporal unit is cyclical
        if ((tm_unit == 'moy' and tm_threshold >= 6)  # if temporal threshold equal to or more than half a cycle...
                or (tm_unit == 'doy' and tm_threshold >= 182.5)):  # ...(i.e., 6 months for MOY / 182.5 days for DOY)...
            pairs_list = list(combinations(range(0, len(zs)), r=2))  # ...all pairs overlap, so get all possible pairs
        else:  # else if temporal threshold less than half a cycle...
            tm_threshold_complementary = (  # ...get the complementary threshold
                    12 - tm_threshold) if tm_unit == 'moy' \
                else 365 - tm_threshold if tm_unit == 'doy' \
                else None
            pairs_list = []  # empty pairs list
            for pair in list(combinations(range(0, len(zs)), r=2)):  # for each possible pair
                za = zs[pair[0]]  # get the first z
                zb = zs[pair[1]]  # get the second z
                inner_diff = max(za, zb) - min(za, zb)  # get the inner difference between the Z values
                if (inner_diff <= tm_threshold  # if the inner difference is less than the threshold or...
                        or inner_diff >= tm_threshold_complementary):  # ...more than the complementary threshold...
                    pairs_list.append(pair)  # ...the pair is within the temporal threshold, so append it
    else:  # else unrecognised value for temporal unit
        raise ValueError(" temporal unit not recognised. Please ensure that value for 'tm_unit' is valid.")
    return pairs_list  # list of pairs that are within the temporal threshold of each other


def get_sptm_pairs(coords: list[Point], sp_threshold: int | float,
                   datetimes: list[pd.Timestamp | datetime], tm_threshold: int | float, tm_unit: str = 'day') \
        -> list[tuple[int, int]]:
    """Get pairs of points that are within both the spatial and temporal thresholds.
    Uses get_sp_pairs() and get_tm_pairs() to get, respectively, the pairs of points that are within the spatial and
     temporal thresholds of each other. Then intersects these two lists of pairs to get only those pairs of points that
     are within both the spatial and temporal thresholds of each other.
    __________
    Parameters:
      coords: list[tuple[float | int, float | int] | Point]
        A standardised list of coordinates that are either tuples or shapely.Points as output by get_coords().
      sp_threshold : int | float, optional, default None
        The spatial threshold to use for spatial and spatiotemporal thinning in the units of the coordinates.
      datetimes: list[datetime | pd.Timestamp]
        A standardised list of datetimes that are either datetime.datetimes or pandas.Timestamps as output by
         get_datetimes().
      tm_threshold : int | float, optional, default None
        The temporal threshold to use for temporal and spatiotemporal thinning in the units set with 'tm_unit'.
      tm_unit: {'year', 'month', 'day', 'hour', 'moy', 'doy'}, optional, default 'day'
        The temporal units to use for temporal or spatiotemporal thinning. Must be one of the following:
          'year': year (all datetimes from the same year will be given the same value)
          'month': month (all datetimes from the same month and year will be given the same value)
          'day': day (all datetimes with the same date will be given the same value)
          'hour': hour (all datetimes in the same hour on the same date will be given the same value)
          'moy': month of the year (i.e., January is 1, February is 2, regardless of the year)
          'doy': day of the year (i.e., January 1st is 1, February 1st is 32, regardless of the year)
        The default value is 'day'.
    __________
    Returns:
      A list of tuples that each contain the indices of a pair of points that are within the temporal threshold of each
       other.
    """

    sp_pairs_list = get_sp_pairs(  # get spatial pairs
        coords=coords,
        sp_threshold=sp_threshold)
    tm_pairs_list = get_tm_pairs(  # get temporal pairs
        datetimes=datetimes,
        tm_threshold=tm_threshold,
        tm_unit=tm_unit)
    pairs_list = list(set(sp_pairs_list) & set(tm_pairs_list))  # get spatiotemporal pairs
    return pairs_list  # list of pairs that are within the both the spatial and temporal thresholds of each other


def get_pairs(
        df: pd.DataFrame = None,
        coords: str | pd.Series | list[tuple[int, int], Point] = None,
        sp_threshold: int | float = None,
        datetimes: str | pd.Series | list[str | pd.Timestamp | datetime] = None,
        tm_threshold: int | float = None,
        tm_unit: str = 'day') \
        -> list[tuple[int, int]]:
    """Get pairs of points that are within either the spatial threshold, the temporal threshold, or the spatial and
     temporal thresholds.
    __________
    Parameters:
        df : pandas.DataFrame | geopandas.GeoDataFrame, optional, default None
            A dataframe containing the points to be thinned. If specified, the column(s) containing the coordinates
             and/or datetimes must be specified with the parameters 'coords' and 'datetimes', respectively.
        coords : str | pandas.Series | list[tuple[int, int], Point], optional, default None
            One of the following:
                the name of the column in 'df' that contains the coordinates
                a pandas.Series of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
                a list of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
        sp_threshold : int | float, optional, default None
            The spatial threshold to use for spatial and spatiotemporal thinning in the units of the coordinates. If both a
            spatial and temporal threshold are specified, spatiotemporal thinning will occur. If only a spatial threshold is
            specified, spatial thinning will occur. If only a temporal threshold is specified, temporal thinning will occur.
        datetimes : str | pandas.Series | list[str | pandas.Timestamp | datetime], optional, default None
            One of the following:
                the name of the column in 'df' that contains the datetimes
                a pandas.Series of datetimes as strings, pandas.Timestamps, or datetime.datetimes
                a list of datetimes as strings, pandas.Timestamps, or datetime.datetimes
        tm_threshold : int | float, optional, default None
            The temporal threshold to use for temporal and spatiotemporal thinning in the units set with 'tm_unit'. If both a
            spatial and temporal threshold are specified, spatiotemporal thinning will occur. If only a spatial threshold is
            specified, spatial thinning will occur. If only a temporal threshold is specified, temporal thinning will occur.
        tm_unit : {'year', 'month', 'day', 'hour', 'moy', 'doy'}, optional, default 'day'
            The temporal units to use for temporal or spatiotemporal thinning. Must be one of the following:
                'year': year (all datetimes from the same year will be given the same value)
                'month': month (all datetimes from the same month and year will be given the same value)
                'day': day (all datetimes with the same date will be given the same value)
                'hour': hour (all datetimes in the same hour on the same date will be given the same value)
                'moy': month of the year (i.e., January is 1, February is 2, regardless of the year)
                'doy': day of the year (i.e., January 1st is 1, February 1st is 32, regardless of the year)
            The default value is 'day'.
    __________
    Returns:
      A list of tuples that each contain the indices of a pair of points that are within the spatial and/or temporal
       threshold of each other.
    """

    # Get the close pairs
    if (isinstance(sp_threshold, int | float)  # spatiotemporal: if both a spatial...
            and isinstance(tm_threshold, int | float)):  # ...and temporal threshold are specified...
        coords = get_coords(df=df, coords=coords)  # get coords
        datetimes = get_datetimes(df=df, datetimes=datetimes)  # get datetimes
        pairs = get_sptm_pairs(  # get spatiotemporal pairs
            coords=coords,
            sp_threshold=sp_threshold,
            datetimes=datetimes,
            tm_threshold=tm_threshold,
            tm_unit=tm_unit)
    elif (isinstance(sp_threshold, int | float)  # spatial: if only a spatial threshold is specified...
          and not isinstance(tm_threshold, int | float)):
        coords = get_coords(df=df, coords=coords)  # get coords
        pairs = get_sp_pairs(  # get spatial pairs
            coords=coords,
            sp_threshold=sp_threshold)
    elif (isinstance(tm_threshold, int | float)  # temporal: if only a temporal threshold is specified...
          and not isinstance(sp_threshold, int | float)):
        datetimes = get_datetimes(df=df, datetimes=datetimes)  # get datetimes
        pairs = get_tm_pairs(  # get temporal pairs
            datetimes=datetimes,
            tm_threshold=tm_threshold,
            tm_unit=tm_unit)
    else:  # invalid input
        raise Exception("neither 'sp_threshold' nor 'tm_threshold' specified correctly.")
    return pairs


def selector(pairs: list[tuple[int, int]], no_reps: int = 100) -> list[int]:
    """Select points to remove.
    From the list of pairs that are within the spatial and/or temporal threshold(s) of each other, select the points to
     remove. This is done by selecting those points that are in the highest number of pairs. In doing so, the maximum
     number of points will be retained.
    __________
    Parameters:
      pairs: list[tuple[int, int]]
        The list of pairs that are within the spatial and/or temporal threshold(s) of each other as output by one of
         get_sp_pairs(), get_tm_pairs(), or get_sptm_pairs().
      no_reps : int, optional, default 100
        The number of repetitions to run when conducting thinning. From these repetitions, one of those that retains the
         most points will be output.
    __________
    Returns:
      A list containing the indices of the points that have been selected to be removed.
    """
    
    reps_list = []  # list for the results from each repetition
    for rep_no in range(int(no_reps)):  # for each repetition
        pairs_rep = pairs.copy()  # copy pairs indices
        selected_rep = []  # list for the indices selected to be removed for the repetition
        while pairs_rep:  # while there are pairs in the pairs list for the repetition
            counts = Counter([index for pair in pairs_rep for index in pair])  # count how many pairs each index is in
            count_max = max(counts.values())  # get maximum number of pairs that any index is in
            indices_max = [index for index, count in counts.items() if count == count_max]  # get indices in maximum
            selected_index = choice(indices_max)  # randomly select one of these indices and...
            selected_rep.append(selected_index)  # ...add it to the list of indices that have been selected to be removed
            pairs_rep = [pair for pair in pairs_rep if selected_index not in pair]  # remove pairs that include selected
        reps_list.append({'selected': selected_rep, 'count': len(selected_rep)})  # append selected and count to list

    reps = pd.DataFrame(reps_list)  # make a dataframe of the repetitions
    selected_min = reps['count'].min()  # minimum number of indices that any repetition selected
    reps_min = reps[reps['count'] == selected_min]  # repetitions that selected the minimum number of indices
    rep_min = choice(reps_min.index.tolist())  # randomly select one of these repetitions...
    selected = reps.iloc[rep_min]['selected']  # ...and get its indices selected to be removed and...
    return selected  # ...return them in a list


def remover(selected: list[int],
            df: pd.DataFrame = None,
            coords: pd.Series | list[tuple[int, int], Point] = None,
            datetimes: pd.Series | list[str | pd.Timestamp | datetime] = None,
            ids: list[str | int | float] = None) \
        -> pd.DataFrame | tuple[list, list, list]:
    """Remove points selected to be removed.
    Takes the list of points selected to be removed by selector() and removes them.
    __________
    Parameters:
      selected: list[int]
        A list of the indices of the points selected to be removed by selector().
      df: pandas.DataFrame | geopandas.GeoDataFrame, optional, default None
        A dataframe containing the points to be thinned. If specified, the column(s) containing the coordinates
         and/or datetimes must be specified with the parameters 'coords' and 'datetimes', respectively.
      coords : str | pandas.Series | list[tuple[int, int], Point], optional, default None
        One of the following:
          the name of the column in 'df' that contains the coordinates
          a pandas.Series of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
          a list of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
      datetimes : str | pandas.Series | list[str | pandas.Timestamp | datetime], optional, default None
        One of the following:
          the name of the column in 'df' that contains the datetimes
          a pandas.Series of datetimes as strings, pandas.Timestamps, or datetime.datetimes
          a list of datetimes as strings, pandas.Timestamps, or datetime.datetimes
      ids : pandas.Series | list[str | int | float], optional, default None
        If using the second option for data input, a pandas.Series or list of unique IDs to identify the points that were
         kept after thinning.
    __________
    Returns:
      One of the following, depending on the input:
        pandas.DataFrame | geopandas.GeoDataFrame
          If using the first input option, a pandas.DataFrame or a geopandas.GeoDataFrame, depending on which was input,
            containing only those points that were kept after thinning.
        tuple[list | list | list]
          If using the second input option, a tuple containing three lists that contain the coordinates, datetimes, and
           IDs, respectively. If one or more of the coordinates, datetimes, and IDs is not input, an empty list will be
           returned in its place (meaning that the tuple will always have three elements: coordinates, datetimes, IDs).
    """

    if isinstance(df, pd.DataFrame):  # if a pandas.DataFrame or geopandas.GeoDataFrame is specified...
        thinned_df = df.copy().reset_index(drop=True)  # copy it and reset index
        thinned_df = thinned_df.loc[~thinned_df.index.isin(selected)]  # remove the indices selected to be removed
        return thinned_df  # return the thinned pandas.DataFrame / geopandas.GeoDataFrame
    else:  # if a pandas.DataFrame or geopandas.GeoDataFrame is not specified
        thinned_coords = [coords[i] for i in range(len(coords)) if i not in selected] \
            if (isinstance(coords, list)) else None  # get thinned coords (if coords provided) based on selected
        thinned_datetimes = [coords[i] for i in range(len(datetimes)) if i not in selected] \
            if (isinstance(datetimes, list)) else None  # get thinned datetimes (if datetimes provided) based on selected
        thinned_ids = [coords[i] for i in range(len(ids)) if i not in selected] \
            if (isinstance(ids, list)) else None  # get thinned ids (if ids provided) based on selected
        return thinned_coords, thinned_datetimes, thinned_ids  # return the thinned coords, datetimes, and IDs


def thinner(
        pairs: list[tuple[int, int]],
        df: pd.DataFrame = None,
        coords: str | pd.Series | list[tuple[int, int], Point] = None,
        datetimes: str | pd.Series | list[str | pd.Timestamp | datetime] = None,
        ids: pd.Series | list[str | int | float] = None,
        no_reps: int = 100) \
        -> pd.DataFrame | tuple[list | list | list]:
    """Thin points.

    pairs: list[tuple[int, int]]
        The list of pairs that are within the spatial and/or temporal threshold(s) of each other as output by
         get_pairs().
    df : pandas.DataFrame | geopandas.GeoDataFrame, optional, default None
        Optionally, a dataframe containing the points to be thinned. If specified, the column(s) containing the
         coordinates and/or datetimes must be specified with the parameters 'coords' and 'datetimes', respectively.
    coords : str | pandas.Series | list[tuple[int, int], Point], optional, default None
        One of the following:
            the name of the column in 'df' that contains the coordinates
            a pandas.Series of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
            a list of coordinates as tuples, e.g., (X, Y), or as shapely.Points, e.g., POINT (X, Y)
    datetimes : str | pandas.Series | list[str | pandas.Timestamp | datetime], optional, default None
        One of the following:
            the name of the column in 'df' that contains the datetimes
            a pandas.Series of datetimes as strings, pandas.Timestamps, or datetime.datetimes
            a list of datetimes as strings, pandas.Timestamps, or datetime.datetimes
    ids : pandas.Series | list[str | int | float], optional, default None
        If using the second option for data input, a pandas.Series or list of unique IDs to identify the points that
         were kept after thinning.
    no_reps : int, optional, default 100
        The number of repetitions to run when conducting thinning. From these repetitions, one of those that retains the
         most points will be output.
    """

    # thin
    if len(pairs) > 0:  # if there are close pairs (i.e., if thinning is required)...
        selected = selector(  # ...select the indices to be removed and...
            pairs=pairs,
            no_reps=no_reps)
        removed = remover(  # ...remove them
            selected=selected,
            df=df,
            coords=coords,
            datetimes=datetimes,
            ids=ids)
        return removed
    else:  # else if there are no close pairs (i.e., if thinning is not required), return what was input
        if isinstance(df, pd.DataFrame):  # if a pandas.DataFrame or geopandas.GeoDataFrame input...
            return df  # ...return it
        else:  # else...
            return coords, datetimes, ids  # ...return the coords, datetimes, and IDs in a tuple
