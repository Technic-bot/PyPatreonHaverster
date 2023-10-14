import argparse
import sys
import os
from patreon_crawler import PatreonCrawler
import caches

def proc_opts():
    parser = argparse.ArgumentParser(description="Patreon art scraper")
    parser.add_argument('url')
    parser.add_argument('outdir')
    parser.add_argument('--limit', default=0, type=int)
    parser.add_argument('--db-file', default='patreon.json')
    parser.add_argument('--login', action='store_true', help='login to patreon for cookies')
    parser.add_argument('--gecko-path', help='Custom geckodriver path')
    parser.add_argument('--browser-dir', help='Browser user directory for cookies and other things')
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
        

if __name__=="__main__":
    args = proc_opts()

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
