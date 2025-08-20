from retry import retry
from herbie import FastHerbie


class NoGribFilesFoundError(Exception):
    """Raised when no GRIB files are found for the specified date/model run."""
    pass


@retry(NoGribFilesFoundError, tries=5, delay=15, max_delay=60, backoff=2)
def get_fast_herbie_object(date: str) -> FastHerbie:
    """
    Get a FastHerbie object for the specified date. Raises an exception when no GRIB files are found.

    Args:
        date: pandas-parsable datetime string
        
    Returns:
        A FastHerbie object configured for the specified date.
        
    Raises:
        NoGribFilesFoundError: If no GRIB files are found for the specified date.
    """
    fast_herbie = FastHerbie([date], model="ifs", fxx=range(0, 360, 3))
    
    if len(fast_herbie.file_exists) == 0:
        raise NoGribFilesFoundError(f"No GRIB files found for the specified date {date}.")
    
    return fast_herbie