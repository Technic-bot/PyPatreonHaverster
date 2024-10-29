import sys
import os
import logging

from patreon_crawler import PatreonCrawler
from utils import proc_opts, setup_processor_logging, cache_factory
import postprocessors


def post_processor_factory(postprocessor, in_dir, out_dir):
    proc = None
    if postprocessor == 'thumbnail':
        proc = postprocessors.ImageResizer(in_dir, out_dir)

    return proc


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

    if args.gecko_path:
        pc.custom_gecko_path = args.gecko_path
    if args.browser_dir:
        pc.browser_dir = args.browser_dir
    if args.ignore_cache:
        pc.ignore_cache = True
            
    if args.login:

        pc.login()
        sys.exit(1)

    pc.crawl()
    pc.driver.quit()

    if args.post_process:
        post_processor = post_processor_factory(
            args.post_process, 
            args.outdir, 
            args.post_process_dir
            )
        post_processor.process()
