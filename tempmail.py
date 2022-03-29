import time, sys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

OS     = "WIN64"
OSLIST = {"RASPY": ["usr/lib/chromium-browser/chromedriver", "usr/lib/chromium-browser/chromium-browser"],"WIN64":["chromedriver.exe",r"Chrome\Application\chrome.exe"]}


DRIVER_PATH  = OSLIST[OS][0]
BROWSER_PATH = OSLIST[OS][1]
SERVICE      = Service(DRIVER_PATH)

class TempMail():
    def get_addr(self):
        self.addr = self.driver.find_element(By.CSS_SELECTOR, self.addr_css_selector).get_attribute("value")
        return self.addr
    def __init__(self, url, addr_css_selector, refresh_css_selector, sender_css_selector, sebject_css_selector, content_css_selector, driver = False):
        l = locals()
        [self.__dict__.update(ii) for ii in [{i:l[i]} for i in l][1:]] #Lazyly update the obj dict
        if not driver:
            opts = Options()
            opts.add_argument("user-agent=Mozilla/5.0")
            opts.add_argument('log-level=3')
            opts.headless = True
            opts.add_argument("window-size=1400,600")
            opts.binary_location = BROWSER_PATH
            self.driver = webdriver.Chrome(service=SERVICE, options=opts)
            
        else: self.driver = driver
        self.driver.get(url)
        for i in range(10):
            try:
                time.sleep(1)
                self.addr = self.get_addr()
                break
                if self.addr == "": raise ValueError("Email is null")
            except KeyboardInterrupt: raise KeyboardInterrupt(f"Getting your address can take a while, don't interrupt after {i}seconds you impatient")
            except Exception as e: print(e)
    def tempmailDotIo(): #If you are lazy, use this preset made for the website tempmail.io
        """
Keep in mind that this method will always return an instance of TempMail
Even if this method is inherited from TempMail and called from a child whose parent is TempMail
Oh yeah and calling it from an instance of TempMail or one of his child make no sense and will cause errors
"""
        return TempMail("https://www.tempmail.io","input#email","li.message__controls-item a.message__toggle--refresh","div#email_list span.message__item--width","div#email_list span.message__item--right","div#email_list span.message__item--right") #It's quite hard to get the content if the mail
        
    def get_last_mail(self):
        ret = {"sender":self.sender_css_selector, "subject":self.sebject_css_selector, "content":self.content_css_selector}
        for i in ret:
            try:
                ret.update({i:self.driver.find_element(By.CSS_SELECTOR, ret[i]).get_attribute("innerText")})
            except Exception as e: ret.update({i:e})
        return ret
    def wait_until(self, fun, timeout= 15):
        wrong_refresh_selector = False
        for i in range(timeout):
            try:
                try: self.driver.find_element(By.CSS_SELECTOR, self.refresh_css_selector).click()
                except: wrong_refresh_selector = True
                time.sleep(1)
                ret = self.get_last_mail()
                if fun(ret): break
                else: raise ValueError
            except KeyboardInterrupt: raise KeyboardInterrupt(f"Doing what you want can take time, don't interrupt after {i}seconds you impatient")
            except:
                ret = ""
        if wrong_refresh_selector: sys.stderr.write("Invalid refresh css selector")
        if ret == "": raise TimeoutError("Unable to find what you want in time")
        return ret
