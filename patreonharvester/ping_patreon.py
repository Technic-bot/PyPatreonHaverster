from utils import proc_opts, setup_processor_logging, cache_factory

import logging
from patreon_crawler import PatreonCrawler

if __name__=="__main__":
    args = proc_opts()
    setup_processor_logging(
        logging.getLogger("patreonharvester"),
        log_file = 'ping_patreon.log'
    )

    cache = cache_factory("pingcache")
        
    pc = PatreonCrawler(
            args.url, args.outdir,
            cache, 20,
        )

    if args.gecko_path:
        pc.custom_gecko_path = args.gecko_path
    if args.browser_dir:
        pc.browser_dir = args.browser_dir
    if args.ignore_cache:
        pc.ignore_cache = True
            
    pc.set_request_metadata()
    if args.login:
        pc.login()

    pc.validate_login()
    pc.get_campaign_id()
    pc.get_img_urls()
    pc.driver.quit()
