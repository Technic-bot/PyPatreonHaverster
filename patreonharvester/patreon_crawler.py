from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC

import requests
import time
import random
import json
import os
import re

import dataclasses

from patreon_classes import PatreonPost

from caches import HarvestCache


import logging
logger = logging.getLogger("patreonharvester."+__name__)

crawl_url = ( "https://www.patreon.com/api/posts?"
              "include=campaign%2Caccess_rules%2Cattachments%2Caudio%2Caudio_preview.null%2Cimages%2Cmedia%2Cnative_video_insights%2Cpoll.choices%2Cpoll.current_user_responses.user%2Cpoll.current_user_responses.choice%2Cpoll.current_user_responses.poll%2Cuser%2Cuser_defined_tags%2Cti_checks"
              "&fields[campaign]=currency%2Cshow_audio_post_download_links%2Cavatar_photo_url%2Cavatar_photo_image_urls%2Cearnings_visibility%2Cis_nsfw%2Cis_monthly%2Cname%2Curl"
              "&fields[post]=change_visibility_at%2Ccomment_count%2Ccommenter_count%2Ccontent%2Ccurrent_user_can_comment%2Ccurrent_user_can_delete%2Ccurrent_user_can_report%2Ccurrent_user_can_view%2Ccurrent_user_comment_disallowed_reason%2Ccurrent_user_has_liked%2Cembed%2Cimage%2Cimpression_count%2Cinsights_last_updated_at%2Cis_paid%2Clike_count%2Cmeta_image_url%2Cmin_cents_pledged_to_view%2Cpost_file%2Cpost_metadata%2Cpublished_at%2Cpatreon_url%2Cpost_type%2Cpledge_url%2Cpreview_asset_type%2Cthumbnail%2Cthumbnail_url%2Cteaser_text%2Ctitle%2Cupgrade_url%2Curl%2Cwas_posted_by_campaign_owner%2Chas_ti_violation%2Cmoderation_status%2Cpost_level_suspension_removal_date%2Cpls_one_liners_by_category%2Cvideo_preview%2Cview_count"
              "&fields[post_tag]=tag_type%2Cvalue"
              "&fields[user]=image_url%2Cfull_name%2Curl"
              "&fields[access_rule]=access_rule_type%2Camount_cents"
              "&fields[media]=id%2Cimage_urls%2Cdownload_url%2Cmetadata%2Cfile_name"
              "&fields[native_video_insights]=average_view_duration%2Caverage_view_pct%2Chas_preview%2Cid%2Clast_updated_at%2Cnum_views%2Cpreview_views%2Cvideo_duration"
              "&filter[campaign_id]={}"
              #"&filter[campaign_id]=145535"
              "&filter[contains_exclusive_posts]=true&filter[is_draft]=false"
              "&sort=-published_at&json-api-version=1.0"
              "&json-api-use-default-includes=false" )

# For specific post media
# meta

