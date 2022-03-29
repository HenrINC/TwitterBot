import json, requests, random, os, time, cv2, _thread, psutil, subprocess
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import numpy as np

OS     = "WIN64"
OSLIST = {"RASPY": ["usr/lib/chromium-browser/chromedriver", "usr/lib/chromium-browser/chromium-browser"],"WIN64":["chromedriver.exe",r"Chrome\Application\chrome.exe"]}

DRIVER_PATH  = OSLIST[OS][0]
BROWSER_PATH = OSLIST[OS][1]
SERVICE      = Service(DRIVER_PATH)

class DebugThread():
    def __init__(self, driver):
        self.driver  = driver
        self.running = False
        self.name = f"Debug-{id(self)}"
    def main(self):
        while self.running:
            png = self.driver.get_screenshot_as_png()
            nparr = np.frombuffer(png, np.uint8)
            cv2.imshow(self.name,cv2.imdecode(nparr, cv2.IMREAD_COLOR))
            cv2.waitKey(1)
    def start(self):
        self.running = True
        
        _thread.start_new_thread(self.main, ())
    def stop(self):
        self.running = False
        cv2.destroyWindow(self.name)

class TorProxy():
    
    def __init__(self, port = 9050, address = "127.0.0.1", directory = "Tor", ip_blacklist = []):
        self.port           = port
        self.addr           = address
        self.dir_           = directory
        self.running        = False
        self.ip_blacklist   = ip_blacklist
        self.steup_files()
        

    def steup_files(self):
        if not f"torrc-{self.port}" in os.listdir(self.dir_):
            #os.system(f"cd {self.dir_} & copy tor.exe tor-{self.port}.exe")
            with open(os.path.join(self.dir_,f"torrc-{self.port}"), "w") as torrc:
                torrc.write("""SocksListenAddress {addr}:{port}
SocksPort {port}
DataDirectory {port}""".format(port = self.port, addr = self.addr))
                
    def start(self):
        if not self.running:
            self.process = subprocess.Popen("{0}/tor.exe -f {0}/torrc-{1}".format(self.dir_, self.port))
            self.pid = self.process.pid
            self.running = True
                
    def stop(self):
        if self.running:
            os.system(f"taskkill -f -pid {self.pid}")
            self.running = False

    def clear_files(self): pass


def kill_all():
    os.system("taskkill /f /im chrome.exe")
    os.system("taskkill /f /im chromedriver.exe")
    os.system("taskkill /f /im tor.exe")


def get_annon_chrome(port = 9050, mod_opts = lambda opts: opts, headless = False, proxy = False):
    if not proxy:
        proxy = TorProxy(port)
        proxy.start()
    
    opts = Options()
    opts.headless = headless
    opts.add_argument("user-agent=Mozilla/5.0")
    opts.add_argument(f"--proxy-server=socks5://127.0.0.1:{proxy.port}")
    opts.binary_location = BROWSER_PATH
    opts = mod_opts(opts)

    driver = webdriver.Chrome(service=SERVICE, options=opts)
    return driver

def is_in_webpage(driver, selector, timeout = 30):
    for i in range(timeout): #Check if the start selector is present e.i. if the page has loaded
        try:
            driver.find_element(By.CSS_SELECTOR, selector)
            break
        except:
            time.sleep(1)
            timeout -= 1
    return bool(timeout)
    
def check_webpage_state(driver, states, timeout = 30):
    """
Check the current status of a webpage
It looks for the first selector in the states's keys and will return the corresponding value
Will raise an error if timeout exeded
"""
    for i in range(timeout):
        for selector in states.keys():
            if driver.find_elements(By.CSS_SELECTOR, selector):
                return states[selector]
        time.sleep(1)
    raise TimeoutError

def smart_scrap(driver, start_selector, requred_selectors, field_selectors, timeout = 30):
    if not is_in_webpage(driver, start_selector, timeout = timeout):
        raise TimeoutError("Can't go there in time")
    js_start_getter = f'e = document.querySelector("{start_selector}").parentElement'
    js_while_cond   = "&&".join([f'(e.querySelector("{i}") == null)' for i in requred_selectors])
    js_while_loop   = f"while ({js_while_cond}) "+"{e = e.parentElement}"
    
    driver.execute_script(js_start_getter)
    driver.execute_script(js_while_loop)
    form = driver.execute_script("return e")
    elements = form.find_elements(By.CSS_SELECTOR, ",".join(field_selectors))
    
    driver.execute_script("while (e.nextSibling == null) {e = e.parentElement}")
    button = driver.execute_script('return e.nextSibling.querySelector("[role=button]")')

    return elements, button, form


def write_on_elements(elements, data):
    for element in elements:
        for i in data:
            if data[i](element):
                element.send_keys(i)


def go_as_blind_where(driver, fun, timeout = 30):
    end = time.time()+timeout
    while True:
        focus = driver.execute_script('return document.activeElement')
        try: 
            if fun(focus):
                return focus
        except: pass
        webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
        if end < time.time():
            raise TimeoutError("Can't go there in time")

        
def compleate_fields(driver,fields, timeout = 30):
    
    """
Fields is a dict {css_selector:keys}
"""
    
    for i in fields:
        target = ""
        for ii in range(timeout):
            try:
                target = driver.find_element(By.CSS_SELECTOR, i)
                break
            except:
                time.sleep(1)
                timeout -= 1
        if target == "":
            raise TimeoutError("Can't go there in time")
        go_as_blind_where(driver,lambda focus: focus == target,timeout)
        webdriver.ActionChains(driver).send_keys(fields[i]).perform()

        
def oibvious_form_compleate(driver,fields,timeout):
    for i in fields:
        for ii in range(timeout):
            try:
                target = driver.find_element(By.CSS_SELECTOR, i)
                break
            except:
                time.sleep(0.1)
        fileds[i](target)


def scrap_and_compleate(driver, start_selector, target_selectors, field_selector, fields, timeout = 30):
    elements, button, form = smart_scrap(driver, start_selector, target_selectors, field_selector, timeout = timeout)
    for field in fields:
        target = form.find_element(By.CSS_SELECTOR, field)
        go_as_blind_where(driver,lambda focus: focus == target,timeout)
        webdriver.ActionChains(driver).send_keys(fields[field]).perform()

    return elements, button, form

def get_pids_for_name(name):
    pids = []
    for pid in psutil.pids():
        try:
            if psutil.Process(pid).name() == name:
                pids.append(pid)
        except: pass
    return pids
    
    
