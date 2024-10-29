from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import DesiredCapabilities

import requests
opts = Options()
logger.info("Setting cookies and headers")
opts.add_argument('--headless')
logger.info(f"Reading from browser directory: {self.browser_dir}")
opts.add_argument('-profile')
opts.add_argument("./selly/")

driver = webdriver.Firefox(options=opts)
driver.set_window_size(1024, 768)
cookies = self.get_browser_cookies()
header = self.get_headers()
driver.quit()

current_user_url = 'https://www.patreon.com/api/current_user'
resp = requests.get(
        current_user_url,
        cookies=self.cookies,
        headers=self.header)
status = resp.status_code
login_succ = True
if status != 200:
    logger.error(f"Login error {status}")
    login_succ = False
else:
    r = resp.json()
    email = r['data']['attributes']['email']
    logger.info(f"Logged as {email}")

opts = Options()
profile = webdriver.FirefoxProfile()
profile.set_preference("dom.webdriver.enabled", False)
#profile.set_preference('useAutomationExtension', False)
profile.set_preference("general.useragent.override","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36")
profile.update_preferences()
opts.profile= profile
driver = webdriver.Firefox(options=opts)
w = WebDriverWait(self.driver, 50)

print("Please login in external browser window")
self.driver.get('https://www.patreon.com/login')
