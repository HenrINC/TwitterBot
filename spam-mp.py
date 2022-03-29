from twitter import Account
from WF2 import get_annon_chrome, TorProxy, kill_all, DebugThread
from tempmail import TempMail
from os import system
import random, psutil, _thread, time, traceback

start = int(time.time())

minutes = 1

succes = 0

succes_per_min = 1

ip_flagged = 0

errors = 0

_try = 0

def thread():
    global succes, start, minutes, succes_per_min, errors, ip_flagged, _try

    _try += 1
    
    try:
        try:
            port = 9200+random.randint(0,99)
            proxy = TorProxy(port)
            proxy.start()
            driver = get_annon_chrome(headless = False, proxy = proxy,
                                      mod_opts = lambda opts: [opts.add_experimental_option("prefs",{"profile.default_content_setting_values": {"images": 2,
                                                                                                                                                "stylesheets":2}}),
                                                               opts.add_argument('log-level=3'),
                                                               opts][-1])            
            tempmail = TempMail.tempmailDotIo()
            dummy = Account("LORD_BLK", f"H0TF1X_{port}", tempmail)
            dummy = dummy.signin(driver = driver)
            dummy.email.driver.quit()
            dummy.send_msg_to("slpng_giants_fr", "Hello world")
            time.sleep(1)
            dummy.driver.save_screenshot('SUCCES.png')
            dummy.driver.quit()
            proxy.stop()
            succes += 1
            succes_per_min = succes / minutes
            print("="*150+f">SUCCES #{succes} ({succes_per_min} S/M)")
        except ConnectionError as e:
            ip_flagged += 1
            raise e
    except Exception as e:
        errors += 1
        print("/ERROR================================================================================ERROR\\")
        print(traceback.format_exc().replace("\n", "|\n"))
        print("\\ERROR================================================================================ERROR/")
        proxy.stop()
        driver.quit()
        tempmail.driver.quit()

while True:
    try:
        thread()
    except: pass
    
    minutes = max(1, (int(time.time())-start)//60)
    print(f"STATUS | errors : {errors} | proxy_errors : {ip_flagged} | succes : {succes} | succes_per_try : {succes/_try} | try_per_min : {_try/minutes}")
