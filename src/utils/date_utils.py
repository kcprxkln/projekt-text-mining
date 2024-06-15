from datetime import datetime, timedelta
import pytz
from typing import Tuple

TIMEZONE = pytz.timezone('America/New_York')

def get_start_and_end_of_day(pytz_timezone: str) -> Tuple[datetime, datetime]:
    """
    Get the start and end datetime objects for the specified timezone.
    
    Args:
    - pytz_timezone (str): A string representing the timezone. 
      Use one of the timezones from the pytz module. 
      See the full list of pytz timezones here: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    
    Returns:
    - Tuple[datetime, datetime]: A tuple containing two datetime objects representing the start and end of the day in the specified timezone.
    """
    timezone  = pytz.timezone(pytz_timezone) #https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568:

    now = datetime.now(timezone)
    today = now.date()

    start_of_today = timezone.localize(datetime(today.year, today.month, today.day))
    end_of_today = start_of_today + timedelta(days=1) 
    
    return start_of_today, end_of_today 