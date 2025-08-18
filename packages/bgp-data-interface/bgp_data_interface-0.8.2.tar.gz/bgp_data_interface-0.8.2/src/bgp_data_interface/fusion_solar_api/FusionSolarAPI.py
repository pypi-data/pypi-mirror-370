from bgp_data_interface.fusion_solar_api.sg5_scraping import Sg5Scraping
import pandas as pd
from playwright.sync_api import sync_playwright
from typing import Any

DEFAULT_FS_CODE = "51085076" 
DEFAULT_DAY = pd.Timestamp.now() - pd.Timedelta(days=1)

class FusionSolarAPI:

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


    def historical(self, params: dict[str, Any]
            ) -> pd.DataFrame:

        location = params.get('fs_code', DEFAULT_FS_CODE)
        sdate = params.get('start_date', DEFAULT_DAY.strftime('%Y-%m-%d'))
        edate = params.get('end_date', DEFAULT_DAY.strftime('%Y-%m-%d'))

        with sync_playwright() as p:
            fs = Sg5Scraping(p)
            fs.open_browser(headless=True)
            fs.login(self.username, self.password)

            return self.__retrieve_historical(fs, location, sdate, edate)

        return pd.DataFrame()


    def __retrieve_historical(self,
            fs: Sg5Scraping,
            location: str,
            start_date: str,
            end_date: str
            ) -> pd.DataFrame:

        all_df = []
        for curr in pd.date_range(start=start_date, end=end_date):
            date_str = curr.strftime('%Y-%m-%d')
            df = fs.historical_api(location, date_str)
            all_df.append(df)

        return pd.concat(all_df, ignore_index=True)
