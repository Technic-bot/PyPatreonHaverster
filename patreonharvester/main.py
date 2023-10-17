import argparse
import sys
import os
import logging

from patreon_crawler import PatreonCrawler
import caches
import postprocessors

def proc_opts():
    parser = argparse.ArgumentParser(description="Patreon art scraper")
    parser.add_argument('url')
    parser.add_argument('outdir')
    parser.add_argument('--limit', default=0, type=int)
    parser.add_argument('--db-file', default='patreon.json')
    parser.add_argument('--login', action='store_true', help='login to patreon for cookies')
    parser.add_argument('--gecko-path', help='Custom geckodriver path')
    parser.add_argument('--browser-dir', help='Browser user directory for cookies and other things')
    parser.add_argument('--post-process', default='', help='Post processor')
    parser.add_argument('--post-process-dir', default='', help='Post Proces output directory')
    return parser.parse_args()


def cache_factory(filename):
    cache = None
    if not os.path.isfile(filename):
        print("No file found starting with empty json cache")
        cache = caches.EmptyJsonCache(filename)
        return cache

    if filename.endswith('.json'):
        cache = caches.JsonCache(filename)
    elif filename.endswith('.db'):
        cache = caches.SqlCache(filename)
        
    n_cache = len(cache.patreon_data)
    print(f"Read {n_cache} post from {filename}")
    return cache


def post_processor_factory(postprocessor, in_dir, out_dir):
    proc = None
    if postprocessor == 'thumbnail':
        proc = postprocessors.ImageResizer(in_dir, out_dir)

    return proc
        

def setup_processor_logging(logger, log_file='patreon_harvester.log'):
    logger.setLevel(logging.DEBUG)

    strem_handler = logging.StreamHandler()
    strem_handler.setLevel(logging.INFO)
    strem_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(message)s'
            )
    strem_handler.setFormatter(strem_formatter)
    logger.addHandler(strem_handler)

    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_fmtr = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    file_handler.setFormatter(file_fmtr)
    logger.addHandler(file_handler)
    return


if __name__=="__main__":
    args = proc_opts()
    setup_processor_logging(
            logging.getLogger("patreonharvester")
            )

    cache = cache_factory(args.db_file)
        
    pc = PatreonCrawler(
            args.url, args.outdir,
            cache, args.limit,
        )

    if args.login:
        pc.login()
        sys.exit(1)

    if args.gecko_path:
        pc.custom_gecko_path = args.gecko_path
    if args.browser_dir:
        pc.browser_dir = args.browser_dir
            
    pc.crawl()
    pc.driver.quit()

    if args.post_process:
        post_processor = post_processor_factory(
            args.post_process, 
            args.outdir, 
            args.post_process_dir
            )
        post_processor.process()
