from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import requests
import time
import random
import json
import os 

from dataclasses import dataclass, field, asdict

crawl_url = (
         "https://www.patreon.com/api/posts?"
         "include=user%2Cattachments%2Ccampaign%2Cpoll.choices%2Cpoll.current_user_responses.user%2Cpoll.current_user_responses.choice%2Cpoll.current_user_responses.poll%2Caccess_rules.tier.null%2Cimages.null%2Caudio.null%2Cuser_defined_tags"
         "&fields[post]=change_visibility_at%2Ccomment_count%2Ccontent%2Ccurrent_user_can_delete%2Ccurrent_user_can_view%2Ccurrent_user_has_liked%2Cembed%2Cimage%2Cis_paid%2Clike_count%2Cmin_cents_pledged_to_view%2Cpost_file%2Cpost_metadata%2Cpublished_at%2Cpatron_count%2Cpatreon_url%2Cpost_type%2Cpledge_url%2Cthumbnail_url%2Cteaser_text%2Ctitle%2Cupgrade_url%2Curl%2Cwas_posted_by_campaign_owner"
         "&fields[user]=image_url%2Cfull_name%2Curl"
         "&fields[campaign]=show_audio_post_download_links%2Cavatar_photo_url%2Cearnings_visibility%2Cis_nsfw%2Cis_monthly%2Cname%2Curl"
         "&fields[access_rule]=access_rule_type%2Camount_cents"
         "&fields[media]=id%2Cimage_urls%2Cdownload_url%2Cmetadata%2Cfile_name"
         "&sort=-published_at"
         "&filter[is_draft]=false&filter[contains_exclusive_posts]=true&json-api-use-default-includes=false&json-api-version=1.0"
#         "&filter[campaign_id]=145535"
         "&filter[campaign_id]={}"
            )

def get_crawl_url():
    return crawl_url

@dataclass
class PatreonPost():
    post_id: int
    title: str
    description: str
    filename: str
    post_type: str
    download_url: str
    patreon_url: str
    publication_date: str
    tags: list[str]= field(default_factory=list)

class PatreonCrawler():
    def __init__(
            self,
            url:str,
            out_dir:str,
            out_json:str,
            limit:int = 50 ):
        self.campaing_url = url
        self.limit = limit
        self.out_folder = out_dir
        self.out_json = out_json

    def crawl(self):
        self.set_driver()
        self.cookies = self.get_browser_cookies()
        self.header = self.get_headers()
        self.campaing_id = self.get_campaign_id()
        if not self.validate_login():
            self.login()
            if not self.validate_login():
                print("Could not validate login terminating")
                return
        # no need to use browser after login
        self.driver.quit()
        print("Starting crawl of {self.campaing_url}")
        posts = self.get_img_urls()
        for p in posts:
            self.download_image(p)

        return

    def get_campaign_id(self):
        r = requests.get(self.campaing_url, cookies=self.cookies, headers=self.header)
        html = r.text 
        eye_catcher ='api/campaigns/'
        idx_str = html.find(eye_catcher)
        idx_stop = html.find('"',idx_str+len(eye_catcher))
        campaign_id = html[idx_str+len(eye_catcher):idx_stop]
        print(f"Got campaing id: {campaign_id}")
        return campaign_id

    def get_img_urls(self):
        next_page = crawl_url.format(self.campaing_id)
        post_list = []
        while next_page:
            r = requests.get(next_page, cookies=self.cookies, headers=self.header)
            jason = r.json()
            posts = jason['data']
            for post in posts:
                attrs = post['attributes']
                typ = attrs['post_type']
                title = attrs['title']
                print(f'{typ} post: {title}')
                if typ == 'image_file' and 'post_file' in attrs:
                    patreon_post = self.process_post(post)
                    post_list.append(patreon_post)
            if len(post_list) > self.limit:
                print(f"Early stop at {len(post_list)}")
                break
            next_page = jason['links']['next']
            jitter = random.uniform(0.0, 1)
            time.sleep(0.5 + jitter)
        return post_list
                
    def process_post(self, post):
        attrs=post['attributes']
        user_tags = post['relationships']['user_defined_tags']
        post_tags = [t['id'].split(';')[-1] for t in user_tags['data']]
        try:
            patreon_post = PatreonPost(post_id=post['id'],
                                title = attrs['title'],
                                description = attrs['content'], 
                                download_url = attrs['post_file']['url'],
                                filename = attrs['post_file']['name'],
                                post_type = attrs['post_type'],
                                tags = post_tags,
                                patreon_url= attrs['url'],
                                publication_date = attrs['published_at'])
        except TypeError as e:
            print(f"Malformed entry: {post['id']} {attrs['title']} ")
        except KeyError as e:
            print(e)
            print(f"Malformed entry : {post['id']} {attrs['title']} ")

        return patreon_post

    def download_image(self, post):
        file_path = self.out_folder + post.filename
        if os.path.isfile(file_path):
            print(f"{file_path} exists skipping")
            return

        print(f"Fetching {post.download_url}") 
        r = requests.get(post.download_url, cookies=self.cookies, headers=self.header)
        with open(post.filename, mode='wb') as file:
            print(f"Saving {post.filename}") 
            file.write(r.content)
        jitter = random.uniform(0.0, 1)
        time.sleep(0.5 + jitter)
        return

    def persis_patreon_json(patreon,filename):
        print(f"Saving json to {filename}")
        with open(filename,'w') as out_file:
            json.dump(patreon, out_file, default=asdict)
        return

    def login(self):
        self.driver 
        w = WebDriverWait(driver,50)
        print("Please login in external browser window")
        w.until(
            EC.presence_of_element_located((By.ID,'pageheader-title'))
           )
        self.cookies = self.get_browser_cookies()
        return

    def set_driver(self):
        opts = Options()
        opts.add_argument('--user-data-dir=selly/')
        opts.add_argument('--headless')
        self.driver = webdriver.Chrome(options=opts)
        self.driver.set_window_size(1024, 768) # optional

    def validate_login(self):
        """ Check if cookies grant access to patreon """
        current_user_url = 'https://www.patreon.com/api/current_user'
        resp =requests.get(
                current_user_url, 
                cookies=self.cookies,
                headers=self.header)
        status = resp.status_code
        login_succ = True
        if status != 200:
            print(f"Login error {status}")
            login_succ = False 
        else:
            r = resp.json()
            email = r['data']['attributes']['email']
        print(f"Logged as {email}")
        return login_succ
    
    def get_browser_cookies(self):
        self.driver.get('https://www.patreon.com/login')
        cookies = self.driver.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            name = cookie['name']
            val = cookie['value']
            cookie_dict[name] = val
            print(f"Setting cookie {name}:{val}")
        return cookie_dict

    def get_headers(self):
        agent = self.driver.execute_script("return navigator.userAgent")
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "DNT" : "1",
            "User-agent" : agent
        }
        return headers
