import math
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# This is an instantiated class because originally, it was going to read the live data, which needs a dev key.
#
# Later on, I found this library. I did this because I don't trust screen scrapers - but I implemented that anyway
# because it's the only thing that would solve the stated assignment.
class Web:
    planner_url = "http://www.mta.info"
  
    def from_planner(self):        
        browser = self.__generate_driver()
        browser.get(self.__class__.planner_url)
        delay = 2
        try:
            myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.subway_GoodService')))
        except TimeoutException:
            raise Exception("could not load the webpage")
            
        try:
            items = browser.find_elements_by_css_selector("#subwayDiv .subwayCategory")
            all_lines = list(map(self.__class__.__parse_planner_status_row, items))
            return list(line for lines in all_lines for line in lines)
        except:
            # We would need to catch this exception to notify that we need to change our scraping
            raise Exception("improperly formatted page")
    
    def __generate_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        return webdriver.Chrome(chrome_options=chrome_options)
    
    
    @classmethod
    def __parse_planner_status_row(cls, item):
        lines = []
        if item.get_attribute("id") == "SIR":
            lines = ["SIR"]
        else:
            lines = list(item.get_attribute("id"))
        
        classes = item.get_attribute("class")
        status = "delays"
        if "subway_GoodService" in classes:
            status = "good"
        elif "subway_PlannedWork" in classes:
            status = "planned_work"
        elif "subway_ServiceChange" in classes:
            status = "service_change"
        
        return list(map(lambda line: { "line": line, "status": status }, lines))