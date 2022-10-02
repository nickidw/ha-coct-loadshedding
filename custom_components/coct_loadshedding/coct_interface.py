import ssl

from aiohttp.client_exceptions import ClientConnectorError, ServerDisconnectedError
from aiohttp_retry import RetryClient
from datetime import datetime
import yaml
import pandas as pd
import pytz

class coct_interface:
    """Interface class to obtain loadshedding information using the https://github.com/beyarkay/eskom-calendar repo"""

    def __init__(self):
        """Initializes class parameters"""

        self.base_url = "https://github.com/beyarkay/eskom-calendar"
        self.headers = {
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0"
        }
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")

    async def async_query_api(self, endpoint, payload=None):
        """Queries a given endpoint on the eskom-calendar repo with the specified payload

        Args:
            endpoint (string): The endpoint of the eskom-calendar repo
            payload (dict, optional): The parameters to apply to the query. Defaults to None.

        Returns:
            The response object from the request
        """
        async with RetryClient() as client:
            async with client.get(
                url=endpoint,
                headers=self.headers,
                params=payload,
                ssl=self.ssl_context,
                retry_attempts=50,
                retry_exceptions={
                    ClientConnectorError,
                    ServerDisconnectedError,
                    ConnectionError,
                    OSError,
                },
            ) as res:
                return await res

    async def async_get_stage(self, currentTime, attempts=5):
        """Fetches the current loadshedding stage from the eskom-calendar repo

        Args:
            attempts (int, optional): The number of attempts to query a sane value from the eskom-calendar repo. Defaults to 5.

        Returns:
            The loadshedding stage if the query succeeded, else `None`
        """

        # Placeholder for returned loadshedding stage
        api_result = None

        # Query the API until a sensible (> 0) value is received, or the number of attempts is exceeded
        for attempt in range(attempts):
            res = await self.async_query_api("https://raw.githubusercontent.com/beyarkay/eskom-calendar/main/manually_specified.yaml")

            # Check if the API returned a valid response
            if res:
                # load the yaml and look through all changes items
                yml = yaml.safe_load(res)
                currentstage = 0
                
                for change in yml['changes']:
                    coct = False
                    for k, v in change.items():
                        if 'include' in k and 'coct' in v:
                            coct = True
                    if coct:
                        if change['start'] < currentTime and change['finsh'] > currentTime:
                            currentstage = change['stage']
                
                api_result = currentstage

                # Only return the result if the API returned a non-negative stage, otherwise retry
                if int(currentstage) > 0:
                    # Return the current loadshedding stage
                    return int(currentstage)

        if api_result:
            # If the API is up but returning "invalid" stages (< 0), simply return 0
            return 0
        else:
            # If the API the query did not succeed after the number of attempts has been exceeded, raise an exception
            raise Exception(
                f"Error, no response received from API after {attempts} attempts"
            )

    async def async_get_status(self, currentTimeUTC, attempts=5):
        """Fetches the current loadshedding status from the eskom-calendar repo

        Args:
            attempts (int, optional): The number of attempts to query a sane value from the eskom-calendar repo. Defaults to 5.

        Returns:
            The loadshedding status if the query succeeded, else `None`
        """
        url = "https://github.com/beyarkay/eskom-calendar/releases/download/latest/machine_friendly.csv"
        df = pd.read_csv(url, parse_dates=['start', 'finsh'])
        #TODO the hardcoded area needs to be passed from config
        coct1 = df[df['area_name'].str.endswith('city-of-cape-town-area-1')] 
        prevstart = currentTimeUTC
        current = "None"
        nextslot = "None"
        upcoming = ""

        for i in range(coct1.index.size-1):
            instance = coct1.iloc[i]
            start = instance["start"]
            finsh = instance["finsh"]
            stage = instance["stage"]

            if currentTimeUTC > start and currentTimeUTC < finsh:
                current = f"In loadshedding From {start} to {finsh} stage {stage}"
            if prevstart < currentTimeUTC and start > currentTimeUTC:
                nextslot = f"Next loadshedding From {start} to {finsh} stage {stage}"
            if start > currentTimeUTC and prevstart > currentTimeUTC:
                upcoming += f"Upcoming loadshedding From {start} to {finsh} stage {stage}"
            prevstart = start

        data = {
            "current": current,
            "next": nextslot,
            "upcoming": upcoming,
        }
    async def async_get_data(self):
        """Fetches data from the loadshedding API"""
        currentTime = datetime.now()

        utc = pytz.timezone('Africa/Johannesburg')
        nowutc = utc.localize(currentTime)

        stage = await self.async_get_stage(currentTime)
        status = await self.async_get_status(nowutc)
        data = {
            "data": {"stage": stage,
            "current": status["current"],
            "next": status["next"],
            "upcoming": status["upcoming"]},
        }
        return data