class PatreonCrawler():
    def __init__(
            self,
            url: str,
            out_dir: str,
            cache: HarvestCache,
            limit: int = 0,
            ):
        self.campaing_url = url
        self.limit = limit
        self.out_folder = out_dir

        self.custom_gecko_path = None

        self.browser_dir = 'selly/'

        self.post_list = []
        self.multi_image_posts = []

        self.ignore_cache = False

        self.cache = cache
        return

    def crawl(self):
        self.set_request_metadata()
        self.campaing_id = self.get_campaign_id()
        if not self.validate_login():
            self.login()
            if not self.validate_login():
                logger.error("Could not validate login terminating")
                return

        logger.info(f"Starting crawl of {self.campaing_url}")
        self.get_img_urls()

        for p in self.post_list:
            self.download_image(p)
        self.cache.persist(self.post_list) 
        return

    def set_request_metadata(self):
        opts = Options()
        logger.info("Setting cookies and headers")
        opts.add_argument('--headless')
        opts.add_argument('-profile')
        logger.info(f"Reading from browser directory: {self.browser_dir}")
        opts.add_argument(self.browser_dir)
        if self.custom_gecko_path:
            service = webdriver.FirefoxService(
                        executable_path=self.custom_gecko_path
                      )
        else:
            service = webdriver.FirefoxService()
        
        self.driver = webdriver.Firefox(service=service, options=opts)
        self.driver.set_window_size(1024, 768)
        self.cookies = self.get_browser_cookies()
        self.header = self.get_headers()
        self.driver.quit()
        return

    def get_browser_cookies(self):
        self.driver.get('https://www.patreon.com/login')
        cookies = self.driver.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            name = cookie['name']
            val = cookie['value']
            cookie_dict[name] = val
            logger.debug(f"Setting cookie {name}:{val}")
        return cookie_dict

    def get_headers(self):
        agent = self.driver.execute_script("return navigator.userAgent")
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "DNT": "1",
            "User-agent": agent
        }
        return headers

    def get_campaign_id(self):
        logger.info(f"Getting id for {self.campaing_url}")
        r = requests.get(self.campaing_url, cookies=self.cookies, headers=self.header)
        html = r.text
        eye_catcher = 'api/campaigns/'
        idx_str = html.find(eye_catcher)
        idx_stop = html.find('"', idx_str+len(eye_catcher))
        campaign_id = html[idx_str+len(eye_catcher):idx_stop]
        logger.info(f"Got campaing id: {campaign_id}")
        return campaign_id

    def validate_login(self):
        """ Check if cookies grant access to patreon """
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
        return login_succ

    def login(self):
        # Make new non-headless driver
        opts = Options()
        opts.add_argument('-profile')
        opts.add_argument(self.browser_dir)
        self.driver = webdriver.Firefox(options=opts)
        self.driver.set_window_size(1024, 768)
        w = WebDriverWait(self.driver, 50)

        print("Please login in external browser window")
        self.driver.get('https://www.patreon.com/login')
        w.until(
            EC.presence_of_element_located((By.ID, 'main-app-navigation'))
           )
        self.cookies = self.get_browser_cookies()
        self.header = self.get_headers()
        self.driver.quit()
        return

    def get_img_urls(self):
        next_page = crawl_url.format(self.campaing_id)
        page_n = 1
        while next_page:
            r = requests.get(next_page, cookies=self.cookies, headers=self.header)
            response = r.json()
            posts = response['data']
            n_posts = len(posts)
            logger.info(f"Got {n_posts} posts at page {page_n}")
            logger.debug(f"Crawling {next_page}")
            latest_post, multi_posts = self.process_api_response(posts)
            self.get_media_image_urls(multi_posts)

            if self.early_stop(latest_post['id']):
                break

            links = response.get('links', None)
            if links:
                next_page = links['next']
            else:
                next_page = None

            page_n += 1
            self.wait()

        return 

    def process_api_response(self, posts: dict):
        multi_posts = []
        latest_post = None
        for post in posts:
            attrs = post['attributes']
            self.report_post_type(attrs, post['id'])

            if  self.is_valid_post(attrs):
                if not latest_post:
                    latest_post = post
                
                if not self.is_processed(post['id']):
                    patreon_post = self.process_post(post)

                    # Uncomment this if you want to detect 
                    # attachements on post
                    # if self.has_multiple_images(post):
                    #    multi_posts.append(patreon_post)
                    
                    self.post_list.append(patreon_post)

        # return last post checked
        return latest_post, multi_posts

    def has_multiple_images(self, post):
        """ Checks if post has more than one image
            This only check if posts shows more than on image
            if more stuff is attached is ignored    
        """
        attrs = post['attributes']
        try: 
            post_metadata = attrs['post_metadata']
            if not post_metadata:
                return False

            # detect multiple images on post
            img_order = post_metadata.get('image_order', None)

            if img_order and len(img_order) > 1: 
                return True

            attached = post['relationships']['attachments']['data']
            if attached:
               return True
        except TypeError as e:
            logger.error(e)
            logger.error(f"Malformed request on {post['id']}")
        except KeyError as e:
            logger.error(e)
            logger.error(f"Malformed request on {post['id']}")

        return False

    def report_post_type(self, attrs: dict, id: int):
        typ = attrs['post_type']
        title = attrs['title']
        date = attrs['published_at']
        logger.debug(f'Detected {typ} post: {id}:{title} @ {date}')
        return

    def get_media_image_urls(self, posts):
        for p in posts:
            resp = self.get_post_media(p.post_id)
            self.process_media_response(p, resp)
            self.wait()
        return

    def get_post_media(self, post_id):
        api_url = "https://www.patreon.com/api/posts/{}/media".format(post_id)
        r = requests.get(api_url, cookies=self.cookies, headers=self.header)
        logger.debug(f'Requesting media for {post_id}')
        return r.json()

    def process_media_response(self, post, resp):
        media_imgs = resp['data']
        for media in media_imgs:
            url = media['attributes']['download_url']
            filename = media['attributes']['file_name']
            if filename != post.filename:
                # Copy post with new filename ignore file 
                # from parent post
                media_post = dataclasses.replace(post)
                media_post.filename = filename 
                logger.debug(f'Detected extra image for '
                             f'{post.post_id}: {media_post.filename}') 
                self.post_list.append(media_post)
        logger.info(f"Got {len(media_imgs)} images from {post.title}")
        return

    def early_stop(self, post_id):
        stop = False
        n_posts = len(self.post_list)
        if self.limit and len(self.post_list) > self.limit:
            logger.info(f"Early stop at {n_posts}")
            stop = True
        logger.debug(f"Checking id for early stop: {post_id}")
        if self.is_processed(post_id) and not self.ignore_cache:
            logger.info(f"Early stop from cache at {n_posts}")
            stop = True
        return stop

    def is_valid_post(self, attrs):
        typ = attrs['post_type']
        valid = typ == 'image_file' and 'post_file' in attrs 
        return valid 

    def is_processed(self, post_id):
        # if self.ignore_cache:
        #    return False

        if not self.cache:
            return False
        return self.cache.is_post_present(int(post_id))

    def process_post(self, post):
        attrs = post['attributes']
        user_tags = post['relationships']['user_defined_tags']
        post_tags = [t['id'].split(';')[-1] for t in user_tags['data']]
        try:
            patreon_post = PatreonPost(
                    post_id=int(post['id']),
                    title=attrs['title'],
                    description=attrs['content'],
                    download_url=attrs['post_file']['url'],
                    post_type=attrs['post_type'],
                    filename=attrs['post_file'].get('name',''),
                    tags=post_tags,
                    patreon_url=attrs['url'],
                    publication_date=attrs['published_at']
            )
        except TypeError as e:
            logger.error(e)
            logger.error(f"Malformed entry: {post['id']} {attrs['title']} ")
        except KeyError as e:
            logger.error(e)
            logger.error(f"Malformed entry : {post['id']} {attrs['title']} ")

        return patreon_post
    
    def wait(self, avg: int = 0.5):
        jitter = random.uniform(0.0, 1)
        time.sleep(avg + jitter)

    def download_image(self, post):
        logger.debug(f"Checking {post.download_url}")
        
        r = requests.head(post.download_url, cookies=self.cookies, headers=self.header)

        content_disp = r.headers['content-disposition']
        post.filename = re.findall(r'filename="(.+)";', content_disp)[0]
    
        file_path = self.out_folder + post.filename
        if os.path.isfile(file_path):
            logger.debug(f"{file_path} exists skipping")
            return

        logger.debug(f"Downloading {post.download_url}")
        r = requests.get(post.download_url, cookies=self.cookies, headers=self.header)
        with open(self.out_folder + post.filename, mode='wb') as file:
            logger.info(f"Saving {post.filename} to {self.out_folder}")
            file.write(r.content)
        self.wait()
        return

