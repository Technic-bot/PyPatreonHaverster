import argparse
import logging
import os

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
    parser.add_argument('--post-process', default='', help='Post processor')
    parser.add_argument('--post-process-dir', default='', help='Post Proces output directory')
    parser.add_argument('--ignore-cache', action='store_true', help='Keep scraping regardless of hitting cache')
    return parser.parse_args()


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


