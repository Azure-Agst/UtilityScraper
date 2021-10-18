# flake8: noqa

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from modules.config import Config
from modules.utilitydata import UtilityData

##########################################################################
#                                                                        #
# be warned, all ye who trespass here!                                   #
# this file is purposely ignored from linting, because there is no way   #
# i can get some of these xpaths to fit in the character limit. such is  #
# the way of selenium. brace yourselves for what's ahead!                #
#                                                                        #
##########################################################################

class TalgovScraperException(Exception):
    pass

class TalgovScraper:
    def __init__(self, config: Config):
        self.config = config
        self.driver = None

    def __del__(self):
        pass

    def _init_driver(self):
        """Initializes main Firefox driver"""

        # see if driver exists, if so skip
        if self.driver is None:

            # print a message to the console
            print(f"Starting {('headless ' if self.config.headless else '')}firefox driver... ")

            # create options for driver, if headless is requested
            if self.config.headless:
                options = Options()
                options.add_argument("-headless")
                self.driver = webdriver.Firefox(options=options)
            else:
                self.driver = webdriver.Firefox()

        else:
            # print error message to console
            print("Firefox driver already initialized, skipping initialization...")

    def scrape_data(self) -> UtilityData:
        """Returns a UtilityData object containing the data from the website"""

        # initialize selenium driver, if not already initialized
        self._init_driver()

        # load main entrypoint and wait until loaded
        print("Loading entrypoint & logging in...")
        self.driver.get(self.config.v_entry_url)
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, 'cphBody_cphCenter_cbtnLogin')))

        # enter username/password and try logging in
        self.driver.find_element_by_id("cphBody_cphCenter_ctbxLoginEmail").send_keys(self.config.v_username)
        self.driver.find_element_by_id("cphBody_cphCenter_ctbxPassword").send_keys(self.config.v_password)
        self.driver.find_element_by_id("cphBody_cphCenter_cbtnLogin").click()

        # error handling
        # if login fails, a popup appears. handle that.
        try:
            WebDriverWait(self.driver, 2).until(EC.alert_is_present(), "Timed out waiting for error alert, logged in!")
            alert = self.driver.switch_to.alert
            alert.accept()
            raise TalgovScraperException("Login Failed!")
        except TimeoutException:
            print("Login successful!")

        # by this point, assume e+ home is loaded, swap to its iframe
        WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="eplusFrame"]')))

        # click the "view usage" button
        self.driver.find_element_by_id('rpaccounts_btnViewAccount_0').click()

        # wait for the usage table to load, then start scraping data :)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'ctl06_lblAccount')))

        # start with the account information
        print("Scraping account information...")
        r_acct_num = self.driver.find_element_by_id('ctl06_lblAccount').text
        r_acct_bal = self.driver.find_element_by_id('ctl20_ctl00_billSummaryControl_lblAccountBalance').text
        r_last_bill = self.driver.find_element_by_id('ctl20_ctl00_billSummaryControl_lblBillDateLabel').text
        r_next_bill = self.driver.find_element_by_id('ctl20_ctl00_billSummaryControl_lblAmountDueLabel').text

        # wait for monthly estimates to load
        print("Scraping monthly estimates... (May take a second to load!)")
        e_billing_xpath = '/html/body/form/table/tbody/tr/td/table/tbody/tr/td[2]/div[11]/div[2]/table/tbody/tr/td/div/div/table[2]/tbody/tr'
        e_td_dict = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, e_billing_xpath))
        ).find_elements_by_tag_name("td")

        # parse static data from monthly estimates
        r_e_usage = e_td_dict[2].text
        r_e_usage_date = e_td_dict[0].text

        # parse monthly estimate table
        r_e_breakdown = {}
        e_breakdown_xpath = '/html/body/form/table/tbody/tr/td/table/tbody/tr/td[2]/div[11]/div[2]/table/tbody/tr/td/div/div/div/table/tbody'
        e_breakdown_children = self.driver.find_element_by_xpath(e_breakdown_xpath).find_elements_by_tag_name("tr")
        for tr in e_breakdown_children:
            tds = tr.find_elements_by_tag_name("td")
            if len(tds) < 2:
                continue
            else:
                # text attribute broken for td? have to get innerHTML instead. weird.
                t_service_name = tds[0].get_attribute("innerHTML")
                t_service_usage = tds[1].get_attribute("innerHTML")
                r_e_breakdown[t_service_name] = float(t_service_usage[1:])

        # close our driver
        print("Done! Wrapping up...")
        self.driver.close()

        # return the data
        return UtilityData(
            vendor="Talgov",
            account_num=r_acct_num,
            account_bal=float(r_acct_bal[1:]),
            last_bill=datetime.strptime(r_last_bill.replace("Bill Summary ending ", ""), "%m/%d/%Y"),
            next_bill=datetime.strptime(r_next_bill.replace("Amount Due ", ""), "%m/%d/%Y"),
            e_usage=float(r_e_usage[1:]),
            e_usage_date=datetime.strptime(r_e_usage_date.replace("Estimated cost as of ", ""), "%m/%d/%Y"),
            e_breakdown=r_e_breakdown
        )

def setup(parser, config):
    parser.add_scraper(TalgovScraper(config))
