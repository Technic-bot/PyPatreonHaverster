from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import requests

crawl_url = 'https://www.patreon.com/api/posts?include=user%2Cattachments%2Ccampaign%2Cpoll.choices%2Cpoll.current_user_responses.user%2Cpoll.current_user_responses.choice%2Cpoll.current_user_responses.poll%2Caccess_rules.tier.null%2Cimages.null%2Caudio.null&fields[post]=change_visibility_at%2Ccomment_count%2Ccontent%2Ccurrent_user_can_delete%2Ccurrent_user_can_view%2Ccurrent_user_has_liked%2Cembed%2Cimage%2Cis_paid%2Clike_count%2Cmin_cents_pledged_to_view%2Cpost_file%2Cpost_metadata%2Cpublished_at%2Cpatron_count%2Cpatreon_url%2Cpost_type%2Cpledge_url%2Cthumbnail_url%2Cteaser_text%2Ctitle%2Cupgrade_url%2Curl%2Cwas_posted_by_campaign_owner&fields[user]=image_url%2Cfull_name%2Curl&fields[campaign]=show_audio_post_download_links%2Cavatar_photo_url%2Cearnings_visibility%2Cis_nsfw%2Cis_monthly%2Cname%2Curl&fields[access_rule]=access_rule_type%2Camount_cents&fields[media]=id%2Cimage_urls%2Cdownload_url%2Cmetadata%2Cfile_name&sort=-published_at&filter[is_draft]=false&filter[contains_exclusive_posts]=true&json-api-use-default-includes=false&json-api-version=1.0&filter[campaign_id]=145535'

def validate_access(cookies, headers):
    current_user_url = 'https://www.patreon.com/api/current_user'
    resp =requests.get(
            current_user_url, 
            cookies=cookies,
            headers=headers)
    r = resp.json()
    print(r)

def open_browser():
    URL= 'https://www.patreon.com/'
    opts = Options()
    opts.add_argument('--user-data-dir=selly/')
    #opts.add_argument('--headless')
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1024, 768) # optional
    cookies = driver.get_cookies()
    driver.get(URL + 'login')

    cookies = driver.get_cookies()
    agent = driver.execute_script("return navigator.userAgent")
    cookie_dict = {}
    for cookie in cookies:
        name = cookie['name']
        val = cookie['value']
        cookie_dict[name] = val
        
    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Cache-Control": "no-cache",
        "DNT" : "1",
        "User-agent" : agent
    }
    validate_access(cookie_dict, headers) 
    w = WebDriverWait(driver,50)
    w.until(
            EC.presence_of_element_located((By.ID,'pageheader-title'))
            )

    driver.quit()
    return cookie_dict

def crawl(cookies):
    resp = requests.get(crawl_url, cookies=cookies)
    out = resp.json()
    entries = out['data']
    for entry in entries:
        attrs = entry['attributes']
        title = attrs['title']
        try:
            url = attrs['post_file']['url']
        except KeyError:
            print(attrs)
        
        print(title,url)
        get_image(url)
        break

def get_image(url, cookies):
    resp = requests.get(crawl_url, cookies=cookies)

if __name__ == "__main__":
    cookies =open_browser()
    crawl(cookies)
