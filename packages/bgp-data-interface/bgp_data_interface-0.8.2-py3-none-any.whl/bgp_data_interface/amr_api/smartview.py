# libs
from datetime import datetime
from io import StringIO
import os
import pandas as pd
import time

# Chrome driver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

LOADPROFILE_URL = "https://smartview.bgrimmpower.com/Elec/LoadProfile"

USERNAME_XPATH = '//*[@id="txt_Username"]'
PASSWORD_XPATH = '//*[@id="txt_Password"]'
CUSTOMER_XPATH = '//*[@id="ContentPlaceHolder1_cmb_Contract_I"]'
DAY_XPATH = '//*[@id="ContentPlaceHolder1_cmb_Day_I"]'
MONTH_XPATH = '//*[@id="ContentPlaceHolder1_cmb_month_I"]'
YEAR_XPATH = '//*[@id="ContentPlaceHolder1_cmb_year_I"]'
# VIEW_BUTTON_XPATH = '//*[@id="ContentPlaceHolder1_btn_View_CD"]/span'

class Smartview:
    def __init__(self, username: str, password: str) -> None:
        self.__open_url()
        self.__login(username, password)

    def __open_url(self) -> None:
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.get(LOADPROFILE_URL)

    def __login(self, username: str, password: str) -> None:
        self.__text_enter(USERNAME_XPATH, username)
        self.__text_enter(PASSWORD_XPATH, password)

    def __text_enter(self, xpath: str, value: str) -> None:
        self.driver.find_element(By.XPATH, xpath) \
            .send_keys(value + Keys.ENTER)

    def get_customer_loads(self,
            customers: list,
            start_date: datetime,
            end_date: datetime) -> pd.DataFrame:
        
        self.__download_daily_loads(customers, start_date, end_date)

        all_customers = pd.DataFrame({
            'date_time': pd.date_range(start_date, end_date, freq='15min')
        })
        
        for customer in customers:
            customer_dir = os.path.join('forecast', 'streaming', 'outputs',
                'smartview_data', customer)

            one_customer = pd.DataFrame()
            for date in pd.date_range(start_date, end_date, freq='D'):
                filename = date.strftime("%Y%m%d")
                one_day = pd.read_csv(f"{customer_dir}/{filename}.csv")
                one_day['date_time'] = pd.to_datetime(one_day['date_time'], format="%d/%m/%Y %H:%M:%S")
                one_customer = pd.concat([one_customer, one_day], ignore_index=True)

            all_customers[customer + ' kw'] = one_customer['kw']
            all_customers[customer + ' kvar'] = one_customer['kvar']

        return all_customers

    def __download_daily_loads(self,
        customers: list,
        start_date: datetime,
        end_date: datetime) -> None:

        for customer in customers:

            output_dir = os.path.join('forecast', 'streaming', 'outputs',
                'smartview_data', customer)
            os.makedirs(output_dir, mode=755, exist_ok=True) 
            
            self.__input_combo(CUSTOMER_XPATH, customer)
            self.__input_combo(YEAR_XPATH, str(start_date.year))
            self.__input_combo(MONTH_XPATH, start_date.strftime("%B"))
            self.__input_enter(MONTH_XPATH)
            time.sleep(5)

            for current_date in pd.date_range(start_date, end_date, freq='D'):
                one_day_path = os.path.join(output_dir,
                    current_date.strftime('%Y%m%d') + ".csv")
                if os.path.exists(one_day_path):
                    continue

                df = self.__extract_from_page(current_date)
                df.to_csv(one_day_path, index=False)

    def __input_combo(self, xpath: str, value: str) -> None:
        combo = self.driver.find_element(By.XPATH, xpath)
        combo.send_keys(Keys.CONTROL + 'a')
        combo.send_keys(value)

    def __input_enter(self, xpath: str) -> None:
        combo = self.driver.find_element(By.XPATH, xpath)
        combo.send_keys(Keys.ENTER)

    def __extract_from_page(self, current_date: datetime) -> pd.DataFrame:
        self.__input_combo(YEAR_XPATH, str(current_date.year))
        self.__input_combo(MONTH_XPATH, current_date.strftime("%B"))
        self.__input_combo(DAY_XPATH, str(current_date.day))
        self.__input_enter(DAY_XPATH)
        time.sleep(2)

        data_list = pd.read_html(StringIO(self.driver.page_source))
        df = data_list[len(data_list) - 1].copy()
        df = df.drop(index=0)

        # not sure why output columns keep changing 
        column_map = {
            6: {0: 'date_time', 1: 'kw', 2: 'kvar'},
            7: {1: 'date_time', 2: 'kw', 3: 'kvar'}
        }
        df = df.rename(columns=column_map[len(df.columns)])

        return df[['date_time', 'kw', 'kvar']]
