import pandas as pd
import requests
import time

LOGIN_URL = 'https://sg5.fusionsolar.huawei.com/pvmswebsite/login/build/index.html'
HISTORICAL_API_URL = 'https://sg5.fusionsolar.huawei.com/rest/pvms/web/station/v3/overview/energy-balance'

USER_XPATH = '//*[@id="username"]/input'
PASSWORD_XPATH = '//*[@id="password"]/input'
LOGIN_XPATH = '//*[@id="submitDataverify"]'

IMG_XPATH = '//*[@id="dpFrameworkHeader"]/div/div[1]/div[1]/div/div/a[1]/img'


# 24 hours * 12 intervals per hour
EMPTY = [None] * (24 * 12)


class Sg5Scraping:

    def __init__(self, playwright):
        self.playwright = playwright
        self.page = None


    def open_browser(self, headless: bool ) -> None:
        browser = self.playwright.chromium.launch(headless=headless)
        self.page = browser.new_page()
        self.page.goto(LOGIN_URL)
        print("Page opened")


    def login(self, username: str, password: str) -> None:
       self.__fill(USER_XPATH, username)
       self.__fill(PASSWORD_XPATH, password)   
       self.__click(LOGIN_XPATH)

       self.__get_session()


    def __get_session(self) -> None:
        self.__wait(IMG_XPATH)
        print("Logged in")

        cookies = self.page.context.cookies()
        print("Cookies acquired")

        self.session = requests.Session()
        for cookie in cookies:
            self.session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie['domain'])
        print("Session acquired")


    def historical_api(self, location: str, date_str: str) -> pd.DataFrame:
        api_params = {
            "stationDn": f"NE={location}",
            "timeDim": "2",
            "timeZone": "7.0",
            "timeZoneStr": "Asia/Bangkok",
            "queryTime": f'{int(time.mktime(time.strptime(date_str, "%Y-%m-%d")) * 1000)}',
            "dateStr": f"{date_str} 00:00:00",
            "_": str(int(time.time() * 1000))
        }

        api_headers = {
            "Content-Type": "application/json"
        }

        response = self.session.get(HISTORICAL_API_URL,
                params=api_params,
                headers=api_headers)
        if response.status_code == 200:
            return self.__to_df(response.json())

        return pd.DataFrame()


    def __to_df(self, data: dict) -> pd.DataFrame:

        productPower = data['data'].get('productPower')
        if productPower is None or len(productPower) == 0:
            productPower = EMPTY

        radiationDosePower = data['data'].get('radiationDosePower') 
        if radiationDosePower is None or len(radiationDosePower) == 0:
            radiationDosePower = EMPTY

        meter = data['data'].get('meterActivePower')
        if meter is None or len(meter) == 0:
            meter = EMPTY

        usePower = data['data'].get('usePower')
        if usePower is None or len(usePower) == 0:
            usePower = EMPTY

        chargePower = data['data'].get('chargePower')
        if chargePower is None or len(chargePower) == 0:
            chargePower = EMPTY

        dischargePower = data['data'].get('dischargePower')
        if dischargePower is None or len(dischargePower) == 0:
            dischargePower = EMPTY

        chargeAndDisChargePower = data['data'].get('chargeAndDisChargePower')
        if chargeAndDisChargePower is None or len(chargeAndDisChargePower) == 0:
            chargeAndDisChargePower = EMPTY

        dieselProductPower = data['data'].get('dieselProductPower')
        if dieselProductPower is None or len(dieselProductPower) == 0:
            dieselProductPower = EMPTY

        mainsUsePower = data['data'].get('mainsUsePower')
        if mainsUsePower is None or len(mainsUsePower) == 0:
            mainsUsePower = EMPTY

        generatorPower = data['data'].get('generatorPower')
        if generatorPower is None or len(generatorPower) == 0:
            generatorPower = EMPTY

        businessChargePower = data['data'].get('businessChargePower')
        if businessChargePower is None or len(businessChargePower) == 0:
            businessChargePower = EMPTY

        df = pd.DataFrame({
            'date_time': data['data']['xAxis'],
            'product_power_kw': productPower,
            'radiation': radiationDosePower,
            'meter_kw': meter,
            'use_power_kw': usePower,
            'charge_power_kw': chargePower,
            'discharge_power_kw': dischargePower,
            'charge_and_discharge_power_kw': chargeAndDisChargePower,
            'diesel_product_power_kw': dieselProductPower,
            'mains_use_power_kw': mainsUsePower,
            'generator_power_kw': generatorPower,
            'business_charge_power_kw': businessChargePower,
        })

        df['date_time'] = pd.to_datetime(df['date_time'])

        return df


    def __fill(self, xpath: str, value: str):
        input = self.page.locator(xpath)
        input.wait_for()
        input.fill(value)
        return input
    
    def __click(self, xpath: str) -> None:
        button = self.page.locator(xpath)
        button.wait_for()
        button.click()

    def __check(self, xpath: str) -> None:
        checkbox = self.page.locator(xpath)
        if not checkbox.is_checked():
            checkbox.check()
    
    def __select_option(self, xpath: str, label=None, index=None) -> None:
        select = self.page.locator(xpath)
        select.select_option(label=label, index=index)
    
    def __hover(self, xpath: str) -> None:
        element = self.page.locator(xpath)
        element.hover()
    
    def __wait(self, xpath: str, timeout: int = 30000) -> None:
        path = self.page.locator(xpath)
        path.wait_for(timeout=timeout)
