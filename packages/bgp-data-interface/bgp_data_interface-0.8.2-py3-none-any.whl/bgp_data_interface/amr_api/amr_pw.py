from datetime import datetime
from io import StringIO
import os
import pandas as pd

LOGIN_URL ="https://amr.bgrimmpower.com/amr/Login.aspx"
LOAD_PROFILE_URL = "https://amr.bgrimmpower.com/amr/branch/{:s}/AMR/Report/PivotLoadProfilePage.aspx"

USERNAME_XPATH = '//*[@id="UserName"]'
PASSWORD_XPATH = '//*[@id="MainContent_LoginUser_Password"]'
DATE_INPUT_XPATH = '//*[@id="MainContent_de_DateUntil_I"]'
LOAD_PROFILE_INPUT_XPATH = '//*[@id="MainContent_cbb_LPData_I"]'
SHOW_BUTTON_XPATH = '//*[@id="MainContent_btn_Show_CD"]/span'
PAGE2_XPATH = '//*[@id="MainContent_gv_PivotLP_DXPagerBottom"]/a[1]'

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"

WAIT_FOR_DATE_JS = """() => {{
    const el = document.querySelector("#MainContent_gv_PivotLP_col3 > table > tbody > tr > td")
    return el && el.textContent === '{:s}'
}}
"""

WAIT_FOR_PAGE2 = """() => {{
    const el = document.querySelector('#MainContent_gv_PivotLP_DXPagerBottom > b.dxp-lead.dxp-summary')
    return el && el.textContent.startsWith('Page 2')
}}
"""

AMR_COLUMNS = ['Customer', 'meter_code'] + \
    [f'{hour:02}:{minute:02}' for hour in range(24) for minute in range(0, 60, 15)]

class AMR:
    def __init__(self, playwright):
        self.playwright = playwright

    async def login(self, username: str, password: str) -> None:
        chrome = await self.playwright.chromium.launch(headless=True)
        self.page = await chrome.new_page(user_agent=USER_AGENT)

        await self.page.goto(LOGIN_URL)
        print("login page opened")

        await self.__fill(USERNAME_XPATH, username)
        print("username filled")

        password_input = await self.__fill(PASSWORD_XPATH, password)
        await password_input.press("Enter")
        print("password entered")

    async def __fill(self, xpath: str, value: str):
        input = self.page.locator(xpath)
        await input.wait_for()
        await input.fill(value)
        return input

    async def load_profile_report(self,
        group: str,
        unit: str,
        start_date: datetime,
        end_date: datetime) -> pd.DataFrame:

        url = LOAD_PROFILE_URL.format(group)
        await self.page.goto(url)
        print("load profile page opened")

        await self.__download_daily_loads(group, unit, start_date, end_date)

        all_df = pd.DataFrame()
        for current_date in pd.date_range(start_date, end_date):

            output_dir = os.path.join('forecast', 'streaming', 'outputs',
                'amr', group)
            one_day_path = os.path.join(output_dir,
                current_date.strftime('%Y%m%d') + ".csv")
            df = pd.read_csv(one_day_path)
            df = df.drop(columns=['meter_code'])
            df = pd.melt(df,
                id_vars=['Customer'],
                var_name='Date_time',
                value_name='Load (kW)')
            df['Date_time'] = pd.to_datetime(
                current_date.strftime("%Y-%m-%d ") + df['Date_time']
            )
            # df.insert(0, 'Date_time', df.pop('Date_time'))
            all_df = df if all_df.empty else pd.concat([all_df, df])
        
        all_df = all_df.sort_values(by=['Customer', 'Date_time'])
        all_df = all_df.dropna()

        return all_df

    async def __download_daily_loads(self,
        group: str,
        unit: str,
        start_date: datetime,
        end_date: datetime) -> None:

        output_dir = os.path.join('forecast', 'streaming', 'outputs',
            'amr', group)
        os.makedirs(output_dir, mode=755, exist_ok=True) 
        
        for current_date in pd.date_range(start_date, end_date, freq='D'):
            one_day_path = os.path.join(output_dir,
                current_date.strftime('%Y%m%d') + ".csv")
            if os.path.exists(one_day_path):
                continue

            df = await self.__extract_from_page(current_date, unit)
            df.to_csv(one_day_path, index=False)
            print("one day saved")

    async def __extract_from_page(self,
        current_date: datetime,
        unit: str) -> pd.DataFrame:

        await self.page.reload()
        await self.__fill(DATE_INPUT_XPATH, current_date.strftime('%d/%m/%Y'))
        print(str(current_date) + " date filled")

        await self.__fill(LOAD_PROFILE_INPUT_XPATH, unit)
        print("unit filled")

        await self.__click(SHOW_BUTTON_XPATH)
        print("button clicked")

        wait_for_date_js = WAIT_FOR_DATE_JS.format(
            str(current_date.day) + current_date.strftime(" %b %Y")
        )
        await self.page.wait_for_function(wait_for_date_js)
        print("ajax loaded")

        df = await self.__read_table()
        if await self.__has_element(PAGE2_XPATH):
            await self.__click(PAGE2_XPATH)
            await self.page.wait_for_function(WAIT_FOR_PAGE2)
            df2 = await self.__read_table()
            print("page2 loaded")
            df = pd.concat([df, df2])

        df.columns = AMR_COLUMNS

        return df

    async def __click(self, xpath: str):
        el = self.page.locator(xpath)
        await el.wait_for()
        await el.click()
    
    async def __read_table(self) -> pd.DataFrame:
        page_source = await self.page.content()
        data_list = pd.read_html(StringIO(str(page_source)))

        return data_list[len(data_list) - 2].iloc[1:, 0:98]

    async def __has_element(self, xpath: str) -> bool:
        el = self.page.locator(xpath)
        count = await el.count()

        return count > 0
