from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
import pytz
import requests
from typing import List, Dict, Any
from urllib.parse import urlencode

BASE_URL = 'https://pi-api.bgrimmpower.com/piwebapi'
CRT_FILE = './src/bgp_data_interface/pi_api/_.bgrimmpower.crt'

HEADERS = {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Cache-Control": "no-cache"
}

tz = pytz.timezone('Asia/Bangkok')

class PI_API:

    username: str
    password: str

    def __init__(self,
                 username: str,
                 password: str) -> None:

        self.username = username
        self.password = password

    def get_webids(self,
                   server: str,
                   tag_list: List[str]) -> List[str]:
        web_ids: List[str] = []
        for tag in tag_list:
            url = f"{BASE_URL}/points?path={server}{tag}"

            response = requests.get(url, 
                                    auth=(self.username, self.password),
                                    verify=CRT_FILE)
            if response.status_code == 200:
                data = response.json()
                web_ids.append(data['WebId'])
            else:
                print(f"Error fetching WebId for tag {tag}: {response.status_code}")
                print(response.text)

        return web_ids

    def get_summary(self,
                    tag_webids: pd.DataFrame,
                    params: Dict[str, Any],
                    start_time: datetime,
                    end_time: datetime) -> pd.DataFrame:

        data = {}
        for tag, webid in np.array(tag_webids):
            all_params: Dict[str, Any] = params | {
                'webid': webid,
                'startTime': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'endTime': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            }

            url = f"{BASE_URL}/streamsets/summary?" + urlencode(all_params)
            data[tag] = {
                'Method': 'GET',
                'Resource': url
            }

        response = requests.post(
            f"{BASE_URL}/batch",
            headers=HEADERS,
            data=json.dumps(data),
            auth=(self.username, self.password),
            verify=CRT_FILE
        )

        if response.status_code == 207:
            tag_response = list(response.json().values())
            datetime_df: pd.DataFrame = self._extract_datetime(tag_response)
            output_df: pd.DataFrame = self._extract_output(tag_response, tag_webids)
            df = pd.concat([datetime_df, output_df], axis=1)

            return df

        print(f'Error: {response.status_code} - {response.text}')
        return pd.DataFrame()  # Return an empty DataFrame in case of error

    def _extract_datetime(self,
                          tag_response: List[Dict[str, Any]]) -> pd.DataFrame:

        first_summary = tag_response[0]['Content']['Items'][0]['Items']
        timestamps = list(map((lambda v: v['Value']['Timestamp']), first_summary))
        date_time = list(map((lambda v: 
            (datetime.fromisoformat(v) + timedelta(minutes=15)).astimezone(tz)),
            timestamps))

        df = pd.DataFrame([])
        df['Date_time'] = date_time
        df['Date_time'] = df['Date_time'].dt.tz_localize(None)

        return df

    def _extract_output(self,
                          tag_response: List[Dict[str, Any]],
                          tag_webids: pd.DataFrame) -> pd.DataFrame:

        df = pd.DataFrame()
        for summaries in tag_response:
            for summary in summaries['Content']['Items']:
                df[summary['Name']] = \
                    [item['Value']['Value'] for item in summary['Items']]

        df = df.reindex(tag_webids.iloc[:, 0], axis=1)

        return df
    
    def get_latest_summary(self,
                            tag_webids: pd.DataFrame,
                            params: Dict[str, Any]) -> pd.DataFrame:

        current_minute = datetime.now().replace(second=0, microsecond=0)
        end_time = current_minute - timedelta(minutes=current_minute.minute % 15)
        start_time = end_time - timedelta(minutes=15)

        return self.get_summary(tag_webids, params, start_time, end_time)
