#!/usr/bin/env python
# -*- coding: utf-8 -*-
# written by Christoph Federrath

import time
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from cfpack import stop, print

# class to control web browser
class browser_control:
    # init
    def __init__(self, verbose=1, headless=False, do_not_open=False):
        self.verbose = verbose # more output (default is 1)
        self.headless = headless # in case we want to run in background (without browser window)
        self.wait = 10 # default wait time (seconds)
        self.sleep = 0.0 # default sleep time between actions (seconds)
        if not do_not_open: self.open()

    # power up web driver window
    def open(self):
        options = None
        if self.headless:
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            if self.verbose: print("Running in 'headless' mode...")
        # open driver
        self.driver = webdriver.Chrome(options=options)

    # close web driver window
    def close(self):
        self.driver.quit()

    # function to load URL
    def load_url(self, url="https://www.mso.anu.edu.au/~chfeder/index.html", wait=None, sleep=None, wait_until_element=""):
        if self.verbose > 1 or self.headless: print("loading URL '"+url+"'...")
        self.driver.get(url)
        try:
            # wait max 'wait' seconds, or until page is loaded
            WebDriverWait(self.driver, self.my_wait(wait)).until(lambda d: d.execute_script("return document.readyState") == "complete")
        except:
            if self.verbose: print("Loading URL took too long; try increasing 'wait' in call to load_url()...")
            stop()
        # check for presence of element (by XPATH)
        if wait_until_element != "":
            WebDriverWait(self.driver, self.my_wait(wait)).until(EC.presence_of_element_located((By.XPATH, wait_until_element)))
        self.my_sleep(sleep) # sleep a bit if requested

    # return selenium by obj based on input arg str
    def selenium_by(by_str='xpath'):
        selenium_by = ""
        if by_str=='xpath': selenium_by = By.XPATH
        if by_str=='name': selenium_by = By.NAME
        return selenium_by

    # return element to find (default: by "xpath"); and perform an action, e.g., click (optional)
    def find_element(self, element_str="", by="xpath", wait=None, sleep=None, click=False, enter_text="", select="", visible=None):
        if self.verbose > 1 or self.headless: print("looking for element '"+element_str+"'...")
        obj = WebDriverWait(self.driver, self.my_wait(wait)).until(EC.presence_of_element_located((by,element_str)))
        self.my_sleep(sleep) # sleep a bit if requested
        if visible is not None:
            WebDriverWait(self.driver, self.my_wait(wait)).until(EC.visibility_of(obj))
        # click (button or tickbox)
        if click:
            WebDriverWait(self.driver, self.my_wait(wait)).until(EC.visibility_of(obj))
            ActionChains(self.driver).move_to_element(obj).perform()
            obj = WebDriverWait(self.driver, self.my_wait(wait)).until(EC.element_to_be_clickable((by,element_str)))
            try: obj.click() # try a normal click first
            except: self.driver.execute_script("arguments[0].click();", obj) # then try a script click
        # enter text (into box)
        if enter_text != "":
            obj.send_keys(enter_text)
        # select something
        if select != "":
            selector = Select(obj)
            selector.select_by_visible_text(select)
        # return found object
        return obj

    # return list of elements to find
    def find_elements(self, element_str="", by="xpath", wait=None, sleep=None):
        if self.verbose > 1 or self.headless: print("looking for elements '"+element_str+"'...")
        obj = WebDriverWait(self.driver, self.my_wait(wait)).until(EC.presence_of_all_elements_located((by,element_str)))
        self.my_sleep(sleep) # sleep a bit if requested
        return obj

    # custom wait; if arg is None, we use the class value self.wait
    def my_wait(self, wait_time=None):
        if wait_time is not None: return wait_time
        else: return self.wait

    # custom sleep; if arg is None, we use the class value self.sleep
    def my_sleep(self, sleep_time=None):
        if sleep_time is not None: time.sleep(sleep_time) # give it some time
        else: time.sleep(self.sleep)


# ===== MAIN Start =====
# ===== the following applies in case we are running this in script mode =====
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Browser control')
    parser.add_argument("-c", "--close", action='store_true', default=False, help="close browser window")
    args = parser.parse_args()

    # testing browser_control
    bc = browser_control()

    # load default URL
    bc.load_url()

    # close window and driver
    if args.close: bc.close()
