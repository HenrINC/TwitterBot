from tempmail import TempMail
from WF2 import *

import os, time, random, sys, hashlib, sys, requests, _thread, cv2, traceback, pyautogui
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import pyperclip as perclip
from traceback import format_exc

OS     = "WIN64"
OSLIST = {"RASPY": ["usr/lib/chromium-browser/chromedriver", "usr/lib/chromium-browser/chromium-browser"],"WIN64":["chromedriver.exe",r"Chrome\Application\chrome.exe"]}

class Account():

    def __init__(self, username, passwd, email, at = None, profile_picture = False, bio = False):
        self.username   = username
        self.passwd     = passwd
        self.email      = email
        self.at         = at
        self.pp         = profile_picture
        self.connected  = False
        self.bio        = bio
        self.state      = ""
        self.driver     = None
        self.url        = "https://twitter.com"

    def connect(self, driver = None, headless = True):
        pass

    def signin(self, driver = None, headless = True):
        try:
            if driver == None:
                driver = get_annon_chrome()

            driver.get(self.url)
            #Accesing registering form
            #driver.find_element(By.CSS_SELECTOR, )

            compleate_fields(driver,{"[href='/i/flow/signup']": Keys.ENTER})
            
            #Registering
            elements, button, form = scrap_and_compleate(driver,
                                                         "[name=name]",
                                                         ["select"],
                                                         ["input","select","[role=button]"],
                                                         {"[name=name]":self.username, "[role=button]":Keys.ENTER,
                                                          "select": [Keys.DOWN]*random.randint(1,12),
                                                          "div+div>select":[Keys.DOWN]*random.randint(1,28),
                                                          "div+div+div>select":[Keys.DOWN]*random.randint(20,25),
                                                          "[name=email]":self.email.addr})
            go_as_blind_where(driver, lambda focus: focus == button)
            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

            #Experience personalisation
            elements, button, form = smart_scrap(driver, "[type=checkbox]",
                                                 ["[role=link]"], ["input"])
            go_as_blind_where(driver, lambda focus: focus == button)
            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

            #Info confirmation
            elements, button, form = smart_scrap(driver, "[name=name]",
                                                 ["a"], ["[role=button]"])
            go_as_blind_where(driver, lambda focus: focus == elements[-1])
            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

            #Confirmation code
            elements, button, form = scrap_and_compleate(driver,
                                                         "input",
                                                         ["[role=button]"],
                                                         ["input"],
                                                         {"input":self.email.wait_until(lambda ret: ret["sender"] == "verify@twitter.com")["subject"].split(" ")[0]})
            go_as_blind_where(driver, lambda focus: focus == button)
            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

            #Phone number (maybe)
            if is_in_webpage(driver, "[name=phone_number]", timeout = 2):
                raise ConnectionError("This node is broken, reset your proxy")


            #Password
            elements, button, form = smart_scrap(driver, "input",
                                                 ["input"],
                                                 ["input"])
            webdriver.ActionChains(driver).send_keys(self.passwd).perform()
            go_as_blind_where(driver, lambda focus: focus == button)
            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

            #Profile picture
            elements, button, form = smart_scrap(driver, "input",
                                                 ["input"],
                                                 ["input"])
            if self.pp:
                compleate_fields(driver,{"div+div div[role=button]": Keys.ENTER})
            else:
                go_as_blind_where(driver, lambda focus: focus == button)
                webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

            #Bio
            elements, button, form = smart_scrap(driver, "textarea",
                                                 ["[role=button]"],
                                                 ["[role=button]"])
            if self.bio: 
                webdriver.ActionChains(driver).send_keys(self.bio).perform()
            go_as_blind_where(driver, lambda focus: focus == elements[-1])
            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

            #@ check
            elements, button, form = smart_scrap(driver, "input",
                                                 ["[role=button]"],
                                                 ["input"])
            go_as_blind_where(driver, lambda focus: focus == button)
            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()


            #4 possibilites :
            #1) Language -> Notification -> Big tiles -> tiles
            #2) Notification -> Big tiles -> tiles
            #3) Big tiles -> tiles
            #4) tiles
            states_dict = {"[role=button]+[role=button]": 3, #"Notification",
                                    "[role=presentation]": 1, #"Tiles",
                                    "li+li+li [role=button]": 2, #"Big tiles",
                                    "input[type=checkbox]": 4 }#"Language"}
            state =  check_webpage_state(driver, states_dict)


            if state >= 4: #Lang
                raise Exception("LANGUAGE NOT SUPPORTED")
            
            if state >= 3: #Notifs
                elements, button, form = smart_scrap(driver, "[role=button]+[role=button]",
                                                         ["svg"],
                                                         ["[role=button]"])
                go_as_blind_where(driver, lambda focus: focus == elements[-1])
                webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

            if state >= 2: #Big Tiles
                elements, button, form = scrap_and_compleate(driver, "li [role=button]", ["section"], ["[role=button]"],
                                            {"li [role=button]": Keys.ENTER,
                                             "li+li [role=button]": Keys.ENTER,
                                             "li+li+li [role=button]": Keys.ENTER})
                button.click()
                states_dict.pop("li+li+li [role=button]")

            if state >= 1:
                elements, button, form = scrap_and_compleate(driver, "[role=presentation]", ["section"], ["[role=button]"],
                                        {"[role=presentation] [role=button]": Keys.ENTER,
                                         "[role=presentation]+[role=presentation] [role=button]": Keys.ENTER,
                                         "[role=presentation]+[role=presentation]+[role=presentation] [role=button]": Keys.ENTER})
                compleate_fields(driver, {"[role=group] [role=group]>div+div>div+div [role=button]":Keys.ENTER}, timeout = 180)            


            #Subs
            elements, button, form = smart_scrap(driver, "section [role=button]",
                                                         ["section"], ["[role=button]"])
            try:
                ind = ["[style*=transform]"]*3
                for i in range(10):
                    compleate_fields(driver,{f"h1[dir=auto]+div.css-1dbjc4n {'+'.join(ind)} div[role=button]":Keys.ENTER}, timeout = 5)
                    ind.append(ind[0])
            except: pass
            
            button.click()
        except ConnectionError as e: raise e
        except Exception as e:
            try:
                driver.save_screenshot(f'ERROR-{int(time.time())}.png')
            except: pass
            raise e
        
        self.state  = "homepage"
        self.driver = driver

        return self
    def goto_profile(self, at):
        if self.driver == None or not self.state:
            raise ValueError("Please connect first")
        self.driver.get(self.url+f"/{at}")
        self.state = f"profile_of_{at}"
        self.driver.refresh()
        
    def send_msg_to(self, at, msg):
        if self.state != f"profile_of_{at}":
            self.goto_profile(at)
            
        if not is_in_webpage(self.driver, "[data-testid=sendDMFromProfile]", timeout = 10):
            time.sleep(2)
            self.driver.refresh()
            if not is_in_webpage(self.driver, "[data-testid=sendDMFromProfile]", timeout = 10):
                raise Exception("Can't send message, DM are close")
        self.driver.find_element_by_css_selector("[data-testid=sendDMFromProfile]").click()
        
        if not is_in_webpage(self.driver, "[data-testid=dmComposerTextInput]", timeout = 10):
            raise Exception("Can't send message, unable to locate text area (this is really wierd)")
        self.driver.find_element_by_css_selector("[data-testid=dmComposerTextInput]").send_keys(msg)
        
        if not is_in_webpage(self.driver, "[data-testid=dmComposerSendButton]", timeout = 10):
            raise Exception("Can't send message, unable to locate send button (this is really wierd)")
        compleate_fields(self.driver, {"[data-testid=dmComposerSendButton]":Keys.ENTER}, timeout = 30)
        
while __name__ == "__main__":
    try:

        port = 9200+random.randint(0,99)

        proxy = TorProxy(port = port)

        proxy.start()

        driver = get_annon_chrome(headless = False)

        debug = DebugThread(driver)

        debug.start()

        tempmail = TempMail.tempmailDotIo()

        dummy = Account("LORD_BLK", "1c4d5sd45", tempmail)

        #dummy.pp = " "

        dummy = dummy.signin(driver = driver)

        dummy.email.driver.quit()

        dummy.send_msg_to("slpng_giants_fr", "Hello world")

        input("SUCCES")
        
        #debug.stop()
    except:

        debug.stop()

        proxy.stop()

        driver.quit()

        tempmail.driver.quit()
        
        print(traceback.format_exc())

                

        
        
        
        
